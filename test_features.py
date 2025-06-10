#!/usr/bin/env python3
"""
채팅봇 기능 테스트 스크립트
- 디버그 모드 토글
- 모델 우선순위
- 저장 프롬프트 기능
"""
import os
import sys
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

# 테스트 결과 저장
TEST_RESULTS = {}

class TestRunner:
    """테스트 실행 클래스"""
    
    def __init__(self):
        self.test_count = 0
        self.passed = 0
        self.failed = 0
    
    async def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 50)
        print("채팅봇 기능 테스트 시작")
        print("=" * 50)
        
        # 테스트 실행
        await self.test_debug_mode_toggle()
        await self.test_model_priority()
        await self.test_save_prompt()
        
        # 결과 출력
        print("\n" + "=" * 50)
        print(f"테스트 완료: 총 {self.test_count}개 테스트")
        print(f"통과: {self.passed}, 실패: {self.failed}")
        print("=" * 50)
    
    def record_result(self, test_name: str, passed: bool, message: str):
        """테스트 결과 기록"""
        self.test_count += 1
        status = "통과" if passed else "실패"
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        
        print(f"[{status}] {test_name}: {message}")
        TEST_RESULTS[test_name] = {"passed": passed, "message": message}
    
    async def test_debug_mode_toggle(self):
        """디버그 모드 토글 기능 테스트"""
        print("\n🧪 디버그 모드 토글 테스트 시작...")
        
        try:
            # chatbot.py 파일의 코드 확인
            chatbot_path = Path("src/cli/chatbot.py")
            if not chatbot_path.exists():
                self.record_result("디버그 모드 토글", False, "chatbot.py 파일이 존재하지 않음")
                return
            
            # 파일에서 디버그 모드 관련 코드 확인
            content = chatbot_path.read_text(encoding='utf-8')
            
            # debug_mode 설정 초기화 확인
            init_check = '"debug_mode"' in content and 'False' in content
            
            # /debug 명령어 처리 확인
            cmd_check = '/debug' in content and 'self.settings["debug_mode"] = not' in content
            
            # 디버그 출력 조건 확인
            output_check = 'if self.settings["debug_mode"]:' in content and '[디버그]' in content
            
            if init_check and cmd_check and output_check:
                self.record_result("디버그 모드 토글", True, "필요한 모든 코드가 구현되어 있습니다")
            else:
                issues = []
                if not init_check:
                    issues.append("설정 초기화 코드 누락")
                if not cmd_check:
                    issues.append("명령어 처리 코드 누락")
                if not output_check:
                    issues.append("디버그 출력 코드 누락")
                self.record_result("디버그 모드 토글", False, f"구현 불완전: {', '.join(issues)}")
        
        except Exception as e:
            self.record_result("디버그 모드 토글", False, f"테스트 중 오류 발생: {str(e)}")
    
    async def test_model_priority(self):
        """모델 우선순위 기능 테스트"""
        print("\n🧪 모델 우선순위 테스트 시작...")
        
        try:
            # chatbot.py 파일의 코드 확인
            chatbot_path = Path("src/cli/chatbot.py")
            if not chatbot_path.exists():
                self.record_result("모델 우선순위", False, "chatbot.py 파일이 존재하지 않음")
                return
            
            # 파일에서 모델 우선순위 관련 코드 확인
            content = chatbot_path.read_text(encoding='utf-8')
            
            # Gemma3:latest 우선 선택 확인
            gemma_priority = 'Gemma3:latest' in content and ('preferred_model' in content or 'priority' in content.lower())
            
            # 모델 자동 선택 확인
            auto_select = 'auto_select_model' in content or 'select_model' in content
            
            if gemma_priority and auto_select:
                self.record_result("모델 우선순위", True, "필요한 모든 코드가 구현되어 있습니다")
            else:
                issues = []
                if not gemma_priority:
                    issues.append("Gemma3:latest 우선순위 코드 누락")
                if not auto_select:
                    issues.append("모델 자동 선택 코드 누락")
                self.record_result("모델 우선순위", False, f"구현 불완전: {', '.join(issues)}")
        
        except Exception as e:
            self.record_result("모델 우선순위", False, f"테스트 중 오류 발생: {str(e)}")
    
    async def test_save_prompt(self):
        """저장 프롬프트 기능 테스트"""
        print("\n🧪 저장 프롬프트 테스트 시작...")
        
        try:
            # interface.py 파일의 코드 확인
            interface_path = Path("src/cli/interface.py")
            if not interface_path.exists():
                self.record_result("저장 프롬프트", False, "interface.py 파일이 존재하지 않음")
                return
            
            # 파일에서 저장 프롬프트 관련 코드 확인
            content = interface_path.read_text(encoding='utf-8')
            
            # ask_to_save 메서드 확인
            save_method = 'ask_to_save' in content
            
            # y/Enter 입력 처리 확인
            input_handling = "y" in content.lower() and ("input(" in content or "enter" in content.lower())
            
            # 한글 지원 확인
            korean_support = "네" in content or "예" in content
            
            # 저장 경로 출력 확인
            path_display = 'path' in content.lower() and ('print' in content.lower() or 'display' in content.lower())
            
            if save_method and input_handling:
                if korean_support and path_display:
                    self.record_result("저장 프롬프트", True, "필요한 모든 코드가 구현되어 있습니다")
                else:
                    extras = []
                    if not korean_support:
                        extras.append("한글 지원이 확인되지 않음")
                    if not path_display:
                        extras.append("저장 경로 출력이 확인되지 않음")
                    self.record_result("저장 프롬프트", True, f"기본 기능 구현됨, 추가 기능 미확인: {', '.join(extras)}")
            else:
                issues = []
                if not save_method:
                    issues.append("ask_to_save 메서드 누락")
                if not input_handling:
                    issues.append("y/Enter 입력 처리 코드 누락")
                self.record_result("저장 프롬프트", False, f"구현 불완전: {', '.join(issues)}")
        
        except Exception as e:
            self.record_result("저장 프롬프트", False, f"테스트 중 오류 발생: {str(e)}")

async def main():
    """메인 함수"""
    # 테스트 실행
    runner = TestRunner()
    await runner.run_all_tests()
    
    # 데모 사용법 표시
    if runner.passed > 0:
        print("\n📘 사용 가이드:")
        print("  1. 실행: python -m src.main")
        print("  2. 디버그 모드 토글: /debug 명령어 입력")
        print("  3. 저장 시: 'y' 입력, 건너뛰기: Enter 키 입력")
    
    return TEST_RESULTS

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n테스트가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n테스트 실행 중 오류 발생: {str(e)}")
