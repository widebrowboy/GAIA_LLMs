#!/usr/bin/env python3
"""
답변 생성 모듈
근육 관련 건강기능식품 연구 질문에 대한 답변 생성
"""

import os
import json
import asyncio
import random
from typing import Dict, Any, List, Optional
from ..api.ollama_client import OllamaClient

class AnswerGenerator:
    """
    건강기능식품 답변 생성 클래스
    질문에 대한 구조화된 답변 생성 및 다양한 답변 스타일 지원
    """
    
    def __init__(self, client: Optional[OllamaClient] = None):
        """
        답변 생성기 초기화
        
        Args:
            client: OllamaClient 인스턴스 (없으면 새로 생성)
        """
        self.client = client or OllamaClient()
        
        # 답변 형식 요구사항 (windsurfrules 기준)
        self.required_sections = [
            "문제 정의",
            "핵심 내용",
            "과학적 근거",
            "복용 방법 및 주의사항",
            "결론 및 요약",
            "참고 문헌"
        ]
    
    async def generate_answer(self, question: str, temperature: float = 0.7) -> str:
        """
        질문에 대한 답변 생성
        
        Args:
            question: 연구 질문
            temperature: 생성 온도 (0.1~1.0, 높을수록 창의적)
            
        Returns:
            str: 생성된 답변 (마크다운 형식)
        """
        # 시스템 프롬프트
        system_prompt = """당신은 근육 발달과 건강기능식품에 관한 전문가입니다.
답변은 항상 다음 형식을 따라야 합니다:
1. 문제 정의: 질문의 범위와 중요성 설명
2. 핵심 내용: 주요 이론, 개념, 원리 설명
3. 과학적 근거: 연구 결과와 데이터 제시
4. 복용 방법 및 주의사항: 실질적인 적용 정보
5. 결론 및 요약: 핵심 요점 정리
6. 참고 문헌: 최소 2개 이상의 신뢰할 수 있는 출처와 URL

답변은 다음 조건을 반드시 충족해야 합니다:
- 최소 1000자 이상의 충분한 길이
- 최소 2개 이상의 참고 문헌 (URL 포함)
- 마크다운 형식 (제목, 목록, 강조 등 활용)
- 과학적으로 정확한 정보 제공
- 한국어로 작성
"""

        # 답변 생성 프롬프트
        prompt = f"""# 질문: {question}

위 질문에 대해 근육 발달과 건강기능식품 전문가로서 답변해주세요. 
답변은 문제 정의, 핵심 내용, 과학적 근거, 복용 방법 및 주의사항, 결론 및 요약, 참고 문헌의 순서로 작성하세요.

각 섹션에는 다음 내용을 포함시켜야 합니다:
- 문제 정의: 질문의 배경과 중요성
- 핵심 내용: 주요 개념과 원리에 대한 설명
- 과학적 근거: 관련 연구 결과와 데이터
- 복용 방법 및 주의사항: 실제 적용에 필요한 지침
- 결론 및 요약: 핵심 내용 정리
- 참고 문헌: 최소 2개 이상의 신뢰할 만한 출처(URL 포함)

답변은 마크다운 형식으로 작성하고, 최소 1000자 이상이어야 합니다.
"""

        try:
            # 답변 생성
            answer = await self.client.generate(prompt, system_prompt, temperature)
            
            # 답변 검증
            if not answer or len(answer) < self.client.min_response_length:
                print(f"⚠️ 생성된 답변이 너무 짧습니다 ({len(answer) if answer else 0}자). 재시도합니다.")
                return await self.generate_answer(question, temperature)
            
            # 모든 필수 섹션이 포함되어 있는지 확인
            missing_sections = []
            for section in self.required_sections:
                if section not in answer and f"#{section}" not in answer and f"# {section}" not in answer:
                    missing_sections.append(section)
            
            # 참고 문헌 섹션 확인
            if "참고 문헌" in missing_sections:
                print("⚠️ 참고 문헌 섹션이 누락되었습니다. 강화된 답변을 생성합니다.")
                return await self.generate_enhanced_answer(question, answer)
            
            # URL 포함 여부 확인
            if "http" not in answer:
                print("⚠️ 답변에 URL이 포함되어 있지 않습니다. 참고 문헌을 보강합니다.")
                return await self.enhance_references(answer)
            
            return answer
            
        except Exception as e:
            print(f"답변 생성 중 오류 발생: {str(e)}")
            # 최소한의 기본 답변 생성
            return f"""# {question}

## 문제 정의
이 질문은 근육 발달과 건강기능식품에 관한 중요한 주제입니다.

## 핵심 내용
답변 생성 중 오류가 발생했습니다. 다시 시도해주세요.

## 참고 문헌
1. 한국건강기능식품협회 (https://www.khsa.or.kr/)
2. 식품의약품안전처 (https://www.mfds.go.kr/)
"""
    
    async def generate_enhanced_answer(self, question: str, partial_answer: str) -> str:
        """
        누락된 섹션을 보완하여 향상된 답변 생성
        
        Args:
            question: 원래 질문
            partial_answer: 일부 내용이 누락된 답변
            
        Returns:
            str: 향상된 답변
        """
        enhance_prompt = f"""다음 답변에 누락된 섹션을 추가하여 완성해주세요. 
특히 참고 문헌이 최소 2개 이상 포함되도록 하고, URL을 명시해주세요.

원래 질문: {question}

기존 답변:
{partial_answer}

누락된 섹션을 추가하고 완성된 답변을 제시해주세요. 
최종 답변은 문제 정의, 핵심 내용, 과학적 근거, 복용 방법 및 주의사항, 결론 및 요약, 참고 문헌의 
모든 섹션을 포함해야 합니다."""
        
        system_prompt = """당신은 근육 발달과 건강기능식품에 관한 전문가입니다. 
누락된 섹션을 식별하고 완성된 답변을 제공해주세요.
특히 참고 문헌에는 최소 2개 이상의 신뢰할 수 있는 출처와 URL을 포함시켜야 합니다."""

        try:
            enhanced_answer = await self.client.generate(enhance_prompt, system_prompt)
            return enhanced_answer
        except Exception as e:
            print(f"답변 개선 중 오류 발생: {str(e)}")
            return partial_answer
    
    async def enhance_references(self, answer: str) -> str:
        """
        참고 문헌 섹션에 URL을 추가하여 개선
        
        Args:
            answer: 참고 문헌에 URL이 없는 답변
            
        Returns:
            str: 참고 문헌이 개선된 답변
        """
        if "참고 문헌" not in answer and "# 참고 문헌" not in answer:
            return answer
            
        # 답변에서 참고 문헌 섹션 추출
        refs_section = answer.split("참고 문헌")[-1]
        
        # URL이 포함되어 있는지 확인
        if "http" in refs_section:
            return answer
        
        # 시스템 프롬프트
        system_prompt = """당신은 건강기능식품 연구 자료의 참고문헌을 개선하는 전문가입니다.
각 참고문헌 항목에 대해 실제 학술 URL을 검색하여 추가해야 합니다.
URL은 [텍스트](URL) 형식의 마크다운 링크로 제공하세요."""
        
        # 사용자 프롬프트
        prompt = f"""다음은 건강기능식품 관련 답변의 참고문헌 섹션입니다:

{refs_section}

이 참고문헌 항목들에 적절한 URL을 추가하여 개선된 참고문헌 섹션을 만들어주세요.
각 참고문헌에 DOI나 PubMed 링크 등을 포함해야 합니다."""
        
        try:
            # 개선된 참고문헌 생성
            improved_refs = await self.client.generate(prompt, system_prompt, temperature=0.3)
            
            # 원래 답변에서 참고문헌 섹션을 개선된 버전으로 교체
            before_refs = answer.split("참고 문헌")[0]
            return f"{before_refs}참고 문헌\n{improved_refs}"
            
        except Exception as e:
            print(f"참고문헌 개선 중 오류 발생: {str(e)}")
            return answer
            
    async def improve_answer(self, question: str, previous_answer: str, feedback: str) -> str:
        """
        이전 답변과 피드백을 기반으로 개선된 답변 생성
        
        Args:
            question: 원래 질문
            previous_answer: 이전 답변 내용
            feedback: 답변에 대한 피드백
            
        Returns:
            str: 개선된 답변
        """
        # 시스템 프롬프트
        system_prompt = """당신은 건강기능식품 연구에 관한 전문가로, 주어진 피드백을 바탕으로 이전 답변을 개선하는 역할을 맡고 있습니다.
피드백의 모든 요점을 충실히 반영하여 답변을 개선하되, 이전 답변의 정확한 부분과 구조는 유지하세요.

답변은 반드시 다음 구조를 유지해야 합니다:
1. 문제 정의
2. 핵심 내용 (이론, 개념, 원리)
3. 과학적 근거 (연구 결과, 데이터)
4. 복용 방법 및 주의사항
5. 결론 및 요약
6. 참고 문헌 (최소 2개 이상의 URL 포함)

개선 사항:
- 피드백에서 지적한 내용을 정확히 수정
- 과학적 근거를 강화 (최신 연구, 통계 추가)
- 참고문헌 보강 (최소 2개 이상 URL 포함)
- 논리 흐름 개선
- 한국어 가독성 향상"""
        
        # 사용자 프롬프트
        prompt = f"""# 질문
{question}

# 이전 답변
{previous_answer}

# 피드백
{feedback}

위 피드백을 반영하여 이전 답변을 개선한 새로운 답변을 작성해주세요. 
기존 답변의 구조를 유지하면서 피드백에서 제시한 모든 문제점을 해결하세요.
특히 과학적 근거와 참고문헌을 보강하고, 논리 흐름을 개선하세요.
최소 1000자 이상, 마크다운 형식으로 작성하세요."""
        
        try:
            # 개선된 답변 생성
            improved_answer = await self.client.generate(prompt, system_prompt, temperature=0.7)
            
            # 최소 길이 확인
            if not improved_answer or len(improved_answer) < self.client.min_response_length:
                print(f"⚠️ 개선된 답변이 너무 짧습니다 ({len(improved_answer) if improved_answer else 0}자). 재시도합니다.")
                return await self.improve_answer(question, previous_answer, feedback)
                
            # 참고 문헌 확인 및 개선
            if "참고 문헌" in improved_answer and "http" not in improved_answer:
                improved_answer = await self.enhance_references(improved_answer)
                
            return improved_answer
            
        except Exception as e:
            print(f"답변 개선 중 오류 발생: {str(e)}")
            return previous_answer  # 오류 발생 시 이전 답변 반환
            
    async def generate_alternative_answers(self, question: str, count: int = 2) -> List[str]:
        """
        동일 질문에 대한 여러 대체 답변 생성
        
        Args:
            question: 연구 질문
            count: 생성할 대체 답변 수
            
        Returns:
            List[str]: 생성된 대체 답변 목록
        """
        # 병렬로 여러 답변 생성
        prompts = []
        
        # 각기 다른 온도값 사용
        temperatures = [0.5 + 0.1 * i for i in range(count)]
        random.shuffle(temperatures)  # 다양성을 위한 셔플
        
        for temp in temperatures:
            prompts.append({
                "prompt": f"""# 질문: {question}

위 질문에 대해 근육 발달과 건강기능식품 전문가로서 답변해주세요.
답변은 다음 요소를 반드시 포함해야 합니다:
1. 문제 정의: 질문의 범위와 중요성 설명
2. 핵심 내용: 주요 개념과 원리에 대한 설명
3. 과학적 근거: 관련 연구 결과와 데이터
4. 복용 방법 및 주의사항: 실질적인 적용 정보
5. 결론 및 요약: 핵심 요점 정리
6. 참고 문헌: 최소 2개 이상의 신뢰할 수 있는 출처와 URL

답변은 마크다운 형식으로 작성하고, 최소 1000자 이상이어야 합니다.""",
                "system": """당신은 근육 발달과 건강기능식품에 관한 전문가입니다.
과학적으로 정확하고 구체적인 정보를 제공하며, 참고 문헌을 통해 신뢰성을 높여주세요.
한국어로 답변하고, 마크다운 형식으로 구조적인 답변을 작성해주세요.""",
                "temperature": temp
            })
            
        # 병렬 실행
        try:
            results = await self.client.generate_parallel(prompts)
            
            # 결과 필터링 (너무 짧은 답변 제외)
            valid_answers = [ans for ans in results if isinstance(ans, str) and len(ans) >= self.client.min_response_length]
            
            if len(valid_answers) < count:
                print(f"⚠️ 대체 답변 중 일부가 유효하지 않습니다 ({len(valid_answers)}/{count})")
            
            return valid_answers
            
        except Exception as e:
            print(f"대체 답변 생성 중 오류 발생: {str(e)}")
            return []
            
    async def research_question(self, question: str) -> str:
        """
        단일 질문에 대한 초기 연구 수행
        
        Args:
            question: 연구할 질문
            
        Returns:
            구조화된 연구 결과 (마크다운 형식)
        """
        # 시스템 프롬프트 설정
        system_prompt = (
            "당신은 스포츠 영양학 전문가입니다. "
            "근육 성장과 회복에 관한 건강기능식품에 대한 질문에 과학적 근거를 바탕으로 정확하고 상세하게 답변해주세요.\n\n"
            "다음 사항을 반드시 지켜주세요:\n"
            "1. 모든 답변은 과학적 연구 결과를 기반으로 해야 합니다.\n"
            "2. 구체적인 수치와 연구 결과를 인용할 때는 출처를 명시해주세요.\n"
            "3. 마크다운 형식을 사용하여 가독성을 높여주세요.\n"
            "4. 전문 용어를 사용할 때는 초보자도 이해할 수 있도록 설명을 추가해주세요."
        )
        
        # 사용자 프롬프트 설정
        prompt = (
            f"{question}\n\n"
            "위 질문에 대해 체계적이고 자세한 답변을 작성해주세요. 다음의 구조를 따라주세요:\n\n"
            "## 1. 문제 정의\n"
            "- 질문의 핵심 내용과 중요성 설명\n\n"
            "## 2. 핵심 내용\n"
            "- 주요 개념과 이론 설명\n"
            "- 관련된 생리학적/생화학적 메커니즘\n\n"
            "## 3. 과학적 근거\n"
            "- 최신 연구 결과 요약 (연구명, 참여자 수, 주요 결과)\n"
            "- 메타분석이 있는 경우 그 결과 포함\n\n"
            "## 4. 복용 방법 및 주의사항\n"
            "- 권장 용량과 복용 시기\n"
            "- 잠재적 부작용과 주의사항\n\n"
            "## 5. 결론 및 요약\n"
            "- 주요 내용 요약\n"
            "- 실용적인 조언\n\n"
            "## 참고 문헌\n"
            "- 인용한 연구 및 자료 목록 (저자, 연도, 저널명, DOI/링크)\n\n"
            "답변은 최소 1500자 이상으로 자세히 작성해주시고, "
            "마크다운 형식을 사용해 구조화해주세요. "
            "과학적 연구 결과를 인용할 때는 반드시 출처를 명시해주세요."
        )
        
        try:
            return await self.client.generate(prompt, system_prompt=system_prompt)
        except Exception as e:
            print(f"연구 질문 처리 중 오류 발생: {str(e)}")
            return f"오류: {str(e)}"


