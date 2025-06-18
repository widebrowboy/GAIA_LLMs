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
║                    📚 GAIA-BT v2.0 도움말 & 사용 가이드                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 기본 사용법:
  - 질문을 직접 입력하면 AI가 답변합니다
  - 명령어는 '/'로 시작하거나 '/' 없이도 사용 가능합니다

📋 기본 명령어:
  /help 또는 help           - 이 도움말 표시
  /debug 또는 debug         - 디버그 모드 토글
  /exit 또는 exit           - 챗봇 종료
  /model <이름>             - AI 모델 변경
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