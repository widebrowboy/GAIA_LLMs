"""
ChatbotService - 핵심 챗봇 기능을 제공하는 서비스 클래스
기존 DrugDevelopmentChatbot의 기능을 서비스로 분리
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime
import logging

from app.cli.chatbot import DrugDevelopmentChatbot, Config
from app.utils.config import OLLAMA_MODEL
from app.utils.prompt_manager import get_prompt_manager

logger = logging.getLogger(__name__)

class ChatbotService:
    """챗봇 핵심 기능을 제공하는 서비스 클래스"""
    
    def __init__(self):
        self.sessions: Dict[str, DrugDevelopmentChatbot] = {}
        self.prompt_manager = get_prompt_manager()
        self.initialized = False
        
    async def initialize(self):
        """서비스 초기화"""
        if not self.initialized:
            logger.info("ChatbotService 초기화 중...")
            # 기본 세션 생성
            await self.create_session("default")
            self.initialized = True
            logger.info("ChatbotService 초기화 완료")
    
    async def shutdown(self):
        """서비스 종료"""
        logger.info("ChatbotService 종료 중...")
        # 모든 세션의 MCP 서버 종료
        for session_id, chatbot in self.sessions.items():
            if chatbot.mcp_commands and chatbot.config.mcp_enabled:
                try:
                    await chatbot.mcp_commands.stop_all_servers()
                except Exception as e:
                    logger.error(f"세션 {session_id} MCP 종료 오류: {e}")
        
        self.sessions.clear()
        logger.info("ChatbotService 종료 완료")
    
    async def create_session(self, session_id: str) -> Dict[str, Any]:
        """새로운 챗봇 세션 생성"""
        if session_id in self.sessions:
            return {"error": f"세션 {session_id}가 이미 존재합니다"}
        
        config = Config(debug_mode=False)
        chatbot = DrugDevelopmentChatbot(config)
        
        # API 연결 확인
        status = await chatbot.client.check_availability()
        if not status:
            return {"error": "Ollama API를 사용할 수 없습니다"}
        
        # 모델 확인
        model_check = await chatbot.auto_select_model()
        if not model_check:
            return {"error": "사용 가능한 모델이 없습니다"}
        
        self.sessions[session_id] = chatbot
        
        return {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "model": chatbot.client.model_name,
            "mode": "normal",
            "prompt_type": "default",
            "mcp_enabled": False,
            "debug": False
        }
    
    async def delete_session(self, session_id: str) -> Dict[str, Any]:
        """세션 삭제"""
        if session_id not in self.sessions:
            return {"error": f"세션 {session_id}를 찾을 수 없습니다"}
        
        chatbot = self.sessions[session_id]
        
        # MCP 서버 종료
        if chatbot.mcp_commands and chatbot.config.mcp_enabled:
            try:
                await chatbot.mcp_commands.stop_all_servers()
            except Exception as e:
                logger.error(f"MCP 종료 오류: {e}")
        
        del self.sessions[session_id]
        
        return {"message": f"세션 {session_id}가 삭제되었습니다"}
    
    def get_session(self, session_id: str) -> Optional[DrugDevelopmentChatbot]:
        """세션 가져오기"""
        return self.sessions.get(session_id)
    
    async def generate_response(self, session_id: str, message: str) -> Dict[str, Any]:
        """일반 응답 생성"""
        chatbot = self.get_session(session_id)
        if not chatbot:
            return {"error": f"세션 {session_id}를 찾을 수 없습니다"}
        
        try:
            response = await chatbot.generate_response(message, ask_to_save=False)
            return {
                "response": response,
                "mode": "deep_research" if chatbot.config.mcp_enabled else "normal",
                "model": chatbot.client.model_name
            }
        except Exception as e:
            logger.error(f"응답 생성 오류: {e}")
            return {"error": str(e)}
    
    async def generate_streaming_response(
        self, 
        message: str, 
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """스트리밍 응답 생성"""
        chatbot = self.get_session(session_id)
        if not chatbot:
            yield f"오류: 세션 {session_id}를 찾을 수 없습니다"
            return
        
        try:
            # 스트리밍 응답 생성
            async for chunk in chatbot.generate_streaming_response(message):
                yield chunk
        except Exception as e:
            logger.error(f"스트리밍 응답 오류: {e}")
            yield f"오류: {str(e)}"
    
    async def process_command(self, command: str, session_id: str) -> Dict[str, Any]:
        """명령어 처리"""
        chatbot = self.get_session(session_id)
        if not chatbot:
            return {"error": f"세션 {session_id}를 찾을 수 없습니다"}
        
        # 명령어 정규화
        if not command.startswith("/"):
            command = "/" + command
        
        try:
            # 명령어별 처리
            if command == "/help":
                return {"type": "help", "content": self._get_help_text()}
            
            elif command.startswith("/mcp"):
                mcp_args = command[4:].strip()
                if not chatbot.mcp_commands:
                    return {"error": "MCP 기능을 사용할 수 없습니다"}
                
                result = await chatbot.mcp_commands.handle_mcp_command(mcp_args)
                # MCP 활성 상태 확인 (안전한 방식)
                chatbot.config.mcp_enabled = getattr(chatbot.mcp_commands, 'is_mcp_active', lambda: chatbot.mcp_enabled)()
                
                return {
                    "type": "mcp",
                    "command": mcp_args,
                    "result": result,
                    "mcp_enabled": chatbot.config.mcp_enabled
                }
            
            elif command.startswith("/model"):
                parts = command.split(maxsplit=1)
                if len(parts) > 1:
                    result = await chatbot.change_model(parts[1])
                    return {
                        "type": "model",
                        "model": chatbot.client.model_name,
                        "result": result
                    }
                else:
                    return {"error": "사용법: /model <모델명>"}
            
            elif command.startswith("/prompt"):
                parts = command.split(maxsplit=1)
                prompt_type = parts[1] if len(parts) > 1 else None
                result = await chatbot.change_prompt(prompt_type)
                
                return {
                    "type": "prompt",
                    "prompt_type": chatbot.current_prompt_type,
                    "result": result
                }
            
            elif command == "/debug":
                chatbot.config.debug_mode = not chatbot.config.debug_mode
                chatbot.client.set_debug_mode(chatbot.config.debug_mode)
                
                return {
                    "type": "debug",
                    "enabled": chatbot.config.debug_mode,
                    "message": f"디버그 모드가 {'켜짐' if chatbot.config.debug_mode else '꺼짐'}으로 설정되었습니다."
                }
            
            elif command == "/normal":
                await chatbot.switch_to_normal_mode()
                return {
                    "type": "mode",
                    "mode": "normal",
                    "message": "일반 모드로 전환되었습니다."
                }
            
            elif command == "/deep":
                # Deep Research 모드로 전환 (MCP 시작)
                if not chatbot.mcp_commands:
                    return {"error": "MCP 기능을 사용할 수 없습니다"}
                
                result = await chatbot.mcp_commands.handle_mcp_command("start")
                chatbot.config.mcp_enabled = True
                
                return {
                    "type": "mode",
                    "mode": "deep_research",
                    "message": "Deep Research 모드로 전환되었습니다. MCP 통합 검색이 활성화됩니다.",
                    "mcp_enabled": True
                }
            
            elif command == "/mcpshow":
                chatbot.toggle_mcp_output()
                return {
                    "type": "mcpshow",
                    "enabled": chatbot.config.show_mcp_output,
                    "message": f"MCP 출력이 {'표시' if chatbot.config.show_mcp_output else '숨김'}됩니다."
                }
            
            else:
                return {"error": f"알 수 없는 명령어: {command}"}
                
        except Exception as e:
            logger.error(f"명령어 처리 오류: {e}")
            return {"error": str(e)}
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """세션 정보 가져오기"""
        chatbot = self.get_session(session_id)
        if not chatbot:
            return {"error": f"세션 {session_id}를 찾을 수 없습니다"}
        
        # 현재 프롬프트 정보
        prompt_template = self.prompt_manager.get_prompt_template(chatbot.current_prompt_type)
        prompt_desc = prompt_template.description if prompt_template else "기본"
        
        return {
            "session_id": session_id,
            "model": chatbot.client.model_name,
            "mode": "deep_research" if chatbot.config.mcp_enabled else "normal",
            "prompt_type": chatbot.current_prompt_type,
            "prompt_description": prompt_desc,
            "mcp_enabled": chatbot.config.mcp_enabled,
            "debug": chatbot.config.debug_mode,
            "mcp_output_visible": chatbot.config.show_mcp_output,
            "available_models": [],  # TODO: 모델 목록 가져오기
            "available_prompts": list(self.prompt_manager.templates.keys())
        }
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """모든 세션 정보 가져오기"""
        sessions = []
        for session_id in self.sessions:
            info = self.get_session_info(session_id)
            if "error" not in info:
                sessions.append(info)
        return sessions
    
    def _get_help_text(self) -> str:
        """도움말 텍스트"""
        return """
