"""
LLM-based Reasoning Agents for RAG Pipeline
Self-RAG, CoT-RAG, MCTS-RAG를 위한 추론 에이전트
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
import json

from app.api.ollama_client import OllamaClient
from app.rag.reasoning_prompts import ReasoningPrompts

logger = logging.getLogger(__name__)


class BaseReasoningAgent(ABC):
    """추론 에이전트 기본 클래스"""
    
    def __init__(self, llm_model: str = "gemma3-12b"):
        self.llm = OllamaClient(model=llm_model)
        self.prompts = ReasoningPrompts()
    
    @abstractmethod
    async def reason(self, *args, **kwargs):
        """추론 수행"""
        pass
    
    async def _generate(self, prompt: str, temperature: float = 0.7) -> str:
        """LLM 생성 헬퍼"""
        response = await self.llm.generate(prompt, temperature=temperature)
        return response.strip()


class RetrievalDecisionAgent(BaseReasoningAgent):
    """검색 필요성 판단 에이전트 [Retrieve]"""
    
    async def reason(
        self,
        query: str,
        history: List[Dict[str, Any]],
        threshold: float = 0.7
    ) -> Tuple[bool, str]:
        """
        검색 필요성 판단
        
        Returns:
            (should_retrieve, reasoning)
        """
        if not history:
            return True, "Initial retrieval needed"
        
        # 최근 컨텍스트 수집
        recent_context = self._get_recent_context(history)
        
        prompt = self.prompts.get_retrieval_decision_prompt(
            query=query,
            context=recent_context,
            support_scores=[step.get("support_score", 0) for step in history]
        )
        
        response = await self._generate(prompt, temperature=0.3)
        
        # 응답 파싱
        try:
            if "YES" in response.upper():
                return True, response
            elif "NO" in response.upper():
                return False, response
            else:
                # 명확하지 않으면 지지도 기반 결정
                avg_support = sum(
                    step.get("support_score", 0) for step in history
                ) / len(history)
                return avg_support < threshold, f"Based on average support: {avg_support:.2f}"
        except:
            return True, "Error in parsing, defaulting to retrieve"
    
    def _get_recent_context(self, history: List[Dict[str, Any]], n: int = 2) -> str:
        """최근 n개의 컨텍스트 추출"""
        recent = history[-n:]
        context_parts = []
        
        for step in recent:
            context_parts.append(
                f"Iteration {step.get('iteration', 0) + 1}:\n"
                f"Answer: {step.get('partial_answer', '')[:200]}...\n"
                f"Support: {step.get('support_score', 0):.2f}"
            )
        
        return "\n\n".join(context_parts)


class QueryRefinementAgent(BaseReasoningAgent):
    """쿼리 개선 에이전트"""
    
    async def reason(
        self,
        original_query: str,
        history: List[Dict[str, Any]],
        focus: Optional[str] = None
    ) -> str:
        """
        컨텍스트 기반 쿼리 개선
        
        Args:
            original_query: 원본 쿼리
            history: 이전 추론 단계
            focus: 특정 포커스 영역
            
        Returns:
            개선된 쿼리
        """
        if not history:
            return original_query
        
        # 이전 답변에서 누락된 정보 파악
        missing_info = await self._identify_missing_info(original_query, history)
        
        prompt = self.prompts.get_query_refinement_prompt(
            original_query=original_query,
            previous_answers=self._get_previous_answers(history),
            missing_info=missing_info,
            focus=focus
        )
        
        refined_query = await self._generate(prompt, temperature=0.5)
        
        # 쿼리 검증
        if len(refined_query) < 10 or len(refined_query) > 500:
            return original_query
        
        return refined_query
    
    async def _identify_missing_info(
        self,
        query: str,
        history: List[Dict[str, Any]]
    ) -> str:
        """누락된 정보 식별"""
        answers = self._get_previous_answers(history)
        
        prompt = f"""Given the question and current answers, identify what information is still missing.

