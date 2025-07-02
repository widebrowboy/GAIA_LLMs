#!/usr/bin/env python3
"""
             

Ollama LLM      CLI          
                            
"""

import datetime
import json
import logging
import os
import sys
import re
from pathlib import Path
import asyncio

#          
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Optional, List, Dict, Any, AsyncGenerator

from app.api.ollama_client import OllamaClient
from app.cli.interface import CliInterface
from app.utils.config import (
    AVAILABLE_MODELS,
    DEFAULT_FEEDBACK_DEPTH,
    DEFAULT_FEEDBACK_WIDTH,
    MIN_REFERENCES,
    MIN_RESPONSE_LENGTH,
    OUTPUT_DIR,
    Config
)
from app.utils.interface import UserInterface
from app.utils.prompt_manager import get_prompt_manager, get_system_prompt

# MCP   
try:
    from mcp.integration.mcp_manager import MCPManager
    from app.cli.mcp_commands import MCPCommands
    from app.core.biomcp_integration import BioMCPIntegration
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"[Warning] MCP    import   : {e}")
    MCPManager = None
    MCPCommands = None
    BioMCPIntegration = None
    MCP_AVAILABLE = False


class DrugDevelopmentChatbot:
    """
                  

                   AI             .
    """

    def __init__(self, config: Config):
        self.config = config
        self.context = []
        self.last_topic = None
        self.logger = logging.getLogger(__name__)
        #                      
        self.settings = {
            "debug_mode": config.debug_mode,
            "mcp_enabled": True,
            #            
            "feedback_depth": config.feedback_depth,
            "feedback_width": config.feedback_width,
            #         
            "min_response_length": config.min_response_length,
            "min_references": config.min_references
        }
        self.mcp_enabled = True  # MCP          
        # Ollama           (config                )
        self.client = OllamaClient(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            min_response_length=config.min_response_length,
            debug_mode=config.debug_mode,
        )
        
        #         
        self.current_mode = "normal"  # "normal"    "deep_research"
        self.mode_banner_shown = False
        
        #       
        self.initial_model_check_done = False
        self.conversation_history = []
        
        #             
        self.prompt_manager = get_prompt_manager()
        self.current_prompt_type = "default"
        self.system_prompt = get_system_prompt(self.current_prompt_type)
        
        #          
        self.interface = UserInterface()
        
        # MCP         
        self.mcp_manager = None
        
        # MCP            
        try:
            from app.cli.mcp_commands import MCPCommands
            self.mcp_commands = MCPCommands(self)
        except ImportError as e:
            self.mcp_commands = None
            if self.config.debug_mode:
                print(f"[Warning] MCP               : {e}")

    def detect_language(self, text: str) -> str:
        """
        사용자 입력 텍스트의 언어를 감지합니다.
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            str: 'korean' 또는 'english'
        """
        import re
        
        # 한글 문자 패턴 (한글 음절, 자음, 모음)
        korean_pattern = r'[가-힣ㄱ-ㅎㅏ-ㅣ]'
        # 영어 문자 패턴 (알파벳)
        english_pattern = r'[a-zA-Z]'
        
        # 전체 텍스트에서 한글과 영어 문자 개수 세기
        korean_chars = len(re.findall(korean_pattern, text))
        english_chars = len(re.findall(english_pattern, text))
        
        # 총 문자 수 (공백, 숫자, 특수문자 제외)
        total_chars = korean_chars + english_chars
        
        # 문자가 없으면 기본값 한국어
        if total_chars == 0:
            return 'korean'
        
        # 한글 비율 계산
        korean_ratio = korean_chars / total_chars
        
        # 한글 비율이 30% 이상이면 한국어, 아니면 영어
        if korean_ratio >= 0.3:
            return 'korean'
        else:
            return 'english'

    def format_response_as_markdown(self, question: str, ai_response: str, references: list = None, metadata: dict = None) -> str:
        """
        Convert chat response and metadata to a structured Markdown document in CLAUDE.md style.

        Args:
            question (str): User's research question.
            ai_response (str): AI-generated answer (raw, not formatted).
            references (list, optional): List of reference strings. If None or less than 2, basic references will be added.
            metadata (dict, optional): Metadata such as timestamp, model name, feedback info, etc.

        Returns:
            str: Professionally formatted Markdown document.
        """
        import datetime
        # 1. Extract topic for title
        topic = self._extract_topic(question) or "Research Report"
        # 2. Remove timestamp display
        # 3. Model
        model = metadata.get("model") if metadata and "model" in metadata else getattr(self, "model", "Unknown")
        # 4. Feedback
        feedback = metadata.get("feedback") if metadata and "feedback" in metadata else "-"
        # 5. References (ensure at least 2)
        ref_list = references or []
        if len(ref_list) < 2:
            ref_list += self._generate_basic_references()[:2-len(ref_list)]
        # 6. Section parsing (split response heuristically)
        # Try to split by Korean section headers if present
        section_map = {
            "     ": "Problem Definition",
            "     ": "Core Content",
            "      ": "Scientific Evidence",
            "            ": "Usage & Precautions",
            "       ": "Conclusion & Summary",
            "     ": "References"
        }
        # Heuristic: split by numbered or header lines, else fallback
        def extract_section(text, keyword):
            import re
            p = rf"[#]*\s*{keyword}.*?\n(.+?)(?=\n[#]+|\n[A-Z -  ]+\n|$)"
            m = re.search(p, text, re.DOTALL)
            return m.group(1).strip() if m else "-"
        sections = {}
        for kor, eng in section_map.items():
            sections[eng] = extract_section(ai_response, kor)
        # Fallback: if all blank, put all in Core Content
        if all(v == "-" for v in sections.values()):
            sections["Core Content"] = ai_response.strip()
        # 7. Markdown template
        md = f"""# {topic}

**Query:** {question}

**Generated:** {now} | **Model:** {model} | **Feedback:** {feedback}

---

## 1. Problem Definition
{sections['Problem Definition']}

## 2. Core Content
{sections['Core Content']}

## 3. Scientific Evidence
{sections['Scientific Evidence']}

## 4. Usage & Precautions
{sections['Usage & Precautions']}

## 5. Conclusion & Summary
{sections['Conclusion & Summary']}

## 6. References
""" + "\n".join([f"{i+1}. {ref}" for i, ref in enumerate(ref_list)]) + """

---
*Generated by GAIA-BT research assistant with scientific rigor.*"""
        return md

    def get_response(self, query: str) -> str:
        """Get response for query."""
        if not query:
            return "Query is empty."
        
        if len(query) > 500:
            return "Query is too long. Maximum 500 characters allowed."

        #         
        self.context.append(query)
        if len(self.context) > 5:  #    5            
            self.context.pop(0)

        #      
        topic_in_query = self._extract_topic(query)
        if "  " in query:
            # '  '                              
            if topic_in_query:
                response = self._generate_response(topic_in_query)
                self.last_topic = topic_in_query
            elif self.last_topic:
                response = self._generate_response(self.last_topic)
            else:
                response = self._generate_response(query)
        else:
            response = self._generate_response(query)
            #         
            if topic_in_query:
                self.last_topic = topic_in_query

        return response

    def _extract_topic(self, query: str) -> str:
        """                 ."""
        #                    
        detail_topics = ["   D", "   C", "   B", "   A"]
        for topic in detail_topics:
            if topic in query:
                return topic
        topics = ["   ", "   ", "       ", "   "]
        for topic in topics:
            if topic in query:
                return topic
        return ""

    def _generate_response(self, query: str) -> str:
        """                """
        #          
        if self.config.debug_mode:
            print(f"[Debug] [   ]      : '{query}'")
            print(f"[Debug] [   ]        : {self.context}")
            print(f"[Debug] [   ]       : {self.last_topic}")

        #                 
        if "   D" in query:
            return "   D                                 . " \
                   "                 ,        ,                 . " \
                   "                      ,                                     ."
        if "   C" in query:
            return "   C                                   . " \
                   "              ,      ,                 . " \
                   "                 100mg     ,                              ."
        if "   " in query:
            return "                                     . " \
                   "               ,       ,               . " \
                   "                      ,                            ."
        elif "   " in query:
            return "   3          ,      ,     ,                 . " \
                   "              ,    ,        . " \
                   "              ,                         ."
        elif "       " in query:
            return "                            . " \
                   "                           , " \
                   "                                ."
        elif "   " in query:
            return "                        . " \
                   "                6-20mg  , " \
                   "                      ."
        else:
            return "     .                      . " \
                   "                                        ."

    async def auto_select_model(self):
        """
        모델 자동 선택 (자동 모델 변경 비활성화)
        현재 설정된 모델을 그대로 유지하고 설치 여부만 확인
        """
        try:
            # 설치된 모델 목록 확인
            models = await self.client.list_models()
            available_models = [m.get("name") for m in models]

            # 현재 모델이 설치되어 있는지 확인만 하고 변경하지 않음
            if self.client.model not in available_models:
                # 모델이 설치되어 있지 않아도 변경하지 않고 경고만 출력
                self.interface.display_error(f"현재 모델 '{self.client.model}'이 설치되어 있지 않습니다. 하지만 자동 변경을 하지 않고 유지합니다.")
                self.logger.warning(f"모델 {self.client.model}이 설치되어 있지 않지만 자동 변경 비활성화로 인해 유지")
                # 모델을 변경하지 않고 그대로 유지
                return True
            else:
                # 모델이 설치되어 있으면 성공
                self.logger.info(f"현재 모델 {self.client.model}이 설치되어 있음을 확인")
                return True

        except Exception as e:
            self.interface.display_error(f"모델 확인 중 오류: {e!s}")
            self.logger.error(f"auto_select_model 오류: {e}")
            # 오류가 있어도 현재 모델 설정 유지
            return True

    async def start(self):
        """
             
        """
        #          
        self.interface.display_welcome()

        try:
            # API       
            status = await self.client.check_availability()
            if not status["available"]:
                self.interface.display_error(f"Ollama API            : {status.get('error', '         ')}")
                return

            #                     
            if not self.initial_model_check_done:
                model_check_result = await self.auto_select_model()
                if not model_check_result:
                    return
                self.initial_model_check_done = True
        except Exception as e:
            self.interface.display_error(f"API            : {e!s}")
            return

        #         
        while True:
            try:
                #          
                user_input = await self.interface.get_user_input()

                if not user_input:
                    continue

                #       
                if user_input.startswith("/"):
                    continue_chat = await self.process_command(user_input)
                    if not continue_chat:
                        break
                else:
                    #         
                    await self.generate_response(user_input)
            except KeyboardInterrupt:
                print("\n           .")
                break
            except Exception as e:
                self.interface.display_error(f"     : {e!s}")

        print("             .")

    async def deep_search_with_database(self, user_input):
        """Database         Deep Search    - DrugBank, OpenTargets, ChEMBL, BioMCP      """
        #          MCP Deep Search         
        if hasattr(self, 'current_mode') and self.current_mode == "normal":
            if self.settings.get("debug_mode", False):
                self.interface.print_thinking("[Drug]             AI          ")
            return None
        
        if not self.mcp_enabled:
            if self.settings.get("debug_mode", False):
                self.interface.print_thinking("[Error] Database             ")
            return None
        
        try:
            if self.config.show_mcp_output:
                self.interface.print_thinking("[Research]    Database Deep Search     ...")
            search_results = []
            # 데이터 출처 추적을 위한 리스트
            data_sources = []
            
            #                     
            input_lower = user_input.lower()
            is_drug_related = any(kw in input_lower for kw in ['  ', '   ', '  ', '   ', '    ', 'drug', 'medication', 'aspirin', '    ', 'metformin', '    '])
            is_target_related = any(kw in input_lower for kw in ['  ', '   ', '   ', 'target', 'protein', 'gene', 'brca1', 'tp53', 'egfr'])
            is_disease_related = any(kw in input_lower for kw in ['  ', ' ', '  ', 'cancer', 'disease', 'diabetes', '   ', 'breast', '     ', 'alzheimer'])
            is_chemical_related = any(kw in input_lower for kw in ['  ', '  ', '  ', 'chemical', 'molecule', 'structure', 'smiles'])
            
            #          
            if self.settings.get("debug_mode", False) and self.config.show_mcp_output:
                self.interface.print_thinking(f"[Search]       :   ={is_drug_related},   ={is_target_related},   ={is_disease_related},   ={is_chemical_related}")
            
            # 1. Sequential Thinking           
            thinking_success = False
            try:
                if self.config.show_mcp_output:
                    self.interface.print_thinking("[Brain] AI              ...")
                
                #             (enableBranching   )
                thinking_result = await self.mcp_commands.call_tool(
                    client_id='default',
                    tool_name='start_thinking',
                    arguments={
                        'problem': f'             : {user_input}',
                        'maxSteps': 5
                    }
                )
                
                if self.settings.get("debug_mode", False):
                    self.interface.print_thinking(f"[Debug] Sequential Thinking   : {thinking_result}")
                
                #                    
                if (thinking_result and 
                    'content' in thinking_result and 
                    thinking_result['content'] and 
                    len(thinking_result['content']) > 0):
                    
                    thinking_text = thinking_result['content'][0].get('text', '').strip()
                    #                    
                    if thinking_text and len(thinking_text) > 30:  #    30             
                        search_results.append(f"[Brain] AI      :\n{thinking_text}")
                        thinking_success = True
                        if self.config.show_mcp_output:
                            self.interface.print_thinking("O AI      ")
                
                if not thinking_success and self.config.show_mcp_output:
                    self.interface.print_thinking("[Warning] AI         ")
                    
            except Exception as e:
                if self.config.show_mcp_output:
                    self.interface.print_thinking(f"[No] AI      : {e}")
                if self.settings.get("debug_mode", False):
                    import traceback
                    self.interface.print_thinking(f"[Debug]      : {traceback.format_exc()}")
                    if "Method not implemented" in str(e):
                        self.interface.print_thinking("[Debug] Sequential Thinking                         ")
            
            # 2. DrugBank             
            if is_drug_related:
                try:
                    if self.config.show_mcp_output:
                        self.interface.print_thinking("[Drug] DrugBank          ...")
                    
                    #            
                    common_drugs = ['aspirin', 'ibuprofen', 'metformin', 'insulin', 'acetaminophen', '    ', '    ']
                    search_terms = []
                    
                    for drug in common_drugs:
                        if drug in input_lower:
                            search_terms.append(drug)
                    
                    #                      
                    if not search_terms:
                        if 'pain' in input_lower or '  ' in input_lower:
                            search_terms = ['aspirin']
                        elif 'diabetes' in input_lower or '  ' in input_lower:
                            search_terms = ['metformin']
                        else:
                            search_terms = ['cancer']  #              
                    
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"[Debug] DrugBank    : {search_terms}")
                    
                    drugbank_success = False
                    for term in search_terms[:2]:  #    2    
                        try:
                            #           ID   
                            drugbank_result = await self.mcp_commands.call_tool(
                                client_id='drugbank-mcp',  #           ID
                                tool_name='search_drugs',
                                arguments={'query': term, 'limit': 3}
                            )
                            
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"[Debug] DrugBank {term}   : {drugbank_result}")
                            
                            #                    
                            if (drugbank_result and 
                                'content' in drugbank_result and 
                                drugbank_result['content'] and 
                                len(drugbank_result['content']) > 0):
                                
                                drug_text = drugbank_result['content'][0].get('text', '').strip()
                                #                    
                                if drug_text and len(drug_text) > 50:  #    50             
                                    search_results.append(f"[Drug] DrugBank - {term}:\n{drug_text}")
                                    drugbank_success = True
                                    # 데이터 출처 추가
                                    data_sources.append({
                                        'source': 'DrugBank',
                                        'query': term,
                                        'url': f'https://www.drugbank.ca/drugs?query={term}',
                                        'type': 'Drug Database'
                                    })
                                    if self.settings.get("debug_mode", False):
                                        self.interface.print_thinking(f"[Debug] DrugBank {term}      : {len(drug_text)} ")
                                
                        except Exception as tool_error:
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"[Debug] DrugBank {term}        : {tool_error}")
                            continue
                    
                    if drugbank_success:
                        self.interface.print_thinking("O DrugBank      ")
                    else:
                        self.interface.print_thinking("[Warning] DrugBank         ")
                        
                except Exception as e:
                    self.interface.print_thinking(f"[No] DrugBank      : {e}")
                    if self.settings.get("debug_mode", False):
                        import traceback
                        self.interface.print_thinking(f"[Debug] DrugBank      : {traceback.format_exc()}")
            
            # 3. OpenTargets   -         
            if is_target_related or is_disease_related:
                try:
                    self.interface.print_thinking("[Target] OpenTargets   -         ...")
                    
                    #    /     
                    common_targets = ['BRCA1', 'TP53', 'EGFR', 'KRAS', 'PIK3CA']
                    target_terms = []
                    
                    for target in common_targets:
                        if target.lower() in input_lower:
                            target_terms.append(target)
                    
                    if not target_terms and (is_target_related or is_disease_related):
                        target_terms = ['cancer']  #       
                    
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"[Debug] OpenTargets    : {target_terms}")
                    
                    opentargets_success = False
                    for term in target_terms[:2]:
                        try:
                            #           ID   
                            targets_result = await self.mcp_commands.call_tool(
                                client_id='opentargets-mcp',  #           ID
                                tool_name='search_targets' if is_target_related else 'search_diseases',
                                arguments={'query': term, 'limit': 3}
                            )
                            
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"[Debug] OpenTargets {term}   : {targets_result}")
                            
                            #                    
                            if (targets_result and 
                                'content' in targets_result and 
                                targets_result['content'] and 
                                len(targets_result['content']) > 0):
                                
                                targets_text = targets_result['content'][0].get('text', '').strip()
                                #                    
                                if targets_text and len(targets_text) > 50:  #    50             
                                    search_results.append(f"[Target] OpenTargets - {term}:\n{targets_text}")
                                    opentargets_success = True
                                    # 데이터 출처 추가
                                    data_sources.append({
                                        'source': 'OpenTargets',
                                        'query': term,
                                        'url': f'https://platform.opentargets.org/search?query={term}',
                                        'type': 'Target/Disease Database'
                                    })
                                    if self.settings.get("debug_mode", False):
                                        self.interface.print_thinking(f"[Debug] OpenTargets {term}      : {len(targets_text)} ")
                                
                        except Exception as tool_error:
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"[Debug] OpenTargets {term}        : {tool_error}")
                            continue
                    
                    if opentargets_success:
                        self.interface.print_thinking("O OpenTargets      ")
                    else:
                        self.interface.print_thinking("[Warning] OpenTargets         ")
                        
                except Exception as e:
                    self.interface.print_thinking(f"[No] OpenTargets      : {e}")
                    if self.settings.get("debug_mode", False):
                        import traceback
                        self.interface.print_thinking(f"[Debug] OpenTargets      : {traceback.format_exc()}")
            
            # 4. ChEMBL                 
            if is_chemical_related or is_drug_related:
                try:
                    self.interface.print_thinking("[Lab] ChEMBL          ...")
                    
                    #     /     
                    chemical_terms = []
                    if 'aspirin' in input_lower or '    ' in input_lower:
                        chemical_terms.append('aspirin')
                    elif 'fluorouracil' in input_lower or '5-FU' in input_lower:
                        chemical_terms.append('fluorouracil')
                    else:
                        chemical_terms.append('cancer')  #            
                    
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"[Debug] ChEMBL    : {chemical_terms}")
                    
                    chembl_success = False
                    for term in chemical_terms[:2]:
                        try:
                            # ChEMBL  default         
                            chembl_result = await self.mcp_commands.call_tool(
                                client_id='default',  # ChEMBL          
                                tool_name='search_molecule',
                                arguments={'query': term, 'limit': 3}
                            )
                            
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"[Debug] ChEMBL {term}   : {chembl_result}")
                            
                            #                    
                            if (chembl_result and 
                                'content' in chembl_result and 
                                chembl_result['content'] and 
                                len(chembl_result['content']) > 0):
                                
                                chembl_text = chembl_result['content'][0].get('text', '').strip()
                                #                    
                                if chembl_text and len(chembl_text) > 50:  #    50             
                                    search_results.append(f"[Lab] ChEMBL - {term}:\n{chembl_text}")
                                    chembl_success = True
                                    # 데이터 출처 추가
                                    data_sources.append({
                                        'source': 'ChEMBL',
                                        'query': term,
                                        'url': f'https://www.ebi.ac.uk/chembl/g/#search_results/all/query={term}',
                                        'type': 'Chemical Database'
                                    })
                                    if self.settings.get("debug_mode", False):
                                        self.interface.print_thinking(f"[Debug] ChEMBL {term}      : {len(chembl_text)} ")
                                
                        except Exception as tool_error:
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"[Debug] ChEMBL {term}        : {tool_error}")
                            continue
                    
                    if chembl_success:
                        self.interface.print_thinking("O ChEMBL      ")
                    else:
                        self.interface.print_thinking("[Warning] ChEMBL         ")
                        
                except Exception as e:
                    self.interface.print_thinking(f"[No] ChEMBL      : {e}")
                    if self.settings.get("debug_mode", False):
                        import traceback
                        self.interface.print_thinking(f"[Debug] ChEMBL      : {traceback.format_exc()}")
            
            # 5. BioMCP              
            biomcp_success = False
            try:
                self.interface.print_thinking("[Doc] BioMCP          ...")
                
                #       -             (article_searcher)
                try:
                    articles_result = await self.mcp_commands.call_tool(
                        client_id='default',  # BioMCP          
                        tool_name='article_searcher',  #    BioMCP     
                        arguments={
                            'call_benefit': f'            "{user_input}"         ',
                            'keywords': user_input,
                            'diseases': user_input if is_disease_related else None,
                            'genes': user_input if is_target_related else None,
                            'chemicals': user_input if is_chemical_related or is_drug_related else None
                        }
                    )
                    
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"[Debug] BioMCP         : {articles_result}")
                    
                    #                    
                    if (articles_result and 
                        'content' in articles_result and 
                        articles_result['content'] and 
                        len(articles_result['content']) > 0):
                        
                        articles_text = articles_result['content'][0].get('text', '').strip()
                        #                    
                        if articles_text and len(articles_text) > 50:  #    50             
                            search_results.append(f"[Doc] BioMCP   :\n{articles_text}")
                            biomcp_success = True
                            # 데이터 출처 추가
                            data_sources.append({
                                'source': 'BioMCP (PubMed)',
                                'query': user_input,
                                'url': f'https://pubmed.ncbi.nlm.nih.gov/?term={user_input}',
                                'type': 'Scientific Literature'
                            })
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"[Debug] BioMCP         : {len(articles_text)} ")
                
                except Exception as article_error:
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"[Debug] BioMCP         : {article_error}")
                    if "Method not implemented" in str(article_error):
                        self.interface.print_thinking("[Debug] BioMCP                         ")
                
                #         (         ) -             (trial_searcher)
                if is_disease_related:
                    try:
                        trials_result = await self.mcp_commands.call_tool(
                            client_id='default',
                            tool_name='trial_searcher',  #    BioMCP     
                            arguments={
                                'call_benefit': f'"{user_input}"               ',
                                'conditions': user_input,
                                'recruiting_status': 'ANY',
                                'study_type': 'INTERVENTIONAL'
                            }
                        )
                        
                        if self.settings.get("debug_mode", False):
                            self.interface.print_thinking(f"[Debug] BioMCP           : {trials_result}")
                        
                        #                    
                        if (trials_result and 
                            'content' in trials_result and 
                            trials_result['content'] and 
                            len(trials_result['content']) > 0):
                            
                            trials_text = trials_result['content'][0].get('text', '').strip()
                            #                    
                            if trials_text and len(trials_text) > 50:  #    50             
                                search_results.append(f"[Hospital] BioMCP     :\n{trials_text}")
                                biomcp_success = True
                                # 데이터 출처 추가
                                data_sources.append({
                                    'source': 'BioMCP (ClinicalTrials)',
                                    'query': user_input,
                                    'url': f'https://clinicaltrials.gov/search?cond={user_input}',
                                    'type': 'Clinical Trials'
                                })
                                if self.settings.get("debug_mode", False):
                                    self.interface.print_thinking(f"[Debug] BioMCP           : {len(trials_text)} ")
                    
                    except Exception as trial_error:
                        if self.settings.get("debug_mode", False):
                            self.interface.print_thinking(f"[Debug] BioMCP           : {trial_error}")
                            if "Method not implemented" in str(trial_error):
                                self.interface.print_thinking("[Debug] BioMCP                         ")
                
                if biomcp_success:
                    self.interface.print_thinking("O BioMCP      ")
                else:
                    self.interface.print_thinking("[Warning] BioMCP         ")
                    
            except Exception as e:
                self.interface.print_thinking(f"[No] BioMCP      : {e}")
                if self.settings.get("debug_mode", False):
                    import traceback
                    self.interface.print_thinking(f"[Debug] BioMCP      : {traceback.format_exc()}")
                    if "Method not implemented" in str(e):
                        self.interface.print_thinking("[Debug] BioMCP               MCP           ")
            
            # 6. BioRxiv            
            biorxiv_success = False
            try:
                self.interface.print_thinking("[Note] BioRxiv            ...")
                
                #             (   7 )
                try:
                    #                  
                    search_terms = []
                    if is_drug_related:
                        search_terms.extend(['drug', 'therapy', 'treatment'])
                    if is_target_related:
                        search_terms.extend(['target', 'protein', 'gene'])
                    if is_disease_related:
                        search_terms.extend(['cancer', 'disease', 'therapy'])
                    if is_chemical_related:
                        search_terms.extend(['compound', 'molecule', 'chemical'])
                    
                    #                      
                    if not search_terms:
                        search_terms = ['biomedical', 'research']
                    
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"[Debug] BioRxiv      :    7       ")
                    
                    # BioRxiv            
                    biorxiv_result = await self.mcp_commands.call_tool(
                        client_id='biorxiv-mcp',  # BioRxiv MCP      
                        tool_name='get_recent_preprints',
                        arguments={
                            'server': 'biorxiv',
                            'interval': 7,  #    7 
                            'limit': 10     #    10 
                        }
                    )
                    
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"[Debug] BioRxiv      : {biorxiv_result}")
                    
                    #                    
                    if (biorxiv_result and 
                        'content' in biorxiv_result and 
                        biorxiv_result['content'] and 
                        len(biorxiv_result['content']) > 0):
                        
                        biorxiv_text = biorxiv_result['content'][0].get('text', '').strip()
                        #                    
                        if biorxiv_text and len(biorxiv_text) > 50:  #    50             
                            search_results.append(f"[Note] BioRxiv      :\n{biorxiv_text}")
                            biorxiv_success = True
                            # 데이터 출처 추가
                            data_sources.append({
                                'source': 'BioRxiv',
                                'query': ' '.join(search_terms[:3]),
                                'url': f'https://www.biorxiv.org/search/{"%20".join(search_terms[:3])}',
                                'type': 'Preprint Repository'
                            })
                            if self.settings.get("debug_mode", False):
                                self.interface.print_thinking(f"[Debug] BioRxiv      : {len(biorxiv_text)} ")
                    
                except Exception as biorxiv_error:
                    if self.settings.get("debug_mode", False):
                        self.interface.print_thinking(f"[Debug] BioRxiv      : {biorxiv_error}")
                        if "Method not implemented" in str(biorxiv_error):
                            self.interface.print_thinking("[Debug] BioRxiv                         ")
                
                if biorxiv_success:
                    self.interface.print_thinking("O BioRxiv      ")
                else:
                    self.interface.print_thinking("[Warning] BioRxiv         ")
                    
            except Exception as e:
                self.interface.print_thinking(f"[No] BioRxiv      : {e}")
                if self.settings.get("debug_mode", False):
                    import traceback
                    self.interface.print_thinking(f"[Debug] BioRxiv      : {traceback.format_exc()}")
                    if "Method not implemented" in str(e):
                        self.interface.print_thinking("[Debug] BioRxiv               MCP           ")
            
            # 7. Web Search               
            web_search_success = False
            try:
                self.interface.print_thinking("[Web] Web Search            ...")
                
                # Sequential Thinking                         
                web_queries = []
                
                # THINK STEP 1: 리뷰 논문 중심 질의 생성
                if is_drug_related:
                    web_queries.append(f"{user_input} drug development review")
                    web_queries.append(f"{user_input} therapeutic review recent advances")
                
                if is_target_related:
                    web_queries.append(f"{user_input} target validation review")
                    web_queries.append(f"{user_input} therapeutic target systematic review")
                
                if is_disease_related:
                    web_queries.append(f"{user_input} treatment review")
                    web_queries.append(f"{user_input} therapy systematic review")
                
                if is_chemical_related:
                    web_queries.append(f"{user_input} compound review")
                    web_queries.append(f"{user_input} chemical biology review")
                
                # 기본 질의가 없다면 일반적인 리뷰 질의 추가
                if not web_queries:
                    web_queries.append(f"{user_input} review recent advances")
                    web_queries.append(f"{user_input} systematic review")
                
                # 최대 2개 질의로 제한 (총 10개 결과를 위해)
                web_queries = web_queries[:2]
                
                if self.settings.get("debug_mode", False):
                    self.interface.print_thinking(f"[Debug] Web Search      : {web_queries}")
                
                # 각 질의에 대해 웹 검색 수행
                for query in web_queries:
                    try:
                        web_result = await self.mcp_commands.call_tool(
                            client_id='web-search',
                            tool_name='search',
                            arguments={
                                'query': query,
                                'limit': 5,  # 각 질의당 5개 결과 (총 최대 10개)
                                'reviewOnly': True,  # 리뷰 논문만 검색
                                'timeRange': 'recent',  # 최근 3-5년 범위
                                'excludePrimary': True  # 1차 연구 논문 제외
                            }
                        )
                        
                        if self.settings.get("debug_mode", False):
                            self.interface.print_thinking(f"[Debug] Web Search '{query[:30]}...'      : {web_result}")
                        
                        # 웹 검색 결과 처리
                        if (web_result and 
                            'content' in web_result and 
                            web_result['content'] and 
                            len(web_result['content']) > 0):
                            
                            web_text = web_result['content'][0].get('text', '').strip()
                            if web_text and len(web_text) > 20:  # 최소 20자 이상 결과만 포함
                                # JSON 형태의 결과를 파싱하여 사용자 친화적으로 포맷
                                try:
                                    import json
                                    web_data = json.loads(web_text)
                                    if isinstance(web_data, list) and len(web_data) > 0:
                                        formatted_results = []
                                        for item in web_data[:3]:  # 최대 3개 결과만 포함
                                            title = item.get('title', 'No title')
                                            url = item.get('url', 'No URL')
                                            description = item.get('description', 'No description')
                                            formatted_results.append(f"• **{title}**\n  {description}\n  URL: {url}")
                                        
                                        search_results.append(f"[Web] Web Search '{query}':\n" + "\n\n".join(formatted_results))
                                        web_search_success = True
                                        
                                        # 데이터 출처 추가
                                        data_sources.append({
                                            'source': 'Web Search',
                                            'query': query,
                                            'url': f'https://www.google.com/search?q={query.replace(" ", "+")}',
                                            'type': 'Web Results'
                                        })
                                        
                                        if self.settings.get("debug_mode", False):
                                            self.interface.print_thinking(f"[Debug] Web Search      : {len(formatted_results)}     ")
                                except json.JSONDecodeError:
                                    # JSON 파싱 실패 시 원본 텍스트 사용
                                    search_results.append(f"[Web] Web Search '{query}':\n{web_text}")
                                    web_search_success = True
                    
                    except Exception as query_error:
                        if self.settings.get("debug_mode", False):
                            self.interface.print_thinking(f"[Debug] Web Search '{query}'      : {query_error}")
                
                if web_search_success:
                    self.interface.print_thinking("O Web Search      ")
                else:
                    self.interface.print_thinking("[Warning] Web Search         ")
                    
            except Exception as e:
                self.interface.print_thinking(f"[No] Web Search      : {e}")
                if self.settings.get("debug_mode", False):
                    import traceback
                    self.interface.print_thinking(f"[Debug] Web Search      : {traceback.format_exc()}")
            
            # 8.           
            if search_results:
                self.interface.print_thinking("[Data]    Deep Search    -         ...")
                
                #                          
                successful_dbs = []
                for result in search_results:
                    if "[Drug] DrugBank" in result:
                        successful_dbs.append("[Drug] DrugBank")
                    elif "[Target] OpenTargets" in result:
                        successful_dbs.append("[Target] OpenTargets")
                    elif "[Lab] ChEMBL" in result:
                        successful_dbs.append("[Lab] ChEMBL")
                    elif "[Doc] BioMCP" in result:
                        successful_dbs.append("[Doc] BioMCP")
                    elif "[Note] BioRxiv" in result:
                        successful_dbs.append("[Note] BioRxiv")
                    elif "[Web] Web Search" in result:
                        successful_dbs.append("[Web] Web Search")
                    elif "[Brain] AI" in result:
                        successful_dbs.append("[Brain] Sequential Thinking")
                
                # 데이터 출처 섹션 생성
                data_sources_section = ""
                if data_sources:
                    data_sources_section = f"""

[References] **실제 활용된 데이터 출처:**
"""
                    for idx, source in enumerate(data_sources, 1):
                        data_sources_section += f"""
{idx}. **{source['source']}** ({source['type']})
   - 검색어: "{source['query']}"
   - 링크: {source['url']}
"""

                result_stats = f"""
[Research] **GAIA-BT v2.0 Alpha    Deep Search      **

[Data] **          Database       :**
{' + '.join(set(successful_dbs)) if successful_dbs else '        '}

  **             :**
-      : "{user_input}"
-          : {'O   ' if is_drug_related else 'X    '}
-   /       : {'O   ' if is_target_related else 'X    '}
-          : {'O   ' if is_disease_related else 'X    '}
-          : {'O   ' if is_chemical_related else 'X    '}

[Target] **     :** {len(search_results)}                     

------------------------------------------------------------------------------
"""
                
                combined_results = result_stats + "\n\n" + "\n\n".join(search_results) + data_sources_section
                
                if self.settings.get("debug_mode", False):
                    self.interface.print_thinking(f"[Debug]            : {len(combined_results)} ")
                
                return combined_results
            else:
                self.interface.print_thinking("[Warning]    Database                      ")
                
                # Database                          
                fallback_message = f"""
[Search] **Database Deep Search      **

  **      :** "{user_input}"

[Warning] **      :**
- Database             ('/database start'       )
-                            
-                  
- Database         ("Method not implemented: tools/call")

   **     :**
1. '/database status'      Database         
2. '/database stop'   '/database start'        
3.                      
4. '/debug'                      

  **        :**
- "EGFR                                "
- "BRCA1                                  "
- "                                     "
"""
                
                return fallback_message
            
        except Exception as e:
            self.interface.print_thinking(f"Deep Search     : {e}")
            if self.settings.get("debug_mode", False):
                import traceback
                self.interface.print_thinking(f"[Debug] Deep Search      : {traceback.format_exc()}")
            return None

    async def generate_response(self, question: str, ask_to_save: bool = True) -> str:
        """
               AI      

        Args:
            question:       
            ask_to_save:                     (   : True)

        Returns:
            str:       
        """
        # 언어 감지
        detected_language = self.detect_language(question)
        
        # MCP Deep Search    (Deep Research      )
        deep_search_context = None
        if self.mcp_enabled and hasattr(self, 'current_mode') and self.current_mode == "deep_research":
            deep_search_context = await self.deep_search_with_database(question)
            
            # MCP     Deep Search           (        )
        
        #               
        self.interface.print_thinking()
        try:
            #    :          (          )
            if self.settings["debug_mode"]:
                print(f"\n[   ]        : {question[:50]}...")
                print(f"[   ]      : {self.client.model}")

            # Deep Search                      
            enhanced_system_prompt = self.system_prompt
            references_section = ""
            
            # 언어별 기본 응답 지침 추가
            language_instruction = ""
            if detected_language == 'english':
                language_instruction = """
**IMPORTANT: The user's question is in English. Please respond in English throughout your entire response.**
- Use English for all explanations, descriptions, and analysis
- Technical terms (drug names, target names, gene names) should remain in their original English form
- Keep disease names, mechanisms, and general medical terms in English
- Maintain professional English academic writing style
"""
            else:  # korean
                language_instruction = """
**중요: 사용자의 질문이 한국어입니다. 전체 응답을 한국어로 작성해주세요.**
- 모든 설명, 기술, 분석을 한국어로 작성
- 전문 용어(약물명, 타겟명, 유전자명)는 영문 그대로 유지
- 질환명, 기전, 일반 의학 용어는 한국어 사용 가능
- 전문적인 한국어 학술 문체 유지
"""
            
            enhanced_system_prompt += language_instruction
            
            # 딥리서치 모드에서 page_format.md와 추가 포맷 가이드 적용
            if self.mcp_enabled and hasattr(self, 'current_mode') and self.current_mode == "deep_research":
                # 언어별 딥리서치 프롬프트 적용
                if detected_language == 'english':
                    page_format_prompt = """

## 📝 ACADEMIC RESEARCH FORMAT (Deep Research Mode)

**You are an academic researcher.** Please follow this paper structure and Sequential Thinking methodology:

### 🧠 SEQUENTIAL THINKING Methodology (Required):

**THINK STEP 1 - Data Collection:**
"I will systematically collect data from [OpenTargets/DrugBank/ChEMBL/BioMCP/WebSearch] for [specific query]..."

**THINK STEP 2 - Data Integration:**
"Integrating results from multiple sources, OpenTargets shows... while DrugBank indicates... and ChEMBL reveals... and web search through recent 3-5 year review papers presents latest trends..."

**THINK STEP 3 - Analysis:**
"Based on the integrated dataset, I can identify key patterns: [pattern analysis]. The competitive landscape analysis shows..."

**THINK STEP 4 - Strategic Insights:**
"Given this evidence base, the strategic implications are... The recommendations include..."

### 학술 논문 구조 템플릿:
```markdown
# [연구 주제]: 딥리서치 분석 보고서

## 초록 (Abstract)
- 연구 목적, 방법론, 주요 발견, 결론 (150-200단어)
- 객관적이고 학술적인 톤
- 기여도 명확히 제시

## 1. 서론 (Introduction) 
- 배경 정보 및 맥락
- 연구 문제 정의
- 연구 목적과 가설
- 연구의 중요성

## 2. 문헌 검토 (Literature Review)
- 기존 연구의 현재 상태
- 주요 이론과 발견사항
- 연구 공백 식별
- 이론적 프레임워크

## 3. 연구 방법론 (Methodology)
- 연구 설계 및 접근법
- 데이터 수집 방법 (Database 소스 활용)
- Sequential Thinking 분석 절차
- 제한사항 및 제약조건

## 4. 결과 (Results)
### 4.1 OpenTargets 분석 결과
### 4.2 DrugBank 정보 분석
### 4.3 ChEMBL 바이오활성 데이터
### 4.4 BioMCP 통합 분석
### 4.5 Sequential Thinking 통합 분석
- 주요 발견사항 제시
- 데이터 해석
- 통계 분석 (해당시)
- 증거 기반 결론

## 5. 토론 (Discussion)
- 결과의 의미 및 시사점
- 기존 문헌과의 비교
- 제한사항 및 제약조건
- 향후 연구 방향

## 6. 결론 (Conclusion)
- 분야에 대한 핵심 기여도
- 실무적 시사점
- 주요 인사이트 요약
- 권장사항

## 참고문헌 (References)
[APA 인용 스타일 준수 - 아래 세부 규칙 적용]

## 💡 추천 후속 연구 질문

**다음 3가지 질문을 통해 연구를 확장해보세요:**

1. **심화 분석 질문**: "[주요 발견]에 대한 더 상세한 분자 메커니즘이나 작용 기전은 무엇인가요?"

2. **비교 연구 질문**: "[연구 주제]와 관련된 다른 치료법이나 접근 방식과 어떤 차이점이 있나요?"

3. **임상 적용 질문**: "이 연구 결과를 실제 임상 환경에서 어떻게 활용할 수 있을까요?"
```

### 🔗 Database 소스별 APA 인용 규칙 (실제 링크 포함 필수):

**OpenTargets 인용 (실제 링크로 표시):**
- 형식: OpenTargets Platform. (2024). [Target Name in English]. Retrieved from https://platform.opentargets.org/[타겟 정보]
- 예시: OpenTargets Platform. (2024). BRCA1. Retrieved from https://platform.opentargets.org/target/ENSG00000012048
- 실제 링크 예시: https://platform.opentargets.org/target/ENSG00000141510 (TP53), https://platform.opentargets.org/target/ENSG00000146648 (EGFR)
- **필수 ID 포함**: ENSG 번호, 질병 연관성 점수, 약물가능성 점수
- **중요**: 타겟명은 반드시 영문 그대로 사용 (예: BRCA1, TP53, EGFR, KRAS, PIK3CA)

**DrugBank 인용 (실제 링크로 표시):**
- 형식: DrugBank. (2024). [Drug Name in English] ([DB 번호]). Retrieved from https://www.drugbank.ca/drugs/[DB 번호]
- 예시: DrugBank. (2024). Aspirin (DB00945). Retrieved from https://www.drugbank.ca/drugs/DB00945
- 실제 링크 예시: https://www.drugbank.ca/drugs/DB00001 (Lepirudin), https://www.drugbank.ca/drugs/DB00002 (Cetuximab)
- **필수 ID 포함**: DB 번호, ATC 코드, 작용 기전, 승인 상태
- **중요**: 약물명은 반드시 영문 그대로 사용 (예: Aspirin, Cetuximab, Bevacizumab, Pembrolizumab)

**ChEMBL 인용 (실제 링크로 표시):**
- 형식: ChEMBL Database. (2024). [Compound Name in English] ([CHEMBL ID]). Retrieved from https://www.ebi.ac.uk/chembl/compound_report_card/[CHEMBL ID]
- 예시: ChEMBL Database. (2024). Aspirin (CHEMBL25). Retrieved from https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL25
- 실제 링크 예시: https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL1 (Lepirudin), https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL59 (Cetuximab)
- **필수 ID 포함**: ChEMBL ID, 분자량, IC50 값, 바이오활성 데이터
- **중요**: 화합물명은 반드시 영문 그대로 사용 (예: Imatinib, Gefitinib, Erlotinib, Osimertinib)

**BioMCP (PubMed) 인용 (실제 링크로 표시):**
- 형식: [Author]. ([Year]). [Title]. [Journal], [Volume(Issue)], [Pages]. PMID: [PMID]. Retrieved from https://pubmed.ncbi.nlm.nih.gov/[PMID]/
- 예시: Smith, J. et al. (2024). Cancer drug discovery. Nature, 610(7931), 123-130. PMID: 12345678. Retrieved from https://pubmed.ncbi.nlm.nih.gov/12345678/
- 실제 링크 예시: https://pubmed.ncbi.nlm.nih.gov/38395897/ (Drug Discovery), https://pubmed.ncbi.nlm.nih.gov/38123456/ (Cancer Research)
- **필수 ID 포함**: PMID, DOI, 저널 Impact Factor, 인용 횟수

**Web Search 인용 (실제 링크로 표시):**
- 형식: [Website Name]. (2024). [Page Title]. Retrieved from [Full URL]
- 예시: Reuters. (2024). Drug development breakthrough reported. Retrieved from https://www.reuters.com/healthcare/pharma/...
- 실제 링크 예시: https://www.nature.com/articles/... (Nature), https://www.science.org/... (Science)
- **필수 정보 포함**: 웹사이트명, 발행일, 페이지 제목, 완전한 URL

**ClinicalTrials.gov 인용 (실제 링크로 표시):**
- 형식: ClinicalTrials.gov. (2024). [임상시험 제목]. Identifier: [NCT 번호]. Retrieved from https://clinicaltrials.gov/study/[NCT 번호]
- 예시: ClinicalTrials.gov. (2024). Phase III Trial of Drug X. Identifier: NCT12345678. Retrieved from https://clinicaltrials.gov/study/NCT12345678
- 실제 링크 예시: https://clinicaltrials.gov/study/NCT00000102 (HIV Drug Study), https://clinicaltrials.gov/study/NCT00000161 (Cancer Trial)
- **필수 ID 포함**: NCT 번호, Phase, 연구 상태, 주요 결과, 등록 환자 수

### 📊 학술 작성 강화 기준:

**톤과 스타일:**
- 객관적이고 학술적인 톤, 증거 기반 논증
- 비판적 분석 접근, 중립적이고 균형잡힌 관점
- Sequential Thinking 과정 명시적 표현

**인용 요구사항 (강화):**
- **APA 스타일 완전 준수** - 모든 Database 소스에 대해
- **본문 인용**: (Database, Year) 또는 Database (Year)
- **사이트별 ID 의무 포함**: DB번호, ENSG번호, ChEMBL ID, PMID, NCT번호 등
- **참고문헌 목록**: 알파벳 순 정렬, 완전한 서지 정보
- **모든 소스의 적절한 귀속** 및 접근 URL 포함

**연구 품질 기준:**
- 체계적이고 철저한 분석, 다각적 관점 고려
- Sequential Thinking 방법론적 엄격성 
- 명확한 논리적 진행, 증거 기반 결론
- **최대한 많은 내용 포함**: 각 Database 소스에서 가능한 모든 관련 데이터 활용

**필수 포함 요소:**
- 각 약물의 DrugBank ID (DB00XXX) - 약물명은 영문 그대로
- 각 타겟의 OpenTargets Gene ID (ENSGXXXXXXXX) - 타겟명은 영문 그대로
- 각 화합물의 ChEMBL ID (CHEMBLXXX) - 화합물명은 영문 그대로
- 임상시험의 NCT 번호
- 논문의 PMID 번호
- 웹 검색 결과의 완전한 URL
- Sequential Thinking 과정의 명시적 서술

**🔤 전문 용어 사용 규칙 (필수 준수):**

**영문 그대로 사용해야 하는 용어들:**
- **약물명**: Aspirin (❌ 아스피린), Pembrolizumab (❌ 펨브롤리주맙), Bevacizumab (❌ 베바시주맙), Cetuximab (❌ 세툭시맙), Trastuzumab (❌ 트라스투주맙)
- **타겟/유전자명**: EGFR (❌ 표피성장인자수용체), BRCA1 (❌ 브르카1), TP53 (❌ p53), KRAS (❌ 케이라스), PIK3CA (❌ 파이케이쓰리시에이), BRAF (❌ 브라프), ALK (❌ 에이엘케이)
- **단백질명**: PD-1 (❌ 피디원), PD-L1 (❌ 피디엘원), VEGF (❌ 베지에프), HER2 (❌ 허투), CTLA-4 (❌ 시티엘에이포)
- **화합물명**: Imatinib (❌ 이마티닙), Gefitinib (❌ 게피티닙), Erlotinib (❌ 엘로티닙), Osimertinib (❌ 오시머티닙), Afatinib (❌ 아파티닙)
- **효소명**: COX-1, COX-2 (❌ 콕스원, 콕스투), PARP (❌ 파프), CDK4/6 (❌ 시디케이포/식스)

**한국어 사용 가능한 용어들:**
- **일반적인 질환명**: 유방암, 폐암, 당뇨병, 고혈압, 심장병, 간염, 신장병
- **일반적인 기전**: 혈관신생억제, 면역관문억제, 세포사멸유도, 신호전달차단
- **임상시험 단계**: 1상, 2상, 3상 임상시험
- **투여경로**: 정맥주사, 경구투여, 피하주사
- **부작용**: 오심, 구토, 설사, 피로감, 발진

**혼합 사용 예시 (권장):**
- "EGFR 표적 항암제" (타겟명 영문 + 설명 한국어)
- "Pembrolizumab의 면역관문억제 효과" (약물명 영문 + 기전 한국어)
- "BRCA1 유전자 변이와 유방암의 연관성" (유전자명 영문 + 질환명 한국어)
- "Imatinib을 이용한 만성골수성백혈병 치료" (약물명 영문 + 질환명 한국어)
"""
                    enhanced_system_prompt += page_format_prompt
                else:  # korean
                    page_format_prompt = """

## 📝 학술 연구 형식 (딥리서치 모드)

**당신은 학술 연구자입니다.** 다음 논문 구조와 Sequential Thinking 방법론을 따라주세요:

### 🧠 SEQUENTIAL THINKING 방법론 (필수):

**THINK STEP 1 - 데이터 수집:**
"[OpenTargets/DrugBank/ChEMBL/BioMCP/WebSearch]에서 [특정 쿼리]에 대한 데이터를 체계적으로 수집하겠습니다..."

**THINK STEP 2 - 데이터 통합:**
"여러 소스의 결과를 통합하면, OpenTargets는... DrugBank는... ChEMBL은... 그리고 최근 3-5년 리뷰 논문을 통한 웹 검색은 최신 동향을..."

**THINK STEP 3 - 분석:**
"통합된 데이터셋을 바탕으로 주요 패턴을 식별할 수 있습니다: [패턴 분석]. 경쟁 환경 분석 결과는..."

**THINK STEP 4 - 전략적 인사이트:**
"이러한 증거 기반을 바탕으로 전략적 시사점은... 권장사항은..."

### 학술 논문 구조 템플릿:
```markdown
# [연구 주제]: 딥리서치 분석 보고서

## 초록 (Abstract)
- 연구 목적, 방법론, 주요 발견, 결론 (150-200단어)
- 객관적이고 학술적인 톤
- 기여도 명확히 제시

## 1. 서론 (Introduction) 
- 배경 정보 및 맥락
- 연구 문제 정의
- 연구 목적과 가설
- 연구의 중요성

## 2. 문헌 검토 (Literature Review)
- 기존 연구의 현재 상태
- 주요 이론과 발견사항
- 연구 공백 식별
- 이론적 프레임워크

## 3. 연구 방법론 (Methodology)
- 연구 설계 및 접근법
- 데이터 수집 방법 (Database 소스 활용)
- Sequential Thinking 분석 절차
- 제한사항 및 제약조건

## 4. 결과 (Results)
### 4.1 OpenTargets 분석 결과
### 4.2 DrugBank 정보 분석
### 4.3 ChEMBL 바이오활성 데이터
### 4.4 BioMCP 통합 분석
### 4.5 Sequential Thinking 통합 분석
- 주요 발견사항 제시
- 데이터 해석
- 통계 분석 (해당시)
- 증거 기반 결론

## 5. 토론 (Discussion)
- 결과의 의미 및 시사점
- 기존 문헌과의 비교
- 제한사항 및 제약조건
- 향후 연구 방향

## 6. 결론 (Conclusion)
- 분야에 대한 핵심 기여도
- 실무적 시사점
- 주요 인사이트 요약
- 권장사항

## 참고문헌 (References)
[APA 인용 스타일 준수 - 아래 세부 규칙 적용]

## 💡 추천 후속 연구 질문

**다음 3가지 질문을 통해 연구를 확장해보세요:**

1. **심화 분석 질문**: "[주요 발견]에 대한 더 상세한 분자 메커니즘이나 작용 기전은 무엇인가요?"

2. **비교 연구 질문**: "[연구 주제]와 관련된 다른 치료법이나 접근 방식과 어떤 차이점이 있나요?"

3. **임상 적용 질문**: "이 연구 결과를 실제 임상 환경에서 어떻게 활용할 수 있을까요?"
```

### 🔗 Database 소스별 APA 인용 규칙 (실제 링크 포함 필수):

**OpenTargets 인용 (실제 링크로 표시):**
- 형식: OpenTargets Platform. (2024). [Target Name in English]. Retrieved from https://platform.opentargets.org/[타겟 정보]
- 예시: OpenTargets Platform. (2024). BRCA1. Retrieved from https://platform.opentargets.org/target/ENSG00000012048
- 실제 링크 예시: https://platform.opentargets.org/target/ENSG00000141510 (TP53), https://platform.opentargets.org/target/ENSG00000146648 (EGFR)
- **필수 ID 포함**: ENSG 번호, 질병 연관성 점수, 약물가능성 점수
- **중요**: 타겟명은 반드시 영문 그대로 사용 (예: BRCA1, TP53, EGFR, KRAS, PIK3CA)

**DrugBank 인용 (실제 링크로 표시):**
- 형식: DrugBank. (2024). [Drug Name in English] ([DB 번호]). Retrieved from https://www.drugbank.ca/drugs/[DB 번호]
- 예시: DrugBank. (2024). Aspirin (DB00945). Retrieved from https://www.drugbank.ca/drugs/DB00945
- 실제 링크 예시: https://www.drugbank.ca/drugs/DB00001 (Lepirudin), https://www.drugbank.ca/drugs/DB00002 (Cetuximab)
- **필수 ID 포함**: DB 번호, ATC 코드, 작용 기전, 승인 상태
- **중요**: 약물명은 반드시 영문 그대로 사용 (예: Aspirin, Cetuximab, Bevacizumab, Pembrolizumab)

**ChEMBL 인용 (실제 링크로 표시):**
- 형식: ChEMBL Database. (2024). [Compound Name in English] ([CHEMBL ID]). Retrieved from https://www.ebi.ac.uk/chembl/compound_report_card/[CHEMBL ID]
- 예시: ChEMBL Database. (2024). Aspirin (CHEMBL25). Retrieved from https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL25
- 실제 링크 예시: https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL1 (Lepirudin), https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL59 (Cetuximab)
- **필수 ID 포함**: ChEMBL ID, 분자량, IC50 값, 바이오활성 데이터
- **중요**: 화합물명은 반드시 영문 그대로 사용 (예: Imatinib, Gefitinib, Erlotinib, Osimertinib)

**BioMCP (PubMed) 인용 (실제 링크로 표시):**
- 형식: [Author]. ([Year]). [Title]. [Journal], [Volume(Issue)], [Pages]. PMID: [PMID]. Retrieved from https://pubmed.ncbi.nlm.nih.gov/[PMID]/
- 예시: Smith, J. et al. (2024). Cancer drug discovery. Nature, 610(7931), 123-130. PMID: 12345678. Retrieved from https://pubmed.ncbi.nlm.nih.gov/12345678/
- 실제 링크 예시: https://pubmed.ncbi.nlm.nih.gov/38395897/ (Drug Discovery), https://pubmed.ncbi.nlm.nih.gov/38123456/ (Cancer Research)
- **필수 ID 포함**: PMID, DOI, 저널 Impact Factor, 인용 횟수

**Web Search 인용 (실제 링크로 표시):**
- 형식: [Website Name]. (2024). [Page Title]. Retrieved from [Full URL]
- 예시: Reuters. (2024). Drug development breakthrough reported. Retrieved from https://www.reuters.com/healthcare/pharma/...
- 실제 링크 예시: https://www.nature.com/articles/... (Nature), https://www.science.org/... (Science)
- **필수 정보 포함**: 웹사이트명, 발행일, 페이지 제목, 완전한 URL

**ClinicalTrials.gov 인용 (실제 링크로 표시):**
- 형식: ClinicalTrials.gov. (2024). [임상시험 제목]. Identifier: [NCT 번호]. Retrieved from https://clinicaltrials.gov/study/[NCT 번호]
- 예시: ClinicalTrials.gov. (2024). Phase III Trial of Drug X. Identifier: NCT12345678. Retrieved from https://clinicaltrials.gov/study/NCT12345678
- 실제 링크 예시: https://clinicaltrials.gov/study/NCT00000102 (HIV Drug Study), https://clinicaltrials.gov/study/NCT00000161 (Cancer Trial)
- **필수 ID 포함**: NCT 번호, Phase, 연구 상태, 주요 결과, 등록 환자 수

### 📊 학술 작성 강화 기준:

**톤과 스타일:**
- 객관적이고 학술적인 톤, 증거 기반 논증
- 비판적 분석 접근, 중립적이고 균형잡힌 관점
- Sequential Thinking 과정 명시적 표현

**인용 요구사항 (강화):**
- **APA 스타일 완전 준수** - 모든 Database 소스에 대해
- **본문 인용**: (Database, Year) 또는 Database (Year)
- **사이트별 ID 의무 포함**: DB번호, ENSG번호, ChEMBL ID, PMID, NCT번호 등
- **참고문헌 목록**: 알파벳 순 정렬, 완전한 서지 정보
- **모든 소스의 적절한 귀속** 및 접근 URL 포함

**연구 품질 기준:**
- 체계적이고 철저한 분석, 다각적 관점 고려
- Sequential Thinking 방법론적 엄격성 
- 명확한 논리적 진행, 증거 기반 결론
- **최대한 많은 내용 포함**: 각 Database 소스에서 가능한 모든 관련 데이터 활용

**필수 포함 요소:**
- 각 약물의 DrugBank ID (DB00XXX) - 약물명은 영문 그대로
- 각 타겟의 OpenTargets Gene ID (ENSGXXXXXXXX) - 타겟명은 영문 그대로
- 각 화합물의 ChEMBL ID (CHEMBLXXX) - 화합물명은 영문 그대로
- 임상시험의 NCT 번호
- 논문의 PMID 번호
- 웹 검색 결과의 완전한 URL
- Sequential Thinking 과정의 명시적 서술

**🔤 전문 용어 사용 규칙 (필수 준수):**

**영문 그대로 사용해야 하는 용어들:**
- **약물명**: Aspirin (❌ 아스피린), Pembrolizumab (❌ 펨브롤리주맙), Bevacizumab (❌ 베바시주맙), Cetuximab (❌ 세툭시맙), Trastuzumab (❌ 트라스투주맙)
- **타겟/유전자명**: EGFR (❌ 표피성장인자수용체), BRCA1 (❌ 브르카1), TP53 (❌ p53), KRAS (❌ 케이라스), PIK3CA (❌ 파이케이쓰리시에이), BRAF (❌ 브라프), ALK (❌ 에이엘케이)
- **단백질명**: PD-1 (❌ 피디원), PD-L1 (❌ 피디엘원), VEGF (❌ 베지에프), HER2 (❌ 허투), CTLA-4 (❌ 시티엘에이포)
- **화합물명**: Imatinib (❌ 이마티닙), Gefitinib (❌ 게피티닙), Erlotinib (❌ 엘로티닙), Osimertinib (❌ 오시머티닙), Afatinib (❌ 아파티닙)
- **효소명**: COX-1, COX-2 (❌ 콕스원, 콕스투), PARP (❌ 파프), CDK4/6 (❌ 시디케이포/식스)

**한국어 사용 가능한 용어들:**
- **일반적인 질환명**: 유방암, 폐암, 당뇨병, 고혈압, 심장병, 간염, 신장병
- **일반적인 기전**: 혈관신생억제, 면역관문억제, 세포사멸유도, 신호전달차단
- **임상시험 단계**: 1상, 2상, 3상 임상시험
- **투여경로**: 정맥주사, 경구투여, 피하주사
- **부작용**: 오심, 구토, 설사, 피로감, 발진

**혼합 사용 예시 (권장):**
- "EGFR 표적 항암제" (타겟명 영문 + 설명 한국어)
- "Pembrolizumab의 면역관문억제 효과" (약물명 영문 + 기전 한국어)
- "BRCA1 유전자 변이와 유방암의 연관성" (유전자명 영문 + 질환명 한국어)
- "Imatinib을 이용한 만성골수성백혈병 치료" (약물명 영문 + 질환명 한국어)
"""
                    enhanced_system_prompt += page_format_prompt
            
            if deep_search_context:
                #                
                references_section = self._extract_references_from_context(deep_search_context)
                
                enhanced_system_prompt += f"""

[Research] **   Deep Research MCP      :**
{deep_search_context}

**[Data] MCP          :**
1.   MCP                                  
2. DrugBank, OpenTargets, ChEMBL, BioMCP                        
3.             MCP               ( : "DrugBank           ...", "OpenTargets          ...")
4. Sequential Thinking                        
5.                                  

  MCP                                               ."""
            
            #       (                  )
            max_quality_retries = 3
            attempt = 0
            response = ""
            reference_pattern = re.compile(r"\[(?:\d+)\]")
            
            while attempt < max_quality_retries:
                response = await self.client.generate(
                    prompt=question,
                    system_prompt=enhanced_system_prompt,
                    temperature=self.config.temperature  #       
                )
                #      
                ref_count = len(reference_pattern.findall(response))
                if len(response) >= self.settings["min_response_length"] and ref_count >= self.settings["min_references"]:
                    break  #         
                attempt += 1
                if self.settings["debug_mode"]:
                    print(f"[   ]          -    {len(response)} /      {ref_count},     {attempt}")

            #    :          (          )
            if self.settings["debug_mode"]:
                print(f"[   ]      : {len(response)}  ")
                print(f"[   ]      : {response[:100]}...")

            #             
            if not response:
                response = "[              .          .]"

            #                   
            if deep_search_context and references_section:
                # Deep Research   : MCP              
                response = self._append_references_to_response(response, references_section)
            else:
                #      :            
                basic_references = self._generate_basic_references()
                response = self._append_references_to_response(response, basic_references)

            #          
            self.conversation_history.append({"question": question, "answer": response})

            #       (             /     )
            if self.settings["debug_mode"]:
                print("\n--- AI       ---")

            #          
            self.interface.display_response(response)

            if self.settings["debug_mode"]:
                print("--- AI       ---\n")

            #                    
            if self.interface and ask_to_save:
                try:
                    save_choice = await self.interface.ask_to_save()

                    #                     
                    if save_choice:
                        #             (         )
                        await self.save_research_result(question, response, {})
                except Exception as e:
                    if self.settings["debug_mode"]:
                        print(f"[   ]             : {e!s}")

            return response

        except Exception as e:
            #              (                   )
            import traceback
            error_msg = f"             : {e!s}"

            if self.settings["debug_mode"]:
                print(f"\n[        ]\n{traceback.format_exc()}")

            self.interface.display_error(error_msg)
            return error_msg
    
    async def generate_streaming_response(self, question: str) -> AsyncGenerator[str, None]:
        """
                       
        
        Args:
            question:       
            
        Yields:
            str:      
        """
        # 언어 감지
        detected_language = self.detect_language(question)
        
        # MCP Deep Search    (Deep Research      )
        deep_search_context = None
        if self.mcp_enabled and hasattr(self, 'current_mode') and self.current_mode == "deep_research":
            deep_search_context = await self.deep_search_with_database(question)
        
        try:
            # Deep Search                      
            enhanced_system_prompt = self.system_prompt
            
            # 언어별 기본 응답 지침 추가
            language_instruction = ""
            if detected_language == 'english':
                language_instruction = """
**IMPORTANT: The user's question is in English. Please respond in English throughout your entire response.**
- Use English for all explanations, descriptions, and analysis
- Technical terms (drug names, target names, gene names) should remain in their original English form
- Keep disease names, mechanisms, and general medical terms in English
- Maintain professional English academic writing style
"""
            else:  # korean
                language_instruction = """
**중요: 사용자의 질문이 한국어입니다. 전체 응답을 한국어로 작성해주세요.**
- 모든 설명, 기술, 분석을 한국어로 작성
- 전문 용어(약물명, 타겟명, 유전자명)는 영문 그대로 유지
- 질환명, 기전, 일반 의학 용어는 한국어 사용 가능
- 전문적인 한국어 학술 문체 유지
"""
            
            enhanced_system_prompt += language_instruction
            
            # 딥리서치 모드에서 page_format.md와 추가 포맷 가이드 적용
            if self.mcp_enabled and hasattr(self, 'current_mode') and self.current_mode == "deep_research":
                # 언어별 딥리서치 프롬프트 적용
                if detected_language == 'english':
                    page_format_prompt = """

## 📝 ACADEMIC RESEARCH FORMAT (Deep Research Mode)

**You are an academic researcher.** Please follow this paper structure and Sequential Thinking methodology:

### 🧠 SEQUENTIAL THINKING Methodology (Required):

**THINK STEP 1 - Data Collection:**
"I will systematically collect data from [OpenTargets/DrugBank/ChEMBL/BioMCP/WebSearch] for [specific query]..."

**THINK STEP 2 - Data Integration:**
"Integrating results from multiple sources, OpenTargets shows... while DrugBank indicates... and ChEMBL reveals... and web search through recent 3-5 year review papers presents latest trends..."

**THINK STEP 3 - Analysis:**
"Based on the integrated dataset, I can identify key patterns: [pattern analysis]. The competitive landscape analysis shows..."

**THINK STEP 4 - Strategic Insights:**
"Given this evidence base, the strategic implications are... The recommendations include..."

### 학술 논문 구조 템플릿:
```markdown
# [연구 주제]: 딥리서치 분석 보고서

## 초록 (Abstract)
- 연구 목적, 방법론, 주요 발견, 결론 (150-200단어)
- 객관적이고 학술적인 톤
- 기여도 명확히 제시

## 1. 서론 (Introduction) 
- 배경 정보 및 맥락
- 연구 문제 정의
- 연구 목적과 가설
- 연구의 중요성

## 2. 문헌 검토 (Literature Review)
- 기존 연구의 현재 상태
- 주요 이론과 발견사항
- 연구 공백 식별
- 이론적 프레임워크

## 3. 연구 방법론 (Methodology)
- 연구 설계 및 접근법
- 데이터 수집 방법 (Database 소스 활용)
- Sequential Thinking 분석 절차
- 제한사항 및 제약조건

## 4. 결과 (Results)
### 4.1 OpenTargets 분석 결과
### 4.2 DrugBank 정보 분석
### 4.3 ChEMBL 바이오활성 데이터
### 4.4 BioMCP 통합 분석
### 4.5 Sequential Thinking 통합 분석
- 주요 발견사항 제시
- 데이터 해석
- 통계 분석 (해당시)
- 증거 기반 결론

## 5. 토론 (Discussion)
- 결과의 의미 및 시사점
- 기존 문헌과의 비교
- 제한사항 및 제약조건
- 향후 연구 방향

## 6. 결론 (Conclusion)
- 분야에 대한 핵심 기여도
- 실무적 시사점
- 주요 인사이트 요약
- 권장사항

## 참고문헌 (References)
[APA 인용 스타일 준수 - 아래 세부 규칙 적용]

## 💡 추천 후속 연구 질문

**다음 3가지 질문을 통해 연구를 확장해보세요:**

1. **심화 분석 질문**: "[주요 발견]에 대한 더 상세한 분자 메커니즘이나 작용 기전은 무엇인가요?"

2. **비교 연구 질문**: "[연구 주제]와 관련된 다른 치료법이나 접근 방식과 어떤 차이점이 있나요?"

3. **임상 적용 질문**: "이 연구 결과를 실제 임상 환경에서 어떻게 활용할 수 있을까요?"
```

### 🔗 Database 소스별 APA 인용 규칙 (실제 링크 포함 필수):

**OpenTargets 인용 (실제 링크로 표시):**
- 형식: OpenTargets Platform. (2024). [Target Name in English]. Retrieved from https://platform.opentargets.org/[타겟 정보]
- 예시: OpenTargets Platform. (2024). BRCA1. Retrieved from https://platform.opentargets.org/target/ENSG00000012048
- 실제 링크 예시: https://platform.opentargets.org/target/ENSG00000141510 (TP53), https://platform.opentargets.org/target/ENSG00000146648 (EGFR)
- **필수 ID 포함**: ENSG 번호, 질병 연관성 점수, 약물가능성 점수
- **중요**: 타겟명은 반드시 영문 그대로 사용 (예: BRCA1, TP53, EGFR, KRAS, PIK3CA)

**DrugBank 인용 (실제 링크로 표시):**
- 형식: DrugBank. (2024). [Drug Name in English] ([DB 번호]). Retrieved from https://www.drugbank.ca/drugs/[DB 번호]
- 예시: DrugBank. (2024). Aspirin (DB00945). Retrieved from https://www.drugbank.ca/drugs/DB00945
- 실제 링크 예시: https://www.drugbank.ca/drugs/DB00001 (Lepirudin), https://www.drugbank.ca/drugs/DB00002 (Cetuximab)
- **필수 ID 포함**: DB 번호, ATC 코드, 작용 기전, 승인 상태
- **중요**: 약물명은 반드시 영문 그대로 사용 (예: Aspirin, Cetuximab, Bevacizumab, Pembrolizumab)

**ChEMBL 인용 (실제 링크로 표시):**
- 형식: ChEMBL Database. (2024). [Compound Name in English] ([CHEMBL ID]). Retrieved from https://www.ebi.ac.uk/chembl/compound_report_card/[CHEMBL ID]
- 예시: ChEMBL Database. (2024). Aspirin (CHEMBL25). Retrieved from https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL25
- 실제 링크 예시: https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL1 (Lepirudin), https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL59 (Cetuximab)
- **필수 ID 포함**: ChEMBL ID, 분자량, IC50 값, 바이오활성 데이터
- **중요**: 화합물명은 반드시 영문 그대로 사용 (예: Imatinib, Gefitinib, Erlotinib, Osimertinib)

**BioMCP (PubMed) 인용 (실제 링크로 표시):**
- 형식: [Author]. ([Year]). [Title]. [Journal], [Volume(Issue)], [Pages]. PMID: [PMID]. Retrieved from https://pubmed.ncbi.nlm.nih.gov/[PMID]/
- 예시: Smith, J. et al. (2024). Cancer drug discovery. Nature, 610(7931), 123-130. PMID: 12345678. Retrieved from https://pubmed.ncbi.nlm.nih.gov/12345678/
- 실제 링크 예시: https://pubmed.ncbi.nlm.nih.gov/38395897/ (Drug Discovery), https://pubmed.ncbi.nlm.nih.gov/38123456/ (Cancer Research)
- **필수 ID 포함**: PMID, DOI, 저널 Impact Factor, 인용 횟수

**Web Search 인용 (실제 링크로 표시):**
- 형식: [Website Name]. (2024). [Page Title]. Retrieved from [Full URL]
- 예시: Reuters. (2024). Drug development breakthrough reported. Retrieved from https://www.reuters.com/healthcare/pharma/...
- 실제 링크 예시: https://www.nature.com/articles/... (Nature), https://www.science.org/... (Science)
- **필수 정보 포함**: 웹사이트명, 발행일, 페이지 제목, 완전한 URL

**ClinicalTrials.gov 인용 (실제 링크로 표시):**
- 형식: ClinicalTrials.gov. (2024). [임상시험 제목]. Identifier: [NCT 번호]. Retrieved from https://clinicaltrials.gov/study/[NCT 번호]
- 예시: ClinicalTrials.gov. (2024). Phase III Trial of Drug X. Identifier: NCT12345678. Retrieved from https://clinicaltrials.gov/study/NCT12345678
- 실제 링크 예시: https://clinicaltrials.gov/study/NCT00000102 (HIV Drug Study), https://clinicaltrials.gov/study/NCT00000161 (Cancer Trial)
- **필수 ID 포함**: NCT 번호, Phase, 연구 상태, 주요 결과, 등록 환자 수

### 📊 학술 작성 강화 기준:

**톤과 스타일:**
- 객관적이고 학술적인 톤, 증거 기반 논증
- 비판적 분석 접근, 중립적이고 균형잡힌 관점
- Sequential Thinking 과정 명시적 표현

**인용 요구사항 (강화):**
- **APA 스타일 완전 준수** - 모든 Database 소스에 대해
- **본문 인용**: (Database, Year) 또는 Database (Year)
- **사이트별 ID 의무 포함**: DB번호, ENSG번호, ChEMBL ID, PMID, NCT번호 등
- **참고문헌 목록**: 알파벳 순 정렬, 완전한 서지 정보
- **모든 소스의 적절한 귀속** 및 접근 URL 포함

**연구 품질 기준:**
- 체계적이고 철저한 분석, 다각적 관점 고려
- Sequential Thinking 방법론적 엄격성 
- 명확한 논리적 진행, 증거 기반 결론
- **최대한 많은 내용 포함**: 각 Database 소스에서 가능한 모든 관련 데이터 활용

**필수 포함 요소:**
- 각 약물의 DrugBank ID (DB00XXX) - 약물명은 영문 그대로
- 각 타겟의 OpenTargets Gene ID (ENSGXXXXXXXX) - 타겟명은 영문 그대로
- 각 화합물의 ChEMBL ID (CHEMBLXXX) - 화합물명은 영문 그대로
- 임상시험의 NCT 번호
- 논문의 PMID 번호
- 웹 검색 결과의 완전한 URL
- Sequential Thinking 과정의 명시적 서술

**🔤 전문 용어 사용 규칙 (필수 준수):**

**영문 그대로 사용해야 하는 용어들:**
- **약물명**: Aspirin (❌ 아스피린), Pembrolizumab (❌ 펨브롤리주맙), Bevacizumab (❌ 베바시주맙), Cetuximab (❌ 세툭시맙), Trastuzumab (❌ 트라스투주맙)
- **타겟/유전자명**: EGFR (❌ 표피성장인자수용체), BRCA1 (❌ 브르카1), TP53 (❌ p53), KRAS (❌ 케이라스), PIK3CA (❌ 파이케이쓰리시에이), BRAF (❌ 브라프), ALK (❌ 에이엘케이)
- **단백질명**: PD-1 (❌ 피디원), PD-L1 (❌ 피디엘원), VEGF (❌ 베지에프), HER2 (❌ 허투), CTLA-4 (❌ 시티엘에이포)
- **화합물명**: Imatinib (❌ 이마티닙), Gefitinib (❌ 게피티닙), Erlotinib (❌ 엘로티닙), Osimertinib (❌ 오시머티닙), Afatinib (❌ 아파티닙)
- **효소명**: COX-1, COX-2 (❌ 콕스원, 콕스투), PARP (❌ 파프), CDK4/6 (❌ 시디케이포/식스)

**한국어 사용 가능한 용어들:**
- **일반적인 질환명**: 유방암, 폐암, 당뇨병, 고혈압, 심장병, 간염, 신장병
- **일반적인 기전**: 혈관신생억제, 면역관문억제, 세포사멸유도, 신호전달차단
- **임상시험 단계**: 1상, 2상, 3상 임상시험
- **투여경로**: 정맥주사, 경구투여, 피하주사
- **부작용**: 오심, 구토, 설사, 피로감, 발진

**혼합 사용 예시 (권장):**
- "EGFR 표적 항암제" (타겟명 영문 + 설명 한국어)
- "Pembrolizumab의 면역관문억제 효과" (약물명 영문 + 기전 한국어)
- "BRCA1 유전자 변이와 유방암의 연관성" (유전자명 영문 + 질환명 한국어)
- "Imatinib을 이용한 만성골수성백혈병 치료" (약물명 영문 + 질환명 한국어)
- 연구 수행 시간 (YYYY-MM-DD HH:MM 포맷)
- 응답 마지막에 3가지 추천 후속 질문 포함
"""
                
                else:  # korean
                    page_format_prompt = """

## 📝 ACADEMIC RESEARCH FORMAT (딥리서치 모드 전용)

**당신은 학술 연구자입니다.** 다음 논문 구조와 Sequential Thinking 방법론을 반드시 따라주세요:

### 🧠 SEQUENTIAL THINKING 방법론 (필수 적용):

**THINK STEP 1 - 데이터 수집:**
"[OpenTargets/DrugBank/ChEMBL/BioMCP/WebSearch]에서 [특정 쿼리]에 대한 체계적 데이터 수집을 시행합니다..."

**THINK STEP 2 - 데이터 통합:**
"여러 소스의 결과를 통합하면, OpenTargets는 ...를 보여주고, DrugBank는 ...를 나타내며, ChEMBL은 ...를 밝혀주고, 웹 검색을 통해 최신 동향은 ...를 제시합니다..."

**THINK STEP 3 - 분석:**
"통합된 데이터셋을 바탕으로 주요 패턴을 식별합니다: [패턴 분석]. 경쟁 환경 분석 결과..."

**THINK STEP 4 - 전략적 인사이트:**
"이 증거 기반을 토대로 전략적 시사점은... 권고사항은..."

### 학술 논문 구조 템플릿:
```markdown
# [연구 주제]: 딥리서치 분석 보고서

## 초록 (Abstract)
- 연구 목적, 방법론, 주요 발견, 결론 (150-200단어)
- 객관적이고 학술적인 톤
- 기여도 명확히 제시

## 1. 서론 (Introduction) 
- 배경 정보 및 맥락
- 연구 문제 정의
- 연구 목적과 가설
- 연구의 중요성

## 2. 문헌 검토 (Literature Review)
- 기존 연구의 현재 상태
- 주요 이론과 발견사항
- 연구 공백 식별
- 이론적 프레임워크

## 3. 연구 방법론 (Methodology)
- 연구 설계 및 접근법
- 데이터 수집 방법 (Database 소스 활용)
- Sequential Thinking 분석 절차
- 제한사항 및 제약조건

## 4. 결과 (Results)
### 4.1 OpenTargets 분석 결과
### 4.2 DrugBank 정보 분석
### 4.3 ChEMBL 바이오활성 데이터
### 4.4 BioMCP 통합 분석
### 4.5 Sequential Thinking 통합 분석
- 주요 발견사항 제시
- 데이터 해석
- 통계 분석 (해당시)
- 증거 기반 결론

## 5. 토론 (Discussion)
- 결과의 의미 및 시사점
- 기존 문헌과의 비교
- 제한사항 및 제약조건
- 향후 연구 방향

## 6. 결론 (Conclusion)
- 분야에 대한 핵심 기여도
- 실무적 시사점
- 주요 인사이트 요약
- 권장사항

## 참고문헌 (References)
[APA 인용 스타일 준수 - 아래 세부 규칙 적용]

## 💡 추천 후속 연구 질문

**다음 3가지 질문을 통해 연구를 확장해보세요:**

1. **심화 분석 질문**: "[주요 발견]에 대한 더 상세한 분자 메커니즘이나 작용 기전은 무엇인가요?"

2. **비교 연구 질문**: "[연구 주제]와 관련된 다른 치료법이나 접근 방식과 어떤 차이점이 있나요?"

3. **임상 적용 질문**: "이 연구 결과를 실제 임상 환경에서 어떻게 활용할 수 있을까요?"
```

### 🔗 Database 소스별 APA 인용 규칙 (실제 링크 포함 필수):

**OpenTargets 인용 (실제 링크로 표시):**
- 형식: OpenTargets Platform. (2024). [Target Name in English]. Retrieved from https://platform.opentargets.org/[타겟 정보]
- 예시: OpenTargets Platform. (2024). BRCA1. Retrieved from https://platform.opentargets.org/target/ENSG00000012048
- 실제 링크 예시: https://platform.opentargets.org/target/ENSG00000141510 (TP53), https://platform.opentargets.org/target/ENSG00000146648 (EGFR)
- **필수 ID 포함**: ENSG 번호, 질병 연관성 점수, 약물가능성 점수
- **중요**: 타겟명은 반드시 영문 그대로 사용 (예: BRCA1, TP53, EGFR, KRAS, PIK3CA)

**DrugBank 인용 (실제 링크로 표시):**
- 형식: DrugBank. (2024). [Drug Name in English] ([DB 번호]). Retrieved from https://www.drugbank.ca/drugs/[DB 번호]
- 예시: DrugBank. (2024). Aspirin (DB00945). Retrieved from https://www.drugbank.ca/drugs/DB00945
- 실제 링크 예시: https://www.drugbank.ca/drugs/DB00001 (Lepirudin), https://www.drugbank.ca/drugs/DB00002 (Cetuximab)
- **필수 ID 포함**: DB 번호, ATC 코드, 작용 기전, 승인 상태
- **중요**: 약물명은 반드시 영문 그대로 사용 (예: Aspirin, Cetuximab, Bevacizumab, Pembrolizumab)

**ChEMBL 인용 (실제 링크로 표시):**
- 형식: ChEMBL Database. (2024). [Compound Name in English] ([CHEMBL ID]). Retrieved from https://www.ebi.ac.uk/chembl/compound_report_card/[CHEMBL ID]
- 예시: ChEMBL Database. (2024). Aspirin (CHEMBL25). Retrieved from https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL25
- 실제 링크 예시: https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL1 (Lepirudin), https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL59 (Cetuximab)
- **필수 ID 포함**: ChEMBL ID, 분자량, IC50 값, 바이오활성 데이터
- **중요**: 화합물명은 반드시 영문 그대로 사용 (예: Imatinib, Gefitinib, Erlotinib, Osimertinib)

**BioMCP (PubMed) 인용 (실제 링크로 표시):**
- 형식: [Author]. ([Year]). [Title]. [Journal], [Volume(Issue)], [Pages]. PMID: [PMID]. Retrieved from https://pubmed.ncbi.nlm.nih.gov/[PMID]/
- 예시: Smith, J. et al. (2024). Cancer drug discovery. Nature, 610(7931), 123-130. PMID: 12345678. Retrieved from https://pubmed.ncbi.nlm.nih.gov/12345678/
- 실제 링크 예시: https://pubmed.ncbi.nlm.nih.gov/38395897/ (Drug Discovery), https://pubmed.ncbi.nlm.nih.gov/38123456/ (Cancer Research)
- **필수 ID 포함**: PMID, DOI, 저널 Impact Factor, 인용 횟수

**Web Search 인용 (실제 링크로 표시):**
- 형식: [Website Name]. (2024). [Page Title]. Retrieved from [Full URL]
- 예시: Reuters. (2024). Drug development breakthrough reported. Retrieved from https://www.reuters.com/healthcare/pharma/...
- 실제 링크 예시: https://www.nature.com/articles/... (Nature), https://www.science.org/... (Science)
- **필수 정보 포함**: 웹사이트명, 발행일, 페이지 제목, 완전한 URL

**ClinicalTrials.gov 인용 (실제 링크로 표시):**
- 형식: ClinicalTrials.gov. (2024). [임상시험 제목]. Identifier: [NCT 번호]. Retrieved from https://clinicaltrials.gov/study/[NCT 번호]
- 예시: ClinicalTrials.gov. (2024). Phase III Trial of Drug X. Identifier: NCT12345678. Retrieved from https://clinicaltrials.gov/study/NCT12345678
- 실제 링크 예시: https://clinicaltrials.gov/study/NCT00000102 (HIV Drug Study), https://clinicaltrials.gov/study/NCT00000161 (Cancer Trial)
- **필수 ID 포함**: NCT 번호, Phase, 연구 상태, 주요 결과, 등록 환자 수

### 📊 학술 작성 강화 기준:

**톤과 스타일:**
- 객관적이고 학술적인 톤, 증거 기반 논증
- 비판적 분석 접근, 중립적이고 균형잡힌 관점
- Sequential Thinking 과정 명시적 표현

**인용 요구사항 (강화):**
- **APA 스타일 완전 준수** - 모든 Database 소스에 대해
- **본문 인용**: (Database, Year) 또는 Database (Year)
- **사이트별 ID 의무 포함**: DB번호, ENSG번호, ChEMBL ID, PMID, NCT번호 등
- **참고문헌 목록**: 알파벳 순 정렬, 완전한 서지 정보
- **모든 소스의 적절한 귀속** 및 접근 URL 포함

**연구 품질 기준:**
- 체계적이고 철저한 분석, 다각적 관점 고려
- Sequential Thinking 방법론적 엄격성 
- 명확한 논리적 진행, 증거 기반 결론
- **최대한 많은 내용 포함**: 각 Database 소스에서 가능한 모든 관련 데이터 활용

**필수 포함 요소:**
- 각 약물의 DrugBank ID (DB00XXX) - 약물명은 영문 그대로
- 각 타겟의 OpenTargets Gene ID (ENSGXXXXXXXX) - 타겟명은 영문 그대로
- 각 화합물의 ChEMBL ID (CHEMBLXXX) - 화합물명은 영문 그대로
- 임상시험의 NCT 번호
- 논문의 PMID 번호
- 웹 검색 결과의 완전한 URL
- Sequential Thinking 과정의 명시적 서술

**🔤 전문 용어 사용 규칙 (필수 준수):**

**영문 그대로 사용해야 하는 용어들:**
- **약물명**: Aspirin (❌ 아스피린), Pembrolizumab (❌ 펨브롤리주맙), Bevacizumab (❌ 베바시주맙), Cetuximab (❌ 세툭시맙), Trastuzumab (❌ 트라스투주맙)
- **타겟/유전자명**: EGFR (❌ 표피성장인자수용체), BRCA1 (❌ 브르카1), TP53 (❌ p53), KRAS (❌ 케이라스), PIK3CA (❌ 파이케이쓰리시에이), BRAF (❌ 브라프), ALK (❌ 에이엘케이)
- **단백질명**: PD-1 (❌ 피디원), PD-L1 (❌ 피디엘원), VEGF (❌ 베지에프), HER2 (❌ 허투), CTLA-4 (❌ 시티엘에이포)
- **화합물명**: Imatinib (❌ 이마티닙), Gefitinib (❌ 게피티닙), Erlotinib (❌ 엘로티닙), Osimertinib (❌ 오시머티닙), Afatinib (❌ 아파티닙)
- **효소명**: COX-1, COX-2 (❌ 콕스원, 콕스투), PARP (❌ 파프), CDK4/6 (❌ 시디케이포/식스)

**한국어 사용 가능한 용어들:**
- **일반적인 질환명**: 유방암, 폐암, 당뇨병, 고혈압, 심장병, 간염, 신장병
- **일반적인 기전**: 혈관신생억제, 면역관문억제, 세포사멸유도, 신호전달차단
- **임상시험 단계**: 1상, 2상, 3상 임상시험
- **투여경로**: 정맥주사, 경구투여, 피하주사
- **부작용**: 오심, 구토, 설사, 피로감, 발진

**혼합 사용 예시 (권장):**
- "EGFR 표적 항암제" (타겟명 영문 + 설명 한국어)
- "Pembrolizumab의 면역관문억제 효과" (약물명 영문 + 기전 한국어)
- "BRCA1 유전자 변이와 유방암의 연관성" (유전자명 영문 + 질환명 한국어)
- "Imatinib을 이용한 만성골수성백혈병 치료" (약물명 영문 + 질환명 한국어)
"""
                
                # 추천 질문 관련 프롬프트 추가
                timestamp_prompt = f"""

### 🔄 Sequential Thinking with Web Search Integration

**THINK STEP 1 - 종합 데이터 수집:**
"OpenTargets/DrugBank/ChEMBL/BioMCP/Web Search에서 [특정 쿼리]에 대한 체계적 데이터 수집을 시행합니다..."

**THINK STEP 2 - 통합 데이터 분석:**
"여러 소스의 결과를 통합하면, OpenTargets는 ...를 보여주고, DrugBank는 ...를 나타내며, ChEMBL은 ...를 밝혀주고, 웹 검색(최근 3-5년 리뷰 논문)을 통해 최신 동향은 ...를 제시합니다..."

**THINK STEP 3 - 경쟁 환경 분석:**
"통합된 데이터셋을 바탕으로 주요 패턴을 식별합니다: [패턴 분석]. 경쟁 환경 분석 결과..."

**THINK STEP 4 - 전략적 인사이트:**
"이 증거 기반을 토대로 전략적 시사점은... 권고사항은..."

### 📝 필수 추천 후속 질문 (응답 마지막에 포함)

**모든 딥리서치 응답 마지막에 다음 3가지 전략적 후속 질문을 반드시 포함하세요:**

#### 💡 추천 후속 연구 질문

1. **경쟁 분석 심화**: "이 타겟/기전에 대한 경쟁사 파이프라인 분석을 더 자세히 진행하시겠습니까?"

2. **치료 전략 확장**: "해당 적응증에서의 combination therapy 전략이나 다른 치료 접근법을 탐색해보시겠습니까?"

3. **IP/특허 분석**: "이 기전이나 화합물에 대한 특허 landscape 분석이 필요하시겠습니까?"

**참고**: 각 질문은 사용자의 연구 주제와 맥락에 맞게 구체적으로 조정하여 제시하세요.
"""
                
                # page_format_prompt += timestamp_prompt  # 시간 정보 제거됨
                enhanced_system_prompt += page_format_prompt
            
            if deep_search_context:
                enhanced_system_prompt += f"""

[Research] **딥리서치 Database 검색 결과:**
{deep_search_context}

**[Data] Database 소스 활용 지침:**
1. 모든 Database 소스 (Web Search 포함)를 체계적으로 활용하세요
2. DrugBank, OpenTargets, ChEMBL, BioMCP, Web Search 결과를 통합 분석하세요
3. 각 소스별 데이터를 명시적으로 인용하세요 (예: "DrugBank 데이터에 따르면...", "OpenTargets 분석 결과...")
4. Sequential Thinking 방법론을 단계별로 적용하세요
5. 시간 정보 표시는 제거되었습니다
6. 웹 검색 결과는 최근 3-5년 리뷰 논문에 집중하세요
7. 응답 마지막에 반드시 3가지 추천 후속 질문을 포함하세요

위 Database 정보를 활용하여 종합적이고 상세한 연구 분석 보고서를 작성해주세요."""
            
            #            (OllamaClient                  )
            #                         
            if hasattr(self.client, 'generate_stream'):
                async for chunk in self.client.generate_stream(
                    prompt=question,
                    system_prompt=enhanced_system_prompt,
                    temperature=self.settings.get("temperature", 0.7)
                ):
                    yield chunk
            else:
                #                                
                response = await self.client.generate(
                    prompt=question,
                    system_prompt=enhanced_system_prompt,
                    temperature=self.settings.get("temperature", 0.7)
                )
                #                   (       )
                chunk_size = 50  #             
                for i in range(0, len(response), chunk_size):
                    yield response[i:i + chunk_size]
                    await asyncio.sleep(0.01)  #          
                    
        except Exception as e:
            import traceback
            error_msg = f"  :                   : {e!s}"
            if self.settings.get("debug_mode", False):
                tb = traceback.format_exc()
                yield f"  :      : {tb}"
            yield error_msg
            return

    def _extract_references_from_context(self, deep_search_context: str) -> str:
        """Deep Search                       """
        if not deep_search_context:
            return ""
        
        references = []
        databases_used = set()
        
        try:
            #              
            if "DrugBank" in deep_search_context:
                databases_used.add("DrugBank")
            if "OpenTargets" in deep_search_context:
                databases_used.add("OpenTargets")
            if "ChEMBL" in deep_search_context:
                databases_used.add("ChEMBL")
            if "BioMCP" in deep_search_context or "PubMed" in deep_search_context:
                databases_used.add("BioMCP/PubMed")
            if "BioRxiv" in deep_search_context:
                databases_used.add("BioRxiv")
            if "ClinicalTrials" in deep_search_context:
                databases_used.add("ClinicalTrials.gov")
            if "Sequential Thinking" in deep_search_context:
                databases_used.add("Sequential Thinking AI")
            
            # DOI  PMID      
            import re
            
            # DOI    ( : doi:10.1000/xyz123    https://doi.org/10.1000/xyz123)
            doi_pattern = r'(?:doi:|https://doi\.org/)([0-9]+\.[0-9]+/[^\s]+)'
            dois = re.findall(doi_pattern, deep_search_context, re.IGNORECASE)
            
            # PMID    ( : PMID: 12345678)
            pmid_pattern = r'PMID:\s*([0-9]+)'
            pmids = re.findall(pmid_pattern, deep_search_context, re.IGNORECASE)
            
            # ChEMBL ID    ( : CHEMBL123456)
            chembl_pattern = r'CHEMBL[0-9]+'
            chembls = re.findall(chembl_pattern, deep_search_context, re.IGNORECASE)
            
            # DrugBank ID    ( : DB00001)
            drugbank_pattern = r'DB[0-9]+'
            drugbanks = re.findall(drugbank_pattern, deep_search_context, re.IGNORECASE)
            
            #        
            ref_count = 1
            
            #             
            for db in sorted(databases_used):
                if db == "DrugBank":
                    references.append(f"[{ref_count}] DrugBank Database. Available at: https://go.drugbank.com/")
                elif db == "OpenTargets":
                    references.append(f"[{ref_count}] Open Targets Platform. Available at: https://www.opentargets.org/")
                elif db == "ChEMBL":
                    references.append(f"[{ref_count}] ChEMBL Database. Available at: https://www.ebi.ac.uk/chembl/")
                elif db == "BioMCP/PubMed":
                    references.append(f"[{ref_count}] PubMed Database via BioMCP. Available at: https://pubmed.ncbi.nlm.nih.gov/")
                elif db == "BioRxiv":
                    references.append(f"[{ref_count}] bioRxiv Preprint Server. Available at: https://www.biorxiv.org/")
                elif db == "ClinicalTrials.gov":
                    references.append(f"[{ref_count}] ClinicalTrials.gov Database. Available at: https://clinicaltrials.gov/")
                elif db == "Sequential Thinking AI":
                    references.append(f"[{ref_count}] Sequential Thinking AI Analysis (MCP-based research planning)")
                ref_count += 1
            
            # DOI      
            for doi in set(dois):
                references.append(f"[{ref_count}] DOI: {doi}. Available at: https://doi.org/{doi}")
                ref_count += 1
            
            # PMID      
            for pmid in set(pmids):
                references.append(f"[{ref_count}] PubMed ID: {pmid}. Available at: https://pubmed.ncbi.nlm.nih.gov/{pmid}/")
                ref_count += 1
            
            # ChEMBL ID   
            for chembl in set(chembls):
                references.append(f"[{ref_count}] ChEMBL ID: {chembl}. Available at: https://www.ebi.ac.uk/chembl/compound_report_card/{chembl}/")
                ref_count += 1
            
            # DrugBank ID   
            for drugbank in set(drugbanks):
                references.append(f"[{ref_count}] DrugBank ID: {drugbank}. Available at: https://go.drugbank.com/drugs/{drugbank}")
                ref_count += 1
            
        except Exception as e:
            if self.settings.get("debug_mode", False):
                print(f"[   ]             : {e}")
        
        return references

    def _generate_basic_references(self) -> list:
        """              """
        basic_references = [
            "  **GAIA-BT AI System** -              ",
            "  **            ** - FDA, EMA, PMDA      ",
            "  **           ** - ClinicalTrials.gov",
            "  **     ** - PubMed,               ",
            "  **        ** - ICH      , GMP   ",
        ]
        return basic_references

    def _append_references_to_response(self, response: str, references: list) -> str:
        """              """
        if not references:
            return response
            
        references_text = "\n\n###       \n"
        for i, ref in enumerate(references, 1):
            references_text += f"{i}. {ref}\n"
        
        return response + references_text
    
    #         generate_response            

    async def process_command(self, command: str) -> bool:
        """
                  

        Args:
            command:        

        Returns:
            bool:         
        """
        try:
            #           
            parts = command.split(None, 1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            #       
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
                    self.interface.display_error("/feedback                .  : /feedback                   ?")
                else:
                    await self.run_feedback_loop(args)

            elif cmd == "/model":
                if not args:
                    self.interface.display_error("/model                 .          : " + ", ".join(AVAILABLE_MODELS))
                else:
                    await self.change_model(args)

            elif cmd == "/debug":
                #          
                self.settings["debug_mode"] = not self.settings["debug_mode"]
                # OllamaClient                 
                self.client.set_debug_mode(self.settings["debug_mode"])
                state = "  " if self.settings["debug_mode"] else "  "
                self.interface.console.print(f"[green]        {state}          .[/green]")

            elif cmd == "/prompt":
                #           
                await self.change_prompt(args)

            elif cmd == "/mcp":
                # MCP        (      )
                if self.settings.get("debug_mode", False):
                    self.interface.console.print(f"[cyan][   ] MCP       : {args}[/cyan]")
                if self.mcp_commands:
                    await self.mcp_commands.handle_mcp_command(args)
                else:
                    self.interface.display_error("MCP               . MCP           .")

            else:
                self.interface.display_error(f"          : {cmd}.          /help       .")
            return True

        except Exception as e:
            self.interface.display_error(f"              : {e!s}")
            return True  #              

    async def save_research_result(self, question: str, response: str, rating_info: Optional[dict] = None) -> None:
        """
                     

        Args:
            question:       
            response:       
            rating_info:           (    )
        """
        try:
            import datetime
            import json
            from pathlib import Path

            from app.utils.config import OUTPUT_DIR

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            #             (    )
            title_words = question.split()[:5]  #    5        
            title = "_".join([w for w in title_words if w]).replace("/", "").replace("\\", "").replace("?", "").replace("!", "")
            if not title:  #             
                title = "research_result"

            #         
            output_dir = Path(OUTPUT_DIR) / timestamp
            output_dir.mkdir(parents=True, exist_ok=True)

            #         
            output_file = output_dir / f"{timestamp}_{title}.md"

            #            
            meta_file = output_dir / f"{timestamp}_{title}_meta.json"

            #           
            with open(output_file, "w", encoding="utf-8") as f:
                #      
                f.write(f"#        : {question}\n\n")

                #          
                f.write(response)

            #         
            metadata = {
                "timestamp": timestamp,
                "question": question,
                "settings": self.settings,
                "model": self.client.model,
                "feedback_loop": {
                    "depth": self.settings["feedback_depth"],
                    "width": self.settings["feedback_width"]
                }
            }

            #          (     )
            if rating_info:
                metadata["user_rating"] = rating_info

            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            #         
            if self.interface:
                self.interface.display_saved_notification(str(output_file))

            if self.settings["debug_mode"]:
                print(f"[   ]         : {output_file}")

        except Exception as e:
            #                            
            if self.settings["debug_mode"]:
                import traceback
                print(f"[   ]              : {e!s}")
                print(traceback.format_exc())
            self.interface.display_error(f"             : {e!s}")

    async def change_model(self, model_name: str) -> None:
        """
                    .

        -         :              
        -                 

        Args:
            model_name:            
        """
        #        (     :latest       )
        model_name = model_name.strip()
        if ":latest" not in model_name:
            model_name = f"{model_name}:latest"

        try:
            # 1.             
            model_check = await self.client.check_model_availability(model_name)
            if not model_check["available"]:
                self.interface.display_error(
                    f"   '{model_name}' ( )           . \n"
                    f"  : {model_check.get('message', '         ')}"
                )
                return

            # 2.                    
            prev_model = self.client.model
            adapter_name = model_check.get('adapter', 'Unknown')

            # 3.            (               )
            if prev_model != model_name:
                # HTTP         
                await self.client.close()

                # OllamaClient       
                self.client = OllamaClient(
                    model=model_name,
                    temperature=float(self.settings.get("temperature", 0.7)),
                    max_tokens=int(self.settings.get("max_tokens", 4000)),
                    min_response_length=int(self.settings.get("min_response_length", 500)),
                )
            else:
                #                     
                self.client.update_model(model_name)

            # 4.        
            self.settings["model"] = model_name

            # 5.             
            self.interface.console.print(
                f"[bold green]    '{model_name}'        .[/bold green]\n"
                f"[blue]   : {adapter_name}[/blue]"
            )
        except Exception as e:
            self.interface.display_error(f"             : {e!s}")
            #                  
            import traceback
            self.interface.console.print(f"[dim]{traceback.format_exc()}[/dim]", highlight=False)

    async def change_prompt(self, prompt_type: str = None) -> None:
        """
                       .
        
        Args:
            prompt_type:         (None        )
        """
        try:
            #                          
            if not prompt_type:
                choices = self.prompt_manager.get_prompt_choices()
                
                from rich.table import Table
                table = Table(title="[Target]               ")
                table.add_column("  ", style="cyan", no_wrap=True)
                table.add_column("  ", style="green")
                table.add_column("  ", style="yellow")
                
                for name, description in choices.items():
                    current = "O" if name == self.current_prompt_type else ""
                    table.add_row(name, description, current)
                
                self.interface.console.print(table)
                self.interface.console.print(f"\n[yellow][Tip]    : /prompt <   >[/yellow]")
                self.interface.console.print(f"[dim]  : /prompt clinical, /prompt chemistry[/dim]")
                return
            
            #           
            prompt_type = prompt_type.strip().lower()
            
            #              
            new_prompt = self.prompt_manager.get_prompt(prompt_type)
            if new_prompt is None:
                available = list(self.prompt_manager.get_prompt_choices().keys())
                self.interface.display_error(
                    f"        '{prompt_type}' ( )          .\n"
                    f"         : {', '.join(available)}"
                )
                return
            
            #        
            old_prompt_type = self.current_prompt_type
            self.current_prompt_type = prompt_type
            self.system_prompt = new_prompt
            
            #             
            template = self.prompt_manager.get_prompt_template(prompt_type)
            description = template.description if template else f"{prompt_type}   "
            
            #             
            self.interface.console.print(
                f"[bold green]         '{prompt_type}'        .[/bold green]\n"
                f"[blue]  : {description}[/blue]\n"
                f"[dim]     : {old_prompt_type}[/dim]"
            )
            
        except Exception as e:
            self.interface.display_error(f"               : {e}")
            if self.settings.get("debug_mode", False):
                import traceback
                self.interface.console.print(f"[dim]{traceback.format_exc()}[/dim]", highlight=False)

    async def update_settings(self, args_str: str) -> None:
        """
                 

        Args:
            args_str:          
        """
        try:
            #           (  : key=value)
            parts = args_str.split()
            updates = {}

            for part in parts:
                if "=" in part:
                    key, value = part.split("=", 1)
                    key = key.strip()

                    if key in self.settings:
                        #           
                        if key in ["feedback_depth", "feedback_width", "min_response_length", "min_references"]:
                            updates[key] = int(value)
                        else:
                            updates[key] = value
                    else:
                        self.interface.display_error(f"         : {key}")

            #       
            if "feedback_depth" in updates and (updates["feedback_depth"] < 1 or updates["feedback_depth"] > 10):
                self.interface.display_error("        1   10             ")
                del updates["feedback_depth"]

            if "feedback_width" in updates and (updates["feedback_width"] < 1 or updates["feedback_width"] > 10):
                self.interface.display_error("        1   10             ")
                del updates["feedback_width"]

            #           
            if updates:
                self.settings.update(updates)
                self.interface.display_settings(self.settings)

        except ValueError as e:
            self.interface.display_error(f"        : {e!s}")
        except Exception as e:
            self.interface.display_error(f"         : {e!s}")

    async def run_feedback_loop(self, question: str) -> None:
        """
                                   

        Args:
            question:       
        """
        depth = self.settings["feedback_depth"]
        width = self.settings["feedback_width"]

        self.interface.display_feedback_progress(0, depth, "         ...")

        #          (           )
        best_response = await self.generate_response(question, ask_to_save=False)

        #          
        for i in range(depth):
            self.interface.display_feedback_progress(i + 1, depth, f"{i + 1}  :           ...")

            #       
            with self.interface.display_thinking():
                try:
                    #          (                         )
                    feedback_prompt = f"""
                           :

  : {question}

     :
{best_response}

   :
1.           (          )
2.                    
3.            (   2    )
4.           

                               .
"""

                    #                  
                    prompts = []
                    for j in range(width):
                        prompts.append({
                            "prompt": feedback_prompt,
                            "system": self.system_prompt,
                            "temperature": 0.5 + (j * 0.2)  #                 
                        })

                    #         
                    alternatives = await self.client.generate_parallel(prompts)

                    #             (         -   ,            )
                    best_score = -1
                    for response in alternatives:
                        if isinstance(response, Exception):
                            continue

                        #       (        )
                        score = len(response)  #       
                        refs_count = response.lower().count("http")  #             
                        score += refs_count * 200  #             

                        if score > best_score:
                            best_response = response
                            best_score = score

                except Exception as e:
                    self.interface.display_error(f"         : {e!s}")
                    break

        #         
        self.interface.display_response(best_response, show_references=True)

        #                  
        save_choice = await self.interface.ask_to_save()

        #                     
        if save_choice:
            #             (         )
            await self.save_research_result(question, best_response, {})

    async def switch_to_deep_research_mode(self):
        """Deep Research        (MCP         )"""
        if self.current_mode != "deep_research":
            self.current_mode = "deep_research"
            self.mode_banner_shown = False  #            
            self._show_mode_banner()
            
            # MCP         
            if hasattr(self, 'mcp_commands') and self.mcp_commands:
                try:
                    print("  MCP                ...")
                    await self.mcp_commands.start_mcp()
                except Exception as e:
                    print(f"[Warning] MCP            : {e}")
                    print("[Tip]      '/mcp start'            .")

    async def switch_to_normal_mode(self):
        """          (MCP         )"""
        if self.current_mode != "normal":
            # MCP          (           )
            if hasattr(self, 'mcp_commands') and self.mcp_commands and self.mcp_enabled:
                try:
                    print("  MCP                ...")
                    await self.mcp_commands.stop_mcp()
                except Exception as e:
                    print(f"[Warning] MCP            : {e}")
            
            self.current_mode = "normal"
            self.mode_banner_shown = False  #            
            self._show_mode_banner()

    def toggle_mcp_output(self):
        """MCP         """
        self.config.show_mcp_output = not self.config.show_mcp_output
        status = "  " if self.config.show_mcp_output else "  "
        print(f"[Search] MCP           {status}          .")
        if self.config.show_mcp_output:
            print("[Tip]    Deep Research      MCP                      .")
        else:
            print("[Tip] MCP                              .")

    def _show_mode_banner(self):
        """               """
        if self.mode_banner_shown:
            return
            
        if self.current_mode == "normal":
            self._show_normal_mode_banner()
        elif self.current_mode == "deep_research":
            self._show_deep_research_mode_banner()
            
        self.mode_banner_shown = True

    def _show_normal_mode_banner(self):
        """           """
        banner = """
+                                                                              +
|                        [DNA]       (Normal Mode) [DNA]                        |
|                             AI                                    |
+                                                                              +

[Drug]         AI          
[DNA]              -            
[Target]                       

[Tip]      :
   "                     "
   "EGFR                ?"

          : /mcp  Deep Research      
        """
        print(banner)

    def _show_deep_research_mode_banner(self):
        """Deep Research         """
        banner = """
+                                                                              +
|                    [Research] Deep Research MCP        [Research]                       |
|                                                                |
+                                                                              +

[Target]                    :
------------------------------------------------------------------------------
[Drug] DrugBank     - 15,000+           (      , ADMET)
[Target] OpenTargets  - 60,000+   -       (      )
[Lab] ChEMBL       -       &          (SAR   )
[Doc] BioMCP       -       &      (PubMed, ClinicalTrials.gov)
[Brain] Sequential   - AI           &   
[Web] Playwright   -       &       
------------------------------------------------------------------------------

[Start]                                  !
[Search]                           !

[Tip] Deep Research    :
1. '/mcp start'         MCP           
2.                                     
3. '/debug'                           

[Lab] Deep Research      :
   "                                     "
   "BRCA1                                  "
   "                                  "
   "                                  "

       : /normal             
        """
        print(banner)


#         
async def main(debug_mode=False):
    """
         

    Args:
        debug_mode (bool):              
    """
    config = Config(debug_mode=debug_mode)
    chatbot = DrugDevelopmentChatbot(config)
    await chatbot.start()
