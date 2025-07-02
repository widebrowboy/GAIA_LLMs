#!/usr/bin/env python3
"""
리랭킹 기능 포함 RAG API 테스트 스크립트

PyMilvus BGE Reranker 통합 테스트
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"


def test_reranking_search():
    """리랭킹 검색 기능 테스트"""
    print("\n=== 리랭킹 검색 테스트 ===")
    
    query = "EGFR 치료제"
    
    # 1. 일반 검색 (리랭킹 없이)
    print("\n🔍 일반 검색 (리랭킹 비활성화):")
    response = requests.get(
        f"{API_BASE_URL}/api/rag/search",
        params={
            "query": query, 
            "top_k": 3,
            "use_reranking": False
        }
    )
    
    if response.status_code == 200:
        normal_results = response.json()
        print(f"검색 결과 수: {len(normal_results)}")
        for i, result in enumerate(normal_results):
            print(f"   {i+1}. 점수: {result['score']:.4f}")
            print(f"      텍스트: {result['text'][:50]}...")
    else:
        print(f"❌ 일반 검색 실패: {response.status_code}")
        return
    
    # 2. 리랭킹 검색 (활성화)
    print("\n🚀 리랭킹 검색 (활성화):")
    response = requests.get(
        f"{API_BASE_URL}/api/rag/search",
        params={
            "query": query, 
            "top_k": 3,
            "use_reranking": True,
            "top_k_initial": 10  # 1단계에서 더 많이 검색
        }
    )
    
    if response.status_code == 200:
        reranked_results = response.json()
        print(f"검색 결과 수: {len(reranked_results)}")
        for i, result in enumerate(reranked_results):
            print(f"   {i+1}. 점수: {result['score']:.4f}")
            print(f"      텍스트: {result['text'][:50]}...")
        
        # 결과 비교
        print("\n📊 결과 비교:")
        print("일반 검색 vs 리랭킹 검색")
        for i in range(min(len(normal_results), len(reranked_results))):
            normal_score = normal_results[i]['score']
            reranked_score = reranked_results[i]['score']
            print(f"   {i+1}순위: {normal_score:.4f} -> {reranked_score:.4f}")
        
    else:
        print(f"❌ 리랭킹 검색 실패: {response.status_code}")


def test_reranking_query():
    """리랭킹 RAG 쿼리 테스트"""
    print("\n=== 리랭킹 RAG 쿼리 테스트 ===")
    
    query = "오시머티닙의 효과는 어떤가요?"
    
    # 1. 일반 RAG (리랭킹 없이)
    print(f"\n질문: {query}")
    print("\n🔍 일반 RAG (리랭킹 비활성화):")
    
    payload = {
        "query": query,
        "top_k": 3,
        "use_reranking": False
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/rag/query",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        normal_result = response.json()
        print(f"답변: {normal_result['answer'][:100]}...")
        print(f"참조 소스 수: {len(normal_result['sources'])}")
        if normal_result['sources']:
            print(f"첫 번째 소스 점수: {normal_result['sources'][0]['score']:.4f}")
    else:
        print(f"❌ 일반 RAG 실패: {response.status_code}")
        return
    
    # 2. 리랭킹 RAG (활성화)
    print("\n🚀 리랭킹 RAG (활성화):")
    
    payload = {
        "query": query,
        "top_k": 3,
        "use_reranking": True,
        "top_k_initial": 10
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/rag/query",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        reranked_result = response.json()
        print(f"답변: {reranked_result['answer'][:100]}...")
        print(f"참조 소스 수: {len(reranked_result['sources'])}")
        if reranked_result['sources']:
            print(f"첫 번째 소스 점수: {reranked_result['sources'][0]['score']:.4f}")
        
        # 소스 비교
        print("\n📊 소스 순위 비교:")
        normal_sources = normal_result['sources']
        reranked_sources = reranked_result['sources']
        
        for i in range(min(len(normal_sources), len(reranked_sources))):
            normal_score = normal_sources[i]['score']
            reranked_score = reranked_sources[i]['score']
            normal_text = normal_sources[i]['text'][:30]
            reranked_text = reranked_sources[i]['text'][:30]
            
            print(f"   {i+1}순위:")
            print(f"     일반: {normal_score:.4f} | {normal_text}...")
            print(f"     리랭킹: {reranked_score:.4f} | {reranked_text}...")
        
    else:
        print(f"❌ 리랭킹 RAG 실패: {response.status_code}")


def test_system_stats():
    """시스템 통계 확인"""
    print("\n=== 시스템 통계 확인 ===")
    
    response = requests.get(f"{API_BASE_URL}/api/rag/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"📊 시스템 통계:")
        print(f"   - 임베딩 모델: {stats['embedding_model']}")
        print(f"   - 생성 모델: {stats['generation_model']}")
        print(f"   - 저장된 문서 수: {stats['vector_store']['num_entities']}")
        
        reranking = stats.get('reranking', {})
        print(f"   - 리랭킹 사용 가능: {reranking.get('available', False)}")
        print(f"   - 리랭킹 활성화: {reranking.get('enabled', False)}")
        print(f"   - 리랭킹 모델: {reranking.get('model', 'N/A')}")
        print(f"   - 디바이스: {reranking.get('device', 'N/A')}")
    else:
        print(f"❌ 통계 조회 실패: {response.status_code}")


def main():
    """메인 테스트 함수"""
    print("🚀 리랭킹 기능 RAG API 테스트 시작")
    
    # API 서버 상태 확인
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code != 200:
            print(f"❌ API 서버가 실행되지 않습니다.")
            return
        print("✅ API 서버 연결 확인")
    except:
        print(f"❌ API 서버가 실행되지 않습니다.")
        return
    
    # 1. 시스템 통계 확인
    test_system_stats()
    
    # 2. 리랭킹 검색 테스트
    test_reranking_search()
    
    # 3. 리랭킹 RAG 쿼리 테스트
    test_reranking_query()
    
    print("\n✅ 모든 리랭킹 API 테스트 완료!")


if __name__ == "__main__":
    main()