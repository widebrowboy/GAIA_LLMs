#!/usr/bin/env python3
"""
Ollama 연결 테스트 스크립트
"""
import asyncio
import httpx
import json
import sys
from datetime import datetime

# 환경 설정
OLLAMA_BASE_URL = "http://localhost:11434"
TEST_MODEL = "txgemma-chat:latest"

async def test_ollama_connection():
    """Ollama 연결 및 응답 테스트"""
    
    print(f"[{datetime.now()}] Ollama 연결 테스트 시작...")
    print(f"Base URL: {OLLAMA_BASE_URL}")
    print(f"Test Model: {TEST_MODEL}")
    print("-" * 50)
    
    # 1. API 상태 확인
    print("\n1. API 상태 확인 (/api/tags)...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            print(f"   상태 코드: {response.status_code}")
            if response.status_code == 200:
                models = response.json()
                print(f"   사용 가능한 모델 수: {len(models.get('models', []))}")
                for model in models.get('models', []):
                    print(f"   - {model.get('name')}: {model.get('size')} bytes")
            else:
                print(f"   오류: {response.text}")
    except Exception as e:
        print(f"   연결 실패: {type(e).__name__}: {e}")
    
    # 2. 모델 정보 확인
    print(f"\n2. 모델 정보 확인 ({TEST_MODEL})...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/show",
                json={"model": TEST_MODEL}
            )
            print(f"   상태 코드: {response.status_code}")
            if response.status_code == 200:
                info = response.json()
                print(f"   모델 존재: ✓")
                print(f"   모델 크기: {info.get('details', {}).get('parameter_size', 'N/A')}")
            else:
                print(f"   오류: {response.text}")
    except Exception as e:
        print(f"   요청 실패: {type(e).__name__}: {e}")
    
    # 3. 생성 테스트 (스트리밍 비활성화)
    print(f"\n3. 텍스트 생성 테스트 (비스트리밍)...")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": TEST_MODEL,
                    "prompt": "신약개발의 중요성을 한 문장으로 설명해주세요.",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 100
                    }
                }
            )
            print(f"   상태 코드: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   응답 수신: ✓")
                print(f"   생성된 텍스트: {result.get('response', '')[:200]}...")
                print(f"   총 소요 시간: {result.get('total_duration', 0) / 1e9:.2f}초")
            else:
                print(f"   오류: {response.text}")
    except httpx.ReadTimeout:
        print(f"   타임아웃 오류: 응답 시간이 120초를 초과했습니다.")
    except Exception as e:
        print(f"   요청 실패: {type(e).__name__}: {e}")
    
    # 4. 스트리밍 테스트
    print(f"\n4. 스트리밍 생성 테스트...")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response_text = ""
            async with client.stream(
                'POST',
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": TEST_MODEL,
                    "prompt": "AI의 미래는",
                    "stream": True,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 50
                    }
                }
            ) as response:
                print(f"   상태 코드: {response.status_code}")
                if response.status_code == 200:
                    print(f"   스트리밍 응답: ", end="", flush=True)
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                token = data.get('response', '')
                                response_text += token
                                print(token, end="", flush=True)
                                if data.get('done'):
                                    break
                            except json.JSONDecodeError:
                                pass
                    print(f"\n   스트리밍 완료: ✓")
                else:
                    print(f"   오류: {await response.aread()}")
    except Exception as e:
        print(f"   스트리밍 실패: {type(e).__name__}: {e}")
    
    # 5. 연결 상태 요약
    print("\n" + "=" * 50)
    print("연결 테스트 요약:")
    print(f"- Ollama 서비스: 실행 중")
    print(f"- API 엔드포인트: {OLLAMA_BASE_URL}")
    print(f"- 테스트 모델: {TEST_MODEL}")
    print("=" * 50)

# 동기 래퍼 함수
def main():
    try:
        asyncio.run(test_ollama_connection())
    except KeyboardInterrupt:
        print("\n\n테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n예상치 못한 오류 발생: {type(e).__name__}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()