#!/usr/bin/env python3
"""
답변 평가 및 피드백 모듈
생성된 답변을 평가하고 개선 제안을 제공
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from ..api.ollama_client import OllamaClient

class AnswerEvaluator:
    """
    건강기능식품 답변 평가 및 피드백 클래스
    답변 품질, 정확성, 과학적 근거 등을 평가
    """
    
    def __init__(self, 
                client: Optional[OllamaClient] = None,
                min_score: float = 7.0,
                evaluation_criteria: Optional[List[str]] = None):
        """
        답변 평가기 초기화
        
        Args:
            client: OllamaClient 인스턴스 (없으면 새로 생성)
            min_score: 최소 품질 점수 (0-10)
            evaluation_criteria: 평가 기준 목록
        """
        # Ollama 클라이언트 설정
        self.client = client or OllamaClient()
        self.min_score = min_score
        
        # 기본 평가 기준
        self.criteria = evaluation_criteria or [
            "문제 정의의 명확성 (1-10)",
            "핵심 내용의 충실성 (1-10)",
            "과학적 근거의 신뢰성 (1-10)",
            "복용 방법 및 주의사항 설명 (1-10)",
            "참고 문헌 충분성 (최소 2개 이상, 1-10)",
            "전체 글자 수 충족 (최소 1000자 이상, 1-10)",
            "결론의 명확성 (1-10)"
        ]
    
    async def evaluate_answer(self, question: str, answer: str) -> Dict[str, Any]:
        """
        답변 품질 평가
        
        Args:
            question: 원래 질문
            answer: 평가할 답변
            
        Returns:
            Dict[str, Any]: 평가 결과 및 점수
        """
        # 평가 프롬프트 구성
        eval_prompt = f"""
건강기능식품 답변에 대한 품질을 평가해주세요. 다음 기준에 따라 1-10점 척도로 점수를 매기고 
구체적인 개선 제안을 제시해주세요.

[원본 질문]
{question}

[평가할 답변]
{answer}

[평가 기준]
{', '.join(self.criteria)}

각 항목별로 점수와 이유를 구체적으로 설명해주세요. 
그리고 전체 평균 점수와 개선할 부분에 대해 구체적으로 제안해주세요.
응답은 JSON 형식으로 반환해주세요.
"""

        # 시스템 프롬프트
        sys_prompt = "당신은 전문적인 건강기능식품 답변 평가 전문가입니다. 객관적이고 공정하게 평가해주세요."
        
        try:
            # 평가 요청
            eval_result_str = await self.client.generate(eval_prompt, sys_prompt)
            
            # JSON 추출 시도
            try:
                # JSON 데이터 추출 (마크다운 코드 블록 또는 일반 텍스트에서)
                import re
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```|({[\s\S]*})', eval_result_str)
                
                if json_match:
                    json_str = json_match.group(1) or json_match.group(2)
                    eval_data = json.loads(json_str)
                else:
                    # JSON 형식이 아닌 경우 텍스트 응답 그대로 반환
                    eval_data = {
                        "raw_evaluation": eval_result_str,
                        "error": "평가 결과를 JSON 형식으로 파싱할 수 없습니다."
                    }
            except json.JSONDecodeError:
                eval_data = {
                    "raw_evaluation": eval_result_str,
                    "error": "JSON 디코딩 오류가 발생했습니다."
                }
                
            return eval_data
            
        except Exception as e:
            return {
                "error": f"평가 중 오류 발생: {str(e)}",
                "score": 0.0
            }
    
    async def generate_improved_answer(self, 
                                     question: str, 
                                     original_answer: str, 
                                     evaluation: Dict[str, Any]) -> str:
        """
        평가 결과를 기반으로 개선된 답변 생성
        
        Args:
            question: 원래 질문
            original_answer: 원래 답변
            evaluation: 평가 결과
            
        Returns:
            str: 개선된 답변
        """
        # 개선 프롬프트 구성
        improvement_prompt = f"""
다음 건강기능식품 관련 질문과 답변, 그리고 평가 결과를 바탕으로 개선된 답변을 생성해주세요.

[질문]
{question}

[기존 답변]
{original_answer}