# 모듈 직접 실행 시 테스트
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='답변 생성 모듈 테스트')
    parser.add_argument('--question', '-q', type=str, default="근육 발달에 가장 중요한 아미노산은 무엇이며, 어떤 식품에 많이 함유되어 있나요?",
                       help='연구 질문')
    parser.add_argument('--alternatives', '-a', type=int, default=0,
                       help='생성할 대체 답변 수 (기본값: 0)')
    parser.add_argument('--temperature', '-t', type=float, default=0.7,
                       help='생성 온도 (0.1~1.0, 기본값: 0.7)')
    
    args = parser.parse_args()
    
    async def test():
        # 생성기 초기화
        generator = AnswerGenerator()
        
        # API 가용성 확인
        client_status = await generator.client.check_availability()
        print(f"Ollama API 상태: {client_status['status']}")
        
        if client_status['status'] != 'available':
            print("❌ Ollama API를 사용할 수 없습니다. 서버가 실행 중인지 확인하세요.")
            return
        
        print(f"\n📝 질문: {args.question}")
        
        # 답변 생성
        print("\n🧠 답변 생성 중...")
        answer = await generator.generate_answer(args.question, args.temperature)
        
        print(f"\n=== 생성된 답변 ===")
        print(answer)
        
        if len(answer) < generator.client.min_response_length:
            print(f"⚠️ 생성된 답변이 너무 짧습니다: {len(answer)}자")
        
        # 대체 답변 생성
        if args.alternatives > 0:
            print(f"\n🔄 대체 답변 {args.alternatives}개 생성 중...")
            alternatives = await generator.generate_alternative_answers(
                args.question, args.alternatives
            )
            
            for i, alt in enumerate(alternatives):
                print(f"\n=== 대체 답변 #{i+1} ===")
                print(alt)
                
    asyncio.run(test())
