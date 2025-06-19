"""
title: GAIA-BT MCP Integration Pipeline
author: GAIA-BT Team
date: 2024-06-18
version: 1.0
license: MIT
description: Deep Research Mode with MCP integration for drug development
requirements: requests, asyncio, subprocess
"""

import os
import sys
import json
import asyncio
import subprocess
from typing import List, Optional, Iterator, Dict, Any
from pydantic import BaseModel, Field

# Add GAIA-BT to Python path
GAIA_BT_PATHS = [
    os.environ.get("GAIA_BT_PATH", "/gaia-bt"),
    "/home/gaia-bt/workspace/GAIA_LLMs",
    "/app/gaia-bt",
    "/gaia-bt"
]

for path in GAIA_BT_PATHS:
    if path and os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

try:
    from app.cli.chatbot import DrugDevelopmentChatbot
    from app.core.research_manager import ResearchManager
    from app.cli.mcp_commands import MCPCommands
    from app.utils.prompt_manager import get_prompt_manager, get_system_prompt
    from app.utils.config import Config
    GAIA_BT_AVAILABLE = True
    print("✅ GAIA-BT modules imported successfully")
except ImportError as e:
    print(f"⚠️ GAIA-BT modules not available: {e}")
    print(f"   Python path: {sys.path[:3]}...")
    GAIA_BT_AVAILABLE = False