[평가 결과 및 개선 제안]
{json.dumps(evaluation, ensure_ascii=False, indent=2)}

위 평가를 반영하여 더 나은 답변을 작성해주세요. 
특히 다음 요구사항을 반드시 충족해야 합니다:
1. 최소 1000자 이상의 충분한 내용
2. 최소 2개 이상의 구체적인 참고문헌(URL 포함)
3. 문제 정의, 핵심 내용, 과학적 근거, 복용 방법 및 주의사항, 결론 및 요약, 참고 문헌 섹션 포함
4. 마크다운 형식 사용(제목, 목록, 강조 등)
5. 평가에서 지적된 모든 부분 개선

답변은 한국어로 작성해주세요.
"""

        # 시스템 프롬프트
        sys_prompt = """당신은 근육 관련 건강기능식품 전문가입니다. 
과학적이고 정확한 정보를 제공하며, 근거 기반의 상세한 답변을 제공합니다. 
마크다운 형식을 사용하여 구조화된 답변을 작성해주세요."""
        
        try:
            # 개선된 답변 생성
            improved_answer = await self.client.generate(improvement_prompt, sys_prompt)
            return improved_answer
            
        except Exception as e:
            return f"개선된 답변 생성 중 오류 발생: {str(e)}"
            
    async def feedback_loop(self, 
                           question: str, 
                           initial_answer: str, 
                           depth: int = 2, 
                           width: int = 2) -> Dict[str, Any]:
        """
        피드백 루프를 통한 답변 개선
        
        Args:
            question: 원래 질문
            initial_answer: 초기 답변
            depth: 피드백 루프 깊이 (몇 번 반복할지)
            width: 피드백 루프 너비 (각 반복에서 몇 개의 대체 답변 생성)
            
        Returns:
            Dict[str, Any]: 최종 답변, 평가 이력, 메타데이터
        """
        current_answer = initial_answer
        best_answer = initial_answer
        best_score = 0.0
        evaluation_history = []
        
        print(f"피드백 루프 시작 (깊이: {depth}, 너비: {width})")
        
        for d in range(depth):
            print(f"\n[{d+1}/{depth}] 피드백 루프 진행 중...")
            
            # 현재 답변 평가
            evaluation = await self.evaluate_answer(question, current_answer)
            
            # 평균 점수 계산
            avg_score = 0.0
            if isinstance(evaluation, dict):
                if "average_score" in evaluation:
                    avg_score = float(evaluation["average_score"])
                elif "score" in evaluation:
                    avg_score = float(evaluation["score"])
            
            print(f"  현재 답변 평가 점수: {avg_score:.2f}/10.0")
            evaluation_history.append({"loop": d+1, "evaluation": evaluation})
            
            # 최고 점수 갱신
            if avg_score > best_score:
                best_score = avg_score
                best_answer = current_answer
                
            # 목표 점수에 도달했으면 조기 종료
            if avg_score >= 9.0:
                print(f"  ✓ 목표 점수 달성! ({avg_score:.2f}/10.0)")
                break
                
            # 대체 답변 병렬 생성
            alternatives = []
            alt_tasks = []
            
            print(f"  대체 답변 {width}개 생성 중...")
            for w in range(width):
                # 대체 답변 생성 작업 생성
                task = asyncio.create_task(
                    self.generate_improved_answer(question, current_answer, evaluation)
                )
                alt_tasks.append(task)
            
            # 모든 대체 답변 대기
            alt_results = await asyncio.gather(*alt_tasks, return_exceptions=True)
            
            # 성공한 결과만 필터링
            for i, result in enumerate(alt_results):
                if isinstance(result, Exception):
                    print(f"  ⚠️ 대체 답변 #{i+1} 생성 실패: {str(result)}")
                else:
                    alternatives.append(result)
            
            if not alternatives:
                print("  ⚠️ 모든 대체 답변 생성이 실패했습니다. 현재 답변 유지.")
                continue
                
            # 대체 답변 평가 및 최고 답변 선택
            alt_scores = []
            alt_eval_tasks = []
            
            print(f"  {len(alternatives)}개 대체 답변 평가 중...")
            for alt in alternatives:
                # 평가 작업 생성
                task = asyncio.create_task(
                    self.evaluate_answer(question, alt)
                )
                alt_eval_tasks.append(task)
                
            # 모든 평가 대기
            alt_evaluations = await asyncio.gather(*alt_eval_tasks, return_exceptions=True)
            
            # 평가 점수 추출
            for i, eval_result in enumerate(alt_evaluations):
                if isinstance(eval_result, Exception):
                    print(f"  ⚠️ 대체 답변 #{i+1} 평가 실패: {str(eval_result)}")
                    alt_scores.append(0.0)
                else:
                    score = 0.0
                    if isinstance(eval_result, dict):
                        if "average_score" in eval_result:
                            score = float(eval_result["average_score"])
                        elif "score" in eval_result:
                            score = float(eval_result["score"])
                    alt_scores.append(score)
                    print(f"  대체 답변 #{i+1} 점수: {score:.2f}/10.0")
            
            # 최고 점수 대체 답변 선택
            if alt_scores:
                best_alt_idx = alt_scores.index(max(alt_scores))
                best_alt_score = alt_scores[best_alt_idx]
                
                if best_alt_score > avg_score:
                    print(f"  ✓ 개선된 답변 선택 (점수: {best_alt_score:.2f} > {avg_score:.2f})")
                    current_answer = alternatives[best_alt_idx]
                    
                    # 전체 최고 점수 갱신
                    if best_alt_score > best_score:
                        best_score = best_alt_score
                        best_answer = current_answer
                else:
                    print(f"  ✗ 대체 답변이 개선되지 않음 (최고 점수: {best_alt_score:.2f} <= {avg_score:.2f})")
        
        # 최종 결과 반환
        return {
            "final_answer": best_answer,
            "best_score": best_score,
            "evaluation_history": evaluation_history,
            "feedback_loops": len(evaluation_history),
            "initial_answer": initial_answer
        }


# 모듈 직접 실행 시 테스트
if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='답변 평가 및 개선 모듈 테스트')
    parser.add_argument('--question', '-q', type=str, default="근육 발달을 위한 최적의 단백질 섭취량은?",
                       help='평가할 질문')
    parser.add_argument('--answer', '-a', type=str, default=None,
                       help='평가할 답변 (없으면 기본 예시 사용)')
    parser.add_argument('--depth', '-d', type=int, default=1,
                       help='피드백 루프 깊이 (기본값: 1)')
    parser.add_argument('--width', '-w', type=int, default=1,
                       help='피드백 루프 너비 (기본값: 1)')
    
    args = parser.parse_args()
    
    # 기본 답변 예시
    default_answer = """
