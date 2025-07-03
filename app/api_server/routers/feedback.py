"""
피드백 시스템 API 엔드포인트
사용자 피드백 저장, 조회, 분석 기능 제공
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

try:
    from app.rag.feedback_store import FeedbackVectorStore
    feedback_store_available = True
except ImportError as e:
    logging.warning(f"FeedbackVectorStore not available: {e}")
    feedback_store_available = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])

# 전역 피드백 저장소 인스턴스
feedback_store = None


class FeedbackRequest(BaseModel):
    """피드백 요청 모델"""
    question: str = Field(..., description="사용자 질문")
    answer: str = Field(..., description="AI 응답")
    feedback_type: str = Field(..., description="피드백 타입 (positive/negative)")
    session_id: Optional[str] = Field(default=None, description="세션 ID")
    user_id: Optional[str] = Field(default=None, description="사용자 ID")
    context_sources: Optional[List[str]] = Field(default=None, description="RAG 컨텍스트 소스")
    model_version: Optional[str] = Field(default="gemma3-12b", description="모델 버전")
    response_time: Optional[float] = Field(default=0.0, description="응답 생성 시간")
    confidence_score: Optional[float] = Field(default=0.0, description="모델 자신감 점수")
    check_duplicates: Optional[bool] = Field(default=True, description="중복 검사 수행 여부")
    similarity_threshold: Optional[float] = Field(default=0.95, description="유사도 임계값 (0.95 이상이면 중복)")


class FeedbackResponse(BaseModel):
    """피드백 응답 모델"""
    feedback_id: Optional[str] = Field(description="피드백 ID (중복인 경우 None)")
    status: str = Field(..., description="저장 상태 (success/duplicate/error)")
    message: str = Field(..., description="응답 메시지")
    learning_contribution: Optional[str] = Field(description="학습 기여도 설명")
    duplicate_info: Optional[Dict[str, Any]] = Field(description="중복 정보 (중복인 경우만)")


class FeedbackSearchRequest(BaseModel):
    """피드백 검색 요청 모델"""
    question: str = Field(..., description="검색할 질문")
    feedback_type: Optional[str] = Field(default=None, description="피드백 타입 필터")
    limit: int = Field(default=10, description="검색 결과 수")


class TrainingDataRequest(BaseModel):
    """학습 데이터 요청 모델"""
    min_quality_score: float = Field(default=0.8, description="최소 품질 점수")
    limit: int = Field(default=1000, description="최대 데이터 수")
    format: str = Field(default="json", description="출력 형식 (json/jsonl)")


# 피드백 저장소 초기화
def initialize_feedback_store():
    """피드백 저장소 초기화"""
    global feedback_store
    if not feedback_store_available:
        return False
    
    try:
        feedback_store = FeedbackVectorStore(
            use_server=True,  # Milvus 서버 모드 사용
            host="localhost",
            port=19530
        )
        logger.info("Feedback store initialized successfully (server mode)")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize feedback store: {e}")
        return False


# 서버 시작 시 초기화
if feedback_store_available:
    initialize_feedback_store()


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest, background_tasks: BackgroundTasks):
    """
    사용자 피드백 제출
    
    **피드백 데이터 저장 과정:**
    1. **임베딩 생성**: 질문과 응답을 mxbai-embed-large로 벡터화
    2. **벡터 DB 저장**: 피드백 데이터를 Milvus에 저장
    3. **QA 쌍 업데이트**: 질문-응답 품질 점수 계산 및 업데이트
    4. **학습 데이터 등록**: 고품질 응답은 파인튜닝 후보로 표시
    
    **Request Body 예시:**
    ```json
    {
        "question": "EGFR 돌연변이 폐암의 1차 치료제는 무엇인가요?",
        "answer": "EGFR 돌연변이 폐암의 1차 치료제로는 게피티닙, 엘로티닙, 오시머티닙 등의 EGFR-TKI가 사용됩니다.",
        "feedback_type": "positive",
        "session_id": "session_123",
        "user_id": "user_456",
        "context_sources": ["DrugBank: Gefitinib", "OpenTargets: EGFR"],
        "model_version": "gemma3-12b",
        "response_time": 2.5,
        "confidence_score": 0.89
    }
    ```
    
    **Response 예시:**
    ```json
    {
        "feedback_id": "fb_12345",
        "status": "success",
        "message": "피드백이 성공적으로 저장되었습니다. 고품질 응답으로 분류되어 AI 학습에 활용됩니다.",
        "learning_contribution": "이 긍정적 피드백으로 신약개발 oncology 도메인 응답 품질이 향상됩니다."
    }
    ```
    """
    if not feedback_store:
        raise HTTPException(
            status_code=503, 
            detail="Feedback store not available. Please check system configuration."
        )
    
    try:
        # 입력 검증
        if request.feedback_type not in ["positive", "negative"]:
            raise HTTPException(
                status_code=400,
                detail="feedback_type must be 'positive' or 'negative'"
            )
        
        # 피드백 저장 (중복 검사 포함)
        result = feedback_store.store_feedback(
            question=request.question,
            answer=request.answer,
            feedback_type=request.feedback_type,
            session_id=request.session_id,
            user_id=request.user_id,
            context_sources=request.context_sources,
            model_version=request.model_version,
            response_time=request.response_time,
            confidence_score=request.confidence_score,
            check_duplicates=request.check_duplicates,
            similarity_threshold=request.similarity_threshold
        )
        
        feedback_id = result.get("feedback_id")
        status = result.get("status")
        duplicate_info = result.get("duplicate_info")
        
        # 상태별 응답 메시지 생성
        if status == "duplicate":
            return FeedbackResponse(
                feedback_id=None,
                status="duplicate",
                message=f"🔄 유사한 피드백이 이미 존재합니다 (유사도: {duplicate_info['similarity']:.3f})",
                learning_contribution="중복 피드백으로 인해 저장되지 않았습니다. 기존 피드백이 이미 학습에 활용되고 있습니다.",
                duplicate_info=duplicate_info
            )
        elif status == "error":
            return FeedbackResponse(
                feedback_id=None,
                status="error",
                message=f"❌ 피드백 저장 실패: {result.get('message', '알 수 없는 오류')}",
                learning_contribution=None,
                duplicate_info=None
            )
        else:
            # 성공한 경우
            if request.feedback_type == "positive":
                learning_msg = "이 긍정적 피드백으로 신약개발 AI의 응답 품질이 향상됩니다. 고품질 응답으로 분류되어 향후 모델 학습에 활용됩니다."
                success_msg = "👍 피드백 감사합니다! 고품질 응답으로 분류되어 AI 학습에 활용됩니다."
            else:
                learning_msg = "이 부정적 피드백을 통해 유사한 응답 패턴을 개선하고, 더 정확한 신약개발 정보를 제공하도록 학습합니다."
                success_msg = "👎 피드백 감사합니다! 응답 품질 개선에 활용하겠습니다."
            
            return FeedbackResponse(
                feedback_id=feedback_id,
                status="success",
                message=success_msg,
                learning_contribution=learning_msg,
                duplicate_info=None
            )
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[Dict[str, Any]])
async def search_similar_feedback(request: FeedbackSearchRequest):
    """
    유사한 피드백 검색
    
    사용자 질문과 유사한 기존 피드백들을 벡터 유사도 기반으로 검색합니다.
    이를 통해 과거 피드백 패턴을 분석하고 응답 품질을 예측할 수 있습니다.
    
    **사용 예시:**
    ```bash
    curl -X POST "http://localhost:8000/api/feedback/search" \\
         -H "Content-Type: application/json" \\
         -d '{
           "question": "EGFR 치료제 부작용은 무엇인가요?",
           "feedback_type": "positive",
           "limit": 5
         }'
    ```
    """
    if not feedback_store:
        raise HTTPException(status_code=503, detail="Feedback store not available")
    
    try:
        similar_feedback = feedback_store.search_similar_feedback(
            question=request.question,
            feedback_type=request.feedback_type,
            limit=request.limit
        )
        
        return similar_feedback
        
    except Exception as e:
        logger.error(f"Error searching feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/training-data", response_model=List[Dict[str, Any]])
async def get_training_data(request: TrainingDataRequest):
    """
    Gemma 파인튜닝용 학습 데이터 조회
    
    고품질 피드백을 받은 질문-응답 쌍들을 파인튜닝 형식으로 제공합니다.
    품질 점수 0.8 이상의 데이터만 선별하여 모델 학습에 활용할 수 있습니다.
    
    **품질 기준:**
    - 긍정 피드백 비율 80% 이상
    - 완전한 문장 구조
    - 신약개발 도메인 관련성
    - 충분한 피드백 수 (최소 3개 이상)
    
    **파인튜닝 데이터 형식:**
    ```json
    {
        "instruction": "신약개발 전문 AI로서 다음 질문에 답변하세요.",
        "input": "EGFR 돌연변이 폐암의 1차 치료제는 무엇인가요?",
        "output": "EGFR 돌연변이 폐암의 1차 치료제로는...",
        "quality_score": 0.92,
        "feedback_count": 8,
        "domain": "oncology"
    }
    ```
    """
    if not feedback_store:
        raise HTTPException(status_code=503, detail="Feedback store not available")
    
    try:
        training_data = feedback_store.get_training_candidates(
            min_quality_score=request.min_quality_score,
            limit=request.limit
        )
        
        if request.format == "jsonl":
            # JSONL 형식으로 변환 (한 줄에 하나의 JSON)
            import json
            jsonl_data = []
            for item in training_data:
                jsonl_data.append(json.dumps(item, ensure_ascii=False))
            return {"format": "jsonl", "data": jsonl_data}
        
        return training_data
        
    except Exception as e:
        logger.error(f"Error getting training data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=Dict[str, Any])
async def get_feedback_stats():
    """
    피드백 시스템 통계 조회
    
    **반환 정보:**
    - **총 피드백 수**: 전체 사용자 피드백 개수
    - **긍정/부정 비율**: 썸업/썸다운 분포
    - **QA 쌍 수**: 생성된 질문-응답 쌍 개수
    - **파인튜닝 후보**: 학습에 적합한 고품질 데이터 수
    - **도메인 분포**: 신약개발 영역별 피드백 분포
    
    **Response 예시:**
    ```json
    {
        "total_feedback": 1250,
        "positive_feedback": 980,
        "negative_feedback": 270,
        "positive_ratio": 0.784,
        "total_qa_pairs": 425,
        "training_candidates": 340,
        "domain_distribution": {
            "oncology": 156,
            "cardiology": 89,
            "clinical_trial": 124
        },
        "collections": {
            "feedback_collection": "feedback_collection",
            "qa_pairs_collection": "qa_pairs_collection"
        }
    }
    ```
    """
    if not feedback_store:
        raise HTTPException(status_code=503, detail="Feedback store not available")
    
    try:
        stats = feedback_store.get_feedback_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting feedback stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reset", response_model=Dict[str, str])
async def reset_feedback_data():
    """
    피드백 데이터 초기화 (개발/테스트용)
    
    ⚠️ **주의**: 이 기능은 모든 피드백 데이터를 삭제합니다.
    프로덕션 환경에서는 사용하지 마세요.
    """
    if not feedback_store:
        raise HTTPException(status_code=503, detail="Feedback store not available")
    
    try:
        # 컬렉션 삭제 및 재생성
        feedback_store.feedback_collection.drop()
        feedback_store.qa_pairs_collection.drop()
        
        # 새로운 저장소 인스턴스 생성
        initialize_feedback_store()
        
        return {
            "status": "success",
            "message": "All feedback data has been reset successfully"
        }
        
    except Exception as e:
        logger.error(f"Error resetting feedback data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
async def feedback_system_health():
    """
    피드백 시스템 상태 확인
    
    벡터 데이터베이스 연결 상태, 컬렉션 정보, 임베딩 서비스 상태를 확인합니다.
    """
    try:
        health_status = {
            "feedback_store_available": feedback_store_available,
            "feedback_store_initialized": feedback_store is not None,
            "embedding_service": "mxbai-embed-large",
            "vector_database": "Milvus Lite",
            "collections": []
        }
        
        if feedback_store:
            try:
                stats = feedback_store.get_feedback_stats()
                health_status.update({
                    "database_connected": True,
                    "total_feedback": stats.get("total_feedback", 0),
                    "total_qa_pairs": stats.get("total_qa_pairs", 0),
                    "collections": [
                        feedback_store.feedback_collection_name,
                        feedback_store.qa_pairs_collection_name
                    ]
                })
            except Exception as e:
                health_status.update({
                    "database_connected": False,
                    "error": str(e)
                })
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error checking feedback system health: {e}")
        return {
            "feedback_store_available": False,
            "error": str(e)
        }