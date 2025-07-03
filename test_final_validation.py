#!/usr/bin/env python3
"""
최종 검증 테스트 스크립트
핵심 기능들이 정상 작동하는지 빠르게 검증
"""

import requests
import time
from typing import Dict, Any, List


class FinalValidationTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.webui_url = "http://localhost:3001"
        self.session_id = None
        self.results = []
        
    def setup_session(self) -> bool:
        """검증용 세션 생성"""
        try:
            response = requests.post(
                f"{self.base_url}/api/session/create",
                json={},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data['session_id']
                print(f"✅ 검증 세션 생성: {self.session_id}")
                return True
            else:
                print(f"❌ 세션 생성 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"💥 세션 생성 중 오류: {e}")
            return False
    
    def test_api_health(self) -> Dict[str, Any]:
        """API 서버 상태 확인"""
        try:
            print("\n🔍 API 서버 상태 확인...")
            
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                return {"success": True, "status": "healthy"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_webui_access(self) -> Dict[str, Any]:
        """WebUI 접근 테스트"""
        try:
            print("\n🔍 WebUI 접근 테스트...")
            
            # Modern WebUI 테스트
            modern_response = requests.get(f"{self.webui_url}/modern", timeout=5)
            modern_ok = modern_response.status_code == 200
            
            # 기존 WebUI 테스트
            legacy_response = requests.get(f"{self.webui_url}/", timeout=5)
            legacy_ok = legacy_response.status_code == 200
            
            return {
                "success": modern_ok or legacy_ok,
                "modern_webui": modern_ok,
                "legacy_webui": legacy_ok
            }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_basic_chat(self) -> Dict[str, Any]:
        """기본 채팅 기능 테스트"""
        try:
            print("\n🔍 기본 채팅 기능 테스트...")
            
            chat_response = requests.post(
                f"{self.base_url}/api/chat/message",
                json={
                    "message": "안녕하세요, 간단한 테스트입니다",
                    "session_id": self.session_id
                },
                timeout=15
            )
            
            if chat_response.status_code == 200:
                data = chat_response.json()
                response_text = data.get('response', '')
                
                return {
                    "success": len(response_text) > 10,
                    "response_length": len(response_text),
                    "mode": data.get('mode', 'unknown')
                }
            else:
                return {"success": False, "error": f"HTTP {chat_response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_command_execution(self) -> Dict[str, Any]:
        """명령어 실행 테스트"""
        try:
            print("\n🔍 명령어 실행 테스트...")
            
            # 간단한 명령어 테스트
            cmd_response = requests.post(
                f"{self.base_url}/api/chat/command",
                json={
                    "command": "/help",
                    "session_id": self.session_id
                },
                timeout=10
            )
            
            if cmd_response.status_code == 200:
                return {"success": True, "command": "/help executed"}
            else:
                return {"success": False, "error": f"HTTP {cmd_response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_mode_switching(self) -> Dict[str, Any]:
        """모드 전환 테스트 (빠른 버전)"""
        try:
            print("\n🔍 모드 전환 테스트...")
            
            # MCP 모드 활성화
            mcp_response = requests.post(
                f"{self.base_url}/api/chat/command",
                json={
                    "command": "/mcp start",
                    "session_id": self.session_id
                },
                timeout=10
            )
            
            mcp_success = mcp_response.status_code == 200
            
            # 일반 모드로 복귀
            normal_response = requests.post(
                f"{self.base_url}/api/chat/command",
                json={
                    "command": "/normal",
                    "session_id": self.session_id
                },
                timeout=10
            )
            
            normal_success = normal_response.status_code == 200
            
            return {
                "success": mcp_success and normal_success,
                "mcp_mode": mcp_success,
                "normal_mode": normal_success
            }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_system_info(self) -> Dict[str, Any]:
        """시스템 정보 확인"""
        try:
            print("\n🔍 시스템 정보 확인...")
            
            info_response = requests.get(f"{self.base_url}/api/system/info", timeout=10)
            
            if info_response.status_code == 200:
                info = info_response.json()
                
                return {
                    "success": True,
                    "ollama_connected": info.get('ollama_status', {}).get('connected', False),
                    "available_models": len(info.get('available_models', [])),
                    "current_model": info.get('current_model', 'unknown')
                }
            else:
                return {"success": False, "error": f"HTTP {info_response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_validation(self):
        """모든 검증 테스트 실행"""
        print("🚀 GAIA-BT 최종 검증 테스트 시작")
        print("=" * 50)
        
        # 세션 설정
        if not self.setup_session():
            print("❌ 세션 설정 실패로 검증을 중단합니다.")
            return False
        
        # 검증 테스트 시나리오들
        validation_tests = [
            ("API 서버 상태", self.test_api_health),
            ("WebUI 접근", self.test_webui_access),
            ("기본 채팅", self.test_basic_chat),
            ("명령어 실행", self.test_command_execution),
            ("모드 전환", self.test_mode_switching),
            ("시스템 정보", self.test_system_info)
        ]
        
        for test_name, test_func in validation_tests:
            try:
                result = test_func()
                if result['success']:
                    print(f"✅ {test_name} 검증 성공")
                    self.results.append({"test": test_name, "status": "PASS", "details": result})
                else:
                    print(f"❌ {test_name} 검증 실패: {result.get('error', 'Unknown error')}")
                    self.results.append({"test": test_name, "status": "FAIL", "details": result})
            except Exception as e:
                print(f"💥 {test_name} 검증 예외: {e}")
                self.results.append({"test": test_name, "status": "ERROR", "details": str(e)})
        
        self.print_validation_summary()
        return self.evaluate_system_status()
        
    def evaluate_system_status(self) -> bool:
        """시스템 상태 평가"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASS'])
        
        # 핵심 기능들 확인
        critical_tests = ["API 서버 상태", "WebUI 접근", "기본 채팅"]
        critical_passed = 0
        
        for result in self.results:
            if result['test'] in critical_tests and result['status'] == 'PASS':
                critical_passed += 1
        
        # 핵심 기능 모두 통과 + 전체 70% 이상 통과
        return critical_passed == len(critical_tests) and (passed_tests / total_tests) >= 0.7
        
    def print_validation_summary(self):
        """검증 결과 요약 출력"""
        print("\n" + "=" * 50)
        print("🎯 GAIA-BT 최종 검증 결과")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.results if r['status'] == 'ERROR'])
        
        print(f"📊 총 검증 항목: {total_tests}")
        print(f"✅ 통과: {passed_tests}")
        print(f"❌ 실패: {failed_tests}")
        print(f"💥 오류: {error_tests}")
        print(f"📈 성공률: {(passed_tests/total_tests)*100:.1f}%")
        
        # 핵심 기능 상태
        print(f"\n🔥 핵심 기능 상태:")
        critical_tests = ["API 서버 상태", "WebUI 접근", "기본 채팅"]
        for result in self.results:
            if result['test'] in critical_tests:
                status_icon = "✅" if result['status'] == 'PASS' else "❌"
                print(f"  {status_icon} {result['test']}")
        
        # 상세 정보
        print(f"\n📋 상세 검증 결과:")
        for result in self.results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"  {status_icon} {result['test']}: {result['status']}")
        
        print("\n" + "=" * 50)
        
        overall_success = self.evaluate_system_status()
        if overall_success:
            print("🎉 GAIA-BT 시스템이 정상적으로 작동합니다!")
            print("✨ 모든 핵심 기능이 검증되어 사용 준비가 완료되었습니다.")
            print("\n📍 접속 정보:")
            print("  • API 서버: http://localhost:8000")
            print("  • Modern WebUI: http://localhost:3001/modern")
            print("  • 기존 WebUI: http://localhost:3001")
            print("  • API 문서: http://localhost:8000/docs")
        else:
            print("⚠️  시스템에 일부 문제가 있어 추가 점검이 필요합니다.")
            print("🔧 실패한 항목들을 확인하여 수정해주세요.")
        
        return overall_success


def main():
    """메인 함수"""
    tester = FinalValidationTester()
    success = tester.run_validation()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())