#!/usr/bin/env python3
"""
신약개발 연구 챗봇 모듈

Ollama LLM을 활용한 CLI 기반 실시간 챗봇
과학적 근거와 참고문헌을 포함하는 상세한 답변 제공
"""

import datetime
import json
import os
import sys
from pathlib import Path
import asyncio

# 내부 모듈 임포트
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Optional

from app.api.ollama_client import OllamaClient
from app.cli.interface import CliInterface
from app.utils.config import (
    AVAILABLE_MODELS,
    DEFAULT_FEEDBACK_DEPTH,
    DEFAULT_FEEDBACK_WIDTH,
    MIN_REFERENCES,
    MIN_RESPONSE_LENGTH,
    OUTPUT_DIR,
)

# MCP 통합
try:
    from mcp.integration.mcp_manager import MCPManager
    from app.cli.mcp_commands import MCPCommands
    from app.core.biomcp_integration import BioMCPIntegration
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ MCP 모듈 import 실패: {e}")
    MCPManager = None
    MCPCommands = None
    BioMCPIntegration = None
    MCP_AVAILABLE = False


class DrugDevelopmentChatbot:
    """
    신약개발 연구 챗봇 클래스

    사용자 인터페이스 관리 및 AI 응답 생성을 담당합니다.
    """

    def __init__(self, debug_mode=False):
        """
        챗봇 초기화

        Args:
            debug_mode (bool): 디버그 모드 활성화 여부
        """
        # 설정 초기화 - 메모리에서 가져온 값을 사용하되, Gemma3를 우선 사용
        preferred_model = "Gemma3:latest"  # 바로 표준 모델로 지정
        self.settings = {
            "model": preferred_model,  # OLLAMA_MODEL 대신 바로 기본값 지정
            "feedback_depth": DEFAULT_FEEDBACK_DEPTH,
            "feedback_width": DEFAULT_FEEDBACK_WIDTH,
            "min_response_length": MIN_RESPONSE_LENGTH,
            "min_references": MIN_REFERENCES,
            "temperature": 0.7,
            "max_tokens": 4000,
            "debug_mode": debug_mode  # 디버그 모드 설정
        }

        # Ollama API 클라이언트 초기화 (설정 후 생성)
        self.client = OllamaClient(
            model=preferred_model,  # 바로 Gemma3:latest로 지정
            max_tokens=4000,
            min_response_length=self.settings["min_response_length"],
            debug_mode=debug_mode  # 디버그 모드 전달
        )

        # 모델 가용성 초기 확인을 위한 상태 변수
        self.initial_model_check_done = False

        # CLI 인터페이스 초기화
        self.interface = CliInterface()

        # 대화 이력
        self.conversation_history = []
        
        # MCP 관리자 초기화 (사용 가능한 경우)
        if MCP_AVAILABLE:
            self.mcp_manager = MCPManager()
            self.mcp_enabled = False
            self.mcp_commands = MCPCommands(self)
            self.biomcp_integration = BioMCPIntegration(self.mcp_manager)
        else:
            self.mcp_manager = None
            self.mcp_enabled = False
            self.mcp_commands = None
            self.biomcp_integration = None

        # 시스템 프롬프트
        self.system_prompt = """
당신은 신약개발 전문가입니다. GAIA-BT v2.0 통합 Deep Research MCP 시스템을 통해 7개의 전문 데이터베이스에 접근할 수 있습니다.

🔬 **통합 MCP 데이터베이스 활용 지침:**

**💊 DrugBank (15,000+ 약물 데이터베이스)**
- 약물 검색, 상호작용, ADMET 특성 분석에 활용
- 질문에 특정 약물명이 있으면 DrugBank 데이터를 우선 참조
- 약물 안전성, 부작용, 약동학 정보 제공

**🎯 OpenTargets (60,000+ 타겟-질병 연관성)**  
- 유전자/타겟과 질병 간의 연관성 분석에 활용
- 타겟 발굴, 질병 메커니즘 이해에 필수
- 유전체 데이터 기반 치료 전략 수립

**🧪 ChEMBL (화학 구조 & 물리화학적 특성)**
- 분자 구조, SAR 분석, 화학적 특성 분석에 활용
- SMILES, InChI 구조 정보 및 활성 데이터 제공
- 화합물 최적화 전략 수립

**📄 BioMCP (생의학 연구 데이터)**
- PubMed/PubTator3: 최신 논문 및 생의학 문헌
- ClinicalTrials.gov: 임상시험 데이터 및 치료법 정보
- 유전체 변이 DB: CIViC, ClinVar, COSMIC, dbSNP

**📑 BioRxiv (프리프린트 논문 저장소)**
- bioRxiv/medRxiv: 최신 프리프린트 논문 및 연구 동향
- 출판 전 최신 연구 결과 및 동향 파악
- 신속한 과학적 정보 접근과 연구 방향성 제시

**🧠 Sequential Thinking (AI 기반 체계적 추론)**
- 복잡한 신약개발 문제의 단계별 분석
- 논리적 추론과 연구 계획 수립

**📊 통합 Deep Research 답변 형식:**
1. **🔍 키워드 분석 및 검색 전략** (제공된 MCP 데이터 활용)
2. **📋 문제 정의** (Sequential Thinking 기반)
3. **🧬 핵심 내용** (이론, 개념, 원리)
4. **💊 약물/화합물 분석** (DrugBank + ChEMBL 데이터 통합)
5. **🎯 타겟-질병 연관성** (OpenTargets 데이터 활용)
6. **📚 과학적 근거** (BioMCP 논문/임상시험 + BioRxiv 프리프린트 데이터)
7. **🔬 임상 개발 전략** (통합 데이터 기반)
8. **📈 결론 및 향후 방향**
9. **📖 참고 문헌** (MCP 데이터 소스 포함, 최소 3개)

**🎯 MCP 데이터 활용 원칙:**
- 제공된 MCP 검색 결과를 반드시 활용하여 답변 구성
- 각 MCP 서버의 데이터를 명시적으로 인용 (예: "DrugBank 데이터에 따르면...")
- 여러 데이터베이스의 정보를 교차 검증하여 신뢰성 높은 결론 도출
- MCP 데이터가 없는 부분은 일반 지식으로 보완하되 구분하여 명시

**📝 작성 요구사항:**
- 마크다운 형식으로 구조화된 답변
- 최소 1500자 이상의 상세한 내용
- MCP 데이터 소스별 명확한 인용
- 실용적이고 구체적인 신약개발 정보 제공

MCP 데이터가 제공된 경우, 반드시 해당 정보를 핵심적으로 활용하여 전문적이고 정확한 답변을 생성하세요.
"""

    async def auto_select_model(self):
        """
        사용 가능한 모델을 확인하고 자동으로 선택합니다.
        Gemma3:latest를 우선적으로 선택하고, 사용 불가능한 경우 다른 모델을 선택합니다.
        """
        try:
            # 사용 가능한 모델 목록 가져오기
            models = await self.client.list_models()
            available_models = [m.get("name") for m in models]

            # 현재 설정된 모델이 사용 가능한지 확인
            if self.settings["model"] not in available_models:
                # 우선 Gemma3:latest가 있는지 확인
                preferred_model = "Gemma3:latest"
                if preferred_model in available_models:
                    self.settings["model"] = preferred_model
                    self.client.model = preferred_model
                    self.interface.console.print(f"[green]모델이 '{preferred_model}'로 설정되었습니다.[/green]")
                # Gemma3가 없으면 다른 사용 가능한 모델 확인
                elif available_models:
                    self.settings["model"] = available_models[0]
                    self.client.model = available_models[0]
                    self.interface.console.print(f"[yellow]Gemma3:latest 모델을 찾을 수 없어 '{available_models[0]}'로 설정되었습니다.[/yellow]")
                else:
                    self.interface.display_error("사용 가능한 Ollama 모델이 없습니다. Ollama를 확인해주세요.")
                    return False

            return True

        except Exception as e:
            self.interface.display_error(f"모델 확인 중 오류 발생: {e!s}")
            return False

    async def start(self):
        """
        챗봇 실행
        """
        # 환영 메시지 표시
        self.interface.display_welcome()

        try:
            # API 가용성 확인
            status = await self.client.check_availability()
            if not status["available"]:
                self.interface.display_error(f"Ollama API에 연결할 수 없습니다: {status.get('error', '알 수 없는 오류')}")
                return

            # 사용 가능한 모델 확인 및 자동 선택
            if not self.initial_model_check_done:
                model_check_result = await self.auto_select_model()
                if not model_check_result:
                    return
                self.initial_model_check_done = True
        except Exception as e:
            self.interface.display_error(f"API 초기화 중 오류 발생: {e!s}")
            return

        # 메인 입력 루프
        while True:
            try:
                # 사용자 입력 받기
                user_input = await self.interface.get_user_input()

                if not user_input:
                    continue

                # 명령어 처리
                if user_input.startswith("/"):
                    continue_chat = await self.process_command(user_input)
                    if not continue_chat:
                        break
                else:
                    # 일반 질문 처리
                    await self.generate_response(user_input)
            except KeyboardInterrupt:
                print("\n프로그램이 종료됩니다.")
                break
            except Exception as e:
                self.interface.display_error(f"오류 발생: {e!s}")

        print("프로그램이 종료되었습니다.")

    async def deep_search_with_mcp(self, user_input):
        """MCP를 활용한 통합 Deep Search 수행 - DrugBank, OpenTargets, ChEMBL, BioMCP 모두 활용"""
        if not self.mcp_enabled:
            if self.settings.get("debug_mode", False):
                self.interface.print_thinking("❌ MCP가 비활성화되어 있습니다")
            return None
        
        try:
            self.interface.print_thinking("🔬 통합 MCP Deep Search 수행 중...")
            search_results = []
            
            # 키워드 분석으로 최적 검색 전략 결정
            input_lower = user_input.lower()
            is_drug_related = any(kw in input_lower for kw in ['약물', '치료제', '복용', '부작용', '상호작용', 'drug', 'medication', 'aspirin', '아스피린', 'metformin', '메트포민'])
            is_target_related = any(kw in input_lower for kw in ['타겟', '유전자', '단백질', 'target', 'protein', 'gene', 'brca1', 'tp53', 'egfr'])
            is_disease_related = any(kw in input_lower for kw in ['질병', '암', '당뇨', 'cancer', 'disease', 'diabetes', '유방암', 'breast', '알츠하이머', 'alzheimer'])
            is_chemical_related = any(kw in input_lower for kw in ['화학', '분자', '구조', 'chemical', 'molecule', 'structure', 'smiles'])
            
            # 디버그 정보 출력
            if self.settings.get("debug_mode", False):
                self.interface.print_thinking(f"🔍 키워드 분석: 약물={is_drug_related}, 타겟={is_target_related}, 질병={is_disease_related}, 화학={is_chemical_related}")
            
            # 1. Sequential Thinking으로 연구 계획 수립
            thinking_success = False
            try:
                self.interface.print_thinking("🧠 AI 분석 및 연구 계획 수립...")
                
                # 수정된 매개변수 사용 (enableBranching 제거)
                thinking_result = await self.mcp_manager.call_tool(
                    client_id='default',
                    tool_name='start_thinking',
                    arguments={
                        'problem': f'신약개발 연구 질문 분석: {user_input}',
                        'maxSteps': 5
                    }
                )
                
                if self.settings.get("debug_mode", False):
                    self.interface.print_thinking(f"🐛 Sequential Thinking 결과: {thinking_result}")
                
                # 결과 검증 및 유의미한 데이터 확인
                if (thinking_result and 
                    'content' in thinking_result and 
                    thinking_result['content'] and 
                    len(thinking_result['content']) > 0):
                    
                    thinking_text = thinking_result['content'][0].get('text', '').strip()
                    # 비어있지 않은 의미있는 결과만 포함
                    if thinking_text and len(thinking_text) > 30:  # 최소 30자 이상의 의미있는 내용
                        search_results.append(f"🧠 AI 연구 계획:\n{thinking_text}")
                        thinking_success = True
                        self.interface.print_thinking("✓ AI 분석 완료")
                
                if not thinking_success:
                    self.interface.print_thinking("⚠️ AI 분석 결과 없음")
                    
            except Exception as e:
                self.interface.print_thinking(f"🙅 AI 분석 실패: {e}")
                if self.settings.get("debug_mode", False):
                    import traceback
                    self.interface.print_thinking(f"🐛 상세 오류: {traceback.format_exc()}")
                    if "Method not implemented" in str(e):
                        self.interface.print_thinking("🐛 Sequential Thinking 서버가 실행되지 않았거나 툴이 구현되지 않음")
            
            # 2. DrugBank 약물 데이터베이스 검색
            if is_drug_related:
                try:
                    self.interface.print_thinking("💊 DrugBank 약물 데이터 검색...")
                    
                    # 질문에서 약물명 추출
                    common_drugs = ['aspirin', 'ibuprofen', 'metformin', 'insulin', 'acetaminophen', '아스피린', '메트포민']
                    search_terms = []
                    
                    for drug in common_drugs:
                        if drug in input_lower:
                            search_terms.append(drug)
                    
                    # 특정 약물이 없으면 일반적 검색어 사용
                    if not search_terms:
                        if 'pain' in input_lower or '통증' in input_lower:
                            search_terms = ['aspirin']
                        elif 'diabetes' in input_lower or '당뇨' in input_lower:
                            search_terms = ['metformin']
                        else:
                            search_terms = ['cancer']  # 일반적인 암 치료제 검색
                    
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"🐛 DrugBank 검색어: {search_terms}")
                    
                    drugbank_success = False
                    for term in search_terms[:2]:  # 최대 2개 검색
                        try:
                            # 올바른 클라이언트 ID 사용
                            drugbank_result = await self.mcp_manager.call_tool(
                                client_id='drugbank-mcp',  # 정확한 클라이언트 ID
                                tool_name='search_drugs',
                                arguments={'query': term, 'limit': 3}
                            )
                            
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"🐛 DrugBank {term} 결과: {drugbank_result}")
                            
                            # 결과 검증 및 유의미한 데이터 확인
                            if (drugbank_result and 
                                'content' in drugbank_result and 
                                drugbank_result['content'] and 
                                len(drugbank_result['content']) > 0):
                                
                                drug_text = drugbank_result['content'][0].get('text', '').strip()
                                # 비어있지 않은 의미있는 결과만 포함
                                if drug_text and len(drug_text) > 50:  # 최소 50자 이상의 의미있는 내용
                                    search_results.append(f"💊 DrugBank - {term}:\n{drug_text}")
                                    drugbank_success = True
                                    if self.settings.get("debug_mode", False):
                                        self.interface.print_thinking(f"🐛 DrugBank {term} 검색 성공: {len(drug_text)}자")
                                
                        except Exception as tool_error:
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"🐛 DrugBank {term} 툴 호출 실패: {tool_error}")
                            continue
                    
                    if drugbank_success:
                        self.interface.print_thinking("✓ DrugBank 검색 완료")
                    else:
                        self.interface.print_thinking("⚠️ DrugBank 검색 결과 없음")
                        
                except Exception as e:
                    self.interface.print_thinking(f"🙅 DrugBank 검색 실패: {e}")
                    if self.settings.get("debug_mode", False):
                        import traceback
                        self.interface.print_thinking(f"🐛 DrugBank 상세 오류: {traceback.format_exc()}")
            
            # 3. OpenTargets 타겟-질병 연관성 검색
            if is_target_related or is_disease_related:
                try:
                    self.interface.print_thinking("🎯 OpenTargets 타겟-질병 연관성 검색...")
                    
                    # 유전자/타겟 검색
                    common_targets = ['BRCA1', 'TP53', 'EGFR', 'KRAS', 'PIK3CA']
                    target_terms = []
                    
                    for target in common_targets:
                        if target.lower() in input_lower:
                            target_terms.append(target)
                    
                    if not target_terms and (is_target_related or is_disease_related):
                        target_terms = ['cancer']  # 기본 검색어
                    
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"🐛 OpenTargets 검색어: {target_terms}")
                    
                    opentargets_success = False
                    for term in target_terms[:2]:
                        try:
                            # 올바른 클라이언트 ID 사용
                            targets_result = await self.mcp_manager.call_tool(
                                client_id='opentargets-mcp',  # 정확한 클라이언트 ID
                                tool_name='search_targets' if is_target_related else 'search_diseases',
                                arguments={'query': term, 'limit': 3}
                            )
                            
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"🐛 OpenTargets {term} 결과: {targets_result}")
                            
                            # 결과 검증 및 유의미한 데이터 확인
                            if (targets_result and 
                                'content' in targets_result and 
                                targets_result['content'] and 
                                len(targets_result['content']) > 0):
                                
                                targets_text = targets_result['content'][0].get('text', '').strip()
                                # 비어있지 않은 의미있는 결과만 포함
                                if targets_text and len(targets_text) > 50:  # 최소 50자 이상의 의미있는 내용
                                    search_results.append(f"🎯 OpenTargets - {term}:\n{targets_text}")
                                    opentargets_success = True
                                    if self.settings.get("debug_mode", False):
                                        self.interface.print_thinking(f"🐛 OpenTargets {term} 검색 성공: {len(targets_text)}자")
                                
                        except Exception as tool_error:
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"🐛 OpenTargets {term} 툴 호출 실패: {tool_error}")
                            continue
                    
                    if opentargets_success:
                        self.interface.print_thinking("✓ OpenTargets 검색 완료")
                    else:
                        self.interface.print_thinking("⚠️ OpenTargets 검색 결과 없음")
                        
                except Exception as e:
                    self.interface.print_thinking(f"🙅 OpenTargets 검색 실패: {e}")
                    if self.settings.get("debug_mode", False):
                        import traceback
                        self.interface.print_thinking(f"🐛 OpenTargets 상세 오류: {traceback.format_exc()}")
            
            # 4. ChEMBL 화학 구조 및 분자 정보 검색
            if is_chemical_related or is_drug_related:
                try:
                    self.interface.print_thinking("🧪 ChEMBL 화학 데이터 검색...")
                    
                    # 화학물질/약물 검색
                    chemical_terms = []
                    if 'aspirin' in input_lower or '아스피린' in input_lower:
                        chemical_terms.append('aspirin')
                    elif 'fluorouracil' in input_lower or '5-FU' in input_lower:
                        chemical_terms.append('fluorouracil')
                    else:
                        chemical_terms.append('cancer')  # 일반적인 항암제 검색
                    
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"🐛 ChEMBL 검색어: {chemical_terms}")
                    
                    chembl_success = False
                    for term in chemical_terms[:2]:
                        try:
                            # ChEMBL은 default 클라이언트 사용
                            chembl_result = await self.mcp_manager.call_tool(
                                client_id='default',  # ChEMBL은 기본 클라이언트
                                tool_name='search_molecule',
                                arguments={'query': term, 'limit': 3}
                            )
                            
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"🐛 ChEMBL {term} 결과: {chembl_result}")
                            
                            # 결과 검증 및 유의미한 데이터 확인
                            if (chembl_result and 
                                'content' in chembl_result and 
                                chembl_result['content'] and 
                                len(chembl_result['content']) > 0):
                                
                                chembl_text = chembl_result['content'][0].get('text', '').strip()
                                # 비어있지 않은 의미있는 결과만 포함
                                if chembl_text and len(chembl_text) > 50:  # 최소 50자 이상의 의미있는 내용
                                    search_results.append(f"🧪 ChEMBL - {term}:\n{chembl_text}")
                                    chembl_success = True
                                    if self.settings.get("debug_mode", False):
                                        self.interface.print_thinking(f"🐛 ChEMBL {term} 검색 성공: {len(chembl_text)}자")
                                
                        except Exception as tool_error:
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"🐛 ChEMBL {term} 툴 호출 실패: {tool_error}")
                            continue
                    
                    if chembl_success:
                        self.interface.print_thinking("✓ ChEMBL 검색 완료")
                    else:
                        self.interface.print_thinking("⚠️ ChEMBL 검색 결과 없음")
                        
                except Exception as e:
                    self.interface.print_thinking(f"🙅 ChEMBL 검색 실패: {e}")
                    if self.settings.get("debug_mode", False):
                        import traceback
                        self.interface.print_thinking(f"🐛 ChEMBL 상세 오류: {traceback.format_exc()}")
            
            # 5. BioMCP 생의학 연구 데이터 검색
            biomcp_success = False
            try:
                self.interface.print_thinking("📄 BioMCP 생의학 논문 검색...")
                
                # 논문 검색 - 올바른 툴 이름 사용 (article_searcher)
                try:
                    articles_result = await self.mcp_manager.call_tool(
                        client_id='default',  # BioMCP는 기본 클라이언트
                        tool_name='article_searcher',  # 실제 BioMCP 툴 이름
                        arguments={
                            'call_benefit': f'신약개발 연구를 위한 "{user_input}" 관련 논문 검색',
                            'keywords': user_input,
                            'diseases': user_input if is_disease_related else None,
                            'genes': user_input if is_target_related else None,
                            'chemicals': user_input if is_chemical_related or is_drug_related else None
                        }
                    )
                    
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"🐛 BioMCP 논문 검색 결과: {articles_result}")
                    
                    # 결과 검증 및 유의미한 데이터 확인
                    if (articles_result and 
                        'content' in articles_result and 
                        articles_result['content'] and 
                        len(articles_result['content']) > 0):
                        
                        articles_text = articles_result['content'][0].get('text', '').strip()
                        # 비어있지 않은 의미있는 결과만 포함
                        if articles_text and len(articles_text) > 50:  # 최소 50자 이상의 의미있는 내용
                            search_results.append(f"📄 BioMCP 논문:\n{articles_text}")
                            biomcp_success = True
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"🐛 BioMCP 논문 검색 성공: {len(articles_text)}자")
                    
                except Exception as article_error:
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"🐛 BioMCP 논문 검색 실패: {article_error}")
                        if "Method not implemented" in str(article_error):
                            self.interface.print_thinking("🐛 BioMCP 서버가 실행되지 않았거나 툴이 구현되지 않음")
                
                # 임상시험 검색 (질병 관련인 경우) - 올바른 툴 이름 사용 (trial_searcher)
                if is_disease_related:
                    try:
                        trials_result = await self.mcp_manager.call_tool(
                            client_id='default',
                            tool_name='trial_searcher',  # 실제 BioMCP 툴 이름
                            arguments={
                                'call_benefit': f'"{user_input}" 관련 임상시험 데이터 검색',
                                'conditions': user_input,
                                'recruiting_status': 'ANY',
                                'study_type': 'INTERVENTIONAL'
                            }
                        )
                        
                        if self.settings.get("debug_mode", False):
                            self.interface.print_thinking(f"🐛 BioMCP 임상시험 검색 결과: {trials_result}")
                        
                        # 결과 검증 및 유의미한 데이터 확인
                        if (trials_result and 
                            'content' in trials_result and 
                            trials_result['content'] and 
                            len(trials_result['content']) > 0):
                            
                            trials_text = trials_result['content'][0].get('text', '').strip()
                            # 비어있지 않은 의미있는 결과만 포함
                            if trials_text and len(trials_text) > 50:  # 최소 50자 이상의 의미있는 내용
                                search_results.append(f"🏥 BioMCP 임상시험:\n{trials_text}")
                                biomcp_success = True
                                if self.settings.get("debug_mode", False):
                                    self.interface.print_thinking(f"🐛 BioMCP 임상시험 검색 성공: {len(trials_text)}자")
                        
                    except Exception as trial_error:
                        if self.settings.get("debug_mode", False):
                            self.interface.print_thinking(f"🐛 BioMCP 임상시험 검색 실패: {trial_error}")
                            if "Method not implemented" in str(trial_error):
                                self.interface.print_thinking("🐛 BioMCP 서버가 실행되지 않았거나 툴이 구현되지 않음")
                
                if biomcp_success:
                    self.interface.print_thinking("✓ BioMCP 검색 완료")
                else:
                    self.interface.print_thinking("⚠️ BioMCP 검색 결과 없음")
                    
            except Exception as e:
                self.interface.print_thinking(f"🙅 BioMCP 검색 실패: {e}")
                if self.settings.get("debug_mode", False):
                    import traceback
                    self.interface.print_thinking(f"🐛 BioMCP 상세 오류: {traceback.format_exc()}")
                    if "Method not implemented" in str(e):
                        self.interface.print_thinking("🐛 BioMCP 서버가 실행되지 않았거나 MCP 툴이 구현되지 않음")
            
            # 6. BioRxiv 프리프린트 논문 검색
            biorxiv_success = False
            try:
                self.interface.print_thinking("📑 BioRxiv 프리프린트 논문 검색...")
                
                # 최근 프리프린트 검색 (기본 7일)
                try:
                    # 연구 관련 키워드가 있으면 검색
                    search_terms = []
                    if is_drug_related:
                        search_terms.extend(['drug', 'therapy', 'treatment'])
                    if is_target_related:
                        search_terms.extend(['target', 'protein', 'gene'])
                    if is_disease_related:
                        search_terms.extend(['cancer', 'disease', 'therapy'])
                    if is_chemical_related:
                        search_terms.extend(['compound', 'molecule', 'chemical'])
                    
                    # 키워드가 없으면 일반적인 생물의학 검색
                    if not search_terms:
                        search_terms = ['biomedical', 'research']
                    
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"🐛 BioRxiv 검색 전략: 최근 7일 프리프린트")
                    
                    # BioRxiv 최근 프리프린트 검색
                    biorxiv_result = await self.mcp_manager.call_tool(
                        client_id='biorxiv-mcp',  # BioRxiv MCP 클라이언트
                        tool_name='get_recent_preprints',
                        arguments={
                            'server': 'biorxiv',
                            'interval': 7,  # 최근 7일
                            'limit': 10     # 최대 10개
                        }
                    )
                    
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"🐛 BioRxiv 검색 결과: {biorxiv_result}")
                    
                    # 결과 검증 및 유의미한 데이터 확인
                    if (biorxiv_result and 
                        'content' in biorxiv_result and 
                        biorxiv_result['content'] and 
                        len(biorxiv_result['content']) > 0):
                        
                        biorxiv_text = biorxiv_result['content'][0].get('text', '').strip()
                        # 비어있지 않은 의미있는 결과만 포함
                        if biorxiv_text and len(biorxiv_text) > 50:  # 최소 50자 이상의 의미있는 내용
                            search_results.append(f"📑 BioRxiv 프리프린트:\n{biorxiv_text}")
                            biorxiv_success = True
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"🐛 BioRxiv 검색 성공: {len(biorxiv_text)}자")
                    
                except Exception as biorxiv_error:
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"🐛 BioRxiv 검색 실패: {biorxiv_error}")
                        if "Method not implemented" in str(biorxiv_error):
                            self.interface.print_thinking("🐛 BioRxiv 서버가 실행되지 않았거나 툴이 구현되지 않음")
                
                if biorxiv_success:
                    self.interface.print_thinking("✓ BioRxiv 검색 완료")
                else:
                    self.interface.print_thinking("⚠️ BioRxiv 검색 결과 없음")
                    
            except Exception as e:
                self.interface.print_thinking(f"🙅 BioRxiv 검색 실패: {e}")
                if self.settings.get("debug_mode", False):
                    import traceback
                    self.interface.print_thinking(f"🐛 BioRxiv 상세 오류: {traceback.format_exc()}")
                    if "Method not implemented" in str(e):
                        self.interface.print_thinking("🐛 BioRxiv 서버가 실행되지 않았거나 MCP 툴이 구현되지 않음")
            
            # 7. 결과 통합 및 요약
            if search_results:
                self.interface.print_thinking("📊 통합 Deep Search 완료 - 데이터 분석 중...")
                
                # 검색 결과 통계 및 성공적인 데이터베이스 확인
                successful_dbs = []
                for result in search_results:
                    if "💊 DrugBank" in result:
                        successful_dbs.append("💊 DrugBank")
                    elif "🎯 OpenTargets" in result:
                        successful_dbs.append("🎯 OpenTargets")
                    elif "🧪 ChEMBL" in result:
                        successful_dbs.append("🧪 ChEMBL")
                    elif "📄 BioMCP" in result:
                        successful_dbs.append("📄 BioMCP")
                    elif "📑 BioRxiv" in result:
                        successful_dbs.append("📑 BioRxiv")
                    elif "🧠 AI" in result:
                        successful_dbs.append("🧠 Sequential Thinking")
                
                result_stats = f"""
🔬 **GAIA-BT v2.0 통합 Deep Search 수행 완루**

📊 **성공적으로 검색된 MCP 데이터베이스:**
{' + '.join(set(successful_dbs)) if successful_dbs else '검색 결과 없음'}

📋 **스마트 키워드 분석 결과:**
- 원본 질문: "{user_input}"
- 약물 관련 키워드: {'✓ 감지' if is_drug_related else '✗ 미감지'}
- 타겟/유전자 키워드: {'✓ 감지' if is_target_related else '✗ 미감지'}
- 질병 관련 키워드: {'✓ 감지' if is_disease_related else '✗ 미감지'}
- 화학 구조 키워드: {'✓ 감지' if is_chemical_related else '✗ 미감지'}

🎯 **검색 결과:** {len(search_results)}개 데이터소스에서 유의미한 데이터 획득

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                
                combined_results = result_stats + "\n\n" + "\n\n".join(search_results)
                
                if self.settings.get("debug_mode", False):
                    self.interface.print_thinking(f"🐛 최종 통합 결과 길이: {len(combined_results)}자")
                
                return combined_results
            else:
                self.interface.print_thinking("⚠️ 모든 MCP 검색에서 유의미한 결과를 찾을 수 없음")
                
                # MCP 서버가 제대로 작동하지 않는 경우에 대한 안내
                fallback_message = f"""
