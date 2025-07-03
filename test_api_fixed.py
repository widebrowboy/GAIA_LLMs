#!/usr/bin/env python3
"""
수정된 API 엔드포인트 테스트
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

async def test_full_api_flow():
    """전체 API 플로우 테스트"""
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}GAIA-BT API 전체 플로우 테스트{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 1. 세션 생성
            print(f"{YELLOW}1. 새 세션 생성...{RESET}")
            session_response = await client.post(
                "http://localhost:8000/api/session/create",
                json={"session_id": "gemma3_test_session"}
            )
            
            if session_response.status_code == 200:
                session_data = session_response.json()
                session_id = session_data['session_id']
                print(f"   {GREEN}✓ 세션 생성 성공: {session_id}{RESET}")
            else:
                print(f"   {RED}✗ 세션 생성 실패: {session_response.status_code}{RESET}")
                return False
            
            # 2. 모델 변경 (올바른 필드명 사용)
            print(f"{YELLOW}2. 모델을 gemma3-12b:latest로 변경...{RESET}")
            model_response = await client.post(
                "http://localhost:8000/api/system/model",
                json={"model_name": "gemma3-12b:latest", "session_id": session_id}
            )
            
            if model_response.status_code == 200:
                print(f"   {GREEN}✓ 모델 변경 성공{RESET}")
            else:
                print(f"   {RED}✗ 모델 변경 실패: {model_response.status_code}{RESET}")
                print(f"   응답: {model_response.text}")
                return False
            
            # 3. 시스템 정보 확인
            print(f"{YELLOW}3. 시스템 정보 확인...{RESET}")
            info_response = await client.get("http://localhost:8000/api/system/info")
            
            if info_response.status_code == 200:
                info_data = info_response.json()
                print(f"   {GREEN}✓ 시스템 정보 확인 성공{RESET}")
                print(f"   현재 모델: {info_data.get('model', 'Unknown')}")
                print(f"   모드: {info_data.get('mode', 'Unknown')}")
            else:
                print(f"   {YELLOW}⚠️  시스템 정보 확인 실패{RESET}")
            
            # 4. 메시지 전송 테스트
            print(f"{YELLOW}4. 메시지 전송 테스트...{RESET}")
            start_time = time.time()
            
            message_response = await client.post(
                "http://localhost:8000/api/chat/message",
                json={
                    "message": "안녕하세요! GAIA-BT로 자기소개를 간단히 해주세요.",
                    "session_id": session_id
                }
            )
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            if message_response.status_code == 200:
                result = message_response.json()
                response_text = result.get('response', '')
                
                print(f"   {GREEN}✓ 메시지 전송 성공!{RESET}")
                print(f"   ⏱️  응답 시간: {elapsed:.2f}초")
                print(f"   📝 응답 길이: {len(response_text)} 문자")
                print(f"   💬 응답 내용:")
                print(f"   {CYAN}{response_text[:300]}...{RESET}")
                
                return True
            else:
                print(f"   {RED}✗ 메시지 전송 실패: {message_response.status_code}{RESET}")
                print(f"   응답: {message_response.text}")
                return False
                
    except Exception as e:
        print(f"{RED}✗ 테스트 오류: {e}{RESET}")
        return False

async def test_streaming_api():
    """스트리밍 API 테스트"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}GAIA-BT API 스트리밍 테스트{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 세션 생성
            session_response = await client.post(
                "http://localhost:8000/api/session/create",
                json={"session_id": "streaming_test_session"}
            )
            
            if session_response.status_code != 200:
                print(f"{RED}✗ 세션 생성 실패{RESET}")
                return False
            
            session_data = session_response.json()
            session_id = session_data['session_id']
            
            # 모델 변경
            model_response = await client.post(
                "http://localhost:8000/api/system/model",
                json={"model_name": "gemma3-12b:latest", "session_id": session_id}
            )
            
            if model_response.status_code != 200:
                print(f"{RED}✗ 모델 변경 실패{RESET}")
                return False
            
            # 스트리밍 메시지 전송
            print(f"{YELLOW}스트리밍 메시지 전송 중...{RESET}")
            start_time = time.time()
            
            response_text = ""
            async with client.stream(
                "POST",
                "http://localhost:8000/api/chat/stream",
                json={
                    "message": "신약개발의 중요성을 간단히 설명해주세요.",
                    "session_id": session_id
                }
            ) as response:
                if response.status_code == 200:
                    print(f"{CYAN}실시간 응답:{RESET}")
                    async for line in response.aiter_lines():
                        if line.strip():
                            if line.startswith("data: "):
                                chunk = line[6:]  # "data: " 제거
                                if chunk != "[DONE]":
                                    response_text += chunk
                                    print(chunk, end='', flush=True)
                else:
                    print(f"{RED}✗ 스트리밍 실패: {response.status_code}{RESET}")
                    return False
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            print(f"\n\n{GREEN}✓ 스트리밍 테스트 성공!{RESET}")
            print(f"⏱️  응답 시간: {elapsed:.2f}초")
            print(f"📝 총 응답 길이: {len(response_text)} 문자")
            
            return True
            
    except Exception as e:
        print(f"{RED}✗ 스트리밍 테스트 오류: {e}{RESET}")
        return False

async def main():
    """메인 테스트"""
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}GAIA-BT API 엔드포인트 전체 테스트{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    # 1. 전체 API 플로우 테스트
    api_success = await test_full_api_flow()
    
    # 2. 스트리밍 API 테스트
    streaming_success = await test_streaming_api()
    
    # 결과 요약
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📊 최종 테스트 결과{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    success_count = sum([api_success, streaming_success])
    total_tests = 2
    
    if api_success:
        print(f"{GREEN}✓ API 플로우 테스트: 성공{RESET}")
    else:
        print(f"{RED}✗ API 플로우 테스트: 실패{RESET}")
    
    if streaming_success:
        print(f"{GREEN}✓ 스트리밍 테스트: 성공{RESET}")
    else:
        print(f"{RED}✗ 스트리밍 테스트: 실패{RESET}")
    
    print(f"\n{CYAN}🎯 전체 성공률: {success_count}/{total_tests} ({success_count/total_tests*100:.0f}%){RESET}")
    
    if success_count == total_tests:
        print(f"{GREEN}🏆 모든 테스트 성공! gemma3-12b:latest 모델이 API에서 정상 작동합니다.{RESET}")
    else:
        print(f"{YELLOW}⚠️  일부 테스트 실패. API 설정을 다시 확인해주세요.{RESET}")
    
    return success_count == total_tests

if __name__ == "__main__":
    asyncio.run(main())