#!/usr/bin/env python3
"""
DrugBank + OpenTargets MCP 통합 데모
신약개발 연구를 위한 새로운 MCP 서버 기능 시연
"""

import asyncio
import os
import sys
from pathlib import Path

# 프로젝트 루트를 파이썬 경로에 추가
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def demo():
    """DrugBank + OpenTargets MCP 통합 데모"""
    
    print("=" * 80)
    print("🧬 GAIA-BT 신약개발 연구 시스템 - DrugBank + OpenTargets 통합 데모")
    print("=" * 80)
    print()
    
    print("🎯 새로 추가된 기능:")
    print()
    
    print("📊 DrugBank MCP 서버:")
    print("  - 약물 검색 및 상세 정보")
    print("  - 적응증별 약물 검색")
    print("  - 약물 상호작용 분석")
    print("  - 타겟별 약물 검색")
    print()
    
    print("🎯 OpenTargets MCP 서버:")
    print("  - 타겟 유전자 검색")
    print("  - 질병 정보 검색")
    print("  - 타겟-질병 연관성 분석")
    print("  - 약물-타겟 관계 분석")
    print()
    
    print("🔧 사용 방법:")
    print()
    print("1. 챗봇 실행:")
    print("   python run_chatbot.py")
    print()
    
    print("2. MCP 서버 시작:")
    print("   > /mcp start")
    print()
    
    print("3. DrugBank 검색 예제:")
    print('   > /mcp drugbank search "aspirin"')
    print('   > /mcp drugbank indication "pain"')
    print('   > /mcp drugbank details "DB00945"')
    print('   > /mcp drugbank interaction "DB00945"')
    print()
    
    print("4. OpenTargets 검색 예제:")
    print('   > /mcp opentargets targets "BRCA1"')
    print('   > /mcp opentargets diseases "breast cancer"')
    print('   > /mcp opentargets target_diseases "ENSG00000012048"')
    print('   > /mcp opentargets drugs "pembrolizumab"')
    print()
    
    print("5. 통합 신약개발 연구 예제:")
    research_examples = [
        "BRCA1을 타겟으로 한 유방암 치료제 개발 전략을 분석해주세요",
        "아스피린의 약물 상호작용과 새로운 적응증 가능성을 조사해주세요",
        "면역항암제 펨브롤리주맙의 타겟 메커니즘과 확장 적응증을 연구해주세요",
        "알츠하이머병 치료제 개발을 위한 새로운 타겟 발굴 전략을 제시해주세요"
    ]
    
    for i, example in enumerate(research_examples, 1):
        print(f"   {i}. {example}")
    print()
    
    print("🧪 통합 테스트:")
    print("   > /mcp test deep  # 전체 시스템 테스트")
    print()
    
    print("📁 프로젝트 구조:")
    print("   mcp/")
    print("   ├── drugbank/")
    print("   │   ├── __init__.py")
    print("   │   └── drugbank_mcp.py          # DrugBank MCP 서버")
    print("   ├── opentargets/")
    print("   │   ├── __init__.py")
    print("   │   └── opentargets_mcp.py       # OpenTargets MCP 서버")
    print("   └── config/mcp.json              # MCP 서버 설정")
    print()
    
    print("🔑 API 키 설정 (선택사항):")
    print("   export DRUGBANK_API_KEY=your_api_key")
    print("   # OpenTargets는 무료 공개 API 사용")
    print()
    
    print("📊 데이터베이스 정보:")
    print("   - DrugBank: 15,000+ 약물 정보")
    print("   - OpenTargets: 60,000+ 타겟, 27,000+ 질병")
    print("   - 실시간 API 연동")
    print("   - JSON 구조화 데이터")
    print()
    
    print("✨ 주요 장점:")
    print("   🔬 포괄적 약물 정보")
    print("   🎯 타겟-질병 연관성")
    print("   📈 상호작용 분석")
    print("   🧬 유전체 기반 연구")
    print("   🤖 AI 기반 통합 분석")
    print()
    
    print("🚀 지금 시작하기:")
    print("   python run_chatbot.py")
    print()
    
    # 실시간 데모 제안
    response = input("지금 실시간 데모를 실행하시겠습니까? (y/N): ").strip().lower()
    
    if response == 'y':
        print("\n🎬 실시간 데모 시작...")
        print("=" * 50)
        
        # 챗봇 실행 명령어 출력
        print("다음 명령어들을 순서대로 실행해보세요:")
        print()
        demo_commands = [
            "/mcp start",
            "/mcp status", 
            '/mcp drugbank search "aspirin"',
            '/mcp opentargets targets "BRCA1"',
            '"BRCA1 타겟을 이용한 유방암 치료제 개발 전략을 분석해주세요"'
        ]
        
        for i, cmd in enumerate(demo_commands, 1):
            print(f"{i}. {cmd}")
        
        print("\n📱 챗봇을 실행합니다...")
        
        # 챗봇 실행
        try:
            os.system("python run_chatbot.py")
        except KeyboardInterrupt:
            print("\n👋 데모를 종료합니다.")
    else:
        print("👋 나중에 시도해보세요!")
        print("📖 더 자세한 정보는 DEEP_RESEARCH_USER_MANUAL.md를 참조하세요.")

if __name__ == "__main__":
    demo()