🔍 **MCP Deep Search 결과 없음**

📝 **분석된 질문:** "{user_input}"

⚠️ **가능한 원인:**
- MCP 서버가 시작되지 않음 ('/mcp start' 명령어 필요)
- 네트워크 연결 문제로 외부 데이터베이스 접근 불가
- 검색어에 대한 관련 데이터 부족
- MCP 툴 구현 오류 ("Method not implemented: tools/call")

🛠️ **해결 방법:**
1. '/mcp status' 명령어로 MCP 서버 상태 확인
2. '/mcp stop' 후 '/mcp start'로 서버 재시작
3. 더 구체적이고 전문적인 질문으로 재시도
4. '/debug' 명령어로 디버그 모드 활성화 후 재시도

📋 **추천 질문 예시:**
- "EGFR 억제제의 내성 메커니즘과 차세대 치료 전략을 분석해주세요"
- "BRCA1 유전자 타겟을 이용한 유방암 치료제 개발 전략을 제시해주세요"
- "아스피린의 약물 상호작용과 새로운 치료제 개발 가능성을 분석해주세요"
"""
                
                return fallback_message
            
        except Exception as e:
            self.interface.print_thinking(f"Deep Search 중 오류: {e}")
            if self.settings.get("debug_mode", False):
                import traceback
                self.interface.print_thinking(f"🐛 Deep Search 상세 오류: {traceback.format_exc()}")
            return None

    async def generate_response(self, question: str, ask_to_save: bool = True) -> str:
        """
        질문에 대한 AI 응답 생성

        Args:
            question: 사용자 질문
            ask_to_save: 저장 여부 확인 프롬프트 표시 여부 (기본값: True)

        Returns:
            str: 생성된 응답
        """
        # MCP Deep Search 수행
        deep_search_context = None
        if self.mcp_enabled:
            deep_search_context = await self.deep_search_with_mcp(question)
            
            # MCP 연구를 Deep Search 컨텍스트로만 사용 (중복 출력 방지)
        
        # 응답 생성 중 스피너 표시
        with self.interface.display_thinking():
            try:
                # 디버깅: 요청 정보 출력 (디버그 모드일 때만)
                if self.settings["debug_mode"]:
                    print(f"\n[디버그] 질문 처리 중: {question[:50]}...")
                    print(f"[디버그] 현재 모델: {self.client.model}")

                # Deep Search 컨텍스트를 포함한 시스템 프롬프트 구성
                enhanced_system_prompt = self.system_prompt
                if deep_search_context:
                    enhanced_system_prompt += f"""

