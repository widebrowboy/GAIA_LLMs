"""
MCP Server Implementation
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Callable, Optional, Union
from dataclasses import asdict

from ..protocol.messages import (
    MCPRequest, MCPResponse, MCPNotification, MCPError, MCPErrorCode,
    MCPTool, MCPMethod
)


class MCPServer:
    def __init__(self, name: str = "GAIA-MCP-Server", version: str = "0.1.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}
        self.tool_handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)
        self.initialized = False
        
    def register_tool(self, tool: MCPTool, handler: Callable):
        """Register a tool with its handler function"""
        self.tools[tool.name] = tool
        self.tool_handlers[tool.name] = handler
        self.logger.info(f"Registered tool: {tool.name}")
    
    async def handle_request(self, request_data: str) -> str:
        """Handle incoming MCP requests"""
        try:
            request_dict = json.loads(request_data)
            request = MCPRequest(**request_dict)
            
            if request.method == MCPMethod.INITIALIZE.value:
                response = await self._handle_initialize(request)
            elif request.method == MCPMethod.TOOLS_LIST.value:
                response = await self._handle_tools_list(request)
            elif request.method == MCPMethod.TOOLS_CALL.value:
                response = await self._handle_tools_call(request)
            elif request.method == MCPMethod.PING.value:
                response = await self._handle_ping(request)
            else:
                response = MCPResponse(
                    id=request.id,
                    error=MCPError(
                        code=MCPErrorCode.METHOD_NOT_FOUND.value,
                        message=f"Method not found: {request.method}"
                    ).to_dict()
                )
                
            return response.to_json()
            
        except json.JSONDecodeError:
            error_response = MCPResponse(
                id="unknown",
                error=MCPError(
                    code=MCPErrorCode.PARSE_ERROR.value,
                    message="Invalid JSON"
                ).to_dict()
            )
            return error_response.to_json()
            
        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            error_response = MCPResponse(
                id=getattr(request, 'id', 'unknown'),
                error=MCPError(
                    code=MCPErrorCode.INTERNAL_ERROR.value,
                    message=str(e)
                ).to_dict()
            )
            return error_response.to_json()
    
    async def _handle_initialize(self, request: MCPRequest) -> MCPResponse:
        """Handle initialize request"""
        self.initialized = True
        return MCPResponse(
            id=request.id,
            result={
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    }
                },
                "serverInfo": {
                    "name": self.name,
                    "version": self.version
                }
            }
        )
    
    async def _handle_tools_list(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/list request"""
        if not self.initialized:
            return MCPResponse(
                id=request.id,
                error=MCPError(
                    code=MCPErrorCode.SERVER_ERROR_START.value,
                    message="Server not initialized"
                ).to_dict()
            )
        
        tools_list = [tool.to_dict() for tool in self.tools.values()]
        return MCPResponse(
            id=request.id,
            result={"tools": tools_list}
        )
    
    async def _handle_tools_call(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/call request"""
        if not self.initialized:
            return MCPResponse(
                id=request.id,
                error=MCPError(
                    code=MCPErrorCode.SERVER_ERROR_START.value,
                    message="Server not initialized"
                ).to_dict()
            )
        
        if not request.params or "name" not in request.params:
            return MCPResponse(
                id=request.id,
                error=MCPError(
                    code=MCPErrorCode.INVALID_PARAMS.value,
                    message="Missing tool name"
                ).to_dict()
            )
        
        tool_name = request.params["name"]
        if tool_name not in self.tool_handlers:
            return MCPResponse(
                id=request.id,
                error=MCPError(
                    code=MCPErrorCode.METHOD_NOT_FOUND.value,
                    message=f"Tool not found: {tool_name}"
                ).to_dict()
            )
        
        try:
            handler = self.tool_handlers[tool_name]
            arguments = request.params.get("arguments", {})
            result = await handler(**arguments)
            
            return MCPResponse(
                id=request.id,
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": str(result)
                        }
                    ]
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            return MCPResponse(
                id=request.id,
                error=MCPError(
                    code=MCPErrorCode.INTERNAL_ERROR.value,
                    message=f"Tool execution failed: {str(e)}"
                ).to_dict()
            )
    
    async def _handle_ping(self, request: MCPRequest) -> MCPResponse:
        """Handle ping request"""
        return MCPResponse(
            id=request.id,
            result={"status": "pong"}
        )