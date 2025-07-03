#!/usr/bin/env python3
"""
API 서버와 Ollama 연결 테스트 스크립트
"""

import asyncio
import httpx
import json
from datetime import datetime

# 색상 코드
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

async def test_direct_ollama():
    """Ollama API 직접 테스트"""
    print(f"\n{BLUE}=== Ollama API 직접 테스트 ==={RESET}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. API 상태 확인
            response = await client.get("http://localhost:11434/api/tags")
            print(f"{GREEN}✓ Ollama API 연결 성공{RESET}")
            models = response.json().get("models", [])
            print(f"  설치된 모델: {len(models)}개")
            for model in models:
                print(f"  - {model['name']} ({model['size'] / 1e9:.1f}GB)")
            
            # 2. 텍스트 생성 테스트
            print(f"\n{YELLOW}텍스트 생성 테스트 중...{RESET}")
            start_time = datetime.now()
            
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "Gemma3:27b-it-q4_K_M",
                    "prompt": "아스피린의 작용 메커니즘을 간단히 설명해주세요.",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 200
                    }
                }
            )
            
            end_time = datetime.now()
            elapsed = (end_time - start_time).total_seconds()
            
            result = response.json()
            print(f"{GREEN}✓ 텍스트 생성 성공{RESET} (소요시간: {elapsed:.2f}초)")
            print(f"  응답 길이: {len(result.get('response', ''))} 문자")
            print(f"  응답 일부: {result.get('response', '')[:100]}...")
            
    except Exception as e:
        print(f"{RED}✗ Ollama API 오류: {e}{RESET}")
        return False
    
    return True

async def test_api_server():
    """GAIA-BT API 서버 테스트"""
    print(f"\n{BLUE}=== GAIA-BT API 서버 테스트 ==={RESET}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 1. 헬스 체크
            response = await client.get("http://localhost:8000/health")
            print(f"{GREEN}✓ API 서버 연결 성공{RESET}")
            health = response.json()
            print(f"  상태: {health.get('status')}")
            print(f"  시간: {health.get('timestamp')}")
            
            # 2. 시스템 정보 확인
            response = await client.get("http://localhost:8000/api/system/info")
            info = response.json()
            print(f"\n{GREEN}✓ 시스템 정보{RESET}")
            print(f"  현재 모델: {info.get('current_model')}")
            print(f"  현재 모드: {info.get('current_mode')}")
            print(f"  디버그 모드: {info.get('debug_mode')}")
            
            # 3. 채팅 메시지 테스트
            print(f"\n{YELLOW}채팅 메시지 테스트 중...{RESET}")
            start_time = datetime.now()
            
            response = await client.post(
                "http://localhost:8000/api/chat/message",
                json={
                    "message": "아스피린의 작용 메커니즘을 간단히 설명해주세요.",
                    "session_id": "default"
                }
            )
            
            end_time = datetime.now()
            elapsed = (end_time - start_time).total_seconds()
            
            if response.status_code == 200:
                result = response.json()
                print(f"{GREEN}✓ 채팅 응답 성공{RESET} (소요시간: {elapsed:.2f}초)")
                print(f"  응답 길이: {len(result.get('response', ''))} 문자")
                print(f"  모드: {result.get('mode')}")
                print(f"  모델: {result.get('model')}")
                print(f"  응답 일부: {result.get('response', '')[:100]}...")
            else:
                print(f"{RED}✗ 채팅 응답 실패: {response.status_code}{RESET}")
                print(f"  오류: {response.text}")
            
    except httpx.ConnectError:
        print(f"{RED}✗ API 서버에 연결할 수 없습니다.{RESET}")
        print(f"  서버가 실행 중인지 확인하세요: python run_api_server.py")
        return False
    except Exception as e:
        print(f"{RED}✗ API 서버 오류: {e}{RESET}")
        return False
    
    return True

async def test_ollama_client():
    """OllamaClient 클래스 직접 테스트"""
    print(f"\n{BLUE}=== OllamaClient 클래스 테스트 ==={RESET}")
    
    try:
        from app.api.ollama_client import OllamaClient
        
        # 클라이언트 생성
        client = OllamaClient(
            model="Gemma3:27b-it-q4_K_M",
            debug_mode=True
        )
        
        # 가용성 확인
        available = await client.check_availability()
        if available:
            print(f"{GREEN}✓ OllamaClient 초기화 성공{RESET}")
        else:
            print(f"{RED}✗ OllamaClient 초기화 실패{RESET}")
            return False
        
        # 텍스트 생성 테스트
        print(f"\n{YELLOW}OllamaClient 생성 테스트 중...{RESET}")
        start_time = datetime.now()
        
        response = await client.generate(
            prompt="아스피린의 작용 메커니즘을 간단히 설명해주세요.",
            system_prompt="당신은 신약개발 전문 AI 어시스턴트입니다."
        )
        
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        
        print(f"{GREEN}✓ 텍스트 생성 성공{RESET} (소요시간: {elapsed:.2f}초)")
        print(f"  응답 길이: {len(response)} 문자")
        print(f"  응답 일부: {response[:100]}...")
        
        # 클라이언트 종료
        await client.close()
        
    except Exception as e:
        print(f"{RED}✗ OllamaClient 오류: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def main():
    """모든 테스트 실행"""
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}GAIA-BT API 서버 & Ollama 연결 진단{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    # 1. Ollama 직접 테스트
    ollama_ok = await test_direct_ollama()
    
    # 2. API 서버 테스트
    api_ok = await test_api_server()
    
    # 3. OllamaClient 테스트
    client_ok = await test_ollama_client()
    
    # 결과 요약
    print(f"\n{BLUE}=== 테스트 결과 요약 ==={RESET}")
    print(f"Ollama API: {'✓ 정상' if ollama_ok else '✗ 오류'}")
    print(f"GAIA-BT API 서버: {'✓ 정상' if api_ok else '✗ 오류'}")
    print(f"OllamaClient 클래스: {'✓ 정상' if client_ok else '✗ 오류'}")
    
    if not ollama_ok:
        print(f"\n{YELLOW}해결 방법:{RESET}")
        print("1. Ollama 서비스 재시작: sudo systemctl restart ollama")
        print("2. 모델 재설치: ollama pull Gemma3:27b-it-q4_K_M")
    
    if not api_ok:
        print(f"\n{YELLOW}해결 방법:{RESET}")
        print("1. API 서버 실행: python run_api_server.py")
        print("2. 포트 확인: lsof -i :8000")
        print("3. 로그 확인: tail -f /tmp/gaia-bt-api.log")
    
    if not client_ok:
        print(f"\n{YELLOW}해결 방법:{RESET}")
        print("1. 환경변수 확인: echo $OLLAMA_BASE_URL")
        print("2. 타임아웃 설정 증가 (현재 120초)")
        print("3. 모델 크기 확인 (27GB 모델은 로딩 시간이 길 수 있음)")

if __name__ == "__main__":
    asyncio.run(main())