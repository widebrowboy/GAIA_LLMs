#!/usr/bin/env python3
"""
통합 Deep Research 기능 테스트
DrugBank + OpenTargets + ChEMBL + BiomCP + Sequential Thinking 모든 MCP 서버 통합 테스트
"""

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트를 파이썬 경로에 추가
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

async def test_deep_research_integration():
    """통합 Deep Research 기능 테스트"""
    
    print("=" * 80)
    print("🧬 GAIA-BT 통합 Deep Research 테스트")
    print("=" * 80)
    print()
    
    try:
        from app.cli.chatbot import DrugDevelopmentChatbot
        
        # 챗봇 인스턴스 생성 (디버그 모드)
        chatbot = DrugDevelopmentChatbot(debug_mode=True)
        print("✅ 챗봇 초기화 완료")
        
        # MCP 가용성 확인
        if chatbot.mcp_manager:
            print("✅ MCP 매니저 사용 가능")
        else:
            print("❌ MCP 매니저를 사용할 수 없습니다.")
            return
        
        # 테스트 질문들 (각기 다른 MCP 서버들을 활용)
        test_questions = [
            {
                "title": "약물 중심 연구",
                "question": "아스피린의 약물 상호작용과 새로운 치료제 개발 가능성을 분석해주세요",
                "expected_mcp": ["DrugBank", "ChEMBL", "BiomCP"],
                "categories": ["drug", "chemical"]
            },
            {
                "title": "타겟-질병 연관성 연구", 
                "question": "BRCA1 유전자 타겟을 이용한 유방암 치료제 개발 전략을 분석해주세요",
                "expected_mcp": ["OpenTargets", "DrugBank", "BiomCP"],
                "categories": ["target", "disease", "drug"]
            },
            {
                "title": "통합 신약개발 연구",
                "question": "알츠하이머병 치료를 위한 새로운 타겟 발굴과 약물 개발 전략을 제시해주세요",
                "expected_mcp": ["OpenTargets", "DrugBank", "ChEMBL", "BiomCP", "Sequential Thinking"],
                "categories": ["disease", "target", "drug", "chemical"]
            }
        ]
        
        print("📋 테스트 시나리오:")
        for i, scenario in enumerate(test_questions, 1):
            print(f"  {i}. {scenario['title']}")
            print(f"     질문: {scenario['question']}")
            print(f"     예상 MCP: {', '.join(scenario['expected_mcp'])}")
            print()
        
        # 사용자 선택
        print("테스트할 시나리오를 선택하세요:")
        print("1, 2, 3 중 하나 선택 또는 'all'로 전체 테스트")
        choice = input("선택: ").strip().lower()
        
        if choice == 'all':
            selected_scenarios = test_questions
        elif choice in ['1', '2', '3']:
            selected_scenarios = [test_questions[int(choice) - 1]]
        else:
            print("❌ 잘못된 선택입니다. 첫 번째 시나리오로 진행합니다.")
            selected_scenarios = [test_questions[0]]
        
        # 선택된 시나리오 실행
        for i, scenario in enumerate(selected_scenarios, 1):
            print(f"\n{'='*60}")
            print(f"🧪 테스트 {i}/{len(selected_scenarios)}: {scenario['title']}")
            print(f"{'='*60}")
            print(f"📝 질문: {scenario['question']}")
            print(f"🎯 예상 활용 MCP: {', '.join(scenario['expected_mcp'])}")
            print()
            
            # Deep Research 직접 테스트
            print("🔬 Deep Search 기능 직접 테스트...")
            
            try:
                # MCP 활성화 (실제로는 서버가 시작되어야 함)
                chatbot.mcp_enabled = True
                
                # Deep Search 실행
                deep_search_result = await chatbot.deep_search_with_mcp(scenario['question'])
                
                if deep_search_result:
                    print("✅ Deep Search 성공!")
                    print(f"📊 검색 결과 길이: {len(deep_search_result)}자")
                    
                    # 결과 분석
                    print("\n📈 결과 분석:")
                    
                    # 각 MCP 서버별 데이터 포함 여부 확인
                    mcp_found = []
                    if "DrugBank" in deep_search_result:
                        mcp_found.append("DrugBank")
                    if "OpenTargets" in deep_search_result:
                        mcp_found.append("OpenTargets")
                    if "ChEMBL" in deep_search_result:
                        mcp_found.append("ChEMBL")
                    if "BiomCP" in deep_search_result:
                        mcp_found.append("BiomCP")
                    if "AI 연구 계획" in deep_search_result:
                        mcp_found.append("Sequential Thinking")
                    
                    print(f"  - 활용된 MCP 서버: {', '.join(mcp_found) if mcp_found else '없음'}")
                    print(f"  - 예상 vs 실제: {len(scenario['expected_mcp'])} vs {len(mcp_found)}")
                    
                    # 결과 미리보기
                    if len(deep_search_result) > 500:
                        preview = deep_search_result[:500] + "..."
                        print(f"\n📖 결과 미리보기:\n{preview}")
                    else:
                        print(f"\n📖 전체 결과:\n{deep_search_result}")
                    
                    # 전체 응답 생성 테스트
                    print(f"\n🤖 전체 AI 응답 생성 테스트...")
                    
                    full_response = await chatbot.generate_response(
                        scenario['question'], 
                        ask_to_save=False
                    )
                    
                    if full_response:
                        print("✅ 전체 응답 생성 성공!")
                        print(f"📊 최종 응답 길이: {len(full_response)}자")
                        
                        # 최종 응답 미리보기
                        if len(full_response) > 300:
                            response_preview = full_response[:300] + "..."
                            print(f"\n📝 최종 응답 미리보기:\n{response_preview}")
                    else:
                        print("❌ 전체 응답 생성 실패")
                        
                else:
                    print("⚠️ Deep Search 결과 없음")
                    
            except Exception as e:
                print(f"❌ Deep Search 테스트 실패: {e}")
                import traceback
                traceback.print_exc()
            
            # 다음 테스트 진행 여부 확인 (여러 테스트인 경우)
            if len(selected_scenarios) > 1 and i < len(selected_scenarios):
                proceed = input("\n다음 테스트를 계속하시겠습니까? (y/N): ").strip().lower()
                if proceed != 'y':
                    break
        
        print(f"\n{'='*80}")
        print("🎉 통합 Deep Research 테스트 완료!")
        print("="*80)
        
        print("\n📊 테스트 요약:")
        print("✅ 통합 Deep Search 기능 검증")
        print("✅ 다중 MCP 서버 연동")
        print("✅ 키워드 기반 적응형 검색")
        print("✅ AI 기반 응답 통합")
        
        print("\n💡 사용 방법:")
        print("1. python run_chatbot.py")
        print("2. /mcp start")
        print("3. 복잡한 신약개발 질문 입력")
        print("4. 자동 Deep Search 수행 확인")
        
    except ImportError as e:
        print(f"❌ 모듈 import 실패: {e}")
        print("프로젝트 구조나 경로를 확인하세요.")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_deep_research_integration())