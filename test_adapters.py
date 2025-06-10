#!/usr/bin/env python3
"""
어댑터 패턴 테스트 스크립트
다양한 모델을 전환하며 어댑터 패턴의 효과를 검증합니다.
"""

import asyncio
import os
import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.api.ollama_client import OllamaClient
from src.api.model_adapters import get_adapter_for_model

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("adapter_test")

# 테스트할 모델 목록
TEST_MODELS = [
    "Gemma3:latest",
    "txgemma-chat:latest", 
    "txgemma-predict:latest"
]

# 테스트 질문
TEST_QUESTIONS = [
    "크레아틴은 어떤 효과가 있나요?",
    "BCAA와 EAA의 차이점은 무엇인가요?",
    "근육 회복을 위한 최고의 보충제는?"
]

# 풍부한 출력을 위한 콘솔 설정
console = Console()

async def test_model_adapter(model_name: str, question: str) -> tuple:
    """
    특정 모델과 어댑터를 테스트합니다.
    
    Args:
        model_name: 테스트할 모델명
        question: 테스트 질문
        
    Returns:
        (model_name, adapter_name, response): 모델명, 어댑터명, 응답 튜플
    """
    # 클라이언트 초기화
    client = OllamaClient(
        model=model_name,
        temperature=0.7,
        max_tokens=1000,
        min_response_length=100
    )
    
    # 어댑터 정보 로깅
    adapter_name = client.adapter.__class__.__name__
    logger.info(f"모델: {model_name}, 어댑터: {adapter_name} 테스트 시작")
    
    try:
        # 응답 생성
        console.print(f"[blue]질문:[/blue] {question}")
        console.print(f"[yellow]응답 생성 중...[/yellow]")
        
        start_time = asyncio.get_event_loop().time()
        response = await client.generate(
            prompt=question,
            system_prompt="한국어로 짧게 답변해주세요. 2-3문장으로 핵심만 요약해서 응답하세요."
        )
        elapsed = asyncio.get_event_loop().time() - start_time
        
        # 클라이언트 세션 종료
        await client.close()
        
        return {
            "model": model_name,
            "adapter": adapter_name,
            "response": response.strip(),
            "time": round(elapsed, 2)
        }
        
    except Exception as e:
        logger.error(f"에러 발생: {str(e)}")
        return {
            "model": model_name,
            "adapter": adapter_name,
            "response": f"에러: {str(e)}",
            "time": 0
        }

async def test_model_switching(models: list, question: str) -> list:
    """
    모델 전환 시나리오를 테스트합니다.
    
    Args:
        models: 테스트할 모델 목록
        question: 테스트 질문
        
    Returns:
        결과 목록
    """
    results = []
    
    # 첫 번째 클라이언트 초기화
    client = OllamaClient(model=models[0])
    
    for i, model in enumerate(models):
        console.print(f"\n[bold green]테스트 {i+1}/{len(models)}: {model}[/bold green]")
        
        # 모델 변경 (첫 번째는 이미 설정됨)
        if i > 0:
            # 클라이언트 종료 후 재초기화 (컨텍스트 완전 분리)
            await client.close() 
            client = OllamaClient(
                model=model,
                temperature=0.7,
                max_tokens=1000
            )
        
        # 어댑터 정보
        adapter_name = client.adapter.__class__.__name__
        console.print(f"[blue]사용 어댑터:[/blue] {adapter_name}")
        
        # 응답 생성
        try:
            start_time = asyncio.get_event_loop().time()
            response = await client.generate(
                prompt=question,
                system_prompt="한국어로 짧게 답변해주세요. 2-3문장으로 핵심만 요약해서 응답하세요."
            )
            elapsed = asyncio.get_event_loop().time() - start_time
            
            results.append({
                "model": model,
                "adapter": adapter_name,
                "response": response.strip(),
                "time": round(elapsed, 2)
            })
            
        except Exception as e:
            console.print(f"[bold red]에러 발생:[/bold red] {str(e)}")
            results.append({
                "model": model, 
                "adapter": adapter_name,
                "response": f"에러: {str(e)}",
                "time": 0
            })
    
    # 마지막 클라이언트 종료
    await client.close()
    return results

async def main():
    """
    어댑터 패턴 테스트 메인 함수
    """
    console.print(Panel.fit(
        "[bold green]어댑터 패턴 테스트[/bold green]\n"
        "각 모델별 어댑터 작동과 모델 전환 시 응답 분리 검증",
        border_style="blue"
    ))
    
    # 1. 모델 가용성 체크
    console.print("\n[bold]1. 모델 가용성 확인[/bold]")
    client = OllamaClient()
    available_models = []
    
    for model in TEST_MODELS:
        result = await client.check_model_availability(model)
        status = "✅ 사용 가능" if result["available"] else "❌ 사용 불가"
        adapter = result.get("adapter", "N/A") if result["available"] else "N/A"
        console.print(f"{model}: {status} (어댑터: {adapter})")
        if result["available"]:
            available_models.append(model)
    
    if not available_models:
        console.print("[bold red]테스트할 수 있는 모델이 없습니다. Ollama에 모델을 설치해주세요.[/bold red]")
        return
    
    # 2. 개별 모델 테스트
    console.print("\n[bold]2. 개별 모델 테스트[/bold]")
    test_question = TEST_QUESTIONS[0]  # 첫 번째 질문 사용
    
    table = Table(title="모델별 응답 결과")
    table.add_column("모델", style="cyan")
    table.add_column("어댑터", style="green")
    table.add_column("응답", style="white")
    table.add_column("응답시간", style="yellow")
    
    for model in available_models:
        result = await test_model_adapter(model, test_question)
        table.add_row(
            result["model"],
            result["adapter"],
            result["response"][:100] + ("..." if len(result["response"]) > 100 else ""),
            f"{result['time']}초"
        )
    
    console.print(table)
    
    # 3. 모델 전환 테스트
    console.print("\n[bold]3. 모델 전환 테스트[/bold]")
    switch_question = TEST_QUESTIONS[1]  # 두 번째 질문 사용
    
    switch_results = await test_model_switching(available_models, switch_question)
    
    switch_table = Table(title="모델 전환 결과")
    switch_table.add_column("모델", style="cyan")
    switch_table.add_column("어댑터", style="green")
    switch_table.add_column("응답", style="white")
    switch_table.add_column("응답시간", style="yellow")
    
    for result in switch_results:
        switch_table.add_row(
            result["model"],
            result["adapter"],
            result["response"][:100] + ("..." if len(result["response"]) > 100 else ""),
            f"{result['time']}초"
        )
    
    console.print(switch_table)
    
    # 4. 동일 질문에 대한 모델별 응답 비교
    console.print("\n[bold]4. 동일 질문에 대한 모델별 응답 비교[/bold]")
    comparison_question = TEST_QUESTIONS[2]  # 세 번째 질문 사용
    
    comparison_results = []
    for model in available_models:
        result = await test_model_adapter(model, comparison_question)
        comparison_results.append(result)
    
    comp_table = Table(title=f"질문: {comparison_question}")
    comp_table.add_column("모델", style="cyan")
    comp_table.add_column("어댑터", style="green") 
    comp_table.add_column("응답", style="white")
    
    for result in comparison_results:
        comp_table.add_row(
            result["model"],
            result["adapter"],
            result["response"]
        )
    
    console.print(comp_table)

if __name__ == "__main__":
    asyncio.run(main())
