#!/usr/bin/env python3
"""
스트리밍 응답 테스트 스크립트
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

async def test_streaming_response():
    """스트리밍 응답 테스트"""
    print(f"{BLUE}=== 스트리밍 응답 테스트 ==={RESET}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print(f"{YELLOW}스트리밍 요청 시작...{RESET}")
            start_time = datetime.now()
            
            response = await client.post(
                "http://localhost:8000/api/chat/stream",
                json={
                    "message": "아스피린의 작용 메커니즘을 간단히 설명해주세요.",
                    "session_id": "default"
                },
                headers={"Accept": "text/event-stream"}
            )
            
            if response.status_code != 200:
                print(f"{RED}✗ 응답 오류: {response.status_code}{RESET}")
                print(f"응답 내용: {response.text}")
                return False
            
            print(f"{GREEN}✓ 스트리밍 시작{RESET}")
            print(f"{BLUE}실시간 응답:{RESET}")
            print("-" * 50)
            
            chunk_count = 0
            full_response = ""
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # "data: " 제거
                    
                    if data == "[DONE]":
                        print(f"\n{GREEN}✓ 스트리밍 완료{RESET}")
                        break
                    
                    chunk_count += 1
                    full_response += data
                    print(data, end="", flush=True)
            
            end_time = datetime.now()
            elapsed = (end_time - start_time).total_seconds()
            
            print("\n" + "-" * 50)
            print(f"{GREEN}✓ 테스트 완료{RESET}")
            print(f"소요시간: {elapsed:.2f}초")
            print(f"청크 수: {chunk_count}")
            print(f"전체 응답 길이: {len(full_response)} 문자")
            
            return True
            
    except Exception as e:
        print(f"{RED}✗ 스트리밍 테스트 오류: {e}{RESET}")
        return False

async def test_regular_vs_streaming():
    """일반 응답 vs 스트리밍 응답 비교"""
    print(f"\n{BLUE}=== 일반 vs 스트리밍 응답 비교 ==={RESET}")
    
    message = "Hello, GAIA-BT!"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. 일반 응답 테스트
        print(f"{YELLOW}1. 일반 응답 테스트...{RESET}")
        start_time = datetime.now()
        
        try:
            response = await client.post(
                "http://localhost:8000/api/chat/message",
                json={
                    "message": message,
                    "session_id": "test_regular"
                }
            )
            
            end_time = datetime.now()
            regular_time = (end_time - start_time).total_seconds()
            
            if response.status_code == 200:
                result = response.json()
                print(f"{GREEN}✓ 일반 응답 성공{RESET} (소요시간: {regular_time:.2f}초)")
                print(f"응답 길이: {len(result.get('response', ''))} 문자")
            else:
                print(f"{RED}✗ 일반 응답 실패: {response.status_code}{RESET}")
                
        except Exception as e:
            print(f"{RED}✗ 일반 응답 오류: {e}{RESET}")
        
        # 2. 스트리밍 응답 테스트
        print(f"\n{YELLOW}2. 스트리밍 응답 테스트...{RESET}")
        start_time = datetime.now()
        first_chunk_time = None
        
        try:
            response = await client.post(
                "http://localhost:8000/api/chat/stream",
                json={
                    "message": message,
                    "session_id": "test_stream"
                },
                headers={"Accept": "text/event-stream"}
            )
            
            if response.status_code == 200:
                chunk_count = 0
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        
                        if data == "[DONE]":
                            break
                        
                        chunk_count += 1
                        
                        # 첫 번째 청크 도착 시간 기록
                        if first_chunk_time is None:
                            first_chunk_time = datetime.now()
                
                end_time = datetime.now()
                streaming_time = (end_time - start_time).total_seconds()
                first_response_time = (first_chunk_time - start_time).total_seconds() if first_chunk_time else 0
                
                print(f"{GREEN}✓ 스트리밍 응답 성공{RESET}")
                print(f"총 소요시간: {streaming_time:.2f}초")
                print(f"첫 응답까지: {first_response_time:.2f}초")
                print(f"청크 수: {chunk_count}")
                
                print(f"\n{BLUE}=== 성능 비교 ==={RESET}")
                print(f"일반 응답: {regular_time:.2f}초")
                print(f"스트리밍 첫 응답: {first_response_time:.2f}초")
                improvement = ((regular_time - first_response_time) / regular_time) * 100
                print(f"체감 속도 개선: {improvement:.1f}%")
                
            else:
                print(f"{RED}✗ 스트리밍 응답 실패: {response.status_code}{RESET}")
                
        except Exception as e:
            print(f"{RED}✗ 스트리밍 응답 오류: {e}{RESET}")

async def main():
    """메인 테스트 함수"""
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}GAIA-BT 스트리밍 응답 테스트{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    # 1. 기본 스트리밍 테스트
    streaming_ok = await test_streaming_response()
    
    # 2. 성능 비교 테스트
    if streaming_ok:
        await test_regular_vs_streaming()
    
    print(f"\n{BLUE}=== 테스트 완료 ==={RESET}")
    if streaming_ok:
        print(f"{GREEN}✓ 스트리밍 기능이 정상적으로 작동합니다!{RESET}")
        print("\n🎉 이제 WebUI에서 실시간 대화를 즐길 수 있습니다:")
        print("   - http://localhost:3001 (WebUI)")
        print("   - http://localhost:8000/docs (API 문서)")
    else:
        print(f"{RED}✗ 스트리밍 기능에 문제가 있습니다.{RESET}")

if __name__ == "__main__":
    asyncio.run(main())