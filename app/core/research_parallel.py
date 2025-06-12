#!/usr/bin/env python3
"""
연구 병렬 처리 모듈
GPU 최적화 및 병렬 처리를 통한 연구 프로세스 실행
"""

import asyncio
from typing import Any, Callable, Dict, List, Optional

from app.api.ollama_client import OllamaClient
from app.core.answer_generator import AnswerGenerator


class ResearchParallel:
    """
    연구 병렬 처리 클래스
    병렬 질문 처리 및 대체 답변 생성 동시 처리 관리
    """

    def __init__(self,
                ollama_client: Optional[OllamaClient] = None,
                concurrent_limit: int = 2):
        """
        병렬 처리 관리자 초기화

        Args:
            ollama_client: OllamaClient 인스턴스 (없으면 새로 생성)
            concurrent_limit: 동시 처리 가능한 작업 수 (기본값: 2)
        """
        self.client = ollama_client or OllamaClient()
        self.concurrent_limit = concurrent_limit
        self.answer_generator = AnswerGenerator(self.client)

    async def process_questions_parallel(
            self,
            questions: List[str],
            process_func: Callable,
            concurrent_limit: Optional[int] = None
        ) -> List[Dict[str, Any]]:
        """
        질문 목록에 대한 병렬 처리 실행

        Args:
            questions: 처리할 질문 목록
            process_func: 각 질문을 처리할 비동기 함수 (idx, question을 인자로 받음)
            concurrent_limit: 동시 처리 제한 (없으면 인스턴스 기본값 사용)

        Returns:
            List[Dict[str, Any]]: 처리된 결과 목록
        """
        # 동시 실행 세마포어
        limit = concurrent_limit or self.concurrent_limit
        semaphore = asyncio.Semaphore(limit)

        # 병렬 처리 래퍼 함수
        async def process_with_semaphore(idx: int, question: str):
            async with semaphore:
                try:
                    return await process_func(idx, question)
                except Exception as e:
                    print(f"[병렬처리 오류] 질문 {idx+1}: {e!s}")
                    return {
                        "question_id": f"Q{idx+1:02d}",
                        "question": question[:100] + "..." if len(question) > 100 else question,
                        "error": str(e),
                        "status": "failed"
                    }

        # 병렬 처리 작업 생성
        tasks = [process_with_semaphore(i, q) for i, q in enumerate(questions)]
        results = await asyncio.gather(*tasks)

        return results

    async def generate_alternative_answers(
            self,
            question: str,
            prompt_template: str,
            system_prompt: Optional[str] = None,
            width: int = 2
        ) -> List[str]:
        """
        단일 질문에 대해 여러 대체 답변을 병렬 생성

        Args:
            question: 질문 문자열
            prompt_template: 프롬프트 템플릿 (질문이 삽입될 위치에 {question} 포함)
            system_prompt: 시스템 프롬프트 (선택사항)
            width: 생성할 대체 답변 수 (기본값: 2)

        Returns:
            List[str]: 생성된 대체 답변 목록
        """
        # 병렬 생성할 프롬프트 목록 준비
        prompts = []
        for i in range(width):
            # 약간의 다양성을 위한 온도 변화 (0.6 ~ 0.8)
            temp = 0.6 + (i * 0.2 / max(1, width-1))

            prompts.append({
                "prompt": prompt_template.format(question=question),
                "system": system_prompt,
                "temperature": temp
            })

        # 병렬 생성 실행
        results = await self.client.generate_parallel(prompts, max_concurrent=width)

        # 오류 처리
        valid_answers = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"[대체답변 생성 오류] 시도 {i+1}: {result!s}")
            else:
                valid_answers.append(result)

        # 최소 하나의 유효한 답변이 없으면 기본 답변 생성
        if not valid_answers:
            try:
                default_answer = await self.answer_generator.generate_answer(
                    question,
                    temperature=0.7
                )
                valid_answers.append(default_answer)
            except Exception as e:
                print(f"[기본 답변 생성 오류]: {e!s}")
                valid_answers.append(f"[답변 생성 실패: {e!s}]")

        return valid_answers


# 모듈 직접 실행 시 테스트
if __name__ == "__main__":
    async def test():
        parallel = ResearchParallel()

        # 테스트 질문
        question = "근육 발달에 가장 중요한 아미노산은 무엇이며, 어떤 식품에 많이 함유되어 있나요?"

        # 병렬 대체 답변 생성 테스트
        template = "다음 질문에 대해 최대한 자세하고 과학적인 근거를 포함하여 답변해주세요:\n\n{question}"
        system = "당신은 근육 관련 건강기능식품 전문가입니다. 항상 참고문헌을 포함하세요."

        print(f"테스트 질문: {question}")
        print("대체 답변 생성 중...")

        answers = await parallel.generate_alternative_answers(
            question, template, system, width=2
        )

        print(f"\n총 {len(answers)}개의 대체 답변 생성됨:")
        for i, answer in enumerate(answers):
            print(f"\n--- 답변 {i+1} ---\n")
            print(answer[:300] + "..." if len(answer) > 300 else answer)

    asyncio.run(test())
