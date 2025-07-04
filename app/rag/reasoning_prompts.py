"""
Reasoning Prompts for RAG Pipeline
추론 파이프라인을 위한 프롬프트 템플릿 관리
"""

from typing import List, Optional, Dict, Any


class ReasoningPrompts:
    """추론 프롬프트 템플릿 클래스"""
    
    def __init__(self):
        """프롬프트 템플릿 초기화"""
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """프롬프트 템플릿 로드"""
        return {
            "retrieval_decision": self._retrieval_decision_template(),
            "query_refinement": self._query_refinement_template(),
            "relevance_evaluation": self._relevance_evaluation_template(),
            "partial_answer": self._partial_answer_template(),
            "final_answer": self._final_answer_template(),
            "support_evaluation": self._support_evaluation_template(),
            "continuation_decision": self._continuation_decision_template()
        }
    
    # Retrieval Decision [Retrieve] 프롬프트
    def get_retrieval_decision_prompt(
        self,
        query: str,
        context: str,
        support_scores: List[float]
    ) -> str:
        """검색 필요성 판단 프롬프트"""
        avg_support = sum(support_scores) / len(support_scores) if support_scores else 0
        
        return f"""You are evaluating whether additional information retrieval is needed to answer a question.

Question: {query}

Current Context and Support:
{context}

Average Support Score: {avg_support:.2f}

Based on the current context and support scores, determine if MORE information retrieval is needed.
Consider:
1. Are there gaps in the current information?
2. Is the support score sufficient (>0.7 is generally good)?
3. Would additional retrieval likely improve the answer?

Respond with either:
- "YES - [brief reason]" if more retrieval is needed
- "NO - [brief reason]" if current information is sufficient

Decision:"""
    
    # Query Refinement 프롬프트
    def get_query_refinement_prompt(
        self,
        original_query: str,
        previous_answers: str,
        missing_info: str,
        focus: Optional[str] = None
    ) -> str:
        """쿼리 개선 프롬프트"""
        focus_instruction = f"\nFocus Area: {focus}" if focus else ""
        
        return f"""Refine the search query to find missing information based on what we've learned so far.

Original Question: {original_query}

Previous Answers:
{previous_answers}

Missing Information:
{missing_info}
{focus_instruction}

Create a refined search query that:
1. Targets the specific missing information
2. Uses precise keywords likely to match relevant documents
3. Remains focused on answering the original question
4. Is concise (under 100 words)

Refined Query:"""
    
    # Relevance Evaluation [Relevant] 프롬프트
    def get_relevance_evaluation_prompt(
        self,
        query: str,
        document: str
    ) -> str:
        """문서 관련성 평가 프롬프트"""
        return f"""Evaluate the relevance of this document to the question.

Question: {query}

Document:
{document}

Rate the relevance on a scale from 0.0 to 1.0:
- 0.0-0.2: Not relevant
- 0.3-0.5: Somewhat relevant
- 0.6-0.8: Relevant
- 0.9-1.0: Highly relevant

Consider:
1. Does the document directly address the question?
2. Does it provide useful context or background?
3. Does it contain specific facts or evidence related to the question?

Relevance Score (0.0-1.0):"""
    
    # Partial Answer Generation 프롬프트
    def get_partial_answer_prompt(
        self,
        query: str,
        context: str,
        previous_reasoning: str
    ) -> str:
        """부분 답변 생성 프롬프트"""
        return f"""Generate a partial answer based on the newly retrieved information.

Question: {query}

New Context:
{context}

Previous Reasoning:
{previous_reasoning}

Instructions:
1. Focus on information from the new context
2. Build upon previous reasoning without repeating
3. Be specific and cite evidence from the documents
4. Keep the answer concise but informative (150-300 words)
5. If the new context adds significant insights, emphasize them

Partial Answer:"""
    
    # Final Answer Synthesis 프롬프트
    def get_final_answer_prompt(
        self,
        query: str,
        all_contexts: str,
        reasoning_chain: str
    ) -> str:
        """최종 답변 합성 프롬프트"""
        return f"""Synthesize a comprehensive final answer by combining insights from the entire reasoning process.

Question: {query}

All Retrieved Contexts:
{all_contexts}

Reasoning Chain:
{reasoning_chain}

Instructions:
1. Provide a complete, well-structured answer to the original question
2. Integrate key insights from all reasoning steps
3. Cite specific evidence from the documents when possible
4. Ensure the answer is coherent and flows naturally
5. Address all aspects of the question
6. Maintain an objective, informative tone
7. Conclude with a brief summary if the answer is long

Final Comprehensive Answer:"""
    
    # Support Evaluation [Support] 프롬프트
    def get_support_evaluation_prompt(
        self,
        answer: str,
        document: str
    ) -> str:
        """답변 지지도 평가 프롬프트"""
        return f"""Evaluate how well this answer is supported by the document.

Answer: {answer}

Supporting Document:
{document}

Rate the support level from 0.0 to 1.0:
- 0.0-0.2: Not supported (contradicts or no relevance)
- 0.3-0.5: Weakly supported (some relevance but lacks evidence)
- 0.6-0.8: Supported (good evidence, minor gaps)
- 0.9-1.0: Fully supported (strong, direct evidence)

Consider:
1. Are the key claims in the answer backed by the document?
2. Is there direct evidence or just topical relevance?
3. Are there any unsupported statements?

Support Score (0.0-1.0):"""
    
    # Chain-of-Thought 프롬프트 (v3.86용)
    def get_cot_planning_prompt(
        self,
        query: str,
        context: Optional[str] = None
    ) -> str:
        """CoT 계획 수립 프롬프트"""
        context_section = f"\nInitial Context:\n{context}" if context else ""
        
        return f"""Break down this complex question into a logical sequence of sub-questions that need to be answered.

Question: {query}
{context_section}

Create a step-by-step plan where each step:
1. Addresses a specific aspect of the main question
2. Builds upon previous steps
3. Can be answered with focused information retrieval

Format:
Step 1: [Sub-question]
Step 2: [Sub-question]
...

Reasoning Plan:"""
    
    # MCTS 프롬프트 (v3.87용)
    def get_mcts_expansion_prompt(
        self,
        query: str,
        current_path: List[str],
        available_actions: List[str]
    ) -> str:
        """MCTS 노드 확장 프롬프트"""
        path_str = " -> ".join(current_path) if current_path else "Start"
        actions_str = "\n".join([f"- {a}" for a in available_actions])
        
        return f"""Given the current reasoning path, select the most promising next action.

Question: {query}

Current Path: {path_str}

Available Actions:
{actions_str}

Consider:
1. Which action is most likely to lead to a complete answer?
2. What information is still missing?
3. Which path avoids redundancy?

Select the best action and explain why:"""
    
    # 신약개발 도메인 특화 프롬프트
    def get_drug_discovery_prompt(
        self,
        query: str,
        mode: str = "general"
    ) -> str:
        """신약개발 특화 프롬프트"""
        if mode == "target_validation":
            return f"""As a drug discovery expert, analyze this target validation question:

{query}

Consider:
1. Genetic evidence (GWAS, knockout studies)
2. Pathway involvement and druggability
3. Disease association strength
4. Safety and selectivity concerns
5. Competitive landscape

Provide a comprehensive analysis:"""
        
        elif mode == "clinical_trial":
            return f"""As a clinical development expert, analyze this clinical trial question:

{query}

Address:
1. Trial design considerations
2. Patient population and inclusion criteria
3. Endpoints (primary/secondary)
4. Safety monitoring requirements
5. Regulatory considerations

Provide detailed insights:"""
        
        else:  # general drug discovery
            return f"""As a pharmaceutical research expert, answer this drug discovery question:

{query}

Consider relevant aspects such as:
- Molecular mechanisms
- Therapeutic potential
- Development challenges
- Regulatory pathway
- Market considerations

Provide a scientifically accurate response:"""
    
    # 템플릿 메서드들
    def _retrieval_decision_template(self) -> str:
        return """Retrieval Decision Template - Determines if more information is needed"""
    
    def _query_refinement_template(self) -> str:
        return """Query Refinement Template - Improves search queries based on context"""
    
    def _relevance_evaluation_template(self) -> str:
        return """Relevance Evaluation Template - Scores document relevance"""
    
    def _partial_answer_template(self) -> str:
        return """Partial Answer Template - Generates incremental answers"""
    
    def _final_answer_template(self) -> str:
        return """Final Answer Template - Synthesizes comprehensive response"""
    
    def _support_evaluation_template(self) -> str:
        return """Support Evaluation Template - Measures answer support level"""
    
    def _continuation_decision_template(self) -> str:
        return """Continuation Decision Template - Decides whether to continue reasoning"""
    
    # 유틸리티 메서드
    def format_citations(self, sources: List[Dict[str, Any]]) -> str:
        """소스 인용 포맷팅"""
        citations = []
        
        for i, source in enumerate(sources, 1):
            metadata = source.get("metadata", {})
            text_preview = source.get("text", "")[:100] + "..."
            
            citation = f"[{i}] "
            if metadata.get("title"):
                citation += f"{metadata['title']}. "
            if metadata.get("authors"):
                citation += f"{metadata['authors']}. "
            if metadata.get("year"):
                citation += f"({metadata['year']}). "
            if metadata.get("source"):
                citation += f"Source: {metadata['source']}. "
            
            citation += f'"{text_preview}"'
            citations.append(citation)
        
        return "\n".join(citations)
    
    def get_prompt_by_name(self, name: str, **kwargs) -> str:
        """이름으로 프롬프트 가져오기"""
        prompt_methods = {
            "retrieval_decision": self.get_retrieval_decision_prompt,
            "query_refinement": self.get_query_refinement_prompt,
            "relevance_evaluation": self.get_relevance_evaluation_prompt,
            "partial_answer": self.get_partial_answer_prompt,
            "final_answer": self.get_final_answer_prompt,
            "support_evaluation": self.get_support_evaluation_prompt,
            "cot_planning": self.get_cot_planning_prompt,
            "mcts_expansion": self.get_mcts_expansion_prompt,
            "drug_discovery": self.get_drug_discovery_prompt
        }
        
        if name in prompt_methods:
            return prompt_methods[name](**kwargs)
        else:
            raise ValueError(f"Unknown prompt name: {name}")