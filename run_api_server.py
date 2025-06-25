#!/usr/bin/env python3
"""
GAIA-BT API Server 실행 스크립트
FastAPI 기반 RESTful API 서버
"""

import sys
import os
import signal
import psutil
import subprocess
import asyncio
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def kill_existing_process(port):
    """지정된 포트를 사용하는 기존 프로세스 종료"""
    try:
        # lsof를 사용하여 포트를 사용하는 프로세스 찾기
        result = subprocess.run(
            ['lsof', '-t', f'-i:{port}'],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"✅ 기존 프로세스 (PID: {pid})를 종료했습니다.")
                except:
                    pass
            
            # 프로세스가 완전히 종료될 때까지 잠시 대기
            import time
            time.sleep(1)
    except:
        # lsof가 없는 경우 psutil 사용
        for conn in psutil.net_connections():
            if conn.laddr and conn.laddr.port == port:
                try:
                    process = psutil.Process(conn.pid)
                    process.terminate()
                    print(f"✅ 기존 프로세스 (PID: {conn.pid})를 종료했습니다.")
                except:
                    pass

async def ensure_ollama_model():
    """Ollama 모델이 실행 중인지 확인하고 필요시 시작"""
    from app.utils.ollama_manager import ensure_single_model_running
    
    model_name = "gemma3-12b:latest"
    print(f"🤖 Ollama 모델 '{model_name}' 상태 확인 중...")
    
    try:
        await ensure_single_model_running(model_name)
        print(f"✅ Ollama 모델 '{model_name}'이 실행 중입니다.")
    except Exception as e:
        print(f"⚠️  Ollama 모델 시작 실패: {e}")
        print("   API 서버는 계속 실행되지만 AI 응답이 제한될 수 있습니다.")

def main():
    """API 서버 실행"""
    try:
        import uvicorn
        from app.api_server.main import app
        
        # 기존 프로세스 종료
        print("🔍 포트 8000에서 실행 중인 기존 프로세스 확인 중...")
        kill_existing_process(8000)
        
        # Ollama 모델 확인 및 시작
        asyncio.run(ensure_ollama_model())
        
        print("\n🚀 GAIA-BT API Server 시작 중...")
        print("📍 API 주소: http://localhost:8000")
        print("📖 API 문서: http://localhost:8000/docs")
        print("🔌 WebSocket: ws://localhost:8000/ws/{session_id}")
        print("\n종료하려면 Ctrl+C를 누르세요.\n")
        
        # Uvicorn 서버 실행
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            
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