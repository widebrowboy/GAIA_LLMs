"""
MCP Router - MCP(Model Context Protocol) 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel

from app.api_server.dependencies import get_chatbot_service
from app.api_server.services.chatbot_service import ChatbotService

router = APIRouter()

class MCPCommand(BaseModel):
    """MCP 명령 모델"""
    command: str
    session_id: str = "default"

class MCPStatus(BaseModel):
    """MCP 상태 모델"""
    enabled: bool
    servers: List[Dict[str, Any]]
    show_output: bool

@router.get("/status", response_model=MCPStatus)
async def get_mcp_status(
    session_id: str = "default",
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """MCP 상태 조회"""
    try:
        chatbot = service.get_session(session_id)
        if not chatbot:
            # 세션이 없으면 기본값 반환
            return {
                "enabled": False,
                "servers": [],
                "show_output": False
            }
        
        servers = []
        if hasattr(chatbot, 'mcp_commands') and chatbot.mcp_commands:
            # MCP 서버 상태 확인
            for server_name in ["drugbank", "opentargets", "chembl", "biomcp", "sequential-thinking"]:
                try:
                    is_active = chatbot.mcp_commands.is_server_active(server_name)
                except:
                    is_active = False
                
                servers.append({
                    "name": server_name,
                    "active": is_active
                })
        else:
            # 기본 서버 목록 반환
            for server_name in ["drugbank", "opentargets", "chembl", "biomcp", "sequential-thinking"]:
                servers.append({
                    "name": server_name,
                    "active": False
                })
        
        return {
            "enabled": getattr(chatbot.config, 'mcp_enabled', False),
            "servers": servers,
            "show_output": getattr(chatbot.config, 'show_mcp_output', False)
        }
    except Exception as e:
        # 오류 발생 시 기본값 반환
        return {
            "enabled": False,
            "servers": [
                {"name": "drugbank", "active": False},
                {"name": "opentargets", "active": False},
                {"name": "chembl", "active": False},
                {"name": "biomcp", "active": False},
                {"name": "sequential-thinking", "active": False}
            ],
            "show_output": False
        }

@router.post("/start")
async def start_mcp(
    command: MCPCommand,
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """MCP 시작"""
    result = await service.process_command("/mcp start", command.session_id)
    return result

@router.post("/stop")
async def stop_mcp(
    command: MCPCommand,
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """MCP 중지"""
    result = await service.process_command("/mcp stop", command.session_id)
    return result

@router.post("/command")
async def execute_mcp_command(
    command: MCPCommand,
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """MCP 명령 실행"""
    full_command = f"/mcp {command.command}"
    result = await service.process_command(full_command, command.session_id)
    return result

@router.post("/toggle-output")
async def toggle_mcp_output(
    session_id: str = "default",
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """MCP 출력 표시 토글"""
    result = await service.process_command("/mcpshow", session_id)
    return result

@router.get("/servers")
async def get_available_servers() -> List[Dict[str, str]]:
    """사용 가능한 MCP 서버 목록"""
    return [
        {
            "name": "drugbank",
            "description": "약물 데이터베이스",
            "commands": ["search", "indication", "interaction"]
        },
        {
            "name": "opentargets",
            "description": "타겟-질병 연관성",
            "commands": ["targets", "diseases", "drugs"]
        },
        {
            "name": "chembl",
            "description": "화학 데이터베이스",
            "commands": ["molecule", "smiles"]
        },
        {
            "name": "biomcp",
            "description": "생의학 데이터베이스",
            "commands": ["bioarticle", "biotrial"]
        },
        {
            "name": "sequential-thinking",
            "description": "AI 추론",
            "commands": ["think"]
        }
    ]