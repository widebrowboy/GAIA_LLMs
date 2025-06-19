"""
WebSocket connection handler for real-time communication
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging
from typing import Dict, Set

from ..core.cli_adapter import cli_adapter

logger = logging.getLogger(__name__)

websocket_router = APIRouter()

class ConnectionManager:
    """WebSocket 연결 관리자"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        """WebSocket 연결"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket connected: {connection_id}")
    
    def disconnect(self, connection_id: str):
        """WebSocket 연결 해제"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """개별 메시지 전송"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            await websocket.send_text(json.dumps(message, ensure_ascii=False))

manager = ConnectionManager()

@websocket_router.websocket("/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """채팅용 WebSocket 엔드포인트"""
    connection_id = f"chat_{session_id}"
    await manager.connect(websocket, connection_id)
    
    try:
        # CLI 어댑터 초기화
        if not cli_adapter.chatbot:
            await cli_adapter.initialize()
        
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            
            if message_type == "chat_message":
                # 채팅 메시지 처리
                message = message_data.get("message", "")
                
                # 스트리밍 응답 전송
                async for response_chunk in cli_adapter.send_message(
                    session_id=session_id,
                    message=message,
                    stream=True
                ):
                    await manager.send_personal_message(
                        response_chunk, 
                        connection_id
                    )
                    
            elif message_type == "ping":
                # Heartbeat 응답
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": message_data.get("timestamp")},
                    connection_id
                )
                
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.send_personal_message(
            {"type": "error", "message": str(e)},
            connection_id
        )
        manager.disconnect(connection_id)