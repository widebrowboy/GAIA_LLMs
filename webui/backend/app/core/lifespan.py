"""
FastAPI lifespan events
애플리케이션 시작/종료 시 실행되는 이벤트 처리
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from ..core.cli_adapter import cli_adapter

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    
    # 시작 시 실행
    logger.info("GAIA-BT WebUI API Server starting...")
    
    try:
        # CLI 어댑터 초기화
        success = await cli_adapter.initialize()
        if success:
            logger.info("CLI Adapter initialized successfully")
        else:
            logger.warning("CLI Adapter initialization failed - running in mock mode")
            
    except Exception as e:
        logger.error(f"Startup error: {e}")
        # Mock 모드로 계속 실행
    
    logger.info("GAIA-BT WebUI API Server started")
    
    yield
    
    # 종료 시 실행
    logger.info("GAIA-BT WebUI API Server shutting down...")
    
    try:
        # 세션 정리
        await cli_adapter.cleanup_inactive_sessions(timeout=0)
        logger.info("Sessions cleaned up")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
    
    logger.info("GAIA-BT WebUI API Server stopped")