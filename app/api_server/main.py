"""
GAIA-BT FastAPI Application
메인 API 서버 - 모든 챗봇 기능을 RESTful API로 제공
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any
import traceback

from app.api_server.routers import chat, system, mcp, session
from app.api_server.services.chatbot_service import ChatbotService
from app.api_server.websocket_manager import WebSocketManager
from app.utils.config import OLLAMA_MODEL

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 전역 서비스 인스턴스
chatbot_service: ChatbotService = None
websocket_manager: WebSocketManager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    global chatbot_service, websocket_manager
    
    # 시작 시 초기화
    logger.info("🚀 GAIA-BT API Server 시작 중...")
    
    # 서비스 초기화
    chatbot_service = ChatbotService()
    await chatbot_service.initialize()
    
    websocket_manager = WebSocketManager()
    
    # 의존성 주입을 위한 상태 저장
    app.state.chatbot_service = chatbot_service
    app.state.websocket_manager = websocket_manager
    
    logger.info("✅ GAIA-BT API Server 준비 완료")
    
    yield
    
    # 종료 시 정리
    logger.info("🛑 GAIA-BT API Server 종료 중...")
    if chatbot_service:
        await chatbot_service.shutdown()
    logger.info("👋 GAIA-BT API Server 종료 완료")

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="GAIA-BT Drug Development Research API",
    description="신약개발 연구 AI 어시스턴트 RESTful API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 도메인 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 예외 처리기
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 처리 - JSON 응답 보장"""
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 예외 처리 - JSON 응답 보장"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

# 라우터 등록
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["mcp"])
app.include_router(session.router, prefix="/api/session", tags=["session"])

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "name": "GAIA-BT API Server",
        "version": "2.0.0",
        "description": "신약개발 연구 AI 어시스턴트",
        "model": OLLAMA_MODEL,
        "endpoints": {
            "chat": "/api/chat",
            "system": "/api/system",
            "mcp": "/api/mcp",
            "session": "/api/session",
            "docs": "/docs",
            "websocket": "/ws"
        }
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    service = app.state.chatbot_service
    
    return {
        "status": "healthy",
        "model": service.current_model if service else None,
        "mode": service.current_mode if service else None,
        "mcp_enabled": service.mcp_enabled if service else False,
        "debug": service.debug_mode if service else False
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket 엔드포인트 - 실시간 스트리밍 지원"""
    manager = app.state.websocket_manager
    service = app.state.chatbot_service
    
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_json()
            
            # 메시지 타입에 따른 처리
            message_type = data.get("type", "chat")
            
            if message_type == "chat":
                # 채팅 메시지 처리
                user_input = data.get("message", "")
                
                # 스트리밍 응답 생성
                async for chunk in service.generate_streaming_response(user_input, session_id):
                    await manager.send_message(session_id, {
                        "type": "chat_chunk",
                        "content": chunk,
                        "done": False
                    })
                
                # 완료 신호
                await manager.send_message(session_id, {
                    "type": "chat_chunk",
                    "content": "",
                    "done": True
                })
                
            elif message_type == "command":
                # 명령어 처리
                command = data.get("command", "")
                result = await service.process_command(command, session_id)
                
                await manager.send_message(session_id, {
                    "type": "command_result",
                    "result": result
                })
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"WebSocket 연결 해제: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket 오류: {e}")
        manager.disconnect(session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)