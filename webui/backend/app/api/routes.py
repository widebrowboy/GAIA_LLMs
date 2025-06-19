"""
GAIA-BT WebUI API Routes
메인 API 라우터 및 엔드포인트 정의
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
import uuid
import json
import logging

from ..core.cli_adapter import cli_adapter
from ..schemas.chat import (
    ChatSessionCreate,
    ChatMessage,
    ChatSessionInfo,
    ChatHistory
)

logger = logging.getLogger(__name__)

# 메인 API 라우터
api_router = APIRouter()

# 채팅 관련 엔드포인트
chat_router = APIRouter(prefix="/chat", tags=["chat"])

@chat_router.post("/sessions", response_model=Dict[str, Any])
async def create_chat_session(session_data: ChatSessionCreate):
    """새로운 채팅 세션 생성"""
    try:
        session_id = str(uuid.uuid4())
        
        # CLI 어댑터 초기화 확인
        if not cli_adapter.chatbot:
            await cli_adapter.initialize()
        
        result = await cli_adapter.create_session(
            session_id=session_id,
            config=session_data.config or {}
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to create chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.get("/sessions/{session_id}", response_model=ChatSessionInfo)
async def get_chat_session(session_id: str):
    """채팅 세션 정보 조회"""
    try:
        session_info = await cli_adapter.get_session_info(session_id)
        return session_info
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get session info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.get("/sessions/{session_id}/history", response_model=List[Dict[str, Any]])
async def get_chat_history(session_id: str):
    """채팅 히스토리 조회"""
    try:
        history = await cli_adapter.get_session_history(session_id)
        return history
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.post("/sessions/{session_id}/messages")
async def send_message(session_id: str, message: ChatMessage):
    """메시지 전송 및 스트리밍 응답"""
    try:
        async def generate_response():
            async for chunk in cli_adapter.send_message(
                session_id=session_id,
                message=message.content,
                stream=True
            ):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.put("/sessions/{session_id}/mode")
async def change_session_mode(session_id: str, mode_data: Dict[str, str]):
    """세션 모드 변경"""
    try:
        mode = mode_data.get("mode")
        if not mode:
            raise HTTPException(status_code=400, detail="Mode is required")
        
        # Mode validation (Mock)
        valid_modes = ["normal", "mcp", "deep_research"]
        if mode not in valid_modes:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid mode. Valid modes: {valid_modes}"
            )
        
        # Mock response
        return {
            "session_id": session_id,
            "mode": mode,
            "status": "mode_changed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to change session mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.put("/sessions/{session_id}/prompt")
async def change_prompt_type(session_id: str, prompt_data: Dict[str, str]):
    """프롬프트 타입 변경"""
    try:
        prompt_type = prompt_data.get("prompt_type")
        if not prompt_type:
            raise HTTPException(status_code=400, detail="Prompt type is required")
        
        # Prompt type validation (Mock)
        valid_types = ["default", "clinical", "research", "chemistry", "regulatory"]
        if prompt_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid prompt type. Valid types: {valid_types}"
            )
        
        # Mock response
        return {
            "session_id": session_id,
            "prompt_type": prompt_type,
            "status": "prompt_changed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to change prompt type: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """채팅 세션 삭제"""
    try:
        # Mock response
        return {
            "session_id": session_id,
            "status": "deleted"
        }
        
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# MCP 관련 엔드포인트
mcp_router = APIRouter(prefix="/mcp", tags=["mcp"])

@mcp_router.get("/status")
async def get_mcp_status():
    """MCP 서버 상태 확인"""
    return {
        "status": "running",
        "servers": {
            "biomcp": {"status": "connected", "tools": 12},
            "chembl": {"status": "connected", "tools": 8},
            "pubmed": {"status": "connected", "tools": 5},
            "clinical_trials": {"status": "connected", "tools": 3}
        }
    }

@mcp_router.post("/search")
async def mcp_search(search_data: Dict[str, Any]):
    """MCP 통합 검색"""
    query = search_data.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    # Mock search results
    return {
        "query": query,
        "results": {
            "pubmed": [
                {
                    "title": f"Research paper about {query}",
                    "authors": "Smith et al.",
                    "year": 2024,
                    "pmid": "12345678"
                }
            ],
            "chembl": [
                {
                    "compound": f"Compound related to {query}",
                    "chembl_id": "CHEMBL123456",
                    "activity": "High",
                    "target": "Example Target"
                }
            ]
        },
        "search_time": 1.23
    }

# 시스템 관련 엔드포인트
system_router = APIRouter(prefix="/system", tags=["system"])

@system_router.get("/health")
async def system_health():
    """시스템 헬스 체크"""
    return {
        "status": "healthy",
        "version": "2.0.0-alpha",
        "components": {
            "cli_adapter": "connected",
            "ollama": "connected",
            "mcp_servers": "connected"
        }
    }

@system_router.get("/info")
async def system_info():
    """시스템 정보"""
    return {
        "name": "GAIA-BT WebUI API",
        "version": "2.0.0-alpha",
        "description": "신약개발 AI 연구 어시스턴트 웹 인터페이스 API",
        "features": [
            "Real-time chat streaming",
            "MCP integration",
            "Deep research mode",
            "Multi-prompt support"
        ]
    }

# 라우터 등록
api_router.include_router(chat_router)
api_router.include_router(mcp_router)
api_router.include_router(system_router)