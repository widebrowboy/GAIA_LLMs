"""
Reasoning RAG Pipeline with PyMilvus Reranker Integration
Self-RAG, CoT-RAG, MCTS-RAG 통합 추론 파이프라인
"""

import asyncio
import json
import math
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

from pymilvus import MilvusClient
import torch
import ollama

from app.rag.embeddings import EmbeddingService
from app.api.ollama_client import OllamaClient
from app.rag.vector_store_lite import MilvusLiteVectorStore
from app.rag.reasoning_agents import (
    RetrievalDecisionAgent,
    QueryRefinementAgent,
    RelevanceEvaluationAgent,
    AnswerGenerationAgent,
    SupportEvaluationAgent,
    ContinuationDecisionAgent
)
from app.rag.reasoning_prompts import ReasoningPrompts

# BGE Reranker 임시 대체 (FlagEmbedding 의존성 해결 후 교체)
try:
    from pymilvus.model.reranker import BGERerankFunction
    RERANKER_AVAILABLE = True
except ImportError:
    RERANKER_AVAILABLE = False
    logger.warning("PyMilvus BGE Reranker not available. Using fallback reranking.")

logger = logging.getLogger(__name__)


@dataclass
class ReasoningStep:
    """추론 단계 데이터 클래스"""
    iteration: int
    query: str
    refined_query: Optional[str]
    documents: List[Dict[str, Any]]
    relevance_scores: List[float]
    partial_answer: str
    support_score: float
    should_continue: bool
    timestamp: datetime


@dataclass
class ReasoningResult:
    """추론 결과 데이터 클래스"""
    query: str
    mode: str
    final_answer: str
    reasoning_steps: List[ReasoningStep]
    total_iterations: int
    confidence_score: float
    sources: List[Dict[str, Any]]
    elapsed_time: float


class MCTSNode:
    """MCTS 트리 노드"""
    
    def __init__(
        self,
        query: str,
        depth: int,
        accumulated_context: str = "",
        refined_query: Optional[str] = None,
        parent: Optional['MCTSNode'] = None
    ):
        self.query = query
        self.refined_query = refined_query
        self.depth = depth
        self.accumulated_context = accumulated_context
        self.parent = parent
        self.children: List['MCTSNode'] = []
        
        # MCTS 통계
        self.visit_count = 0
        self.total_reward = 0.0
        self.is_terminal = False
        self.is_expanded = False
        
    def average_reward(self) -> float:
        """평균 보상 계산"""
        if self.visit_count == 0:
            return 0.0
        return self.total_reward / self.visit_count
    
    def ucb1_value(self, exploration_constant: float = 1.4) -> float:
        """UCB1 값 계산"""
        if self.visit_count == 0:
            return float('inf')
        
        if self.parent is None or self.parent.visit_count == 0:
            return self.average_reward()
        
        exploitation = self.average_reward()
        exploration = exploration_constant * math.sqrt(
            math.log(self.parent.visit_count) / self.visit_count
        )
        
        return exploitation + exploration
    
    def best_child_value(self) -> float:
        """최고 자식의 평균 보상"""
        if not self.children:
            return self.average_reward()
        
        return max(child.average_reward() for child in self.children)
    
    def add_child(self, child: 'MCTSNode') -> 'MCTSNode':
        """자식 노드 추가"""
        child.parent = self
        self.children.append(child)
        return child
    
    def update(self, reward: float):
        """노드 업데이트"""
        self.visit_count += 1
        self.total_reward += reward


