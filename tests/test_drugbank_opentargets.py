#!/usr/bin/env python3
"""
DrugBank + OpenTargets MCP 통합 테스트
"""

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트를 파이썬 경로에 추가
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from app.cli.chatbot import DrugDevelopmentChatbot

async def test_drugbank_opentargets_integration():
    """DrugBank와 OpenTargets MCP 서버 통합 테스트"""
    
    print("=== DrugBank + OpenTargets MCP 통합 테스트 ===\n")
    
    # 챗봇 인스턴스 생성
    chatbot = DrugDevelopmentChatbot()
    await chatbot.initialize()
    
    print("✅ 챗봇 초기화 완료\n")
    
    # 테스트 시나리오
    test_scenarios = [
        {
            "title": "DrugBank 약물 검색 테스트",
            "description": "아스피린 약물 정보 검색",
            "commands": [
                "/mcp drugbank search aspirin",
                "/mcp drugbank indication inflammation"
            ]
        },
        {
            "title": "OpenTargets 타겟 검색 테스트", 
            "description": "BRCA1 유전자 타겟 정보 검색",
            "commands": [
                "/mcp opentargets targets BRCA1",
                "/mcp opentargets target_diseases ENSG00000012048"
            ]
        },
        {
            "title": "통합 신약개발 연구 테스트",
            "description": "암 치료를 위한 신약개발 연구",
            "question": "BRCA1 타겟을 대상으로 한 유방암 치료제 개발에 대해 DrugBank와 OpenTargets 데이터를 활용하여 종합적으로 분석해주세요."
        }
    ]
    
    # MCP 시작
    print("🚀 MCP 서버 시작 중...")
    try:
        await chatbot.mcp_commands.start_mcp()
        print("✅ MCP 서버 시작 완료\n")
        
        # 서버 상태 확인
        print("📊 MCP 상태 확인:")
        await chatbot.mcp_commands.show_mcp_status()
        print()
        
    except Exception as e:
        print(f"❌ MCP 서버 시작 실패: {e}")
        return
    
    # 개별 테스트 시나리오 실행
    for i, scenario in enumerate(test_scenarios[:2], 1):  # 처음 2개 시나리오
        print(f"📝 테스트 {i}: {scenario['title']}")
        print(f"   설명: {scenario['description']}")
        
        if 'commands' in scenario:
            for cmd in scenario['commands']:
                print(f"\n⚡ 실행: {cmd}")
                try:
                    # 명령어 파싱 및 실행
                    if cmd.startswith("/mcp "):
                        args = cmd[5:]  # "/mcp " 제거
                        await chatbot.mcp_commands.handle_mcp_command(args)
                        print("✅ 명령어 실행 완료")
                    
                except Exception as e:
                    print(f"❌ 명령어 실행 실패: {e}")
        
        print(f"\n{'='*50}\n")
    
    # 통합 연구 테스트
    print("🧬 통합 신약개발 연구 테스트")
    print(f"질문: {test_scenarios[2]['question']}")
    
    try:
        print("\n🔬 MCP 기반 Deep Research 수행 중...")
        response = await chatbot.generate_response(
            test_scenarios[2]['question'], 
            ask_to_save=False
        )
        
        print(f"\n✅ 연구 완료!")
        print(f"📊 응답 길이: {len(response)}자")
        
        # 응답 미리보기
        if len(response) > 300:
            preview = response[:300] + "..."
            print(f"\n📖 응답 미리보기:\n{preview}")
        else:
            print(f"\n📖 전체 응답:\n{response}")
            
        # 저장
        await chatbot.save_research_result(
            "DrugBank_OpenTargets_Integration_Test", 
            response
        )
        print("💾 연구 결과 저장 완료")
        
    except Exception as e:
        print(f"❌ 통합 연구 실패: {e}")
    
    # MCP 중지
    print("\n🛑 MCP 서버 중지...")
    try:
        await chatbot.mcp_commands.stop_mcp()
        print("✅ MCP 서버 중지 완료")
    except Exception as e:
        print(f"❌ MCP 서버 중지 실패: {e}")
    
    print("\n🎉 통합 테스트 완료!")
    print("\n📁 결과 확인:")
    print("- 저장된 연구 결과: outputs/research/ 디렉토리")
    print("- 로그 파일: 터미널 출력 참조")

async def test_mcp_tools_availability():
    """MCP 툴 가용성 테스트"""
    
    print("=== MCP 툴 가용성 테스트 ===\n")
    
    chatbot = DrugDevelopmentChatbot()
    await chatbot.initialize()
    
    # MCP 시작
    try:
        await chatbot.mcp_commands.start_mcp()
        print("✅ MCP 서버 시작 완료")
        
        # 툴 목록 확인
        print("\n🔧 사용 가능한 MCP 툴 목록:")
        await chatbot.mcp_commands.list_mcp_tools()
        
        # 연결된 서버 확인
        print("\n🖥️ 연결된 MCP 서버:")
        servers = await chatbot.mcp_commands.get_connected_mcp_servers()
        
        target_servers = ["drugbank-mcp", "opentargets-mcp"]
        for server_name in target_servers:
            found = any(s['name'] == server_name for s in servers)
            status = "✅ 연결됨" if found else "❌ 미연결"
            print(f"- {server_name}: {status}")
        
        await chatbot.mcp_commands.stop_mcp()
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

def main():
    """메인 실행 함수"""
    
    print("DrugBank + OpenTargets MCP 통합 테스트 스크립트")
    print("=" * 60)
    
    print("\n테스트 옵션:")
    print("1. 툴 가용성 테스트 (빠른 확인)")
    print("2. 전체 통합 테스트 (완전한 테스트)")
    print("3. 종료")
    
    choice = input("\n선택하세요 (1-3): ").strip()
    
    if choice == "1":
        print("\n🧪 툴 가용성 테스트 시작...")
        asyncio.run(test_mcp_tools_availability())
    elif choice == "2":
        print("\n🧪 전체 통합 테스트 시작...")
        asyncio.run(test_drugbank_opentargets_integration())
    elif choice == "3":
        print("👋 테스트를 종료합니다.")
        return
    else:
        print("❌ 잘못된 선택입니다.")
        return

if __name__ == "__main__":
    main()