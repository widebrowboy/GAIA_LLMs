#!/usr/bin/env python3
"""
GAIA-BT 신약개발 연구 챗봇 실행 스크립트
통합 Deep Research MCP 시스템 v2.0
"""

import sys
import os
import asyncio
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def display_startup_banner():
    """시작 배너 표시"""
    from app.utils.config import OLLAMA_MODEL
    from app.utils.prompt_manager import get_prompt_manager
    
    # 현재 프롬프트 정보 가져오기
    prompt_manager = get_prompt_manager()
    default_prompt = prompt_manager.get_prompt_template("default")
    prompt_desc = default_prompt.description if default_prompt else "신약개발 전문 AI"
    
    # 프롬프트 설명 포맷팅
    prompt_text = f"default ({prompt_desc[:35]}{'...' if len(prompt_desc) > 35 else ''})"
    
    banner = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       🧬 GAIA-BT v2.0 Alpha 🧬                             ║
║                     신약개발 연구 AI 어시스턴트                                  ║
║                                                                              ║
║  💊 신약개발 전문 AI - 분자부터 임상까지 전 과정 지원                        ║
║  🧬 과학적 근거 기반 답변 - 참고문헌과 함께 제공                             ║
║  🎯 전문 프롬프트 시스템 - 목적에 맞는 전문화된 응답                         ║
║                                                                              ║
║  🤖 현재 AI 모델: {OLLAMA_MODEL:<55} ║
║  💡 모델 변경: /model <모델명> (예: /model gemma3:latest)                    ║
║  🎯 현재 프롬프트: {prompt_text:<52} ║
║  🔧 프롬프트 변경: /prompt <모드> (clinical/research/chemistry/regulatory)    ║
║                                                                              ║
║  📚 고급 기능: /help로 모든 명령어 확인 | /mcp로 Deep Research 시작          ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

