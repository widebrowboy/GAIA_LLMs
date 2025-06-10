#!/usr/bin/env python3
"""
연구 관리자 CLI 도구
ResearchManager 모듈을 위한 독립적인 명령행 인터페이스
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
from src.research.research_manager import ResearchManager


async def conduct_research(args):
    """
    질문 연구 수행
    """
    try:
        # 질문 목록 설정
        questions = []
        
        if args.question:
            # 직접 입력된 질문 사용
            questions = [args.question]
        elif args.questions:
            # 여러 질문 직접 입력
            questions = args.questions
        elif args.file:
            # 파일에서 질문 읽기
            if not os.path.exists(args.file):
                print(f"❌ 파일을 찾을 수 없습니다: {args.file}")
                return 1
                
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 파일 형식 확인 및 질문 추출
            if args.file.endswith('.json'):
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        questions = data
                    elif isinstance(data, dict) and "questions" in data:
                        questions = data["questions"]
                    else:
                        print("❌ JSON 파일 형식 오류: 'questions' 배열을 찾을 수 없습니다")
                        return 1
                except json.JSONDecodeError:
                    print("❌ 유효하지 않은 JSON 파일입니다")
                    return 1
            else:
                # 일반 텍스트 파일로 처리 (각 행을 질문으로 간주)
                questions = [line.strip() for line in content.split('\n') if line.strip()]
        
        # 질문 유효성 검사
        questions = [q for q in questions if q]
        if not questions:
            print("❌ 유효한 질문이 없습니다")
            return 1
            
        print(f"📋 {len(questions)}개 질문 준비 완료")
        
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
        
        # 연구 관리자 초기화
        manager = ResearchManager(
            ollama_client=client,
            feedback_depth=args.depth,
            feedback_width=args.width,
            concurrent_research=args.concurrent,
            output_dir=args.output_dir
        )
        
        start_time = datetime.now()
        
        # 단일 질문인 경우
        if len(questions) == 1 and not args.batch:
            print(f"\n📚 단일 질문 연구 시작: '{questions[0]}'")
            result = await manager.research_question(questions[0])
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            if "error" in result:
                print(f"❌ 연구 실패: {result['error']}")
                return 1
                
            print(f"\n✅ 연구 완료 (소요 시간: {elapsed:.1f}초)")
            print(f"📊 품질 점수: {result.get('score', 'N/A')}/10")
            print(f"🔄 피드백 루프: {result.get('feedback_loops', 'N/A')}회")
            print(f"📁 결과 저장 위치: {result.get('output_directory', manager.output_dir)}")
            
            # 결과 요약 표시
            if args.show_result:
                answer = result.get("answer", "")
                print("\n" + "=" * 50)
                print("📝 연구 결과 요약 (처음 500자)")
                print("=" * 50)
                print(answer[:500] + "...\n" if len(answer) > 500 else answer)
        
        # 여러 질문 또는 배치 모드
        else:
            print(f"\n📚 심층 연구 시작 ({len(questions)}개 질문, 동시 처리: {args.concurrent}개)")
            print(f"- 피드백 루프: 깊이={args.depth}, 너비={args.width}")
            
            results = await manager.conduct_research(questions, args.concurrent)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            if "error" in results:
                print(f"❌ 연구 실패: {results['error']}")
                return 1
                
            print(f"\n✅ 심층 연구 완료 (총 소요 시간: {elapsed:.1f}초)")
            print(f"📊 완료된 질문: {results.get('completed_questions', 0)}/{len(questions)}")
            print(f"📁 결과 저장 위치: {results.get('output_directory', '')}")
            
            # 결과 세부 정보
            if args.show_result and "results" in results:
                print("\n===== 개별 질문 결과 요약 =====")
                for i, res in enumerate(results["results"]):
                    status = "✅ 완료" if res.get("status") == "completed" else "❌ 실패"
                    print(f"{i+1}. '{res.get('question', '')[:50]}...' - {status}")
                    if "score" in res:
                        print(f"   점수: {res.get('score')}/10")
                    if "error" in res:
                        print(f"   오류: {res.get('error')}")
        
        # 결과를 추가로 JSON 파일로 저장
        if args.save_json:
            output_file = args.save_json
            dir_path = os.path.dirname(output_file) if os.path.dirname(output_file) else '.'
            os.makedirs(dir_path, exist_ok=True)
            
            if len(questions) == 1 and not args.batch:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            else:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"📁 결과를 '{output_file}' 파일로 저장했습니다.")
            
        return 0
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return 1


async def main():
    parser = argparse.ArgumentParser(
        description='연구 관리자 CLI 도구',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # 질문 입력 방식 (여러 옵션 중 하나)
    input_group = parser.add_argument_group('질문 입력 옵션 (하나를 선택)')
    input_ex = input_group.add_mutually_exclusive_group(required=True)
    input_ex.add_argument('--question', '-q', type=str, help='연구할 단일 질문')
    input_ex.add_argument('--questions', '-qs', type=str, nargs='+', help='연구할 여러 질문')
    input_ex.add_argument('--file', '-f', type=str, help='질문이 포함된 파일 경로 (텍스트 또는 JSON)')
    
    # 연구 설정
    parser.add_argument('--model', '-m', type=str, default='gemma3:4b',
                      help='사용할 Ollama 모델')
    parser.add_argument('--temperature', '-t', type=float, default=0.7,
                      help='생성 온도 (0.1~1.0, 높을수록 창의적)')
    parser.add_argument('--depth', '-d', type=int, default=2,
                      help='피드백 루프 깊이 (1-10)')
    parser.add_argument('--width', '-w', type=int, default=2,
                      help='피드백 루프 너비 (1-10)')
    parser.add_argument('--concurrent', '-c', type=int, default=2,
                      help='동시 처리할 최대 질문 수')
    parser.add_argument('--output-dir', '-o', type=str, default='./research_outputs',
                      help='연구 결과 저장 디렉토리')
    parser.add_argument('--batch', '-b', action='store_true',
                      help='단일 질문도 배치 모드로 처리')
    parser.add_argument('--show-result', '-s', action='store_true',
                      help='결과 요약 표시')
    parser.add_argument('--save-json', '-j', type=str, default='',
                      help='결과를 JSON 파일로 저장 (파일 경로)')
    
    args = parser.parse_args()
    return await conduct_research(args)


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
