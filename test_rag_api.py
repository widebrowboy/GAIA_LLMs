#!/usr/bin/env python3
"""
RAG API 테스트 스크립트

API 서버를 통한 RAG 시스템 테스트
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"


def test_add_documents():
    """문서 추가 테스트"""
    print("\n=== 문서 추가 테스트 ===")
    
    documents = [
        {
            "text": """
            EGFR (Epidermal Growth Factor Receptor) 돌연변이는 비소세포폐암(NSCLC) 환자의 
            약 10-15%에서 발견됩니다. EGFR-TKI (Tyrosine Kinase Inhibitor) 치료제인 
            게피티닙(Gefitinib), 엘로티닙(Erlotinib), 아파티닙(Afatinib) 등이 
            1차 치료제로 사용됩니다.
            """,
            "metadata": {"topic": "EGFR", "type": "overview"}
        },
        {
            "text": """
            최근 3세대 EGFR-TKI인 오시머티닙(Osimertinib)이 T790M 내성 돌연변이를 가진 
            환자들에게 효과적인 것으로 입증되었습니다. FLAURA 연구에서 오시머티닙은 
            1차 치료에서도 우수한 효과를 보였으며, 중앙 무진행 생존기간(PFS)이 
            18.9개월로 나타났습니다.
            """,
            "metadata": {"topic": "EGFR", "type": "clinical_trial", "drug": "Osimertinib"}
        },
        {
            "text": """
            ALK (Anaplastic Lymphoma Kinase) 재배열은 NSCLC 환자의 약 5%에서 발견됩니다.
            크리조티닙(Crizotinib)이 최초의 ALK 억제제로 승인되었으며, 이후 
            세리티닙(Ceritinib), 알렉티닙(Alectinib), 브리가티닙(Brigatinib) 등의 
            차세대 ALK 억제제가 개발되었습니다.
            """,
            "metadata": {"topic": "ALK", "type": "overview"}
        }
    ]
    
    payload = {
        "documents": documents,
        "chunk_size": 200
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/rag/documents",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 문서 추가 성공: {result['message']}")
            return True
        else:
            print(f"❌ 문서 추가 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API 호출 오류: {str(e)}")
        return False


def test_query():
    """RAG 쿼리 테스트"""
    print("\n=== RAG 쿼리 테스트 ===")
    
    queries = [
        "EGFR 돌연변이 폐암의 1차 치료제는 무엇인가요?",
        "오시머티닙의 임상시험 결과는 어떻게 되나요?",
        "ALK 재배열 폐암의 치료 옵션은 무엇인가요?"
    ]
    
    for query in queries:
        print(f"\n질문: {query}")
        
        payload = {
            "query": query,
            "top_k": 3
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/rag/query",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"답변: {result['answer'][:200]}...")
                print(f"참조 소스 수: {len(result['sources'])}")
                
                if result['sources']:
                    first_source = result['sources'][0]
                    print(f"첫 번째 소스:")
                    print(f"   - 텍스트: {first_source['text'][:100]}...")
                    print(f"   - 점수: {first_source['score']:.4f}")
                    print(f"   - 메타데이터: {first_source['metadata']}")
            else:
                print(f"❌ 쿼리 실패: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ API 호출 오류: {str(e)}")


def test_search():
    """문서 검색 테스트"""
    print("\n=== 문서 검색 테스트 ===")
    
    query = "EGFR 치료제"
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/rag/search",
            params={"query": query, "top_k": 3}
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"검색 결과 수: {len(results)}")
            
            for i, result in enumerate(results):
                print(f"\n결과 {i+1}:")
                print(f"   - 텍스트: {result['text'][:100]}...")
                print(f"   - 점수: {result['score']:.4f}")
                print(f"   - 메타데이터: {result['metadata']}")
        else:
            print(f"❌ 검색 실패: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ API 호출 오류: {str(e)}")


def test_stats():
    """RAG 시스템 통계 확인"""
    print("\n=== RAG 시스템 통계 ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/rag/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"통계 정보:")
            print(f"   - 임베딩 모델: {stats.get('embedding_model', 'N/A')}")
            print(f"   - 생성 모델: {stats.get('generation_model', 'N/A')}")
            
            vector_store = stats.get('vector_store', {})
            print(f"   - 컬렉션 이름: {vector_store.get('name', 'N/A')}")
            print(f"   - 저장된 문서 수: {vector_store.get('num_entities', 0)}")
        else:
            print(f"❌ 통계 조회 실패: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ API 호출 오류: {str(e)}")


def main():
    """메인 테스트 함수"""
    print("🚀 RAG API 테스트 시작")
    
    # API 서버 상태 확인
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code != 200:
            print(f"❌ API 서버가 실행되지 않습니다. {API_BASE_URL}에서 접근할 수 없습니다.")
            return
        print("✅ API 서버 연결 확인")
    except:
        print(f"❌ API 서버가 실행되지 않습니다. {API_BASE_URL}에서 접근할 수 없습니다.")
        return
    
    # 1. 문서 추가
    if not test_add_documents():
        return
    
    # 2. 통계 확인
    test_stats()
    
    # 3. RAG 쿼리
    test_query()
    
    # 4. 문서 검색
    test_search()
    
    print("\n✅ 모든 RAG API 테스트 완료!")


if __name__ == "__main__":
    main()