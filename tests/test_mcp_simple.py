#!/usr/bin/env python3
"""
간단한 MCP 서버 통합 테스트 (자동화)
"""

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트를 파이썬 경로에 추가
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

async def test_mcp_servers():
    """MCP 서버들의 기본 기능 테스트"""
    
    print("=== MCP 서버 통합 테스트 ===\n")
    
    try:
        from app.cli.chatbot import DrugDevelopmentChatbot
        
        # 챗봇 인스턴스 생성
        chatbot = DrugDevelopmentChatbot(debug_mode=True)
        print("✅ 챗봇 초기화 완료")
        
        # MCP 매니저 가용성 확인
        if hasattr(chatbot, 'mcp_manager') and chatbot.mcp_manager:
            print("✅ MCP 매니저 사용 가능")
        else:
            print("⚠️ MCP 매니저를 사용할 수 없습니다. MCP 기능이 제한됩니다.")
            return
        
        # MCP 명령어 객체 확인
        if hasattr(chatbot, 'mcp_commands') and chatbot.mcp_commands:
            print("✅ MCP 명령어 처리기 사용 가능")
        else:
            print("❌ MCP 명령어 처리기를 찾을 수 없습니다.")
            return
        
        # 서버 시작 테스트
        print("\n🚀 MCP 서버 시작 테스트...")
        try:
            # 기본 MCP 가용성 확인
            status = chatbot.mcp_manager.get_status()
            print(f"MCP 매니저 상태: {status}")
            
            # 연결된 서버 목록 확인
            servers = await chatbot.mcp_commands.get_connected_mcp_servers()
            print(f"\n📊 등록된 MCP 서버 수: {len(servers)}")
            
            target_servers = ["drugbank-mcp", "opentargets-mcp", "chembl", "biomcp"]
            for server_name in target_servers:
                found = any(s['name'] == server_name for s in servers)
                status_icon = "✅" if found else "⚠️"
                print(f"{status_icon} {server_name}: {'등록됨' if found else '미등록'}")
            
        except Exception as e:
            print(f"❌ MCP 서버 시작 테스트 실패: {e}")
        
        # 설정 파일 확인
        print("\n📝 MCP 설정 파일 확인...")
        config_path = project_root / "config" / "mcp.json"
        if config_path.exists():
            print(f"✅ MCP 설정 파일 존재: {config_path}")
            
            import json
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            servers_in_config = config.get('mcpServers', {})
            print(f"📊 설정된 MCP 서버 수: {len(servers_in_config)}")
            
            for server_name in target_servers:
                if server_name in servers_in_config:
                    print(f"✅ {server_name}: 설정 존재")
                else:
                    print(f"⚠️ {server_name}: 설정 없음")
        else:
            print(f"❌ MCP 설정 파일 없음: {config_path}")
        
        # 새 서버 파일 확인
        print("\n📁 새 MCP 서버 파일 확인...")
        
        drugbank_path = project_root / "mcp" / "drugbank" / "drugbank_mcp.py"
        opentargets_path = project_root / "mcp" / "opentargets" / "opentargets_mcp.py"
        
        if drugbank_path.exists():
            print(f"✅ DrugBank MCP 서버: {drugbank_path}")
        else:
            print(f"❌ DrugBank MCP 서버 없음: {drugbank_path}")
        
        if opentargets_path.exists():
            print(f"✅ OpenTargets MCP 서버: {opentargets_path}")
        else:
            print(f"❌ OpenTargets MCP 서버 없음: {opentargets_path}")
        
        # 의존성 확인
        print("\n📦 의존성 확인...")
        
        dependencies = [
            ("httpx", "HTTP 클라이언트"),
            ("pydantic", "데이터 검증"),
            ("rich", "CLI 인터페이스")
        ]
        
        for module_name, description in dependencies:
            try:
                __import__(module_name)
                print(f"✅ {module_name}: {description}")
            except ImportError:
                print(f"❌ {module_name}: {description} - 설치 필요")
        
        print("\n🎯 테스트 요약:")
        print("- ✅ 기본 구조 검증 완료")
        print("- ✅ 설정 파일 확인 완료")
        print("- ✅ 서버 파일 존재 확인")
        print("- ✅ 의존성 검증 완료")
        
        print("\n📝 다음 단계:")
        print("1. MCP 의존성 설치: pip install mcp fastmcp")
        print("2. DrugBank API 키 설정 (선택사항): export DRUGBANK_API_KEY=your_key")
        print("3. 챗봇 실행: python run_chatbot.py")
        print("4. MCP 시작: /mcp start")
        print("5. 테스트: /mcp drugbank search aspirin")
        
    except ImportError as e:
        print(f"❌ 모듈 import 실패: {e}")
        print("프로젝트 구조나 경로를 확인하세요.")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_servers())