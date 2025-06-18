"""
CLI 인터페이스 관리 모듈.

이 모듈은 CLI 기반 챗봇의 사용자 인터페이스 요소를 관리합니다.
터미널에 텍스트를 표시하고, 사용자 입력을 처리하며, 보기 좋은 형식으로 출력합니다.
"""

import asyncio
import os
import shutil
from typing import Any, Dict

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# 스타일 정의
STYLE = Style.from_dict({
    'prompt': '#00AAFF bold',
    'input': '#FFFFFF italic',
    'output': '#00AA00',
    'error': '#FF0000 bold',
})

# Rich 콘솔 초기화
console = Console()

class CliInterface:
    """
    CLI 인터페이스 관리 클래스.
    터미널 표시, 사용자 입력, 출력 형식을 관리합니다.
    """

    def __init__(self, app_name: str = "신약개발 연구 챗봇"):
        """
        CLI 인터페이스 초기화

        Args:
            app_name: 애플리케이션 이름
        """
        self.app_name = app_name
        self.session = PromptSession()
        self.console = console

        # 터미널 크기 가져오기
        self.terminal_width, self.terminal_height = shutil.get_terminal_size()

    def display_welcome(self):
        """시작 메시지와 사용 지침을 표시합니다."""
        from app.utils.config import OLLAMA_MODEL
        # GAIA-BT GPT 배너
        banner = """
[bold bright_blue]
 ██████╗  █████╗ ██╗ █████╗       ██████╗ ████████╗
██╔════╝ ██╔══██╗██║██╔══██╗      ██╔══██╗╚══██╔══╝
██║  ███╗███████║██║███████║█████╗██████╔╝   ██║   
██║   ██║██╔══██║██║██╔══██║╚════╝██╔══██╗   ██║   
╚██████╔╝██║  ██║██║██║  ██║      ██████╔╝   ██║   
 ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝      ╚═════╝    ╚═╝   
[/bold bright_blue]
[bold bright_cyan]                     G P T[/bold bright_cyan]
"""
        
        # 현재 프롬프트 정보 가져오기
        from app.utils.prompt_manager import get_prompt_manager
        prompt_manager = get_prompt_manager()
        default_prompt = prompt_manager.get_prompt_template("default")
        prompt_desc = default_prompt.description if default_prompt else "신약개발 전문 AI"
        
        # 소개글 - 간결한 설명
        intro_text = f"""[bold bright_green]🧪 GAIA-BT: 신약개발 전문 AI 연구 어시스턴트[/bold bright_green]

[bold yellow]💡 핵심 특징:[/bold yellow]
[green]✓[/green] [cyan]신약개발 전 과정 전문화[/cyan] - 타겟 발굴부터 임상시험까지
[green]✓[/green] [cyan]과학적 근거 기반 답변[/cyan] - 모든 응답에 참고문헌 포함
[green]✓[/green] [cyan]전문 프롬프트 시스템[/cyan] - 목적에 맞는 맞춤형 응답

[bold magenta]🤖 현재 AI 모델: {OLLAMA_MODEL}[/bold magenta]
[dim bright_yellow]💡 모델 변경: /model <모델명> | 프롬프트 변경: /prompt <모드>[/dim bright_yellow]

[bold cyan]🎯 현재 프롬프트: default ({prompt_desc})[/bold cyan]

[dim bright_cyan]분자 구조 분석부터 임상 연구 데이터까지, 신뢰할 수 있는 신약개발 정보를 제공합니다.[/dim bright_cyan]
"""

        welcome_text = """
[bold bright_blue]💬 기본 사용법[/bold bright_blue]
📝 [cyan]신약개발 질문[/cyan] - 일반적인 질문을 자연어로 입력하세요
🎯 [cyan]전문 프롬프트[/cyan] - 임상/연구/화학/규제 전문 모드 활용
📚 [cyan]과학적 근거[/cyan] - 모든 답변에 참고문헌 및 근거 포함

[bold yellow]⚡ 사용 예시:[/bold yellow]
[bright_green]"아스피린의 작용 메커니즘을 설명해주세요"[/bright_green]
[bright_green]"EGFR 억제제의 부작용은 무엇인가요?"[/bright_green]
[bright_green]"임상시험 1상과 2상의 차이점은?"[/bright_green]

[bold cyan]🔧 고급 기능:[/bold cyan]
[bright_green]/help[/bright_green] - 모든 명령어 및 고급 기능 확인
[bright_green]/mcp[/bright_green] - Deep Research 시스템 (전문 데이터베이스 연동)
[bright_green]/prompt[/bright_green] - 전문 프롬프트 모드 변경

[dim bright_yellow]💡 궁금한 신약개발 관련 질문을 자유롭게 입력해보세요![/dim bright_yellow]
        """

        # 배너 출력 (왼쪽 정렬)
        self.console.print(banner, justify="left")
        
        # 소개글 출력
        self.console.print(Panel.fit(
            intro_text,
            border_style="bright_cyan",
            padding=(0, 1),
            width=min(90, self.terminal_width - 4)
        ))
        
        # 기능 안내 출력
        self.console.print(Panel.fit(
            welcome_text,
            title="🔬 신약개발 전문 기능",
            border_style="bright_blue",
            padding=(1, 2),
            width=min(95, self.terminal_width - 4)
        ))

    def display_help(self):
        """도움말 정보를 표시합니다."""
        help_text = """
[bold]🔍 챗봇 사용 방법[/bold]

[bold cyan]1. 기본 사용법[/bold cyan]
질문을 입력하시면 AI가 신약개발에 대한 정보를 제공합니다.
각 응답은 과학적 근거와 최소 2개 이상의 참고문헌을 포함합니다.

[bold cyan]2. 명령어[/bold cyan]
- [cyan]/exit[/cyan] 또는 [cyan]/quit[/cyan] - 프로그램 종료
- [cyan]/help[/cyan] - 현재 도움말 표시
- [cyan]/feedback[/cyan] - 피드백 루프 활성화 (더 깊은 연구 수행)
- [cyan]/mcp[/cyan] - MCP 툴 관리 (고급 연구 기능)
- [cyan]/model[/cyan] - AI 모델 변경 (사용 예: /model txgemma-chat)
- [cyan]/settings[/cyan] - 설정 변경
- [cyan]/clear[/cyan] - 화면 지우기

[bold cyan]3. 피드백 모드[/bold cyan]
'/feedback 질문' 형식으로 입력하면 더 깊은 연구를 수행합니다.
여러 응답을 생성하고 최적의 답변을 선택하는 피드백 루프를 실행합니다.
결과는 파일로 저장됩니다.

[bold cyan]4. 설정 변경[/bold cyan]
'/settings' 명령으로 피드백 깊이/너비, 응답 길이 등을 조정할 수 있습니다.
        """

        self.console.print(Panel(
            help_text,
            title="📚 도움말",
            border_style="green",
            padding=(1, 2),
            width=min(100, self.terminal_width - 4)
        ))

    async def get_user_input(self, prompt_text: str = "질문") -> str:
        """
        사용자 입력을 받습니다.

        Args:
            prompt_text: 프롬프트로 표시할 텍스트

        Returns:
            str: 사용자가 입력한 텍스트
        """
        prompt_html = HTML(f'<prompt>{prompt_text} > </prompt>')
        user_input = await asyncio.to_thread(
            lambda: self.session.prompt(prompt_html, style=STYLE)
        )
        return user_input.strip()

    def display_thinking(self):
        """AI가 생각 중임을 표시하는 스피너를 반환합니다."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]응답 생성 중...[/bold blue]"),
            transient=True
        )
    
    def print_thinking(self, message: str):
        """MCP Deep Search 진행 상황을 표시합니다."""
        self.console.print(f"[dim cyan]🔍 {message}[/dim cyan]")

    def display_response(self, response: str, show_references: bool = True):
        """
        AI 응답을 마크다운 형식으로 표시합니다.

        Args:
            response: 표시할 마크다운 형식의 텍스트
            show_references: 참고문헌 섹션을 강조할지 여부
        """
        # 응답 내용 확인
        if not response or response.isspace():
            print("[경고] 응답이 비어있습니다.")
            return

        # 디버그 출력 제거 - 마크다운 렌더링만 표시

        try:
            # 참고문헌 강조
            if show_references and "참고 문헌" in response:
                parts = response.split("## 참고 문헌", 1)
                if len(parts) > 1:
                    content = parts[0]
                    refs = "## 참고 문헌" + parts[1]

                    # 콘텐츠 표시
                    self.console.print(Markdown(content))

                    # 참고문헌 강조 표시
                    self.console.print(Panel(
                        Markdown(refs),
                        title="참고 문헌",
                        border_style="yellow",
                        padding=(1, 1)
                    ))
                    return

            # 일반 마크다운 표시 시도
            self.console.print(Markdown(response))
        except Exception as e:
            # Rich 라이브러리에 문제가 있는 경우 기본 텍스트로 표시
            print(f"[경고] 마크다운 렌더링 오류: {e!s}")
            print(response)

    def display_settings(self, settings: Dict[str, Any]):
        """
        현재 설정을 테이블 형식으로 표시합니다.

        Args:
            settings: 표시할 설정 사전
        """
        table = Table(title="⚙️ 현재 설정")

        table.add_column("설정", style="cyan")
        table.add_column("값", style="green")
        table.add_column("설명", style="white")

        for key, value in settings.items():
            if key == "feedback_depth":
                table.add_row("피드백 깊이", str(value), "AI가 자체 답변을 개선하는 횟수")
            elif key == "feedback_width":
                table.add_row("피드백 너비", str(value), "각 단계에서 생성할 대체 답변 수")
            elif key == "min_response_length":
                table.add_row("최소 응답 길이", str(value), "최소 응답 길이 (문자)")
            elif key == "min_references":
                table.add_row("최소 참고문헌", str(value), "최소 참고문헌 수")
            elif key == "model":
                table.add_row("AI 모델", str(value), "사용 중인 Ollama 모델")
            else:
                table.add_row(key, str(value), "")

        self.console.print(table)

    def display_error(self, message: str):
        """
        오류 메시지를 표시합니다.

        Args:
            message: 표시할 오류 메시지
        """
        self.console.print(f"[bold red]오류:[/bold red] {message}")

    def clear_screen(self):
        """화면을 지웁니다."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_feedback_progress(self, current: int, total: int, stage: str):
        """
        피드백 루프 진행 상황을 표시합니다.

        Args:
            current: 현재 단계
            total: 총 단계 수
            stage: 단계 설명
        """
        self.console.print(f"[bold blue]피드백 루프:[/bold blue] {current}/{total} - {stage}")

    def display_saved_notification(self, file_path: str) -> None:
        """
        저장 완료 알림 표시

        Args:
            file_path: 저장된 파일 경로
        """
        # 절대 경로로 변환
        import os
        absolute_path = os.path.abspath(file_path)

        self.console.print("[bold green] 연구 결과가 저장되었습니다![/bold green]")
        self.console.print(f"[green]파일 경로: {absolute_path}[/green]")
        self.console.print(f"[저장 폴더: {os.path.dirname(absolute_path)}]")
        self.console.print("")

    async def ask_to_save(self) -> bool:
        """
        사용자에게 결과를 저장할지 묻습니다.
        엔터키를 누르면 저장하지 않고, y를 입력하면 저장합니다.

        Returns:
            bool: 저장 여부 (True: 저장함, False: 저장 안함)
        """
        # 저장 여부 메시지를 바로 출력
        print("\n이 결과를 저장하시겠습니까? (y 입력 = 저장, Enter = 넘어가기) > ", end="", flush=True)

        # 프롬프트 툴킷 대신 직접 input을 사용하여 즉시 응답 받기
        # 비동기 처리를 위해 run_in_executor 사용
        loop = asyncio.get_event_loop()
        user_input = await loop.run_in_executor(None, input)

        # 빈 입력(엔터키)는 False로 처리, 'y'나 'Y'는 True로 처리
        save_choice = user_input.strip().lower() in ('y', 'yes', '예', '네')

        if not save_choice:
            print("저장하지 않고 계속 진행합니다.")

        return save_choice
