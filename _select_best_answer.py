async def _select_best_answer(self, question: str, original_answer: str, alternative_answers: List[str]) -> Dict[str, Any]:
    """
    여러 답변 중 최적의 답변을 선택합니다.
    
    Args:
        question: 연구 질문
        original_answer: 원래 답변
        alternative_answers: 대체 답변 목록
        
    Returns:
        Dict: 최적의 답변과 메타데이터
    """
    try:
        # 답변이 없는 경우 원래 답변 반환
        if not alternative_answers:
            return {
                "best_answer": original_answer,
                "reason": "대체 답변이 없어 원래 답변을 선택했습니다.",
                "timestamp": datetime.now().isoformat()
            }
        
        # 모든 답변 통합 (원래 답변 + 대체 답변들)
        all_answers = [original_answer] + alternative_answers
        
        # 평가 프롬프트 생성
        system_prompt = (
            "당신은 근육 관련 건강기능식품 전문가이자 과학 연구 평가자입니다. "
            "여러 답변 중에서 과학적 정확성, 완전성, 명확성, 참고 문헌 품질을 "
            "종합적으로 평가하여 최적의 답변을 선택해주세요."
        )
        
        prompt = (
            f"### 질문\n{question}\n\n"
            "### 답변 목록\n"
        )
        
        # 각 답변 추가
        for i, answer in enumerate(all_answers):
            # 답변 요약 (처음 200자 + ... + 마지막 100자)
            if len(answer) > 300:
                summary = f"{answer[:200]}... [중략] ...{answer[-100:]}"
            else:
                summary = answer
            
            prompt += f"#### [답변 {i+1}]\n{summary}\n\n"
        
        prompt += (
            "### 평가 지침\n"
            "위 답변들을 다음 기준에 따라 평가해주세요:\n\n"
            "- **과학적 정확성** (40%): 최신 연구 결과 반영, 사실 기반 정보\n"
            "- **완전성** (25%): 질문에 대한 모든 측면 포함, 누락 없음\n"
            "- **명확성** (20%): 설명의 명확성, 전문 용어 설명, 예시 활용\n"
            "- **참고 문헌** (15%): 신뢰할 수 있는 출처, 적절한 인용\n\n"
            "### 응답 형식\n"
            "1. 각 답변에 대한 간략한 평가 (장점과 단점)\n"
            "2. 최적의 답변 번호 선택 (1부터 시작)\n"
            "3. 선택 이유 설명\n\n"
            "최종 결정은 '최적의 답변은 [번호]번입니다.' 형식으로 명확히 표시해주세요."
        )
        
        # 평가 및 선택 (GPU 가속 파라미터 적용)
        evaluation = await self.generate_with_ollama(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3  # 일관된 평가를 위해 낮은 온도 사용
        )
        
        # 선택된 답변 번호 추출
        import re
        match = re.search(r'최적의 답변은 (\d+)번입니다', evaluation)
        
        if match:
            selected_index = int(match.group(1)) - 1
            if 0 <= selected_index < len(all_answers):
                selected_answer = all_answers[selected_index]
                is_original = selected_index == 0
                
                return {
                    "best_answer": selected_answer,
                    "is_original": is_original,
                    "selected_index": selected_index,
                    "evaluation": evaluation,
                    "timestamp": datetime.now().isoformat()
                }
        
        # 선택 실패 시 원래 답변 반환
        print("      ⚠️ 최적 답변 선택 실패, 원래 답변 사용")
        return {
            "best_answer": original_answer,
            "reason": "답변 선택 실패로 원래 답변을 사용합니다.",
            "evaluation": evaluation,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"      ⚠️ 최적 답변 선택 중 오류: {str(e)}")
        return {
            "best_answer": original_answer,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
