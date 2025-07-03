"""
MCP Client Tests
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from mcp.client.mcp_client import MCPClient
from mcp.protocol.messages import MCPTool, MCPMethod


class TestMCPClient:
    """MCP Client test cases"""
    
    @pytest.fixture
    def client(self):
        """Create test client instance"""
        return MCPClient("Test-Client", "0.1.0")
    
    def test_client_initialization(self, client):
        """Test client initialization"""
        assert client.client_name == "Test-Client"
        assert client.client_version == "0.1.0"
        assert not client.initialized
        assert not client.connected
        assert len(client.available_tools) == 0
        assert client.server_info is None
    
    def test_generate_request_id(self, client):
        """Test request ID generation"""
        id1 = client._generate_request_id()
        id2 = client._generate_request_id()
        
        assert id1 != id2
        assert id1.startswith("req_1_")
        assert id2.startswith("req_2_")
    
    @pytest.mark.asyncio
    async def test_connect(self, client):
        """Test connection"""
        result = await client.connect()
        assert result is True
        assert client.connected is True
    
    @pytest.mark.asyncio
    async def test_disconnect(self, client):
        """Test disconnection"""
        # Connect first
        await client.connect()
        client.initialized = True
        client.available_tools = [MagicMock()]
        client.server_info = {"test": "info"}
        
        # Disconnect
        await client.disconnect()
        
        assert client.connected is False
        assert client.initialized is False
        assert len(client.available_tools) == 0
        assert client.server_info is None
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, client):
        """Test successful initialization"""
        # Mock the _send_request method
        with patch.object(client, '_send_request') as mock_send:
            mock_response = MagicMock()
            mock_response.error = None
            mock_response.result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": True}},
                "serverInfo": {"name": "Test-Server", "version": "0.1.0"}
            }
            mock_send.return_value = mock_response
            
            # Mock list_tools
            with patch.object(client, 'list_tools') as mock_list_tools:
                mock_list_tools.return_value = []
                
                result = await client.initialize()
                
                assert result is True
                assert client.initialized is True
                assert client.server_info is not None
    
    @pytest.mark.asyncio
    async def test_initialize_failure(self, client):
        """Test initialization failure"""
        # Mock the _send_request method to return error
        with patch.object(client, '_send_request') as mock_send:
            mock_response = MagicMock()
            mock_response.error = {"code": -32603, "message": "Internal error"}
            mock_response.result = None
            mock_send.return_value = mock_response
            
            result = await client.initialize()
            
            assert result is False
            assert client.initialized is False
    
    @pytest.mark.asyncio
    async def test_list_tools_success(self, client):
        """Test successful tools listing"""
        client.initialized = True
        
        # Mock the _send_request method
        with patch.object(client, '_send_request') as mock_send:
            mock_response = MagicMock()
            mock_response.error = None
            mock_response.result = {
                "tools": [
                    {
                        "name": "test_tool",
                        "description": "A test tool",
                        "inputSchema": {"type": "object"}
                    }
                ]
            }
            mock_send.return_value = mock_response
            
            tools = await client.list_tools()
            
            assert len(tools) == 1
            assert tools[0]["name"] == "test_tool"
            assert len(client.available_tools) == 1
            assert client.available_tools[0].name == "test_tool"
    
    @pytest.mark.asyncio
    async def test_list_tools_not_initialized(self, client):
        """Test tools listing when not initialized"""
        client.initialized = False
        
        with pytest.raises(RuntimeError, match="Client not initialized"):
            await client.list_tools()
    
    @pytest.mark.asyncio
    async def test_call_tool_success(self, client):
        """Test successful tool call"""
        client.initialized = True
        
        # Mock the _send_request method
        with patch.object(client, '_send_request') as mock_send:
            mock_response = MagicMock()
            mock_response.error = None
            mock_response.result = {
                "content": [
                    {
                        "type": "text",
                        "text": "Tool executed successfully"
                    }
                ]
            }
            mock_send.return_value = mock_response
            
            result = await client.call_tool("test_tool", {"arg1": "value1"})
            
            assert result["content"][0]["text"] == "Tool executed successfully"
    
    @pytest.mark.asyncio
    async def test_call_tool_not_initialized(self, client):
        """Test tool call when not initialized"""
        client.initialized = False
        
        with pytest.raises(RuntimeError, match="Client not initialized"):
            await client.call_tool("test_tool")
    
    @pytest.mark.asyncio
    async def test_call_tool_failure(self, client):
        """Test tool call failure"""
        client.initialized = True
        
        # Mock the _send_request method to return error
        with patch.object(client, '_send_request') as mock_send:
            mock_response = MagicMock()
            mock_response.error = {"code": -32601, "message": "Method not found"}
            mock_response.result = None
            mock_send.return_value = mock_response
            
            with pytest.raises(RuntimeError, match="Tool call failed"):
                await client.call_tool("nonexistent_tool")
    
    @pytest.mark.asyncio
    async def test_ping_success(self, client):
        """Test successful ping"""
        client.connected = True
        
        # Mock the _send_request method
        with patch.object(client, '_send_request') as mock_send:
            mock_response = MagicMock()
            mock_response.error = None
            mock_response.result = {"status": "pong"}
            mock_send.return_value = mock_response
            
            result = await client.ping()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_ping_not_connected(self, client):
        """Test ping when not connected"""
        client.connected = False
        
        result = await client.ping()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_ping_failure(self, client):
        """Test ping failure"""
        client.connected = True
        
        # Mock the _send_request method to return error
        with patch.object(client, '_send_request') as mock_send:
            mock_response = MagicMock()
            mock_response.error = {"code": -32603, "message": "Internal error"}
            mock_response.result = None
            mock_send.return_value = mock_response
            
            result = await client.ping()
            
            assert result is False
    
    def test_get_tool_by_name(self, client):
        """Test getting tool by name"""
        # Add a test tool
        test_tool = MCPTool(
            name="test_tool",
            description="A test tool",
            inputSchema={"type": "object"}
        )
        client.available_tools = [test_tool]
        
        # Test existing tool
        result = client.get_tool_by_name("test_tool")
        assert result == test_tool
        
        # Test non-existing tool
        result = client.get_tool_by_name("nonexistent_tool")
        assert result is None
    
    def test_get_available_tool_names(self, client):
        """Test getting available tool names"""
        # Add test tools
        tool1 = MCPTool("tool1", "Tool 1", {"type": "object"})
        tool2 = MCPTool("tool2", "Tool 2", {"type": "object"})
        client.available_tools = [tool1, tool2]
        
        names = client.get_available_tool_names()
        
        assert len(names) == 2
        assert "tool1" in names
        assert "tool2" in names


if __name__ == "__main__":
    pytest.main([__file__])