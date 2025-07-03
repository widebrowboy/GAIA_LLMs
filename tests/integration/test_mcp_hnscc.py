#!/usr/bin/env python3
"""
MCP HNSCC (Head and Neck Squamous Cell Carcinoma) 연구 테스트
biomcp-examples의 researcher_hnscc 예제를 활용한 테스트 스크립트
"""

import asyncio
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent))

from src.cli.chatbot import HealthSupplementChatbot
from src.cli.interface import ChatInterface
from rich.console import Console

# HNSCC 연구 질문 (biomcp-examples에서 사용된 예제)
HNSCC_RESEARCH_QUESTION = """
What are the emerging treatment strategies for head and neck squamous cell carcinoma (HNSCC), 
particularly focusing on immunotherapy combinations, targeted therapies, and novel approaches 
currently in clinical trials?
"""

async def test_mcp_servers():
    """MCP 서버 테스트"""
    console = Console()
    
    console.print("\n[bold blue]=== MCP HNSCC 연구 테스트 ===[/bold blue]\n")
    
    # 챗봇 초기화
    interface = ChatInterface()
    chatbot = HealthSupplementChatbot(interface)
    
    try:
        # 1. MCP 시작
        console.print("[yellow]1. MCP 서버들을 시작합니다...[/yellow]")
        await chatbot.mcp_commands.start_mcp()
        
        # 잠시 대기
        await asyncio.sleep(3)
        
        # 2. MCP 상태 확인
        console.print("\n[yellow]2. MCP 연결 상태 확인[/yellow]")
        await chatbot.mcp_commands.show_mcp_status()
        
        # 3. 사용 가능한 툴 목록
        console.print("\n[yellow]3. 사용 가능한 MCP 툴 확인[/yellow]")
        await chatbot.mcp_commands.list_mcp_tools()
        
        # 4. Sequential Thinking으로 문제 분석
        console.print("\n[yellow]4. Sequential Thinking으로 HNSCC 치료 전략 분석[/yellow]")
        await chatbot.mcp_commands.start_sequential_thinking(
            "Analyze emerging treatment strategies for HNSCC focusing on immunotherapy"
        )
        
        # 5. BiomCP로 논문 검색
        console.print("\n[yellow]5. BiomCP로 HNSCC 면역치료 관련 논문 검색[/yellow]")
        await chatbot.mcp_commands.search_biomedical_articles(
            "HNSCC immunotherapy combination PD-1 PD-L1"
        )
        
        # 6. BiomCP로 임상시험 검색
        console.print("\n[yellow]6. BiomCP로 HNSCC 임상시험 검색[/yellow]")
        await chatbot.mcp_commands.search_clinical_trials(
            "head neck squamous cell carcinoma immunotherapy"
        )
        
        # 7. 종합 연구 수행
        console.print("\n[yellow]7. MCP를 통한 종합 연구 수행[/yellow]")
        console.print(f"[cyan]연구 질문:[/cyan] {HNSCC_RESEARCH_QUESTION}")
        await chatbot.mcp_commands.mcp_research(HNSCC_RESEARCH_QUESTION)
        
        # 8. 테스트 완료
        console.print("\n[green]✓ 모든 MCP 테스트가 완료되었습니다![/green]")
        
    except Exception as e:
        console.print(f"\n[red]테스트 중 오류 발생: {e}[/red]")
        import traceback
        traceback.print_exc()
        
    finally:
        # MCP 서버 중지
        console.print("\n[yellow]MCP 서버를 중지합니다...[/yellow]")
        await chatbot.mcp_commands.stop_mcp()

async def main():
    """메인 함수"""
    console = Console()
    
    console.print("[bold]GAIA MCP HNSCC 연구 테스트를 시작합니다.[/bold]")
    console.print("이 테스트는 biomcp-examples의 researcher_hnscc 예제를 기반으로 합니다.\n")
    
    # 사용자 확인
    confirm = input("테스트를 시작하시겠습니까? (y/N): ").strip().lower()
    if confirm != 'y':
        console.print("[yellow]테스트가 취소되었습니다.[/yellow]")
        return
    
    await test_mcp_servers()
    
    console.print("\n[bold green]테스트가 완료되었습니다![/bold green]")

if __name__ == "__main__":
    asyncio.run(main())