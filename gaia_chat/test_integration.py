#!/usr/bin/env python3
"""
GAIA Chat + GAIA-BT API 통합 테스트 스크립트
"""

import requests
import json
import time

# API 서버 설정
GAIA_BT_API = "http://localhost:8000"
NEXT_JS_FRONTEND = "http://localhost:3000"

def test_gaia_bt_integration():
    print("🧪 GAIA Chat + GAIA-BT API 통합 테스트 시작")
    print("=" * 60)
    
    # 1. 서버 연결 확인
    try:
        # GAIA-BT API 서버 확인
        response = requests.get(f"{GAIA_BT_API}/health", timeout=5)
        api_status = response.json()
        print(f"✅ GAIA-BT API 서버: {api_status['status']}")
        print(f"   - 모델: {api_status['model']}")
        print(f"   - 모드: {api_status['mode']}")
        print(f"   - MCP: {'활성화' if api_status['mcp_enabled'] else '비활성화'}")
        
        # Next.js 프론트엔드 확인
        response = requests.get(f"{NEXT_JS_FRONTEND}", timeout=5)
        print(f"✅ Next.js 프론트엔드: {response.status_code} OK")
        
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return
    
    print("\n" + "=" * 60)
    
    # 2. 세션 생성 테스트
    session_id = f"test_session_{int(time.time())}"
    try:
        response = requests.post(f"{GAIA_BT_API}/api/session/create", 
                               json={"session_id": session_id}, timeout=10)
        if response.status_code in [200, 201]:
            print(f"✅ 세션 생성 성공: {session_id}")
        else:
            print(f"⚠️ 세션이 이미 존재하거나 생성 실패")
    except Exception as e:
        print(f"❌ 세션 생성 오류: {e}")
    
    # 3. 기본 채팅 테스트
    print("\n📝 기본 채팅 기능 테스트")
    chat_tests = [
        "안녕하세요",
        "아스피린의 작용 메커니즘은?",
        "EGFR 억제제에 대해 설명해주세요",
        "임상시험 1상과 2상의 차이점은?"
    ]
    
    for i, message in enumerate(chat_tests, 1):
        try:
            response = requests.post(f"{GAIA_BT_API}/api/chat/message",
                                   json={"message": message, "session_id": session_id},
                                   timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_length = len(result['response'])
                print(f"   {i}. '{message}' → AI 응답 {response_length}자 (모드: {result['mode']})")
            else:
                print(f"   {i}. '{message}' → 오류: {response.status_code}")
        except Exception as e:
            print(f"   {i}. '{message}' → 예외: {e}")
        
        time.sleep(1)  # API 부하 방지
    
    # 4. MCP 명령어 테스트
    print("\n🔬 MCP 명령어 테스트")
    mcp_commands = [
        ("start", "MCP 시스템 시작"),
        ("status", "MCP 상태 확인"),
        ("stop", "MCP 시스템 중지")
    ]
    
    for command, description in mcp_commands:
        try:
            response = requests.post(f"{GAIA_BT_API}/api/chat/command",
                                   json={"command": f"/mcp {command}", "session_id": session_id},
                                   timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {description}: {result.get('type', 'success')}")
            else:
                print(f"   ❌ {description}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {description}: {e}")
        
        time.sleep(1)
    
    # 5. 프롬프트 모드 변경 테스트
    print("\n🎯 프롬프트 모드 변경 테스트")
    prompt_modes = ["clinical", "research", "chemistry", "regulatory", "default"]
    
    for mode in prompt_modes:
        try:
            response = requests.post(f"{GAIA_BT_API}/api/system/prompt",
                                   json={"prompt_type": mode, "session_id": session_id},
                                   timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {mode} 모드 설정 성공")
            else:
                print(f"   ❌ {mode} 모드 설정 실패: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {mode} 모드 오류: {e}")
    
    # 6. 최종 상태 확인
    print("\n📊 최종 시스템 상태")
    try:
        response = requests.get(f"{GAIA_BT_API}/health", timeout=5)
        final_status = response.json()
        print(f"   API 상태: {final_status['status']}")
        print(f"   현재 모델: {final_status['model']}")
        print(f"   현재 모드: {final_status['mode']}")
        print(f"   MCP 활성화: {final_status['mcp_enabled']}")
        print(f"   디버그 모드: {final_status['debug']}")
    except Exception as e:
        print(f"   ❌ 상태 확인 실패: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 통합 테스트 완료!")
    print(f"🌐 웹 인터페이스: {NEXT_JS_FRONTEND}")
    print(f"🔗 API 문서: {GAIA_BT_API}/docs")
    print(f"📋 API 건강 상태: {GAIA_BT_API}/health")
    
    print("\n💡 주요 기능:")
    print("  • 기본 채팅: GAIA-BT 신약개발 전문 AI 대화")
    print("  • Deep Research: MCP 통합 다중 데이터베이스 검색")
    print("  • 프롬프트 모드: clinical/research/chemistry/regulatory")
    print("  • 실시간 상태: 사이드바에서 실시간 시스템 모니터링")
    print("  • 로컬 히스토리: 브라우저 로컬 스토리지에 대화 저장")

if __name__ == "__main__":
    test_gaia_bt_integration()