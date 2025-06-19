"""
GAIA-BT WebUI FastAPI Application
기존 CLI 시스템과 완전 통합된 웹 API 서버
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any
import sys
from pathlib import Path

# GAIA-BT Core 시스템 경로 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

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
    logger.info("🚀 GAIA-BT WebUI API Server 시작 중...")
    
    # 서비스 초기화
    chatbot_service = ChatbotService()
    await chatbot_service.initialize()
    
    websocket_manager = WebSocketManager()
    
    # 의존성 주입을 위한 상태 저장
    app.state.chatbot_service = chatbot_service
    app.state.websocket_manager = websocket_manager
    
    logger.info("✅ GAIA-BT WebUI API Server 준비 완료")
    
    yield
    
    # 종료 시 정리
    logger.info("🛑 GAIA-BT WebUI API Server 종료 중...")
    if chatbot_service:
        await chatbot_service.shutdown()
    logger.info("👋 GAIA-BT WebUI API Server 종료 완료")

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="GAIA-BT Drug Development Research WebUI API",
    description="""
    # 🧬 GAIA-BT 신약개발 연구 AI 어시스턴트 WebUI API
    
    신약개발 전문 AI 어시스턴트의 모든 기능을 웹에서 사용할 수 있는 RESTful API 및 WebSocket 서비스입니다.
    
    ## 🎯 주요 기능
    
    ### 💬 채팅 시스템
    - **실시간 스트리밍**: 단어별 점진적 응답 생성
    - **다중 세션**: 독립적인 대화 세션 관리
    - **모드 전환**: 일반 모드 ↔ Deep Research 모드
    
    ### 🔬 Deep Research 시스템
    - **MCP 통합**: 다중 데이터베이스 동시 검색
    - **논문 검색**: PubMed, PubTator3 통합
    - **임상시험**: ClinicalTrials.gov 데이터
    - **화학 정보**: ChEMBL, DrugBank 연동
    - **타겟 분석**: OpenTargets 플랫폼
    
    ### 🎯 전문 프롬프트
    - **임상시험**: 환자 중심 약물 개발
    - **연구 분석**: 문헌 분석 및 증거 종합
    - **의약화학**: 분자 설계 및 구조 분석
    - **규제 전문**: 글로벌 승인 프로세스
    
    ## 🚀 사용 예시
    
    ### 기본 채팅
    ```bash
    curl -X POST "/api/chat/message" \\
      -H "Content-Type: application/json" \\
      -d '{"message": "아스피린의 작용 메커니즘은?", "session_id": "my_session"}'
    ```
    
    ### Deep Research 활성화
    ```bash
    curl -X POST "/api/mcp/start" \\
      -H "Content-Type: application/json" \\
      -d '{"session_id": "my_session"}'
    ```
    
    ### 프롬프트 변경
    ```bash
    curl -X POST "/api/system/prompt" \\
      -H "Content-Type: application/json" \\
      -d '{"prompt_type": "clinical", "session_id": "my_session"}'
    ```
    
    ## 🔌 WebSocket 연결
    
    실시간 스트리밍을 위한 WebSocket 엔드포인트:
    ```
    ws://localhost:8000/ws/{session_id}
    ```
    
    ## 📖 추가 정보
    
    - **GitHub**: [GAIA-BT Repository](https://github.com/your-repo/gaia-bt)
    - **문서**: [사용자 가이드](https://your-docs.com)
    - **지원**: [Issues](https://github.com/your-repo/gaia-bt/issues)
    """,
    version="2.0.1",
    lifespan=lifespan,
    contact={
        "name": "GAIA-BT Development Team",
        "email": "support@gaia-bt.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    tags_metadata=[
        {
            "name": "chat",
            "description": "💬 **채팅 시스템** - AI와의 대화 및 스트리밍 응답",
            "externalDocs": {
                "description": "채팅 사용 가이드",
                "url": "https://docs.gaia-bt.com/chat",
            },
        },
        {
            "name": "system", 
            "description": "⚙️ **시스템 관리** - 모델, 프롬프트, 설정 관리",
            "externalDocs": {
                "description": "시스템 설정 가이드",
                "url": "https://docs.gaia-bt.com/system",
            },
        },
        {
            "name": "mcp",
            "description": "🔬 **MCP 제어** - Deep Research 모드 및 데이터베이스 검색",
            "externalDocs": {
                "description": "MCP 사용 가이드", 
                "url": "https://docs.gaia-bt.com/mcp",
            },
        },
        {
            "name": "session",
            "description": "👥 **세션 관리** - 다중 대화 세션 생성 및 관리",
            "externalDocs": {
                "description": "세션 관리 가이드",
                "url": "https://docs.gaia-bt.com/session",
            },
        },
    ]
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js 개발 서버  
        "http://localhost:3001",  # Next.js 대안 포트
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://localhost:3000",
        "https://localhost:3001", 
        "*"  # 개발 환경에서는 모든 오리진 허용
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["mcp"])
app.include_router(session.router, prefix="/api/session", tags=["session"])

@app.get("/", 
         summary="🏠 API 서버 정보",
         description="GAIA-BT WebUI API 서버의 기본 정보와 사용 가능한 엔드포인트를 반환합니다.",
         response_description="서버 정보 및 엔드포인트 목록")
async def root():
    """
    ## API 서버 루트 엔드포인트
    
    GAIA-BT WebUI API 서버의 기본 정보를 제공합니다.
    
    ### 반환 정보
    - 서버 이름 및 버전
    - 현재 AI 모델
    - 사용 가능한 API 엔드포인트
    - 문서 링크
    """
    return {
        "name": "GAIA-BT WebUI API Server",
        "version": "2.0.1",
        "description": "신약개발 연구 AI 어시스턴트",
        "model": OLLAMA_MODEL,
        "features": [
            "실시간 스트리밍 채팅",
            "Deep Research 모드", 
            "다중 세션 관리",
            "전문 프롬프트 시스템",
            "MCP 데이터베이스 통합"
        ],
        "endpoints": {
            "chat": "/api/chat",
            "system": "/api/system", 
            "mcp": "/api/mcp",
            "session": "/api/session",
            "docs": "/docs",
            "websocket": "/ws/{session_id}"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }

@app.get("/health",
         summary="🏥 헬스 체크", 
         description="API 서버의 상태를 확인합니다.",
         response_description="서버 상태 정보")
async def health_check():
    """
    ## 헬스 체크 엔드포인트
    
    API 서버와 연결된 서비스들의 상태를 확인합니다.
    
    ### 확인 항목
    - API 서버 상태
    - 현재 AI 모델
    - 현재 모드 (일반/Deep Research)
    - MCP 활성화 여부
    - 디버그 모드 상태
    """
    service = app.state.chatbot_service
    
    return {
        "status": "healthy",
        "server": "GAIA-BT WebUI API",
        "version": "2.0.1",
        "model": service.current_model if service else OLLAMA_MODEL,
        "mode": service.current_mode if service else "normal",
        "mcp_enabled": service.mcp_enabled if service else False,
        "debug": service.debug_mode if service else False,
        "active_sessions": len(service.sessions) if service else 0
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    ## WebSocket 엔드포인트
    
    실시간 스트리밍 채팅을 위한 WebSocket 연결을 제공합니다.
    
    ### 연결 방법
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/my_session');
    ```
    
    ### 메시지 포맷
    
    **보내기:**
    ```json
    {
        "type": "chat",
        "message": "사용자 메시지"
    }
    ```
    
    **받기:**
    ```json
    {
        "type": "chat_chunk", 
        "content": "AI 응답 청크",
        "done": false
    }
    ```
    """
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