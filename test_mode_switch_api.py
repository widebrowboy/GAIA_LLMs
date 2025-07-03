#!/usr/bin/env python3
"""
모드 전환 API 테스트 스크립트
"""

import asyncio
import httpx
import json
from rich.console import Console
from rich.table import Table

console = Console()

API_BASE_URL = "http://localhost:8000"
SESSION_ID = "test_session"

async def test_mode_switching():
    """모드 전환 API 테스트"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. 현재 상태 확인
        console.print("\n[bold cyan]1. 현재 시스템 상태 확인[/bold cyan]")
        response = await client.get(f"{API_BASE_URL}/api/system/info")
        if response.status_code == 200:
            data = response.json()
            console.print(f"현재 모드: [yellow]{data.get('mode', 'unknown')}[/yellow]")
            console.print(f"MCP 활성화: [yellow]{data.get('mcp_enabled', False)}[/yellow]")
        else:
            console.print(f"[red]상태 확인 실패: {response.status_code}[/red]")
            return
        
        # 2. Deep Research 모드로 전환
        console.print("\n[bold cyan]2. Deep Research 모드로 전환 테스트[/bold cyan]")
        response = await client.post(
            f"{API_BASE_URL}/api/system/mode/deep_research",
            json={"session_id": SESSION_ID}
        )
        
        if response.status_code == 200:
            data = response.json()
            console.print("[green]✅ Deep Research 모드 전환 성공[/green]")
            console.print(f"응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            console.print(f"[red]❌ Deep Research 모드 전환 실패: {response.status_code}[/red]")
            console.print(f"응답: {response.text}")
        
        # 3. 잠시 대기
        await asyncio.sleep(2)
        
        # 4. 상태 재확인
        console.print("\n[bold cyan]3. 모드 전환 후 상태 확인[/bold cyan]")
        response = await client.get(f"{API_BASE_URL}/api/system/info")
        if response.status_code == 200:
            data = response.json()
            console.print(f"현재 모드: [yellow]{data.get('mode', 'unknown')}[/yellow]")
            console.print(f"MCP 활성화: [yellow]{data.get('mcp_enabled', False)}[/yellow]")
        
        # 5. 일반 모드로 전환
        console.print("\n[bold cyan]4. 일반 모드로 전환 테스트[/bold cyan]")
        response = await client.post(
            f"{API_BASE_URL}/api/system/mode/normal",
            json={"session_id": SESSION_ID}
        )
        
        if response.status_code == 200:
            data = response.json()
            console.print("[green]✅ 일반 모드 전환 성공[/green]")
            console.print(f"응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            console.print(f"[red]❌ 일반 모드 전환 실패: {response.status_code}[/red]")
            console.print(f"응답: {response.text}")
        
        # 6. 최종 상태 확인
        console.print("\n[bold cyan]5. 최종 상태 확인[/bold cyan]")
        response = await client.get(f"{API_BASE_URL}/api/system/info")
        if response.status_code == 200:
            data = response.json()
            console.print(f"최종 모드: [yellow]{data.get('mode', 'unknown')}[/yellow]")
            console.print(f"MCP 활성화: [yellow]{data.get('mcp_enabled', False)}[/yellow]")

async def main():
    """메인 함수"""
    console.print("[bold green]🔬 GAIA-BT 모드 전환 API 테스트[/bold green]")
    console.print("="*60)
    
    try:
        await test_mode_switching()
    except Exception as e:
        console.print(f"\n[red]❌ 테스트 실패: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
    
    console.print("\n[green]✅ 테스트 완료[/green]")

if __name__ == "__main__":
    asyncio.run(main())