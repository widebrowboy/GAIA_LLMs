#!/usr/bin/env python3
"""
gemma3-12b:latest 모델 성능 테스트
"""

import asyncio
import httpx
import time
import json

# 색상 코드
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"

async def test_ollama_direct():
    """Ollama API 직접 테스트"""
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}gemma3-12b:latest 직접 API 테스트{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print(f"{YELLOW}🧪 테스트 중... (최대 60초){RESET}")
            start_time = time.time()
            
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "gemma3-12b:latest",
                    "prompt": "Hello! Please introduce yourself as GAIA-BT, a drug development AI assistant, in 2-3 sentences.",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 150,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                }
            )
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                print(f"{GREEN}✓ 성공!{RESET}")
                print(f"⏱️  응답 시간: {elapsed:.2f}초")
                print(f"📝 응답 길이: {len(response_text)} 문자")
                print(f"🧠 모델 정보:")
                print(f"   - 총 소요시간: {result.get('total_duration', 0) / 1_000_000_000:.2f}초")
                print(f"   - 로딩 시간: {result.get('load_duration', 0) / 1_000_000_000:.2f}초") 
                print(f"   - 평가 시간: {result.get('eval_duration', 0) / 1_000_000_000:.2f}초")
                print(f"   - 토큰 수: {result.get('eval_count', 0)} 토큰")
                if result.get('eval_count', 0) > 0:
                    tokens_per_sec = result.get('eval_count', 0) / (result.get('eval_duration', 1) / 1_000_000_000)
                    print(f"   - 처리 속도: {tokens_per_sec:.1f} 토큰/초")
                
                print(f"\n💬 응답 내용:")
                print(f"{CYAN}{response_text}{RESET}")
                
                return {
                    'success': True,
                    'time': elapsed,
                    'response': response_text,
                    'tokens_per_sec': tokens_per_sec if 'tokens_per_sec' in locals() else 0
                }
            else:
                print(f"{RED}✗ HTTP 오류: {response.status_code}{RESET}")
                return {'success': False, 'error': f"HTTP {response.status_code}"}
                
    except Exception as e:
        print(f"{RED}✗ 오류: {e}{RESET}")
        return {'success': False, 'error': str(e)}

