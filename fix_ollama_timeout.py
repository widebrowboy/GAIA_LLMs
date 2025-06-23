#!/usr/bin/env python3
"""
Ollama 타임아웃 문제 해결 스크립트
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

async def test_ollama_models():
    """다양한 모델로 Ollama 테스트"""
    models = [
        ("llama2", "간단한 7B 모델"),
        ("Gemma3:latest", "일반 Gemma3 모델"),
        ("Gemma3:27b-it-q4_K_M", "대용량 27B 모델")
    ]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for model_name, description in models:
            print(f"\n{BLUE}=== {model_name} 테스트 ({description}) ==={RESET}")
            
            try:
                # 모델 존재 확인
                response = await client.get("http://localhost:11434/api/tags")
                available_models = [m['name'] for m in response.json().get('models', [])]
                
                if model_name not in available_models:
                    print(f"{YELLOW}⚠️  모델 {model_name}이 설치되지 않았습니다.{RESET}")
                    continue
                
                # 짧은 프롬프트로 테스트
                print(f"{YELLOW}테스트 중...{RESET}")
                start_time = datetime.now()
                
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model_name,
                        "prompt": "Say hello in one sentence.",
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "num_predict": 50  # 매우 짧은 응답
                        }
                    },
                    timeout=120.0  # 2분 타임아웃
                )
                
                end_time = datetime.now()
                elapsed = (end_time - start_time).total_seconds()
                
                result = response.json()
                print(f"{GREEN}✓ 성공!{RESET} (소요시간: {elapsed:.2f}초)")
                print(f"  응답: {result.get('response', '')[:100]}")
                
            except httpx.TimeoutException:
                print(f"{RED}✗ 타임아웃 발생{RESET}")
            except Exception as e:
                print(f"{RED}✗ 오류: {e}{RESET}")

async def check_model_loading():
    """모델 로딩 상태 확인"""
    print(f"\n{BLUE}=== 모델 로딩 상태 확인 ==={RESET}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get("http://localhost:11434/api/ps")
            data = response.json()
            
            if data.get('models'):
                print(f"{GREEN}✓ 현재 로드된 모델:{RESET}")
                for model in data['models']:
                    print(f"  - {model['name']} (크기: {model.get('size', 'unknown')})")
            else:
                print(f"{YELLOW}⚠️  현재 로드된 모델이 없습니다.{RESET}")
                
        except Exception as e:
            print(f"{RED}✗ 상태 확인 실패: {e}{RESET}")

async def preload_model(model_name):
    """모델 사전 로드"""
    print(f"\n{BLUE}=== {model_name} 모델 사전 로드 ==={RESET}")
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            print(f"{YELLOW}모델을 메모리에 로드 중... (최대 5분 소요){RESET}")
            start_time = datetime.now()
            
            # 빈 프롬프트로 모델 로드
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model_name,
                    "prompt": "",
                    "stream": False,
                    "options": {
                        "num_predict": 1
                    }
                }
            )
            
            end_time = datetime.now()
            elapsed = (end_time - start_time).total_seconds()
            
            if response.status_code == 200:
                print(f"{GREEN}✓ 모델 로드 완료!{RESET} (소요시간: {elapsed:.2f}초)")
                return True
            else:
                print(f"{RED}✗ 모델 로드 실패: {response.status_code}{RESET}")
                return False
                
        except httpx.TimeoutException:
            print(f"{RED}✗ 모델 로드 타임아웃 (5분 초과){RESET}")
            return False
        except Exception as e:
            print(f"{RED}✗ 모델 로드 오류: {e}{RESET}")
            return False

async def main():
    """메인 진단 및 해결"""
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Ollama 타임아웃 문제 진단 및 해결{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    # 1. 현재 로드된 모델 확인
    await check_model_loading()
    
    # 2. 대용량 모델 사전 로드
    model_loaded = await preload_model("Gemma3:27b-it-q4_K_M")
    
    if model_loaded:
        # 3. 다시 모델 상태 확인
        await check_model_loading()
        
        # 4. 모든 모델 테스트
        await test_ollama_models()
    
    print(f"\n{BLUE}=== 권장 해결 방법 ==={RESET}")
    print("1. 대용량 모델(27GB)은 첫 실행 시 로딩에 1-5분이 소요됩니다.")
    print("2. 모델을 미리 로드하려면: ollama run Gemma3:27b-it-q4_K_M")
    print("3. 더 작은 모델 사용을 고려: ollama pull llama2")
    print("4. API 서버의 타임아웃을 300초 이상으로 설정하세요.")
    print("5. GPU 메모리가 충분한지 확인: nvidia-smi")

if __name__ == "__main__":
    asyncio.run(main())