# 근육 발달을 위한 단백질 섭취량

단백질은 근육 발달에 중요합니다. 보통 체중 1kg당 1.6-2.2g의 단백질이 권장됩니다.
운동 후 20-30g의 단백질을 섭취하는 것이 좋습니다.

참고문헌:
1. 건강기능식품학회
"""
    
    answer_to_evaluate = args.answer or default_answer
    
    async def run_test():
        # 평가기 생성
        evaluator = AnswerEvaluator()
        
        # API 가용성 확인
        status = await evaluator.client.check_availability()
        print(f"Ollama API 상태: {status['status']}")
        
        if status['status'] != 'available':
            print("Ollama API를 사용할 수 없습니다. 서버가 실행 중인지 확인하세요.")
            sys.exit(1)
            
        # 답변 평가
        print("\n=== 답변 평가 중 ===")
        eval_result = await evaluator.evaluate_answer(args.question, answer_to_evaluate)
        print(f"평가 결과: {json.dumps(eval_result, ensure_ascii=False, indent=2)}")
        
        if args.depth > 0:
            # 피드백 루프 실행
            print(f"\n=== 피드백 루프 실행 (깊이: {args.depth}, 너비: {args.width}) ===")
            feedback_result = await evaluator.feedback_loop(
                args.question, answer_to_evaluate, args.depth, args.width
            )
            
            print(f"\n=== 최종 개선 답변 (점수: {feedback_result['best_score']:.2f}/10) ===")
            print(feedback_result['final_answer'])
    
    asyncio.run(run_test())