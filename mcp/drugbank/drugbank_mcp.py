#!/usr/bin/env python3
"""
DrugBank MCP Server for GAIA-BT Drug Development Research
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

class DrugBankMCPServer:
    """DrugBank API MCP Server for drug development research"""
    
    def __init__(self):
        self.server = Server("drugbank-mcp")
        self.api_key = os.getenv("DRUGBANK_API_KEY")
        self.base_url = "https://go.drugbank.com/api/v1"
        
        if not self.api_key:
            logger.warning("DRUGBANK_API_KEY not found. Some features may be limited.")
        
        # 툴 등록
        self._register_tools()
    
    def _register_tools(self):
        """MCP 툴 등록"""
        
        @self.server.call_tool()
        async def search_drugs(query: str, limit: int = 10) -> List[Dict[str, Any]]:
            """
            DrugBank에서 약물 검색
            
            Args:
                query: 검색할 약물명 또는 키워드
                limit: 반환할 최대 결과 수 (기본값: 10)
            
            Returns:
                검색된 약물 정보 리스트
            """
            try:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/drugs.json",
                        headers=headers,
                        params={"q": query, "limit": limit}
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # 결과 포맷팅
                    results = []
                    for drug in data.get("data", [])[:limit]:
                        results.append({
                            "drugbank_id": drug.get("id"),
                            "name": drug.get("name"),
                            "description": drug.get("description", "")[:200] + "..." if len(drug.get("description", "")) > 200 else drug.get("description", ""),
                            "cas_number": drug.get("cas_number"),
                            "drug_type": drug.get("type"),
                            "groups": drug.get("groups", [])
                        })
                    
                    return results
                    
            except httpx.HTTPError as e:
                logger.error(f"DrugBank API 오류: {e}")
                return [{"error": f"API 요청 실패: {str(e)}"}]
            except Exception as e:
                logger.error(f"예상치 못한 오류: {e}")
                return [{"error": f"예상치 못한 오류: {str(e)}"}]
        
        @self.server.call_tool()
        async def get_drug_details(drugbank_id: str) -> Dict[str, Any]:
            """
            특정 약물의 상세 정보 조회
            
            Args:
                drugbank_id: DrugBank ID (예: DB00001)
            
            Returns:
                약물의 상세 정보
            """
            try:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/drugs/{drugbank_id}.json",
                        headers=headers
                    )
                    response.raise_for_status()
                    
                    drug = response.json()
                    
                    # 상세 정보 포맷팅
                    return {
                        "drugbank_id": drug.get("drugbank_id"),
                        "name": drug.get("name"),
                        "description": drug.get("description"),
                        "cas_number": drug.get("cas_number"),
                        "drug_type": drug.get("type"),
                        "groups": drug.get("groups", []),
                        "indication": drug.get("indication"),
                        "pharmacodynamics": drug.get("pharmacodynamics"),
                        "mechanism_of_action": drug.get("mechanism_of_action"),
                        "toxicity": drug.get("toxicity"),
                        "metabolism": drug.get("metabolism"),
                        "absorption": drug.get("absorption"),
                        "half_life": drug.get("half_life"),
                        "protein_binding": drug.get("protein_binding"),
                        "route_of_elimination": drug.get("route_of_elimination"),
                        "volume_of_distribution": drug.get("volume_of_distribution"),
                        "clearance": drug.get("clearance")
                    }
                    
            except httpx.HTTPError as e:
                logger.error(f"DrugBank API 오류: {e}")
                return {"error": f"API 요청 실패: {str(e)}"}
            except Exception as e:
                logger.error(f"예상치 못한 오류: {e}")
                return {"error": f"예상치 못한 오류: {str(e)}"}
        
        @self.server.call_tool()
        async def find_drugs_by_indication(indication: str, limit: int = 10) -> List[Dict[str, Any]]:
            """
            특정 적응증에 사용되는 약물 검색
            
            Args:
                indication: 적응증 (예: "cancer", "diabetes")
                limit: 반환할 최대 결과 수
            
            Returns:
                해당 적응증의 약물 리스트
            """
            try:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/drugs.json",
                        headers=headers,
                        params={"indication": indication, "limit": limit}
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # 결과 포맷팅
                    results = []
                    for drug in data.get("data", [])[:limit]:
                        results.append({
                            "drugbank_id": drug.get("id"),
                            "name": drug.get("name"),
                            "indication": drug.get("indication"),
                            "mechanism_of_action": drug.get("mechanism_of_action"),
                            "drug_type": drug.get("type"),
                            "groups": drug.get("groups", [])
                        })
                    
                    return results
                    
            except httpx.HTTPError as e:
                logger.error(f"DrugBank API 오류: {e}")
                return [{"error": f"API 요청 실패: {str(e)}"}]
            except Exception as e:
                logger.error(f"예상치 못한 오류: {e}")
                return [{"error": f"예상치 못한 오류: {str(e)}"}]
        
        @self.server.call_tool()
        async def get_drug_interactions(drugbank_id: str, limit: int = 20) -> List[Dict[str, Any]]:
            """
            약물 상호작용 정보 조회
            
            Args:
                drugbank_id: DrugBank ID
                limit: 반환할 최대 상호작용 수
            
            Returns:
                약물 상호작용 정보 리스트
            """
            try:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/drugs/{drugbank_id}/interactions.json",
                        headers=headers,
                        params={"limit": limit}
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # 상호작용 정보 포맷팅
                    interactions = []
                    for interaction in data.get("interactions", [])[:limit]:
                        interactions.append({
                            "interacting_drug": {
                                "drugbank_id": interaction.get("drugbank_id"),
                                "name": interaction.get("name")
                            },
                            "description": interaction.get("description"),
                            "severity": interaction.get("severity"),
                            "mechanism": interaction.get("mechanism")
                        })
                    
                    return interactions
                    
            except httpx.HTTPError as e:
                logger.error(f"DrugBank API 오류: {e}")
                return [{"error": f"API 요청 실패: {str(e)}"}]
            except Exception as e:
                logger.error(f"예상치 못한 오류: {e}")
                return [{"error": f"예상치 못한 오류: {str(e)}"}]
        
        @self.server.call_tool()
        async def find_drugs_by_target(target: str, limit: int = 10) -> List[Dict[str, Any]]:
            """
            특정 타겟에 작용하는 약물 검색
            
            Args:
                target: 타겟 단백질명 또는 유전자명
                limit: 반환할 최대 결과 수
            
            Returns:
                해당 타겟의 약물 리스트
            """
            try:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/drugs.json",
                        headers=headers,
                        params={"target": target, "limit": limit}
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # 결과 포맷팅
                    results = []
                    for drug in data.get("data", [])[:limit]:
                        results.append({
                            "drugbank_id": drug.get("id"),
                            "name": drug.get("name"),
                            "target_info": drug.get("targets", []),
                            "mechanism_of_action": drug.get("mechanism_of_action"),
                            "drug_type": drug.get("type"),
                            "groups": drug.get("groups", [])
                        })
                    
                    return results
                    
            except httpx.HTTPError as e:
                logger.error(f"DrugBank API 오류: {e}")
                return [{"error": f"API 요청 실패: {str(e)}"}]
            except Exception as e:
                logger.error(f"예상치 못한 오류: {e}")
                return [{"error": f"예상치 못한 오류: {str(e)}"}]

async def main():
    """DrugBank MCP 서버 실행"""
    logger.info("DrugBank MCP Server 시작...")
    
    # 서버 인스턴스 생성
    drugbank_server = DrugBankMCPServer()
    
    if MCP_AVAILABLE:
        # stdio를 통한 서버 실행
        async with stdio_server() as (read_stream, write_stream):
            await drugbank_server.server.run(
                read_stream,
                write_stream,
                drugbank_server.server.create_initialization_options()
            )
    else:
        logger.warning("MCP 라이브러리가 설치되지 않았습니다. 기본 모드로 실행합니다.")
        print("DrugBank MCP 서버가 기본 모드로 실행 중...")
        print("사용 가능한 툴:")
        for tool_name in drugbank_server.server._tools.keys():
            print(f"  - {tool_name}")
        
        # 간단한 대기 루프
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("서버를 종료합니다.")

if __name__ == "__main__":
    asyncio.run(main())