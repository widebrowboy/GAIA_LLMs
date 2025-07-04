"""
PyMilvus BGE Reranker Service
Cross Encoder 기반 문서 재순위화 서비스
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
import torch
import numpy as np

# PyMilvus BGE Reranker 조건부 임포트
try:
    from pymilvus.model.reranker import BGERerankFunction
    PYMILVUS_RERANKER_AVAILABLE = True
except ImportError:
    PYMILVUS_RERANKER_AVAILABLE = False
    logger.warning("PyMilvus BGE Reranker not available. Using fallback implementation.")

# Transformers 기반 BGE Reranker 임포트
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available for BGE Reranker fallback.")
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


@dataclass
class RerankResult:
    """리랭킹 결과 데이터 클래스"""
    query: str
    documents: List[Dict[str, Any]]
    scores: List[float]
    original_rank: List[int]
    new_rank: List[int]


class RerankerService:
    """
    BGE Cross Encoder Reranker Service
    PyMilvus 내장 reranker 활용
    """
    
    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-v2-m3",
        device: Optional[str] = None,
        use_fp16: bool = True,
        batch_size: int = 16
    ):
        """
        Initialize Reranker Service
        
        Args:
            model_name: BGE reranker 모델 이름
            device: 디바이스 (None이면 자동 감지)
            use_fp16: FP16 사용 여부
            batch_size: 배치 크기
        """
        if device is None:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
        
        self.device = device
        self.batch_size = batch_size
        
        # Reranker 초기화 (PyMilvus 우선, Fallback 지원)
        self.reranker = None
        self.fallback_reranker = None
        
        if PYMILVUS_RERANKER_AVAILABLE:
            try:
                self.reranker = BGERerankFunction(
                    model_name=model_name,
                    device=device,
                    use_fp16=use_fp16 and device.startswith("cuda")
                )
                logger.info("PyMilvus BGE Reranker initialized successfully")
            except Exception as e:
                logger.warning(f"PyMilvus BGE Reranker init failed: {e}")
                
        # Fallback to Transformers-based implementation
        if self.reranker is None and TRANSFORMERS_AVAILABLE:
            try:
                self.fallback_reranker = self._init_transformers_reranker(model_name, device, use_fp16)
                logger.info("Transformers BGE Reranker fallback initialized")
            except Exception as e:
                logger.warning(f"Transformers BGE Reranker fallback failed: {e}")
                
        if self.reranker is None and self.fallback_reranker is None:
            logger.error("No reranker available. Scoring will be disabled.")
        
        # Thread pool for CPU-bound operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info(f"Reranker Service initialized on {device}")
        logger.info(f"Model: {model_name}, FP16: {use_fp16}, Batch: {batch_size}")
    
    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5,
        return_scores: bool = True
    ) -> RerankResult:
        """
        문서 리랭킹 수행
        
        Args:
            query: 검색 쿼리
            documents: 문서 리스트 (text 필드 필수)
            top_k: 상위 k개 문서 반환
            return_scores: 점수 반환 여부
            
        Returns:
            RerankResult: 리랭킹 결과
        """
        if not documents:
            return RerankResult(
                query=query,
                documents=[],
                scores=[],
                original_rank=[],
                new_rank=[]
            )
        
        # 문서 텍스트 추출
        doc_texts = [doc.get("text", "") for doc in documents]
        
        # 배치 처리를 위한 준비
        if len(doc_texts) > self.batch_size:
            # 큰 문서 세트는 배치로 나누어 처리
            reranked_indices = await self._batch_rerank(query, doc_texts, top_k)
        else:
            # 작은 세트는 직접 처리
            reranked_indices = await self._single_rerank(query, doc_texts, top_k)
        
        # 결과 구성
        reranked_docs = []
        scores = []
        original_rank = list(range(len(documents)))
        new_rank = []
        
        for idx in reranked_indices:
            reranked_docs.append(documents[idx])
            new_rank.append(idx)
            
            # 순위 기반 점수 계산 (1위: 1.0, 2위: 0.9, ...)
            if return_scores:
                rank_score = 1.0 - (len(reranked_docs) - 1) * 0.1
                scores.append(max(rank_score, 0.1))
        
        return RerankResult(
            query=query,
            documents=reranked_docs,
            scores=scores if return_scores else [],
            original_rank=original_rank[:len(reranked_docs)],
            new_rank=new_rank
        )
    
    async def _single_rerank(
        self,
        query: str,
        documents: List[str],
        top_k: int
    ) -> List[int]:
        """단일 배치 리랭킹"""
        loop = asyncio.get_event_loop()
        
        # CPU-bound 작업을 별도 스레드에서 실행
        reranked_indices = await loop.run_in_executor(
            self.executor,
            self._rerank_sync,
            query,
            documents,
            top_k
        )
        
        return reranked_indices
    
    def _rerank_sync(
        self,
        query: str,
        documents: List[str],
        top_k: int
    ) -> List[int]:
        """동기식 리랭킹 (스레드에서 실행)"""
        if self.reranker:
            # PyMilvus reranker 호출
            try:
                reranked_indices = self.reranker(
                    query=query,
                    documents=documents,
                    top_k=min(top_k, len(documents))
                )
                return reranked_indices
            except Exception as e:
                logger.warning(f"PyMilvus reranking failed: {e}. Falling back to transformers.")
                
        if self.fallback_reranker:
            # Transformers 기반 리랭킹
            try:
                return self._rerank_with_transformers(query, documents, top_k)
            except Exception as e:
                logger.error(f"Transformers reranking failed: {e}")
        
        # 모든 리랭킹 실패 시 원본 순서 반환
        return list(range(min(top_k, len(documents))))
    
    async def _batch_rerank(
        self,
        query: str,
        documents: List[str],
        top_k: int
    ) -> List[int]:
        """대용량 문서 세트를 위한 배치 리랭킹"""
        all_scores = []
        
        # 배치 단위로 처리
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            batch_indices = await self._single_rerank(query, batch, len(batch))
            
            # 전체 인덱스로 변환
            global_indices = [i + idx for idx in batch_indices]
            all_scores.extend(global_indices)
        
        # 상위 k개만 반환
        return all_scores[:top_k]
    
    async def rerank_multiple(
        self,
        queries: List[str],
        documents_list: List[List[Dict[str, Any]]],
        top_k: int = 5
    ) -> List[RerankResult]:
        """
        여러 쿼리에 대한 동시 리랭킹
        
        Args:
            queries: 쿼리 리스트
            documents_list: 각 쿼리별 문서 리스트
            top_k: 상위 k개 문서
            
        Returns:
            리랭킹 결과 리스트
        """
        tasks = [
            self.rerank(query, docs, top_k)
            for query, docs in zip(queries, documents_list)
        ]
        
        results = await asyncio.gather(*tasks)
        return results
    
    def compare_rankings(
        self,
        original_docs: List[Dict[str, Any]],
        reranked_result: RerankResult
    ) -> Dict[str, Any]:
        """
        원본 순위와 리랭킹 순위 비교
        
        Returns:
            순위 변화 분석 결과
        """
        analysis = {
            "total_documents": len(original_docs),
            "reranked_count": len(reranked_result.documents),
            "rank_changes": []
        }
        
        for i, (orig_idx, new_idx) in enumerate(
            zip(reranked_result.original_rank, reranked_result.new_rank)
        ):
            change = {
                "document_id": original_docs[new_idx].get("id"),
                "original_rank": orig_idx + 1,
                "new_rank": i + 1,
                "rank_change": orig_idx - i,
                "improved": orig_idx > i
            }
            analysis["rank_changes"].append(change)
        
        # 통계
        improvements = sum(1 for c in analysis["rank_changes"] if c["improved"])
        analysis["improvements"] = improvements
        analysis["improvement_rate"] = improvements / len(analysis["rank_changes"])
        
        return analysis
    
    async def evaluate_reranking(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        ground_truth_ids: List[str],
        top_k: int = 5
    ) -> Dict[str, float]:
        """
        리랭킹 성능 평가
        
        Args:
            query: 검색 쿼리
            documents: 문서 리스트
            ground_truth_ids: 정답 문서 ID 리스트
            top_k: 평가할 상위 k개
            
        Returns:
            평가 지표 (precision, recall, mrr 등)
        """
        # 리랭킹 수행
        result = await self.rerank(query, documents, top_k)
        
        # 리랭킹된 문서 ID 추출
        reranked_ids = [doc.get("id") for doc in result.documents]
        
        # Precision@k
        relevant_in_top_k = sum(
            1 for doc_id in reranked_ids[:top_k]
            if doc_id in ground_truth_ids
        )
        precision_at_k = relevant_in_top_k / min(top_k, len(reranked_ids))
        
        # Recall@k
        recall_at_k = relevant_in_top_k / len(ground_truth_ids) if ground_truth_ids else 0
        
        # MRR (Mean Reciprocal Rank)
        mrr = 0.0
        for i, doc_id in enumerate(reranked_ids):
            if doc_id in ground_truth_ids:
                mrr = 1.0 / (i + 1)
                break
        
        # NDCG@k 계산
        dcg = 0.0
        idcg = 0.0
        
        for i in range(min(top_k, len(reranked_ids))):
            rel = 1.0 if reranked_ids[i] in ground_truth_ids else 0.0
            dcg += rel / np.log2(i + 2)
            
            if i < len(ground_truth_ids):
                idcg += 1.0 / np.log2(i + 2)
        
        ndcg_at_k = dcg / idcg if idcg > 0 else 0.0
        
        return {
            "precision@k": precision_at_k,
            "recall@k": recall_at_k,
            "mrr": mrr,
            "ndcg@k": ndcg_at_k,
            "k": top_k,
            "total_retrieved": len(result.documents)
        }
    
    def get_device_info(self) -> Dict[str, Any]:
        """디바이스 정보 반환"""
        info = {
            "device": self.device,
            "cuda_available": torch.cuda.is_available(),
            "batch_size": self.batch_size
        }
        
        if torch.cuda.is_available() and self.device.startswith("cuda"):
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_memory_allocated"] = torch.cuda.memory_allocated() / 1024**3  # GB
            info["gpu_memory_reserved"] = torch.cuda.memory_reserved() / 1024**3   # GB
        
        return info
    
    def _init_transformers_reranker(self, model_name: str, device: str, use_fp16: bool):
        """Transformers 기반 BGE Reranker 초기화"""
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)
        
        if use_fp16 and device.startswith("cuda"):
            model.half()
            
        model.eval()
        
        return {
            "tokenizer": tokenizer,
            "model": model,
            "device": device,
            "max_length": 512
        }
    
    def _rerank_with_transformers(
        self,
        query: str,
        documents: List[str],
        top_k: int
    ) -> List[int]:
        """Transformers 기반 리랭킹"""
        if not self.fallback_reranker:
            return list(range(min(top_k, len(documents))))
            
        tokenizer = self.fallback_reranker["tokenizer"]
        model = self.fallback_reranker["model"]
        device = self.fallback_reranker["device"]
        max_length = self.fallback_reranker["max_length"]
        
        # 쿼리-문서 쌍 생성
        pairs = [[query, doc] for doc in documents]
        
        # 토크나이징
        inputs = tokenizer(
            pairs,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=max_length
        ).to(device)
        
        # 스코어 계산
        with torch.no_grad():
            outputs = model(**inputs)
            scores = torch.sigmoid(outputs.logits.view(-1).float())
            
        # 점수 기준 정렬
        scores_np = scores.cpu().numpy()
        sorted_indices = np.argsort(scores_np)[::-1]
        
        return sorted_indices[:top_k].tolist()