Question: {query}

Current answers:
{answers}

What specific information is missing? Be concise:"""
        
        return await self._generate(prompt, temperature=0.3)
    
    def _get_previous_answers(self, history: List[Dict[str, Any]]) -> str:
        """이전 답변 추출"""
        answers = []
        for step in history[-3:]:  # 최근 3개
            answers.append(
                f"- {step.get('partial_answer', '')[:150]}..."
            )
        return "\n".join(answers)


class RelevanceEvaluationAgent(BaseReasoningAgent):
    """문서 관련성 평가 에이전트 [Relevant]"""
    
    async def reason(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 3
    ) -> Tuple[float, List[float]]:
        """
        문서 관련성 평가
        
        Returns:
            (overall_relevance, individual_scores)
        """
        if not documents:
            return 0.0, []
        
        # 상위 k개 문서 평가
        eval_docs = documents[:top_k]
        individual_scores = []
        
        for doc in eval_docs:
            score = await self._evaluate_single_doc(query, doc)
            individual_scores.append(score)
        
        # 전체 관련성 (가중 평균)
        weights = [0.5, 0.3, 0.2][:len(individual_scores)]
        overall = sum(s * w for s, w in zip(individual_scores, weights))
        
        return overall, individual_scores
    
    async def _evaluate_single_doc(
        self,
        query: str,
        document: Dict[str, Any]
    ) -> float:
        """단일 문서 평가"""
        doc_text = document.get("text", "")[:500]
        
        prompt = self.prompts.get_relevance_evaluation_prompt(
            query=query,
            document=doc_text
        )
        
        response = await self._generate(prompt, temperature=0.2)
        
        # 점수 파싱
        try:
            # 응답에서 숫자 추출
            import re
            numbers = re.findall(r'0\.\d+|1\.0|[01]', response)
            if numbers:
                score = float(numbers[0])
                return min(max(score, 0.0), 1.0)
        except:
            pass
        
        # 키워드 기반 폴백
        response_lower = response.lower()
        if "highly relevant" in response_lower or "very relevant" in response_lower:
            return 0.9
        elif "relevant" in response_lower:
            return 0.7
        elif "somewhat relevant" in response_lower:
            return 0.5
        elif "not relevant" in response_lower:
            return 0.2
        
        return 0.5  # 기본값


class AnswerGenerationAgent(BaseReasoningAgent):
    """답변 생성 에이전트"""
    
    async def reason(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        history: List[Dict[str, Any]],
        mode: str = "partial"
    ) -> str:
        """
        답변 생성
        
        Args:
            mode: "partial" 또는 "final"
        """
        context = self._prepare_context(documents)
        previous = self._get_previous_reasoning(history)
        
        if mode == "partial":
            prompt = self.prompts.get_partial_answer_prompt(
                query=query,
                context=context,
                previous_reasoning=previous
            )
        else:  # final
            prompt = self.prompts.get_final_answer_prompt(
                query=query,
                all_contexts=self._get_all_contexts(history),
                reasoning_chain=self._get_reasoning_chain(history)
            )
        
        answer = await self._generate(prompt, temperature=0.7)
        
        # 답변 후처리
        return self._postprocess_answer(answer, mode)
    
    def _prepare_context(self, documents: List[Dict[str, Any]], max_docs: int = 3) -> str:
        """문서 컨텍스트 준비"""
        contexts = []
        
        for i, doc in enumerate(documents[:max_docs]):
            text = doc.get("text", "")[:600]
            metadata = doc.get("metadata", {})
            
            context = f"Document {i+1}:\n{text}"
            if metadata.get("source"):
                context += f"\nSource: {metadata['source']}"
            
            contexts.append(context)
        
        return "\n\n".join(contexts)
    
    def _get_previous_reasoning(self, history: List[Dict[str, Any]]) -> str:
        """이전 추론 과정 추출"""
        if not history:
            return "No previous reasoning"
        
        recent = history[-2:]
        reasoning = []
        
        for step in recent:
            reasoning.append(
                f"Step {step.get('iteration', 0) + 1}: "
                f"{step.get('partial_answer', '')[:200]}..."
            )
        
        return "\n".join(reasoning)
    
    def _get_all_contexts(self, history: List[Dict[str, Any]]) -> str:
        """모든 컨텍스트 수집"""
        all_docs = []
        
        for step in history:
            docs = step.get("documents", [])
            all_docs.extend(docs[:2])  # 각 단계에서 상위 2개
        
        # 중복 제거
        seen = set()
        unique_docs = []
        
        for doc in all_docs:
            doc_id = doc.get("id") or doc.get("text", "")[:50]
            if doc_id not in seen:
                seen.add(doc_id)
                unique_docs.append(doc)
        
        return self._prepare_context(unique_docs[:5])
    
    def _get_reasoning_chain(self, history: List[Dict[str, Any]]) -> str:
        """추론 체인 구성"""
        chain = []
        
        for step in history:
            chain.append({
                "iteration": step.get("iteration", 0) + 1,
                "query": step.get("refined_query", ""),
                "answer": step.get("partial_answer", "")[:150] + "...",
                "support": step.get("support_score", 0)
            })
        
        return json.dumps(chain, indent=2)
    
    def _postprocess_answer(self, answer: str, mode: str) -> str:
        """답변 후처리"""
        # 불필요한 프리픽스 제거
        prefixes_to_remove = [
            "Based on the documents,",
            "According to the context,",
            "The documents show that",
            "Answer:",
            "Response:"
        ]
        
        for prefix in prefixes_to_remove:
            if answer.startswith(prefix):
                answer = answer[len(prefix):].strip()
        
        # 길이 조정
        if mode == "partial" and len(answer) > 500:
            # 문장 단위로 자르기
            sentences = answer.split(". ")
            truncated = []
            total_len = 0
            
            for sent in sentences:
                if total_len + len(sent) > 500:
                    break
                truncated.append(sent)
                total_len += len(sent) + 2
            
            answer = ". ".join(truncated) + "."
        
        return answer


class SupportEvaluationAgent(BaseReasoningAgent):
    """답변 지지도 평가 에이전트 [Support]"""
    
    async def reason(
        self,
        answer: str,
        documents: List[Dict[str, Any]],
        check_factual: bool = True
    ) -> Tuple[float, Dict[str, Any]]:
        """
        답변이 문서에 의해 얼마나 지지되는지 평가
        
        Returns:
            (support_score, evaluation_details)
        """
        if not documents:
            return 0.0, {"reason": "No supporting documents"}
        
        # 문서별 지지도 평가
        doc_supports = []
        
        for doc in documents[:3]:
            support = await self._evaluate_doc_support(answer, doc)
            doc_supports.append(support)
        
        # 전체 지지도 계산
        overall_support = max(doc_supports) if doc_supports else 0.0
        
        # 팩트 체크 (선택적)
        factual_consistency = 1.0
        if check_factual:
            factual_consistency = await self._check_factual_consistency(
                answer, documents
            )
        
        # 최종 점수
        final_score = overall_support * 0.7 + factual_consistency * 0.3
        
        details = {
            "document_supports": doc_supports,
            "overall_support": overall_support,
            "factual_consistency": factual_consistency,
            "supporting_evidence": await self._extract_evidence(answer, documents)
        }
        
        return final_score, details
    
    async def _evaluate_doc_support(
        self,
        answer: str,
        document: Dict[str, Any]
    ) -> float:
        """단일 문서의 지지도 평가"""
        doc_text = document.get("text", "")[:800]
        
        prompt = self.prompts.get_support_evaluation_prompt(
            answer=answer,
            document=doc_text
        )
        
        response = await self._generate(prompt, temperature=0.2)
        
        # 점수 추출
        try:
            import re
            numbers = re.findall(r'0\.\d+|1\.0|[01]', response)
            if numbers:
                return float(numbers[0])
        except:
            pass
        
        # 키워드 기반 평가
        response_lower = response.lower()
        if "fully supported" in response_lower or "strongly supported" in response_lower:
            return 0.9
        elif "supported" in response_lower or "partially supported" in response_lower:
            return 0.6
        elif "weakly supported" in response_lower:
            return 0.3
        elif "not supported" in response_lower:
            return 0.1
        
        return 0.5
    
    async def _check_factual_consistency(
        self,
        answer: str,
        documents: List[Dict[str, Any]]
    ) -> float:
        """사실적 일관성 확인"""
        context = "\n\n".join([
            doc.get("text", "")[:400]
            for doc in documents[:3]
        ])
        
        prompt = f"""Check if the answer contains any factual inconsistencies with the documents.

