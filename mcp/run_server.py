#!/usr/bin/env python3
"""
GAIA MCP 서버 실행 스크립트
"""

import asyncio
import logging
import argparse
from rich.logging import RichHandler

from .integration.gaia_mcp_server import GAIAMCPServer

async def main():
    parser = argparse.ArgumentParser(description="GAIA MCP 서버 실행")
    parser.add_argument("--transport", choices=["stdio", "websocket"], default="stdio",
                      help="서버 전송 방식 (stdio 또는 websocket)")
    parser.add_argument("--host", default="localhost",
                      help="웹소켓 서버 호스트 (websocket 전송 방식일 때만 사용)")
    parser.add_argument("--port", type=int, default=8765,
                      help="웹소켓 서버 포트 (websocket 전송 방식일 때만 사용)")
    parser.add_argument("--log-level", default="INFO",
                      choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      help="로그 레벨")
    parser.add_argument("--server-name", default="GAIA-MCP",
                      help="서버 이름")
    parser.add_argument("--version", default="0.1.0",
                      help="서버 버전")
    
    args = parser.parse_args()
    
    # 로깅 설정
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    
    logger = logging.getLogger("mcp-server")
    logger.info(f"Starting {args.server_name} v{args.version}")
    
    try:
        # 서버 시작
        server = GAIAMCPServer(
            name=args.server_name,
            version=args.version,
            transport_type=args.transport
        )
        
        # 서버 시작
        await server.start(args.host, args.port)
        
        # 클라이언트 연결 대기
        if args.transport == "websocket":
            logger.info(f"Server running on ws://{args.host}:{args.port}")
        else:
            logger.info("Server running in stdio mode")
            
        # 무한 대기
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        if 'server' in locals():
            await server.stop()

if __name__ == "__main__":
    asyncio.run(main())