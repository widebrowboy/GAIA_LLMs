#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
근육 관련 건강기능식품 챗봇 테스트 모듈입니다.

이 모듈은 Ollama LLM을 활용한 챗봇의 기능을 테스트합니다.
"""

from typing import Dict, List, Optional, Any
import asyncio
import json
from datetime import datetime
import aiohttp
import re


class ChatbotTester:
    """챗봇 테스트를 관리하는 클래스입니다."""

    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        """
        챗봇 테스터를 초기화합니다.

        Args:
            base_url (str): Ollama API 기본 URL
        """
        self.base_url = base_url
        self.prompt_template = """
당신은 근육 관련 건강기능식품 전문가입니다. 
다음 질문에 대해 과학적 근거를 바탕으로 상세하게 답변해주세요.

답변은 반드시 다음 형식을 따라주세요:

1. 핵심 내용
   - 주요 개념과 원리
   - 작용 메커니즘
   - 중요 포인트

2. 과학적 근거
   - 연구 결과
   - 임상 데이터
   - 전문가 의견

3. 권장사항
   - 복용 방법
   - 주의사항
   - 최적의 시기

답변 시 다음 사항을 반드시 포함해주세요:
- 구체적인 수치와 데이터
- 명확한 시간/용량 정보
- 과학적 용어의 정확한 사용

