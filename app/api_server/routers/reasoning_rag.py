"""
Reasoning RAG API Router
Self-RAG, CoT-RAG, MCTS-RAG 통합 추론 시스템 API
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from app.rag.reasoning_rag_pipeline import ReasoningRAGPipeline, ReasoningResult

logger = logging.getLogger(__name__)

router = APIRouter()

# 전역 Reasoning RAG 파이프라인 인스턴스
reasoning_pipeline: Optional[ReasoningRAGPipeline] = None


class ReasoningRAGRequest(BaseModel):
    """Reasoning RAG 요청 모델"""
    query: str = Field(..., description="사용자 질문")
    mode: str = Field(default="self_rag", description="추론 모드 (self_rag, cot_rag, mcts_rag)")
    max_iterations: int = Field(default=3, ge=1, le=5, description="최대 반복 횟수")
    stream: bool = Field(default=False, description="스트리밍 응답 여부")
    search_top_k: int = Field(default=20, ge=5, le=50, description="벡터 검색 상위 K개")
    rerank_top_k: int = Field(default=5, ge=1, le=10, description="리랭킹 상위 K개")


class ReasoningRAGResponse(BaseModel):
    """Reasoning RAG 응답 모델"""
    success: bool
    query: str
    mode: str
    final_answer: str
    reasoning_steps: List[Dict[str, Any]]
    total_iterations: int
    confidence_score: float
    sources: List[Dict[str, Any]]
    elapsed_time: float
    timestamp: datetime


def get_reasoning_pipeline() -> ReasoningRAGPipeline:
    """Reasoning RAG 파이프라인 인스턴스 반환 (전역 싱글톤)"""
    global reasoning_pipeline
    
    if reasoning_pipeline is None:
        try:
            # 기존 RAG 시스템과 동일한 설정 사용
            reasoning_pipeline = ReasoningRAGPipeline(
                milvus_uri="./milvus_lite.db",
                collection_name="gaia_bt_documents",
                embedding_model="mxbai-embed-large",
                llm_model="gemma3-12b",
                reranker_model="BAAI/bge-reranker-v2-m3"
            )
            logger.info("Reasoning RAG Pipeline Lite 모드로 초기화 완료")
        except Exception as e:
            logger.error(f"Reasoning RAG Pipeline 초기화 실패: {e}")
            # 기본 설정으로 재시도
            reasoning_pipeline = ReasoningRAGPipeline(
                milvus_uri="./milvus_lite.db",
                collection_name="gaia_bt_documents"
            )
            logger.info("Reasoning RAG Pipeline 기본 설정으로 초기화 완료")
    
    return reasoning_pipeline


async def stream_reasoning_callback(data: Dict[str, Any]) -> str:
    """추론 과정 스트리밍 콜백"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/query", response_model=ReasoningRAGResponse)
async def reasoning_rag_query(
    request: ReasoningRAGRequest,
    background_tasks: BackgroundTasks
) -> JSONResponse:
    """
    Reasoning RAG 질의 처리 (동기 응답)
    
    - Self-RAG: 반성적 추론을 통한 반복적 검색 및 평가
    - CoT-RAG: 사고의 연쇄를 통한 단계별 추론 (v3.86 구현 예정)
    - MCTS-RAG: 몬테카를로 트리 탐색을 통한 최적 추론 경로 (v3.87 구현 예정)
    """
    try:
        pipeline = get_reasoning_pipeline()
        
        # 파이프라인 설정 업데이트
        pipeline.search_top_k = request.search_top_k
        pipeline.rerank_top_k = request.rerank_top_k
        pipeline.max_iterations = request.max_iterations
        
        logger.info(f"Reasoning RAG 요청 처리 시작 - Mode: {request.mode}, Query: {request.query[:100]}...")
        
        # 추론 실행
        result: ReasoningResult = await pipeline.reasoning_search(
            query=request.query,
            mode=request.mode
        )
        
        # 응답 데이터 변환
        reasoning_steps_data = []
        for step in result.reasoning_steps:
            step_data = {
                "iteration": step.iteration,
                "query": step.query,
                "refined_query": step.refined_query,
                "documents_count": len(step.documents),
                "top_relevance_scores": step.relevance_scores[:3],
                "partial_answer": step.partial_answer,
                "support_score": step.support_score,
                "should_continue": step.should_continue,
                "timestamp": step.timestamp.isoformat()
            }
            reasoning_steps_data.append(step_data)
        
        response_data = ReasoningRAGResponse(
            success=True,
            query=result.query,
            mode=result.mode,
            final_answer=result.final_answer,
            reasoning_steps=reasoning_steps_data,
            total_iterations=result.total_iterations,
            confidence_score=result.confidence_score,
            sources=result.sources[:5],  # 상위 5개 소스만 반환
            elapsed_time=result.elapsed_time,
            timestamp=datetime.now()
        )
        
        logger.info(f"Reasoning RAG 완료 - 반복: {result.total_iterations}, 신뢰도: {result.confidence_score:.3f}")
        
        return JSONResponse(content=response_data.dict())
        
    except Exception as e:
        logger.error(f"Reasoning RAG 처리 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Reasoning RAG 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/stream")
