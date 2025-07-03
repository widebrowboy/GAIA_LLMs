#!/usr/bin/env python3
"""
모드 전환 테스트 스크립트
일반 모드 ↔ Deep Research 모드 전환 테스트
"""

import requests
import json
import time
from typing import Dict, Any


class ModeSwitchingTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session_id = None
        self.results = []
        
    def setup_session(self) -> bool:
        """테스트용 세션 생성"""
        try:
            response = requests.post(
                f"{self.base_url}/api/session/create",
                json={},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data['session_id']
                print(f"✅ 세션 생성 성공: {self.session_id}")
                return True
            else:
                print(f"❌ 세션 생성 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"💥 세션 생성 중 오류: {e}")
            return False
    
    def test_normal_mode(self) -> Dict[str, Any]:
        """일반 모드 테스트"""
        try:
            print("\n🔍 일반 모드 테스트...")
            
            # 일반 모드로 전환
            mode_response = requests.post(
                f"{self.base_url}/api/chat/command",
                json={
                    "command": "/normal",
                    "session_id": self.session_id
                },
                timeout=10
            )
            
            if mode_response.status_code != 200:
                return {"success": False, "error": f"일반 모드 전환 실패: HTTP {mode_response.status_code}"}
            
            # 일반 모드에서 질문
            chat_response = requests.post(
                f"{self.base_url}/api/chat/message",
                json={
                    "message": "아스피린의 기본적인 작용 메커니즘을 설명해주세요",
                    "session_id": self.session_id
                },
                timeout=30
            )
            
            if chat_response.status_code == 200:
                data = chat_response.json()
                mode = data.get('mode', 'unknown')
                response_length = len(data.get('response', ''))
                
                return {
                    "success": True,
                    "mode": mode,
                    "response_length": response_length,
                    "mcp_enabled": data.get('mcp_enabled', False)
                }
            else:
                return {"success": False, "error": f"일반 모드 채팅 실패: HTTP {chat_response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_deep_research_mode(self) -> Dict[str, Any]:
        """Deep Research 모드 테스트"""
        try:
            print("\n🔍 Deep Research 모드 테스트...")
            
            # Deep Research 모드로 전환
            mcp_response = requests.post(
                f"{self.base_url}/api/chat/command",
                json={
                    "command": "/mcp start",
                    "session_id": self.session_id
                },
                timeout=20
            )
            
            if mcp_response.status_code != 200:
                return {"success": False, "error": f"Deep Research 모드 전환 실패: HTTP {mcp_response.status_code}"}
            
            mcp_data = mcp_response.json()
            if not mcp_data.get('mcp_enabled', False):
                return {"success": False, "error": "MCP가 활성화되지 않음"}
            
            # Deep Research 모드에서 복잡한 질문
            research_response = requests.post(
                f"{self.base_url}/api/chat/message",
                json={
                    "message": "아스피린의 약물 상호작용과 새로운 치료제 개발 가능성을 종합적으로 분석해주세요",
                    "session_id": self.session_id
                },
                timeout=45
            )
            
            if research_response.status_code == 200:
                data = research_response.json()
                mode = data.get('mode', 'unknown')
                response_length = len(data.get('response', ''))
                
                return {
                    "success": True,
                    "mode": mode,
                    "response_length": response_length,
                    "mcp_enabled": data.get('mcp_enabled', False),
                    "sources": data.get('sources', [])
                }
            else:
                return {"success": False, "error": f"Deep Research 채팅 실패: HTTP {research_response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_mode_switching_sequence(self) -> Dict[str, Any]:
        """모드 전환 시퀀스 테스트"""
        try:
            print("\n🔍 모드 전환 시퀀스 테스트...")
            
            sequence_results = []
            
            # 1. Normal → Deep Research
            print("  📌 Normal → Deep Research")
            normal_to_deep = requests.post(
                f"{self.base_url}/api/chat/command",
                json={
                    "command": "/mcp start",
                    "session_id": self.session_id
                },
                timeout=15
            )
            
            if normal_to_deep.status_code == 200:
                sequence_results.append("Normal→Deep: 성공")
            else:
                sequence_results.append("Normal→Deep: 실패")
            
            time.sleep(2)
            
            # 2. Deep Research → Normal
            print("  📌 Deep Research → Normal")
            deep_to_normal = requests.post(
                f"{self.base_url}/api/chat/command",
                json={
                    "command": "/normal",
                    "session_id": self.session_id
                },
                timeout=15
            )
            
            if deep_to_normal.status_code == 200:
                sequence_results.append("Deep→Normal: 성공")
            else:
                sequence_results.append("Deep→Normal: 실패")
            
            time.sleep(2)
            
            # 3. Normal → Deep Research (재전환)
            print("  📌 Normal → Deep Research (재전환)")
            normal_to_deep_2 = requests.post(
                f"{self.base_url}/api/chat/command",
                json={
                    "command": "/mcp start",
                    "session_id": self.session_id
                },
                timeout=15
            )
            
            if normal_to_deep_2.status_code == 200:
                sequence_results.append("재전환 Normal→Deep: 성공")
            else:
                sequence_results.append("재전환 Normal→Deep: 실패")
            
            success_count = len([r for r in sequence_results if "성공" in r])
            total_count = len(sequence_results)
            
            return {
                "success": success_count == total_count,
                "sequence_results": sequence_results,
                "success_rate": f"{success_count}/{total_count}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_prompt_switching(self) -> Dict[str, Any]:
        """프롬프트 모드 전환 테스트"""
        try:
            print("\n🔍 프롬프트 모드 전환 테스트...")
            
            prompt_modes = ["clinical", "research", "chemistry", "regulatory", "default"]
            prompt_results = []
            
            for mode in prompt_modes:
                print(f"  📌 {mode} 프롬프트 모드")
                prompt_response = requests.post(
                    f"{self.base_url}/api/chat/command",
                    json={
                        "command": f"/prompt {mode}",
                        "session_id": self.session_id
                    },
                    timeout=10
                )
                
                if prompt_response.status_code == 200:
                    prompt_results.append(f"{mode}: 성공")
                else:
                    prompt_results.append(f"{mode}: 실패")
                
                time.sleep(1)
            
            success_count = len([r for r in prompt_results if "성공" in r])
            total_count = len(prompt_results)
            
            return {
                "success": success_count == total_count,
                "prompt_results": prompt_results,
                "success_rate": f"{success_count}/{total_count}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_all_tests(self):
        """모든 모드 전환 테스트 실행"""
        print("🚀 GAIA-BT 모드 전환 테스트 시작")
        print("=" * 50)
        
        # 세션 설정
        if not self.setup_session():
            print("❌ 세션 설정 실패로 테스트를 중단합니다.")
            return False
        
        # 테스트 시나리오들
        test_scenarios = [
            ("일반 모드 테스트", self.test_normal_mode),
            ("Deep Research 모드 테스트", self.test_deep_research_mode),
            ("모드 전환 시퀀스 테스트", self.test_mode_switching_sequence),
            ("프롬프트 모드 전환 테스트", self.test_prompt_switching)
        ]
        
        for test_name, test_func in test_scenarios:
            try:
                result = test_func()
                if result['success']:
                    print(f"✅ {test_name} 성공")
                    self.results.append({"test": test_name, "status": "PASS", "details": result})
                else:
                    print(f"❌ {test_name} 실패: {result.get('error', 'Unknown error')}")
                    self.results.append({"test": test_name, "status": "FAIL", "details": result})
            except Exception as e:
                print(f"💥 {test_name} 예외 발생: {e}")
                self.results.append({"test": test_name, "status": "ERROR", "details": str(e)})
        
        self.print_summary()
        
    def print_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 50)
        print("🎯 모드 전환 테스트 결과 요약")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.results if r['status'] == 'ERROR'])
        
        print(f"📊 총 테스트: {total_tests}")
        print(f"✅ 통과: {passed_tests}")
        print(f"❌ 실패: {failed_tests}")
        print(f"💥 오류: {error_tests}")
        print(f"📈 성공률: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0 or error_tests > 0:
            print("\n🔍 실패한 테스트:")
            for result in self.results:
                if result['status'] != 'PASS':
                    print(f"  • {result['test']}: {result['status']} - {result['details']}")
        
        print("\n" + "=" * 50)
        
        if passed_tests == total_tests:
            print("🎉 모든 모드 전환 테스트가 성공적으로 완료되었습니다!")
            return True
        else:
            print("⚠️  일부 모드 전환 테스트가 실패했습니다. 위의 오류를 확인해주세요.")
            return False


def main():
    """메인 함수"""
    tester = ModeSwitchingTester()
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())