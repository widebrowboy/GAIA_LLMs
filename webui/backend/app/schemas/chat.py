"""
Chat-related Pydantic schemas
채팅 관련 데이터 모델 정의
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class ChatSessionCreate(BaseModel):
    """채팅 세션 생성 요청"""
    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="세션 설정 (모드, 프롬프트 타입 등)"
    )

class ChatMessage(BaseModel):
    """채팅 메시지"""
    content: str = Field(..., description="메시지 내용")
    
class ChatSessionInfo(BaseModel):
    """채팅 세션 정보"""
    session_id: str
    mode: str
    prompt_type: str
    message_count: int
    created_at: float
    last_activity: float

class ChatHistory(BaseModel):
    """채팅 히스토리"""
    role: str = Field(..., description="메시지 역할 (user/assistant)")
    content: str = Field(..., description="메시지 내용")
    timestamp: float = Field(..., description="타임스탬프")
    search_results: Optional[Dict[str, Any]] = Field(
        default=None,
        description="MCP 검색 결과 (Deep Research 모드)"
    )

class StreamResponse(BaseModel):
    """스트리밍 응답 청크"""
    type: str = Field(..., description="응답 타입")
    content: Optional[str] = Field(default=None, description="응답 내용")
    session_id: str = Field(..., description="세션 ID")
    enhanced: Optional[bool] = Field(default=False, description="Deep Research 응답 여부")
    
class MCPSearchRequest(BaseModel):
    """MCP 검색 요청"""
    query: str = Field(..., description="검색 쿼리")
    sources: Optional[List[str]] = Field(
        default=None,
        description="검색할 소스 (pubmed, chembl, clinical_trials 등)"
    )
    
class MCPSearchResult(BaseModel):
    """MCP 검색 결과"""
    query: str
    results: Dict[str, List[Dict[str, Any]]]
    search_time: float