🔬 **통합 Deep Research MCP 검색 결과:**
{deep_search_context}

**📊 MCP 데이터 활용 지침:**
1. 위 MCP 검색 결과에서 각 데이터베이스의 정보를 구체적으로 인용하세요
2. DrugBank, OpenTargets, ChEMBL, BioMCP의 데이터를 교차 검증하여 종합적 결론 도출
3. 각 섹션에서 해당하는 MCP 데이터를 명시적으로 활용 (예: "DrugBank 검색 결과에 따르면...", "OpenTargets 데이터에서 확인된...")
4. Sequential Thinking의 연구 계획을 바탕으로 체계적인 답변 구성
5. 검색된 키워드 분석 정보를 활용하여 질문의 핵심 포인트 파악

위 MCP 통합 데이터를 핵심적으로 활용하여 전문적이고 정확한 신약개발 연구 답변을 생성하세요."""
                
                # 응답 생성
                response = await self.client.generate(
                    prompt=question,
                    system_prompt=enhanced_system_prompt
                )

                # 디버깅: 응답 길이 확인 (디버그 모드일 때만)
                if self.settings["debug_mode"]:
                    print(f"[디버그] 응답 길이: {len(response)} 자")
                    print(f"[디버그] 응답 시작: {response[:100]}...")

                # 응답이 비어있는지 확인
                if not response:
                    response = "[응답이 생성되지 않았습니다. 다시 시도해주세요.]"

                # 대화 이력에 추가
                self.conversation_history.append({"question": question, "answer": response})

                # 응답 출력 (디버그 모드일 때만 시작/종료 표시)
                if self.settings["debug_mode"]:
                    print("\n--- AI 응답 시작 ---")

                # 항상 응답은 출력
                self.interface.display_response(response)

                if self.settings["debug_mode"]:
                    print("--- AI 응답 종료 ---\n")

                # 사용자에게 결과 저장 여부 물어보기
                if self.interface and ask_to_save:
                    try:
                        save_choice = await self.interface.ask_to_save()

                        # 사용자가 저장을 원하는 경우에만 저장
                        if save_choice:
                            # 평가 정보 없이 저장 (빈 딕셔너리 전달)
                            await self.save_research_result(question, response, {})
                    except Exception as e:
                        if self.settings["debug_mode"]:
                            print(f"[디버그] 저장 프로세스 중 오류: {e!s}")

                return response

            except Exception as e:
                # 상세한 오류 정보 출력 (디버그 모드일 때만 상세 정보 출력)
                import traceback
                error_msg = f"응답 생성 중 오류 발생: {e!s}"

                if self.settings["debug_mode"]:
                    print(f"\n[오류 상세 정보]\n{traceback.format_exc()}")

                self.interface.display_error(error_msg)
                return error_msg

    async def process_command(self, command: str) -> bool:
        """
        사용자 명령어 처리

        Args:
            command: 사용자 명령어

        Returns:
            bool: 계속 실행 여부
        """
        try:
            # 명령어와 인수 분리
            parts = command.split(None, 1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            # 명령어 처리
            if cmd in ["/exit", "/quit"]:
                return False

            elif cmd == "/help":
                self.interface.display_help()

            elif cmd == "/clear":
                self.interface.clear_screen()

            elif cmd == "/settings":
                if args:
                    await self.update_settings(args)
                else:
                    self.interface.display_settings(self.settings)

            elif cmd == "/feedback":
                if not args:
                    self.interface.display_error("/feedback 명령어에는 질문이 필요합니다. 예: /feedback 근육 증강을 위한 최고의 보충제는?")
                else:
                    await self.run_feedback_loop(args)

            elif cmd == "/model":
                if not args:
                    self.interface.display_error("/model 명령어에는 모델명이 필요합니다. 사용 가능한 모델: " + ", ".join(AVAILABLE_MODELS))
                else:
                    await self.change_model(args)

            elif cmd == "/debug":
                # 디버그 모드 토글
                self.settings["debug_mode"] = not self.settings["debug_mode"]
                # OllamaClient의 디버그 모드도 함께 업데이트
                self.client.set_debug_mode(self.settings["debug_mode"])
                state = "켜짐" if self.settings["debug_mode"] else "꺼짐"
                self.interface.console.print(f"[green]디버그 모드가 {state}으로 설정되었습니다.[/green]")

            elif cmd == "/mcp":
                # MCP 명령어 처리 (스피너 방지)
                if self.settings.get("debug_mode", False):
                    self.interface.console.print(f"[cyan][디버그] MCP 명령어 처리: {args}[/cyan]")
                if self.mcp_commands:
                    await self.mcp_commands.handle_mcp_command(args)
                else:
                    self.interface.display_error("MCP 기능을 사용할 수 없습니다. MCP 모듈을 설치해주세요.")

            else:
                self.interface.display_error(f"알 수 없는 명령어: {cmd}. 도움말을 보려면 /help를 입력하세요.")
            return True

        except Exception as e:
            self.interface.display_error(f"명령어 처리 중 오류 발생: {e!s}")
            return True  # 오류가 있어도 계속 실행

    async def save_research_result(self, question: str, response: str, rating_info: Optional[dict] = None) -> None:
        """
        연구 결과를 파일로 저장

        Args:
            question: 사용자 질문
            response: 생성된 응답
            rating_info: 사용자 평가 정보 (선택사항)
        """
        try:
            import datetime
            import json
            from pathlib import Path

            from app.utils.config import OUTPUT_DIR

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            # 질문에서 파일명 생성 (간단하게)
            title_words = question.split()[:5]  # 처음 5개 단어만 사용
            title = "_".join([w for w in title_words if w]).replace("/", "").replace("\\", "").replace("?", "").replace("!", "")
            if not title:  # 파일명이 비어있을 경우
                title = "research_result"

            # 저장 폴더 생성
            output_dir = Path(OUTPUT_DIR) / timestamp
            output_dir.mkdir(parents=True, exist_ok=True)

            # 결과 파일 경로
            output_file = output_dir / f"{timestamp}_{title}.md"

            # 메타데이터 파일 경로
            meta_file = output_dir / f"{timestamp}_{title}_meta.json"

            # 마크다운 파일 저장
            with open(output_file, "w", encoding="utf-8") as f:
                # 제목 추가
                f.write(f"# 신약개발 연구: {question}\n\n")

                # 생성된 결과 추가
                f.write(response)

            # 메타데이터 저장
            metadata = {
                "timestamp": timestamp,
                "question": question,
                "settings": self.settings,
                "model": self.settings["model"],
                "feedback_loop": {
                    "depth": self.settings["feedback_depth"],
                    "width": self.settings["feedback_width"]
                }
            }

            # 평가 정보 추가 (있는 경우)
            if rating_info:
                metadata["user_rating"] = rating_info

            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            # 저장 알림 표시
            if self.interface:
                self.interface.display_saved_notification(str(output_file))

            if self.settings["debug_mode"]:
                print(f"[디버그] 파일 저장 완료: {output_file}")

        except Exception as e:
            # 오류 발생 시 디버그 모드일 때만 상세 정보 출력
            if self.settings["debug_mode"]:
                import traceback
                print(f"[디버그] 파일 저장 중 오류 발생: {e!s}")
                print(traceback.format_exc())
            self.interface.display_error(f"결과 저장 중 오류 발생: {e!s}")


async def start(self):
    """
    챗봇 실행
    """
    # 환영 메시지 표시
    self.interface.display_welcome()

    try:
        # API 가용성 확인
        status = await self.client.check_availability()
        if not status["available"]:
            self.interface.display_error(f"Ollama API에 연결할 수 없습니다: {status.get('error', '알 수 없는 오류')}")
            return

        # 사용 가능한 모델 확인 및 자동 선택
        if not self.initial_model_check_done:
            model_check_result = await self.auto_select_model()
            if not model_check_result:
                return
            self.initial_model_check_done = True

        # 메인 루프 시작
        running = True
        while running:
            # 사용자 입력 받기
            user_input = await self.interface.get_input()

            # 입력이 명령어인지 확인
            if user_input.startswith("/"):
                running = await self.process_command(user_input)
            else:
                # 일반 질문 처리
                await self.process_input(user_input)

    except KeyboardInterrupt:
        self.interface.console.print("\n[yellow]프로그램이 중단되었습니다.[/yellow]")
    except Exception as e:
        import traceback
        error_msg = f"오류가 발생하여 프로그램이 중단되었습니다: {e!s}"

        if self.settings["debug_mode"]:
            print(f"\n[오류 상세 정보]\n{traceback.format_exc()}")

        self.interface.display_error(error_msg)

    async def change_model(self, model_name: str) -> None:
        """
        사용 모델을 변경합니다.

        - 업데이트된 기능: 모델별 어댑터 자동 적용
        - 이전 컨텍스트 및 상태 초기화

        Args:
            model_name: 사용할 새 모델 이름
        """
        # 모델명 정리 (마지막에 :latest 없으면 추가)
        model_name = model_name.strip()
        if ":latest" not in model_name:
            model_name = f"{model_name}:latest"

        try:
            # 1. 모델 사용 가능성 확인
            model_check = await self.client.check_model_availability(model_name)
            if not model_check["available"]:
                self.interface.display_error(
                    f"모델 '{model_name}'을(를) 사용할 수 없습니다. \n"
                    f"오류: {model_check.get('message', '알 수 없는 오류')}"
                )
                return

            # 2. 모델 변경 전 이전 컨텍스트 초기화
            prev_model = self.client.model
            adapter_name = model_check.get('adapter', 'Unknown')

            # 3. 클라이언트 재초기화 (완전한 컨텍스트 분리를 위해)
            if prev_model != model_name:
                # HTTP 클라이언트 종료
                await self.client.close()

                # OllamaClient 연결 초기화
                self.client = OllamaClient(
                    model=model_name,
                    temperature=float(self.settings.get("temperature", 0.7)),
                    max_tokens=int(self.settings.get("max_tokens", 4000)),
                    min_response_length=int(self.settings.get("min_response_length", 500)),
                )
            else:
                # 동일 모델이지만 어댑터 업데이트 필요
                self.client.update_model(model_name)

            # 4. 설정 업데이트
            self.settings["model"] = model_name

            # 5. 사용자에게 피드백 제공
            self.interface.console.print(
                f"[bold green]모델을 '{model_name}'로 변경했습니다.[/bold green]\n"
                f"[blue]어댑터: {adapter_name}[/blue]"
            )
        except Exception as e:
            self.interface.display_error(f"모델 변경 중 오류 발생: {e!s}")
            # 오류 발생 시 자세한 로그 출력
            import traceback
            self.interface.console.print(f"[dim]{traceback.format_exc()}[/dim]", highlight=False)

    async def update_settings(self, args_str: str) -> None:
        """
        사용자 설정 갱신

        Args:
            args_str: 설정 인수 문자열
        """
        try:
            # 설정 문자열 파싱 (형식: key=value)
            parts = args_str.split()
            updates = {}

            for part in parts:
                if "=" in part:
                    key, value = part.split("=", 1)
                    key = key.strip()

                    if key in self.settings:
                        # 적절한 값으로 변환
                        if key in ["feedback_depth", "feedback_width", "min_response_length", "min_references"]:
                            updates[key] = int(value)
                        else:
                            updates[key] = value
                    else:
                        self.interface.display_error(f"알 수 없는 설정: {key}")

            # 유효성 검사
            if "feedback_depth" in updates and (updates["feedback_depth"] < 1 or updates["feedback_depth"] > 10):
                self.interface.display_error("피드백 깊이는 1에서 10 사이의 값이어야 합니다")
                del updates["feedback_depth"]

            if "feedback_width" in updates and (updates["feedback_width"] < 1 or updates["feedback_width"] > 10):
                self.interface.display_error("피드백 너비는 1에서 10 사이의 값이어야 합니다")
                del updates["feedback_width"]

            # 설정 갱신 및 표시
            if updates:
                self.settings.update(updates)
                self.interface.display_settings(self.settings)

        except ValueError as e:
            self.interface.display_error(f"설정 갱신 오류: {e!s}")
        except Exception as e:
            self.interface.display_error(f"예상치 못한 오류: {e!s}")

    async def save_research_result(self, question: str, response: str, rating_info: Optional[dict] = None) -> None:
        """
        연구 결과를 파일로 저장

        Args:
            question: 사용자 질문
            response: 생성된 응답
            rating_info: 사용자 평가 정보 (선택사항)
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # 질문에서 파일명 생성 (간단하게)
        title_words = question.split()[:5]  # 처음 5개 단어만 사용
        title = "_".join(title_words).replace("/", "").replace("\\", "").replace("?", "").replace("!", "")

        # 저장 폴더 생성
        output_dir = Path(OUTPUT_DIR) / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)

        # 결과 파일 경로
        output_file = output_dir / f"{timestamp}_{title}.md"

        # 메타데이터 파일 경로
        meta_file = output_dir / f"{timestamp}_{title}_meta.json"

        # 마크다운 파일 저장
        with open(output_file, "w", encoding="utf-8") as f:
            # 제목 추가
            f.write(f"# 신약개발 연구: {question}\n\n")

            # 생성된 결과 추가
            f.write(response)

        # 메타데이터 저장
        metadata = {
            "timestamp": timestamp,
            "question": question,
            "settings": self.settings,
            "model": self.settings["model"],
            "feedback_loop": {
                "depth": self.settings["feedback_depth"],
                "width": self.settings["feedback_width"]
            }
        }

        # 평가 정보 추가 (있는 경우)
        if rating_info:
            metadata["user_rating"] = rating_info

        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # 저장 알림 표시
        self.interface.display_saved_notification(str(output_file))

    async def run_feedback_loop(self, question: str) -> None:
        """
        피드백 루프를 실행하여 고품질 응답 생성 및 저장

        Args:
            question: 사용자 질문
        """
        depth = self.settings["feedback_depth"]
        width = self.settings["feedback_width"]

        self.interface.display_feedback_progress(0, depth, "피드백 루프 시작...")

        # 초기 응답 생성 (저장 여부 확인 없이)
        best_response = await self.generate_response(question, ask_to_save=False)

        # 피드백 루프 실행
        for i in range(depth):
            self.interface.display_feedback_progress(i + 1, depth, f"{i + 1}단계: 대체 응답 생성 중...")

            # 스피너 표시
            with self.interface.display_thinking():
                try:
                    # 대체 응답 생성 (각 응답은 이전 최서 응답에 대한 피드백 제공)
                    feedback_prompt = f"""
이 질문에 대해 이전에 제공한 답변을 개선해주세요:

질문: {question}

이전 답변:
{best_response}

개선점:
1. 과학적 근거 강화 (연구와 데이터 추가)
2. 영양소 복용방법 및 주의사항 상세화
3. 최신 참고문헌 추가 (최소 2개 이상)
4. 구체적인 예시 추가

위 개선점을 반영하여 더 완성도 높은 답변을 제공해주세요.
"""

                    # 너비만큼의 대체 응답 병렬 생성
                    prompts = []
                    for j in range(width):
                        prompts.append({
                            "prompt": feedback_prompt,
                            "system": self.system_prompt,
                            "temperature": 0.5 + (j * 0.2)  # 다양성을 위해 다른 온도 적용
                        })

                    # 병렬 응답 생성
                    alternatives = await self.client.generate_parallel(prompts)

                    # 가장 좋은 응답 선택 (간단한 휘리스틱 - 길이, 참고문헌 수 등 고려)
                    best_score = -1
                    for response in alternatives:
                        if isinstance(response, Exception):
                            continue

                        # 점수 계산 (간단한 휘리스틱)
                        score = len(response)  # 길이 가중치
                        refs_count = response.lower().count("http")  # 참고문헌 수 대략 추정
                        score += refs_count * 200  # 참고문헌에 대한 보너스

                        if score > best_score:
                            best_response = response
                            best_score = score

                except Exception as e:
                    self.interface.display_error(f"피드백 루프 오류: {e!s}")
                    break

        # 최종 응답 표시
        self.interface.display_response(best_response, show_references=True)

        # 사용자에게 결과 저장 여부 확인
        save_choice = await self.interface.ask_to_save()

        # 사용자가 저장을 원하는 경우에만 저장
        if save_choice:
            # 평가 정보 없이 저장 (빈 딕셔너리 전달)
            await self.save_research_result(question, best_response, {})


# 챗봇 런처 구현
async def main(debug_mode=False):
    """
    메인 함수

    Args:
        debug_mode (bool): 디버그 모드 활성화 여부
    """
    chatbot = HealthSupplementChatbot(debug_mode=debug_mode)
    await chatbot.start()
