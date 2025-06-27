"""
GAIA-BT FastAPI Application
메인 API 서버 - 모든 챗봇 기능을 RESTful API로 제공
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
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
    
    # 1. Ollama 모델 상태 검증 및 자동 시작 (최우선)
    validation_result = None
    try:
        from app.utils.startup_validator import validate_ollama_startup
        validation_result = await validate_ollama_startup()
        
        if not validation_result["validation_success"]:
            error_msg = f"❌ Ollama 모델 검증 실패: {validation_result['error']}"
            logger.error(error_msg)
            logger.error(f"📍 실패 단계: {validation_result['stage']}")
            
            # 서비스 연결 실패인 경우에만 서버 시작 중단
            if validation_result['stage'] in ['service_check', 'no_models_installed']:
                logger.error("🚨 크리티컬 오류 - API 서버 시작 중단")
                raise RuntimeError(f"API 서버 시작 불가: {validation_result['error']}")
            else:
                # 모델 시작 관련 오류는 경고로만 처리하고 서버는 계속 시작
                logger.warning(f"⚠️ Ollama 모델 검증 실패하지만 서버는 계속 시작: {validation_result['error']}")
                validation_result["validation_success"] = True  # 강제로 성공으로 변경
                validation_result["message"] = f"서버 시작 (모델 검증 실패: {validation_result['error']})"
        else:
            logger.info(f"✅ Ollama 모델 검증 성공: {validation_result.get('message', '모델 준비 완료')}")
            if validation_result.get("started_model"):
                logger.info(f"🎯 자동 시작된 모델: {validation_result['started_model']}")
                
    except Exception as e:
        error_msg = f"❌ Ollama 모델 검증 중 예외 발생: {str(e)}"
        logger.error(error_msg)
        
        # 크리티컬 서비스 오류인지 확인
        if "연결" in str(e) or "service" in str(e).lower() or "tags" in str(e).lower():
            logger.error("🚨 Ollama 서비스 연결 불가 - 서버 시작 중단")
            raise RuntimeError(f"API 서버 시작 불가: {error_msg}")
        else:
            # 기타 오류는 경고로 처리
            logger.warning(f"⚠️ Ollama 검증 중 오류 발생하지만 서버는 계속 시작: {str(e)}")
            validation_result = {
                "validation_success": True,
                "stage": "fallback",
                "message": f"서버 시작 (검증 오류: {str(e)})",
                "running_models": [],
                "started_model": None
            }
    
    # 2. ChatbotService 초기화
    try:
        chatbot_service = ChatbotService()
        await chatbot_service.initialize()
        logger.info("✅ ChatbotService 초기화 완료")
    except Exception as e:
        logger.error(f"❌ ChatbotService 초기화 실패: {str(e)}")
        raise RuntimeError(f"ChatbotService 초기화 실패: {str(e)}")
    
    # 3. WebSocket 매니저 초기화
    try:
        websocket_manager = WebSocketManager()
        logger.info("✅ WebSocketManager 초기화 완료")
    except Exception as e:
        logger.error(f"❌ WebSocketManager 초기화 실패: {str(e)}")
        raise RuntimeError(f"WebSocketManager 초기화 실패: {str(e)}")
    
    # 의존성 주입을 위한 상태 저장
    app.state.chatbot_service = chatbot_service
    app.state.websocket_manager = websocket_manager
    app.state.ollama_validation = validation_result  # 검증 결과도 저장
    
    logger.info("✅ GAIA-BT API Server 준비 완료")
    logger.info(f"🎯 활성 모델: {validation_result.get('running_models', [])}")
    # 시스템 정상 작동 확인
    
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

# UTF-8 인코딩 강제 설정을 위한 미들웨어
class UTF8EncodingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # JSON 응답에 UTF-8 인코딩 명시
        if isinstance(response, JSONResponse):
            response.headers["Content-Type"] = "application/json; charset=utf-8"
        # 스트리밍 응답에 UTF-8 인코딩 명시 (SSE)
        elif isinstance(response, StreamingResponse) and response.media_type == "text/event-stream":
            response.headers["Content-Type"] = "text/event-stream; charset=utf-8"
        
        return response

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진 허용 (개발용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# UTF-8 인코딩 미들웨어 추가
app.add_middleware(UTF8EncodingMiddleware)

# 전역 예외 처리기
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 처리 - JSON 응답 보장"""
    # 상세한 오류 정보 로깅
    error_details = {
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "request_url": str(request.url),
        "request_method": request.method,
        "request_headers": dict(request.headers),
        "traceback": traceback.format_exc()
    }
    
    logger.error(f"🚨 Internal Server Error occurred:")
    logger.error(f"📍 URL: {request.method} {request.url}")
    logger.error(f"🔍 Error Type: {type(exc).__name__}")
    logger.error(f"💬 Error Message: {str(exc)}")
    logger.error(f"📋 Full Traceback:\n{traceback.format_exc()}")
    
    # PromptManager 관련 오류 특별 처리
    if "PromptManager" in str(exc) or "templates" in str(exc):
        logger.error("🎯 PromptManager 관련 오류 감지 - templates property 접근 문제일 가능성")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "type": type(exc).__name__,
            "timestamp": str(asyncio.get_event_loop().time()) if hasattr(asyncio, 'get_event_loop') else None
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
    """헬스 체크 엔드포인트

    우선 순위
    1. 실제로 *running* 상태인 Ollama 모델 목록을 조회해 표시
    2. 실행 중인 모델이 없으면 ChatbotService 의 current_model 사용
    """
    service = app.state.chatbot_service

    from app.utils.ollama_manager import list_running_models  # 늦은 import 로 의존 최소화
    running = await list_running_models()

    # 첫 번째 실행 모델(가장 최근에 띄운 모델)을 대표값으로 사용
    current_model = running[-1] if running else (service.current_model if service else None)

    return {
        "status": "healthy",
        "model": current_model,
        "mode": service.current_mode if service else None,
        "mcp_enabled": service.mcp_enabled if service else False,
        "debug": service.debug_mode if service else False,
        "running_models": running  # UI에서 목록으로도 활용 가능하도록 추가
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

async def test_ollama_model_response(model_name: str = "gemma3-12b:latest") -> dict:
    """Ollama 모델과 실제 대화 테스트를 통한 연결 상태 확인"""
    try:
        from app.utils.ollama_manager import list_running_models, start_model
        
        # 1. 모델이 실행 중인지 확인
        running_models = await list_running_models()
        if model_name not in running_models:
            logger.info(f"모델 '{model_name}' 실행되지 않음, 시작 시도 중...")
            await start_model(model_name)
            running_models = await list_running_models()
        
        # 2. 실제 모델 응답 테스트
        service = app.state.chatbot_service
        if service and service.sessions:
            # 기본 세션의 클라이언트 사용
            default_session = service.sessions.get("default")
            if default_session and hasattr(default_session, 'client'):
                test_message = "Hello"
                
                # 간단한 응답 테스트 (타임아웃 10초)
                import asyncio
                try:
                    response = await asyncio.wait_for(
                        default_session.client.generate(test_message),
                        timeout=10.0
                    )
                    
                    if response and len(response.strip()) > 0:
                        return {
                            "model_ready": True,
                            "model_name": model_name,
                            "running_models": running_models,
                            "test_success": True,
                            "response_length": len(response)
                        }
                    else:
                        return {
                            "model_ready": False,
                            "model_name": model_name,
                            "running_models": running_models,
                            "test_success": False,
                            "error": "Empty response from model"
                        }
                        
                except asyncio.TimeoutError:
                    return {
                        "model_ready": False,
                        "model_name": model_name,
                        "running_models": running_models,
                        "test_success": False,
                        "error": "Model response timeout"
                    }
                    
            else:
                return {
                    "model_ready": False,
                    "model_name": model_name,
                    "running_models": running_models,
                    "test_success": False,
                    "error": "Default session client not available"
                }
                
        else:
            return {
                "model_ready": False,
                "model_name": model_name,
                "running_models": running_models,
                "test_success": False,
                "error": "ChatbotService not available"
            }
            
    except Exception as e:
        logger.error(f"Ollama 모델 테스트 오류: {e}")
        return {
            "model_ready": False,
            "model_name": model_name,
            "running_models": [],
            "test_success": False,
            "error": str(e)
        }

@app.websocket("/ws/status/{session_id}")
async def status_websocket_endpoint(websocket: WebSocket, session_id: str):
    """연결 상태 모니터링 전용 WebSocket 엔드포인트"""
    await websocket.accept()
    
    connected = True
    try:
        import asyncio
        
        while connected:
            # 서버 상태 정보 수집
            try:
                service = app.state.chatbot_service
                
                # 실제 모델 대화 가능 상태 테스트
                model_test_result = await test_ollama_model_response()
                
                status_data = {
                    "type": "status_update",
                    "timestamp": int(asyncio.get_event_loop().time()),
                    "server_healthy": True,
                    "model_ready": model_test_result.get("model_ready", False),
                    "ollama_models": model_test_result.get("running_models", []),
                    "current_model": model_test_result.get("model_name"),
                    "mode": service.current_mode if service else "normal",
                    "mcp_enabled": service.mcp_enabled if service else False,
                    "connected_sessions": len(app.state.websocket_manager.active_connections) if app.state.websocket_manager else 0,
                    "test_result": {
                        "success": model_test_result.get("test_success", False),
                        "error": model_test_result.get("error"),
                        "response_length": model_test_result.get("response_length", 0)
                    }
                }
                
                # WebSocket 연결 상태 확인 후 전송
                if connected and websocket.client_state.value == 1:  # CONNECTED
                    try:
                        await websocket.send_json(status_data)
                    except Exception as send_error:
                        logger.warning(f"Status WebSocket 전송 실패: {send_error}")
                        connected = False
                        break
                else:
                    connected = False
                    break
                
            except Exception as e:
                # 서버 오류 시 상태 정보
                error_data = {
                    "type": "status_update",
                    "timestamp": int(asyncio.get_event_loop().time()),
                    "server_healthy": False,
                    "model_ready": False,
                    "error": str(e),
                    "ollama_models": [],
                    "current_model": None,
                    "test_result": {
                        "success": False,
                        "error": str(e)
                    }
                }
                
                # WebSocket 연결 상태 확인 후 전송
                if connected and websocket.client_state.value == 1:  # CONNECTED
                    try:
                        await websocket.send_json(error_data)
                    except Exception as send_error:
                        logger.warning(f"Error WebSocket 전송 실패: {send_error}")
                        connected = False
                        break
                else:
                    connected = False
                    break
            
            # 10초마다 상태 업데이트 (모델 테스트 포함으로 간격 증가)
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                connected = False
                break
            
    except WebSocketDisconnect:
        logger.info(f"Status WebSocket 연결 해제: {session_id}")
        connected = False
    except Exception as e:
        logger.error(f"Status WebSocket 오류: {e}")
        connected = False

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)