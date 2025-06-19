"""
Session Router - 세션 관리 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import time

from app.api_server.dependencies import get_chatbot_service
from app.api_server.services.chatbot_service import ChatbotService

router = APIRouter()

class SessionCreate(BaseModel):
    """세션 생성 요청"""
    session_id: Optional[str] = None  # 선택적 필드로 변경

class SessionInfo(BaseModel):
    """세션 정보"""
    session_id: str
    model: str
    mode: str
    prompt_type: str
    prompt_description: str
    mcp_enabled: bool
    debug: bool
    mcp_output_visible: bool

@router.post("/create")
async def create_session(
    request: SessionCreate = None,
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """새 세션 생성"""
    # 세션 ID가 제공되지 않으면 자동 생성
    session_id = request.session_id if request and request.session_id else f"session_{int(time.time() * 1000)}"
    
    result = await service.create_session(session_id)
    
    if "error" in result:
        raise HTTPException(400, result["error"])
    
    return result

@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """세션 삭제"""
    result = await service.delete_session(session_id)
    
    if "error" in result:
        raise HTTPException(404, result["error"])
    
    return result

@router.get("/{session_id}", response_model=SessionInfo)
async def get_session_info(
    session_id: str,
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """세션 정보 조회"""
    info = service.get_session_info(session_id)
    
    if "error" in info:
        raise HTTPException(404, info["error"])
    
    return info

@router.get("/")
async def list_sessions(
    service: ChatbotService = Depends(get_chatbot_service)
) -> List[Dict[str, Any]]:
    """모든 세션 목록 조회"""
    return service.get_all_sessions()