class Pipeline:
    def __init__(self):
        self.name = "GAIA-BT MCP Pipeline"
        self.description = "신약개발 전문 AI 어시스턴트 with Deep Research Mode"
        
        # Initialize valves (configuration)
        self.valves = self.Valves(
            **{
                "GAIA_BT_MODE": "normal",
                "MCP_OUTPUT_ENABLED": False,
                "SELECTED_PROMPT_MODE": "default",
                "DEFAULT_MODEL": "gemma3:27b-it-q4_K_M",
                "ENABLE_DEEP_SEARCH": True,
                "DEBUG_MODE": False
            }
        )
        
        # Initialize GAIA-BT components if available
        if GAIA_BT_AVAILABLE:
            try:
                # Initialize configuration
                self.config = Config()
                
                # Initialize chatbot with proper async setup
                self.chatbot = DrugDevelopmentChatbot()
                
                # Initialize research manager
                self.research_manager = ResearchManager()
                
                # Initialize MCP commands
                self.mcp_commands = MCPCommands()
                
                # Initialize prompt manager
                self.prompt_manager = get_prompt_manager()
                
                print("✅ GAIA-BT components initialized successfully")
                print(f"   Config loaded: {self.config.OLLAMA_MODEL}")
                print(f"   Prompt manager: {len(self.prompt_manager.prompts)} prompts available")
                
            except Exception as e:
                print(f"⚠️ Failed to initialize GAIA-BT components: {e}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
                self.chatbot = None
                self.research_manager = None
                self.mcp_commands = None
                self.prompt_manager = None
        else:
            self.chatbot = None
            self.research_manager = None
            self.mcp_commands = None
            self.prompt_manager = None

    class Valves(BaseModel):
        GAIA_BT_MODE: str = Field(
            default="normal", 
            description="GAIA-BT Operation Mode",
            enum=["normal", "deep_research"]
        )
        MCP_OUTPUT_ENABLED: bool = Field(
            default=False, 
            description="Show MCP search process output"
        )
        SELECTED_PROMPT_MODE: str = Field(
            default="default", 
            description="Prompt specialization mode",
            enum=["default", "clinical", "research", "chemistry", "regulatory"]
        )
        DEFAULT_MODEL: str = Field(
            default="gemma3:27b-it-q4_K_M",
            description="Default model for GAIA-BT"
        )
        ENABLE_DEEP_SEARCH: bool = Field(
            default=True,
            description="Enable MCP Deep Search functionality"
        )
        DEBUG_MODE: bool = Field(
            default=False,
            description="Enable debug logging"
        )

    async def on_startup(self):
        """Pipeline startup initialization"""
        print(f"🧬 GAIA-BT MCP Pipeline v1.0 initialized")
        print(f"   Mode: {self.valves.GAIA_BT_MODE}")
        print(f"   Prompt Mode: {self.valves.SELECTED_PROMPT_MODE}")
        print(f"   Default Model: {self.valves.DEFAULT_MODEL}")
        print(f"   Deep Search: {'Enabled' if self.valves.ENABLE_DEEP_SEARCH else 'Disabled'}")
        print(f"   GAIA-BT Available: {'Yes' if GAIA_BT_AVAILABLE else 'No'}")
        
        # Test GAIA-BT connectivity
        if GAIA_BT_AVAILABLE and self.chatbot:
            try:
                # Test basic functionality
                result = await self._test_gaia_bt_connection()
                if result:
                    print("✅ GAIA-BT connection test successful")
                else:
                    print("⚠️ GAIA-BT connection test failed")
            except Exception as e:
                print(f"⚠️ GAIA-BT connection error: {e}")

    async def on_shutdown(self):
        """Pipeline shutdown cleanup"""
        print("🧬 GAIA-BT MCP Pipeline shutdown")

    def pipe(
        self, 
        prompt: str = None, 
        **kwargs
    ) -> Iterator[str]:
        """Main pipeline processing function"""
        
        if self.valves.DEBUG_MODE:
            yield f"🔧 [DEBUG] Processing prompt in {self.valves.GAIA_BT_MODE} mode\n"
            yield f"🔧 [DEBUG] Prompt: {prompt[:100]}...\n"
        
        # Check if GAIA-BT is available
        if not GAIA_BT_AVAILABLE:
            yield "⚠️ GAIA-BT 시스템을 사용할 수 없습니다. Mock 응답을 제공합니다.\n\n"
            yield from self._generate_mock_response(prompt)
            return
        
        # GAIA-BT 배너 출력
        yield from self._generate_gaia_banner()
        
        # Process based on mode
        if self.valves.GAIA_BT_MODE == "deep_research":
            yield from self._process_deep_research_mode(prompt, **kwargs)
        else:
            yield from self._process_normal_mode(prompt, **kwargs)

    def _generate_gaia_banner(self) -> Iterator[str]:
        """Generate GAIA-BT branded banner"""
        mode_emoji = "🔬" if self.valves.GAIA_BT_MODE == "deep_research" else "💬"
        mode_name = "Deep Research Mode" if self.valves.GAIA_BT_MODE == "deep_research" else "Normal Mode"
        
        banner = f"""
╭─────────────────────────────────────────────────╮
│ 🧬 GAIA-BT v2.0 Alpha 신약개발 연구 어시스턴트      │
│ {mode_emoji} Mode: {mode_name:<35} │
│ 📋 Prompt: {self.valves.SELECTED_PROMPT_MODE:<33} │
│ 🤖 Model: {self.valves.DEFAULT_MODEL:<34} │
╰─────────────────────────────────────────────────╯

"""
        yield banner

    def _process_normal_mode(self, prompt: str, **kwargs) -> Iterator[str]:
        """Process in normal mode"""
        yield "💬 **일반 모드**로 처리 중입니다...\n\n"
        
        try:
            if self.chatbot and hasattr(self.chatbot, 'process_user_input'):
                # Use GAIA-BT chatbot's process_user_input method
                yield "🧬 GAIA-BT 신약개발 AI 분석 중...\n\n"
                
                # Get system prompt based on selected mode
                if self.prompt_manager:
                    system_prompt = get_system_prompt(self.valves.SELECTED_PROMPT_MODE)
                    if system_prompt:
                        yield f"📋 **프롬프트 모드**: {self.valves.SELECTED_PROMPT_MODE}\n\n"
                
                # Process through GAIA-BT chatbot
                # Note: This would need async handling in real implementation
                try:
                    # For now, use a simplified approach
                    response = self._call_gaia_bt_sync(prompt)
                    yield response
                except Exception as chatbot_error:
                    yield f"⚠️ GAIA-BT 처리 실패: {str(chatbot_error)}\n"
                    yield from self._generate_specialized_mock_response(prompt)
            else:
                yield from self._generate_specialized_mock_response(prompt)
        except Exception as e:
            yield f"⚠️ 처리 중 오류가 발생했습니다: {str(e)}\n"
            yield from self._generate_specialized_mock_response(prompt)

    def _process_deep_research_mode(self, prompt: str, **kwargs) -> Iterator[str]:
        """Process in deep research mode with MCP integration"""
        yield "🔬 **Deep Research Mode**로 처리 중입니다...\n\n"
        
        if not self.valves.ENABLE_DEEP_SEARCH:
            yield "⚠️ Deep Search 기능이 비활성화되어 있습니다.\n"
            yield from self._process_normal_mode(prompt, **kwargs)
            return
        
        try:
            # Show MCP search process if enabled
            if self.valves.MCP_OUTPUT_ENABLED:
                yield "🔍 **MCP 통합 검색 시작**\n"
                yield "```\n"
                yield "🔗 BiomCP: PubMed/임상시험 검색 중...\n"
                yield "🔗 ChEMBL: 화학구조/약물상호작용 분석 중...\n"
                yield "🔗 Sequential Thinking: 연구 계획 수립 중...\n"
                yield "```\n\n"
            
            if self.mcp_commands and self.research_manager:
                # Perform integrated MCP search
                research_results = self._perform_integrated_search(prompt)
                
                # Generate comprehensive analysis
                yield "📊 **통합 분석 결과**\n\n"
                yield research_results
                
                # Generate final recommendation
                yield "\n🎯 **연구 권장사항**\n\n"
                recommendations = self._generate_recommendations(prompt, research_results)
                yield recommendations
            else:
                yield from self._generate_mock_deep_research(prompt)
                
        except Exception as e:
            yield f"⚠️ Deep Research 처리 중 오류: {str(e)}\n"
            yield from self._generate_mock_deep_research(prompt)

    def _call_gaia_bt_sync(self, prompt: str) -> str:
        """Call GAIA-BT chatbot synchronously"""
        try:
            if self.chatbot and hasattr(self.chatbot, 'ollama_client'):
                # Get system prompt
                system_prompt = get_system_prompt(self.valves.SELECTED_PROMPT_MODE)
                
                # Create full prompt with system context
                full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
                
                # Call Ollama client directly for synchronous response
                import requests
                import json
                
                # Use local Ollama API
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": self.valves.DEFAULT_MODEL,
                        "prompt": full_prompt,
                        "stream": False
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response', 'No response received')
                else:
                    return f"API 오류: {response.status_code}"
                    
            else:
                return "GAIA-BT chatbot not available"
                
        except Exception as e:
            return f"동기 호출 오류: {str(e)}"

    def _generate_mock_response(self, prompt: str) -> Iterator[str]:
        """Generate mock response for testing"""
        yield f"🧬 **GAIA-BT 신약개발 응답** (Mock Mode)\n\n"
        yield f"질문: {prompt}\n\n"
        
        if "cancer" in prompt.lower() or "암" in prompt:
            yield "🎯 **암 치료제 개발 관점에서의 분석**\n\n"
            yield "• 타겟 검증: 종양 특이적 바이오마커 확인 필요\n"
            yield "• 화합물 최적화: ADMET 프로파일 개선 방향\n"
            yield "• 임상시험 전략: Phase I/II 디자인 고려사항\n\n"
        else:
            yield "이 질문은 신약개발 관점에서 분석이 필요합니다.\n"
            yield "더 구체적인 정보를 제공해주시면 전문적인 답변을 드릴 수 있습니다.\n\n"
        
        yield f"---\n*GAIA-BT v2.0 Alpha - {self.valves.SELECTED_PROMPT_MODE} mode*"

    def _generate_specialized_mock_response(self, prompt: str) -> Iterator[str]:
        """Generate specialized mock response based on prompt mode"""
        mode = self.valves.SELECTED_PROMPT_MODE
        
        yield f"🧬 **GAIA-BT {mode.title()} Mode** 전문 분석\n\n"
        
        if mode == "clinical":
            yield "🏥 **임상시험 관점 분석**\n"
            yield "• 환자 안전성 최우선 고려\n"
            yield "• 규제 요구사항 준수 필요\n"
            yield "• 바이오마커 개발 검토\n\n"
        elif mode == "research":
            yield "🔬 **연구 분석 관점**\n"
            yield "• 최신 문헌 검토 필요\n"
            yield "• 실험 설계 최적화\n"
            yield "• 통계적 유의성 확보\n\n"
        elif mode == "chemistry":
            yield "⚗️ **의약화학 관점 분석**\n"
            yield "• 분자 구조-활성 관계(SAR) 분석\n"
            yield "• ADMET 특성 최적화\n"
            yield "• 합성 경로 검토\n\n"
        elif mode == "regulatory":
            yield "📋 **규제 관점 분석**\n"
            yield "• FDA/EMA 가이드라인 준수\n"
            yield "• 품질 관리 체계 구축\n"
            yield "• 제출 자료 준비 계획\n\n"
        else:
            yield "💊 **신약개발 종합 분석**\n"
            yield "• 타겟 검증부터 시장 출시까지\n"
            yield "• 과학적 근거 기반 접근\n"
            yield "• 리스크 관리 전략\n\n"
        
        yield f"---\n*GAIA-BT v2.0 Alpha - {mode} 전문 모드로 분석*"

    def _generate_mock_deep_research(self, prompt: str) -> Iterator[str]:
        """Generate mock deep research response"""
        yield "📚 **문헌 검색 결과** (Mock)\n"
        yield "• PubMed: 관련 논문 15편 발견\n"
        yield "• ClinicalTrials.gov: 진행 중인 임상시험 3건\n"
        yield "• ChEMBL: 유사 화합물 127개 데이터베이스 매칭\n\n"
        
        yield "🔬 **실험 설계 제안** (Mock)\n"
        yield "• In vitro 세포 독성 실험\n"
        yield "• 동물 모델을 이용한 efficacy 평가\n"
        yield "• ADMET 프로파일 분석\n\n"
        
        yield "📈 **시장 분석** (Mock)\n"
        yield "• 글로벌 시장 규모: $50B (예상)\n"
        yield "• 주요 경쟁사: 3개 회사 개발 중\n"
        yield "• 규제 현황: FDA 가이드라인 준수 필요\n\n"

    def _perform_integrated_search(self, query: str) -> str:
        """Perform integrated MCP search"""
        try:
            # Use GAIA-BT MCP integration
            if self.mcp_commands:
                search_results = self.mcp_commands.handle_deep_search(query)
                return search_results
            else:
                return self._mock_integrated_search(query)
        except Exception as e:
            if self.valves.DEBUG_MODE:
                return f"Mock search results for: {query}\n\nError: {str(e)}"
            return self._mock_integrated_search(query)

    def _mock_integrated_search(self, query: str) -> str:
        """Mock integrated search results"""
        return f"""
**통합 검색 결과 (Mock)**

📖 **문헌 분석**
- 관련 논문: 25편 (최근 5년)
- 핵심 연구자: Dr. Smith (하버드), Dr. Kim (서울대)
- 주요 발견: 새로운 타겟 메커니즘 확인

🧪 **화학 분석**
- 유사 화합물: 45개 (ChEMBL 데이터베이스)
- 약물 상호작용: 3개 주요 경로 확인
- ADMET 예측: 중등도 투과성, 낮은 독성

🏥 **임상 현황**
- 진행 중인 시험: 7건 (Phase I-III)
- 승인된 치료제: 2개 (2019, 2021)
- 규제 가이드라인: 최신 FDA/EMA 요구사항

Query processed: {query}
"""

    def _generate_recommendations(self, query: str, results: str) -> str:
        """Generate research recommendations based on results"""
        try:
            if self.research_manager:
                recommendations = self.research_manager.generate_recommendations(query, results)
                return recommendations
            else:
                return self._mock_recommendations(query)
        except Exception as e:
            return self._mock_recommendations(query)

    def _mock_recommendations(self, query: str) -> str:
        """Mock research recommendations"""
        return f"""
**연구 권장사항 (Mock)**

🎯 **단기 목표 (6개월)**
1. 타겟 검증 실험 완료
2. 리드 화합물 3-5개 선정
3. 초기 ADMET 스크리닝

🚀 **중기 목표 (1-2년)**
1. 화합물 최적화 완료
2. 전임상 안전성 평가
3. IND 신청 준비

📊 **장기 목표 (3-5년)**
1. Phase I 임상시험 시작
2. 바이오마커 개발
3. 파트너링 기회 탐색

💡 **핵심 고려사항**
- 지적재산권 확보 전략
- 규제 전략 수립
- 자금 조달 계획

Query: {query}
"""

    async def _test_gaia_bt_connection(self) -> bool:
        """Test GAIA-BT system connectivity"""
        try:
            if self.chatbot:
                # Simple connectivity test
                test_response = self.chatbot.generate_specialized_response("test", mode="default")
                return len(test_response) > 0
            return False
        except Exception:
            return False

    def get_provider_models(self) -> List[Dict[str, Any]]:
        """Provide GAIA-BT specific models"""
        return [
            {
                "id": "gaia-bt-normal",
                "name": "GAIA-BT Normal Mode",
                "model": {
                    "id": "gaia-bt-normal",
                    "name": "GAIA-BT Normal Mode",
                    "meta": {
                        "description": "신약개발 일반 모드 - 빠른 응답",
                        "capabilities": ["text"],
                        "vision": False
                    },
                    "ollama": {
                        "name": self.valves.DEFAULT_MODEL,
                        "model": self.valves.DEFAULT_MODEL
                    }
                }
            },
            {
                "id": "gaia-bt-deep-research",
                "name": "GAIA-BT Deep Research Mode",
                "model": {
                    "id": "gaia-bt-deep-research", 
                    "name": "GAIA-BT Deep Research Mode",
                    "meta": {
                        "description": "신약개발 Deep Research 모드 - MCP 통합 검색",
                        "capabilities": ["text", "research", "mcp"],
                        "vision": False
                    },
                    "ollama": {
                        "name": self.valves.DEFAULT_MODEL,
                        "model": self.valves.DEFAULT_MODEL
                    }
                }
            }
        ]