📚 GAIA-BT v2.0 API 도움말

🎯 기본 명령어:
  /help            - 이 도움말 표시
  /debug           - 디버그 모드 토글
  /mcpshow         - MCP 검색 과정 표시 토글
  /normal          - 일반 모드로 전환
  /model <이름>    - AI 모델 변경
  /prompt <모드>   - 전문 프롬프트 변경

🔬 MCP 명령어:
  /mcp start       - 통합 MCP 시스템 시작
  /mcp stop        - MCP 서버 중지
  /mcp status      - MCP 상태 확인

📝 프롬프트 모드:
  - default: 기본 신약개발 AI
  - clinical: 임상시험 전문
  - research: 연구 분석 전문
  - chemistry: 의약화학 전문
  - regulatory: 규제 전문
"""
    
    @property
    def current_model(self) -> str:
        """현재 모델"""
        if "default" in self.sessions:
            return self.sessions["default"].client.model_name
        return OLLAMA_MODEL
    
    @property
    def current_mode(self) -> str:
        """현재 모드"""
        if "default" in self.sessions:
            return "deep_research" if self.sessions["default"].config.mcp_enabled else "normal"
        return "normal"
    
    @property
    def mcp_enabled(self) -> bool:
        """MCP 활성화 여부"""
        if "default" in self.sessions:
            return self.sessions["default"].config.mcp_enabled
        return False
    
    @property
    def debug_mode(self) -> bool:
        """디버그 모드"""
        if "default" in self.sessions:
            return self.sessions["default"].config.debug_mode
        return False