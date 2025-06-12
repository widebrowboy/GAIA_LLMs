#!/usr/bin/env python3
"""
GAIA MCP Server Runner

Script to run the GAIA MCP server with different transport options.
"""

import asyncio
import argparse
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from integration.gaia_mcp_server import GAIAMCPServer


async def main():
    """Main function to run GAIA MCP server"""
    parser = argparse.ArgumentParser(description="GAIA MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "websocket"],
        default="stdio",
        help="Transport type (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for websocket server (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port for websocket server (default: 8765)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level (default: INFO)"
    )
    parser.add_argument(
        "--name",
        default="GAIA-MCP-Server",
        help="Server name (default: GAIA-MCP-Server)"
    )
    parser.add_argument(
        "--version",
        default="0.1.0",
        help="Server version (default: 0.1.0)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Create and start server
        server = GAIAMCPServer(
            name=args.name,
            version=args.version,
            transport_type=args.transport
        )
        
        logger.info(f"Starting GAIA MCP Server '{args.name}' v{args.version}")
        logger.info(f"Transport: {args.transport}")
        
        if args.transport == "websocket":
            logger.info(f"WebSocket server will run on {args.host}:{args.port}")
        
        # Start server
        await server.start(args.host, args.port)
        
        # Keep running until interrupted
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        
    except Exception as e:
        logger.error(f"Error running server: {e}")
        return 1
    
    finally:
        # Cleanup
        try:
            await server.stop()
            logger.info("Server stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping server: {e}")
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))