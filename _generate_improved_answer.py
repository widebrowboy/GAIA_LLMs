async def _generate_improved_answer(self, question: str, current_answer: str, feedback: str) -> str:
    """
    피드백을 기반으로 개선된 답변을 생성합니다.
    
    Args:
        question: 연구 질문
        current_answer: 현재 답변
        feedback: 피드백 내용
        
    Returns:
        str: 개선된 답변
    """
    try:
        # 개선 프롬프트 생성
        system_prompt = (
            "당신은 근육 관련 건강기능식품 전문가입니다. "
            "주어진 질문에 대해 과학적 근거에 기반한 정확하고 상세한 답변을 제공해주세요."
        )
        
        prompt = (
            f"### 질문\n{question}\n\n"
            f"### 현재 답변\n{current_answer}\n\n"
            f"### 피드백\n{feedback}\n\n"
            "### 지시사항\n"
            "위의 피드백을 바탕으로 개선된 답변을 작성해주세요. "
            "다음 구조를 반드시 따라주세요:\n\n"
            "## 1. 문제 정의\n"
            "## 2. 핵심 내용\n"
            "## 3. 과학적 근거\n"
            "## 4. 복용 방법 및 주의사항\n"
            "## 5. 결론 및 요약\n"
            "## 참고 문헌\n\n"
            "답변은 최소 1500자 이상으로 자세히 작성해주시고, "
            "모든 과학적 주장은 반드시 출처를 명시해주세요."
        )
        
        # 개선된 답변 생성 (GPU 가속 파라미터 적용)
        improved_answer = await self.generate_with_ollama(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        return improved_answer
        
    except Exception as e:
        print(f"      ⚠️ 개선된 답변 생성 중 오류: {str(e)}")
        return f"개선된 답변 생성 중 오류가 발생했습니다: {str(e)}"
