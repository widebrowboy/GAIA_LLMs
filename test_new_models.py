#!/usr/bin/env python3
"""
새로 추가된 모델들을 포함한 모든 모델 테스트
"""

import asyncio
import httpx
import time

# 색상 코드
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"

class ModelTester:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.models = [
            "gemma3-12b:latest",           # 새로 추가된 모델
            "txgemma-chat:latest",         # 기존 모델
            "txgemma-predict:latest",      # 기존 모델
            "Gemma3:27b-it-q4_K_M"        # 기존 대용량 모델
        ]
    
    async def test_model_direct(self, model_name):
        """Ollama API 직접 테스트"""
        print(f"\n{CYAN}=== {model_name} 직접 API 테스트 ==={RESET}")
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                start_time = time.time()
                
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": model_name,
                        "prompt": "Hello! Please introduce yourself as GAIA-BT, a drug development AI assistant, in 2-3 sentences.",
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": 200
                        }
                    }
                )
                
                end_time = time.time()
                elapsed = end_time - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('response', '')
                    
                    print(f"{GREEN}✓ 성공{RESET}")
                    print(f"⏱️  소요시간: {elapsed:.2f}초")
                    print(f"📝 응답 길이: {len(response_text)} 문자")
                    print(f"💬 응답: {response_text[:150]}...")
                    
                    return {
                        'success': True,
                        'time': elapsed,
                        'response_length': len(response_text),
                        'response': response_text
                    }
                else:
                    print(f"{RED}✗ HTTP 오류: {response.status_code}{RESET}")
                    return {'success': False, 'error': f"HTTP {response.status_code}"}
                    
        except Exception as e:
            print(f"{RED}✗ 오류: {e}{RESET}")
            return {'success': False, 'error': str(e)}
    
    async def test_model_gaia_api(self, model_name):
        """GAIA-BT API 서버를 통한 테스트"""
        print(f"\n{CYAN}=== {model_name} GAIA-BT API 테스트 ==={RESET}")
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # 세션 생성
                session_response = await client.post(
                    "http://localhost:8000/api/session/create",
                    json={"session_id": f"test_{model_name.replace(':', '_')}"}
                )
                
                if session_response.status_code != 200:
                    print(f"{RED}✗ 세션 생성 실패{RESET}")
                    return {'success': False, 'error': 'Session creation failed'}
                
                session_data = session_response.json()
                session_id = session_data['session_id']
                
                # 모델 변경
                model_response = await client.post(
                    "http://localhost:8000/api/system/model",
                    json={"model": model_name, "session_id": session_id}
                )
                
                if model_response.status_code != 200:
                    print(f"{RED}✗ 모델 변경 실패{RESET}")
                    return {'success': False, 'error': 'Model change failed'}
                
                # 메시지 전송
                start_time = time.time()
                
                message_response = await client.post(
                    "http://localhost:8000/api/chat/message",
                    json={
                        "message": "신약개발 과정의 주요 단계 3가지를 간단히 설명해주세요.",
                        "session_id": session_id
                    }
                )
                
                end_time = time.time()
                elapsed = end_time - start_time
                
                if message_response.status_code == 200:
                    result = message_response.json()
                    response_text = result.get('response', '')
                    
                    print(f"{GREEN}✓ 성공{RESET}")
                    print(f"⏱️  소요시간: {elapsed:.2f}초")
                    print(f"📝 응답 길이: {len(response_text)} 문자")
                    print(f"💬 응답: {response_text[:150]}...")
                    
                    return {
                        'success': True,
                        'time': elapsed,
                        'response_length': len(response_text),
                        'response': response_text
                    }
                else:
                    print(f"{RED}✗ HTTP 오류: {message_response.status_code}{RESET}")
                    return {'success': False, 'error': f"HTTP {message_response.status_code}"}
                    
        except Exception as e:
            print(f"{RED}✗ 오류: {e}{RESET}")
            return {'success': False, 'error': str(e)}
    
    async def test_model_streaming(self, model_name):
        """스트리밍 API 테스트"""
        print(f"\n{CYAN}=== {model_name} 스트리밍 테스트 ==={RESET}")
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                start_time = time.time()
                
                async with client.stream(
                    "POST",
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": model_name,
                        "prompt": "Explain drug discovery briefly.",
                        "stream": True,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": 100
                        }
                    }
                ) as response:
                    if response.status_code != 200:
                        print(f"{RED}✗ HTTP 오류: {response.status_code}{RESET}")
                        return {'success': False, 'error': f"HTTP {response.status_code}"}
                    
                    chunks = []
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                import json
                                chunk = json.loads(line)
                                if chunk.get("response"):
                                    chunks.append(chunk["response"])
                                if chunk.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
                
                end_time = time.time()
                elapsed = end_time - start_time
                
                full_response = ''.join(chunks)
                
                print(f"{GREEN}✓ 스트리밍 성공{RESET}")
                print(f"⏱️  소요시간: {elapsed:.2f}초")
                print(f"📦 청크 수: {len(chunks)}")
                print(f"📝 응답 길이: {len(full_response)} 문자")
                print(f"💬 응답: {full_response[:150]}...")
                
                return {
                    'success': True,
                    'time': elapsed,
                    'chunks': len(chunks),
                    'response_length': len(full_response),
                    'response': full_response
                }
                
        except Exception as e:
            print(f"{RED}✗ 스트리밍 오류: {e}{RESET}")
            return {'success': False, 'error': str(e)}

