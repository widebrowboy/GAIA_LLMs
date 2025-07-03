#!/usr/bin/env python3
"""
WebUI-API 서버 통합 테스트 스크립트
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_health():
    """헬스 체크"""
    print("🔍 API 서버 헬스 체크...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API 서버 정상")
            print(f"   응답: {response.json()}")
            return True
        else:
            print(f"❌ API 서버 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API 서버 연결 실패: {e}")
        return False

def test_system_info():
    """시스템 정보 조회"""
    print("\n🔍 시스템 정보 조회...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/system/info")
        if response.status_code == 200:
            data = response.json()
            print("✅ 시스템 정보 조회 성공")
            print(f"   모델: {data.get('model')}")
            print(f"   모드: {data.get('mode')}")
            print(f"   사용 가능한 모델: {len(data.get('available_models', []))}개")
            return True
        else:
            print(f"❌ 시스템 정보 조회 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 시스템 정보 조회 오류: {e}")
        return False

def test_session_creation():
    """세션 생성"""
    print("\n🔍 세션 생성 테스트...")
    try:
        session_id = f"test_session_{int(time.time())}"
        response = requests.post(
            f"{API_BASE_URL}/api/session/create",
            json={"session_id": session_id}
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ 세션 생성 성공")
            print(f"   세션 ID: {data.get('session_id')}")
            return session_id
        else:
            print(f"❌ 세션 생성 실패: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 세션 생성 오류: {e}")
        return None

def test_chat_message(session_id):
    """채팅 메시지 테스트"""
    print("\n🔍 채팅 메시지 테스트...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat/message",
            json={
                "message": "안녕하세요! 신약개발에 대해 간단히 설명해주세요.",
                "session_id": session_id,
                "conversation_history": []
            }
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ 채팅 메시지 성공")
            print(f"   응답 길이: {len(data.get('response', ''))} 문자")
            print(f"   응답 미리보기: {data.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ 채팅 메시지 실패: {response.status_code}")
            print(f"   오류: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 채팅 메시지 오류: {e}")
        return False

def test_mode_switching(session_id):
    """모드 전환 테스트"""
    print("\n🔍 모드 전환 테스트...")
    try:
        # Deep Research 모드로 전환
        response = requests.post(
            f"{API_BASE_URL}/api/system/mode/deep_research",
            json={"session_id": session_id}
        )
        if response.status_code == 200:
            print("✅ Deep Research 모드 전환 성공")
        else:
            print(f"❌ Deep Research 모드 전환 실패: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # 일반 모드로 되돌리기
        response = requests.post(
            f"{API_BASE_URL}/api/system/mode/normal",
            json={"session_id": session_id}
        )
        if response.status_code == 200:
            print("✅ 일반 모드 전환 성공")
            return True
        else:
            print(f"❌ 일반 모드 전환 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 모드 전환 오류: {e}")
        return False

def test_model_change(session_id):
    """모델 변경 테스트"""
    print("\n🔍 모델 변경 테스트...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/system/model",
            json={
                "model": "gemma3-12b:latest",
                "session_id": session_id
            }
        )
        if response.status_code == 200:
            print("✅ 모델 변경 성공")
            return True
        else:
            print(f"❌ 모델 변경 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 모델 변경 오류: {e}")
        return False

def main():
    """통합 테스트 실행"""
    print("🚀 WebUI-API 서버 통합 테스트 시작\n")
    
    # 1. 헬스 체크
    if not test_health():
        print("\n❌ API 서버가 실행되지 않았습니다. 서버를 먼저 시작해주세요.")
        return False
    
    # 2. 시스템 정보
    if not test_system_info():
        print("\n❌ 시스템 정보 조회 실패")
        return False
    
    # 3. 세션 생성
    session_id = test_session_creation()
    if not session_id:
        print("\n❌ 세션 생성 실패")
        return False
    
    # 4. 채팅 메시지
    if not test_chat_message(session_id):
        print("\n❌ 채팅 메시지 테스트 실패")
        return False
    
    # 5. 모드 전환
    if not test_mode_switching(session_id):
        print("\n❌ 모드 전환 테스트 실패")
        return False
    
    # 6. 모델 변경
    if not test_model_change(session_id):
        print("\n❌ 모델 변경 테스트 실패")
        return False
    
    print("\n🎉 모든 테스트 통과! WebUI-API 서버 통합이 정상 작동합니다.")
    return True

if __name__ == "__main__":
    main()