"""
MCP Manager for GAIA System Integration
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
import json
import os
import subprocess

from ..client.mcp_client import MCPClient
from ..server.mcp_server import MCPServer
from .gaia_mcp_server import GAIAMCPServer


class MCPManager:
    """Manager for MCP client/server operations in GAIA system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.server: Optional[GAIAMCPServer] = None
        self.server_task: Optional[asyncio.Task] = None
        self.local_server = None
        self.clients: Dict[str, MCPClient] = {}
        self.external_servers: Dict[str, subprocess.Popen] = {}
        self.running = False
        self.mcp_config_path = "/home/gaia-bt/workspace/GAIA_LLMs/mcp.json"
    
    async def start_server(self, 
                          transport_type: str = "mock",  # 실제 전송 없이 로컬 서버만 초기화
                          host: str = "localhost", 
                          port: int = 8765) -> bool:
        """Start GAIA MCP server"""
        try:
            # 간단한 로컬 서버 생성 (전송 없이)
            from ..server.mcp_server import MCPServer
            from ..server.handlers.gaia_tools import GAIAToolsHandler
            
            # MCP 서버 생성 및 툴 등록
            local_server = MCPServer("GAIA-MCP-Server", "0.1.0")
            tools_handler = GAIAToolsHandler(local_server)
            
            # 서버를 인스턴스 변수에 저장
            self.local_server = local_server
            self.running = True
            
            self.logger.info("GAIA MCP Server initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start MCP server: {e}")
            return False
    
    async def stop_server(self):
        """Stop GAIA MCP server"""
        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass
            self.server_task = None
        
        if self.server:
            await self.server.stop()
            self.server = None
            
        if self.local_server:
            self.local_server = None
            
        self.running = False
        self.logger.info("GAIA MCP Server stopped")
    
    async def create_client(self, client_id: str, client_name: str = None):
        """Create and initialize MCP client"""
        if client_name is None:
            client_name = f"GAIA-Client-{client_id}"
        
        # "default" 클라이언트는 로컬 서버를 사용하므로 BioMCP 툴을 지원하는 Mock 객체 생성
        if client_id == "default":
            class DefaultMockClient:
                def __init__(self, name):
                    self.name = name
                    self.server_type = 'biomcp'  # BioMCP 툴 지원
                    
                async def call_tool(self, tool_name: str, arguments: dict = None):
                    # BioMCP 툴들 처리
                    if tool_name in ['article_searcher', 'trial_searcher', 'search_variants']:
                        return await self._mock_biomcp_response(tool_name, arguments)
                    elif tool_name in ['start_thinking', 'think', 'complete_thinking']:
                        return await self._mock_thinking_response(tool_name, arguments)
                    elif tool_name in ['get_recent_preprints', 'search_preprints', 'get_preprint_by_doi', 'find_published_version']:
                        return await self._mock_biorxiv_response(tool_name, arguments)
                    else:
                        return {"content": [{"type": "text", "text": f"Default mock response for {tool_name}"}]}
                
                async def _mock_biomcp_response(self, tool_name: str, arguments: dict):
                    keywords = arguments.get('keywords', 'unknown') if arguments else 'unknown'
                    call_benefit = arguments.get('call_benefit', '') if arguments else ''
                    
                    if tool_name == 'article_searcher':
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"""BioMCP 생의학 논문 검색 결과 ('{keywords}'):

📄 **최신 연구 논문:**

1. "Molecular mechanisms of {keywords} in therapeutic applications"
   - 저자: Smith J, et al. (2024) 
   - 녹지: Nature Medicine
   - PMID: 38234567
   - 요약: {keywords}에 대한 최신 분자 메커니즘 연구

2. "Clinical efficacy and safety of {keywords}-based treatments" 
   - 저자: Johnson K, et al. (2024)
   - 녹지: The Lancet
   - PMID: 38234568
   - 요약: 임상 효능 및 안전성 프로파일 분석

📋 **검색 정보:**
- 키워드: {keywords}
- 검색 목적: {call_benefit}

⚠️ **Mock 데이터:** 실제 BioMCP 서버 시작 및 '/mcp start' 명령어로 실시간 데이터 확인 가능"""
                                }
                            ]
                        }
                    elif tool_name == 'trial_searcher':
                        conditions = arguments.get('conditions', 'unknown') if arguments else 'unknown'
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"""BioMCP 임상시험 검색 결과 ('{conditions}'):

🏥 **진행 중인 임상시험:**

1. NCT05234567: "Phase III Study of {conditions} Treatment"
   - 상태: Recruiting
   - 대상: 300명 
   - 예상 완료: 2026-12-31
   - 주진렴: Memorial Sloan Kettering

2. NCT05234568: "Novel Biomarker Study for {conditions}"
   - 상태: Active, not recruiting
   - 대상: 150명
   - Phase: II
   - 주진렴: Johns Hopkins University

📋 **검색 정보:**
- 질환/조건: {conditions}
- 검색 목적: {call_benefit}

⚠️ **Mock 데이터:** 실제 BioMCP 서버 시작으로 실시간 ClinicalTrials.gov 데이터 확인 가능"""
                                }
                            ]
                        }
                    else:
                        return {"content": [{"type": "text", "text": f"BioMCP Mock: {tool_name} 기본 응답"}]}
                
                async def _mock_thinking_response(self, tool_name: str, arguments: dict):
                    problem = arguments.get('problem', 'unknown') if arguments else 'unknown'
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"""Sequential Thinking 연구 계획:

🧠 **문제 분석:** {problem}

📋 **AI 연구 전략:**
1. 문제 정의 및 범위 설정
2. 기존 연구 문헌 검토 및 분석
3. 과학적 근거 및 데이터 평가
4. 신약개발 가능성 분석
5. 결론 및 추천 사항 도출

⚠️ **Mock 데이터:** 실제 Sequential Thinking 서버로 상세한 AI 분석 가능"""
                            }
                        ]
                    }
                
                async def _mock_biorxiv_response(self, tool_name: str, arguments: dict):
                    server = arguments.get('server', 'biorxiv') if arguments else 'biorxiv'
                    interval = arguments.get('interval', 7) if arguments else 7
                    limit = arguments.get('limit', 10) if arguments else 10
                    
                    if tool_name == 'get_recent_preprints':
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"""BioRxiv 최신 프리프린트 검색 결과 ({server}, 최근 {interval}일):

📑 **최신 프리프린트 논문:**

1. "Novel CRISPR-Cas9 applications in cancer therapy: recent advances"
   - 저자: Chen L, et al. (2024)
   - 서버: bioRxiv
   - DOI: 10.1101/2024.12.01.123456
   - 날짜: 2024-12-01
   - 요약: CRISPR-Cas9 기술을 이용한 최신 암 치료법 개발에 대한 연구

2. "Machine learning approaches for drug discovery: preprint analysis"
   - 저자: Smith K, et al. (2024)
   - 서버: bioRxiv  
   - DOI: 10.1101/2024.11.30.789012
   - 날짜: 2024-11-30
   - 요약: 머신러닝을 활용한 신약개발 접근법 분석

📋 **검색 매개변수:**
- 서버: {server}
- 검색 기간: 최근 {interval}일
- 결과 한도: {limit}개

⚠️ **주의:** 이는 Mock 데이터입니다. 실제 BioRxiv 서버를 시작하여 실시간 프리프린트 데이터를 확인하세요."""
                                }
                            ]
                        }
                    else:
                        return {"content": [{"type": "text", "text": f"BioRxiv Mock: {tool_name} 기본 응답"}]}
                    
            self.clients[client_id] = DefaultMockClient(client_name)
            self.logger.info(f"Default mock MCP client '{client_id}' created with BioMCP tool support")
            return self.clients[client_id]
        
        # 실제 외부 클라이언트 생성
        client = MCPClient(client_name)
        
        # Initialize client
        if await client.initialize():
            self.clients[client_id] = client
            self.logger.info(f"MCP client '{client_id}' created and initialized")
            return client
        else:
            raise RuntimeError(f"Failed to initialize MCP client '{client_id}'")
    
    async def remove_client(self, client_id: str):
        """Remove MCP client"""
        if client_id in self.clients:
            await self.clients[client_id].disconnect()
            del self.clients[client_id]
            self.logger.info(f"MCP client '{client_id}' removed")
    
    async def call_tool(self, 
                       client_id: str, 
                       tool_name: str, 
                       arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call tool using specific client"""
        # "default" 클라이언트인 경우 로컬 서버 사용
        if client_id == "default" and self.local_server:
            try:
                # 직접 툴 핸들러 호출
                if tool_name in self.local_server.tool_handlers:
                    handler = self.local_server.tool_handlers[tool_name]
                    result = await handler(**(arguments or {}))
                    
                    # MCP 응답 형식으로 래핑
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": str(result)
                            }
                        ]
                    }
                else:
                    # 로컬 서버에 없으면 외부 서버에서 찾기
                    return await self._find_and_call_tool(tool_name, arguments)
            except Exception as e:
                # 로컬 실행 실패시 외부 서버 시도
                try:
                    return await self._find_and_call_tool(tool_name, arguments)
                except:
                    raise RuntimeError(f"Tool execution failed: {e}")
        
        # 외부 클라이언트 사용
        if client_id not in self.clients:
            raise ValueError(f"Client '{client_id}' not found")
        
        client = self.clients[client_id]
        return await client.call_tool(tool_name, arguments)
    
    async def _find_and_call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Find tool in available servers and call it"""
        # ChEMBL 툴들
        chembl_tools = ['search_molecule', 'search_target', 'canonicalize_smiles']
        if tool_name in chembl_tools and 'chembl' in self.clients:
            client = self.clients['chembl']
            return await client.call_tool(tool_name, arguments)
        
        # BioMCP 툴들 - default 클라이언트에서 처리 (Mock 응답)
        biomcp_tools = ['article_searcher', 'trial_searcher', 'search_variants']
        if tool_name in biomcp_tools:
            # default 클라이언트에서 Mock 응답 사용
            if 'default' in self.clients:
                return await self.clients['default'].call_tool(tool_name, arguments)
            else:
                # default 클라이언트가 없으면 직접 Mock 응답 생성
                return await self._generate_biomcp_mock_response(tool_name, arguments)
        
        # 호환성을 위한 별칭 매핑
        biomcp_aliases = {
            'search_articles': 'article_searcher',
            'search_trials': 'trial_searcher'
        }
        if tool_name in biomcp_aliases:
            actual_tool_name = biomcp_aliases[tool_name]
            # default 클라이언트에서 실제 툴 이름으로 호출
            if 'default' in self.clients:
                return await self.clients['default'].call_tool(actual_tool_name, arguments)
            else:
                return await self._generate_biomcp_mock_response(actual_tool_name, arguments)
        
        # Sequential Thinking 툴들 - default 클라이언트에서 처리
        thinking_tools = ['start_thinking', 'think', 'complete_thinking']
        if tool_name in thinking_tools:
            if 'default' in self.clients:
                return await self.clients['default'].call_tool(tool_name, arguments)
            else:
                return await self._generate_thinking_mock_response(tool_name, arguments)
        
        # BioRxiv 툴들 - Mock 응답으로 처리
        biorxiv_tools = ['get_recent_preprints', 'search_preprints', 'get_preprint_by_doi', 'find_published_version']
        if tool_name in biorxiv_tools:
            if 'biorxiv-mcp' in self.clients:
                return await self.clients['biorxiv-mcp'].call_tool(tool_name, arguments)
            else:
                return await self._generate_biorxiv_mock_response(tool_name, arguments)
        
        # 마지막으로 모든 클라이언트에서 툴 찾기 (단, Mock 클라이언트만)
        for client_id, client in self.clients.items():
            if hasattr(client, 'call_tool') and hasattr(client, 'server_type'):
                try:
                    return await client.call_tool(tool_name, arguments)
                except Exception as e:
                    # "Method not implemented" 오류는 무시하고 다음 클라이언트 시도
                    if "Method not implemented" in str(e):
                        continue
                    else:
                        continue
        
        raise ValueError(f"Tool '{tool_name}' not found in any available server")
    
    async def list_tools(self, client_id: str) -> List[Dict[str, Any]]:
        """List available tools for specific client"""
        # "default" 클라이언트인 경우 로컬 서버 사용
        if client_id == "default" and self.local_server:
            return [tool.to_dict() for tool in self.local_server.tools.values()]
        
        # 외부 클라이언트 사용
        if client_id not in self.clients:
            raise ValueError(f"Client '{client_id}' not found")
        
        client = self.clients[client_id]
        return await client.list_tools()
    
    async def research_question(self, 
                               question: str, 
                               depth: str = "detailed",
                               client_id: str = "default") -> str:
        """Research a question using MCP tools"""
        try:
            # Ensure client exists
            if client_id not in self.clients:
                await self.create_client(client_id)
            
            # Call research tool
            result = await self.call_tool(
                client_id=client_id,
                tool_name="research_question",
                arguments={
                    "question": question,
                    "depth": depth
                }
            )
            
            # Extract text content from result
            content = result.get("content", [])
            if content and len(content) > 0:
                return content[0].get("text", "No result")
            else:
                return "No result returned"
                
        except Exception as e:
            self.logger.error(f"Error researching question: {e}")
            return f"Error: {str(e)}"
    
    async def evaluate_answer(self, 
                             question: str, 
                             answer: str,
                             criteria: List[str] = None,
                             client_id: str = "default") -> str:
        """Evaluate an answer using MCP tools"""
        try:
            # Ensure client exists
            if client_id not in self.clients:
                await self.create_client(client_id)
            
            # Call evaluation tool
            result = await self.call_tool(
                client_id=client_id,
                tool_name="evaluate_answer",
                arguments={
                    "question": question,
                    "answer": answer,
                    "criteria": criteria or ["accuracy", "completeness", "clarity"]
                }
            )
            
            # Extract text content from result
            content = result.get("content", [])
            if content and len(content) > 0:
                return content[0].get("text", "No result")
            else:
                return "No result returned"
                
        except Exception as e:
            self.logger.error(f"Error evaluating answer: {e}")
            return f"Error: {str(e)}"
    
    async def save_research(self, 
                           title: str, 
                           content: str,
                           format: str = "markdown",
                           client_id: str = "default") -> str:
        """Save research using MCP tools"""
        try:
            # Ensure client exists
            if client_id not in self.clients:
                await self.create_client(client_id)
            
            # Call save tool
            result = await self.call_tool(
                client_id=client_id,
                tool_name="save_research",
                arguments={
                    "title": title,
                    "content": content,
                    "format": format
                }
            )
            
            # Extract text content from result
            content = result.get("content", [])
            if content and len(content) > 0:
                return content[0].get("text", "No result")
            else:
                return "No result returned"
                
        except Exception as e:
            self.logger.error(f"Error saving research: {e}")
            return f"Error: {str(e)}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get MCP manager status"""
        server_info = None
        if self.local_server:
            server_info = {
                "name": self.local_server.name,
                "version": self.local_server.version,
                "tools_count": len(self.local_server.tools),
                "initialized": self.local_server.initialized
            }
        elif self.server:
            server_info = self.server.get_server_info()
            
        return {
            "running": self.running,
            "server_active": self.local_server is not None or self.server is not None,
            "clients_count": len(self.clients),
            "client_ids": list(self.clients.keys()),
            "server_info": server_info
        }
    
    async def cleanup(self):
        """Cleanup all resources"""
        # Disconnect all clients
        for client_id in list(self.clients.keys()):
            await self.remove_client(client_id)
        
        # Stop server
        await self.stop_server()
        
        self.logger.info("MCP Manager cleanup completed")
    
    async def start_external_servers(self, servers: List[str] = None):
        """Start external MCP servers (biomcp, sequential-thinking, etc.)"""
        try:
            # Load MCP configuration
            config_path = "/home/gaia-bt/workspace/GAIA_LLMs/config/mcp.json"  # 올바른 경로 사용
            if not os.path.exists(config_path):
                self.logger.error(f"mcp.json not found at {config_path}")
                return False
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Default to all available drug development servers if not specified
            if servers is None:
                servers = ['biomcp', 'chembl', 'sequential-thinking', 'drugbank-mcp', 'opentargets-mcp', 'biorxiv-mcp']
            
            for server_name in servers:
                if server_name in config.get('mcpServers', {}):
                    server_config = config['mcpServers'][server_name]
                    
                    try:
                        # Special handling for different server types
                        if server_name in ['drugbank-mcp', 'opentargets-mcp', 'biorxiv-mcp']:
                            # DrugBank, OpenTargets, and BioRxiv servers - create mock clients for now
                            await self._create_mock_client(server_name, server_config)
                        else:
                            # Original server startup logic for other servers
                            await self._start_server_process(server_name, server_config)
                            
                    except Exception as e:
                        self.logger.error(f"Failed to start {server_name}: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting external servers: {e}")
            return False
    
    async def _create_mock_client(self, server_name: str, server_config: Dict[str, Any]):
        """Create mock client for DrugBank and OpenTargets servers"""
        class MockMCPClient:
            def __init__(self, name, server_type):
                self.name = name
                self.server_type = server_type
                
            async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None):
                # Mock responses for different tools
                if self.server_type == 'drugbank-mcp':
                    return await self._mock_drugbank_response(tool_name, arguments)
                elif self.server_type == 'opentargets-mcp':
                    return await self._mock_opentargets_response(tool_name, arguments)
                elif self.server_type == 'biorxiv-mcp':
                    return await self._mock_biorxiv_response(tool_name, arguments)
                elif self.server_type == 'biomcp' or self.server_type == 'default':
                    return await self._mock_biomcp_response(tool_name, arguments)
                else:
                    return {"content": [{"type": "text", "text": f"Mock response for {tool_name}"}]}
            
            async def _mock_drugbank_response(self, tool_name: str, arguments: Dict[str, Any]):
                query = arguments.get('query', 'unknown') if arguments else 'unknown'
                
                if tool_name == 'search_drugs':
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"""DrugBank 약물 검색 결과 ('{query}'):

• DB00945: 아스피린 (Aspirin)
  - 적응증: 통증 완화, 해열, 심혈관 보호
  - 작용 메커니즘: COX-1/COX-2 억제
  - 주의사항: 출혈 위험, 위장관 부작용

• DB01050: 이부프로펜 (Ibuprofen)  
  - 적응증: 염증성 통증, 관절염
  - 작용 메커니즘: 비선택적 COX 억제
  - 주의사항: 신독성, 심혈관 위험

• DB00563: 메트포민 (Metformin)
  - 적응증: 제2형 당뇨병
  - 작용 메커니즘: 글루코오스 생산 억제
  - 주의사항: 유산산증 위험"""
                            }
                        ]
                    }
                elif tool_name == 'get_drug_details':
                    return {
                        "content": [
                            {
                                "type": "text", 
                                "text": f"DrugBank 상세 정보: {query}에 대한 상세 약물 정보가 포함됩니다."
                            }
                        ]
                    }
                else:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"DrugBank {tool_name}: {query}에 대한 결과"
                            }
                        ]
                    }
            
            async def _mock_opentargets_response(self, tool_name: str, arguments: Dict[str, Any]):
                query = arguments.get('query', 'unknown') if arguments else 'unknown'
                
                if tool_name == 'search_targets':
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"""OpenTargets 타겟 검색 결과 ('{query}'):

• ENSG00000139618: BRCA1
  - 유전자명: BRCA1 (Breast Cancer 1)
  - 염색체 위치: 17q21.31
  - 기능: DNA 손상 복구, 종양 억제
  - 연관 질병: 유방암, 난소암

• ENSG00000141510: TP53
  - 유전자명: TP53 (Tumor Protein p53)
  - 염색체 위치: 17p13.1  
  - 기능: 세포 주기 조절, 아폽토시스
  - 연관 질병: 다양한 암종

• ENSG00000146648: EGFR
  - 유전자명: EGFR (Epidermal Growth Factor Receptor)
  - 염색체 위치: 7p11.2
  - 기능: 세포 성장 신호 전달
  - 연관 질병: 폐암, 두경부암"""
                            }
                        ]
                    }
                elif tool_name == 'search_diseases':
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"""OpenTargets 질병 검색 결과 ('{query}'):

• EFO_0000311: 유방암 (Breast Carcinoma)
  - 치료 영역: 종양학
  - 연관 타겟: BRCA1, BRCA2, TP53, EGFR
  - 임상시험 수: 2,847개

• EFO_0001071: 당뇨병 (Diabetes Mellitus)
  - 치료 영역: 내분비학
  - 연관 타겟: INS, INSR, PPARG
  - 임상시험 수: 1,523개

• EFO_0000249: 알츠하이머병 (Alzheimer Disease)
  - 치료 영역: 신경학
  - 연관 타겟: APP, PSEN1, APOE
  - 임상시험 수: 1,102개"""
                            }
                        ]
                    }
                else:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"OpenTargets {tool_name}: {query}에 대한 결과"
                            }
                        ]
                    }
            
            async def _mock_biorxiv_response(self, tool_name: str, arguments: Dict[str, Any]):
                """Mock responses for BioRxiv tools"""
                server = arguments.get('server', 'biorxiv') if arguments else 'biorxiv'
                interval = arguments.get('interval', 7) if arguments else 7
                limit = arguments.get('limit', 10) if arguments else 10
                
                if tool_name == 'get_recent_preprints':
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"""BioRxiv 최신 프리프린트 검색 결과 ({server}, 최근 {interval}일):

📑 **최신 프리프린트 논문:**

1. "Novel CRISPR-Cas9 applications in cancer therapy: recent advances"
   - 저자: Chen L, et al. (2024)
   - 서버: bioRxiv
   - DOI: 10.1101/2024.12.01.123456
   - 날짜: 2024-12-01
   - 요약: CRISPR-Cas9 기술을 이용한 최신 암 치료법 개발에 대한 연구

2. "Machine learning approaches for drug discovery: preprint analysis"
   - 저자: Smith K, et al. (2024)
   - 서버: bioRxiv
   - DOI: 10.1101/2024.11.30.789012
   - 날짜: 2024-11-30
   - 요약: 머신러닝을 활용한 신약개발 접근법 분석

3. "Targeted therapy resistance mechanisms in solid tumors"
   - 저자: Johnson M, et al. (2024)
   - 서버: bioRxiv
   - DOI: 10.1101/2024.11.29.345678
   - 날짜: 2024-11-29
   - 요약: 고형암에서의 표적치료 내성 메커니즘 연구

📋 **검색 매개변수:**
- 서버: {server}
- 검색 기간: 최근 {interval}일
- 결과 한도: {limit}개
- 총 검색된 논문: 3개 (Mock 데이터)

⚠️ **주의:** 이는 Mock 데이터입니다. 실제 BioRxiv 서버를 시작하여 실시간 프리프린트 데이터를 확인하세요."""
                            }
                        ]
                    }
                elif tool_name == 'search_preprints':
                    start_date = arguments.get('start_date', '2024-11-20') if arguments else '2024-11-20'
                    end_date = arguments.get('end_date', '2024-12-12') if arguments else '2024-12-12'
                    category = arguments.get('category', None) if arguments else None
                    
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"""BioRxiv 프리프린트 검색 결과 ({start_date} ~ {end_date}):

📑 **검색된 프리프린트 논문:**

1. "Single-cell RNA sequencing reveals novel biomarkers for immunotherapy"
   - 저자: Wang H, et al. (2024)
   - 카테고리: Cancer Biology
   - DOI: 10.1101/2024.12.10.112233
   - 날짜: 2024-12-10
   - 요약: 단일세포 RNA 시퀀싱을 통한 면역치료 바이오마커 발굴

2. "AI-driven compound optimization for kinase inhibitors"
   - 저자: Lee S, et al. (2024)
   - 카테고리: Chemical Biology
   - DOI: 10.1101/2024.12.08.445566
   - 날짜: 2024-12-08
   - 요약: 인공지능 기반 키나제 억제제 화합물 최적화

📋 **검색 매개변수:**
- 검색 기간: {start_date} ~ {end_date}
- 카테고리: {category if category else '전체'}
- 서버: {server}
- 결과 한도: {limit}개

⚠️ **주의:** 이는 Mock 데이터입니다. 실제 BioRxiv API 접속으로 최신 프리프린트를 확인하세요."""
                            }
                        ]
                    }
                elif tool_name == 'get_preprint_by_doi':
                    doi = arguments.get('doi', 'unknown') if arguments else 'unknown'
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"""BioRxiv 프리프린트 상세 정보 (DOI: {doi}):

📑 **프리프린트 세부사항:**

제목: "Advanced gene editing techniques for cancer therapy"
저자: Martinez A, Brown B, Davis C, et al.
서버: bioRxiv
버전: v2
게시일: 2024-12-01
카테고리: Cancer Biology

📋 **초록:**
본 연구는 암 치료를 위한 고급 유전자 편집 기술의 개발과 적용에 대해 다룹니다. 
CRISPR-Cas9, Prime Editing, Base Editing 등의 차세대 유전자 편집 도구들의 
임상 적용 가능성을 종합적으로 분석하였습니다.

🔗 **DOI URL:** https://doi.org/{doi}

⚠️ **주의:** 이는 Mock 데이터입니다. 실제 DOI로 정확한 프리프린트 정보를 확인하세요."""
                            }
                        ]
                    }
                else:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"BioRxiv Mock: {tool_name} 툴에 대한 기본 응답입니다."
                            }
                        ]
                    }
            
            async def _mock_biomcp_response(self, tool_name: str, arguments: Dict[str, Any]):
                """Mock responses for BioMCP tools"""
                keywords = arguments.get('keywords', 'unknown') if arguments else 'unknown'
                call_benefit = arguments.get('call_benefit', '') if arguments else ''
                
                if tool_name == 'article_searcher':
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"""BioMCP 생의학 논문 검색 결과 ('{keywords}'):

📄 **최신 연구 논문:**

1. "Molecular mechanisms of {keywords} in therapeutic applications"
   - 저자: Smith J, et al. (2024)
   - 녹지: Nature Medicine
   - PMID: 38234567
   - 요약: {keywords}에 대한 최신 분자 메커니즘 연구 결과

2. "Clinical efficacy and safety profile of {keywords}-based treatments"
   - 저자: Johnson K, et al. (2024)
   - 녹지: The Lancet
   - PMID: 38234568
   - 요약: 임상 효능 및 안전성 프로파일 분석

3. "Emerging therapeutic targets related to {keywords}"
   - 저자: Williams M, et al. (2023)
   - 녹지: Cell
   - PMID: 37891234
   - 요약: 신규 치료 타겟 발굴 및 검증

📋 **검색 매개변수:**
- 키워드: {keywords}
- 검색 목적: {call_benefit}
- 검색된 논문 수: 3개 (Mock 데이터)

⚠️ **주의:** 이는 Mock 데이터입니다. 실제 BioMCP 서버를 시작하여 실시간 PubMed 데이터를 확인하세요."""
                            }
                        ]
                    }
                
                elif tool_name == 'trial_searcher':
                    conditions = arguments.get('conditions', 'unknown') if arguments else 'unknown'
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"""BioMCP 임상시험 검색 결과 ('{conditions}'):

🏥 **진행 중인 임상시험:**

1. NCT05234567: "Phase III Study of {conditions} Treatment"
   - 상태: Recruiting
   - 대상: 300명
   - 시작일: 2024-01-15
   - 예상 완료: 2026-12-31
   - 주진렴: Memorial Sloan Kettering Cancer Center

2. NCT05234568: "Novel Biomarker Study for {conditions}"
   - 상태: Active, not recruiting
   - 대상: 150명
   - Phase: II
   - 주진렴: Johns Hopkins University

3. NCT05234569: "Combination Therapy for Advanced {conditions}"
   - 상태: Recruiting
   - 대상: 500명
   - Phase: III
   - 주진렴: Mayo Clinic

📋 **검색 매개변수:**
- 질환/조건: {conditions}
- 검색 목적: {call_benefit}
- 찾은 임상시험 수: 3개 (Mock 데이터)

⚠️ **주의:** 이는 Mock 데이터입니다. 실제 BioMCP 서버를 시작하여 실시간 ClinicalTrials.gov 데이터를 확인하세요."""
                            }
                        ]
                    }
                
                elif tool_name == 'start_thinking':
                    problem = arguments.get('problem', 'unknown') if arguments else 'unknown'
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"""Sequential Thinking 연구 계획 수립:

🧠 **문제 분석:** {problem}

📋 **연구 전략:**
1. 문제 정의 및 대상 범위 설정
2. 기존 연구 문헌 검토
3. 과학적 근거 또는 임상 데이터 분석
4. 신약개발 가능성 평가
5. 결론 및 추천 사항 도출

🎯 **예상 결과:** 체계적이고 근거 기반의 연구 계획 수립

⚠️ **주의:** 이는 Mock 데이터입니다. 실제 Sequential Thinking 서버를 시작하여 상세한 AI 분석을 받으세요."""
                            }
                        ]
                    }
                
                else:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"BioMCP Mock: {tool_name} 툴에 대한 기본 응답입니다."
                            }
                        ]
                    }
        
        # Create and register the mock client
        mock_client = MockMCPClient(f"GAIA-{server_name}", server_name)
        self.clients[server_name] = mock_client
        
        # BioMCP 툴들을 default 클라이언트에도 등록
        if server_name == 'biomcp':
            self.clients['default'] = mock_client
        
        self.logger.info(f"Created mock MCP client for: {server_name}")
    
    async def _start_server_process(self, server_name: str, server_config: Dict[str, Any]):
        """Start actual server process for biomcp, chembl, etc."""
        # Build command
        cmd = [server_config['command']] + server_config.get('args', [])
        
        # Set environment
        env = os.environ.copy()
        if 'env' in server_config:
            env.update(server_config['env'])
        
        # Set working directory
        cwd = server_config.get('cwd', None)
        
        # Start server process
        process = subprocess.Popen(
            cmd,
            env=env,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        
        self.external_servers[server_name] = process
        self.logger.info(f"Started external MCP server: {server_name}")
        
        # Give server time to initialize
        await asyncio.sleep(2)
        
        # Create client for this server
        await self.create_client(server_name, f"GAIA-{server_name}")
    
    async def stop_external_servers(self):
        """Stop all external MCP servers"""
        for server_name, process in self.external_servers.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                self.logger.info(f"Stopped external MCP server: {server_name}")
            except:
                process.kill()
                self.logger.warning(f"Force killed external MCP server: {server_name}")
        
        self.external_servers.clear()
    
    async def connect_to_mcp_server(self, server_name: str, server_config: Dict[str, Any]):
        """Connect to a specific MCP server"""
        try:
            # Create specialized client based on server type
            if server_name == 'biomcp':
                # BiomCP specific connection
                client = MCPClient(f"GAIA-{server_name}")
                # Configure for BiomCP
                await client.initialize()
                self.clients[server_name] = client
                
            elif server_name in ['sequential-thinking', 'gaia-sequential-thinking-python']:
                # Sequential Thinking specific connection
                client = MCPClient(f"GAIA-{server_name}")
                # Configure for Sequential Thinking
                await client.initialize()
                self.clients[server_name] = client
                
            else:
                # Generic MCP connection
                client = MCPClient(f"GAIA-{server_name}")
                await client.initialize()
                self.clients[server_name] = client
                
            self.logger.info(f"Connected to MCP server: {server_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {server_name}: {e}")
            return False
    
    async def _generate_biomcp_mock_response(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate mock response for BioMCP tools when server is not available"""
        keywords = arguments.get('keywords', 'unknown') if arguments else 'unknown'
        call_benefit = arguments.get('call_benefit', '') if arguments else ''
        
        if tool_name == 'article_searcher':
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"""BioMCP 생의학 논문 검색 결과 ('{keywords}'):

📄 **최신 연구 논문:**

1. "Molecular mechanisms of {keywords} in therapeutic applications"
   - 저자: Smith J, et al. (2024) 
   - 녹지: Nature Medicine
   - PMID: 38234567
   - 요약: {keywords}에 대한 최신 분자 메커니즘 연구

2. "Clinical efficacy and safety of {keywords}-based treatments" 
   - 저자: Johnson K, et al. (2024)
   - 녹지: The Lancet
   - PMID: 38234568
   - 요약: 임상 효능 및 안전성 프로파일 분석

📋 **검색 정보:**
- 키워드: {keywords}
- 검색 목적: {call_benefit}

⚠️ **Mock 데이터:** 실제 BioMCP 서버 시작 및 '/mcp start' 명령어로 실시간 데이터 확인 가능"""
                    }
                ]
            }
        elif tool_name == 'trial_searcher':
            conditions = arguments.get('conditions', 'unknown') if arguments else 'unknown'
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"""BioMCP 임상시험 검색 결과 ('{conditions}'):

🏥 **진행 중인 임상시험:**

1. NCT05234567: "Phase III Study of {conditions} Treatment"
   - 상태: Recruiting
   - 대상: 300명 
   - 예상 완료: 2026-12-31
   - 주진렴: Memorial Sloan Kettering

2. NCT05234568: "Novel Biomarker Study for {conditions}"
   - 상태: Active, not recruiting
   - 대상: 150명
   - Phase: II
   - 주진렴: Johns Hopkins University

📋 **검색 정보:**
- 질환/조건: {conditions}
- 검색 목적: {call_benefit}

⚠️ **Mock 데이터:** 실제 BioMCP 서버 시작으로 실시간 ClinicalTrials.gov 데이터 확인 가능"""
                    }
                ]
            }
        else:
            return {"content": [{"type": "text", "text": f"BioMCP Mock: {tool_name} 기본 응답"}]}
    
    async def _generate_thinking_mock_response(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate mock response for Sequential Thinking tools when server is not available"""
        problem = arguments.get('problem', 'unknown') if arguments else 'unknown'
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"""Sequential Thinking 연구 계획:

🧠 **문제 분석:** {problem}

📋 **AI 연구 전략:**
1. 문제 정의 및 범위 설정
2. 기존 연구 문헌 검토 및 분석
3. 과학적 근거 및 데이터 평가
4. 신약개발 가능성 분석
5. 결론 및 추천 사항 도출

⚠️ **Mock 데이터:** 실제 Sequential Thinking 서버로 상세한 AI 분석 가능"""
                }
            ]
        }
    
    async def _generate_biorxiv_mock_response(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate mock response for BioRxiv tools when server is not available"""
        server = arguments.get('server', 'biorxiv') if arguments else 'biorxiv'
        interval = arguments.get('interval', 7) if arguments else 7
        limit = arguments.get('limit', 10) if arguments else 10
        
        if tool_name == 'get_recent_preprints':
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"""BioRxiv 최신 프리프린트 검색 결과 ({server}, 최근 {interval}일):

📑 **최신 프리프린트 논문:**

1. "Novel CRISPR-Cas9 applications in cancer therapy: recent advances"
   - 저자: Chen L, et al. (2024)
   - 서버: bioRxiv
   - DOI: 10.1101/2024.12.01.123456
   - 날짜: 2024-12-01
   - 요약: CRISPR-Cas9 기술을 이용한 최신 암 치료법 개발에 대한 연구

2. "Machine learning approaches for drug discovery: preprint analysis"
   - 저자: Smith K, et al. (2024)
   - 서버: bioRxiv
   - DOI: 10.1101/2024.11.30.789012
   - 날짜: 2024-11-30
   - 요약: 머신러닝을 활용한 신약개발 접근법 분석

📋 **검색 매개변수:**
- 서버: {server}
- 검색 기간: 최근 {interval}일
- 결과 한도: {limit}개

⚠️ **주의:** 이는 Mock 데이터입니다. 실제 BioRxiv 서버를 시작하여 실시간 프리프린트 데이터를 확인하세요."""
                    }
                ]
            }
        else:
            return {"content": [{"type": "text", "text": f"BioRxiv Mock: {tool_name} 기본 응답"}]}