"""
MCP Manager for GAIA System Integration
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
import json
import os
import subprocess

from ..client.mcp_client import MCPClient
from ..server.mcp_server import MCPServer
from .gaia_mcp_server import GAIAMCPServer


class MCPManager:
    """Manager for MCP client/server operations in GAIA system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.server: Optional[GAIAMCPServer] = None
        self.server_task: Optional[asyncio.Task] = None
        self.local_server = None
        self.clients: Dict[str, MCPClient] = {}
        self.external_servers: Dict[str, subprocess.Popen] = {}
        self.running = False
        self.mcp_config_path = "/home/gaia-bt/workspace/GAIA_LLMs/mcp.json"
    
    async def start_server(self, 
                          transport_type: str = "mock",  # 실제 전송 없이 로컬 서버만 초기화
                          host: str = "localhost", 
                          port: int = 8765) -> bool:
        """Start GAIA MCP server"""
        try:
            # 간단한 로컬 서버 생성 (전송 없이)
            from ..server.mcp_server import MCPServer
            from ..server.handlers.gaia_tools import GAIAToolsHandler
            
            # MCP 서버 생성 및 툴 등록
            local_server = MCPServer("GAIA-MCP-Server", "0.1.0")
            tools_handler = GAIAToolsHandler(local_server)
            
            # 서버를 인스턴스 변수에 저장
            self.local_server = local_server
            self.running = True
            
            self.logger.info("GAIA MCP Server initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start MCP server: {e}")
            return False
    
    async def stop_server(self):
        """Stop GAIA MCP server"""
        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass
            self.server_task = None
        
        if self.server:
            await self.server.stop()
            self.server = None
            
        if self.local_server:
            self.local_server = None
            
        self.running = False
        self.logger.info("GAIA MCP Server stopped")
    
    async def create_client(self, client_id: str, client_name: str = None):
        """Create and initialize MCP client"""
        if client_name is None:
            client_name = f"GAIA-Client-{client_id}"
        
        # "default" 클라이언트는 로컬 서버를 사용하므로 가짜 객체 생성
        if client_id == "default":
            class MockClient:
                def __init__(self, name):
                    self.name = name
                    
            self.clients[client_id] = MockClient(client_name)
            self.logger.info(f"Mock MCP client '{client_id}' created for local server")
            return self.clients[client_id]
        
        # 실제 외부 클라이언트 생성
        client = MCPClient(client_name)
        
        # Initialize client
        if await client.initialize():
            self.clients[client_id] = client
            self.logger.info(f"MCP client '{client_id}' created and initialized")
            return client
        else:
            raise RuntimeError(f"Failed to initialize MCP client '{client_id}'")
    
    async def remove_client(self, client_id: str):
        """Remove MCP client"""
        if client_id in self.clients:
            await self.clients[client_id].disconnect()
            del self.clients[client_id]
            self.logger.info(f"MCP client '{client_id}' removed")
    
    async def call_tool(self, 
                       client_id: str, 
                       tool_name: str, 
                       arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call tool using specific client"""
        # "default" 클라이언트인 경우 로컬 서버 사용
        if client_id == "default" and self.local_server:
            try:
                # 직접 툴 핸들러 호출
                if tool_name in self.local_server.tool_handlers:
                    handler = self.local_server.tool_handlers[tool_name]
                    result = await handler(**(arguments or {}))
                    
                    # MCP 응답 형식으로 래핑
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": str(result)
                            }
                        ]
                    }
                else:
                    # 로컬 서버에 없으면 외부 서버에서 찾기
                    return await self._find_and_call_tool(tool_name, arguments)
            except Exception as e:
                # 로컬 실행 실패시 외부 서버 시도
                try:
                    return await self._find_and_call_tool(tool_name, arguments)
                except:
                    raise RuntimeError(f"Tool execution failed: {e}")
        
        # 외부 클라이언트 사용
        if client_id not in self.clients:
            raise ValueError(f"Client '{client_id}' not found")
        
        client = self.clients[client_id]
        return await client.call_tool(tool_name, arguments)
    
    async def _find_and_call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Find tool in available servers and call it"""
        # ChEMBL 툴들
        chembl_tools = ['search_molecule', 'search_target', 'canonicalize_smiles']
        if tool_name in chembl_tools and 'chembl' in self.clients:
            client = self.clients['chembl']
            return await client.call_tool(tool_name, arguments)
        
        # BiomCP 툴들
        biomcp_tools = ['search_articles', 'search_trials', 'search_variants']
        if tool_name in biomcp_tools and 'biomcp' in self.clients:
            client = self.clients['biomcp']
            return await client.call_tool(tool_name, arguments)
        
        # Sequential Thinking 툴들
        thinking_tools = ['start_thinking', 'think', 'complete_thinking']
        if tool_name in thinking_tools and 'sequential-thinking' in self.clients:
            client = self.clients['sequential-thinking']
            return await client.call_tool(tool_name, arguments)
        
        # 모든 클라이언트에서 툴 찾기
        for client_id, client in self.clients.items():
            if hasattr(client, 'call_tool'):
                try:
                    return await client.call_tool(tool_name, arguments)
                except:
                    continue
        
        raise ValueError(f"Tool '{tool_name}' not found in any available server")
    
    async def list_tools(self, client_id: str) -> List[Dict[str, Any]]:
        """List available tools for specific client"""
        # "default" 클라이언트인 경우 로컬 서버 사용
        if client_id == "default" and self.local_server:
            return [tool.to_dict() for tool in self.local_server.tools.values()]
        
        # 외부 클라이언트 사용
        if client_id not in self.clients:
            raise ValueError(f"Client '{client_id}' not found")
        
        client = self.clients[client_id]
        return await client.list_tools()
    
    async def research_question(self, 
                               question: str, 
                               depth: str = "detailed",
                               client_id: str = "default") -> str:
        """Research a question using MCP tools"""
        try:
            # Ensure client exists
            if client_id not in self.clients:
                await self.create_client(client_id)
            
            # Call research tool
            result = await self.call_tool(
                client_id=client_id,
                tool_name="research_question",
                arguments={
                    "question": question,
                    "depth": depth
                }
            )
            
            # Extract text content from result
            content = result.get("content", [])
            if content and len(content) > 0:
                return content[0].get("text", "No result")
            else:
                return "No result returned"
                
        except Exception as e:
            self.logger.error(f"Error researching question: {e}")
            return f"Error: {str(e)}"
    
    async def evaluate_answer(self, 
                             question: str, 
                             answer: str,
                             criteria: List[str] = None,
                             client_id: str = "default") -> str:
        """Evaluate an answer using MCP tools"""
        try:
            # Ensure client exists
            if client_id not in self.clients:
                await self.create_client(client_id)
            
            # Call evaluation tool
            result = await self.call_tool(
                client_id=client_id,
                tool_name="evaluate_answer",
                arguments={
                    "question": question,
                    "answer": answer,
                    "criteria": criteria or ["accuracy", "completeness", "clarity"]
                }
            )
            
            # Extract text content from result
            content = result.get("content", [])
            if content and len(content) > 0:
                return content[0].get("text", "No result")
            else:
                return "No result returned"
                
        except Exception as e:
            self.logger.error(f"Error evaluating answer: {e}")
            return f"Error: {str(e)}"
    
    async def save_research(self, 
                           title: str, 
                           content: str,
                           format: str = "markdown",
                           client_id: str = "default") -> str:
        """Save research using MCP tools"""
        try:
            # Ensure client exists
            if client_id not in self.clients:
                await self.create_client(client_id)
            
            # Call save tool
            result = await self.call_tool(
                client_id=client_id,
                tool_name="save_research",
                arguments={
                    "title": title,
                    "content": content,
                    "format": format
                }
            )
            
            # Extract text content from result
            content = result.get("content", [])
            if content and len(content) > 0:
                return content[0].get("text", "No result")
            else:
                return "No result returned"
                
        except Exception as e:
            self.logger.error(f"Error saving research: {e}")
            return f"Error: {str(e)}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get MCP manager status"""
        server_info = None
        if self.local_server:
            server_info = {
                "name": self.local_server.name,
                "version": self.local_server.version,
                "tools_count": len(self.local_server.tools),
                "initialized": self.local_server.initialized
            }
        elif self.server:
            server_info = self.server.get_server_info()
            
        return {
            "running": self.running,
            "server_active": self.local_server is not None or self.server is not None,
            "clients_count": len(self.clients),
            "client_ids": list(self.clients.keys()),
            "server_info": server_info
        }
    
    async def cleanup(self):
        """Cleanup all resources"""
        # Disconnect all clients
        for client_id in list(self.clients.keys()):
            await self.remove_client(client_id)
        
        # Stop server
        await self.stop_server()
        
        self.logger.info("MCP Manager cleanup completed")
    
    async def start_external_servers(self, servers: List[str] = None):
        """Start external MCP servers (biomcp, sequential-thinking, etc.)"""
        try:
            # Load MCP configuration
            if not os.path.exists(self.mcp_config_path):
                self.logger.error("mcp.json not found")
                return False
            
            with open(self.mcp_config_path, 'r') as f:
                config = json.load(f)
            
            # Default to biomcp, chembl and sequential-thinking if not specified
            if servers is None:
                servers = ['biomcp', 'chembl', 'sequential-thinking']
            
            for server_name in servers:
                if server_name in config.get('mcpServers', {}):
                    server_config = config['mcpServers'][server_name]
                    
                    # Build command
                    cmd = [server_config['command']] + server_config.get('args', [])
                    
                    # Set environment
                    env = os.environ.copy()
                    if 'env' in server_config:
                        env.update(server_config['env'])
                    
                    # Set working directory
                    cwd = server_config.get('cwd', None)
                    
                    # Start server process
                    try:
                        process = subprocess.Popen(
                            cmd,
                            env=env,
                            cwd=cwd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE
                        )
                        
                        self.external_servers[server_name] = process
                        self.logger.info(f"Started external MCP server: {server_name}")
                        
                        # Give server time to initialize
                        await asyncio.sleep(2)
                        
                        # Create client for this server
                        await self.create_client(server_name, f"GAIA-{server_name}")
                        
                    except Exception as e:
                        self.logger.error(f"Failed to start {server_name}: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting external servers: {e}")
            return False
    
    async def stop_external_servers(self):
        """Stop all external MCP servers"""
        for server_name, process in self.external_servers.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                self.logger.info(f"Stopped external MCP server: {server_name}")
            except:
                process.kill()
                self.logger.warning(f"Force killed external MCP server: {server_name}")
        
        self.external_servers.clear()
    
    async def connect_to_mcp_server(self, server_name: str, server_config: Dict[str, Any]):
        """Connect to a specific MCP server"""
        try:
            # Create specialized client based on server type
            if server_name == 'biomcp':
                # BiomCP specific connection
                client = MCPClient(f"GAIA-{server_name}")
                # Configure for BiomCP
                await client.initialize()
                self.clients[server_name] = client
                
            elif server_name in ['sequential-thinking', 'gaia-sequential-thinking-python']:
                # Sequential Thinking specific connection
                client = MCPClient(f"GAIA-{server_name}")
                # Configure for Sequential Thinking
                await client.initialize()
                self.clients[server_name] = client
                
            else:
                # Generic MCP connection
                client = MCPClient(f"GAIA-{server_name}")
                await client.initialize()
                self.clients[server_name] = client
                
            self.logger.info(f"Connected to MCP server: {server_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {server_name}: {e}")
            return False