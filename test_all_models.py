#!/usr/bin/env python3
"""
설치된 모든 Ollama 모델 테스트 스크립트
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
CYAN = "\033[96m"
RESET = "\033[0m"

class ModelTester:
    def __init__(self):
        self.test_prompt = "Hello! Please introduce yourself briefly."
        self.models = []
        
    async def get_available_models(self):
        """설치된 모델 목록 가져오기"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("http://localhost:11434/api/tags")
                data = response.json()
                self.models = [model['name'] for model in data.get('models', [])]
                return True
        except Exception as e:
            print(f"{RED}✗ 모델 목록 가져오기 실패: {e}{RESET}")
            return False
    
    async def test_model_direct(self, model_name):
        """Ollama API로 모델 직접 테스트"""
        print(f"\n{CYAN}--- {model_name} 직접 테스트 ---{RESET}")
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                print(f"{YELLOW}테스트 중... (최대 2분 대기){RESET}")
                start_time = datetime.now()
                
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model_name,
                        "prompt": self.test_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": 100  # 짧은 응답
                        }
                    }
                )
                
                end_time = datetime.now()
                elapsed = (end_time - start_time).total_seconds()
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('response', '')
                    
                    print(f"{GREEN}✓ 성공{RESET} (소요시간: {elapsed:.2f}초)")
                    print(f"응답 길이: {len(response_text)} 문자")
                    print(f"응답 미리보기: {response_text[:100]}...")
                    
                    return {
                        'success': True,
                        'time': elapsed,
                        'response_length': len(response_text),
                        'response_preview': response_text[:100]
                    }
                else:
                    print(f"{RED}✗ HTTP 오류: {response.status_code}{RESET}")
                    return {'success': False, 'error': f"HTTP {response.status_code}"}
                    
        except asyncio.TimeoutError:
            print(f"{RED}✗ 타임아웃 (2분 초과){RESET}")
            return {'success': False, 'error': 'Timeout'}
        except Exception as e:
            print(f"{RED}✗ 오류: {e}{RESET}")
            return {'success': False, 'error': str(e)}
    
    async def test_model_via_api(self, model_name):
        """GAIA-BT API를 통한 모델 테스트"""
        print(f"\n{CYAN}--- {model_name} API 테스트 ---{RESET}")
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # 1. 모델 변경
                print(f"{YELLOW}모델 변경 중...{RESET}")
                change_response = await client.post(
                    "http://localhost:8000/api/chat/command",
                    json={
                        "command": f"/model {model_name}",
                        "session_id": f"test_{model_name.replace(':', '_')}"
                    }
                )
                
                if change_response.status_code != 200:
                    print(f"{RED}✗ 모델 변경 실패: {change_response.status_code}{RESET}")
                    return {'success': False, 'error': f"Model change failed: {change_response.status_code}"}
                
                # 2. 메시지 테스트
                print(f"{YELLOW}메시지 테스트 중...{RESET}")
                start_time = datetime.now()
                
                chat_response = await client.post(
                    "http://localhost:8000/api/chat/message",
                    json={
                        "message": self.test_prompt,
                        "session_id": f"test_{model_name.replace(':', '_')}"
                    }
                )
                
                end_time = datetime.now()
                elapsed = (end_time - start_time).total_seconds()
                
                if chat_response.status_code == 200:
                    result = chat_response.json()
                    response_text = result.get('response', '')
                    
                    print(f"{GREEN}✓ 성공{RESET} (소요시간: {elapsed:.2f}초)")
                    print(f"모드: {result.get('mode', 'unknown')}")
                    print(f"모델: {result.get('model', 'unknown')}")
                    print(f"응답 길이: {len(response_text)} 문자")
                    print(f"응답 미리보기: {response_text[:100]}...")
                    
                    return {
                        'success': True,
                        'time': elapsed,
                        'mode': result.get('mode'),
                        'model': result.get('model'),
                        'response_length': len(response_text),
                        'response_preview': response_text[:100]
                    }
                else:
                    print(f"{RED}✗ HTTP 오류: {chat_response.status_code}{RESET}")
                    error_text = chat_response.text
                    print(f"오류 내용: {error_text}")
                    return {'success': False, 'error': f"HTTP {chat_response.status_code}: {error_text}"}
                    
        except asyncio.TimeoutError:
            print(f"{RED}✗ 타임아웃 (2분 초과){RESET}")
            return {'success': False, 'error': 'Timeout'}
        except Exception as e:
            print(f"{RED}✗ 오류: {e}{RESET}")
            return {'success': False, 'error': str(e)}
    
    async def test_model_streaming(self, model_name):
        """스트리밍 모드 테스트"""
        print(f"\n{CYAN}--- {model_name} 스트리밍 테스트 ---{RESET}")
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                print(f"{YELLOW}스트리밍 테스트 중...{RESET}")
                start_time = datetime.now()
                first_chunk_time = None
                
                response = await client.post(
                    "http://localhost:8000/api/chat/stream",
                    json={
                        "message": self.test_prompt,
                        "session_id": f"stream_{model_name.replace(':', '_')}"
                    },
                    headers={"Accept": "text/event-stream"}
                )
                
                if response.status_code == 200:
                    chunk_count = 0
                    full_response = ""
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            
                            if data == "[DONE]":
                                break
                            
                            chunk_count += 1
                            full_response += data
                            
                            # 첫 번째 청크 도착 시간 기록
                            if first_chunk_time is None:
                                first_chunk_time = datetime.now()
                    
                    end_time = datetime.now()
                    total_time = (end_time - start_time).total_seconds()
                    first_response_time = (first_chunk_time - start_time).total_seconds() if first_chunk_time else 0
                    
                    print(f"{GREEN}✓ 성공{RESET}")
                    print(f"총 소요시간: {total_time:.2f}초")
                    print(f"첫 응답까지: {first_response_time:.2f}초")
                    print(f"청크 수: {chunk_count}")
                    print(f"응답 길이: {len(full_response)} 문자")
                    print(f"응답 미리보기: {full_response[:100]}...")
                    
                    return {
                        'success': True,
                        'total_time': total_time,
                        'first_response_time': first_response_time,
                        'chunk_count': chunk_count,
                        'response_length': len(full_response),
                        'response_preview': full_response[:100]
                    }
                else:
                    print(f"{RED}✗ HTTP 오류: {response.status_code}{RESET}")
                    return {'success': False, 'error': f"HTTP {response.status_code}"}
                    
        except asyncio.TimeoutError:
            print(f"{RED}✗ 타임아웃 (2분 초과){RESET}")
            return {'success': False, 'error': 'Timeout'}
        except Exception as e:
            print(f"{RED}✗ 오류: {e}{RESET}")
            return {'success': False, 'error': str(e)}