Answer: {answer}

Documents:
{context}

Are there any factual inconsistencies? Rate from 0 (many inconsistencies) to 1 (perfectly consistent):"""
        
        response = await self._generate(prompt, temperature=0.2)
        
        try:
            import re
            numbers = re.findall(r'0\.\d+|1\.0|[01]', response)
            if numbers:
                return float(numbers[0])
        except:
            pass
        
        return 0.8  # 기본값
    
    async def _extract_evidence(
        self,
        answer: str,
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """답변을 지지하는 증거 추출"""
        evidence = []
        
        # 간단한 키워드 매칭으로 증거 추출
        answer_keywords = set(answer.lower().split())
        
        for doc in documents[:3]:
            doc_text = doc.get("text", "")
            sentences = doc_text.split(". ")
            
            for sent in sentences:
                sent_keywords = set(sent.lower().split())
                overlap = len(answer_keywords & sent_keywords)
                
                if overlap > 5:  # 5개 이상 키워드 겹침
                    evidence.append(sent.strip())
                    if len(evidence) >= 3:
                        return evidence
        
        return evidence


class ContinuationDecisionAgent(BaseReasoningAgent):
    """계속 여부 결정 에이전트 [Continue]"""
    
    async def reason(
        self,
        iteration: int,
        support_score: float,
        history: List[Dict[str, Any]],
        max_iterations: int = 3
    ) -> Tuple[bool, str]:
        """
        추론을 계속할지 결정
        
        Returns:
            (should_continue, reasoning)
        """
        # 하드 리미트
        if iteration >= max_iterations - 1:
            return False, f"Reached maximum iterations ({max_iterations})"
        
        # 높은 지지도
        if support_score >= 0.85:
            return False, f"High support score achieved: {support_score:.2f}"
        
        # 개선 없음 체크
        if len(history) >= 2:
            recent_scores = [
                step.get("support_score", 0)
                for step in history[-2:]
            ]
            
            improvement = recent_scores[-1] - recent_scores[-2] if len(recent_scores) >= 2 else 0
            
            if all(s >= 0.7 for s in recent_scores) and abs(improvement) < 0.05:
                return False, "No significant improvement in recent iterations"
        
        # 수렴 체크
        if await self._check_convergence(history):
            return False, "Answers have converged"
        
        # 기본적으로 계속
        return True, f"Support score {support_score:.2f} below threshold, continuing"
    
    async def _check_convergence(self, history: List[Dict[str, Any]]) -> bool:
        """답변이 수렴했는지 확인"""
        if len(history) < 2:
            return False
        
        recent_answers = [
            step.get("partial_answer", "")
            for step in history[-2:]
        ]
        
        if not all(recent_answers):
            return False
        
        # 답변 유사도 체크
        prompt = f"""Compare these two answers and determine if they are essentially saying the same thing.

Answer 1: {recent_answers[0][:300]}...

Answer 2: {recent_answers[1][:300]}...

Are these answers essentially the same? (YES/NO):"""
        
        response = await self._generate(prompt, temperature=0.2)
        
        return "YES" in response.upper()