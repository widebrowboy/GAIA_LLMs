"""
MCP Server Tests
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from mcp.server.mcp_server import MCPServer
from mcp.protocol.messages import MCPTool, MCPRequest, MCPResponse, MCPMethod


class TestMCPServer:
    """MCP Server test cases"""
    
    @pytest.fixture
    def server(self):
        """Create test server instance"""
        return MCPServer("Test-Server", "0.1.0")
    
    @pytest.fixture
    def sample_tool(self):
        """Create sample tool for testing"""
        return MCPTool(
            name="test_tool",
            description="A test tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"]
            }
        )
    
    def test_server_initialization(self, server):
        """Test server initialization"""
        assert server.name == "Test-Server"
        assert server.version == "0.1.0"
        assert not server.initialized
        assert len(server.tools) == 0
        assert len(server.tool_handlers) == 0
    
    def test_register_tool(self, server, sample_tool):
        """Test tool registration"""
        async def test_handler(message: str):
            return f"Received: {message}"
        
        server.register_tool(sample_tool, test_handler)
        
        assert "test_tool" in server.tools
        assert "test_tool" in server.tool_handlers
        assert server.tools["test_tool"] == sample_tool
    
    @pytest.mark.asyncio
    async def test_handle_initialize_request(self, server):
        """Test initialize request handling"""
        request_data = json.dumps({
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": "test-1",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "Test-Client", "version": "0.1.0"}
            }
        })
        
        response_json = await server.handle_request(request_data)
        response = json.loads(response_json)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "test-1"
        assert "result" in response
        assert response["result"]["protocolVersion"] == "2024-11-05"
        assert server.initialized
    
    @pytest.mark.asyncio
    async def test_handle_tools_list_request(self, server, sample_tool):
        """Test tools/list request handling"""
        # Register a tool first
        async def test_handler(message: str):
            return f"Received: {message}"
        
        server.register_tool(sample_tool, test_handler)
        server.initialized = True  # Set as initialized
        
        request_data = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "test-2"
        })
        
        response_json = await server.handle_request(request_data)
        response = json.loads(response_json)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "test-2"
        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) == 1
        assert response["result"]["tools"][0]["name"] == "test_tool"
    
    @pytest.mark.asyncio
    async def test_handle_tools_call_request(self, server, sample_tool):
        """Test tools/call request handling"""
        # Register a tool first
        async def test_handler(message: str):
            return f"Received: {message}"
        
        server.register_tool(sample_tool, test_handler)
        server.initialized = True  # Set as initialized
        
        request_data = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": "test-3",
            "params": {
                "name": "test_tool",
                "arguments": {"message": "Hello World"}
            }
        })
        
        response_json = await server.handle_request(request_data)
        response = json.loads(response_json)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "test-3"
        assert "result" in response
        assert "content" in response["result"]
        assert len(response["result"]["content"]) == 1
        assert response["result"]["content"][0]["text"] == "Received: Hello World"
    
    @pytest.mark.asyncio
    async def test_handle_ping_request(self, server):
        """Test ping request handling"""
        request_data = json.dumps({
            "jsonrpc": "2.0",
            "method": "ping",
            "id": "test-4"
        })
        
        response_json = await server.handle_request(request_data)
        response = json.loads(response_json)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "test-4"
        assert "result" in response
        assert response["result"]["status"] == "pong"
    
    @pytest.mark.asyncio
    async def test_handle_unknown_method(self, server):
        """Test unknown method handling"""
        request_data = json.dumps({
            "jsonrpc": "2.0",
            "method": "unknown_method",
            "id": "test-5"
        })
        
        response_json = await server.handle_request(request_data)
        response = json.loads(response_json)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "test-5"
        assert "error" in response
        assert response["error"]["code"] == -32601  # Method not found
    
    @pytest.mark.asyncio
    async def test_handle_invalid_json(self, server):
        """Test invalid JSON handling"""
        response_json = await server.handle_request("invalid json")
        response = json.loads(response_json)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "unknown"
        assert "error" in response
        assert response["error"]["code"] == -32700  # Parse error
    
    @pytest.mark.asyncio
    async def test_tools_call_without_initialization(self, server, sample_tool):
        """Test tools/call without initialization"""
        # Register a tool but don't initialize
        async def test_handler(message: str):
            return f"Received: {message}"
        
        server.register_tool(sample_tool, test_handler)
        
        request_data = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": "test-6",
            "params": {
                "name": "test_tool",
                "arguments": {"message": "Hello World"}
            }
        })
        
        response_json = await server.handle_request(request_data)
        response = json.loads(response_json)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "test-6"
        assert "error" in response
        assert "not initialized" in response["error"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_tools_call_nonexistent_tool(self, server):
        """Test calling nonexistent tool"""
        server.initialized = True
        
        request_data = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": "test-7",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {}
            }
        })
        
        response_json = await server.handle_request(request_data)
        response = json.loads(response_json)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "test-7"
        assert "error" in response
        assert "not found" in response["error"]["message"].lower()


if __name__ == "__main__":
    pytest.main([__file__])