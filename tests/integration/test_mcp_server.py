#!/usr/bin/env python3
"""
Test script for GAIA MCP Server
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.mcp_server import MCPServer
from mcp.server.handlers.gaia_tools import GAIAToolsHandler


async def test_server():
    """Test server initialization and tool registration"""
    print("Testing GAIA MCP Server...")
    
    # Create server
    server = MCPServer("GAIA-Test-Server", "0.1.0")
    
    # Initialize tools handler
    tools_handler = GAIAToolsHandler(server)
    
    print(f"Server name: {server.name}")
    print(f"Server version: {server.version}")
    print(f"Registered tools: {len(server.tools)}")
    
    for tool_name, tool in server.tools.items():
        print(f"  - {tool_name}: {tool.description}")
    
    # Test server info response
    test_request = '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}}}'
    response = await server.handle_request(test_request)
    print(f"\nInitialize response: {response}")
    
    # Test tools list
    tools_request = '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}'
    response = await server.handle_request(tools_request)
    print(f"\nTools list response: {response}")
    
    print("\n✅ MCP Server test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_server())