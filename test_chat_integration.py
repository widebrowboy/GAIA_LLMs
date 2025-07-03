#!/usr/bin/env python3
"""
WebUI 대화 기능 통합 테스트 및 에러 감지
"""

import requests
import json
import time
import asyncio
import websockets
from urllib.parse import urljoin

API_BASE_URL = "http://localhost:8000"
WEBUI_BASE_URL = "http://localhost:3001"

class ChatIntegrationTester:
    def __init__(self):
        self.session_id = f"chat_test_{int(time.time())}"
        self.errors = []
        self.warnings = []
        
    def log_error(self, error_msg):
        """에러 로깅"""
        self.errors.append(error_msg)
        print(f"❌ ERROR: {error_msg}")
        
    def log_warning(self, warning_msg):
        """경고 로깅"""
        self.warnings.append(warning_msg)
        print(f"⚠️ WARNING: {warning_msg}")
        
    def log_success(self, success_msg):
        """성공 로깅"""
        print(f"✅ SUCCESS: {success_msg}")

    def test_api_connectivity(self):
        """API 서버 연결성 테스트"""
        print("\n🔍 API 서버 연결성 테스트...")
        
        try:
            # 1. Health check
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log_success("API Health check 통과")
            else:
                self.log_error(f"API Health check 실패: {response.status_code}")
                return False
                
            # 2. System info
            response = requests.get(f"{API_BASE_URL}/api/system/info", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_success(f"시스템 정보 조회 성공 - 모델: {data.get('model')}")
            else:
                self.log_error(f"시스템 정보 조회 실패: {response.status_code}")
                return False
                
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_error(f"API 서버 연결 실패: {e}")
            return False

    def test_session_creation(self):
        """세션 생성 테스트"""
        print("\n🔍 세션 생성 테스트...")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/session/create",
                json={"session_id": self.session_id},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_success(f"세션 생성 성공: {data.get('session_id')}")
                return True
            else:
                self.log_error(f"세션 생성 실패: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_error(f"세션 생성 요청 실패: {e}")
            return False

    def test_chat_message_basic(self):
        """기본 채팅 메시지 테스트"""
        print("\n🔍 기본 채팅 메시지 테스트...")
        
        test_messages = [
            "안녕하세요!",
            "신약개발이란 무엇인가요?",
            "아스피린의 작용 메커니즘을 설명해주세요."
        ]
        
        for i, message in enumerate(test_messages, 1):
            try:
                print(f"  📝 테스트 메시지 {i}: {message}")
                
                response = requests.post(
                    f"{API_BASE_URL}/api/chat/message",
                    json={
                        "message": message,
                        "session_id": self.session_id,
                        "conversation_history": []
                    },
                    timeout=30  # 30초 타임아웃
                )
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get('response', '')
                    if response_text:
                        self.log_success(f"메시지 {i} 응답 성공 ({len(response_text)} 문자)")
                        print(f"    응답 미리보기: {response_text[:100]}...")
                    else:
                        self.log_warning(f"메시지 {i} 응답이 비어있음")
                else:
                    self.log_error(f"메시지 {i} 응답 실패: {response.status_code}")
                    print(f"    오류 내용: {response.text}")
                    
                # 메시지 간 잠시 대기
                time.sleep(2)
                
            except requests.exceptions.Timeout:
                self.log_error(f"메시지 {i} 타임아웃 (30초 초과)")
            except requests.exceptions.RequestException as e:
                self.log_error(f"메시지 {i} 요청 실패: {e}")

    def test_mode_switching(self):
        """모드 전환 테스트"""
        print("\n🔍 모드 전환 테스트...")
        
        try:
            # Deep Research 모드로 전환
            response = requests.post(
                f"{API_BASE_URL}/api/system/mode/deep_research",
                json={"session_id": self.session_id},
                timeout=15
            )
            
            if response.status_code == 200:
                self.log_success("Deep Research 모드 전환 성공")
                
                # 짧은 메시지 테스트
                chat_response = requests.post(
                    f"{API_BASE_URL}/api/chat/message",
                    json={
                        "message": "Deep Research 모드 테스트입니다.",
                        "session_id": self.session_id,
                        "conversation_history": []
                    },
                    timeout=60  # Deep Research는 시간이 더 걸릴 수 있음
                )
                
                if chat_response.status_code == 200:
                    self.log_success("Deep Research 모드 채팅 성공")
                else:
                    self.log_error(f"Deep Research 모드 채팅 실패: {chat_response.status_code}")
            else:
                self.log_error(f"Deep Research 모드 전환 실패: {response.status_code}")
                
            time.sleep(2)
            
            # 일반 모드로 복귀
            response = requests.post(
                f"{API_BASE_URL}/api/system/mode/normal",
                json={"session_id": self.session_id},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_success("일반 모드 복귀 성공")
            else:
                self.log_error(f"일반 모드 복귀 실패: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_error(f"모드 전환 테스트 실패: {e}")

    def test_model_switching(self):
        """모델 전환 테스트"""
        print("\n🔍 모델 전환 테스트...")
        
        # 사용 가능한 모델 목록 가져오기
        try:
            response = requests.get(f"{API_BASE_URL}/api/system/info", timeout=5)
            if response.status_code == 200:
                data = response.json()
                available_models = data.get('available_models', [])
                
                if available_models:
                    # 첫 번째 사용 가능한 모델로 전환 테스트
                    test_model = available_models[0]
                    
                    model_response = requests.post(
                        f"{API_BASE_URL}/api/system/model",
                        json={
                            "model": test_model,
                            "session_id": self.session_id
                        },
                        timeout=10
                    )
                    
                    if model_response.status_code == 200:
                        self.log_success(f"모델 전환 성공: {test_model}")
                    else:
                        self.log_error(f"모델 전환 실패: {model_response.status_code}")
                else:
                    self.log_warning("사용 가능한 모델이 없음")
            else:
                self.log_error("모델 목록 조회 실패")
                
        except requests.exceptions.RequestException as e:
            self.log_error(f"모델 전환 테스트 실패: {e}")

    def test_webui_accessibility(self):
        """WebUI 접근성 테스트"""
        print("\n🔍 WebUI 접근성 테스트...")
        
        try:
            response = requests.get(WEBUI_BASE_URL, timeout=10)
            if response.status_code == 200:
                html_content = response.text
                
                # 중요한 UI 요소들 확인
                ui_elements = [
                    "새 대화",
                    "대화 기록", 
                    "시스템 상태",
                    "전문 프롬프트",
                    "GAIA-GPT"
                ]
                
                for element in ui_elements:
                    if element in html_content:
                        self.log_success(f"UI 요소 확인됨: {element}")
                    else:
                        self.log_warning(f"UI 요소 누락: {element}")
                        
            else:
                self.log_error(f"WebUI 접근 실패: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_error(f"WebUI 접근성 테스트 실패: {e}")

    def test_error_handling(self):
        """에러 처리 테스트"""
        print("\n🔍 에러 처리 테스트...")
        
        # 잘못된 세션 ID로 테스트
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/chat/message",
                json={
                    "message": "테스트",
                    "session_id": "invalid_session_123",
                    "conversation_history": []
                },
                timeout=10
            )
            
            if response.status_code in [200, 400, 404]:
                self.log_success("잘못된 세션 ID 처리 정상")
            else:
                self.log_warning(f"예상치 못한 응답 코드: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_warning(f"에러 처리 테스트 중 예외: {e}")
            
        # 빈 메시지 테스트
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/chat/message",
                json={
                    "message": "",
                    "session_id": self.session_id,
                    "conversation_history": []
                },
                timeout=10
            )
            
            if response.status_code in [200, 400]:
                self.log_success("빈 메시지 처리 정상")
            else:
                self.log_warning(f"빈 메시지 처리 예상치 못한 응답: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_warning(f"빈 메시지 테스트 중 예외: {e}")

    def generate_report(self):
        """테스트 결과 보고서 생성"""
        print("\n" + "="*60)
        print("📋 ChatIntegration 테스트 결과 보고서")
        print("="*60)
        
        print(f"\n📊 통계:")
        print(f"  - 에러: {len(self.errors)}개")
        print(f"  - 경고: {len(self.warnings)}개")
        
        if self.errors:
            print(f"\n❌ 발견된 에러들:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
                
        if self.warnings:
            print(f"\n⚠️ 경고사항들:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
                
        if not self.errors and not self.warnings:
            print("\n🎉 모든 테스트 통과! 에러나 경고사항이 없습니다.")
        elif not self.errors:
            print("\n✅ 주요 기능 정상, 일부 경고사항 있음")
        else:
            print("\n🔧 일부 에러 발견됨, 수정 필요")
            
        return len(self.errors) == 0

    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 WebUI-API 통합 채팅 테스트 시작")
        print("="*60)
        
        # 1. API 연결성
        if not self.test_api_connectivity():
            print("❌ API 서버 연결 실패로 테스트 중단")
            return False
            
        # 2. 세션 생성
        if not self.test_session_creation():
            print("❌ 세션 생성 실패로 일부 테스트 스킵")
        
        # 3. 기본 채팅
        self.test_chat_message_basic()
        
        # 4. 모드 전환
        self.test_mode_switching()
        
        # 5. 모델 전환
        self.test_model_switching()
        
        # 6. WebUI 접근성
        self.test_webui_accessibility()
        
        # 7. 에러 처리
        self.test_error_handling()
        
        # 8. 결과 보고서
        return self.generate_report()

def main():
    tester = ChatIntegrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 결론: WebUI-API 통합이 성공적으로 작동합니다!")
    else:
        print("\n🔧 결론: 일부 문제가 발견되었습니다. 로그를 확인하여 수정해주세요.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())