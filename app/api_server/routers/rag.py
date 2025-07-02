"""
RAG 시스템 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from app.rag import RAGPipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["RAG"])

# 전역 RAG 파이프라인 인스턴스
rag_pipeline = None


class DocumentInput(BaseModel):
    """문서 입력 모델"""
    text: str = Field(..., description="문서 텍스트")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="문서 메타데이터")


class AddDocumentsRequest(BaseModel):
    """문서 추가 요청 모델"""
    documents: List[DocumentInput] = Field(..., description="추가할 문서 리스트")
    chunk_size: int = Field(default=500, description="청크 크기")


class QueryRequest(BaseModel):
    """쿼리 요청 모델"""
    query: str = Field(..., description="검색 쿼리")
    top_k: int = Field(default=5, description="반환할 결과 수")
    system_prompt: Optional[str] = Field(default=None, description="시스템 프롬프트")
    use_reranking: bool = Field(default=True, description="리랭킹 사용 여부")
    top_k_initial: Optional[int] = Field(default=None, description="1단계 검색 결과 수 (리랭킹용)")


class RAGResponse(BaseModel):
    """RAG 응답 모델"""
    answer: str = Field(..., description="생성된 답변")
    sources: List[Dict[str, Any]] = Field(..., description="참조 소스")
    query: str = Field(..., description="원본 쿼리")
    context: List[str] = Field(..., description="사용된 컨텍스트")


# RAG 파이프라인 초기화
try:
    rag_pipeline = RAGPipeline()
    logger.info("RAG pipeline initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
    rag_pipeline = None


@router.post("/documents", response_model=Dict[str, Any])
async def add_documents(request: AddDocumentsRequest):
    """
    문서를 RAG 시스템에 추가
    
    - 문서를 청크로 분할
    - 임베딩 생성
    - Milvus에 저장
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        # 문서와 메타데이터 분리
        documents = [doc.text for doc in request.documents]
        metadata = [doc.metadata for doc in request.documents if doc.metadata]
        
        # 문서 추가
        success = rag_pipeline.add_documents(
            documents=documents,
            metadata=metadata if metadata else None,
            chunk_size=request.chunk_size
        )
        
        if success:
            return {
                "status": "success",
                "message": f"Successfully added {len(documents)} documents",
                "documents_count": len(documents)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add documents")
            
    except Exception as e:
        logger.error(f"Error adding documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=RAGResponse)
async def query_rag(request: QueryRequest):
    """
    RAG 시스템에 쿼리 실행 (리랭킹 지원)
    
    **전체 RAG 파이프라인:**
    1. **문서 검색**: 2단계 검색 아키텍처 (Retrieval + Reranking)
    2. **컨텍스트 추출**: 검색된 문서에서 관련 정보 추출
    3. **응답 생성**: gemma3-12b를 활용한 컨텍스트 기반 답변 생성
    
    **Request Body 예시:**
    ```json
    {
        "query": "EGFR 돌연변이 폐암의 1차 치료제는 무엇인가요?",
        "top_k": 5,
        "use_reranking": true,
        "top_k_initial": 20,
        "system_prompt": "당신은 신약개발 전문 AI 어시스턴트입니다."
    }
    ```
    
    **Response 예시:**
    ```json
    {
        "answer": "EGFR 돌연변이 폐암의 1차 치료제로는 게피티닙, 엘로티닙, 아파티닙 등의 EGFR-TKI가 사용됩니다.",
        "sources": [
            {
                "text": "EGFR-TKI 치료제인 게피티닙(Gefitinib)...",
                "score": 0.95,
                "metadata": {"topic": "EGFR", "type": "overview"}
            }
        ],
        "query": "EGFR 돌연변이 폐암의 1차 치료제는 무엇인가요?",
        "context": ["관련 컨텍스트 텍스트..."]
    }
    ```
    
    **Parameters:**
    - **query**: 사용자 질문
    - **top_k**: 참조할 문서 수 (기본값: 5)
    - **use_reranking**: 리랭킹 사용 여부 (기본값: True)
    - **top_k_initial**: 1단계 검색 결과 수 (기본값: None, 자동 설정)
    - **system_prompt**: 시스템 프롬프트 (선택사항)
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        # 임시로 리랭킹 설정 저장 및 변경
        original_reranking = rag_pipeline.enable_reranking
        if not request.use_reranking:
            rag_pipeline.enable_reranking = False
        
        try:
            # RAG 쿼리 실행
            result = rag_pipeline.query(
                query=request.query,
                top_k=request.top_k,
                system_prompt=request.system_prompt,
                top_k_initial=request.top_k_initial
            )
        finally:
            # 원래 설정 복원
            rag_pipeline.enable_reranking = original_reranking
        
        return RAGResponse(
            answer=result.answer,
            sources=result.sources,
            query=result.query,
            context=result.context
        )
        
    except Exception as e:
        logger.error(f"Error querying RAG: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[Dict[str, Any]])
async def search_documents(
    query: str = "EGFR 치료제",
    top_k: int = 5,
    use_reranking: bool = True,
    top_k_initial: Optional[int] = None
):
    """
    문서 검색만 수행 (2단계 검색 아키텍처 지원)
    
    **2단계 검색 프로세스:**
    1. **1단계 (Retrieval)**: mxbai-embed-large로 임베딩된 벡터를 Milvus에서 빠르게 검색
    2. **2단계 (Reranking)**: BGE Reranker로 후보 문서들을 정밀하게 재랭킹
    
    **Parameters:**
    - **query**: 검색 쿼리 (예: "EGFR 치료제", "오시머티닙 효과")
    - **top_k**: 최종 반환할 결과 수 (기본값: 5)
    - **use_reranking**: 리랭킹 사용 여부 (기본값: True)
    - **top_k_initial**: 1단계 검색 결과 수 (리랭킹용, 기본값: top_k * 4)
    
    **사용 예시:**
    ```bash
    # 기본 리랭킹 검색
    curl "http://localhost:8000/api/rag/search?query=EGFR 치료제&top_k=3"
    
    # 리랭킹 비활성화
    curl "http://localhost:8000/api/rag/search?query=EGFR 치료제&use_reranking=false"
    
    # 고급 설정 (1단계에서 20개 검색 후 3개로 리랭킹)
    curl "http://localhost:8000/api/rag/search?query=EGFR 치료제&top_k=3&top_k_initial=20"
    ```
    
    **Returns:**
    - 검색된 문서 리스트 (텍스트, 점수, 메타데이터 포함)
    - 리랭킹 활성화 시 더 정확한 문서 순위 제공
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        # 임시로 리랭킹 설정 저장 및 변경
        original_reranking = rag_pipeline.enable_reranking
        if not use_reranking:
            rag_pipeline.enable_reranking = False
        
        try:
            # 검색만 수행
            results = rag_pipeline.retrieve(
                query=query, 
                top_k=top_k,
                top_k_initial=top_k_initial
            )
            
            # 결과 포맷팅
            formatted_results = []
            for text, score, metadata in results:
                formatted_results.append({
                    "text": text,
                    "score": float(score),
                    "metadata": metadata
                })
            
            return formatted_results
        finally:
            # 원래 설정 복원
            rag_pipeline.enable_reranking = original_reranking
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=Dict[str, Any])
async def get_rag_stats():
    """
    RAG 시스템 통계 조회 (리랭킹 정보 포함)
    
    **반환 정보:**
    - **vector_store**: Milvus 벡터 스토어 상태 및 문서 수
    - **embedding_model**: 임베딩 모델 정보 (mxbai-embed-large)
    - **generation_model**: 생성 모델 정보 (gemma3-12b)
    - **reranking**: 리랭킹 시스템 상태
    
    **Response 예시:**
    ```json
    {
        "vector_store": {
            "name": "gaia_bt_documents",
            "db_file": "./milvus_lite.db",
            "exists": true,
            "num_entities": 15
        },
        "embedding_model": "mxbai-embed-large",
        "generation_model": "gemma3-12b:latest",
        "reranking": {
            "enabled": true,
            "available": true,
            "model": "BAAI/bge-reranker-v2-gemma",
            "device": "cpu"
        }
    }
    ```
    
    **리랭킹 상태 설명:**
    - **available**: PyMilvus BGERerankFunction 사용 가능 여부
    - **enabled**: 현재 리랭킹 활성화 상태
    - **model**: 사용 중인 리랭킹 모델 이름
    - **device**: 실행 디바이스 (cpu/cuda)
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        stats = rag_pipeline.get_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting RAG stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents", response_model=Dict[str, Any])
async def clear_documents():
    """
    모든 문서 삭제 (컬렉션 초기화)
    
    주의: 이 작업은 되돌릴 수 없습니다
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        # 컬렉션 삭제 및 재생성
        rag_pipeline.vector_store.delete_collection()
        rag_pipeline.vector_store.create_collection()
        
        return {
            "status": "success",
            "message": "All documents cleared successfully"
        }
        
    except Exception as e:
        logger.error(f"Error clearing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))