async def test_gaia_api():
    """GAIA-BT API 서버 테스트"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}GAIA-BT API 서버 테스트{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 1. 새 세션 생성
            print(f"{YELLOW}📝 새 세션 생성 중...{RESET}")
            session_response = await client.post(
                "http://localhost:8000/api/session/create",
                json={"session_id": "test_gemma3_12b"}
            )
            
            if session_response.status_code != 200:
                print(f"{RED}✗ 세션 생성 실패: {session_response.status_code}{RESET}")
                return {'success': False, 'error': 'Session creation failed'}
            
            session_data = session_response.json()
            session_id = session_data['session_id']
            print(f"{GREEN}✓ 세션 생성 성공: {session_id}{RESET}")
            
            # 2. 모델 변경
            print(f"{YELLOW}🔄 모델을 gemma3-12b:latest로 변경 중...{RESET}")
            model_response = await client.post(
                "http://localhost:8000/api/system/model",
                json={"model": "gemma3-12b:latest", "session_id": session_id}
            )
            
            if model_response.status_code != 200:
                print(f"{RED}✗ 모델 변경 실패: {model_response.status_code}{RESET}")
                return {'success': False, 'error': 'Model change failed'}
            
            print(f"{GREEN}✓ 모델 변경 성공{RESET}")
            
            # 3. 메시지 전송 테스트
            print(f"{YELLOW}💬 메시지 전송 중...{RESET}")
            start_time = time.time()
            
            message_response = await client.post(
                "http://localhost:8000/api/chat/message",
                json={
                    "message": "신약개발의 주요 단계 3가지를 간단히 설명해주세요.",
                    "session_id": session_id
                }
            )
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            if message_response.status_code == 200:
                result = message_response.json()
                response_text = result.get('response', '')
                
                print(f"{GREEN}✓ API 메시지 전송 성공!{RESET}")
                print(f"⏱️  응답 시간: {elapsed:.2f}초")
                print(f"📝 응답 길이: {len(response_text)} 문자")
                print(f"\n💬 응답 내용:")
                print(f"{CYAN}{response_text[:500]}...{RESET}")
                
                return {
                    'success': True,
                    'time': elapsed,
                    'response': response_text
                }
            else:
                print(f"{RED}✗ 메시지 전송 실패: {message_response.status_code}{RESET}")
                print(f"응답: {message_response.text}")
                return {'success': False, 'error': f"HTTP {message_response.status_code}"}
                
    except Exception as e:
        print(f"{RED}✗ 오류: {e}{RESET}")
        return {'success': False, 'error': str(e)}

async def test_streaming():
    """스트리밍 테스트"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}gemma3-12b:latest 스트리밍 테스트{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print(f"{YELLOW}🌊 스트리밍 테스트 중...{RESET}")
            start_time = time.time()
            
            chunks = []
            async with client.stream(
                "POST",
                "http://localhost:11434/api/generate",
                json={
                    "model": "gemma3-12b:latest",
                    "prompt": "Explain drug discovery process briefly.",
                    "stream": True,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 100,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                }
            ) as response:
                if response.status_code != 200:
                    print(f"{RED}✗ HTTP 오류: {response.status_code}{RESET}")
                    return {'success': False, 'error': f"HTTP {response.status_code}"}
                
                print(f"{CYAN}실시간 응답:{RESET}")
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            chunk = json.loads(line)
                            if chunk.get("response"):
                                chunk_text = chunk["response"]
                                chunks.append(chunk_text)
                                print(chunk_text, end='', flush=True)
                            if chunk.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            full_response = ''.join(chunks)
            
            print(f"\n\n{GREEN}✓ 스트리밍 성공!{RESET}")
            print(f"⏱️  응답 시간: {elapsed:.2f}초")
            print(f"📦 청크 수: {len(chunks)}")
            print(f"📝 총 응답 길이: {len(full_response)} 문자")
            
            return {
                'success': True,
                'time': elapsed,
                'chunks': len(chunks),
                'response': full_response
            }
            
    except Exception as e:
        print(f"{RED}✗ 스트리밍 오류: {e}{RESET}")
        return {'success': False, 'error': str(e)}

async def main():
    """메인 테스트 함수"""
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}GAIA-BT gemma3-12b:latest 종합 성능 테스트{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    results = {}
    
    # 1. Ollama 직접 API 테스트
    direct_result = await test_ollama_direct()
    results['direct'] = direct_result
    
    # 2. GAIA-BT API 서버 테스트
    gaia_result = await test_gaia_api()
    results['gaia_api'] = gaia_result
    
    # 3. 스트리밍 테스트
    streaming_result = await test_streaming()
    results['streaming'] = streaming_result
    
    # 결과 요약
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📊 테스트 결과 요약{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    success_count = 0
    total_time = 0
    
    for test_name, result in results.items():
        if result.get('success', False):
            success_count += 1
            time_taken = result.get('time', 0)
            total_time += time_taken
            
            print(f"{GREEN}✓ {test_name.replace('_', ' ').title()}{RESET}: {time_taken:.2f}초")
            
            if test_name == 'direct' and 'tokens_per_sec' in result:
                print(f"   🚀 처리 속도: {result['tokens_per_sec']:.1f} 토큰/초")
            
            if test_name == 'streaming':
                print(f"   📦 청크 수: {result.get('chunks', 0)}")
        else:
            print(f"{RED}✗ {test_name.replace('_', ' ').title()}{RESET}: {result.get('error', 'Unknown error')}")
    
    # 최종 평가
    print(f"\n{CYAN}🎯 최종 평가:{RESET}")
    print(f"   성공률: {success_count}/3 ({success_count/3*100:.0f}%)")
    if success_count > 0:
        avg_time = total_time / success_count
        print(f"   평균 응답 시간: {avg_time:.2f}초")
        
        if avg_time < 10:
            print(f"   {GREEN}🏆 성능 등급: 우수 (10초 미만){RESET}")
        elif avg_time < 30:
            print(f"   {YELLOW}⭐ 성능 등급: 양호 (30초 미만){RESET}")
        else:
            print(f"   {RED}⚠️  성능 등급: 개선 필요 (30초 이상){RESET}")
    
    print(f"\n{GREEN}gemma3-12b:latest 모델 테스트 완료!{RESET}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())