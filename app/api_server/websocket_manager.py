"""
WebSocket Manager
WebSocket 연결 관리 및 메시지 브로드캐스팅
"""

from typing import Dict, List
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    """WebSocket 연결 관리자"""
    
    def __init__(self):
        # session_id -> WebSocket 매핑
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """WebSocket 연결"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket 연결 추가: {session_id}")
        
        # 연결 성공 메시지
        await self.send_message(session_id, {
            "type": "connection",
            "status": "connected",
            "session_id": session_id
        })
    
    def disconnect(self, session_id: str):
        """WebSocket 연결 해제"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket 연결 해제: {session_id}")
    
    async def send_message(self, session_id: str, message: Dict):
        """특정 세션에 메시지 전송"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"메시지 전송 실패 ({session_id}): {e}")
                self.disconnect(session_id)
    
    async def broadcast(self, message: Dict):
        """모든 연결된 클라이언트에 메시지 브로드캐스트"""
        disconnected = []
        
        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"브로드캐스트 실패 ({session_id}): {e}")
                disconnected.append(session_id)
        
        # 실패한 연결 제거
        for session_id in disconnected:
            self.disconnect(session_id)
    
    def get_active_sessions(self) -> List[str]:
        """활성 세션 목록 반환"""
        return list(self.active_connections.keys())
    
    def is_connected(self, session_id: str) -> bool:
        """세션 연결 상태 확인"""
        return session_id in self.active_connections
    
    # Reasoning RAG 전용 메시지 전송 메서드들
    async def send_reasoning_start(self, session_id: str, query: str, mode: str):
        """추론 시작 알림"""
        await self.send_message(session_id, {
            "type": "reasoning_start",
            "query": query,
            "mode": mode,
            "timestamp": self._get_timestamp()
        })
    
    async def send_iteration_start(self, session_id: str, iteration: int, max_iterations: int):
        """반복 시작 알림"""
        await self.send_message(session_id, {
            "type": "iteration_start",
            "iteration": iteration,
            "max_iterations": max_iterations,
            "timestamp": self._get_timestamp()
        })
    
    async def send_query_refined(self, session_id: str, original: str, refined: str):
        """쿼리 개선 알림"""
        await self.send_message(session_id, {
            "type": "query_refined",
            "original_query": original,
            "refined_query": refined,
            "timestamp": self._get_timestamp()
        })
    
    async def send_documents_retrieved(self, session_id: str, count: int, top_score: float):
        """문서 검색 완료 알림"""
        await self.send_message(session_id, {
            "type": "documents_retrieved",
            "document_count": count,
            "top_score": top_score,
            "timestamp": self._get_timestamp()
        })
    
    async def send_relevance_evaluated(self, session_id: str, score: float):
        """관련성 평가 완료 알림"""
        await self.send_message(session_id, {
            "type": "relevance_evaluated",
            "relevance_score": score,
            "timestamp": self._get_timestamp()
        })
    
    async def send_partial_answer(self, session_id: str, answer: str, iteration: int):
        """부분 답변 생성 알림"""
        await self.send_message(session_id, {
            "type": "partial_answer",
            "answer": answer,
            "iteration": iteration,
            "timestamp": self._get_timestamp()
        })
    
    async def send_support_evaluated(self, session_id: str, score: float):
        """지지도 평가 완료 알림"""
        await self.send_message(session_id, {
            "type": "support_evaluated",
            "support_score": score,
            "timestamp": self._get_timestamp()
        })
    
    async def send_iteration_complete(self, session_id: str, iteration: int, should_continue: bool):
        """반복 완료 알림"""
        await self.send_message(session_id, {
            "type": "iteration_complete",
            "iteration": iteration,
            "should_continue": should_continue,
            "timestamp": self._get_timestamp()
        })
    
    async def send_reasoning_complete(self, session_id: str, final_answer: str, confidence: float, total_time: float):
        """추론 완료 알림"""
        await self.send_message(session_id, {
            "type": "reasoning_complete",
            "final_answer": final_answer,
            "confidence_score": confidence,
            "elapsed_time": total_time,
            "timestamp": self._get_timestamp()
        })
    
    async def send_reasoning_error(self, session_id: str, error: str):
        """추론 오류 알림"""
        await self.send_message(session_id, {
            "type": "reasoning_error",
            "error": error,
            "timestamp": self._get_timestamp()
        })
    
    def _get_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().isoformat()