#!/usr/bin/env python3
"""
질문 처리 모듈
근육 관련 건강기능식품 연구 질문 로드 및 전처리
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from ..api.ollama_client import OllamaClient

class QuestionHandler:
    """
    건강기능식품 연구 질문 처리 클래스
    파일에서 질문 로드 및 질문 개선/확장 기능 제공
    """
    
    def __init__(self, client: Optional[OllamaClient] = None):
        """
        질문 처리기 초기화
        
        Args:
            client: OllamaClient 인스턴스 (없으면 새로 생성)
        """
        self.client = client or OllamaClient()
    
    async def load_questions_from_file(self, file_path: str) -> List[str]:
        """
        파일에서 질문 목록 로드
        
        Args:
            file_path: 질문 파일 경로 (JSON 또는 텍스트)
            
        Returns:
            List[str]: 질문 목록
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"질문 파일을 찾을 수 없습니다: {file_path}")
            
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.json':
                # JSON 파일 형식 (질문 목록 또는 객체 배열)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    # 문자열 목록이거나 객체 목록인지 확인
                    if all(isinstance(item, str) for item in data):
                        return data
                    elif all(isinstance(item, dict) for item in data):
                        # 'question' 키가 있는지 확인
                        questions = []
                        for item in data:
                            if 'question' in item and isinstance(item['question'], str):
                                questions.append(item['question'])
                            else:
                                print(f"경고: 항목에 'question' 키가 없습니다: {item}")
                        return questions
                elif isinstance(data, dict) and 'questions' in data:
                    # {'questions': [...]} 형식
                    return data['questions']
                
                # 알 수 없는 JSON 형식
                raise ValueError(f"지원되지 않는 JSON 형식입니다: {data}")
                
            else:
                # 일반 텍스트 파일 (한 줄에 하나의 질문)
                with open(file_path, 'r', encoding='utf-8') as f:
                    questions = [line.strip() for line in f if line.strip()]
                return questions
                
        except Exception as e:
            print(f"질문 파일 로드 중 오류 발생: {str(e)}")
            # 기본 질문 반환
            return [
                "근육 발달에 가장 중요한 아미노산은 무엇이며, 어떤 식품에 많이 함유되어 있나요?",
                "운동 후 단백질 섭취 타이밍이 중요한 이유는 무엇인가요?",
                "크레아틴 모노하이드레이트의 효능과 적정 복용량은 어떻게 되나요?"
            ]
    
    async def enhance_question(self, question: str) -> str:
        """
        질문 개선 및 정교화
        
        Args:
            question: 원본 질문
            
        Returns:
            str: 개선된 질문
        """
        enhance_prompt = f"""
다음 근육 건강기능식품 관련 질문을 더 정확하고 구체적인 형태로 개선해주세요.
질문에 과학적 용어와 맥락을 추가하고, 근육 관련 핵심 개념을 명확히 해주세요.
주제의 특정 측면을 지나치게 확장하지 말고, 원래 질문의 의도는 유지해주세요.

원본 질문: {question}

개선된 질문:"""

        system_prompt = "당신은 전문적인 스포츠 영양학 및 근육생리학 전문가입니다. 정확하고 과학적인 표현을 사용해주세요."
        
        try:
            enhanced = await self.client.generate(enhance_prompt, system_prompt)
            if enhanced and len(enhanced) > len(question):
                return enhanced.strip()
            return question  # 개선 실패시 원본 반환
        except Exception as e:
            print(f"질문 개선 중 오류 발생: {str(e)}")
            return question
    
    async def generate_related_questions(self, question: str, count: int = 3) -> List[str]:
        """
        관련 질문 생성
        
        Args:
            question: 기준 질문
            count: 생성할 관련 질문 수
            
        Returns:
            List[str]: 관련 질문 목록
        """
        related_prompt = f"""
다음 근육 건강기능식품 질문에 대해, 이 주제를 더 깊이 탐구하는 {count}개의 관련 후속 질문을 생성해주세요.
생성된 질문은 원본 질문과 직접적으로 관련이 있어야 하며, 과학적이고 구체적이어야 합니다.

원본 질문: {question}

관련 질문들:
1."""

        system_prompt = "당신은 근육 건강기능식품 전문가입니다. 주제를 깊이 탐구하는 후속 질문을 생성해주세요."
        
        try:
            related = await self.client.generate(related_prompt, system_prompt)
            # 숫자로 시작하는 줄 파싱
            import re
            questions = re.findall(r'^\d+\.?\s*(.*?)$', related, re.MULTILINE)
            
            # 최대 개수 제한
            result = [q.strip() for q in questions if q.strip()][:count]
            
            # 결과가 없으면 빈 목록 반환
            return result if result else []
            
        except Exception as e:
            print(f"관련 질문 생성 중 오류 발생: {str(e)}")
            return []


# 모듈 직접 실행 시 테스트
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='연구 질문 처리 모듈 테스트')
    parser.add_argument('--file', '-f', type=str, default=None,
                       help='질문 파일 경로 (JSON 또는 텍스트)')
    parser.add_argument('--question', '-q', type=str, default=None,
                       help='개선할 개별 질문')
    parser.add_argument('--related', '-r', action='store_true',
                       help='관련 질문 생성')
    parser.add_argument('--count', '-c', type=int, default=3,
                       help='생성할 관련 질문 수')
    
    args = parser.parse_args()
    
    async def test():
        handler = QuestionHandler()
        
        # API 가용성 확인
        client_status = await handler.client.check_availability()
        print(f"Ollama API 상태: {client_status['status']}")
        
        if client_status['status'] != 'available':
            print("❌ Ollama API를 사용할 수 없습니다. 서버가 실행 중인지 확인하세요.")
            return
        
        # 파일에서 질문 로드
        if args.file:
            print(f"\n📝 파일에서 질문 로드: {args.file}")
            try:
                questions = await handler.load_questions_from_file(args.file)
                print(f"로드된 질문 수: {len(questions)}")
                for i, q in enumerate(questions):
                    print(f"{i+1}. {q}")
            except Exception as e:
                print(f"❌ 오류 발생: {str(e)}")
        
        # 질문 개선
        if args.question:
            print(f"\n🔍 질문 개선 중...")
            print(f"원본 질문: {args.question}")
            
            enhanced = await handler.enhance_question(args.question)
            print(f"개선된 질문: {enhanced}")
            
            # 관련 질문 생성
            if args.related:
                print(f"\n🔄 관련 질문 생성 중...")
                related_questions = await handler.generate_related_questions(args.question, args.count)
                
                if related_questions:
                    print(f"생성된 관련 질문:")
                    for i, q in enumerate(related_questions):
                        print(f"{i+1}. {q}")
                else:
                    print("관련 질문을 생성할 수 없습니다.")
        
    asyncio.run(test())
