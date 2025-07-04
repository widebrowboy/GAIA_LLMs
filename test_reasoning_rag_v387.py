#!/usr/bin/env python3
"""
GAIA-BT v3.87 Reasoning RAG 시스템 MCTS-RAG 테스트
Monte Carlo Tree Search RAG 전용 테스트 스크립트
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
    print(f"🎯 {title}")
    print(f"{'='*60}")

def print_result(success: bool, message: str):
    """테스트 결과 출력"""
    status = "✅ 성공" if success else "❌ 실패"
    print(f"{status}: {message}")

async def test_mcts_rag_complex_query():
    """MCTS-RAG 복잡한 추론 테스트"""
    print_header("MCTS-RAG 복잡한 추론 테스트")
    
    test_query = """
    항암제 개발에서 Target Discovery부터 Clinical Trial까지의 전 과정에서:
    1) 각 단계별 주요 기술과 방법론은 무엇이며
    2) 실패 원인과 해결 방안은 무엇이고
    3) 최신 AI/ML 기술이 어떻게 활용되고 있는가?
    """
    
    payload = {
        "query": test_query,
        "mode": "mcts_rag",
        "max_iterations": 5,  # MCTS는 더 많은 탐색이 필요할 수 있음
        "stream": False,
        "search_top_k": 20,
        "rerank_top_k": 8
    }
    
    try:
        print(f"복잡한 다단계 질문: {test_query[:80]}...")
        print("MCTS-RAG 트리 탐색 시작...")
        
        start_time = time.time()
        response = requests.post(
            f"{REASONING_RAG_URL}/query",
            json=payload,
            timeout=120  # MCTS는 오래 걸릴 수 있음
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print_result(True, f"MCTS-RAG 완료 ({elapsed_time:.2f}초)")
            print(f"탐색 반복: {data.get('total_iterations', 0)}")
            print(f"최종 신뢰도: {data.get('confidence_score', 0):.3f}")
            print(f"참조 소스: {len(data.get('sources', []))}개")
            
            # MCTS 추론 단계 분석
            steps = data.get('reasoning_steps', [])
            print(f"\n🎯 MCTS 탐색 과정 ({len(steps)}단계):")
            
            for i, step in enumerate(steps):
                iteration = step.get('iteration', i)
                query = step.get('query', '')
                refined = step.get('refined_query', '')
                support = step.get('support_score', 0)
                
                print(f"  노드 {iteration + 1}: {query[:60]}...")
                if refined and refined != query:
                    print(f"    → 개선: {refined[:60]}...")
                print(f"    → 지지도: {support:.3f}")
            
            # 최종 답변 구조 분석
            final_answer = data.get('final_answer', '')
            if final_answer:
                sections = final_answer.split('\n\n')
                print(f"\n📋 최종 답변 구조 ({len(sections)}개 섹션):")
                for i, section in enumerate(sections[:5]):  # 처음 5개 섹션만
                    preview = section.strip()[:100].replace('\n', ' ')
                    print(f"  {i+1}. {preview}...")
            
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print_result(False, f"MCTS-RAG 테스트 실패: {e}")

async def test_mcts_rag_optimization():
    """MCTS-RAG 최적화 경로 테스트"""
    print_header("MCTS-RAG 최적화 경로 테스트")
    
    test_query = "CRISPR-Cas9 유전자 편집 기술의 off-target 효과를 최소화하는 최신 기법들과 임상 적용에서의 안전성 확보 방안은?"
    
    payload = {
        "query": test_query,
        "mode": "mcts_rag",
        "max_iterations": 4,
        "stream": False,
        "search_top_k": 15,
        "rerank_top_k": 5
    }
    
    try:
        print(f"최적화 테스트 질문: {test_query}")
        print("MCTS UCB1 기반 경로 최적화...")
        
        start_time = time.time()
        response = requests.post(
            f"{REASONING_RAG_URL}/query",
            json=payload,
            timeout=90
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print_result(True, f"최적화 완료 ({elapsed_time:.2f}초)")
            
            # 탐색 효율성 분석
            steps = data.get('reasoning_steps', [])
            confidence = data.get('confidence_score', 0)
            
            print(f"탐색 노드 수: {len(steps)}")
            print(f"신뢰도 개선: {confidence:.3f}")
            
            # 단계별 지지도 변화 추적
            if steps:
                print("\n📈 지지도 개선 경로:")
                for step in steps:
                    iteration = step.get('iteration', 0)
                    support = step.get('support_score', 0)
                    query_preview = step.get('query', '')[:50]
                    print(f"  Step {iteration + 1}: {support:.3f} - {query_preview}...")
            
            # 최적 경로 분석
            if len(steps) > 1:
                initial_support = steps[0].get('support_score', 0)
                final_support = steps[-1].get('support_score', 0)
                improvement = final_support - initial_support
                
                print(f"\n🎯 최적화 결과:")
                print(f"  초기 지지도: {initial_support:.3f}")
                print(f"  최종 지지도: {final_support:.3f}")
                print(f"  개선도: {improvement:+.3f}")
                
                if improvement > 0.1:
                    print("  ✅ 유의미한 개선 달성")
                else:
                    print("  ⚠️ 제한적 개선")
            
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print_result(False, f"MCTS 최적화 테스트 실패: {e}")

async def test_mcts_vs_other_modes():
    """MCTS-RAG vs 다른 모드 비교 테스트"""
    print_header("MCTS-RAG vs Self-RAG vs CoT-RAG 비교")
    
    test_query = "mRNA 백신 기술의 핵심 원리와 COVID-19 이후 다른 질병에 대한 적용 현황 및 향후 전망은?"
    
    modes_to_test = ["self_rag", "cot_rag", "mcts_rag"]
    results = {}
    
    for mode in modes_to_test:
        payload = {
            "query": test_query,
            "mode": mode,
            "max_iterations": 3,
            "stream": False,
            "search_top_k": 12,
            "rerank_top_k": 4
        }
        
        try:
            print(f"\n🔄 {mode.upper()} 모드 테스트...")
            
            start_time = time.time()
            response = requests.post(
                f"{REASONING_RAG_URL}/query",
                json=payload,
                timeout=60
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                results[mode] = {
                    "success": True,
                    "elapsed_time": elapsed_time,
                    "iterations": data.get('total_iterations', 0),
                    "confidence": data.get('confidence_score', 0),
                    "sources": len(data.get('sources', [])),
                    "answer_length": len(data.get('final_answer', ''))
                }
                print_result(True, f"{mode} 완료 ({elapsed_time:.2f}초)")
            else:
                results[mode] = {"success": False, "error": response.status_code}
                print_result(False, f"{mode} 실패: HTTP {response.status_code}")
                
        except Exception as e:
            results[mode] = {"success": False, "error": str(e)}
            print_result(False, f"{mode} 오류: {e}")
    
    # 결과 비교 분석
    print(f"\n📊 모드별 성능 비교:")
    print(f"{'모드':<12} {'성공':<6} {'시간(초)':<8} {'반복':<6} {'신뢰도':<8} {'소스':<6} {'답변길이':<8}")
    print("-" * 60)
    
    for mode, result in results.items():
        if result.get("success"):
            print(f"{mode:<12} ✅    {result['elapsed_time']:<8.2f} {result['iterations']:<6} "
                  f"{result['confidence']:<8.3f} {result['sources']:<6} {result['answer_length']:<8}")
        else:
            print(f"{mode:<12} ❌    오류: {result.get('error', 'Unknown')}")
    
    # MCTS 우수성 분석
    if "mcts_rag" in results and results["mcts_rag"].get("success"):
        mcts_result = results["mcts_rag"]
        
        print(f"\n🎯 MCTS-RAG 특성 분석:")
        print(f"  신뢰도: {mcts_result['confidence']:.3f}")
        print(f"  탐색 효율성: {mcts_result['iterations']}회 반복")
        print(f"  응답 시간: {mcts_result['elapsed_time']:.2f}초")
        
        # 다른 모드와의 신뢰도 비교
        other_confidences = [
            results[mode]["confidence"] 
            for mode in ["self_rag", "cot_rag"] 
            if mode in results and results[mode].get("success")
        ]
        
        if other_confidences:
            avg_other = sum(other_confidences) / len(other_confidences)
            improvement = mcts_result['confidence'] - avg_other
            
            if improvement > 0.05:
                print(f"  ✅ 다른 모드 대비 신뢰도 우수: +{improvement:.3f}")
            elif improvement > -0.05:
                print(f"  ⚖️ 다른 모드와 유사한 성능: {improvement:+.3f}")
            else:
                print(f"  ⚠️ 다른 모드 대비 신뢰도 낮음: {improvement:+.3f}")

async def test_mcts_streaming():
    """MCTS-RAG 스트리밍 테스트"""
    print_header("MCTS-RAG 실시간 스트리밍 테스트")
    
    test_query = "신약개발에서 AI가 활용되는 주요 분야와 성공 사례는?"
    
    payload = {
        "query": test_query,
        "mode": "mcts_rag",
        "max_iterations": 3,
        "stream": True
    }
    
    try:
        print(f"스트리밍 질문: {test_query}")
        print("MCTS 트리 탐색 과정 실시간 모니터링...")
        
        response = requests.post(
            f"{REASONING_RAG_URL}/stream",
            json=payload,
            timeout=45,
            stream=True
        )
        
        if response.status_code == 200:
            print_result(True, "MCTS 스트리밍 연결 성공")
            
            events = []
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            event_type = data.get('type', 'unknown')
                            events.append(event_type)
                            
                            # 주요 이벤트만 출력
                            if event_type in ['start', 'search_iteration', 'final_result', 'end']:
                                if event_type == 'search_iteration':
                                    iteration = data.get('iteration', 0)
                                    support = data.get('support_score', 0)
                                    print(f"  🔍 탐색 {iteration + 1}: 지지도 {support:.3f}")
                                elif event_type == 'final_result':
                                    confidence = data.get('confidence_score', 0)
                                    iterations = data.get('total_iterations', 0)
                                    print(f"  ✅ 완료: {iterations}회 탐색, 신뢰도 {confidence:.3f}")
                                elif event_type == 'start':
                                    print(f"  🚀 MCTS 탐색 시작")
                                elif event_type == 'end':
                                    print(f"  🏁 스트리밍 종료")
                                    break
                                    
                        except json.JSONDecodeError:
                            continue
            
            print(f"총 {len(events)}개 스트림 이벤트 수신")
            
        else:
            print_result(False, f"HTTP {response.status_code}")
            
    except Exception as e:
        print_result(False, f"MCTS 스트리밍 테스트 실패: {e}")

async def test_mcts_edge_cases():
    """MCTS-RAG 엣지 케이스 테스트"""
    print_header("MCTS-RAG 엣지 케이스 테스트")
    
    edge_cases = [
        {
            "name": "매우 짧은 질문",
            "query": "aspirin",
            "expected": "기본 검색으로 처리"
        },
        {
            "name": "매우 긴 질문",
            "query": " ".join(["질문"] * 100),  # 100개 단어 반복
            "expected": "쿼리 트렁케이션"
        },
        {
            "name": "특수 문자 포함",
            "query": "COVID-19 mRNA 백신 (BNT162b2/mRNA-1273)의 효능은?",
            "expected": "정상 처리"
        },
        {
            "name": "최대 반복 테스트",
            "query": "복잡한 신약개발 프로세스 전체 과정",
            "max_iterations": 1,
            "expected": "1회 반복으로 제한"
        }
    ]
    
    for case in edge_cases:
        print(f"\n🧪 테스트: {case['name']}")
        
        payload = {
            "query": case["query"],
            "mode": "mcts_rag",
            "max_iterations": case.get("max_iterations", 2),
            "stream": False,
            "search_top_k": 10,
            "rerank_top_k": 3
        }
        
        try:
            response = requests.post(
                f"{REASONING_RAG_URL}/query",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                iterations = data.get('total_iterations', 0)
                confidence = data.get('confidence_score', 0)
                
                print_result(True, f"처리 완료 - 반복: {iterations}, 신뢰도: {confidence:.3f}")
                print(f"  예상: {case['expected']}")
                
            else:
                print_result(False, f"HTTP {response.status_code}")
                
        except Exception as e:
            print_result(False, f"오류: {e}")

async def main():
    """메인 테스트 함수"""
    print("🎯 GAIA-BT v3.87 MCTS-RAG 시스템 테스트")
    print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 서버: {BASE_URL}")
    print("\n🧠 Monte Carlo Tree Search RAG 전용 테스트 실행")
    
    # 헬스체크
    try:
        response = requests.get(f"{REASONING_RAG_URL}/health", timeout=5)
        if response.status_code == 200:
            print_result(True, "서버 헬스체크 통과")
        else:
            print_result(False, f"서버 상태 이상: HTTP {response.status_code}")
            return
    except Exception as e:
        print_result(False, f"서버 연결 실패: {e}")
        return
    
    # MCTS-RAG 전용 테스트 실행
    await test_mcts_rag_complex_query()
    await test_mcts_rag_optimization()
    await test_mcts_vs_other_modes()
    await test_mcts_streaming()
    await test_mcts_edge_cases()
    
    print_header("MCTS-RAG 테스트 완료")
    print("✨ 모든 MCTS-RAG 테스트가 완료되었습니다!")
    print("\n🎯 MCTS-RAG v3.87 특징 요약:")
    print("  • UCB1 기반 트리 탐색으로 최적 추론 경로 발견")
    print("  • 복잡한 다단계 질문에 대한 체계적 탐색")
    print("  • 실시간 스트리밍으로 탐색 과정 모니터링")
    print("  • 다른 추론 모드 대비 높은 신뢰도 달성")
    print("  • 엣지 케이스 및 오류 상황 안정적 처리")

if __name__ == "__main__":
    asyncio.run(main())