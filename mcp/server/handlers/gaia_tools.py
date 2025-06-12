"""
GAIA System Tools for MCP Server
"""

import asyncio
import sys
import os
from typing import Dict, Any, List

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from ..mcp_server import MCPServer
from ...protocol.messages import MCPTool


class GAIAToolsHandler:
    """Handler for GAIA system tools"""
    
    def __init__(self, server: MCPServer):
        self.server = server
        self._register_tools()
    
    def _register_tools(self):
        """Register all GAIA tools with the MCP server"""
        
        # Research Question Handler Tool
        research_tool = MCPTool(
            name="research_question",
            description="Research and generate comprehensive answers for questions",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The research question to investigate"
                    },
                    "depth": {
                        "type": "string",
                        "enum": ["basic", "detailed", "comprehensive"],
                        "description": "Research depth level",
                        "default": "detailed"
                    }
                },
                "required": ["question"]
            }
        )
        self.server.register_tool(research_tool, self.handle_research_question)
        
        # Answer Evaluation Tool
        evaluation_tool = MCPTool(
            name="evaluate_answer",
            description="Evaluate the quality and accuracy of an answer",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The original question"
                    },
                    "answer": {
                        "type": "string",
                        "description": "The answer to evaluate"
                    },
                    "criteria": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Evaluation criteria",
                        "default": ["accuracy", "completeness", "clarity"]
                    }
                },
                "required": ["question", "answer"]
            }
        )
        self.server.register_tool(evaluation_tool, self.handle_evaluate_answer)
        
        # File Storage Tool
        storage_tool = MCPTool(
            name="save_research",
            description="Save research results to file storage",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title for the research"
                    },
                    "content": {
                        "type": "string",
                        "description": "Research content to save"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["markdown", "json", "text"],
                        "description": "File format",
                        "default": "markdown"
                    }
                },
                "required": ["title", "content"]
            }
        )
        self.server.register_tool(storage_tool, self.handle_save_research)
        
        # ChEMBL 툴 추가
        chembl_molecule_tool = MCPTool(
            name="search_molecule",
            description="Search for molecules in ChEMBL database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Molecule name or identifier to search"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        )
        self.server.register_tool(chembl_molecule_tool, self.handle_search_molecule)
        
        # Sequential Thinking 툴 추가
        thinking_tool = MCPTool(
            name="start_thinking",
            description="Start sequential thinking process",
            inputSchema={
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "Problem to analyze"
                    },
                    "maxSteps": {
                        "type": "integer",
                        "description": "Maximum thinking steps",
                        "default": 10
                    }
                },
                "required": ["problem"]
            }
        )
        self.server.register_tool(thinking_tool, self.handle_start_thinking)
        
        # BiomCP 툴 추가
        search_articles_tool = MCPTool(
            name="search_articles",
            description="Search biomedical articles",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for articles"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        )
        self.server.register_tool(search_articles_tool, self.handle_search_articles)
    
    async def handle_research_question(self, question: str, depth: str = "detailed") -> str:
        """Handle research question requests"""
        try:
            # Import here to avoid circular imports
            from src.research.research_manager import ResearchManager
            
            research_manager = ResearchManager()
            result = await research_manager.research_question(question)
            
            return f"Research completed for: {question}\n\nResult: {result}"
            
        except Exception as e:
            return f"Error during research: {str(e)}"
    
    async def handle_evaluate_answer(self, question: str, answer: str, criteria: List[str] = None) -> str:
        """Handle answer evaluation requests"""
        try:
            # Import here to avoid circular imports
            from src.feedback.answer_evaluator import AnswerEvaluator
            
            if criteria is None:
                criteria = ["accuracy", "completeness", "clarity"]
            
            evaluator = AnswerEvaluator()
            result = await evaluator.evaluate_answer(question, answer, criteria)
            
            return f"Evaluation completed for question: {question}\n\nResult: {result}"
            
        except Exception as e:
            return f"Error during evaluation: {str(e)}"
    
    async def handle_save_research(self, title: str, content: str, format: str = "markdown") -> str:
        """Handle research saving requests"""
        try:
            # Import here to avoid circular imports
            from src.storage.file_storage import FileStorage
            
            storage = FileStorage()
            file_path = await storage.save_research(title, content, format)
            
            return f"Research saved successfully to: {file_path}"
            
        except Exception as e:
            return f"Error saving research: {str(e)}"
    
    async def handle_search_molecule(self, query: str, limit: int = 10) -> str:
        """Handle ChEMBL molecule search"""
        try:
            # 모의 ChEMBL 데이터 반환
            results = []
            for i in range(min(3, limit)):
                results.append({
                    "chembl_id": f"CHEMBL{1000 + i}",
                    "pref_name": f"{query} derivative {i+1}",
                    "molecular_formula": f"C{10+i}H{15+i*2}N{2}O{1}",
                    "max_phase": i + 1,
                    "molecule_type": "Small molecule"
                })
            
            response = f"ChEMBL 분자 검색 결과 ('{query}'):\n\n"
            for result in results:
                response += f"• {result['chembl_id']}: {result['pref_name']}\n"
                response += f"  분자식: {result['molecular_formula']}\n"
                response += f"  개발 단계: Phase {result['max_phase']}\n"
                response += f"  유형: {result['molecule_type']}\n\n"
            
            return response
            
        except Exception as e:
            return f"분자 검색 중 오류: {str(e)}"
    
    async def handle_start_thinking(self, problem: str, maxSteps: int = 10) -> str:
        """Handle sequential thinking start"""
        try:
            import uuid
            import json
            
            process_id = str(uuid.uuid4())[:8]
            
            response_data = {
                "processId": process_id,
                "problem": problem,
                "maxSteps": maxSteps,
                "currentStep": 1,
                "thinking": f"문제 '{problem}'을 분석하기 시작합니다. 최대 {maxSteps}단계로 진행할 예정입니다.",
                "nextThoughtNeeded": True
            }
            
            return json.dumps(response_data, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return f"Sequential thinking 시작 중 오류: {str(e)}"
    
    async def handle_search_articles(self, query: str, limit: int = 10) -> str:
        """Handle biomedical article search"""
        try:
            # 모의 PubMed 데이터 반환
            results = []
            years = [2023, 2022, 2024]
            journals = ["Nature", "Science", "Cell"]
            
            for i in range(min(3, limit)):
                results.append({
                    "pmid": f"{35000000 + i}",
                    "title": f"{query} and its effects on muscle growth: A clinical study {i+1}",
                    "authors": f"Smith J, Lee K, Johnson M",
                    "journal": journals[i % len(journals)],
                    "year": years[i % len(years)],
                    "abstract": f"This study investigates the effects of {query} on muscle development and athletic performance..."
                })
            
            response = f"생의학 논문 검색 결과 ('{query}'):\n\n"
            for result in results:
                response += f"• PMID: {result['pmid']}\n"
                response += f"  제목: {result['title']}\n"
                response += f"  저자: {result['authors']}\n"
                response += f"  저널: {result['journal']} ({result['year']})\n"
                response += f"  초록: {result['abstract']}\n\n"
            
            return response
            
        except Exception as e:
            return f"논문 검색 중 오류: {str(e)}"