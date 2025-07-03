#!/usr/bin/env python3
"""
HNSCC 연구 테스트 - 기본 Python 구현
biomcp-examples researcher_hnscc 예제 기반
"""

import os
import sys
from pathlib import Path

# 프로젝트 경로 설정
sys.path.insert(0, str(Path(__file__).parent))

# 필요한 모듈 임포트
from src.research.research_manager import ResearchManager
from src.feedback.answer_evaluator import AnswerEvaluator
from src.storage.file_storage import FileStorage
from src.utils.config import Config

def test_hnscc_research():
    """HNSCC 연구 테스트"""
    print("\n=== HNSCC (Head and Neck Squamous Cell Carcinoma) 연구 테스트 ===\n")
    
    # HNSCC 연구 질문 (biomcp-examples에서 사용된 질문)
    hnscc_question = """
    What are the emerging treatment strategies for head and neck squamous cell carcinoma (HNSCC), 
    particularly focusing on immunotherapy combinations, targeted therapies, and novel approaches 
    currently in clinical trials?
    """
    
    print(f"연구 질문: {hnscc_question.strip()}\n")
    
    # 1. 연구 매니저 초기화
    print("1. 연구 시스템 초기화...")
    config = Config()
    storage = FileStorage(config)
    research_manager = ResearchManager(config, storage)
    evaluator = AnswerEvaluator(config)
    
    # 2. 다양한 접근 방식으로 연구 수행
    print("\n2. 다양한 접근 방식으로 연구 수행...")
    
    # 접근 방식 1: 일반 연구
    print("\n[접근 방식 1] 일반 연구")
    try:
        result1 = research_manager.research_question(hnscc_question)
        print(f"✓ 연구 완료 - 답변 길이: {len(result1)} 글자")
        print(f"답변 미리보기: {result1[:200]}...")
    except Exception as e:
        print(f"✗ 오류 발생: {e}")
    
    # 접근 방식 2: 깊이 있는 연구
    print("\n[접근 방식 2] 깊이 있는 연구")
    try:
        # 세부 주제로 나누어 연구
        subtopics = [
            "HNSCC immunotherapy combinations with PD-1/PD-L1 inhibitors",
            "Targeted therapies for HNSCC including EGFR and PI3K inhibitors",
            "Novel approaches in HNSCC clinical trials 2023-2024"
        ]
        
        combined_result = []
        for subtopic in subtopics:
            print(f"  - 연구 중: {subtopic[:50]}...")
            sub_result = research_manager.research_question(subtopic)
            combined_result.append(f"### {subtopic}\n\n{sub_result}")
        
        result2 = "\n\n".join(combined_result)
        print(f"✓ 깊이 있는 연구 완료 - 총 답변 길이: {len(result2)} 글자")
    except Exception as e:
        print(f"✗ 오류 발생: {e}")
    
    # 3. 답변 평가
    print("\n3. 답변 평가...")
    try:
        if 'result1' in locals():
            evaluation = evaluator.evaluate_answer(hnscc_question, result1)
            print("\n[평가 결과]")
            print(f"- 정확성: {evaluation.get('accuracy_score', 'N/A')}/10")
            print(f"- 완전성: {evaluation.get('completeness_score', 'N/A')}/10")
            print(f"- 명확성: {evaluation.get('clarity_score', 'N/A')}/10")
            print(f"- 전체 점수: {evaluation.get('overall_score', 'N/A')}/10")
            
            if 'feedback' in evaluation:
                print(f"\n피드백: {evaluation['feedback'][:200]}...")
    except Exception as e:
        print(f"✗ 평가 중 오류: {e}")
    
    # 4. 결과 저장
    print("\n4. 연구 결과 저장...")
    try:
        if 'result2' in locals():
            # 종합 결과 생성
            final_result = f"""# HNSCC 치료 전략 연구 보고서

## 연구 질문
{hnscc_question.strip()}

## 연구 날짜
{storage._get_timestamp()}

## 연구 결과

{result2}

## 평가 요약
{evaluation if 'evaluation' in locals() else '평가 미완료'}

---
*본 연구는 GAIA 시스템을 통해 자동으로 수행되었습니다.*
"""
            
            # 저장
            filename = storage.save_research_result("HNSCC_emerging_treatments", final_result)
            print(f"✓ 연구 결과가 저장되었습니다: {filename}")
    except Exception as e:
        print(f"✗ 저장 중 오류: {e}")
    
    print("\n=== 테스트 완료 ===")

def main():
    """메인 함수"""
    print("GAIA HNSCC 연구 테스트")
    print("biomcp-examples의 researcher_hnscc 예제를 기반으로 합니다.")
    print("-" * 60)
    
    # 테스트 실행
    test_hnscc_research()
    
    print("\n테스트가 종료되었습니다.")
    print("연구 결과는 research_outputs 폴더에서 확인할 수 있습니다.")

if __name__ == "__main__":
    main()