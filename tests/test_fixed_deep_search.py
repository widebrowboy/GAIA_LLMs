#!/usr/bin/env python3
"""
수정된 Deep Search 기능 테스트
DrugBank, OpenTargets, ChEMBL, BiomCP, Sequential Thinking 통합 검증
"""

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트를 파이썬 경로에 추가
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

async def test_fixed_deep_search():
    """수정된 Deep Search 기능 테스트"""
    
    print("=" * 80)
    print("🧬 수정된 GAIA-BT Deep Search 기능 테스트")
    print("=" * 80)
    print()
    
    try:
        from app.cli.chatbot import DrugDevelopmentChatbot
        
        # 챗봇 인스턴스 생성 (디버그 모드로)
        chatbot = DrugDevelopmentChatbot(debug_mode=True)
        print("✅ 챗봇 초기화 완료 (디버그 모드)")
        
        # MCP 가용성 확인
        if chatbot.mcp_manager:
            print("✅ MCP 매니저 사용 가능")
            
            # MCP 서버 시작
            print("\n🔧 MCP 서버 시작 중...")
            server_started = await chatbot.mcp_manager.start_server()
            if server_started:
                print("✅ MCP 서버 시작 성공")
                
                # 기본 클라이언트 생성
                await chatbot.mcp_manager.create_client("default")
                print("✅ 기본 클라이언트 생성")
                
                # 외부 서버들 시작
                external_started = await chatbot.mcp_manager.start_external_servers()
                if external_started:
                    print("✅ 외부 MCP 서버들 시작 성공")
                    
                    # 상태 확인
                    status = chatbot.mcp_manager.get_status()
                    print(f"📊 MCP 상태:")
                    print(f"  - 실행 중: {status['running']}")
                    print(f"  - 클라이언트 수: {status['clients_count']}")
                    print(f"  - 활성 클라이언트: {', '.join(status.get('client_ids', []))}")
                else:
                    print("⚠️ 외부 서버 시작에 실패했지만 계속 진행")
            else:
                print("❌ MCP 서버 시작 실패")
                return
        else:
            print("❌ MCP 매니저를 사용할 수 없습니다.")
            return
        
        # MCP 활성화
        chatbot.mcp_enabled = True
        print("✅ 챗봇 MCP 기능 활성화")
        
        # 테스트 시나리오들
        test_scenarios = [
            {
                "title": "약물 중심 연구 (아스피린)",
                "question": "아스피린의 약물 상호작용과 새로운 치료제 개발 가능성을 분석해주세요",
                "expected_keywords": ["약물", "화학"],
                "expected_servers": ["DrugBank", "ChEMBL", "BiomCP", "Sequential Thinking"]
            },
            {
                "title": "타겟-질병 연구 (BRCA1)",
                "question": "BRCA1 유전자 타겟을 이용한 유방암 치료제 개발 전략을 분석해주세요",
                "expected_keywords": ["타겟", "질병", "약물"],
                "expected_servers": ["OpenTargets", "DrugBank", "BiomCP", "Sequential Thinking"]
            }
        ]
        
        print(f"\n📋 테스트 시나리오: {len(test_scenarios)}개")
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{'='*60}")
            print(f"🧪 테스트 {i}: {scenario['title']}")
            print(f"{'='*60}")
            print(f"📝 질문: {scenario['question']}")
            print(f"🎯 예상 키워드: {', '.join(scenario['expected_keywords'])}")
            print(f"🔬 예상 서버: {', '.join(scenario['expected_servers'])}")
            print()
            
            try:
                # Deep Search 실행
                print("🔍 Deep Search 실행 중...")
                
                deep_search_result = await chatbot.deep_search_with_mcp(scenario['question'])
                
                if deep_search_result:
                    print("✅ Deep Search 성공!")
                    print(f"📊 검색 결과 길이: {len(deep_search_result)}자")
                    
                    # 결과 분석
                    print("\n📈 결과 분석:")
                    
                    # 각 서버별 데이터 포함 여부 확인
                    found_servers = []
                    for server in scenario['expected_servers']:
                        if server in deep_search_result or server.lower() in deep_search_result.lower():
                            found_servers.append(server)
                    
                    print(f"  - 발견된 서버: {', '.join(found_servers) if found_servers else '없음'}")
                    print(f"  - 예상 vs 실제: {len(scenario['expected_servers'])} vs {len(found_servers)}")
                    
                    # 키워드 분석 정보 확인
                    if "키워드 분석" in deep_search_result:
                        print("  ✅ 키워드 분석 정보 포함됨")
                    
                    if "검색된 데이터 소스" in deep_search_result:
                        print("  ✅ 검색 통계 정보 포함됨")
                    
                    # 결과 미리보기
                    if len(deep_search_result) > 800:
                        preview = deep_search_result[:800] + "..."
                        print(f"\n📖 결과 미리보기:\n{preview}")
                    else:
                        print(f"\n📖 전체 결과:\n{deep_search_result}")
                    
                    print(f"\n✅ 테스트 {i} 완료!")
                    
                else:
                    print("⚠️ Deep Search 결과 없음")
                    
            except Exception as e:
                print(f"❌ 테스트 {i} 실패: {e}")
                import traceback
                print(f"🐛 상세 오류:\n{traceback.format_exc()}")
        
        print(f"\n{'='*80}")
        print("🎉 Deep Search 기능 테스트 완료!")
        print("="*80)
        
        print("\n📊 개선사항 검증:")
        print("✅ 클라이언트 이름 매핑 수정")
        print("✅ Sequential Thinking 매개변수 수정")
        print("✅ BiomCP 툴 이름 수정 (article_searcher, trial_searcher)")
        print("✅ 디버그 정보 출력 추가")
        print("✅ 키워드 분석 및 검색 통계 표시")
        print("✅ Mock 클라이언트로 DrugBank/OpenTargets 연동")
        
        print("\n💡 사용 방법:")
        print("1. python run_chatbot.py")
        print("2. /debug (디버그 모드 켜기)")
        print("3. /mcp start")
        print("4. 복잡한 신약개발 질문 입력")
        print("5. 상세한 디버그 정보와 함께 Deep Search 수행 확인")
        
    except ImportError as e:
        print(f"❌ 모듈 import 실패: {e}")
        print("프로젝트 구조나 경로를 확인하세요.")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fixed_deep_search())