async def main():
    """메인 테스트 함수"""
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}GAIA-BT 설치된 모든 모델 가용성 테스트{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    tester = ModelTester()
    
    # 1. 설치된 모델 목록 가져오기
    print(f"\n{BLUE}1. 설치된 모델 확인{RESET}")
    if not await tester.get_available_models():
        return
    
    print(f"{GREEN}✓ 발견된 모델: {len(tester.models)}개{RESET}")
    for i, model in enumerate(tester.models, 1):
        print(f"  {i}. {model}")
    
    # 2. 각 모델 테스트
    results = {}
    
    for model in tester.models:
        print(f"\n{BLUE}{'='*50}{RESET}")
        print(f"{BLUE}모델: {model}{RESET}")
        print(f"{BLUE}{'='*50}{RESET}")
        
        # 직접 테스트
        direct_result = await tester.test_model_direct(model)
        
        # API 테스트
        api_result = await tester.test_model_via_api(model)
        
        # 스트리밍 테스트
        streaming_result = await tester.test_model_streaming(model)
        
        results[model] = {
            'direct': direct_result,
            'api': api_result,
            'streaming': streaming_result
        }
    
    # 3. 결과 요약
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}테스트 결과 요약{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    working_models = []
    partially_working = []
    broken_models = []
    
    for model, tests in results.items():
        direct_ok = tests['direct']['success']
        api_ok = tests['api']['success']
        stream_ok = tests['streaming']['success']
        
        print(f"\n{CYAN}{model}:{RESET}")
        print(f"  직접 테스트: {'✓' if direct_ok else '✗'}")
        print(f"  API 테스트: {'✓' if api_ok else '✗'}")
        print(f"  스트리밍 테스트: {'✓' if stream_ok else '✗'}")
        
        if direct_ok and api_ok and stream_ok:
            working_models.append(model)
            print(f"  {GREEN}상태: 완전 작동{RESET}")
        elif any([direct_ok, api_ok, stream_ok]):
            partially_working.append(model)
            print(f"  {YELLOW}상태: 부분 작동{RESET}")
        else:
            broken_models.append(model)
            print(f"  {RED}상태: 비작동{RESET}")
    
    # 최종 요약
    print(f"\n{BLUE}=== 최종 요약 ==={RESET}")
    print(f"{GREEN}완전 작동: {len(working_models)}개{RESET}")
    for model in working_models:
        print(f"  ✓ {model}")
    
    if partially_working:
        print(f"\n{YELLOW}부분 작동: {len(partially_working)}개{RESET}")
        for model in partially_working:
            print(f"  ⚠ {model}")
    
    if broken_models:
        print(f"\n{RED}비작동: {len(broken_models)}개{RESET}")
        for model in broken_models:
            print(f"  ✗ {model}")
    
    # 권장사항
    print(f"\n{BLUE}=== 권장사항 ==={RESET}")
    if working_models:
        fastest_model = None
        fastest_time = float('inf')
        
        for model in working_models:
            if results[model]['api']['success']:
                time = results[model]['api']['time']
                if time < fastest_time:
                    fastest_time = time
                    fastest_model = model
        
        if fastest_model:
            print(f"가장 빠른 모델: {GREEN}{fastest_model}{RESET} ({fastest_time:.2f}초)")
            print(f"설정 변경: export OLLAMA_MODEL={fastest_model}")
    
    if broken_models:
        print(f"\n{YELLOW}비작동 모델 해결 방법:{RESET}")
        print("1. 모델 재설치: ollama pull <모델명>")
        print("2. Ollama 재시작: sudo systemctl restart ollama")
        print("3. 메모리 확인: 대용량 모델은 충분한 RAM/VRAM 필요")

if __name__ == "__main__":
    asyncio.run(main())