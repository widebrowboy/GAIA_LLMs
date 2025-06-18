class UserInterface:
    def __init__(self):
        try:
            from rich.console import Console
            self.console = Console()
        except ImportError:
            self.console = None
        self.display_error = self._display_error
        self.display_welcome = self._display_welcome
    
    def _display_error(self, message: str):
        print(f"❌ {message}")
    
    def _display_welcome(self):
        print("\n안녕하세요! GAIA-BT 챗봇입니다. 무엇을 도와드릴까요?")
        print("도움이 필요하시다면 '/help'를 입력해주세요.")

    async def get_user_input(self, prompt: str = "\n> ") -> str:
        """비동기 사용자 입력을 받습니다."""
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(None, input, prompt)

    def print_thinking(self, message: str = "🤔 답변을 생성 중입니다... 잠시만 기다려주세요."):
        print(message)
    
    def display_thinking(self, message: str):
        """사고 과정을 표시합니다."""
        print(f"💭 {message}")
    
    def display_response(self, response: str):
        """AI 응답을 표시합니다."""
        print(f"\n{response}\n")
    
    def display_help(self):
        """도움말을 표시합니다."""
        help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                  📚 GAIA-BT v2.0 Alpha 도움말 & 사용 가이드                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 기본 사용법:
  - 신약개발 관련 질문을 자연어로 입력하세요
  - 모든 답변에 과학적 근거와 참고문헌이 포함됩니다

📋 기본 명령어:
  /help 또는 help           - 이 도움말 표시
  /model <이름>             - AI 모델 변경 (예: gemma3:latest)
  /prompt <모드>            - 전문 프롬프트 변경 (clinical/research/chemistry)
  /debug 또는 debug         - 디버그 모드 토글
  /exit 또는 exit           - 챗봇 종료

🔬 고급 기능:
  /mcp                      - Deep Research 시스템 (전문 데이터베이스 연동)
  
💡 사용 예시:
  "아스피린의 작용 메커니즘을 설명해주세요"
  "EGFR 억제제의 임상 데이터를 분석해주세요"
        """
        print(help_text)
    
    def clear_screen(self):
        """화면을 지웁니다."""
        import os
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_settings(self, settings: dict):
        """현재 설정을 표시합니다."""
        print("\n📋 현재 설정:")
        for key, value in settings.items():
            print(f"  • {key}: {value}")
        print()
    
    def ask_to_save(self) -> bool:
        """저장 여부를 물어봅니다."""
        response = input("\n💾 이 대화를 저장하시겠습니까? (y/n): ").strip().lower()
        return response == 'y'
    
    def display_saved_notification(self, filepath: str):
        """저장 완료 알림을 표시합니다."""
        print(f"✅ 대화가 저장되었습니다: {filepath}")
    
    def display_feedback_progress(self, iteration: int, total: int):
        """피드백 진행 상황을 표시합니다."""
        print(f"🔄 피드백 반복 {iteration}/{total}...") 