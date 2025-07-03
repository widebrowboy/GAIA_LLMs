"""
피드백 벡터 저장소
사용자의 썸업/썸다운 피드백을 벡터 데이터베이스에 저장하고 관리
"""

import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from app.rag.embeddings import EmbeddingService

logger = logging.getLogger(__name__)


@dataclass
class FeedbackData:
    """피드백 데이터 구조"""
    id: str
    question_text: str
    answer_text: str
    feedback_type: str  # "positive" or "negative"
    question_embedding: List[float]
    answer_embedding: List[float]
    timestamp: str
    session_id: str
    user_id: str
    context_sources: List[str]
    model_version: str
    response_time: float
    confidence_score: float


@dataclass
class QAPairData:
    """질문-응답 쌍 데이터 구조"""
    id: str
    question_text: str
    answer_text: str
    question_embedding: List[float]
    answer_embedding: List[float]
    positive_feedback_count: int
    negative_feedback_count: int
    quality_score: float
    is_training_candidate: bool
    domain_tags: List[str]
    created_at: str
    updated_at: str


class FeedbackVectorStore:
    """피드백 벡터 저장소 클래스"""
    
    def __init__(self, 
                 use_server: bool = False,
                 host: str = "localhost",
                 port: int = 19530,
                 db_file: str = "./feedback_milvus.db"):
        self.use_server = use_server
        self.host = host
        self.port = port
        self.db_file = db_file
        self.embedding_service = EmbeddingService()
        self.embedding_dim = 1024  # mxbai-embed-large 차원 (1024로 통일)
        
        # 컬렉션 이름
        self.feedback_collection_name = "feedback_collection"
        self.qa_pairs_collection_name = "qa_pairs_collection"
        
        self._connect()
        self._create_collections()
    
    def _connect(self):
        """Milvus 연결"""
        try:
            if self.use_server:
                # Milvus 서버 연결
                connections.connect(
                    alias="default",
                    host=self.host,
                    port=self.port
                )
                logger.info(f"Connected to Milvus Server: {self.host}:{self.port}")
                logger.info("🌐 Milvus 웹 UI: http://localhost:9091/webui")
            else:
                # Milvus Lite 연결 (로컬 파일 기반)
                connections.connect(
                    alias="default",
                    uri=self.db_file
                )
                logger.info(f"Connected to Milvus Lite: {self.db_file}")
                logger.info("💡 Milvus 웹 UI를 사용하려면 서버 모드로 전환하세요.")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            if self.use_server:
                logger.error("Milvus 서버가 실행되지 않았을 수 있습니다.")
                logger.error("./scripts/milvus_manager.sh start 명령으로 서버를 시작하세요.")
            raise
    
    def _create_collections(self):
        """피드백 및 QA 쌍 컬렉션 생성"""
        try:
            self._create_feedback_collection()
            self._create_qa_pairs_collection()
        except Exception as e:
            logger.error(f"Failed to create collections: {e}")
            raise
    
    def _create_feedback_collection(self):
        """피드백 컬렉션 생성"""
        # 스키마 정의
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
            FieldSchema(name="question_text", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(name="answer_text", dtype=DataType.VARCHAR, max_length=8192),
            FieldSchema(name="feedback_type", dtype=DataType.VARCHAR, max_length=16),
            FieldSchema(name="question_embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
            FieldSchema(name="answer_embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
            FieldSchema(name="timestamp", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="session_id", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="context_sources", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(name="model_version", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="response_time", dtype=DataType.FLOAT),
            FieldSchema(name="confidence_score", dtype=DataType.FLOAT),
        ]
        
        schema = CollectionSchema(
            fields=fields,
            description="사용자 피드백 저장소"
        )
        
        # 컬렉션 생성 (존재하지 않는 경우)
        if not utility.has_collection(self.feedback_collection_name):
            self.feedback_collection = Collection(
                name=self.feedback_collection_name,
                schema=schema
            )
            
            # 인덱스 생성
            self.feedback_collection.create_index(
                field_name="question_embedding",
                index_params={
                    "metric_type": "IP",  # Inner Product (Cosine similarity)
                    "index_type": "FLAT"
                }
            )
            
            self.feedback_collection.create_index(
                field_name="answer_embedding",
                index_params={
                    "metric_type": "IP",
                    "index_type": "FLAT"
                }
            )
            
            logger.info(f"Created feedback collection: {self.feedback_collection_name}")
        else:
            self.feedback_collection = Collection(self.feedback_collection_name)
            logger.info(f"Loaded existing feedback collection: {self.feedback_collection_name}")
    
    def _create_qa_pairs_collection(self):
        """QA 쌍 컬렉션 생성"""
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
            FieldSchema(name="question_text", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(name="answer_text", dtype=DataType.VARCHAR, max_length=8192),
            FieldSchema(name="question_embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
            FieldSchema(name="answer_embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
            FieldSchema(name="positive_feedback_count", dtype=DataType.INT64),
            FieldSchema(name="negative_feedback_count", dtype=DataType.INT64),
            FieldSchema(name="quality_score", dtype=DataType.FLOAT),
            FieldSchema(name="is_training_candidate", dtype=DataType.BOOL),
            FieldSchema(name="domain_tags", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="updated_at", dtype=DataType.VARCHAR, max_length=32),
        ]
        
        schema = CollectionSchema(
            fields=fields,
            description="질문-응답 쌍 및 품질 데이터"
        )
        
        if not utility.has_collection(self.qa_pairs_collection_name):
            self.qa_pairs_collection = Collection(
                name=self.qa_pairs_collection_name,
                schema=schema
            )
            
            # 인덱스 생성
            self.qa_pairs_collection.create_index(
                field_name="question_embedding",
                index_params={
                    "metric_type": "IP",
                    "index_type": "FLAT"
                }
            )
            
            self.qa_pairs_collection.create_index(
                field_name="answer_embedding",
                index_params={
                    "metric_type": "IP",
                    "index_type": "FLAT"
                }
            )
            
            logger.info(f"Created QA pairs collection: {self.qa_pairs_collection_name}")
        else:
            self.qa_pairs_collection = Collection(self.qa_pairs_collection_name)
            logger.info(f"Loaded existing QA pairs collection: {self.qa_pairs_collection_name}")
    
    def check_duplicate_feedback(self, 
                                question: str, 
                                answer: str, 
                                similarity_threshold: float = 0.95) -> Optional[Dict[str, Any]]:
        """
        유사한 피드백이 이미 존재하는지 확인
        
        Args:
            question: 사용자 질문
            answer: AI 응답
            similarity_threshold: 유사도 임계값 (0.95 이상이면 중복으로 판단)
            
        Returns:
            중복된 피드백 정보 또는 None
        """
        try:
            # 질문 임베딩 생성
            question_embedding = self.embedding_service.embed_text(question)
            answer_embedding = self.embedding_service.embed_text(answer)
            
            # 피드백 컬렉션 로드
            self.feedback_collection.load()
            
            search_params = {
                "metric_type": "IP",
                "params": {"nprobe": 10}
            }
            
            # 질문 기준 유사 피드백 검색
            question_results = self.feedback_collection.search(
                data=[question_embedding],
                anns_field="question_embedding",
                param=search_params,
                limit=5,
                expr=None,
                output_fields=["id", "question_text", "answer_text", "feedback_type", "timestamp"]
            )
            
            # 답변 기준 유사 피드백 검색
            answer_results = self.feedback_collection.search(
                data=[answer_embedding],
                anns_field="answer_embedding",
                param=search_params,
                limit=5,
                expr=None,
                output_fields=["id", "question_text", "answer_text", "feedback_type", "timestamp"]
            )
            
            # 유사도 임계값 이상인 항목 확인
            for results, search_type in [(question_results, "질문"), (answer_results, "답변")]:
                if results and len(results[0]) > 0:
                    for hit in results[0]:
                        if hit.distance >= similarity_threshold:
                            logger.info(f"중복 피드백 발견 ({search_type} 기준): 유사도 {hit.distance:.3f}")
                            return {
                                "duplicate_id": hit.id,
                                "similarity": hit.distance,
                                "search_type": search_type,
                                "existing_question": hit.entity.get("question_text"),
                                "existing_answer": hit.entity.get("answer_text"),
                                "existing_feedback": hit.entity.get("feedback_type"),
                                "existing_timestamp": hit.entity.get("timestamp")
                            }
            
            return None
            
        except Exception as e:
            logger.error(f"중복 검사 실패: {e}")
            return None
    
    def store_feedback(self, 
                      question: str,
                      answer: str,
                      feedback_type: str,
                      session_id: str = None,
                      user_id: str = None,
                      context_sources: List[str] = None,
                      model_version: str = "gemma3-12b",
                      response_time: float = 0.0,
                      confidence_score: float = 0.0,
                      check_duplicates: bool = True,
                      similarity_threshold: float = 0.95) -> Dict[str, Any]:
        """
        피드백 데이터 저장
        
        Args:
            question: 사용자 질문
            answer: AI 응답
            feedback_type: "positive" or "negative"
            session_id: 세션 ID
            user_id: 사용자 ID
            context_sources: RAG 컨텍스트 소스들
            model_version: 모델 버전
            response_time: 응답 생성 시간
            confidence_score: 모델 자신감 점수
            check_duplicates: 중복 검사 여부
            similarity_threshold: 유사도 임계값
            
        Returns:
            저장 결과 정보 (Dict)
        """
        try:
            # 중복 검사 수행
            if check_duplicates:
                duplicate_info = self.check_duplicate_feedback(
                    question, answer, similarity_threshold
                )
                if duplicate_info:
                    logger.info(f"중복 피드백으로 인해 저장 건너뜀: {duplicate_info['duplicate_id']}")
                    return {
                        "status": "duplicate",
                        "message": f"유사한 피드백이 이미 존재합니다 (유사도: {duplicate_info['similarity']:.3f})",
                        "duplicate_info": duplicate_info,
                        "feedback_id": None
                    }
            
            # 임베딩 생성
            question_embedding = self.embedding_service.embed_text(question)
            answer_embedding = self.embedding_service.embed_text(answer)
            
            # 피드백 데이터 생성
            feedback_id = str(uuid.uuid4())
            feedback_data = FeedbackData(
                id=feedback_id,
                question_text=question,
                answer_text=answer,
                feedback_type=feedback_type,
                question_embedding=question_embedding,
                answer_embedding=answer_embedding,
                timestamp=datetime.now().isoformat(),
                session_id=session_id or str(uuid.uuid4()),
                user_id=user_id or "anonymous",
                context_sources=context_sources or [],
                model_version=model_version,
                response_time=response_time,
                confidence_score=confidence_score
            )
            
            # Milvus 형식으로 변환
            entities = [
                [feedback_data.id],
                [feedback_data.question_text],
                [feedback_data.answer_text],
                [feedback_data.feedback_type],
                [feedback_data.question_embedding],
                [feedback_data.answer_embedding],
                [feedback_data.timestamp],
                [feedback_data.session_id],
                [feedback_data.user_id],
                [str(feedback_data.context_sources)],  # JSON 문자열로 저장
                [feedback_data.model_version],
                [feedback_data.response_time],
                [feedback_data.confidence_score]
            ]
            
            # 데이터 삽입
            self.feedback_collection.insert(entities)
            self.feedback_collection.flush()
            
            # QA 쌍 데이터 업데이트
            self._update_qa_pair(question, answer, feedback_type, question_embedding, answer_embedding)
            
            logger.info(f"Stored feedback: {feedback_id} ({feedback_type})")
            return {
                "status": "success",
                "message": "피드백이 성공적으로 저장되었습니다.",
                "feedback_id": feedback_id,
                "duplicate_info": None
            }
            
        except Exception as e:
            logger.error(f"Failed to store feedback: {e}")
            return {
                "status": "error",
                "message": f"피드백 저장 실패: {str(e)}",
                "feedback_id": None,
                "duplicate_info": None
            }
    
    def _update_qa_pair(self, 
                       question: str, 
                       answer: str, 
                       feedback_type: str,
                       question_embedding: List[float],
                       answer_embedding: List[float]):
        """QA 쌍 데이터 업데이트"""
        try:
            # 기존 QA 쌍 검색 (질문 기준 유사성)
            self.qa_pairs_collection.load()
            
            search_params = {
                "metric_type": "IP",
                "params": {"nprobe": 10}
            }
            
            results = self.qa_pairs_collection.search(
                data=[question_embedding],
                anns_field="question_embedding",
                param=search_params,
                limit=1,
                expr=None,
                output_fields=["id", "positive_feedback_count", "negative_feedback_count", "quality_score"]
            )
            
            if results and len(results[0]) > 0 and results[0][0].distance > 0.95:  # 높은 유사성
                # 기존 QA 쌍 업데이트
                existing_qa = results[0][0]
                qa_id = existing_qa.entity.get("id")
                
                positive_count = existing_qa.entity.get("positive_feedback_count", 0)
                negative_count = existing_qa.entity.get("negative_feedback_count", 0)
                
                if feedback_type == "positive":
                    positive_count += 1
                else:
                    negative_count += 1
                
                # 품질 점수 재계산
                total_feedback = positive_count + negative_count
                positive_ratio = positive_count / total_feedback if total_feedback > 0 else 0
                quality_score = self._calculate_quality_score(positive_ratio)
                
                # TODO: 실제로는 UPDATE 쿼리 필요 (현재 Milvus Lite는 제한적)
                logger.info(f"Would update QA pair {qa_id}: +{positive_count}, -{negative_count}, quality: {quality_score}")
                
            else:
                # 새로운 QA 쌍 생성
                qa_id = str(uuid.uuid4())
                positive_count = 1 if feedback_type == "positive" else 0
                negative_count = 1 if feedback_type == "negative" else 0
                quality_score = self._calculate_quality_score(positive_count / (positive_count + negative_count))
                
                qa_data = QAPairData(
                    id=qa_id,
                    question_text=question,
                    answer_text=answer,
                    question_embedding=question_embedding,
                    answer_embedding=answer_embedding,
                    positive_feedback_count=positive_count,
                    negative_feedback_count=negative_count,
                    quality_score=quality_score,
                    is_training_candidate=quality_score >= 0.8,
                    domain_tags=self._extract_domain_tags(question + " " + answer),
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                
                # QA 쌍 삽입
                entities = [
                    [qa_data.id],
                    [qa_data.question_text],
                    [qa_data.answer_text],
                    [qa_data.question_embedding],
                    [qa_data.answer_embedding],
                    [qa_data.positive_feedback_count],
                    [qa_data.negative_feedback_count],
                    [qa_data.quality_score],
                    [qa_data.is_training_candidate],
                    [str(qa_data.domain_tags)],
                    [qa_data.created_at],
                    [qa_data.updated_at]
                ]
                
                self.qa_pairs_collection.insert(entities)
                self.qa_pairs_collection.flush()
                
                logger.info(f"Created new QA pair: {qa_id} (quality: {quality_score})")
                
        except Exception as e:
            logger.error(f"Failed to update QA pair: {e}")
    
    def _calculate_quality_score(self, positive_ratio: float) -> float:
        """품질 점수 계산"""
        # 간단한 버전: 긍정 피드백 비율 기반
        # 추후 더 복잡한 알고리즘으로 확장 가능
        return positive_ratio
    
    def _extract_domain_tags(self, text: str) -> List[str]:
        """도메인 태그 추출 (간단한 키워드 기반)"""
        domain_keywords = {
            "oncology": ["cancer", "tumor", "oncology", "EGFR", "chemotherapy", "radiation"],
            "cardiology": ["heart", "cardiac", "cardiovascular", "hypertension"],
            "neurology": ["brain", "neurological", "alzheimer", "parkinson"],
            "clinical_trial": ["trial", "study", "phase", "clinical", "randomized"],
            "drug_development": ["drug", "compound", "molecule", "pharmaceutical", "therapy"]
        }
        
        tags = []
        text_lower = text.lower()
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(domain)
        
        return tags[:5]  # 최대 5개 태그
    
    def search_similar_feedback(self, 
                               question: str, 
                               feedback_type: str = None,
                               limit: int = 10) -> List[Dict[str, Any]]:
        """유사한 피드백 검색"""
        try:
            question_embedding = self.embedding_service.embed_text(question)
            
            self.feedback_collection.load()
            
            search_params = {
                "metric_type": "IP",
                "params": {"nprobe": 10}
            }
            
            # 피드백 타입 필터
            expr = f'feedback_type == "{feedback_type}"' if feedback_type else None
            
            results = self.feedback_collection.search(
                data=[question_embedding],
                anns_field="question_embedding",
                param=search_params,
                limit=limit,
                expr=expr,
                output_fields=["question_text", "answer_text", "feedback_type", "timestamp", "quality_score"]
            )
            
            similar_feedback = []
            if results and len(results[0]) > 0:
                for hit in results[0]:
                    similar_feedback.append({
                        "question": hit.entity.get("question_text"),
                        "answer": hit.entity.get("answer_text"),
                        "feedback_type": hit.entity.get("feedback_type"),
                        "timestamp": hit.entity.get("timestamp"),
                        "similarity": hit.distance,
                        "id": hit.id
                    })
            
            return similar_feedback
            
        except Exception as e:
            logger.error(f"Failed to search similar feedback: {e}")
            return []
    
    def get_training_candidates(self, 
                               min_quality_score: float = 0.8,
                               limit: int = 1000) -> List[Dict[str, Any]]:
        """파인튜닝 후보 데이터 조회"""
        try:
            self.qa_pairs_collection.load()
            
            # 높은 품질 점수의 QA 쌍 검색
            expr = f"quality_score >= {min_quality_score} && is_training_candidate == true"
            
            results = self.qa_pairs_collection.query(
                expr=expr,
                output_fields=["question_text", "answer_text", "quality_score", "positive_feedback_count", "domain_tags"],
                limit=limit
            )
            
            training_data = []
            for result in results:
                training_data.append({
                    "instruction": "신약개발 전문 AI로서 다음 질문에 답변하세요.",
                    "input": result["question_text"],
                    "output": result["answer_text"],
                    "quality_score": result["quality_score"],
                    "feedback_count": result["positive_feedback_count"],
                    "domain": result["domain_tags"]
                })
            
            return training_data
            
        except Exception as e:
            logger.error(f"Failed to get training candidates: {e}")
            return []
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """피드백 통계 조회"""
        try:
            self.feedback_collection.load()
            self.qa_pairs_collection.load()
            
            # 전체 피드백 수
            total_feedback = self.feedback_collection.num_entities
            
            # 긍정/부정 피드백 수 (실제로는 더 정교한 쿼리 필요)
            positive_results = self.feedback_collection.query(
                expr='feedback_type == "positive"',
                output_fields=["id"],
                limit=10000
            )
            
            negative_results = self.feedback_collection.query(
                expr='feedback_type == "negative"',
                output_fields=["id"],
                limit=10000
            )
            
            positive_count = len(positive_results)
            negative_count = len(negative_results)
            
            # QA 쌍 수
            total_qa_pairs = self.qa_pairs_collection.num_entities
            
            # 파인튜닝 후보 수
            training_candidates = self.qa_pairs_collection.query(
                expr="is_training_candidate == true",
                output_fields=["id"],
                limit=10000
            )
            
            return {
                "total_feedback": total_feedback,
                "positive_feedback": positive_count,
                "negative_feedback": negative_count,
                "positive_ratio": positive_count / total_feedback if total_feedback > 0 else 0,
                "total_qa_pairs": total_qa_pairs,
                "training_candidates": len(training_candidates),
                "collections": {
                    "feedback_collection": self.feedback_collection_name,
                    "qa_pairs_collection": self.qa_pairs_collection_name
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get feedback stats: {e}")
            return {"error": str(e)}