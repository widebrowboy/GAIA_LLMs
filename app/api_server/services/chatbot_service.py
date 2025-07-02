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
from app.utils.config import OLLAMA_MODEL, MAX_CONVERSATION_CONTEXT, MAX_CONVERSATION_HISTORY
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
                    await chatbot.mcp_commands.stop_mcp()
                except Exception as e:
                    logger.error(f"세션 {session_id} MCP 종료 오류: {e}")
        
        self.sessions.clear()
        logger.info("ChatbotService 종료 완료")
    
    async def create_session(self, session_id: str) -> Dict[str, Any]:
        """새로운 챗봇 세션 생성"""
        if session_id in self.sessions:
            return {"error": f"세션 {session_id}가 이미 존재합니다"}
        
        # 현재 실행 중인 모델 감지 또는 사용자 설정 기본 모델 사용
        from app.utils.ollama_manager import list_running_models
        try:
            running_models = await list_running_models()
            if running_models:
                # 실행 중인 모델이 있으면 그것을 사용 (모델 변경 방지)
                current_model = running_models[-1]
                logger.info(f"세션 {session_id} 생성 시 현재 실행 중인 모델 유지: {current_model}")
            else:
                # 실행 중인 모델이 없으면 사용자 설정 기본 모델 사용하지 않고 현재 실행된 모델 유지
                # 모델 변경을 방지하기 위해 현재 클라이언트의 모델을 유지
                current_model = "gemma3-12b:latest"  # 최후 폴백
                logger.info(f"세션 {session_id} 생성 시 실행 중인 모델이 없어 폴백 모델 사용: {current_model}")
        except Exception as e:
            logger.warning(f"실행 중인 모델 감지 실패, 폴백 모델 사용: {e}")
            current_model = "gemma3-12b:latest"
        
        config = Config(debug_mode=False, model=current_model)
        chatbot = DrugDevelopmentChatbot(config)
        
        # API 연결 확인
        status = await chatbot.client.check_availability()
        if not status:
            return {"error": "Ollama API를 사용할 수 없습니다"}
        
        # 모델이 실행 중이라면 auto_select_model 건너뛰기
        if running_models and current_model in running_models:
            logger.info(f"모델 {current_model}이 이미 실행 중이므로 auto_select_model 건너뛰기")
            # 모델명만 설정
            chatbot.client._model_name = current_model
            # 설정 기본값 확인
            if not hasattr(chatbot.client, 'model_name') or chatbot.client.model_name != current_model:
                chatbot.client.model_name = current_model
        else:
            # 모델이 실행 중이지 않다면 현재 설정된 모델을 시작
            logger.info(f"모델 {current_model}이 실행 중이지 않음. 시작 시도 중...")
            try:
                from app.utils.ollama_manager import start_model
                await start_model(current_model)
                chatbot.client._model_name = current_model
                if not hasattr(chatbot.client, 'model_name') or chatbot.client.model_name != current_model:
                    chatbot.client.model_name = current_model
                logger.info(f"✅ 모델 {current_model} 시작 완료")
            except Exception as e:
                logger.error(f"❌ 모델 {current_model} 시작 실패: {e}")
                # auto_select_model 사용을 비활성화하여 자동 모델 변경 방지
                # 대신 현재 모델 설정을 유지하고 경고만 로그
                logger.warning(f"모델 {current_model} 시작 실패, 하지만 auto_select_model 호출 건너뛰기 (자동 모델 변경 방지)")
                chatbot.client._model_name = current_model
                if not hasattr(chatbot.client, 'model_name') or chatbot.client.model_name != current_model:
                    chatbot.client.model_name = current_model
        
        # 기본 프롬프트가 제대로 로드되었는지 확인하고 재로드
        chatbot.current_prompt_type = "default"
        chatbot.system_prompt = self.prompt_manager.get_prompt("default")
        
        # 프롬프트 로드 확인 로그
        if chatbot.system_prompt:
            logger.info(f"세션 {session_id}: default 프롬프트 로드 성공 ({len(chatbot.system_prompt)}자)")
        else:
            logger.warning(f"세션 {session_id}: default 프롬프트 로드 실패, 폴백 사용")
        
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
                await chatbot.mcp_commands.stop_mcp()
            except Exception as e:
                logger.error(f"MCP 종료 오류: {e}")
        
        del self.sessions[session_id]
        
        return {"message": f"세션 {session_id}가 삭제되었습니다"}
    
    def get_session(self, session_id: str) -> Optional[DrugDevelopmentChatbot]:
        """세션 가져오기"""
        return self.sessions.get(session_id)
    
    async def generate_response(self, session_id: str, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """일반 응답 생성"""
        chatbot = self.get_session(session_id)
        if not chatbot:
            # 세션이 없으면 자동으로 생성
            logger.info(f"세션 {session_id}가 없어 자동 생성합니다.")
            session_result = await self.create_session(session_id)
            if "error" in session_result:
                return session_result
            chatbot = self.get_session(session_id)
        
        try:
            # 대화 히스토리가 제공된 경우 챗봇의 컨텍스트를 업데이트
            if conversation_history:
                # 기존 컨텍스트 초기화
                chatbot.context = []
                chatbot.conversation_history = []
                
                # 최근 메시지만 처리하도록 제한 (성능 및 메모리 최적화)
                recent_history = conversation_history[-MAX_CONVERSATION_CONTEXT * 2:] if len(conversation_history) > MAX_CONVERSATION_CONTEXT * 2 else conversation_history
                
                # 대화 히스토리를 챗봇에 복원
                for i, msg in enumerate(recent_history):
                    if msg.get('role') == 'user':
                        # 사용자 메시지를 컨텍스트에 추가
                        chatbot.context.append(msg.get('content', ''))
                        # 짝을 이루는 assistant 응답이 있는지 확인
                        if i + 1 < len(recent_history) and recent_history[i + 1].get('role') == 'assistant':
                            assistant_msg = recent_history[i + 1]
                            # 대화 히스토리에 질문-답변 쌍 추가
                            chatbot.conversation_history.append({
                                "question": msg.get('content', ''),
                                "answer": assistant_msg.get('content', '')
                            })
                
                # 컨텍스트가 설정된 최대값을 초과하면 최근 것만 유지
                if len(chatbot.context) > MAX_CONVERSATION_CONTEXT:
                    chatbot.context = chatbot.context[-MAX_CONVERSATION_CONTEXT:]
                
                # 대화 히스토리도 설정된 최대값으로 제한
                if len(chatbot.conversation_history) > MAX_CONVERSATION_HISTORY:
                    chatbot.conversation_history = chatbot.conversation_history[-MAX_CONVERSATION_HISTORY:]
                
                logger.info(f"세션 {session_id}: {len(chatbot.context)}개의 컨텍스트, {len(chatbot.conversation_history)}개의 대화 히스토리 복원됨")
            
            response = await chatbot.generate_response(message, ask_to_save=False)
            
            # 현재 프롬프트 내용을 포함하여 디버깅에 도움
            current_prompt = self.prompt_manager.get_prompt(chatbot.current_prompt_type)
            
            return {
                "response": response,
                "mode": "deep_research" if chatbot.config.mcp_enabled else "normal",
                "model": chatbot.client.model_name,
                "prompt_type": chatbot.current_prompt_type,
                "debug_info": {
                    "system_prompt_length": len(current_prompt) if current_prompt else 0,
                    "system_prompt_preview": current_prompt[:200] + "..." if current_prompt and len(current_prompt) > 200 else current_prompt
                } if hasattr(chatbot.config, 'debug') and chatbot.config.debug else None
            }
        except Exception as e:
            logger.error(f"응답 생성 오류: {e}")
            return {"error": str(e)}
    
    async def generate_streaming_response(
        self, 
        message: str, 
        session_id: str,
        mode: str = "normal",
        mcp_enabled: bool = False,
        model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """스트리밍 응답 생성"""
        # 모델 전환 로직 비활성화 - 사용자가 선택한 모델을 유지
        # 자동 모델 전환을 하지 않고, 현재 실행 중인 모델을 그대로 사용
        # if model:
        #     from app.utils.ollama_manager import list_running_models
        #     running_models = await list_running_models()
        #     current_running_model = running_models[-1] if running_models else None
        #     
        #     if current_running_model != model:
        #         logger.info(f"요청된 모델 {model}이 현재 실행 중인 모델 {current_running_model}과 다름. 모델 전환 시작...")
        #         switch_result = await self.switch_model_safely(model)
        #         if not switch_result.get("success"):
        #             yield f"오류: 모델 전환 실패 - {switch_result.get('error', 'Unknown error')}"
        #             return
        
        # 대신 현재 실행 중인 모델이 무엇인지만 로깅
        if model:
            from app.utils.ollama_manager import list_running_models
            try:
                running_models = await list_running_models()
                current_running_model = running_models[-1] if running_models else None
                logger.info(f"🎯 요청된 모델: {model}, 현재 실행 중인 모델: {current_running_model} (자동 전환 비활성화됨)")
            except Exception as e:
                logger.warning(f"실행 중인 모델 확인 실패: {e}")
        
        chatbot = self.get_session(session_id)
        if not chatbot:
            # 세션이 없으면 자동으로 생성
            logger.info(f"세션 {session_id}가 없어 자동 생성합니다.")
            session_result = await self.create_session(session_id)
            if "error" in session_result:
                yield f"오류: {session_result['error']}"
                return
            chatbot = self.get_session(session_id)
        
        # 세션의 모드 및 MCP 설정 업데이트
        if hasattr(chatbot, 'current_mode'):
            chatbot.current_mode = mode
        if hasattr(chatbot, 'mcp_enabled'):
            chatbot.mcp_enabled = mcp_enabled
        
        # 프롬프트가 올바르게 로드되었는지 확인하고 필요시 재로드
        if not chatbot.system_prompt or len(chatbot.system_prompt) < 100:
            chatbot.system_prompt = self.prompt_manager.get_prompt(chatbot.current_prompt_type)
            logger.info(f"세션 {session_id}: 프롬프트 재로드 완료 ({len(chatbot.system_prompt)}자)")
        
        logger.info(f"세션 {session_id} 모드 설정: {mode}, MCP: {mcp_enabled}, 프롬프트: {chatbot.current_prompt_type}")
        
        try:
            # Ollama 연결 상태 확인
            connection_status = await chatbot.client.check_ollama_connection()
            if not connection_status["connected"]:
                error_msg = f"[연결 오류] {connection_status['error']}"
                logger.error(error_msg)
                yield error_msg
                return
            
            # 모델이 실행되지 않은 경우 현재 모델 시작 (다른 모델로 변경하지 않음)
            if not connection_status.get("current_model_running", False):
                logger.info(f"모델 '{chatbot.client.model}'이 실행되지 않음. 현재 모델 시작 시도 중... (자동 모델 변경 비활성화)")
                start_result = await chatbot.client.ensure_model_running()
                if not start_result["success"]:
                    error_msg = f"[모델 시작 오류] {start_result['message']}"
                    logger.error(error_msg)
                    # 모델 시작 실패 시에도 기존 모델 설정 유지하고 계속 진행
                    logger.warning(f"모델 시작 실패했지만 기존 모델 설정 유지하고 계속 진행")
                    # yield error_msg
                    # return
                else:
                    logger.info(f"✅ {start_result['message']}")
            
            # 스트리밍 응답 생성
            async for chunk in chatbot.generate_streaming_response(message):
                yield chunk
        except Exception as e:
            logger.error(f"스트리밍 응답 오류: {e}")
            if "connection" in str(e).lower() or "ollama" in str(e).lower():
                yield f"[연결 오류] Ollama 서비스 연결 실패: {str(e)}"
            else:
                yield f"오류: {str(e)}"
    
    async def process_command(self, command: str, session_id: str) -> Dict[str, Any]:
        """명령어 처리"""
        chatbot = self.get_session(session_id)
        if not chatbot:
            # 세션이 없으면 자동으로 생성
            logger.info(f"세션 {session_id}가 없어 자동 생성합니다.")
            session_result = await self.create_session(session_id)
            if "error" in session_result:
                return session_result
            chatbot = self.get_session(session_id)
        
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
            "available_models": ["gemma3-12b:latest", "txgemma-chat:latest", "txgemma-predict:latest", "Gemma3:27b-it-q4_K_M"],
            "available_prompts": list(self.prompt_manager.templates.keys()) if hasattr(self.prompt_manager, 'templates') and self.prompt_manager.templates else []
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
    
    def update_current_model(self, model_name: str) -> None:
        """현재 모델 업데이트"""
        if "default" in self.sessions:
            # OllamaClient의 _model_name 속성을 직접 수정
            self.sessions["default"].client._model_name = model_name
            logger.info(f"현재 모델을 '{model_name}'로 업데이트했습니다.")
    
    async def switch_model_safely(self, new_model_name: str) -> Dict[str, Any]:
        """안전한 모델 전환 - 기존 모델 중지 후 새 모델 실행"""
        try:
            from app.utils.ollama_manager import stop_all_models, ensure_single_model_running
            
            logger.info(f"🔄 안전한 모델 전환 시작: {new_model_name}")
            
            # 1단계: 기존 실행 중인 모든 모델 중지
            logger.info("🛑 기존 실행 중인 모든 모델 중지...")
            try:
                await stop_all_models()
                logger.info("✅ 모든 모델 중지 완료")
            except Exception as stop_error:
                logger.warning(f"모델 중지 중 일부 오류 발생: {stop_error}")
            
            # 2단계: 새 모델 시작 (단일 모델 보장)
            logger.info(f"🚀 새 모델 시작: {new_model_name}")
            try:
                await ensure_single_model_running(new_model_name)
                logger.info(f"✅ 모델 전환 완료: {new_model_name}")
                
                # 3단계: 챗봇 세션의 모델 정보 업데이트
                self.update_current_model(new_model_name)
                
                return {
                    "success": True,
                    "message": f"모델이 '{new_model_name}'로 성공적으로 전환되었습니다.",
                    "current_model": new_model_name,
                    "previous_models_stopped": True
                }
            except Exception as start_error:
                logger.error(f"❌ 새 모델 시작 실패: {start_error}")
                return {
                    "success": False,
                    "error": f"새 모델 시작 실패: {str(start_error)}"
                }
                
        except Exception as e:
            logger.error(f"❌ 모델 전환 중 오류 발생: {e}")
            return {
                "success": False,
                "error": f"모델 전환 중 오류 발생: {str(e)}"
            }