async def main():
    """메인 함수"""
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}전체 모델 성능 테스트 (새 모델 포함){RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    tester = ModelTester()
    all_results = {}
    
    # 각 모델에 대해 3가지 테스트 실행
    for model_name in tester.models:
        print(f"\n{YELLOW}🧪 {model_name} 테스트 시작{RESET}")
        
        model_results = {}
        
        # 1. 직접 API 테스트
        direct_result = await tester.test_model_direct(model_name)
        model_results['direct'] = direct_result
        
        # 2. GAIA-BT API 테스트
        gaia_result = await tester.test_model_gaia_api(model_name)
        model_results['gaia_api'] = gaia_result
        
        # 3. 스트리밍 테스트
        streaming_result = await tester.test_model_streaming(model_name)
        model_results['streaming'] = streaming_result
        
        all_results[model_name] = model_results
        
        # 모델별 요약
        success_count = sum(1 for r in model_results.values() if r.get('success', False))
        print(f"\n{CYAN}📊 {model_name} 요약: {success_count}/3 테스트 성공{RESET}")
    
    # 전체 결과 요약
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📈 전체 테스트 결과 요약{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    successful_models = []
    
    for model_name, results in all_results.items():
        direct_success = results['direct'].get('success', False)
        gaia_success = results['gaia_api'].get('success', False)
        streaming_success = results['streaming'].get('success', False)
        
        success_rate = sum([direct_success, gaia_success, streaming_success]) / 3
        
        if direct_success:
            avg_time = (
                results['direct'].get('time', 0) + 
                results['gaia_api'].get('time', 0) + 
                results['streaming'].get('time', 0)
            ) / 3
            successful_models.append((model_name, avg_time, success_rate))
        
        status = f"{GREEN}✓{RESET}" if success_rate >= 0.67 else f"{RED}✗{RESET}"
        print(f"{status} {model_name}: {success_rate*100:.0f}% 성공률")
        
        if direct_success:
            print(f"    ⏱️  평균 응답 시간: {avg_time:.2f}초")
        
        if not direct_success:
            print(f"    ❌ 오류: {results['direct'].get('error', 'Unknown error')}")
    
    # 성능 순위
    if successful_models:
        successful_models.sort(key=lambda x: x[1])  # 평균 시간순 정렬
        print(f"\n{CYAN}🏆 모델 성능 순위 (평균 응답 시간 기준):{RESET}")
        for i, (model_name, avg_time, success_rate) in enumerate(successful_models, 1):
            print(f"  {i}. {model_name} ({avg_time:.2f}초, {success_rate*100:.0f}% 성공률)")
    
    # 권장사항
    print(f"\n{BLUE}🎯 권장사항{RESET}")
    if successful_models:
        fastest_model = successful_models[0][0]
        print(f"🥇 가장 빠른 모델: {GREEN}{fastest_model}{RESET}")
        print(f"📋 설정 변경 제안:")
        print(f"   export OLLAMA_MODEL={fastest_model}")
        print(f"   OLLAMA_MODEL = '{fastest_model}' # config.py에서")
        
        # 새 모델 성능 분석
        gemma3_12b_result = all_results.get('gemma3-12b:latest')
        if gemma3_12b_result and gemma3_12b_result['direct'].get('success'):
            gemma3_time = gemma3_12b_result['direct']['time']
            print(f"\n🆕 새 모델 분석:")
            print(f"   gemma3-12b:latest: {gemma3_time:.2f}초")
            
            # 기존 모델과 비교
            txgemma_chat_result = all_results.get('txgemma-chat:latest')
            if txgemma_chat_result and txgemma_chat_result['direct'].get('success'):
                txgemma_time = txgemma_chat_result['direct']['time']
                if gemma3_time < txgemma_time:
                    print(f"   ✅ gemma3-12b가 txgemma-chat보다 {txgemma_time - gemma3_time:.2f}초 빠름")
                else:
                    print(f"   ⚠️  txgemma-chat이 gemma3-12b보다 {gemma3_time - txgemma_time:.2f}초 빠름")
    
    print(f"\n{GREEN}전체 모델 테스트 완료!{RESET}")

if __name__ == "__main__":
    asyncio.run(main())