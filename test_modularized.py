#!/usr/bin/env python3
"""
모듈화된 연구 시스템 테스트 스크립트
각 구성요소가 독립적으로 작동하는지 테스트
"""

import os
import asyncio
import argparse
from typing import List, Dict, Any

# 모듈화된 컴포넌트 임포트
from src.api.ollama_client import OllamaClient
from src.research.answer_generator import AnswerGenerator
from src.feedback.answer_evaluator import AnswerEvaluator
from src.research.research_manager import ResearchManager

async def test_ollama_client():
    """OllamaClient 테스트"""
    print("\n===== OllamaClient 테스트 =====")
    client = OllamaClient()
    
    # API 가용성 확인
    status = await client.check_availability()
    print(f"- API 상태: {status['status']}")
    
    if status['status'] == 'available':
        # GPU 최적화 파라미터 출력
        print(f"- 모델: {client.model}")
        print(f"- GPU 가속: num_gpu={client.gpu_params['num_gpu']}, num_thread={client.gpu_params['num_thread']}")
        
        # 간단한 텍스트 생성 테스트
        response = await client.generate(
            prompt="크레아틴 모노하이드레이트의 효능을 간단히 요약해주세요.",
            system_prompt="건강기능식품 전문가로서 간결하게 답변해주세요.",
            temperature=0.7
        )
        print(f"\n- 생성된 텍스트 (일부): {response[:100]}...")
        
        return True
    else:
        print(f"❌ API를 사용할 수 없습니다: {status.get('error', '알 수 없는 오류')}")
        return False

async def test_answer_generator(client: OllamaClient):
    """AnswerGenerator 테스트"""
    print("\n===== AnswerGenerator 테스트 =====")
    generator = AnswerGenerator(client)
    
    # 답변 생성 테스트
    question = "근육 회복을 위한 BCAA의 효능은 무엇인가요?"
    print(f"- 질문: {question}")
    
    answer = await generator.generate_answer(question)
    print(f"- 생성된 답변 (일부): {answer[:150]}...")
    
    # 대체 답변 생성 테스트
    print("- 대체 답변 생성 중...")
    alt_answers = await generator.generate_alternative_answers(question, count=2)
    print(f"- 생성된 대체 답변 수: {len(alt_answers)}")
    
    # 연구 질문 처리 테스트
    print("- research_question 메소드 테스트...")
    result = await generator.research_question(question)
    print(f"- 결과 길이: {len(result)} 자")
    
    return len(answer) > 0 and len(alt_answers) > 0 and len(result) > 0

async def test_answer_evaluator(client: OllamaClient):
    """AnswerEvaluator 테스트"""
    print("\n===== AnswerEvaluator 테스트 =====")
    evaluator = AnswerEvaluator(client)
    generator = AnswerGenerator(client)
    
    # 평가 테스트용 질문과 답변
    question = "근육 발달에 가장 중요한 아미노산은 무엇인가요?"
    print(f"- 질문: {question}")
    
    # 답변 생성
    answer = await generator.generate_answer(question)
    print(f"- 생성된 답변 (일부): {answer[:100]}...")
    
    # 답변 평가
    print("- 답변 평가 중...")
    evaluation = await evaluator.evaluate_answer(question, answer)
    print(f"- 총점: {evaluation.get('overall_score', 'N/A')}/10")
    print(f"- 주요 피드백: {evaluation.get('improvement_suggestions', 'N/A')[:150]}...")
    
    # 개선된 답변 생성
    print("- 개선된 답변 생성 중...")
    improved = await evaluator.generate_improved_answer(question, answer, evaluation)
    print(f"- 개선된 답변 (일부): {improved[:100]}...")
    
    # 피드백 루프 테스트 (간소화된 설정)
    print("- 피드백 루프 테스트 (깊이=1, 너비=1)...")
    feedback_result = await evaluator.feedback_loop(question, answer, depth=1, width=1)
    print(f"- 최종 점수: {feedback_result['best_score']}/10")
    
    return "best_score" in feedback_result and "final_answer" in feedback_result

async def test_research_manager(client: OllamaClient):
    """ResearchManager 테스트"""
    print("\n===== ResearchManager 테스트 =====")
    manager = ResearchManager(
        ollama_client=client,
        feedback_depth=1,  # 테스트를 위해 낮은 값 사용
        feedback_width=1,
        concurrent_research=2,
        output_dir="./test_outputs"
    )
    
    # 테스트 질문
    questions = [
        "크레아틴의 근육 발달 효과는 어떻게 되나요?",
        "운동 후 단백질 섭취 시간이 중요한 이유는 무엇인가요?"
    ]
    print(f"- 테스트 질문: {len(questions)}개")
    
    # 단일 질문 테스트
    print(f"\n- 단일 질문 테스트: '{questions[0][:30]}...'")
    single_result = await manager.research_question(questions[0])
    print(f"  - 상태: {single_result.get('status', 'N/A')}")
    print(f"  - 점수: {single_result.get('score', 'N/A')}")
    
    # 질문 목록에 대한 연구 테스트 (단순화)
    print("\n- 질문 목록 심층 연구 테스트...")
    print("  (테스트를 위해 간소화된 설정 사용)")
    
    results = await manager.conduct_research(questions[:1])  # 첫 번째 질문만 사용
    print(f"  - 완료된 질문: {results.get('completed_questions', 'N/A')}")
    print(f"  - 저장 위치: {results.get('output_directory', 'N/A')}")
    
    return single_result.get('status') == 'completed' and 'results' in results

async def main():
    """테스트 메인 함수"""
    parser = argparse.ArgumentParser(description='모듈화된 연구 시스템 테스트')
    parser.add_argument('--test', '-t', choices=['all', 'client', 'generator', 'evaluator', 'manager'], 
                      default='all', help='실행할 테스트 (기본값: all)')
    args = parser.parse_args()
    
    test_type = args.test
    print(f"===== 모듈화된 연구 시스템 테스트: {test_type} =====")
    
    # 기본 클라이언트 초기화
    client = OllamaClient()
    
    # 선택된 테스트 실행
    results = {}
    
    if test_type in ['all', 'client']:
        results['client'] = await test_ollama_client()
        if not results['client']:
            print("❌ OllamaClient 테스트 실패 - 다른 테스트를 진행할 수 없습니다")
            return
    
    if test_type in ['all', 'generator'] and (test_type != 'all' or results.get('client', True)):
        results['generator'] = await test_answer_generator(client)
        
    if test_type in ['all', 'evaluator'] and (test_type != 'all' or results.get('client', True)):
        results['evaluator'] = await test_answer_evaluator(client)
        
    if test_type in ['all', 'manager'] and (test_type != 'all' or results.get('client', True)):
        results['manager'] = await test_research_manager(client)
        
    # 결과 요약
    print("\n===== 테스트 결과 요약 =====")
    for test_name, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"- {test_name}: {status}")
    
    if all(results.values()):
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다. 로그를 확인하세요.")

if __name__ == "__main__":
    asyncio.run(main())
