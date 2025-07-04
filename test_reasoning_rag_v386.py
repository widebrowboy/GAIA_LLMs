#!/usr/bin/env python3
"""
GAIA-BT v3.86 Reasoning RAG 시스템 테스트
Self-RAG, CoT-RAG 통합 테스트 스크립트
"""

import asyncio
import json
import time
from typing import Dict, Any
import requests
from datetime import datetime

# API 서버 기본 URL
BASE_URL = "http://localhost:8000"
REASONING_RAG_URL = f"{BASE_URL}/api/reasoning-rag"

def print_header(title: str):
    """테스트 섹션 헤더 출력"""
    print(f"\n{'='*60}")
    print(f"🧠 {title}")
    print(f"{'='*60}")

def print_result(success: bool, message: str):
    """테스트 결과 출력"""
    status = "✅ 성공" if success else "❌ 실패"
    print(f"{status}: {message}")

async def test_health_check():
    """헬스체크 테스트"""
    print_header("Reasoning RAG 헬스체크")
    
    try:
        response = requests.get(f"{REASONING_RAG_URL}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"시스템 상태: {data.get('status', 'unknown')}")
            print(f"파이프라인 준비: {data.get('pipeline_ready', False)}")
            print(f"검색 기능: {data.get('search_functional', False)}")
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print_result(False, f"헬스체크 실패: {e}")

async def test_modes_info():
    """지원 모드 정보 테스트"""
    print_header("지원 추론 모드 조회")
    
    try:
        response = requests.get(f"{REASONING_RAG_URL}/modes", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            modes = data.get("modes", {})
            
            print_result(True, f"현재 버전: {data.get('current_version')}")
            print(f"기본 모드: {data.get('default_mode')}")
            
            for mode_name, mode_info in modes.items():
                status = mode_info.get("status", "unknown")
                print(f"  • {mode_name}: {mode_info.get('name')} - {status}")
                
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print_result(False, f"모드 조회 실패: {e}")

async def test_self_rag_query():
    """Self-RAG 추론 테스트"""
    print_header("Self-RAG 추론 테스트")
    
    test_query = "EGFR 돌연변이 폐암의 1차 치료제로 오시머티닙의 효과와 부작용은 무엇인가요?"
    
    payload = {
        "query": test_query,
        "mode": "self_rag",
        "max_iterations": 2,
        "stream": False,
        "search_top_k": 10,
        "rerank_top_k": 3
    }
    
    try:
        print(f"테스트 질문: {test_query}")
        print("Self-RAG 추론 시작...")
        
        start_time = time.time()
        response = requests.post(
            f"{REASONING_RAG_URL}/query",
            json=payload,
            timeout=60  # Self-RAG는 시간이 걸릴 수 있음
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print_result(True, f"Self-RAG 완료 ({elapsed_time:.2f}초)")
            print(f"반복 횟수: {data.get('total_iterations', 0)}")
            print(f"신뢰도: {data.get('confidence_score', 0):.3f}")
            print(f"소스 수: {len(data.get('sources', []))}")
            
            # 추론 단계 요약
            steps = data.get('reasoning_steps', [])
            print(f"\n추론 단계 ({len(steps)}개):")
            for i, step in enumerate(steps):
                print(f"  단계 {step.get('iteration', i) + 1}: 지지도 {step.get('support_score', 0):.2f}")
            
            # 최종 답변 미리보기
            final_answer = data.get('final_answer', '')
            preview = final_answer[:200] + "..." if len(final_answer) > 200 else final_answer
            print(f"\n최종 답변 미리보기:\n{preview}")
            
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print_result(False, f"Self-RAG 테스트 실패: {e}")

async def test_cot_rag_query():
    """CoT-RAG 추론 테스트"""
    print_header("CoT-RAG 추론 테스트")
    
    test_query = "항암제 개발에서 in vitro, in vivo, 임상시험 단계별 효능 평가 방법과 각 단계의 중요한 고려사항은 무엇인가요?"
    
    payload = {
        "query": test_query,
        "mode": "cot_rag",
        "max_iterations": 4,  # CoT는 단계가 많을 수 있음
        "stream": False,
        "search_top_k": 15,
        "rerank_top_k": 5
    }
    
    try:
        print(f"테스트 질문: {test_query}")
        print("CoT-RAG 추론 시작...")
        
        start_time = time.time()
        response = requests.post(
            f"{REASONING_RAG_URL}/query",
            json=payload,
            timeout=90  # CoT-RAG는 더 오래 걸릴 수 있음
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print_result(True, f"CoT-RAG 완료 ({elapsed_time:.2f}초)")
            print(f"단계 수: {data.get('total_iterations', 0)}")
            print(f"신뢰도: {data.get('confidence_score', 0):.3f}")
            print(f"소스 수: {len(data.get('sources', []))}")
            
            # 추론 단계 상세 정보
            steps = data.get('reasoning_steps', [])
            print(f"\n단계별 추론 과정:")
            for step in steps:
                sub_query = step.get('query', '')
                support = step.get('support_score', 0)
                print(f"  • {sub_query[:80]}... (지지도: {support:.2f})")
            
            # 최종 답변 미리보기
            final_answer = data.get('final_answer', '')
            preview = final_answer[:300] + "..." if len(final_answer) > 300 else final_answer
            print(f"\n최종 답변 미리보기:\n{preview}")
            
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print_result(False, f"CoT-RAG 테스트 실패: {e}")

async def test_stats():
    """시스템 통계 테스트"""
    print_header("시스템 통계 조회")
    
    try:
        response = requests.get(f"{REASONING_RAG_URL}/stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get("stats", {})
            
            print_result(True, f"버전: {stats.get('version')}")
            
            # 파이프라인 설정
            config = stats.get("pipeline_config", {})
            print(f"임베딩 모델: {config.get('embedding_model')}")
            print(f"LLM 모델: {config.get('llm_model')}")
            print(f"Reranker 모델: {config.get('reranker_model')}")
            print(f"검색 설정: {config.get('search_top_k')}->{config.get('rerank_top_k')}")
            
            # 기능 상태
            features = stats.get("features", {})
            print(f"\n지원 기능:")
            for feature, enabled in features.items():
                status = "✅" if enabled else "❌"
                print(f"  {status} {feature}")
                
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print_result(False, f"통계 조회 실패: {e}")

async def test_streaming_basic():
    """기본 스트리밍 테스트"""
    print_header("스트리밍 기능 기본 테스트")
    
    test_query = "아스피린의 작용 기전과 부작용은 무엇인가요?"
    
    payload = {
        "query": test_query,
        "mode": "self_rag",
        "max_iterations": 2,
        "stream": True
    }
    
    try:
        print(f"스트리밍 테스트 질문: {test_query}")
        
        response = requests.post(
            f"{REASONING_RAG_URL}/stream",
            json=payload,
            timeout=30,
            stream=True
        )
        
        if response.status_code == 200:
            print_result(True, "스트리밍 연결 성공")
            
            chunk_count = 0
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            event_type = data.get('type', 'unknown')
                            
                            chunk_count += 1
                            if chunk_count <= 5:  # 처음 5개 청크만 출력
                                print(f"  스트림 이벤트: {event_type}")
                                
                            if event_type == 'end':
                                break
                                
                        except json.JSONDecodeError:
                            continue
            
            print(f"총 {chunk_count}개 스트림 이벤트 수신")
            
        else:
            print_result(False, f"HTTP {response.status_code}")
            
    except Exception as e:
        print_result(False, f"스트리밍 테스트 실패: {e}")

async def main():
    """메인 테스트 함수"""
    print("🧬 GAIA-BT v3.86 Reasoning RAG 시스템 테스트")
    print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 서버: {BASE_URL}")
    
    # 테스트 실행
    await test_health_check()
    await test_modes_info()
    await test_stats()
    await test_self_rag_query()
    await test_cot_rag_query()
    await test_streaming_basic()
    
    print_header("테스트 완료")
    print("✨ 모든 테스트가 완료되었습니다!")
    print("\n📊 결과 요약:")
    print("  • Self-RAG: 반성적 추론 시스템")
    print("  • CoT-RAG: 단계별 사고 연쇄 추론")
    print("  • API 통합: 5개 엔드포인트 제공")
    print("  • 실시간 스트리밍: 추론 과정 모니터링")

if __name__ == "__main__":
    asyncio.run(main())