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