class ReasoningRAGPipeline:
    """
    Reasoning RAG Pipeline with 2-stage retrieval:
    1. Milvus vector search (k=20)
    2. BGE Cross Encoder reranking (k=5)
    """
    
    def __init__(
        self,
        milvus_uri: str = "tcp://localhost:19530",
        collection_name: str = "documents",
        embedding_model: str = "mxbai-embed-large",
        llm_model: str = "gemma3-12b",
        reranker_model: str = "BAAI/bge-reranker-v2-m3"
    ):
        """
        Initialize Reasoning RAG Pipeline
        
        Args:
            milvus_uri: Milvus 서버 URI
            collection_name: 컬렉션 이름
            embedding_model: 임베딩 모델 이름
            llm_model: LLM 모델 이름
            reranker_model: Reranker 모델 이름
        """
        # Milvus 클라이언트
        self.milvus_client = MilvusClient(uri=milvus_uri)
        self.collection_name = collection_name
        
        # 임베딩 서비스
        self.embedder = EmbeddingService(model_name=embedding_model)
        
        # BGE Reranker 초기화
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.device = device
        self.reranker_model_name = reranker_model
        
        if RERANKER_AVAILABLE:
            try:
                self.reranker = BGERerankFunction(
                    model_name=reranker_model,
                    device=device,
                    use_fp16=True if device == "cuda:0" else False
                )
                logger.info(f"BGE Reranker loaded on {device}")
            except Exception as e:
                logger.warning(f"BGE Reranker init failed: {e}. Using fallback.")
                self.reranker = None
        else:
            self.reranker = None
        
        # LLM
        self.llm = OllamaClient(model=llm_model)
        
        # 추론 에이전트 초기화
        self.retrieval_agent = RetrievalDecisionAgent(llm_model)
        self.query_agent = QueryRefinementAgent(llm_model)
        self.relevance_agent = RelevanceEvaluationAgent(llm_model)
        self.answer_agent = AnswerGenerationAgent(llm_model)
        self.support_agent = SupportEvaluationAgent(llm_model)
        self.continuation_agent = ContinuationDecisionAgent(llm_model)
        
        # 프롬프트 매니저
        self.prompts = ReasoningPrompts()
        
        # 설정
        self.search_top_k = 20  # 1단계 검색
        self.rerank_top_k = 5   # 2단계 리랭킹
        self.max_iterations = 3  # Self-RAG 최대 반복
        
        logger.info(f"Reasoning RAG Pipeline initialized with {device}")
        logger.info("Reasoning agents loaded: Retrieval, Query, Relevance, Answer, Support, Continuation")
    
    async def reasoning_search(
        self,
        query: str,
        mode: str = "self_rag",
        stream_callback: Optional[callable] = None
    ) -> ReasoningResult:
        """
        다단계 추론 검색 실행
        
        Args:
            query: 사용자 질문
            mode: 추론 모드 (self_rag, cot_rag, mcts_rag)
            stream_callback: 스트리밍 콜백 함수
            
        Returns:
            ReasoningResult: 추론 결과
        """
        start_time = datetime.now()
        
        if mode == "self_rag":
            result = await self._self_rag_pipeline(query, stream_callback)
        elif mode == "cot_rag":
            result = await self._cot_rag_pipeline(query, stream_callback)
        elif mode == "mcts_rag":
            result = await self._mcts_rag_pipeline(query, stream_callback)
        else:
            raise ValueError(f"Unknown reasoning mode: {mode}")
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        result.elapsed_time = elapsed_time
        
        return result
    
    async def _search_and_rerank(
        self,
        query: str,
        context: Optional[List[str]] = None
    ) -> Tuple[List[Dict[str, Any]], List[float]]:
        """
        2단계 검색 및 리랭킹
        
        Args:
            query: 검색 쿼리
            context: 이전 컨텍스트
            
        Returns:
            문서 리스트와 관련성 점수
        """
        # 1단계: 벡터 검색 (rule_2.md 방식)
        query_embedding = self._embed_with_ollama(query, dim=1024)  # 기존 컬렉션 차원 맞춤
        
        search_params = {
            "metric_type": "IP",
            "params": {"ef": 150}
        }
        
        results = self.milvus_client.search(
            collection_name=self.collection_name,
            data=[query_embedding],
            anns_field="vector",
            search_params=search_params,
            limit=self.search_top_k,
            output_fields=["text", "metadata"]
        )
        
        if not results or not results[0]:
            return [], []
        
        # 검색 결과 추출
        documents = []
        for hit in results[0]:
            doc = {
                "id": hit.id,
                "text": hit.entity.get("text", ""),
                "metadata": hit.entity.get("metadata", {}),
                "score": hit.score
            }
            documents.append(doc)
        
        # 2단계: BGE Reranking
        doc_texts = [doc["text"] for doc in documents]
        
        if self.reranker and len(doc_texts) > 0:
            try:
                # PyMilvus BGE reranker 호출
                reranked_results = self.reranker(
                    query,
                    doc_texts,
                    top_k=min(self.rerank_top_k, len(doc_texts))
                )
                
                # 리랭킹된 문서와 점수
                reranked_docs = []
                relevance_scores = []
                
                # reranked_results는 순서대로 정렬된 문서 텍스트 리스트
                for i, reranked_text in enumerate(reranked_results):
                    # 원본 문서에서 매칭되는 문서 찾기
                    for doc in documents:
                        if doc["text"] == reranked_text:
                            reranked_docs.append(doc)
                            # 순위 기반 점수 생성 (1.0에서 시작해서 0.1씩 감소)
                            relevance_scores.append(1.0 - i * 0.15)
                            break
                            
            except Exception as e:
                logger.warning(f"BGE reranking failed: {e}. Using vector search results.")
                reranked_docs = documents[:self.rerank_top_k]
                relevance_scores = [1.0 - i * 0.1 for i in range(len(reranked_docs))]
        else:
            # Fallback: 벡터 검색 결과만 사용
            reranked_docs = documents[:self.rerank_top_k]
            relevance_scores = [1.0 - i * 0.1 for i in range(len(reranked_docs))]
        
        return reranked_docs, relevance_scores
    
    def _embed_with_ollama(self, text: str, dim: int = 512) -> List[float]:
        """
        rule_2.md 방식: ollama 라이브러리로 직접 임베딩
        
        Args:
            text: 임베딩할 텍스트
            dim: 임베딩 차원 (mxbai-embed-large는 512 권장)
            
        Returns:
            임베딩 벡터
        """
        try:
            response = ollama.embeddings(
                model=self.embedder.model_name,
                prompt=text,
                options={"dimensions": dim}
            )
            
            # 응답 타입에 따른 처리
            if hasattr(response, 'embedding'):
                # ollama._types.EmbeddingsResponse 객체
                return response.embedding
            elif isinstance(response, dict) and "embedding" in response:
                # 딕셔너리 형태 응답
                return response["embedding"]
            else:
                logger.warning(f"Unexpected ollama response type: {type(response)}")
                logger.debug(f"Response content: {response}")
                raise ValueError(f"Invalid ollama response format: {type(response)}")
        except Exception as e:
            logger.error(f"Ollama embedding failed: {e}")
            # Fallback to existing service
            fallback = self.embedder.embed_text(text)
            return fallback if fallback else [0.0] * dim
    
    async def _self_rag_pipeline(
        self,
        query: str,
        stream_callback: Optional[callable] = None
    ) -> ReasoningResult:
        """
        Self-RAG 추론 파이프라인
        반성 토큰: [Retrieve], [Relevant], [Support], [Continue]
        """
        reasoning_steps = []
        all_sources = []
        
        for iteration in range(self.max_iterations):
            step_start = datetime.now()
            
            # 스트리밍 알림
            if stream_callback:
                await stream_callback({
                    "type": "iteration_start",
                    "iteration": iteration + 1,
                    "max_iterations": self.max_iterations
                })
            
            # 1. 검색 필요성 판단 [Retrieve] - 에이전트 활용
            should_retrieve, retrieve_reason = await self.retrieval_agent.reason(
                query=query,
                history=[step.__dict__ for step in reasoning_steps],
                threshold=0.7
            )
            
            if not should_retrieve and iteration > 0:
                if stream_callback:
                    await stream_callback({
                        "type": "skip_retrieval",
                        "reason": retrieve_reason
                    })
                break
            
            # 2. 쿼리 개선 - 에이전트 활용
            refined_query = await self.query_agent.reason(
                original_query=query,
                history=[step.__dict__ for step in reasoning_steps],
                focus=None
            )
            
            if stream_callback:
                await stream_callback({
                    "type": "query_refined",
                    "original": query,
                    "refined": refined_query
                })
            
            # 3. 검색 및 리랭킹
            documents, relevance_scores = await self._search_and_rerank(refined_query)
            
            if stream_callback:
                await stream_callback({
                    "type": "documents_retrieved",
                    "count": len(documents),
                    "top_score": relevance_scores[0] if relevance_scores else 0
                })
            
            # 4. 관련성 평가 [Relevant] - 에이전트 활용
            relevance_eval, individual_scores = await self.relevance_agent.reason(
                query=query,
                documents=documents,
                top_k=3
            )
            
            # 5. 부분 답변 생성 - 에이전트 활용
            partial_answer = await self.answer_agent.reason(
                query=query,
                documents=documents,
                history=[step.__dict__ for step in reasoning_steps],
                mode="partial"
            )
            
            if stream_callback:
                await stream_callback({
                    "type": "partial_answer",
                    "answer": partial_answer
                })
            
            # 6. 지지도 평가 [Support] - 에이전트 활용
            support_score, support_details = await self.support_agent.reason(
                answer=partial_answer,
                documents=documents,
                check_factual=True
            )
            
            # 7. 계속 여부 결정 [Continue] - 에이전트 활용
            should_continue, continue_reason = await self.continuation_agent.reason(
                iteration=iteration,
                support_score=support_score,
                history=[step.__dict__ for step in reasoning_steps],
                max_iterations=self.max_iterations
            )
            
            # 추론 단계 저장
            step = ReasoningStep(
                iteration=iteration,
                query=query,
                refined_query=refined_query,
                documents=documents,
                relevance_scores=individual_scores,  # 에이전트에서 반환된 개별 점수 사용
                partial_answer=partial_answer,
                support_score=support_score,
                should_continue=should_continue,
                timestamp=step_start
            )
            reasoning_steps.append(step)
            all_sources.extend(documents[:3])  # 상위 3개 소스 저장
            
            if not should_continue:
                break
        
        # 최종 답변 합성 - 에이전트 활용
        final_answer = await self.answer_agent.reason(
            query=query,
            documents=all_sources,
            history=[step.__dict__ for step in reasoning_steps],
            mode="final"
        )
        
        # 신뢰도 점수 계산
        confidence_score = self._calculate_confidence(reasoning_steps)
        
        return ReasoningResult(
            query=query,
            mode="self_rag",
            final_answer=final_answer,
            reasoning_steps=reasoning_steps,
            total_iterations=len(reasoning_steps),
            confidence_score=confidence_score,
            sources=all_sources,
            elapsed_time=0  # 나중에 설정됨
        )
    
    async def _should_retrieve(
        self,
        query: str,
        history: List[ReasoningStep]
    ) -> bool:
        """
        검색 필요성 판단 [Retrieve] 토큰
        rule_2.md 설계: LLM 기반 검색 필요성 평가
        """
        if not history:
            return True
        
        # 최근 단계들의 성능 평가
        recent_steps = history[-2:] if len(history) >= 2 else history
        avg_support = sum(step.support_score for step in recent_steps) / len(recent_steps)
        avg_relevance = sum(
            sum(step.relevance_scores) / len(step.relevance_scores) if step.relevance_scores else 0.5
            for step in recent_steps
        ) / len(recent_steps)
        
        # LLM 기반 검색 필요성 판단
        context_info = "\n".join([
            f"Step {step.iteration}: Support={step.support_score:.2f}, Answer={step.partial_answer[:100]}..."
            for step in recent_steps
        ])
        
        prompt = f"""Based on the search history, determine if additional retrieval is needed.

Query: {query}
Recent search context:
{context_info}

Current performance:
- Average support score: {avg_support:.2f}
- Average relevance: {avg_relevance:.2f}

Should retrieve more information? Consider:
1. Is the current answer well-supported? (support > 0.8)
2. Are there gaps in information?
3. Could additional sources improve the answer?

Answer with only 'YES' or 'NO':"""

        response = await self.llm.generate(prompt)
        should_retrieve = "YES" in response.upper()
        
        logger.debug(f"[Retrieve] Support={avg_support:.2f}, Relevance={avg_relevance:.2f} -> {should_retrieve}")
        return should_retrieve
    
    async def _refine_query(
        self,
        query: str,
        history: List[ReasoningStep]
    ) -> str:
        """컨텍스트 기반 쿼리 개선"""
        if not history:
            return query
        
        # 이전 부분 답변을 고려한 쿼리 개선
        context = "\n".join([step.partial_answer for step in history[-2:]])
        
        prompt = f"""Given the original question and previous context, 
        refine the search query to find missing information.
        
        Original question: {query}
        Previous context: {context}
        
        Refined query:"""
        
        response = await self.llm.generate(prompt)
        return response.strip()
    
    async def _evaluate_relevance(
        self,
        query: str,
        documents: List[Dict[str, Any]]
    ) -> float:
        """
        문서 관련성 평가 [Relevant] 토큰
        rule_2.md 설계: 개별 문서 및 전체 관련성 평가
        """
        if not documents:
            return 0.0
        
        # 각 문서별 관련성 평가
        individual_scores = []
        for i, doc in enumerate(documents[:5]):  # 상위 5개 문서 평가
            doc_prompt = f"""Rate the relevance of this document to the query on a scale of 0-1.

Query: {query}
Document {i+1}: {doc["text"][:300]}...

Consider:
1. Does the document directly address the query?
2. Is the information accurate and specific?
3. How well does it match the query intent?

Relevance score (0.0-1.0):"""
            
            try:
                response = await self.llm.generate(doc_prompt)
                score = float(response.strip())
                individual_scores.append(min(max(score, 0.0), 1.0))
            except:
                individual_scores.append(0.5)
        
        # 전체 관련성 평가 (가중 평균 - 상위 문서에 더 큰 가중치)
        if individual_scores:
            weights = [0.5 ** i for i in range(len(individual_scores))]
            total_weight = sum(weights)
            weighted_score = sum(score * weight for score, weight in zip(individual_scores, weights))
            final_score = weighted_score / total_weight
        else:
            final_score = 0.0
            
        logger.debug(f"[Relevant] Individual scores: {individual_scores}, Final: {final_score:.3f}")
        return final_score
    
    async def _generate_partial_answer(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        history: List[ReasoningStep]
    ) -> str:
        """부분 답변 생성"""
        context = "\n\n".join([doc["text"] for doc in documents[:3]])
        
        previous_answers = ""
        if history:
            previous_answers = "\n".join([
                f"Iteration {step.iteration + 1}: {step.partial_answer}"
                for step in history[-2:]
            ])
        
        prompt = f"""Based on the retrieved documents, provide a partial answer to the question.
        Build upon previous iterations if available.
        
        Question: {query}
        
        Retrieved Context:
        {context}
        
        Previous Answers:
        {previous_answers}
        
        Partial Answer:"""
        
        response = await self.llm.generate(prompt)
        return response.strip()
    
    async def _evaluate_support(
        self,
        answer: str,
        documents: List[Dict[str, Any]]
    ) -> float:
        """
        답변 지지도 평가 [Support] 토큰
        rule_2.md 설계: 세분화된 지지도 평가
        """
        if not documents or not answer:
            return 0.0
        
        # 문서별 지지도 평가
        support_scores = []
        for i, doc in enumerate(documents[:3]):
            support_prompt = f"""Evaluate how well this specific document supports the given answer.

Answer: {answer}
Document {i+1}: {doc["text"][:400]}

Evaluation criteria:
1. Factual accuracy: Does the document contain facts that confirm the answer?
2. Coverage: How much of the answer is covered by this document?
3. Consistency: Is there any contradiction between document and answer?
4. Specificity: Does the document provide specific details mentioned in the answer?

Support score (0.0-1.0):"""
            
            try:
                response = await self.llm.generate(support_prompt)
                score = float(response.strip())
                support_scores.append(min(max(score, 0.0), 1.0))
            except:
                support_scores.append(0.3)
        
        # 전체 지지도 계산 (최고 점수에 가중치 부여)
        if support_scores:
            # 최고 점수와 평균 점수의 가중 조합
            max_support = max(support_scores)
            avg_support = sum(support_scores) / len(support_scores)
            final_support = 0.7 * max_support + 0.3 * avg_support
        else:
            final_support = 0.0
        
        # 추가 일관성 검사
        consistency_prompt = f"""Check if the answer is internally consistent and well-supported overall.

Answer: {answer}
Available evidence: {len(documents)} documents

Rate overall consistency and evidence strength (0.0-1.0):"""
        
        try:
            consistency_response = await self.llm.generate(consistency_prompt)
            consistency_score = float(consistency_response.strip())
            consistency_score = min(max(consistency_score, 0.0), 1.0)
            
            # 최종 지지도: 문서 지지도 + 일관성 점수
            final_support = 0.8 * final_support + 0.2 * consistency_score
        except:
            pass
            
        logger.debug(f"[Support] Doc scores: {support_scores}, Final: {final_support:.3f}")
        return final_support
    
    async def _should_continue(
        self,
        iteration: int,
        support_score: float,
        history: List[ReasoningStep]
    ) -> bool:
        """계속 여부 결정 [Continue] 토큰"""
        # 최대 반복 도달
        if iteration >= self.max_iterations - 1:
            return False
        
        # 충분한 지지도
        if support_score >= 0.85:
            return False
        
        # 개선이 없는 경우
        if len(history) >= 2:
            recent_scores = [step.support_score for step in history[-2:]]
            if all(s >= 0.7 for s in recent_scores) and abs(recent_scores[0] - recent_scores[1]) < 0.1:
                return False
        
        return True
    
    async def _synthesize_final_answer(
        self,
        query: str,
        steps: List[ReasoningStep]
    ) -> str:
        """최종 답변 합성"""
        # 모든 부분 답변 수집
        partial_answers = [step.partial_answer for step in steps]
        
        # 가장 신뢰도 높은 소스들
        all_sources = []
        for step in steps:
            all_sources.extend(step.documents[:2])
        
        context = "\n\n".join([doc["text"][:500] for doc in all_sources[:5]])
        
        prompt = f"""Synthesize a comprehensive final answer based on the iterative reasoning process.
        Combine insights from all iterations into a coherent response.
        
        Question: {query}
        
        Reasoning Steps:
        {chr(10).join([f"Step {i+1}: {ans}" for i, ans in enumerate(partial_answers)])}
        
        Key Sources:
        {context}
        
        Final Comprehensive Answer:"""
        
        response = await self.llm.generate(prompt)
        return response.strip()
    
    def _calculate_confidence(self, steps: List[ReasoningStep]) -> float:
        """전체 신뢰도 점수 계산"""
        if not steps:
            return 0.0
        
        # 지지도 점수의 가중 평균 (최근 단계에 더 큰 가중치)
        weights = [0.5 ** i for i in range(len(steps)-1, -1, -1)]
        total_weight = sum(weights)
        
        weighted_score = sum(
            step.support_score * weight
            for step, weight in zip(steps, weights)
        )
        
        return weighted_score / total_weight
    
    async def _cot_rag_pipeline(
        self,
        query: str,
        stream_callback: Optional[callable] = None
    ) -> ReasoningResult:
        """
        Chain-of-Thought RAG 파이프라인
        복잡한 질문을 단계별로 분해하여 순차적으로 추론
        """
        start_time = datetime.now()
        reasoning_steps = []
        all_sources = []
        
        # Step 1: 질문 분해 (Question Decomposition)
        if stream_callback:
            await stream_callback({
                "type": "cot_start",
                "message": "질문을 하위 문제로 분해 중..."
            })
        
        sub_questions = await self._decompose_question(query)
        
        if stream_callback:
            await stream_callback({
                "type": "question_decomposition",
                "sub_questions": sub_questions,
                "count": len(sub_questions)
            })
        
        # Step 2: 각 하위 질문에 대한 순차적 추론
        accumulated_context = ""
        
        for i, sub_query in enumerate(sub_questions):
            step_start = datetime.now()
            
            if stream_callback:
                await stream_callback({
                    "type": "sub_question_start",
                    "step": i + 1,
                    "total_steps": len(sub_questions),
                    "sub_question": sub_query
                })
            
            # 이전 컨텍스트를 고려한 검색
            context_enhanced_query = await self._enhance_query_with_context(
                sub_query, accumulated_context
            )
            
            # 검색 및 리랭킹
            documents, relevance_scores = await self._search_and_rerank(context_enhanced_query)
            
            # 관련성 평가
            relevance_eval, individual_scores = await self.relevance_agent.reason(
                query=sub_query,
                documents=documents,
                top_k=3
            )
            
            # 부분 답변 생성 (이전 컨텍스트 포함)
            partial_answer = await self._generate_cot_step_answer(
                sub_query, documents, accumulated_context, i + 1
            )
            
            # 지지도 평가
            support_score, support_details = await self.support_agent.reason(
                answer=partial_answer,
                documents=documents,
                check_factual=True
            )
            
            # 추론 단계 저장
            step = ReasoningStep(
                iteration=i,
                query=sub_query,
                refined_query=context_enhanced_query,
                documents=documents,
                relevance_scores=individual_scores,
                partial_answer=partial_answer,
                support_score=support_score,
                should_continue=i < len(sub_questions) - 1,
                timestamp=step_start
            )
            reasoning_steps.append(step)
            all_sources.extend(documents[:2])  # 상위 2개 소스 저장
            
            # 컨텍스트 누적
            accumulated_context += f"\n\n단계 {i + 1}: {sub_query}\n답변: {partial_answer}"
            
            if stream_callback:
                await stream_callback({
                    "type": "sub_question_completed",
                    "step": i + 1,
                    "partial_answer": partial_answer,
                    "support_score": support_score
                })
        
        # Step 3: 최종 답변 합성
        if stream_callback:
            await stream_callback({
                "type": "final_synthesis",
                "message": "단계별 결과를 종합하여 최종 답변 생성 중..."
            })
        
        final_answer = await self._synthesize_cot_final_answer(
            query, reasoning_steps, accumulated_context
        )
        
        # 신뢰도 점수 계산 (CoT는 단계별 일관성도 고려)
        confidence_score = self._calculate_cot_confidence(reasoning_steps)
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        
        return ReasoningResult(
            query=query,
            mode="cot_rag",
            final_answer=final_answer,
            reasoning_steps=reasoning_steps,
            total_iterations=len(reasoning_steps),
            confidence_score=confidence_score,
            sources=all_sources,
            elapsed_time=elapsed_time
        )
    
    async def _decompose_question(self, query: str) -> List[str]:
        """
        질문을 하위 문제로 분해
        CoT-RAG의 첫 번째 단계
        """
        decomposition_prompt = f"""Break down this complex question into 3-5 smaller, more specific sub-questions.
        Each sub-question should address a different aspect of the main question.
        
        Main Question: {query}
        
        Guidelines:
        1. Each sub-question should be self-contained and answerable
        2. Sub-questions should build upon each other logically
        3. Cover all important aspects of the main question
        4. Keep sub-questions focused and specific
        
        Return only the sub-questions, one per line, numbered:"""
        
        response = await self.llm.generate(decomposition_prompt)
        
        # 응답에서 하위 질문 추출
        lines = response.strip().split('\n')
        sub_questions = []
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # 번호나 불릿 포인트 제거
                question = line.split('.', 1)[-1].strip()
                question = question.lstrip('- •').strip()
                if question and len(question) > 10:
                    sub_questions.append(question)
        
        # 최소 2개, 최대 5개로 제한
        if len(sub_questions) < 2:
            sub_questions = [query]  # 분해 실패 시 원본 질문 사용
        elif len(sub_questions) > 5:
            sub_questions = sub_questions[:5]
        
        return sub_questions
    
    async def _enhance_query_with_context(
        self,
        sub_query: str,
        accumulated_context: str
    ) -> str:
        """이전 컨텍스트를 고려하여 검색 쿼리 향상"""
        if not accumulated_context:
            return sub_query
        
        enhancement_prompt = f"""Given the previous context, enhance this search query to be more specific and informative.
        
        Current question: {sub_query}
        
        Previous context:
        {accumulated_context[-800:]}  # 최근 800자만 사용
        
        Enhanced search query (keep it concise but specific):"""
        
        enhanced_query = await self.llm.generate(enhancement_prompt)
        
        # 쿼리가 너무 길거나 비어있으면 원본 사용
        enhanced_query = enhanced_query.strip()
        if len(enhanced_query) < 10 or len(enhanced_query) > 200:
            return sub_query
        
        return enhanced_query
    
    async def _generate_cot_step_answer(
        self,
        sub_query: str,
        documents: List[Dict[str, Any]],
        accumulated_context: str,
        step_number: int
    ) -> str:
        """CoT 단계별 답변 생성"""
        context = self._prepare_context(documents, max_docs=3)
        
        cot_prompt = f"""Answer this sub-question as part of a step-by-step reasoning process.
        
        Step {step_number} Question: {sub_query}
        
        Retrieved Information:
        {context}
        
        Previous Steps Context:
        {accumulated_context[-600:] if accumulated_context else "This is the first step."}
        
        Guidelines:
        1. Provide a focused answer to this specific sub-question
        2. Build upon previous steps when relevant
        3. Be concise but comprehensive
        4. Support your answer with evidence from the retrieved information
        
        Step {step_number} Answer:"""
        
        answer = await self.llm.generate(cot_prompt)
        return answer.strip()
    
    async def _synthesize_cot_final_answer(
        self,
        original_query: str,
        reasoning_steps: List[ReasoningStep],
        accumulated_context: str
    ) -> str:
        """CoT 최종 답변 합성"""
        step_summaries = []
        for i, step in enumerate(reasoning_steps):
            summary = f"Step {i + 1} ({step.query}): {step.partial_answer[:200]}..."
            step_summaries.append(summary)
        
        synthesis_prompt = f"""Synthesize a comprehensive final answer based on the step-by-step reasoning process.
        
        Original Question: {original_query}
        
        Step-by-Step Analysis:
        {chr(10).join(step_summaries)}
        
        Full Context:
        {accumulated_context}
        
        Guidelines:
        1. Integrate insights from all steps into a coherent answer
        2. Address the original question completely
        3. Maintain logical flow and consistency
        4. Highlight key findings and connections between steps
        5. Provide a clear, well-structured response
        
        Final Comprehensive Answer:"""
        
        final_answer = await self.llm.generate(synthesis_prompt)
        return final_answer.strip()
    
    def _calculate_cot_confidence(self, reasoning_steps: List[ReasoningStep]) -> float:
        """
        CoT 신뢰도 계산
        단계별 일관성과 지지도를 모두 고려
        """
        if not reasoning_steps:
            return 0.0
        
        # 기본 지지도 점수
        support_scores = [step.support_score for step in reasoning_steps]
        avg_support = sum(support_scores) / len(support_scores)
        
        # 단계별 일관성 보너스
        consistency_bonus = 0.0
        if len(reasoning_steps) >= 2:
            # 단계별 지지도 편차가 작을수록 일관성이 높음
            support_variance = sum(
                (score - avg_support) ** 2 for score in support_scores
            ) / len(support_scores)
            
            # 편차가 0.1 이하면 일관성 보너스 최대 0.1
            consistency_bonus = max(0, 0.1 - support_variance)
        
        # 전체 단계 수 보너스 (더 많은 단계 = 더 신뢰할 만함)
        step_bonus = min(0.05, len(reasoning_steps) * 0.01)
        
        final_confidence = min(1.0, avg_support + consistency_bonus + step_bonus)
        return final_confidence

    async def _mcts_rag_pipeline(
        self,
        query: str,
        stream_callback: Optional[callable] = None
    ) -> ReasoningResult:
        """
        Monte Carlo Tree Search RAG 파이프라인
        트리 탐색을 통한 최적 추론 경로 발견
        """
        start_time = datetime.now()
        reasoning_steps = []
        all_sources = []
        
        # MCTS 파라미터
        max_depth = 3
        exploration_constant = 1.4  # UCB1 상수
        num_simulations = 10
        
        if stream_callback:
            await stream_callback({
                "type": "mcts_start",
                "message": f"MCTS 탐색 시작 (시뮬레이션: {num_simulations}회)"
            })
        
        # MCTS 트리 초기화
        mcts_tree = MCTSNode(
            query=query,
            depth=0,
            accumulated_context=""
        )
        
        # 시뮬레이션 실행
        for simulation in range(num_simulations):
            if stream_callback:
                await stream_callback({
                    "type": "simulation_start",
                    "simulation": simulation + 1,
                    "total_simulations": num_simulations
                })
            
            # 1. Selection: UCB1 기반 노드 선택
            selected_node = await self._select_node(mcts_tree, exploration_constant)
            
            # 2. Expansion: 새로운 자식 노드 생성
            if selected_node.depth < max_depth and not selected_node.is_terminal:
                expanded_node = await self._expand_node(selected_node, query)
                if expanded_node:
                    selected_node = expanded_node
            
            # 3. Simulation: 리프 노드부터 끝까지 시뮬레이션
            reward = await self._simulate_path(selected_node, query)
            
            # 4. Backpropagation: 보상을 상위 노드로 전파
            await self._backpropagate(selected_node, reward)
            
            if stream_callback:
                await stream_callback({
                    "type": "simulation_completed",
                    "simulation": simulation + 1,
                    "reward": reward,
                    "best_path_reward": mcts_tree.best_child_value()
                })
        
        # 최적 경로 추출
        best_path = self._extract_best_path(mcts_tree)
        
        if stream_callback:
            await stream_callback({
                "type": "best_path_found",
                "path_length": len(best_path),
                "total_reward": sum(node.average_reward() for node in best_path)
            })
        
        # 최적 경로를 따라 실제 추론 실행
        for i, node in enumerate(best_path[1:]):  # 루트 제외
            step_start = datetime.now()
            
            # 검색 및 리랭킹
            documents, relevance_scores = await self._search_and_rerank(
                node.refined_query or node.query
            )
            
            # 관련성 평가
            relevance_eval, individual_scores = await self.relevance_agent.reason(
                query=node.query,
                documents=documents,
                top_k=3
            )
            
            # 답변 생성
            partial_answer = await self._generate_mcts_answer(
                node, documents, i + 1
            )
            
            # 지지도 평가
            support_score, support_details = await self.support_agent.reason(
                answer=partial_answer,
                documents=documents,
                check_factual=True
            )
            
            # 추론 단계 저장
            step = ReasoningStep(
                iteration=i,
                query=node.query,
                refined_query=node.refined_query,
                documents=documents,
                relevance_scores=individual_scores,
                partial_answer=partial_answer,
                support_score=support_score,
                should_continue=i < len(best_path) - 2,
                timestamp=step_start
            )
            reasoning_steps.append(step)
            all_sources.extend(documents[:2])
        
        # 최종 답변 합성
        final_answer = await self._synthesize_mcts_final_answer(
            query, reasoning_steps, best_path
        )
        
        # 신뢰도 점수 계산 (MCTS는 탐색 품질도 고려)
        confidence_score = self._calculate_mcts_confidence(reasoning_steps, mcts_tree)
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        
        return ReasoningResult(
            query=query,
            mode="mcts_rag",
            final_answer=final_answer,
            reasoning_steps=reasoning_steps,
            total_iterations=len(reasoning_steps),
            confidence_score=confidence_score,
            sources=all_sources,
            elapsed_time=elapsed_time
        )
    
    async def _select_node(self, root: MCTSNode, exploration_constant: float) -> MCTSNode:
        """UCB1 기반 노드 선택 (Selection)"""
        current = root
        
        while current.children and current.is_expanded:
            # UCB1 값이 가장 높은 자식 선택
            current = max(
                current.children,
                key=lambda child: child.ucb1_value(exploration_constant)
            )
        
        return current
    
    async def _expand_node(self, node: MCTSNode, original_query: str) -> Optional[MCTSNode]:
        """노드 확장 (Expansion)"""
        if node.is_terminal or node.depth >= 3:
            return None
        
        # 가능한 하위 쿼리 생성
        possible_queries = await self._generate_child_queries(node, original_query)
        
        if not possible_queries:
            node.is_terminal = True
            return None
        
        # 첫 번째 미탐색 쿼리로 자식 노드 생성
        for sub_query in possible_queries:
            child_node = MCTSNode(
                query=sub_query,
                depth=node.depth + 1,
                accumulated_context=node.accumulated_context,
                parent=node
            )
            node.add_child(child_node)
        
        node.is_expanded = True
        
        # 첫 번째 자식 반환
        return node.children[0] if node.children else None
    
    async def _generate_child_queries(
        self,
        node: MCTSNode,
        original_query: str
    ) -> List[str]:
        """자식 노드를 위한 하위 쿼리 생성"""
        if node.depth == 0:
            # 루트: 원본 질문을 다양한 관점으로 분해
            prompt = f"""Break down this research question into 2-3 different focused sub-questions.
            Each should explore a different aspect or approach.
            
            Original Question: {original_query}
            
            Return 2-3 sub-questions, one per line:"""
        
        elif node.depth == 1:
            # 깊이 1: 더 구체적인 세부 질문들
            prompt = f"""Given this sub-question, generate 2 more specific questions that would help answer it.
            
            Current Sub-Question: {node.query}
            Original Question: {original_query}
            
            Return 2 specific questions, one per line:"""
        
        else:
            # 깊이 2+: 세부 검증 질문들  
            prompt = f"""Generate 1-2 verification questions for this specific query.
            
            Current Query: {node.query}
            Context: {node.accumulated_context[-200:]}
            
            Return 1-2 verification questions, one per line:"""
        
        response = await self.llm.generate(prompt)
        
        # 응답에서 질문 추출
        lines = response.strip().split('\n')
        queries = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                # 번호나 불릿 포인트 제거
                query = line.split('.', 1)[-1].strip()
                query = query.lstrip('- •').strip()
                if query and len(query) > 10:
                    queries.append(query)
        
        return queries[:3]  # 최대 3개로 제한
    
    async def _simulate_path(self, node: MCTSNode, original_query: str) -> float:
        """경로 시뮬레이션 (Simulation)"""
        # 간단한 시뮬레이션: 검색 품질 예측
        try:
            # 현재 노드의 쿼리로 빠른 검색 수행
            documents, relevance_scores = await self._search_and_rerank(
                node.query, context=[]
            )
            
            # 시뮬레이션 보상 계산
            if not documents:
                return 0.1  # 문서 없음
            
            # 검색 품질 기반 보상
            avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.5
            
            # 쿼리 품질 보너스 (원본 질문과의 관련성)
            query_quality = await self._evaluate_query_quality(node.query, original_query)
            
            # 깊이 페널티 (너무 깊으면 감점)
            depth_penalty = max(0, node.depth - 2) * 0.1
            
            reward = avg_relevance * 0.6 + query_quality * 0.4 - depth_penalty
            return min(max(reward, 0.0), 1.0)
            
        except Exception as e:
            logger.warning(f"MCTS simulation failed: {e}")
            return 0.2  # 기본 낮은 보상
    
    async def _evaluate_query_quality(self, sub_query: str, original_query: str) -> float:
        """쿼리 품질 평가"""
        prompt = f"""Rate how well this sub-question helps answer the original question.
        
        Original Question: {original_query}
        Sub-Question: {sub_query}
        
        Rate from 0.0 (not helpful) to 1.0 (very helpful):"""
        
        try:
            response = await self.llm.generate(prompt)
            import re
            numbers = re.findall(r'0\.\d+|1\.0|[01]', response)
            if numbers:
                return float(numbers[0])
        except:
            pass
        
        return 0.5  # 기본값
    
    async def _backpropagate(self, node: MCTSNode, reward: float):
        """보상 역전파 (Backpropagation)"""
        current = node
        
        while current is not None:
            current.update(reward)
            current = current.parent
    
    def _extract_best_path(self, root: MCTSNode) -> List[MCTSNode]:
        """최적 경로 추출"""
        path = [root]
        current = root
        
        while current.children:
            # 가장 높은 평균 보상을 가진 자식 선택
            best_child = max(
                current.children,
                key=lambda child: child.average_reward()
            )
            path.append(best_child)
            current = best_child
        
        return path
    
    async def _generate_mcts_answer(
        self,
        node: MCTSNode,
        documents: List[Dict[str, Any]],
        step_number: int
    ) -> str:
        """MCTS 단계별 답변 생성"""
        context = self._prepare_context(documents, max_docs=3)
        
        mcts_prompt = f"""Answer this question as part of a tree-search guided reasoning process.
        
        Step {step_number} Question: {node.query}
        Search Depth: {node.depth}
        
        Retrieved Information:
        {context}
        
        Previous Context:
        {node.accumulated_context[-400:] if node.accumulated_context else "Starting exploration."}
        
        Guidelines:
        1. Focus on this specific question
        2. Consider the search strategy that led here
        3. Build upon previous findings
        4. Be precise and evidence-based
        
        Step {step_number} Answer:"""
        
        answer = await self.llm.generate(mcts_prompt)
        return answer.strip()
    
    async def _synthesize_mcts_final_answer(
        self,
        original_query: str,
        reasoning_steps: List[ReasoningStep],
        best_path: List[MCTSNode]
    ) -> str:
        """MCTS 최종 답변 합성"""
        # 경로 정보 수집
        path_info = []
        for i, node in enumerate(best_path):
            if i > 0:  # 루트 제외
                reward = node.average_reward()
                path_info.append(f"Path {i} (Depth {node.depth}): {node.query} (Quality: {reward:.2f})")
        
        # 단계별 답변 수집
        step_answers = [step.partial_answer for step in reasoning_steps]
        
        synthesis_prompt = f"""Synthesize a comprehensive final answer based on Monte Carlo Tree Search guided reasoning.
        
        Original Question: {original_query}
        
        Optimal Search Path:
        {chr(10).join(path_info)}
        
        Step-by-Step Findings:
        {chr(10).join([f"{i+1}. {ans[:150]}..." for i, ans in enumerate(step_answers)])}
        
        Guidelines:
        1. Integrate insights from the optimal search path
        2. Emphasize findings with higher quality scores
        3. Address the original question comprehensively
        4. Highlight the systematic exploration process
        
        Final Comprehensive Answer:"""
        
        final_answer = await self.llm.generate(synthesis_prompt)
        return final_answer.strip()
    
    def _calculate_mcts_confidence(
        self,
        reasoning_steps: List[ReasoningStep],
        mcts_tree: MCTSNode
    ) -> float:
        """MCTS 신뢰도 계산"""
        if not reasoning_steps:
            return 0.0
        
        # 기본 지지도 점수
        support_scores = [step.support_score for step in reasoning_steps]
        avg_support = sum(support_scores) / len(support_scores)
        
        # 탐색 품질 보너스
        exploration_bonus = 0.0
        if mcts_tree.children:
            # 탐색된 경로의 평균 품질
            path_qualities = []
            for child in mcts_tree.children:
                if child.visit_count > 0:
                    path_qualities.append(child.average_reward())
            
            if path_qualities:
                exploration_bonus = sum(path_qualities) / len(path_qualities) * 0.2
        
        # 시뮬레이션 수 보너스 (더 많은 탐색 = 더 신뢰)
        simulation_bonus = min(0.1, mcts_tree.visit_count * 0.01)
        
        final_confidence = min(1.0, avg_support + exploration_bonus + simulation_bonus)
        return final_confidence