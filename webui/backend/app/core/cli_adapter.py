"""
GAIA-BT CLI System Adapter
CLI 시스템과 WebUI 간 브리지 패턴 구현
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, AsyncGenerator
import json
import logging

# GAIA-BT CLI 시스템 import
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

logger = logging.getLogger(__name__)

class CLIAdapter:
    """
    GAIA-BT CLI 시스템과 WebUI 간 어댑터 클래스
    CLI 기능을 WebUI에서 사용할 수 있도록 래핑
    """
    
    def __init__(self):
        self.chatbot: Optional[Any] = None
        self.research_manager: Optional[Any] = None
        self.mcp_commands: Optional[Any] = None
        self._sessions: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self) -> bool:
        """CLI 시스템 초기화"""
        try:
            # GAIA-BT CLI 시스템 동적 import
            from app.cli.chatbot import DrugDevelopmentChatbot
            from app.core.research_manager import ResearchManager
            from app.cli.mcp_commands import MCPCommands
            
            # DrugDevelopmentChatbot 초기화
            self.chatbot = DrugDevelopmentChatbot()
            await self.chatbot.initialize()
            
            # ResearchManager 초기화
            self.research_manager = ResearchManager()
            
            # MCPCommands 초기화 
            self.mcp_commands = MCPCommands()
            
            logger.info("CLI Adapter initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize CLI Adapter: {e}")
            return False
    
    async def create_session(self, session_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """새로운 채팅 세션 생성"""
        try:
            session_config = config or {}
            
            self._sessions[session_id] = {
                'config': session_config,
                'history': [],
                'mode': session_config.get('mode', 'normal'),
                'prompt_type': session_config.get('prompt_type', 'default'),
                'created_at': asyncio.get_event_loop().time(),
                'last_activity': asyncio.get_event_loop().time()
            }
            
            return {
                'session_id': session_id,
                'status': 'created',
                'config': session_config
            }
            
        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            raise
    
    async def send_message(
        self, 
        session_id: str, 
        message: str,
        stream: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """메시지 처리 및 스트리밍 응답"""
        
        if session_id not in self._sessions:
            yield {
                'type': 'error',
                'message': f'Session {session_id} not found'
            }
            return
        
        session = self._sessions[session_id]
        session['last_activity'] = asyncio.get_event_loop().time()
        
        try:
            # 사용자 메시지 히스토리에 추가
            session['history'].append({
                'role': 'user',
                'content': message,
                'timestamp': asyncio.get_event_loop().time()
            })
            
            yield {
                'type': 'message_received',
                'session_id': session_id,
                'message': message
            }
            
            # 현재 모드에 따라 처리 방식 결정
            mode = session.get('mode', 'normal')
            
            if mode == 'mcp' or mode == 'deep_research':
                # Deep Research 모드 - MCP 통합 검색
                async for response_chunk in self._process_deep_research(message, session_id):
                    yield response_chunk
            else:
                # 일반 모드 - 기본 AI 응답
                async for response_chunk in self._process_normal_chat(message, session_id):
                    yield response_chunk
                    
        except Exception as e:
            logger.error(f"Error processing message in session {session_id}: {e}")
            yield {
                'type': 'error',
                'message': str(e),
                'session_id': session_id
            }
    
    async def _process_normal_chat(
        self, 
        message: str, 
        session_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """일반 모드 채팅 처리"""
        
        yield {
            'type': 'thinking_start',
            'session_id': session_id
        }
        
        try:
            # Mock 응답 (실제 구현에서는 CLI 챗봇 사용)
            response = f"신약개발 AI 어시스턴트 응답: {message}에 대한 전문적인 분석을 제공합니다."
            
            # 응답을 청크 단위로 스트리밍
            words = response.split(' ')
            chunk_size = 3
            
            for i in range(0, len(words), chunk_size):
                chunk = ' '.join(words[i:i + chunk_size])
                
                yield {
                    'type': 'response_chunk',
                    'content': chunk + (' ' if i + chunk_size < len(words) else ''),
                    'session_id': session_id
                }
                
                await asyncio.sleep(0.05)
            
            # 응답을 세션 히스토리에 추가
            session = self._sessions[session_id]
            session['history'].append({
                'role': 'assistant',
                'content': response,
                'timestamp': asyncio.get_event_loop().time()
            })
            
            yield {
                'type': 'response_complete',
                'session_id': session_id
            }
            
        except Exception as e:
            yield {
                'type': 'error',
                'message': f"채팅 처리 오류: {str(e)}",
                'session_id': session_id
            }
    
    async def _process_deep_research(
        self, 
        message: str, 
        session_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Deep Research 모드 처리"""
        
        yield {
            'type': 'deep_research_start',
            'session_id': session_id
        }
        
        try:
            # MCP 검색 시작
            yield {
                'type': 'mcp_search_start',
                'message': '🔬 통합 MCP Deep Search 수행 중...',
                'session_id': session_id
            }
            
            # Mock 검색 결과
            search_results = {
                'pubmed': [
                    {'title': 'Example Research Paper', 'authors': 'Smith et al.', 'year': 2024}
                ],
                'chembl': [
                    {'compound': 'Example Compound', 'activity': 'High', 'target': 'Example Target'}
                ]
            }
            
            yield {
                'type': 'mcp_search_results',
                'results': search_results,
                'session_id': session_id
            }
            
            # Mock AI 응답
            response = f"Deep Research 분석 결과: {message}에 대한 종합적인 과학적 분석을 제공합니다. 검색된 논문과 화합물 데이터를 바탕으로 상세한 답변을 드립니다."
            
            # 응답 스트리밍
            words = response.split(' ')
            chunk_size = 3
            
            for i in range(0, len(words), chunk_size):
                chunk = ' '.join(words[i:i + chunk_size])
                
                yield {
                    'type': 'response_chunk',
                    'content': chunk + (' ' if i + chunk_size < len(words) else ''),
                    'session_id': session_id,
                    'enhanced': True
                }
                
                await asyncio.sleep(0.05)
            
            # 응답을 세션 히스토리에 추가
            session = self._sessions[session_id]
            session['history'].append({
                'role': 'assistant',
                'content': response,
                'timestamp': asyncio.get_event_loop().time(),
                'search_results': search_results
            })
            
            yield {
                'type': 'deep_research_complete',
                'session_id': session_id
            }
            
        except Exception as e:
            yield {
                'type': 'error',
                'message': f"Deep Research 오류: {str(e)}",
                'session_id': session_id
            }
    
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """세션 정보 조회"""
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self._sessions[session_id]
        return {
            'session_id': session_id,
            'mode': session['mode'],
            'prompt_type': session['prompt_type'],
            'message_count': len(session['history']),
            'created_at': session['created_at'],
            'last_activity': session['last_activity']
        }

# 글로벌 CLI 어댑터 인스턴스
cli_adapter = CLIAdapter()