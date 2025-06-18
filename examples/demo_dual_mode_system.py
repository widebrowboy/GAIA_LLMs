#!/usr/bin/env python3
"""
GAIA-BT v2.0 Alpha 이중 모드 시스템 데모

이 스크립트는 일반 모드와 Deep Research 모드의 차이점을 보여줍니다.
또한 새로운 MCP 출력 제어 기능을 시연합니다.
"""

import asyncio
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.cli.chatbot import DrugDevelopmentChatbot
from app.utils.config import Config

async def demo_dual_mode_system():
    """이중 모드 시스템 데모"""
    
    print("🧬 GAIA-BT v2.0 Alpha 이중 모드 시스템 데모")
    print("=" * 60)
    
    # 챗봇 초기화
    config = Config(debug_mode=False)
    chatbot = DrugDevelopmentChatbot(config)
    
    print(f"\n📋 초기 설정:")
    print(f"  • 현재 모드: {chatbot.current_mode}")
    print(f"  • MCP 출력 표시: {chatbot.config.show_mcp_output}")
    print(f"  • 디버그 모드: {chatbot.config.debug_mode}")
    
    # 1. 일반 모드 데모
    print("\n" + "=" * 60)
    print("🧬 1. 일반 모드 (Normal Mode) 데모")
    print("=" * 60)
    
    print("\n특징:")
    print("  • 기본 AI 답변만 제공")
    print("  • 빠른 응답 속도")
    print("  • 신약개발 기본 지식")
    print("  • MCP 검색 비활성화")
    
    # 일반 모드 배너 표시
    chatbot._show_mode_banner()
    
    print("\n💬 일반 모드 질문 예시:")
    normal_questions = [
        "아스피린의 작용 메커니즘을 설명해주세요",
        "임상시험 1상과 2상의 차이점은?",
        "신약개발 과정의 주요 단계를 설명해주세요"
    ]
    
    for i, question in enumerate(normal_questions, 1):
        print(f"  {i}. \"{question}\"")
    
    # 2. Deep Research 모드로 전환
    print("\n" + "=" * 60)
    print("🔬 2. Deep Research 모드로 전환")
    print("=" * 60)
    
    print("\n🔄 모드 전환 중...")
    chatbot.switch_to_deep_research_mode()
    
    print(f"\n📋 변경된 설정:")
    print(f"  • 현재 모드: {chatbot.current_mode}")
    print(f"  • MCP 출력 표시: {chatbot.config.show_mcp_output}")
    
    print("\n특징:")
    print("  • 다중 데이터베이스 동시 검색")
    print("  • 논문, 임상시험 데이터 통합 분석")
    print("  • Sequential Thinking AI 연구 계획")
    print("  • 과학적 근거 기반 상세 답변")
    
    # 3. MCP 출력 제어 데모
    print("\n" + "=" * 60)
    print("🔧 3. MCP 출력 제어 기능 데모")
    print("=" * 60)
    
    print("\n기본 상태 (MCP 출력 숨김):")
    print(f"  • show_mcp_output: {chatbot.config.show_mcp_output}")
    print("  • 특징: 백그라운드 검색 후 최종 결과만 표시")
    
    print("\n🔄 MCP 출력 표시 켜기...")
    chatbot.toggle_mcp_output()
    
    print(f"\n변경된 상태 (MCP 출력 표시):")
    print(f"  • show_mcp_output: {chatbot.config.show_mcp_output}")
    print("  • 특징: 실시간 검색 과정 표시")
    
    print("\n🔄 MCP 출력 표시 끄기...")
    chatbot.toggle_mcp_output()
    
    # 4. Deep Research 모드 질문 예시
    print("\n" + "=" * 60)
    print("🧪 4. Deep Research 모드 질문 예시")
    print("=" * 60)
    
    deep_questions = [
        "아스피린의 약물 상호작용과 새로운 치료제 개발 가능성을 분석해주세요",
        "BRCA1 유전자 타겟을 이용한 유방암 치료제 개발 전략을 분석해주세요",
        "알츠하이머병 치료를 위한 새로운 타겟 발굴 전략을 제시해주세요",
        "키나제 억제제의 구조 최적화 방법과 임상 데이터를 분석해주세요"
    ]
    
    print("\n💬 Deep Research 모드 질문 예시:")
    for i, question in enumerate(deep_questions, 1):
        print(f"  {i}. \"{question}\"")
    
    # 5. 일반 모드로 복귀
    print("\n" + "=" * 60)
    print("🔄 5. 일반 모드로 복귀")
    print("=" * 60)
    
    print("\n🔄 일반 모드로 전환 중...")
    chatbot.switch_to_normal_mode()
    
    print(f"\n📋 최종 설정:")
    print(f"  • 현재 모드: {chatbot.current_mode}")
    print(f"  • MCP 출력 표시: {chatbot.config.show_mcp_output}")
    
    # 6. 사용 가능한 명령어 요약
    print("\n" + "=" * 60)
    print("📝 6. 사용 가능한 명령어 요약")
    print("=" * 60)
    
    commands = [
        ("/mcp start", "Deep Research 모드 활성화"),
        ("/normal", "일반 모드로 전환"),
        ("/mcpshow", "MCP 검색 과정 표시/숨김 토글"),
        ("/debug", "디버그 모드 토글"),
        ("/prompt <모드>", "전문 프롬프트 변경"),
        ("/help", "전체 도움말 표시")
    ]
    
    print("\n💻 주요 명령어:")
    for cmd, desc in commands:
        print(f"  • {cmd:<15} - {desc}")
    
    print("\n💡 사용 팁:")
    print("  • 명령어는 '/' 없이도 사용 가능 (예: mcpshow, normal)")
    print("  • 일반 모드: 빠른 기본 답변")
    print("  • Deep Research 모드: 종합적 연구 분석")
    print("  • MCP 출력 제어로 검색 과정 표시 여부 선택 가능")
    
    print("\n🎉 이중 모드 시스템 데모 완료!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(demo_dual_mode_system())
    except KeyboardInterrupt:
        print("\n\n👋 데모가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()