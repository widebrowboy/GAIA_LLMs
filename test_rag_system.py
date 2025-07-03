#!/usr/bin/env python3
"""
RAG 시스템 테스트 스크립트

Milvus 연결, 임베딩 생성, 문서 저장 및 검색 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag import EmbeddingService, RAGPipeline
from app.rag.vector_store_lite import MilvusLiteVectorStore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_embedding_service():
    """임베딩 서비스 테스트"""
    print("\n=== 임베딩 서비스 테스트 ===")
    
    embedding_service = EmbeddingService()
    
    # 테스트 텍스트
    test_text = "EGFR 표적 항암제는 폐암 치료에 중요한 역할을 합니다."
    
    # 임베딩 생성
    embedding = embedding_service.embed_text(test_text)
    
    if embedding:
        print(f"✅ 임베딩 생성 성공!")
        print(f"   - 차원: {len(embedding)}")
        print(f"   - 첫 5개 값: {embedding[:5]}")
    else:
        print("❌ 임베딩 생성 실패")
        return False
    
    return True


def test_milvus_connection():
    """Milvus Lite 연결 테스트"""
    print("\n=== Milvus Lite 연결 테스트 ===")
    
    # 임베딩 차원 확인
    embedding_service = EmbeddingService()
    dimension = embedding_service.get_embedding_dimension()
    if not dimension:
        dimension = 1024
    
    vector_store = MilvusLiteVectorStore(
        db_file="./test_milvus_lite.db",
        dimension=dimension
    )
    
    # Milvus Lite 연결
    if vector_store.connect():
        print("✅ Milvus Lite 연결 성공!")
    else:
        print("❌ Milvus Lite 연결 실패")
        return False
    
    # 컬렉션 생성
    if vector_store.create_collection():
        print("✅ 컬렉션 생성/확인 성공!")
    else:
        print("❌ 컬렉션 생성 실패")
        return False
    
    return True


def test_rag_pipeline():
    """전체 RAG 파이프라인 테스트"""
    print("\n=== RAG 파이프라인 테스트 ===")
    
    # RAG 파이프라인 초기화 (Milvus Lite 사용)
    rag_pipeline = RAGPipeline(
        milvus_lite_db="./test_milvus_lite.db"
    )
    
    # 테스트 문서 추가
    test_documents = [
        """
        EGFR (Epidermal Growth Factor Receptor) 돌연변이는 비소세포폐암(NSCLC) 환자의 
        약 10-15%에서 발견됩니다. EGFR-TKI (Tyrosine Kinase Inhibitor) 치료제인 
        게피티닙(Gefitinib), 엘로티닙(Erlotinib), 아파티닙(Afatinib) 등이 
        1차 치료제로 사용됩니다.
        """,
        """
        최근 3세대 EGFR-TKI인 오시머티닙(Osimertinib)이 T790M 내성 돌연변이를 가진 
        환자들에게 효과적인 것으로 입증되었습니다. FLAURA 연구에서 오시머티닙은 
        1차 치료에서도 우수한 효과를 보였으며, 중앙 무진행 생존기간(PFS)이 
        18.9개월로 나타났습니다.
        """,
        """
        ALK (Anaplastic Lymphoma Kinase) 재배열은 NSCLC 환자의 약 5%에서 발견됩니다.
        크리조티닙(Crizotinib)이 최초의 ALK 억제제로 승인되었으며, 이후 
        세리티닙(Ceritinib), 알렉티닙(Alectinib), 브리가티닙(Brigatinib) 등의 
        차세대 ALK 억제제가 개발되었습니다.
        """
    ]
    
    # 메타데이터 추가
    metadata = [
        {"topic": "EGFR", "type": "overview"},
        {"topic": "EGFR", "type": "clinical_trial", "drug": "Osimertinib"},
        {"topic": "ALK", "type": "overview"}
    ]
    
    print("문서 추가 중...")
    success = rag_pipeline.add_documents(
        documents=test_documents,
        metadata=metadata,
        chunk_size=200
    )
    
    if success:
        print("✅ 문서 추가 성공!")
    else:
        print("❌ 문서 추가 실패")
        return False
    
    # 통계 확인
    stats = rag_pipeline.get_stats()
    print(f"\n벡터 스토어 통계:")
    print(f"   - 컬렉션: {stats['vector_store'].get('name', 'N/A')}")
    print(f"   - 저장된 엔티티 수: {stats['vector_store'].get('num_entities', 0)}")
    
    # 쿼리 테스트
    print("\n=== 쿼리 테스트 ===")
    
    test_queries = [
        "EGFR 돌연변이 폐암의 1차 치료제는 무엇인가요?",
        "오시머티닙의 임상시험 결과는 어떻게 되나요?",
        "ALK 재배열 폐암의 치료 옵션은?"
    ]
    
    for query in test_queries:
        print(f"\n질문: {query}")
        
        # RAG 쿼리 실행
        response = rag_pipeline.query(query, top_k=3)
        
        print(f"답변: {response.answer[:200]}...")
        print(f"참조 소스 수: {len(response.sources)}")
        
        if response.sources:
            print("첫 번째 소스:")
            print(f"   - 텍스트: {response.sources[0]['text'][:100]}...")
            print(f"   - 점수: {response.sources[0]['score']:.4f}")
            print(f"   - 메타데이터: {response.sources[0]['metadata']}")
    
    return True


def main():
    """메인 테스트 함수"""
    print("🧬 GAIA-BT RAG 시스템 테스트 시작")
    
    # 1. 임베딩 서비스 테스트
    if not test_embedding_service():
        print("\n❌ 임베딩 서비스 테스트 실패")
        print("Ollama가 실행 중이고 mxbai-embed-large 모델이 설치되어 있는지 확인하세요.")
        return
    
    # 2. Milvus 연결 테스트
    if not test_milvus_connection():
        print("\n❌ Milvus Lite 연결 테스트 실패")
        return
    
    # 3. RAG 파이프라인 테스트
    if not test_rag_pipeline():
        print("\n❌ RAG 파이프라인 테스트 실패")
        return
    
    print("\n✅ 모든 테스트 성공! RAG 시스템이 정상적으로 작동합니다.")


if __name__ == "__main__":
    main()