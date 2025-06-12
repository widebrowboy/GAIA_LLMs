"""
STDIO Transport for MCP
"""

import asyncio
import json
import logging
import sys
from typing import Callable, Optional, Dict, Any


class StdioTransport:
    """STDIO transport for MCP communication"""
    
    def __init__(self, message_handler: Callable[[str], str] = None):
        self.message_handler = message_handler
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.reader = None
        self.writer = None
    
    async def start(self):
        """Start the STDIO transport"""
        self.running = True
        self.logger.info("Starting STDIO transport")
        
        # Create reader/writer for stdin/stdout using modern asyncio approach
        loop = asyncio.get_event_loop()
        
        # Create stdin reader
        self.reader = asyncio.StreamReader()
        reader_protocol = asyncio.StreamReaderProtocol(self.reader)
        await loop.connect_read_pipe(lambda: reader_protocol, sys.stdin)
        
        # Create stdout writer using connect_write_pipe
        transport, protocol = await loop.connect_write_pipe(
            lambda: asyncio.Protocol(), sys.stdout
        )
        self.writer = asyncio.StreamWriter(transport, protocol, None, loop)
        
        # Start message processing loop
        await self._message_loop()
    
    async def stop(self):
        """Stop the STDIO transport"""
        self.running = False
        self.logger.info("Stopping STDIO transport")
    
    async def send_message(self, message: str):
        """Send a message via STDIO"""
        if not self.writer:
            raise RuntimeError("Transport not started")
        
        # Send message with newline delimiter
        self.writer.write(f"{message}\n".encode())
        await self.writer.drain()
        self.logger.debug(f"Sent message: {message}")
    
    async def _message_loop(self):
        """Main message processing loop"""
        while self.running:
            try:
                # Read message from stdin
                line = await self.reader.readline()
                if not line:
                    break
                
                message = line.decode().strip()
                if not message:
                    continue
                
                self.logger.debug(f"Received message: {message}")
                
                # Process message if handler is available
                if self.message_handler:
                    try:
                        response = await self.message_handler(message)
                        if response:
                            await self.send_message(response)
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
                        await self.send_message(json.dumps(error_response))
                        
            except Exception as e:
                self.logger.error(f"Error in message loop: {e}")
                break
        
        self.logger.info("Message loop ended")