async def run_chatbot_interactive():
    """대화형 챗봇 실행"""
    try:
        from app.cli.chatbot import DrugDevelopmentChatbot, Config
        
        # 시작 배너 표시
        display_startup_banner()
        
        # 챗봇 초기화
        config = Config(debug_mode=False)
        chatbot = DrugDevelopmentChatbot(config)
        
        # GAIA-BT 환영 메시지
        chatbot.interface.display_welcome()
        
        # API 연결 확인
        print("🔗 시스템 초기화 중...")
        status = await chatbot.client.check_availability()
        if not status:
            print("❌ Ollama API를 사용할 수 없습니다.")
            return
        
        print("✅ Ollama API 연결 성공")
        
        # 모델 확인
        model_check = await chatbot.auto_select_model()
        if not model_check:
            print("❌ 사용 가능한 모델이 없습니다.")
            print("🔧 해결방법: ollama pull gemma3:latest")
            return
        
        print("✅ AI 모델 준비 완료")
        
        # 일반 모드 배너 표시
        chatbot._show_mode_banner()
        
        # 기본 사용법 안내
        print("\n" + "="*80)
        print("💬 신약개발 질문을 입력하거나 명령어를 사용하세요:")
        print("📝 예시: \"아스피린의 작용 메커니즘을 설명해주세요\"")
        print("🔧 고급 기능: '/help' 명령어로 전체 기능을 확인하세요")
        print("="*80)
        
        # 메인 대화 루프
        while True:
            try:
                # 입력 받기 (터미널 환경 확인)
                try:
                    user_input = input("\n> ").strip()
                except EOFError:
                    print("\n👋 입력이 종료되었습니다.")
                    break
                
                if not user_input:
                    continue
                
                # 입력 정규화 (잠재적 인코딩 문제 해결)
                user_input = user_input.strip().replace('\u200b', '').replace('\ufeff', '')  # 제로폭 공백 제거
                
                # 디버그: 입력 문자열 분석
                if chatbot.config.debug_mode:
                    print(f"🐛 [디버그] 입력 원본: repr='{repr(user_input)}', 길이={len(user_input)}")
                    print(f"🐛 [디버그] 첫 글자: '{user_input[0] if user_input else 'None'}' (ASCII: {ord(user_input[0]) if user_input else 'None'})")
                    print(f"🐛 [디버그] startswith('/'): {user_input.startswith('/')}")
                
                # 종료 명령어 처리 (여러 형태 지원)
                if user_input.lower() in ['/exit', 'exit', 'quit', 'q', '/quit', '/q']:
                    print("👋 챗봇을 종료합니다.")
                    break
                
                # 명령어 정규화 - '/' 없이 입력된 명령어도 처리
                normalized_input = user_input
                if not user_input.startswith("/") and user_input.split()[0] in ['help', 'mcp', 'model', 'prompt', 'debug', 'exit', 'normal']:
                    normalized_input = "/" + user_input
                    if chatbot.config.debug_mode:
                        print(f"🐛 [디버그] 명령어 정규화: '{user_input}' → '{normalized_input}'")
                
                # 명령어 처리
                if normalized_input.startswith("/"):
                    # 디버그: 명령어 감지 확인
                    if chatbot.config.debug_mode:
                        print(f"🐛 [디버그] 명령어 감지: '{normalized_input}'")
                    
                    if normalized_input == "/help":
                        print_help()
                    elif normalized_input.startswith("/mcp"):
                        # MCP 명령어 부분 추출 (공백 문제 해결)
                        mcp_args = normalized_input[4:].strip()  # "/mcp" 제거하고 공백 정리
                        
                        if chatbot.config.debug_mode:
                            print(f"🐛 [디버그] MCP 명령어 처리: '{mcp_args}'")
                        
                        # MCP 사용 가능성 확인
                        if chatbot.mcp_commands is None:
                            print("❌ MCP 기능을 사용할 수 없습니다. MCP 모듈을 설치해주세요.")
                        else:
                            try:
                                await chatbot.mcp_commands.handle_mcp_command(mcp_args)
                            except Exception as e:
                                print(f"❌ MCP 명령어 처리 중 오류: {e}")
                                if chatbot.config.debug_mode:
                                    import traceback
                                    print(f"🐛 [디버그] MCP 오류 상세: {traceback.format_exc()}")
                    elif normalized_input.startswith("/model"):
                        parts = normalized_input.split(maxsplit=1)
                        if len(parts) > 1:
                            await chatbot.change_model(parts[1])
                        else:
                            print("사용법: /model <모델명>")
                    elif normalized_input.startswith("/prompt"):
                        parts = normalized_input.split(maxsplit=1)
                        prompt_type = parts[1] if len(parts) > 1 else None
                        await chatbot.change_prompt(prompt_type)
                    elif normalized_input == "/debug":
                        # 디버그 모드 토글
                        chatbot.config.debug_mode = not chatbot.config.debug_mode
                        chatbot.client.set_debug_mode(chatbot.config.debug_mode)
                        state = "켜짐" if chatbot.config.debug_mode else "꺼짐"
                        print(f"🐛 디버그 모드가 {state}으로 설정되었습니다.")
                    elif normalized_input == "/normal":
                        # 일반 모드로 전환
                        chatbot.switch_to_normal_mode()
                        print("🔄 일반 모드로 전환되었습니다.")
                    else:
                        print(f"❌ 알 수 없는 명령어: {normalized_input}")
                        print("사용 가능한 명령어: /help, /mcp, /model, /prompt, /debug, /normal, /exit")
                        print("💡 팁: '/' 없이도 명령어를 사용할 수 있습니다 (예: mcp start)")
                else:
                    # 특별 MCP 명령어 패턴 확인 (추가 안전장치)
                    # 다양한 형태의 mcp 명령어 지원
                    mcp_patterns = [
                        'mcp start', '/mcp start', 'mcp status', '/mcp status',
                        'mcp stop', '/mcp stop', 'mcp test', '/mcp test',
                        'mcp help', '/mcp help', 'mcp test deep', '/mcp test deep'
                    ]
                    
                    user_lower = user_input.lower().strip()
                    if any(user_lower.startswith(pattern) for pattern in mcp_patterns):
                        command_part = user_lower.replace('/', '').strip()
                        if chatbot.config.debug_mode:
                            print(f"🐛 [디버그] 특별 MCP 명령어 감지: '{command_part}'")
                        
                        if chatbot.mcp_commands is None:
                            print("❌ MCP 기능을 사용할 수 없습니다. MCP 모듈을 설치해주세요.")
                        else:
                            try:
                                mcp_args = command_part[3:].strip()  # "mcp" 제거
                                await chatbot.mcp_commands.handle_mcp_command(mcp_args)
                            except Exception as e:
                                print(f"❌ MCP 명령어 처리 중 오류: {e}")
                                if chatbot.config.debug_mode:
                                    import traceback
                                    print(f"🐛 [디버그] MCP 오류 상세: {traceback.format_exc()}")
                        continue
                    
                    # 일반 질문 처리
                    print("🤔 답변 생성 중...")
                    response = await chatbot.generate_response(user_input, ask_to_save=True)
                    print(f"\n📝 답변:\n{response}")
                    
            except KeyboardInterrupt:
                print("\n👋 프로그램을 종료합니다.")
                break
            except EOFError:
                print("\n👋 입력이 종료되었습니다.")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
                continue
                
    except Exception as e:
        print(f"❌ 챗봇 시작 실패: {e}")
        import traceback
        traceback.print_exc()

def print_help():
    """도움말 출력"""
    help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    📚 GAIA-BT v2.0 도움말 & 사용 가이드                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 기본 사용법:
  - 질문을 직접 입력하면 AI가 답변합니다
  - 명령어는 '/'로 시작하거나 '/' 없이도 사용 가능합니다

