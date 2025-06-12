#!/usr/bin/env python3
"""
GAIA-BT 신약개발 연구 챗봇 실행 스크립트
"""

import sys
import os
import asyncio
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

async def run_chatbot_interactive():
    """대화형 챗봇 실행"""
    try:
        from app.cli.chatbot import DrugDevelopmentChatbot
        
        
        # 챗봇 초기화
        chatbot = DrugDevelopmentChatbot(debug_mode=False)
        
        # GAIA-BT GPT 배너 표시
        chatbot.interface.display_welcome()
        
        # API 연결 확인
        status = await chatbot.client.check_availability()
        if not status["available"]:
            print(f"❌ Ollama API 연결 실패: {status.get('error', '알 수 없는 오류')}")
            print("Ollama가 실행 중인지 확인하세요: ollama serve")
            return
        
        print("✅ Ollama API 연결 성공")
        
        # 모델 확인
        model_check = await chatbot.auto_select_model()
        if not model_check:
            print("❌ 사용 가능한 모델이 없습니다.")
            return
        
        print("✅ AI 모델 준비 완료")
        print("\n💬 질문을 입력하거나 명령어를 사용하세요:")
        
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
                
                # 종료 명령어 처리
                if user_input.lower() in ['/exit', 'exit', 'quit', 'q']:
                    print("👋 챗봇을 종료합니다.")
                    break
                
                # 명령어 처리
                if user_input.startswith("/"):
                    if user_input == "/help":
                        print_help()
                    elif user_input.startswith("/mcp"):
                        await chatbot.mcp_commands.handle_mcp_command(user_input[5:])
                    elif user_input.startswith("/model"):
                        parts = user_input.split(maxsplit=1)
                        if len(parts) > 1:
                            await chatbot.change_model(parts[1])
                        else:
                            print("사용법: /model <모델명>")
                    else:
                        print(f"알 수 없는 명령어: {user_input}")
                        print("'/help'로 도움말을 확인하세요.")
                else:
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
📚 GAIA 신약개발 연구 챗봇 도움말

🎯 기본 사용법:
  - 질문을 직접 입력하면 AI가 답변합니다
  - 명령어는 '/'로 시작합니다

📋 주요 명령어:
  /help                     - 이 도움말 표시
  /exit                     - 챗봇 종료
  /model <이름>             - AI 모델 변경

🔬 MCP (고급 연구) 명령어:
  /mcp start               - MCP 서버 시작
  /mcp stop                - MCP 서버 중지  
  /mcp status              - MCP 상태 확인
  /mcp test deep           - Deep Research 테스트
  
  /mcp bioarticle <검색어>  - 생의학 논문 검색
  /mcp biotrial <조건>     - 임상시험 검색
  /mcp chembl molecule <분자> - 화학 분자 검색
  /mcp think <문제>        - Sequential Thinking

🧪 테스트 질문 예제:
  "항암제 개발에서 분자 타겟팅 치료법의 원리를 설명해주세요"
  "신약개발 과정에서 전임상 시험의 주요 단계를 분석해주세요"
  
📁 자세한 내용은 DEEP_RESEARCH_USER_MANUAL.md 파일을 참조하세요.
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