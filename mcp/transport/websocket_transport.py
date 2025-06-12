"""
WebSocket Transport for MCP
"""

import asyncio
import json
import logging
from typing import Callable, Optional, Dict, Any
import websockets
from websockets.server import WebSocketServerProtocol
from websockets.client import WebSocketClientProtocol


class WebSocketTransport:
    """WebSocket transport for MCP communication"""
    
    def __init__(self, message_handler: Callable[[str], str] = None):
        self.message_handler = message_handler
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.websocket: Optional[WebSocketServerProtocol] = None
        self.server = None
    
    async def start_server(self, host: str = "localhost", port: int = 8765):
        """Start WebSocket server"""
        self.running = True
        self.logger.info(f"Starting WebSocket server on {host}:{port}")
        
        self.server = await websockets.serve(
            self._handle_client,
            host,
            port
        )
        
        self.logger.info(f"WebSocket server started on {host}:{port}")
    
    async def start_client(self, uri: str):
        """Start WebSocket client"""
        self.running = True
        self.logger.info(f"Connecting to WebSocket server at {uri}")
        
        try:
            self.websocket = await websockets.connect(uri)
            self.logger.info(f"Connected to WebSocket server at {uri}")
            
            # Start message processing loop
            await self._client_message_loop()
            
        except Exception as e:
            self.logger.error(f"Failed to connect to WebSocket server: {e}")
            raise
    
    async def stop(self):
        """Stop the WebSocket transport"""
        self.running = False
        
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
        
        self.logger.info("WebSocket transport stopped")
    
    async def send_message(self, message: str):
        """Send a message via WebSocket"""
        if not self.websocket:
            raise RuntimeError("WebSocket not connected")
        
        await self.websocket.send(message)
        self.logger.debug(f"Sent message: {message}")
    
    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle incoming WebSocket client connection"""
        self.websocket = websocket
        self.logger.info(f"Client connected: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                if not self.running:
                    break
                
                self.logger.debug(f"Received message: {message}")
                
                # Process message if handler is available
                if self.message_handler:
                    try:
                        response = await self.message_handler(message)
                        if response:
                            await websocket.send(response)
                    except Exception as e:
                        self.logger.error(f"Error processing message: {e}")
                        # Send error response
                        error_response = {
                            "jsonrpc": "2.0",
                            "id": None,
                            "error": {
                                "code": -32603,
                                "message": f"Internal error: {str(e)}"
                            }
                        }
                        await websocket.send(json.dumps(error_response))
                        
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("Client disconnected")
        except Exception as e:
            self.logger.error(f"Error handling client: {e}")
        finally:
            self.websocket = None
    
    async def _client_message_loop(self):
        """Message processing loop for client mode"""
        try:
            async for message in self.websocket:
                if not self.running:
                    break
                
                self.logger.debug(f"Received message: {message}")
                
                # Process message if handler is available
                if self.message_handler:
                    try:
                        response = await self.message_handler(message)
                        if response:
                            await self.websocket.send(response)
                    except Exception as e:
                        self.logger.error(f"Error processing message: {e}")
                        
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("Connection closed")
        except Exception as e:
            self.logger.error(f"Error in client message loop: {e}")
        finally:
            self.running = False