📋 기본 명령어 (유연한 입력 지원):
  /help 또는 help           - 이 도움말 표시
  /debug 또는 debug         - 디버그 모드 토글 (Deep Search 과정 표시)
  /normal 또는 normal       - 일반 모드로 전환
  /exit 또는 exit           - 챗봇 종료
  /model <이름>             - AI 모델 변경 (gemma3:latest 권장)
  /prompt <모드>            - 전문 프롬프트 변경 (clinical/research/chemistry)

🔬 통합 Deep Research MCP 명령어 (유연한 입력 지원):
  ┌─ 기본 제어 ─────────────────────────────────────────────────────┐
  │ /mcp start 또는 mcp start   - 통합 MCP 시스템 시작 (필수!)     │
  │ /mcp stop 또는 mcp stop     - MCP 서버 중지                     │
  │ /mcp status 또는 mcp status - MCP 상태 및 연결된 서버 확인      │
  └─────────────────────────────────────────────────────────────────┘
  
  ┌─ DrugBank (약물 데이터베이스) ──────────────────────────────────┐
  │ /mcp drugbank search <약물명>      - 약물 검색                 │
  │ /mcp drugbank indication <적응증>  - 적응증별 약물 검색        │
  │ /mcp drugbank interaction <ID>     - 약물 상호작용 분석        │
  └─────────────────────────────────────────────────────────────────┘
  
  ┌─ OpenTargets (타겟-질병 연관성) ────────────────────────────────┐
  │ /mcp opentargets targets <유전자>  - 타겟 검색                 │
  │ /mcp opentargets diseases <질병>   - 질병 검색                 │
  │ /mcp opentargets drugs <약물>      - 약물 검색                 │
  └─────────────────────────────────────────────────────────────────┘
  
  ┌─ ChEMBL (화학 데이터베이스) ────────────────────────────────────┐
  │ /mcp chembl molecule <분자명>      - 분자 정보 검색            │
  │ /mcp smiles <SMILES>               - SMILES 구조 분석          │
  └─────────────────────────────────────────────────────────────────┘
  
  ┌─ BioMCP (생의학 데이터베이스) ──────────────────────────────────┐
  │ /mcp bioarticle <검색어>           - 생의학 논문 검색          │
  │ /mcp biotrial <조건>               - 임상시험 검색             │
  └─────────────────────────────────────────────────────────────────┘
  
  ┌─ Sequential Thinking (AI 추론) ─────────────────────────────────┐
  │ /mcp think <문제>                  - 단계별 사고 분석          │
  └─────────────────────────────────────────────────────────────────┘
  
  ┌─ 테스트 ────────────────────────────────────────────────────────┐
  │ /mcp test deep                     - Deep Research 통합 테스트 │
  └─────────────────────────────────────────────────────────────────┘

🚀 통합 Deep Search 사용법:
  1. '/mcp start' 명령어로 모든 MCP 서버를 시작
  2. '/debug' 명령어로 디버그 모드 활성화 (권장)
  3. 복잡한 신약개발 질문을 입력하면 자동으로 관련 데이터베이스들을 검색
  
🧪 Deep Search 질문 예제:
  "아스피린의 약물 상호작용과 새로운 치료제 개발 가능성을 분석해주세요"
  "BRCA1 유전자 타겟을 이용한 유방암 치료제 개발 전략을 분석해주세요"
  "알츠하이머병 치료를 위한 새로운 타겟 발굴 전략을 제시해주세요"
  "키나제 억제제의 구조 최적화 방법을 분석해주세요"
  
📖 상세 문서:
  - QUICK_START_GUIDE.md        - 5분 빠른 시작 가이드
  - DEEP_RESEARCH_USER_MANUAL.md - 상세 사용자 매뉴얼
  - START_CHATBOT.md            - 챗봇 실행 가이드
  - README.md                   - 전체 시스템 개요

💡 사용 팁:
  • 디버그 모드를 켜면 각 MCP 서버의 검색 과정을 실시간 확인 가능
  • 명령어는 '/' 없이도 사용 가능 (예: mcp start, help, debug)
  • 공백이 있어도 자동으로 처리됩니다

📝 명령어 사용 예시:
  다음 표현들은 모두 동일하게 작동합니다:
  ✓ /mcp start    ✓ mcp start    ✓ /mcp  start    ✓ mcp  start
  ✓ /help         ✓ help
  ✓ /debug        ✓ debug
  ✓ /exit         ✓ exit
"""
    print(help_text)

if __name__ == "__main__":
    try:
        # 챗봇 실행
        asyncio.run(run_chatbot_interactive())
    except KeyboardInterrupt:
        print("\n\n👋 사용해 주셔서 감사합니다!")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("문제가 지속되면 GitHub 이슈로 보고해 주세요.")