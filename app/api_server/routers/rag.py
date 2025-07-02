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
    RAG 시스템에 쿼리 실행
    
    - 쿼리 임베딩 생성
    - 관련 문서 검색
    - 컨텍스트 기반 응답 생성
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        # RAG 쿼리 실행
        result = rag_pipeline.query(
            query=request.query,
            top_k=request.top_k,
            system_prompt=request.system_prompt
        )
        
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
    query: str,
    top_k: int = 5
):
    """
    문서 검색만 수행 (생성 없이)
    
    - 쿼리 임베딩 생성
    - 유사 문서 검색
    - 검색 결과 반환
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        # 검색만 수행
        results = rag_pipeline.retrieve(query=query, top_k=top_k)
        
        # 결과 포맷팅
        formatted_results = []
        for text, score, metadata in results:
            formatted_results.append({
                "text": text,
                "score": float(score),
                "metadata": metadata
            })
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=Dict[str, Any])
async def get_rag_stats():
    """
    RAG 시스템 통계 조회
    
    - 벡터 스토어 상태
    - 모델 정보
    - 문서 수 등
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