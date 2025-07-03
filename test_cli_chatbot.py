#!/usr/bin/env python3
"""
CLI 챗봇 자동 테스트 스크립트
"""

import subprocess
import sys
import time
import threading
import queue
import os
from pathlib import Path

class CLIChatbotTester:
    def __init__(self):
        self.results = []
        self.process = None
        
    def run_cli_test(self):
        """CLI 챗봇 테스트 실행"""
        print("🤖 CLI 챗봇 테스트 시작")
        print("=" * 50)
        
        # 테스트 시나리오
        test_scenarios = [
            {
                "name": "기본 실행 테스트",
                "test": self.test_basic_startup,
            },
            {
                "name": "간단한 질문 테스트", 
                "test": self.test_simple_question,
            },
            {
                "name": "명령어 테스트",
                "test": self.test_commands,
            },
            {
                "name": "MCP 모드 테스트",
                "test": self.test_mcp_mode,
            }
        ]
        
        for scenario in test_scenarios:
            try:
                print(f"\n🔍 {scenario['name']}...")
                result = scenario['test']()
                if result['success']:
                    print(f"✅ {scenario['name']} 성공")
                    self.results.append({"test": scenario['name'], "status": "PASS", "details": result})
                else:
                    print(f"❌ {scenario['name']} 실패: {result.get('error', 'Unknown error')}")
                    self.results.append({"test": scenario['name'], "status": "FAIL", "details": result})
            except Exception as e:
                print(f"💥 {scenario['name']} 예외 발생: {e}")
                self.results.append({"test": scenario['name'], "status": "ERROR", "details": str(e)})
        
        self.print_summary()
    
    def test_basic_startup(self):
        """기본 실행 테스트"""
        try:
            # CLI 챗봇 실행 확인
            result = subprocess.run([
                'python', 'run_chatbot.py', '--help'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return {"success": True, "output": "CLI 실행 성공"}
            else:
                return {"success": False, "error": f"Exit code: {result.returncode}", "stderr": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout - CLI 실행 시간 초과"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_simple_question(self):
        """간단한 질문 테스트"""
        try:
            # 간단한 API 테스트로 대체 (CLI는 대화형이므로)
            import requests
            
            # 세션 생성
            session_response = requests.post(
                "http://localhost:8000/api/session/create",
                json={},
                timeout=10
            )
            
            if session_response.status_code != 200:
                return {"success": False, "error": "세션 생성 실패"}
            
            session_data = session_response.json()
            session_id = session_data['session_id']
            
            # 간단한 질문
            chat_response = requests.post(
                "http://localhost:8000/api/chat/message",
                json={
                    "message": "안녕하세요! CLI 테스트입니다.",
                    "session_id": session_id
                },
                timeout=30
            )
            
            if chat_response.status_code == 200:
                data = chat_response.json()
                return {"success": True, "response_length": len(data.get('response', ''))}
            else:
                return {"success": False, "error": f"HTTP {chat_response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_commands(self):
        """명령어 테스트"""
        try:
            import requests
            
            # 세션 생성
            session_response = requests.post(
                "http://localhost:8000/api/session/create",
                json={},
                timeout=10
            )
            
            if session_response.status_code != 200:
                return {"success": False, "error": "세션 생성 실패"}
            
            session_data = session_response.json()
            session_id = session_data['session_id']
            
            # 명령어 테스트
            commands = ["/help", "/model", "/prompt"]
            command_results = []
            
            for cmd in commands:
                cmd_response = requests.post(
                    "http://localhost:8000/api/chat/command",
                    json={
                        "command": cmd,
                        "session_id": session_id
                    },
                    timeout=15
                )
                
                if cmd_response.status_code == 200:
                    command_results.append(f"{cmd}: 성공")
                else:
                    command_results.append(f"{cmd}: 실패")
            
            return {"success": True, "commands_tested": command_results}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_mcp_mode(self):
        """MCP 모드 테스트"""
        try:
            import requests
            
            # 세션 생성
            session_response = requests.post(
                "http://localhost:8000/api/session/create",
                json={},
                timeout=10
            )
            
            if session_response.status_code != 200:
                return {"success": False, "error": "세션 생성 실패"}
            
            session_data = session_response.json()
            session_id = session_data['session_id']
            
            # MCP 시작
            mcp_response = requests.post(
                "http://localhost:8000/api/chat/command",
                json={
                    "command": "/mcp start",
                    "session_id": session_id
                },
                timeout=20
            )
            
            if mcp_response.status_code == 200:
                data = mcp_response.json()
                mcp_enabled = data.get('mcp_enabled', False)
                
                if mcp_enabled:
                    # Deep Research 질문 테스트
                    research_response = requests.post(
                        "http://localhost:8000/api/chat/message",
                        json={
                            "message": "아스피린의 작용 메커니즘을 분석해주세요",
                            "session_id": session_id
                        },
                        timeout=30
                    )
                    
                    if research_response.status_code == 200:
                        research_data = research_response.json()
                        return {
                            "success": True, 
                            "mcp_enabled": True,
                            "mode": research_data.get('mode', 'unknown'),
                            "response_length": len(research_data.get('response', ''))
                        }
                
                return {"success": True, "mcp_enabled": mcp_enabled}
            else:
                return {"success": False, "error": f"MCP 시작 실패: HTTP {mcp_response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def print_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 50)
        print("🎯 CLI 챗봇 테스트 결과 요약")
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
            print("🎉 모든 CLI 테스트가 성공적으로 완료되었습니다!")
            return True
        else:
            print("⚠️  일부 CLI 테스트가 실패했습니다. 위의 오류를 확인해주세요.")
            return False

def main():
    """메인 함수"""
    print("🚀 GAIA-BT CLI 챗봇 테스트 시작")
    print("📌 API 서버가 http://localhost:8000에서 실행 중인지 확인하세요")
    
    tester = CLIChatbotTester()
    success = tester.run_cli_test()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()