질문: {question}
"""
        self.test_cases: List[Dict[str, Any]] = [
            {
                "id": "TC001",
                "question": "프로틴 파우더는 언제 먹는 것이 가장 효과적인가요?",
                "expected_keywords": {
                    "primary": ["운동 후", "30분", "단백질 합성", "근육 회복"],
                    "synonyms": {
                        "운동 후": ["트레이닝 후", "workout 후", "exercise 후"],
                        "30분": ["30분 이내", "30분 안에", "half hour"],
                        "단백질 합성": ["protein synthesis", "근육 단백질 합성"],
                        "근육 회복": ["근육 회복력", "muscle recovery"]
                    }
                }
            },
            {
                "id": "TC002",
                "question": "BCAA의 주요 효과는 무엇인가요?",
                "expected_keywords": {
                    "primary": ["근육 회복", "통증 감소", "분기쇄 아미노산", "단백질 합성"],
                    "synonyms": {
                        "근육 회복": ["근육 회복력", "muscle recovery"],
                        "통증 감소": ["근육통 감소", "pain reduction"],
                        "분기쇄 아미노산": ["BCAA", "branched-chain amino acids"],
                        "단백질 합성": ["protein synthesis", "근육 단백질 합성"]
                    }
                }
            },
            {
                "id": "TC003",
                "question": "크레아틴의 권장 섭취량은 얼마인가요?",
                "expected_keywords": {
                    "primary": ["3-5g", "로딩", "유지", "근육 성장"],
                    "synonyms": {
                        "3-5g": ["3그램", "5그램", "3 to 5 grams"],
                        "로딩": ["로딩 기간", "loading phase"],
                        "유지": ["유지 기간", "maintenance"],
                        "근육 성장": ["근육량 증가", "muscle growth"]
                    }
                }
            },
            {
                "id": "TC004",
                "question": "글루타민의 주요 효과와 복용 시기는 언제인가요?",
                "expected_keywords": {
                    "primary": ["면역력", "회복", "취침 전", "운동 후"],
                    "synonyms": {
                        "면역력": ["면역 기능", "immune function"],
                        "회복": ["회복력", "recovery"],
                        "취침 전": ["취침 직전", "before sleep"],
                        "운동 후": ["트레이닝 후", "post-workout"]
                    }
                }
            },
            {
                "id": "TC005",
                "question": "오메가3와 단백질 보충제를 함께 복용해도 될까요?",
                "expected_keywords": {
                    "primary": ["상호작용", "흡수", "항염증", "근육 회복"],
                    "synonyms": {
                        "상호작용": ["시너지", "interaction"],
                        "흡수": ["흡수율", "absorption"],
                        "항염증": ["항염증 효과", "anti-inflammatory"],
                        "근육 회복": ["근육 회복력", "muscle recovery"]
                    }
                }
            },
        ]

    def _normalize_text(self, text: str) -> str:
        """
        텍스트를 정규화합니다.

        Args:
            text (str): 정규화할 텍스트

        Returns:
            str: 정규화된 텍스트
        """
        # 소문자 변환
        text = text.lower()
        # 특수문자 제거
        text = re.sub(r'[^\w\s]', ' ', text)
        # 여러 공백을 하나로
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _check_keyword_match(self, text: str, keyword: str, synonyms: List[str]) -> bool:
        """
        키워드와 동의어 매칭을 확인합니다.

        Args:
            text (str): 검사할 텍스트
            keyword (str): 기본 키워드
            synonyms (List[str]): 동의어 목록

        Returns:
            bool: 매칭 여부
        """
        normalized_text = self._normalize_text(text)
        normalized_keyword = self._normalize_text(keyword)
        normalized_synonyms = [self._normalize_text(syn) for syn in synonyms]
        
        return (normalized_keyword in normalized_text or 
                any(syn in normalized_text for syn in normalized_synonyms))

    async def test_chatbot(self, question: str) -> Dict[str, Any]:
        """
        챗봇에 질문을 보내고 응답을 받습니다.

        Args:
            question (str): 테스트할 질문

        Returns:
            Dict[str, Any]: 챗봇의 응답과 메타데이터
        """
        formatted_prompt = self.prompt_template.format(question=question)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": "gemma3:latest",
                    "prompt": formatted_prompt,
                    "stream": False,
                    "options": {
                        "num_gpu": 99,
                        "num_thread": 8,
                        "f16_kv": True,
                        "mirostat": 2,
                        "temperature": 0.7,
                        "top_p": 0.9,
                    },
                },
            ) as response:
                result = await response.json()
                return {
                    "question": question,
                    "response": result.get("response", ""),
                    "timestamp": datetime.now().isoformat(),
                }

    async def run_test_suite(self) -> List[Dict[str, Any]]:
        """
        전체 테스트 스위트를 실행합니다.

        Returns:
            List[Dict[str, Any]]: 테스트 결과 목록
        """
        results = []
        for test_case in self.test_cases:
            result = await self.test_chatbot(test_case["question"])
            result["test_case_id"] = test_case["id"]
            result["expected_keywords"] = test_case["expected_keywords"]
            results.append(result)
        return results

    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        테스트 결과를 분석합니다.

        Args:
            results (List[Dict[str, Any]]): 테스트 결과 목록

        Returns:
            Dict[str, Any]: 분석 결과
        """
        analysis = {
            "total_tests": len(results),
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": [],
        }

        for result in results:
            response_text = result["response"]
            expected_keywords = result["expected_keywords"]
            
            found_keywords = []
            missing_keywords = []
            
            for keyword in expected_keywords["primary"]:
                synonyms = expected_keywords["synonyms"].get(keyword, [])
                if self._check_keyword_match(response_text, keyword, synonyms):
                    found_keywords.append(keyword)
                else:
                    missing_keywords.append(keyword)
            
            matching_rate = len(found_keywords) / len(expected_keywords["primary"]) * 100
            
            test_result = {
                "test_case_id": result["test_case_id"],
                "question": result["question"],
                "keywords_found": found_keywords,
                "keywords_missing": missing_keywords,
                "matching_rate": matching_rate,
                "passed": matching_rate >= 50.0,
            }
            
            if test_result["passed"]:
                analysis["passed_tests"] += 1
            else:
                analysis["failed_tests"] += 1
            
            analysis["test_details"].append(test_result)

        return analysis


async def main() -> None:
    """메인 실행 함수입니다."""
    tester = ChatbotTester()
    
    print("챗봇 테스트를 시작합니다...")
    results = await tester.run_test_suite()
    analysis = tester.analyze_results(results)
    
    print("\n테스트 결과 요약:")
    print(f"총 테스트 수: {analysis['total_tests']}")
    print(f"통과한 테스트: {analysis['passed_tests']}")
    print(f"실패한 테스트: {analysis['failed_tests']}")
    
    print("\n상세 테스트 결과:")
    for detail in analysis["test_details"]:
        print(f"\n테스트 케이스 {detail['test_case_id']}:")
        print(f"질문: {detail['question']}")
        print(f"발견된 키워드: {', '.join(detail['keywords_found'])}")
        print(f"누락된 키워드: {', '.join(detail['keywords_missing'])}")
        print(f"키워드 매칭률: {detail['matching_rate']:.1f}%")
        print(f"결과: {'통과' if detail['passed'] else '실패'}")


if __name__ == "__main__":
    asyncio.run(main()) 