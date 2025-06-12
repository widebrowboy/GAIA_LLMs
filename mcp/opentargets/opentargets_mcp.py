#!/usr/bin/env python3
"""
OpenTargets MCP Server for GAIA-BT Drug Development Research
Based on gosset-ai/mcps implementation with enhancements for drug development research.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

# MCP 임포트 (설치된 경우에만)
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        CallToolRequest,
        CallToolResult,
    )
    MCP_AVAILABLE = True
except ImportError:
    # MCP가 설치되지 않은 경우 기본 클래스 제공
    MCP_AVAILABLE = False
    
    class Server:
        def __init__(self, name):
            self.name = name
            self._tools = {}
        
        def call_tool(self):
            def decorator(func):
                self._tools[func.__name__] = func
                return func
            return decorator

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenTargetsMCPServer:
    """OpenTargets Platform API MCP Server for drug development research"""
    
    def __init__(self):
        self.server = Server("opentargets-mcp")
        self.base_url = "https://api.platform.opentargets.org/api/v4"
        
        # 툴 등록
        self._register_tools()
    
    def _register_tools(self):
        """MCP 툴 등록"""
        
        @self.server.call_tool()
        async def search_targets(query: str, limit: int = 10) -> List[Dict[str, Any]]:
            """
            OpenTargets에서 타겟 유전자 검색
            
            Args:
                query: 검색할 유전자명 또는 키워드
                limit: 반환할 최대 결과 수 (기본값: 10)
            
            Returns:
                검색된 타겟 정보 리스트
            """
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/graphql",
                        params={
                            "query": f"""
                            query SearchTargets {{
                                search(queryString: "{query}", entityNames: ["target"]) {{
                                    hits {{
                                        id
                                        name
                                        description
                                        object {{
                                            ... on Target {{
                                                id
                                                approvedSymbol
                                                approvedName
                                                biotype
                                                functionDescriptions
                                                go {{
                                                    id
                                                    name
                                                }}
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                            """
                        }
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # 결과 포맷팅
                    results = []
                    hits = data.get("data", {}).get("search", {}).get("hits", [])
                    
                    for hit in hits[:limit]:
                        target_obj = hit.get("object", {})
                        results.append({
                            "target_id": target_obj.get("id"),
                            "symbol": target_obj.get("approvedSymbol"),
                            "name": target_obj.get("approvedName"),
                            "biotype": target_obj.get("biotype"),
                            "description": hit.get("description"),
                            "function_descriptions": target_obj.get("functionDescriptions", []),
                            "go_terms": [go.get("name") for go in target_obj.get("go", [])][:5]
                        })
                    
                    return results
                    
            except httpx.HTTPError as e:
                logger.error(f"OpenTargets API 오류: {e}")
                return [{"error": f"API 요청 실패: {str(e)}"}]
            except Exception as e:
                logger.error(f"예상치 못한 오류: {e}")
                return [{"error": f"예상치 못한 오류: {str(e)}"}]
        
        @self.server.call_tool()
        async def get_target_details(target_id: str) -> Dict[str, Any]:
            """
            특정 타겟의 상세 정보 조회
            
            Args:
                target_id: OpenTargets 타겟 ID (예: ENSG00000139618)
            
            Returns:
                타겟의 상세 정보
            """
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/graphql",
                        params={
                            "query": f"""
                            query GetTargetDetails {{
                                target(ensemblId: "{target_id}") {{
                                    id
                                    approvedSymbol
                                    approvedName
                                    biotype
                                    chromosome
                                    start
                                    end
                                    strand
                                    description
                                    functionDescriptions
                                    synonyms
                                    nameSynonyms
                                    symbolSynonyms
                                    subcellularLocations
                                    pathways {{
                                        pathway
                                        pathwayId
                                    }}
                                    tractability {{
                                        label
                                        value
                                    }}
                                }}
                            }}
                            """
                        }
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    target = data.get("data", {}).get("target", {})
                    
                    if not target:
                        return {"error": f"타겟 {target_id}를 찾을 수 없습니다."}
                    
                    # 상세 정보 포맷팅
                    return {
                        "target_id": target.get("id"),
                        "symbol": target.get("approvedSymbol"),
                        "name": target.get("approvedName"),
                        "biotype": target.get("biotype"),
                        "chromosome": target.get("chromosome"),
                        "genomic_location": {
                            "start": target.get("start"),
                            "end": target.get("end"),
                            "strand": target.get("strand")
                        },
                        "description": target.get("description"),
                        "function_descriptions": target.get("functionDescriptions", []),
                        "synonyms": target.get("synonyms", []),
                        "subcellular_locations": target.get("subcellularLocations", []),
                        "pathways": [{"name": p.get("pathway"), "id": p.get("pathwayId")} 
                                   for p in target.get("pathways", [])],
                        "tractability": [{"category": t.get("label"), "score": t.get("value")} 
                                       for t in target.get("tractability", [])]
                    }
                    
            except httpx.HTTPError as e:
                logger.error(f"OpenTargets API 오류: {e}")
                return {"error": f"API 요청 실패: {str(e)}"}
            except Exception as e:
                logger.error(f"예상치 못한 오류: {e}")
                return {"error": f"예상치 못한 오류: {str(e)}"}
        
        @self.server.call_tool()
        async def search_diseases(query: str, limit: int = 10) -> List[Dict[str, Any]]:
            """
            OpenTargets에서 질병 검색
            
            Args:
                query: 검색할 질병명 또는 키워드
                limit: 반환할 최대 결과 수
            
            Returns:
                검색된 질병 정보 리스트
            """
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/graphql",
                        params={
                            "query": f"""
                            query SearchDiseases {{
                                search(queryString: "{query}", entityNames: ["disease"]) {{
                                    hits {{
                                        id
                                        name
                                        description
                                        object {{
                                            ... on Disease {{
                                                id
                                                name
                                                description
                                                therapeuticAreas {{
                                                    id
                                                    name
                                                }}
                                                synonyms
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                            """
                        }
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # 결과 포맷팅
                    results = []
                    hits = data.get("data", {}).get("search", {}).get("hits", [])
                    
                    for hit in hits[:limit]:
                        disease_obj = hit.get("object", {})
                        results.append({
                            "disease_id": disease_obj.get("id"),
                            "name": disease_obj.get("name"),
                            "description": disease_obj.get("description"),
                            "therapeutic_areas": [ta.get("name") for ta in disease_obj.get("therapeuticAreas", [])],
                            "synonyms": disease_obj.get("synonyms", [])[:5]
                        })
                    
                    return results
                    
            except httpx.HTTPError as e:
                logger.error(f"OpenTargets API 오류: {e}")
                return [{"error": f"API 요청 실패: {str(e)}"}]
            except Exception as e:
                logger.error(f"예상치 못한 오류: {e}")
                return [{"error": f"예상치 못한 오류: {str(e)}"}]
        
        @self.server.call_tool()
        async def get_target_associated_diseases(target_id: str, limit: int = 10) -> List[Dict[str, Any]]:
            """
            특정 타겟과 연관된 질병 조회
            
            Args:
                target_id: OpenTargets 타겟 ID
                limit: 반환할 최대 결과 수
            
            Returns:
                타겟과 연관된 질병 리스트
            """
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/graphql",
                        params={
                            "query": f"""
                            query GetTargetDiseases {{
                                target(ensemblId: "{target_id}") {{
                                    associatedDiseases(size: {limit}) {{
                                        rows {{
                                            disease {{
                                                id
                                                name
                                                description
                                            }}
                                            score
                                            datatypeScores {{
                                                componentId
                                                score
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                            """
                        }
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    target_data = data.get("data", {}).get("target", {})
                    
                    if not target_data:
                        return [{"error": f"타겟 {target_id}를 찾을 수 없습니다."}]
                    
                    # 연관 질병 정보 포맷팅
                    results = []
                    rows = target_data.get("associatedDiseases", {}).get("rows", [])
                    
                    for row in rows:
                        disease = row.get("disease", {})
                        results.append({
                            "disease_id": disease.get("id"),
                            "disease_name": disease.get("name"),
                            "description": disease.get("description"),
                            "association_score": row.get("score"),
                            "evidence_scores": {
                                score.get("componentId"): score.get("score") 
                                for score in row.get("datatypeScores", [])
                            }
                        })
                    
                    return results
                    
            except httpx.HTTPError as e:
                logger.error(f"OpenTargets API 오류: {e}")
                return [{"error": f"API 요청 실패: {str(e)}"}]
            except Exception as e:
                logger.error(f"예상치 못한 오류: {e}")
                return [{"error": f"예상치 못한 오류: {str(e)}"}]
        
        @self.server.call_tool()
        async def get_disease_associated_targets(disease_id: str, limit: int = 10) -> List[Dict[str, Any]]:
            """
            특정 질병과 연관된 타겟 조회
            
            Args:
                disease_id: OpenTargets 질병 ID (예: EFO_0000311)
                limit: 반환할 최대 결과 수
            
            Returns:
                질병과 연관된 타겟 리스트
            """
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/graphql",
                        params={
                            "query": f"""
                            query GetDiseaseTargets {{
                                disease(efoId: "{disease_id}") {{
                                    associatedTargets(size: {limit}) {{
                                        rows {{
                                            target {{
                                                id
                                                approvedSymbol
                                                approvedName
                                                biotype
                                            }}
                                            score
                                            datatypeScores {{
                                                componentId
                                                score
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                            """
                        }
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    disease_data = data.get("data", {}).get("disease", {})
                    
                    if not disease_data:
                        return [{"error": f"질병 {disease_id}를 찾을 수 없습니다."}]
                    
                    # 연관 타겟 정보 포맷팅
                    results = []
                    rows = disease_data.get("associatedTargets", {}).get("rows", [])
                    
                    for row in rows:
                        target = row.get("target", {})
                        results.append({
                            "target_id": target.get("id"),
                            "symbol": target.get("approvedSymbol"),
                            "name": target.get("approvedName"),
                            "biotype": target.get("biotype"),
                            "association_score": row.get("score"),
                            "evidence_scores": {
                                score.get("componentId"): score.get("score") 
                                for score in row.get("datatypeScores", [])
                            }
                        })
                    
                    return results
                    
            except httpx.HTTPError as e:
                logger.error(f"OpenTargets API 오류: {e}")
                return [{"error": f"API 요청 실패: {str(e)}"}]
            except Exception as e:
                logger.error(f"예상치 못한 오류: {e}")
                return [{"error": f"예상치 못한 오류: {str(e)}"}]
        
        @self.server.call_tool()
        async def search_drugs(query: str, limit: int = 10) -> List[Dict[str, Any]]:
            """
            OpenTargets에서 약물 검색
            
            Args:
                query: 검색할 약물명 또는 키워드
                limit: 반환할 최대 결과 수
            
            Returns:
                검색된 약물 정보 리스트
            """
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/graphql",
                        params={
                            "query": f"""
                            query SearchDrugs {{
                                search(queryString: "{query}", entityNames: ["drug"]) {{
                                    hits {{
                                        id
                                        name
                                        description
                                        object {{
                                            ... on Drug {{
                                                id
                                                name
                                                type
                                                maximumClinicalTrialPhase
                                                hasBeenWithdrawn
                                                withdrawnNotice
                                                synonyms
                                                tradeNames
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                            """
                        }
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # 결과 포맷팅
                    results = []
                    hits = data.get("data", {}).get("search", {}).get("hits", [])
                    
                    for hit in hits[:limit]:
                        drug_obj = hit.get("object", {})
                        results.append({
                            "drug_id": drug_obj.get("id"),
                            "name": drug_obj.get("name"),
                            "description": hit.get("description"),
                            "type": drug_obj.get("type"),
                            "clinical_trial_phase": drug_obj.get("maximumClinicalTrialPhase"),
                            "withdrawn": drug_obj.get("hasBeenWithdrawn"),
                            "withdrawn_notice": drug_obj.get("withdrawnNotice"),
                            "synonyms": drug_obj.get("synonyms", [])[:5],
                            "trade_names": drug_obj.get("tradeNames", [])[:5]
                        })
                    
                    return results
                    
            except httpx.HTTPError as e:
                logger.error(f"OpenTargets API 오류: {e}")
                return [{"error": f"API 요청 실패: {str(e)}"}]
            except Exception as e:
                logger.error(f"예상치 못한 오류: {e}")
                return [{"error": f"예상치 못한 오류: {str(e)}"}]

async def main():
    """OpenTargets MCP 서버 실행"""
    logger.info("OpenTargets MCP Server 시작...")
    
    # 서버 인스턴스 생성
    opentargets_server = OpenTargetsMCPServer()
    
    if MCP_AVAILABLE:
        # stdio를 통한 서버 실행
        async with stdio_server() as (read_stream, write_stream):
            await opentargets_server.server.run(
                read_stream,
                write_stream,
                opentargets_server.server.create_initialization_options()
            )
    else:
        logger.warning("MCP 라이브러리가 설치되지 않았습니다. 기본 모드로 실행합니다.")
        print("OpenTargets MCP 서버가 기본 모드로 실행 중...")
        print("사용 가능한 툴:")
        for tool_name in opentargets_server.server._tools.keys():
            print(f"  - {tool_name}")
        
        # 간단한 대기 루프
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("서버를 종료합니다.")

if __name__ == "__main__":
    asyncio.run(main())