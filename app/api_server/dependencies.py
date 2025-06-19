"""
FastAPI Dependencies
의존성 주입을 위한 함수들
"""

from fastapi import Request

from app.api_server.services.chatbot_service import ChatbotService
from app.api_server.websocket_manager import WebSocketManager

def get_chatbot_service(request: Request) -> ChatbotService:
    """ChatbotService 인스턴스 가져오기"""
    return request.app.state.chatbot_service

def get_websocket_manager(request: Request) -> WebSocketManager:
    """WebSocketManager 인스턴스 가져오기"""
    return request.app.state.websocket_manager