"""
MCP Integration Tests
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from mcp.integration.mcp_manager import MCPManager
from mcp.integration.gaia_mcp_server import GAIAMCPServer


class TestMCPIntegration:
    """MCP Integration test cases"""
    
    @pytest.fixture
    def mcp_manager(self):
        """Create test MCP manager instance"""
        return MCPManager()
    
    @pytest.fixture
    def gaia_server(self):
        """Create test GAIA MCP server instance"""
        return GAIAMCPServer("Test-GAIA-Server", "0.1.0", "stdio")
    
    def test_mcp_manager_initialization(self, mcp_manager):
        """Test MCP manager initialization"""
        assert mcp_manager.server is None
        assert len(mcp_manager.clients) == 0
        assert not mcp_manager.running
    
    def test_gaia_server_initialization(self, gaia_server):
        """Test GAIA MCP server initialization"""
        assert gaia_server.server.name == "Test-GAIA-Server"
        assert gaia_server.server.version == "0.1.0"
        assert gaia_server.transport_type == "stdio"
        assert gaia_server.tools_handler is not None
    
    def test_gaia_server_info(self, gaia_server):
        """Test GAIA server info"""
        info = gaia_server.get_server_info()
        
        assert info["name"] == "Test-GAIA-Server"
        assert info["version"] == "0.1.0"
        assert info["transport"] == "stdio"
        assert "tools_count" in info
        assert "initialized" in info
    
    def test_gaia_server_available_tools(self, gaia_server):
        """Test GAIA server available tools"""
        tools = gaia_server.get_available_tools()
        
        # Should have GAIA tools registered
        assert len(tools) > 0
        assert "research_question" in tools
        assert "evaluate_answer" in tools
        assert "save_research" in tools
    
    @pytest.mark.asyncio
    async def test_mcp_manager_server_lifecycle(self, mcp_manager):
        """Test MCP manager server start/stop lifecycle"""
        # Mock the GAIAMCPServer
        with patch('mcp.integration.mcp_manager.GAIAMCPServer') as mock_server_class:
            mock_server = AsyncMock()
            mock_server_class.return_value = mock_server
            
            # Test start server
            result = await mcp_manager.start_server()
            assert result is True
            assert mcp_manager.running is True
            assert mcp_manager.server is not None
            mock_server.start.assert_called_once()
            
            # Test stop server
            await mcp_manager.stop_server()
            assert mcp_manager.running is False
            assert mcp_manager.server is None
            mock_server.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mcp_manager_client_lifecycle(self, mcp_manager):
        """Test MCP manager client create/remove lifecycle"""
        # Mock the MCPClient
        with patch('mcp.integration.mcp_manager.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.initialize.return_value = True
            mock_client_class.return_value = mock_client
            
            # Test create client
            client = await mcp_manager.create_client("test_client")
            assert client is not None
            assert "test_client" in mcp_manager.clients
            mock_client.initialize.assert_called_once()
            
            # Test remove client
            await mcp_manager.remove_client("test_client")
            assert "test_client" not in mcp_manager.clients
            mock_client.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mcp_manager_client_creation_failure(self, mcp_manager):
        """Test MCP manager client creation failure"""
        # Mock the MCPClient to fail initialization
        with patch('mcp.integration.mcp_manager.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.initialize.return_value = False
            mock_client_class.return_value = mock_client
            
            # Test create client failure
            with pytest.raises(RuntimeError, match="Failed to initialize"):
                await mcp_manager.create_client("test_client")
    
    @pytest.mark.asyncio
    async def test_mcp_manager_tool_operations(self, mcp_manager):
        """Test MCP manager tool operations"""
        # Mock client
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"result": "success"}
        mock_client.list_tools.return_value = [{"name": "test_tool"}]
        mcp_manager.clients["test_client"] = mock_client
        
        # Test call tool
        result = await mcp_manager.call_tool("test_client", "test_tool", {"arg": "value"})
        assert result["result"] == "success"
        mock_client.call_tool.assert_called_once_with("test_tool", {"arg": "value"})
        
        # Test list tools
        tools = await mcp_manager.list_tools("test_client")
        assert len(tools) == 1
        assert tools[0]["name"] == "test_tool"
        mock_client.list_tools.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mcp_manager_tool_operations_no_client(self, mcp_manager):
        """Test MCP manager tool operations with non-existent client"""
        # Test call tool with non-existent client
        with pytest.raises(ValueError, match="Client 'nonexistent' not found"):
            await mcp_manager.call_tool("nonexistent", "test_tool")
        
        # Test list tools with non-existent client
        with pytest.raises(ValueError, match="Client 'nonexistent' not found"):
            await mcp_manager.list_tools("nonexistent")
    
    @pytest.mark.asyncio
    async def test_mcp_manager_research_question(self, mcp_manager):
        """Test MCP manager research question"""
        # Mock client
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {
            "content": [{"text": "Research result"}]
        }
        
        # Mock create_client
        with patch.object(mcp_manager, 'create_client', return_value=mock_client):
            with patch.object(mcp_manager, 'call_tool') as mock_call_tool:
                mock_call_tool.return_value = {
                    "content": [{"text": "Research result"}]
                }
                
                result = await mcp_manager.research_question("What is AI?")
                assert result == "Research result"
    
    @pytest.mark.asyncio
    async def test_mcp_manager_evaluate_answer(self, mcp_manager):
        """Test MCP manager evaluate answer"""
        # Mock client
        mock_client = AsyncMock()
        
        # Mock create_client and call_tool
        with patch.object(mcp_manager, 'create_client', return_value=mock_client):
            with patch.object(mcp_manager, 'call_tool') as mock_call_tool:
                mock_call_tool.return_value = {
                    "content": [{"text": "Evaluation result"}]
                }
                
                result = await mcp_manager.evaluate_answer("Question?", "Answer")
                assert result == "Evaluation result"
    
    @pytest.mark.asyncio
    async def test_mcp_manager_save_research(self, mcp_manager):
        """Test MCP manager save research"""
        # Mock client
        mock_client = AsyncMock()
        
        # Mock create_client and call_tool
        with patch.object(mcp_manager, 'create_client', return_value=mock_client):
            with patch.object(mcp_manager, 'call_tool') as mock_call_tool:
                mock_call_tool.return_value = {
                    "content": [{"text": "Saved to file.md"}]
                }
                
                result = await mcp_manager.save_research("Title", "Content")
                assert result == "Saved to file.md"
    
    def test_mcp_manager_status(self, mcp_manager):
        """Test MCP manager status"""
        status = mcp_manager.get_status()
        
        assert "running" in status
        assert "server_active" in status
        assert "clients_count" in status
        assert "client_ids" in status
        assert "server_info" in status
        
        assert status["running"] is False
        assert status["server_active"] is False
        assert status["clients_count"] == 0
        assert status["client_ids"] == []
        assert status["server_info"] is None
    
    @pytest.mark.asyncio
    async def test_mcp_manager_cleanup(self, mcp_manager):
        """Test MCP manager cleanup"""
        # Add mock clients
        mock_client1 = AsyncMock()
        mock_client2 = AsyncMock()
        mcp_manager.clients["client1"] = mock_client1
        mcp_manager.clients["client2"] = mock_client2
        
        # Mock server
        mock_server = AsyncMock()
        mcp_manager.server = mock_server
        mcp_manager.running = True
        
        # Test cleanup
        with patch.object(mcp_manager, 'remove_client') as mock_remove:
            with patch.object(mcp_manager, 'stop_server') as mock_stop:
                await mcp_manager.cleanup()
                
                # Should remove all clients
                assert mock_remove.call_count == 2
                mock_stop.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])