async def reasoning_rag_stream(request: ReasoningRAGRequest):
    """
    Reasoning RAG 스트리밍 질의 처리
    
    실시간으로 추론 과정을 스트리밍하여 사용자에게 진행 상황을 제공
    """
    try:
        pipeline = get_reasoning_pipeline()
        
        # 파이프라인 설정 업데이트
        pipeline.search_top_k = request.search_top_k
        pipeline.rerank_top_k = request.rerank_top_k
        pipeline.max_iterations = request.max_iterations
        
        async def generate_stream():
            """스트리밍 제너레이터"""
            try:
                # 스트리밍 시작 알림
                yield f"data: {json.dumps({'type': 'start', 'query': request.query, 'mode': request.mode}, ensure_ascii=False)}\n\n"
                
                # 스트리밍 콜백 함수
                async def callback(data: Dict[str, Any]):
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                
                # 추론 실행
                result: ReasoningResult = await pipeline.reasoning_search(
                    query=request.query,
                    mode=request.mode,
                    stream_callback=callback
                )
                
                # 최종 결과 전송
                final_data = {
                    "type": "final_result",
                    "final_answer": result.final_answer,
                    "total_iterations": result.total_iterations,
                    "confidence_score": result.confidence_score,
                    "elapsed_time": result.elapsed_time
                }
                yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"
                
                # 스트리밍 종료
                yield f"data: {json.dumps({'type': 'end'}, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                error_data = {
                    "type": "error",
                    "message": str(e)
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        logger.error(f"Reasoning RAG 스트리밍 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Reasoning RAG 스트리밍 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/modes")
async def get_reasoning_modes():
    """
    사용 가능한 추론 모드 목록 반환
    """
    modes = {
        "self_rag": {
            "name": "Self-RAG",
            "description": "반성적 추론을 통한 반복적 검색 및 평가",
            "status": "available",
            "reflection_tokens": ["[Retrieve]", "[Relevant]", "[Support]", "[Continue]"]
        },
        "cot_rag": {
            "name": "Chain-of-Thought RAG",
            "description": "사고의 연쇄를 통한 단계별 추론",
            "status": "available",
            "version": "v3.87",
            "features": ["question_decomposition", "sequential_reasoning", "context_accumulation"]
        },
        "mcts_rag": {
            "name": "Monte Carlo Tree Search RAG",
            "description": "몬테카를로 트리 탐색을 통한 최적 추론 경로",
            "status": "available",
            "version": "v3.87",
            "features": ["tree_search", "ucb1_selection", "path_optimization", "simulation_based"]
        }
    }
    
    return JSONResponse(content={
        "success": True,
        "modes": modes,
        "default_mode": "self_rag",
        "current_version": "v3.87"
    })


@router.get("/stats")
async def get_reasoning_stats():
    """
    Reasoning RAG 시스템 통계 정보
    """
    try:
        pipeline = get_reasoning_pipeline()
        
        stats = {
            "pipeline_config": {
                "embedding_model": "mxbai-embed-large",
                "llm_model": "gemma3-12b",
                "reranker_model": "BAAI/bge-reranker-v2-m3",
                "search_top_k": pipeline.search_top_k,
                "rerank_top_k": pipeline.rerank_top_k,
                "max_iterations": pipeline.max_iterations
            },
            "system_status": {
                "pipeline_initialized": pipeline is not None,
                "milvus_connected": True,  # TODO: 실제 연결 상태 확인
                "reranker_loaded": True   # TODO: 실제 모델 로드 상태 확인
            },
            "version": "v3.87",
            "features": {
                "self_rag": True,
                "cot_rag": True,
                "mcts_rag": True,
                "streaming": True,
                "real_time_feedback": True
            }
        }
        
        return JSONResponse(content={
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Reasoning RAG 통계 조회 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"통계 정보 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/reset")
async def reset_reasoning_pipeline():
    """
    Reasoning RAG 파이프라인 재초기화
    """
    global reasoning_pipeline
    reasoning_pipeline = None
    
    try:
        # 새 파이프라인 인스턴스 생성
        pipeline = get_reasoning_pipeline()
        return JSONResponse(content={
            "success": True,
            "message": "Reasoning RAG Pipeline 재초기화 완료",
            "collection_name": pipeline.collection_name,
            "milvus_uri": pipeline.milvus_client.uri if hasattr(pipeline.milvus_client, 'uri') else "unknown",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Reasoning RAG 파이프라인 재초기화 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"파이프라인 재초기화 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/health")
async def reasoning_health_check():
    """
    Reasoning RAG 시스템 헬스체크
    """
    try:
        pipeline = get_reasoning_pipeline()
        
        # 파이프라인 초기화 상태만 확인
        pipeline_ready = pipeline is not None and hasattr(pipeline, 'milvus_client')
        
        return JSONResponse(content={
            "success": True,
            "status": "healthy",
            "pipeline_ready": pipeline_ready,
            "search_functional": pipeline_ready,  # 기본적인 준비 상태만 확인
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Reasoning RAG 헬스체크 실패: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )