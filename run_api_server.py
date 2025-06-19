#!/usr/bin/env python3
"""
GAIA-BT API Server 실행 스크립트
FastAPI 기반 RESTful API 서버
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def main():
    """API 서버 실행"""
    try:
        import uvicorn
        from app.api_server.main import app
        
        print("🚀 GAIA-BT API Server 시작 중...")
        print("📍 API 주소: http://localhost:8000")
        print("📖 API 문서: http://localhost:8000/docs")
        print("🔌 WebSocket: ws://localhost:8000/ws/{session_id}")
        print("\n종료하려면 Ctrl+C를 누르세요.\n")
        
        # Uvicorn 서버 실행
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ 필요한 패키지가 설치되지 않았습니다: {e}")
        print("다음 명령어로 설치하세요:")
        print("pip install fastapi uvicorn websockets")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 API 서버를 종료합니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()