"""
GAIA MCP Server Integration
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from ..server.mcp_server import MCPServer
from ..server.handlers.gaia_tools import GAIAToolsHandler
from ..transport.stdio_transport import StdioTransport
from ..transport.websocket_transport import WebSocketTransport


class GAIAMCPServer:
    """GAIA-integrated MCP Server"""
    
    def __init__(self, 
                 name: str = "GAIA-MCP-Server",
                 version: str = "0.1.0",
                 transport_type: str = "stdio"):
        self.server = MCPServer(name, version)
        self.transport_type = transport_type
        self.transport = None
        self.tools_handler = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize tools handler
        self.tools_handler = GAIAToolsHandler(self.server)
    
    async def start(self, host: str = "localhost", port: int = 8765):
        """Start the GAIA MCP server"""
        self.logger.info(f"Starting GAIA MCP Server with {self.transport_type} transport")
        
        # Initialize transport
        if self.transport_type == "stdio":
            self.transport = StdioTransport(self.server.handle_request)
            await self.transport.start()
        elif self.transport_type == "websocket":
            self.transport = WebSocketTransport(self.server.handle_request)
            await self.transport.start_server(host, port)
        else:
            raise ValueError(f"Unsupported transport type: {self.transport_type}")
    
    async def stop(self):
        """Stop the GAIA MCP server"""
        if self.transport:
            await self.transport.stop()
        self.logger.info("GAIA MCP Server stopped")
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "name": self.server.name,
            "version": self.server.version,
            "transport": self.transport_type,
            "tools_count": len(self.server.tools),
            "initialized": self.server.initialized
        }
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get available tools information"""
        return {
            tool_name: {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool_name, tool in self.server.tools.items()
        }