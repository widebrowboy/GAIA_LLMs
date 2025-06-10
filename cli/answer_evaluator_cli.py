#!/usr/bin/env python3
"""
답변 평가기 CLI 도구
AnswerEvaluator 모듈을 위한 독립적인 명령행 인터페이스
"""

import os
import sys
import json
import asyncio
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

# 상위 디렉토리를 모듈 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 모듈 임포트
from src.api.ollama_client import OllamaClient
from src.feedback.answer_evaluator import AnswerEvaluator


async def evaluate_answer(args):
    """
    질문과 답변을 평가
    """
    try:
        # 입력 확인
        question = args.question
        
        if args.answer:
            # 직접 입력된 답변 사용
            answer = args.answer
        elif args.file:
            # 파일에서 답변 읽기
            if not os.path.exists(args.file):
                print(f"❌ 파일을 찾을 수 없습니다: {args.file}")
                return 1
            with open(args.file, 'r', encoding='utf-8') as f:
                answer = f.read()
        else:
            print("❌ 답변 또는 답변이 포함된 파일이 필요합니다")
            return 1
        
        # 시작 메시지 출력
        print(f"📊 답변 평가 시작:")
        print(f"- 질문: '{question}'")
        print(f"- 답변 길이: {len(answer)} 자")
        
        # 클라이언트 초기화
        client = OllamaClient(
            model=args.model,
            temperature=args.temperature
        )
        
        # API 가용성 확인
        status = await client.check_availability()
        if status["status"] != "available":
            print(f"❌ Ollama API를 사용할 수 없습니다: {status.get('error', '알 수 없는 오류')}")
            return 1
        
        print(f"🚀 {status.get('current_model', client.model)} 모델 사용 중...")
        
        # 평가기 초기화 및 평가 수행
        evaluator = AnswerEvaluator(client)
        
        start_time = datetime.now()
        
        if args.feedback:
            # 피드백 루프 실행
            print(f"🔄 피드백 루프 실행 중 (깊이: {args.depth}, 너비: {args.width})...")
            result = await evaluator.feedback_loop(
                question=question,
                initial_answer=answer,
                depth=args.depth,
                width=args.width
            )
            elapsed = (datetime.now() - start_time).total_seconds()
            
            # 결과 출력
            print(f"\n✅ 피드백 루프 완료 (소요 시간: {elapsed:.1f}초)")
            print(f"📈 최종 점수: {result.get('best_score', 'N/A')}/10")
            print(f"🔄 피드백 루프: {result.get('feedback_loops', 'N/A')}회")
            
            # 개선된 답변 출력
            if args.show_result:
                improved_answer = result.get("final_answer", "")
                print("\n===== 개선된 답변 (처음 500자) =====\n")
                print(improved_answer[:500] + "..." if len(improved_answer) > 500 else improved_answer)
            
            # 결과 저장
            if args.output:
                output_file = args.output
                dir_path = os.path.dirname(output_file) if os.path.dirname(output_file) else '.'
                os.makedirs(dir_path, exist_ok=True)
                
                if output_file.endswith('.json'):
                    # JSON 형식으로 저장
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                else:
                    # 텍스트 형식으로 개선된 답변만 저장
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(result.get("final_answer", ""))
                
                print(f"📁 결과를 '{output_file}' 파일로 저장했습니다.")
        
        else:
            # 단순 평가만 수행
            print("🔍 답변 평가 중...")
            evaluation = await evaluator.evaluate_answer(question, answer)
            elapsed = (datetime.now() - start_time).total_seconds()
            
            # 결과 출력
            print(f"\n✅ 평가 완료 (소요 시간: {elapsed:.1f}초)")
            print(f"📊 총점: {evaluation.get('overall_score', 'N/A')}/10")
            
            # 세부 평가 항목 출력
            if "criteria_scores" in evaluation:
                print("\n===== 평가 세부 항목 =====")
                for criterion, score in evaluation["criteria_scores"].items():
                    print(f"- {criterion}: {score}/10")
            
            # 개선 제안 출력
            if "improvement_suggestions" in evaluation and args.show_result:
                print("\n===== 개선 제안 =====")
                print(evaluation["improvement_suggestions"])
            
            # 결과 저장
            if args.output:
                output_file = args.output
                dir_path = os.path.dirname(output_file) if os.path.dirname(output_file) else '.'
                os.makedirs(dir_path, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(evaluation, f, ensure_ascii=False, indent=2)
                
                print(f"📁 평가 결과를 '{output_file}' 파일로 저장했습니다.")
        
        return 0
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return 1


async def main():
    parser = argparse.ArgumentParser(
        description='답변 평가기 CLI 도구',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # 필수 인자
    parser.add_argument('question', type=str, help='답변을 평가할 질문')
    
    # 답변 입력 방식 (둘 중 하나 필요)
    input_group = parser.add_argument_group('답변 입력 옵션 (하나를 선택)')
    input_ex = input_group.add_mutually_exclusive_group(required=True)
    input_ex.add_argument('--answer', '-a', type=str, help='평가할 답변 텍스트 (직접 입력)')
    input_ex.add_argument('--file', '-f', type=str, help='평가할 답변이 포함된 파일 경로')
    
    # 선택 인자
    parser.add_argument('--model', '-m', type=str, default='gemma3:4b',
                      help='사용할 Ollama 모델')
    parser.add_argument('--temperature', '-t', type=float, default=0.7,
                      help='생성 온도 (0.1~1.0, 높을수록 창의적)')
    parser.add_argument('--output', '-o', type=str, default='',
                      help='결과를 저장할 파일 경로 (생략 시 저장하지 않음)')
    parser.add_argument('--show-result', '-s', action='store_true',
                      help='상세한 평가 결과 또는 개선된 답변 표시')
    
    # 피드백 관련 인자
    parser.add_argument('--feedback', '-fb', action='store_true',
                      help='피드백 루프를 통한 답변 개선 수행')
    parser.add_argument('--depth', '-d', type=int, default=2,
                      help='피드백 루프 깊이 (1-10)')
    parser.add_argument('--width', '-w', type=int, default=2,
                      help='피드백 루프 너비 (1-10)')
    
    args = parser.parse_args()
    return await evaluate_answer(args)


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
