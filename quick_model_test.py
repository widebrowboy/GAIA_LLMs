#!/usr/bin/env python3
"""
빠른 모델 성능 테스트
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

async def test_model_quick(model_name):
    """빠른 모델 테스트"""
    print(f"\n{CYAN}🧪 {model_name} 테스트{RESET}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            start_time = time.time()
            
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model_name,
                    "prompt": "Hello",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 30
                    }
                }
            )
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                print(f"  {GREEN}✓ 성공{RESET} - {elapsed:.2f}초")
                print(f"  📝 응답: {response_text[:100]}...")
                
                return {
                    'success': True,
                    'time': elapsed,
                    'response': response_text
                }
            else:
                print(f"  {RED}✗ HTTP 오류: {response.status_code}{RESET}")
                return {'success': False, 'error': f"HTTP {response.status_code}"}
                
    except Exception as e:
        print(f"  {RED}✗ 오류: {e}{RESET}")
        return {'success': False, 'error': str(e)}

async def main():
    """메인 함수"""
    print(f"{BLUE}{'='*50}{RESET}")
    print(f"{BLUE}빠른 모델 성능 테스트{RESET}")
    print(f"{BLUE}{'='*50}{RESET}")
    
    models = [
        "gemma3-12b:latest",           # 새로 추가된 모델
        "txgemma-chat:latest",         # 기존 모델
        "txgemma-predict:latest",      # 기존 모델
        # "Gemma3:27b-it-q4_K_M"       # 대용량 모델은 일단 제외
    ]
    
    results = {}
    
    # 각 모델 테스트
    for model_name in models:
        result = await test_model_quick(model_name)
        results[model_name] = result
    
    # 결과 요약
    print(f"\n{BLUE}{'='*50}{RESET}")
    print(f"{BLUE}📊 테스트 결과 요약{RESET}")
    print(f"{BLUE}{'='*50}{RESET}")
    
    successful_models = []
    
    for model_name, result in results.items():
        if result.get('success', False):
            time_taken = result['time']
            successful_models.append((model_name, time_taken))
            print(f"{GREEN}✓ {model_name}{RESET}: {time_taken:.2f}초")
        else:
            print(f"{RED}✗ {model_name}{RESET}: {result.get('error', 'Unknown error')}")
    
    # 성능 순위
    if successful_models:
        successful_models.sort(key=lambda x: x[1])  # 시간순 정렬
        print(f"\n{CYAN}🏆 성능 순위 (빠른 순):{RESET}")
        for i, (model_name, time_taken) in enumerate(successful_models, 1):
            print(f"  {i}. {model_name} ({time_taken:.2f}초)")
        
        # 가장 빠른 모델 권장
        fastest_model = successful_models[0][0]
        print(f"\n{YELLOW}🥇 가장 빠른 모델: {GREEN}{fastest_model}{RESET}")
        print(f"{YELLOW}📋 권장 설정:{RESET}")
        print(f"   export OLLAMA_MODEL={fastest_model}")
        
        # 새 모델 분석
        gemma3_result = results.get('gemma3-12b:latest')
        if gemma3_result and gemma3_result.get('success'):
            gemma3_time = gemma3_result['time']
            print(f"\n{BLUE}🆕 새 모델 (gemma3-12b) 분석:{RESET}")
            print(f"   응답 시간: {gemma3_time:.2f}초")
            
            # 기존 모델과 비교
            txgemma_result = results.get('txgemma-chat:latest')
            if txgemma_result and txgemma_result.get('success'):
                txgemma_time = txgemma_result['time']
                if gemma3_time < txgemma_time:
                    print(f"   ✅ txgemma-chat보다 {txgemma_time - gemma3_time:.2f}초 빠름")
                else:
                    print(f"   ⚠️  txgemma-chat이 {gemma3_time - txgemma_time:.2f}초 빠름")
    
    print(f"\n{GREEN}테스트 완료!{RESET}")

if __name__ == "__main__":
    asyncio.run(main())