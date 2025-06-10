#!/usr/bin/env python3
"""
근육 관련 건강기능식품 연구 시스템 - CLI 인터페이스
명령줄에서 시스템의 다양한 기능에 접근할 수 있는 인터페이스 제공
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

# 상위 디렉토리를 모듈 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 모듈 임포트
from src.api.ollama_client import OllamaClient
from src.research.research_manager import ResearchManager
from src.research.answer_generator import AnswerGenerator
from src.feedback.answer_evaluator import AnswerEvaluator
from src.storage.file_storage import FileStorage

# 버전 정보
VERSION = "1.0.0"


async def handle_single_question(args):
    """
    단일 질문에 대한 연구 수행
    """
    print(f"📚 질문 연구 시작: '{args.question}'")
    
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
    
    print(f"🚀 {status.get('current_model', client.model)} 모델 사용 중")
    
    # 연구 관리자 초기화
    manager = ResearchManager(
        ollama_client=client,
        feedback_depth=args.depth,
        feedback_width=args.width,
        concurrent_research=args.concurrent,
        output_dir=args.output_dir
    )
    
    # 연구 수행
    start_time = datetime.now()
    result = await manager.research_question(args.question)
    elapsed = (datetime.now() - start_time).total_seconds()
    
    # 결과 출력
    if "error" in result:
        print(f"❌ 연구 실패: {result['error']}")
        return 1
        
    print(f"\n✅ 연구 완료 (소요 시간: {elapsed:.1f}초)")
    print(f"📊 품질 점수: {result.get('score', 'N/A')}/10")
    print(f"🔄 피드백 루프: {result.get('feedback_loops', 'N/A')}회")
    print(f"📁 결과 저장 위치: {manager.file_storage.get_session_directory(manager.session_id)}")
    
    # 결과 요약 표시
    if args.show_summary:
        answer = result.get("answer", "")
        print("\n" + "=" * 50)
        print("📝 연구 결과 요약 (처음 500자)")
        print("=" * 50)
        print(answer[:500] + "...\n")
        
    return 0


async def handle_questions_file(args):
    """
    파일에서 질문 목록을 읽어 연구 수행
    """
    if not os.path.exists(args.file):
        print(f"❌ 파일을 찾을 수 없습니다: {args.file}")
        return 1
    
    try:
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
        
        # 빈 질문 필터링
        questions = [q for q in questions if q]
        
        if not questions:
            print("❌ 파일에 질문이 없습니다")
            return 1
            
        print(f"📋 {len(questions)}개 질문 로드 완료")
        
        # 클라이언트 초기화
        client = OllamaClient(
            model=args.model,
            temperature=args.temperature
        )
        
        # ResearchManager 초기화
        manager = ResearchManager(
            ollama_client=client,
            feedback_depth=args.depth,
            feedback_width=args.width,
            concurrent_research=args.concurrent,
            output_dir=args.output_dir
        )
        
        # 연구 수행
        print(f"\n🔍 심층 연구 시작 (동시 처리: {args.concurrent}개, 피드백 깊이: {args.depth}, 너비: {args.width})")
        start_time = datetime.now()
        results = await manager.conduct_research(questions)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # 결과 출력
        print(f"\n✅ 연구 완료 (총 소요 시간: {elapsed:.1f}초)")
        print(f"📊 완료된 질문: {results.get('completed_questions', 0)}/{len(questions)}")
        print(f"📁 결과 저장 위치: {results.get('output_directory', 'N/A')}")
        
        return 0
    
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return 1


async def handle_interactive_mode(args):
    """
    대화형 모드로 질문 연구 수행
    """
    print("\n" + "=" * 50)
    print("🤖 근육 관련 건강기능식품 연구 시스템 - 대화형 모드")
    print("=" * 50)
    print("📝 질문을 입력하고 Enter 키를 누르세요")
    print("📝 'exit' 또는 'quit'을 입력하면 종료합니다")
    print("=" * 50 + "\n")
    
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
        
    print(f"🚀 {status.get('current_model', client.model)} 모델 사용 중\n")
    
    # 연구 관리자 초기화
    manager = ResearchManager(
        ollama_client=client,
        feedback_depth=args.depth,
        feedback_width=args.width,
        concurrent_research=args.concurrent,
        output_dir=args.output_dir
    )
    
    while True:
        try:
            question = input("🔍 질문을 입력하세요 > ")
            if not question:
                continue
                
            if question.lower() in ["exit", "quit", "종료", "나가기"]:
                print("👋 프로그램을 종료합니다")
                break
                
            # 연구 수행
            start_time = datetime.now()
            result = await manager.research_question(question)
            elapsed = (datetime.now() - start_time).total_seconds()
            
            # 결과 출력
            if "error" in result:
                print(f"❌ 연구 실패: {result['error']}")
                continue
                
            print(f"\n✅ 연구 완료 (소요 시간: {elapsed:.1f}초)")
            print(f"📊 품질 점수: {result.get('score', 'N/A')}/10")
            print(f"🔄 피드백 루프: {result.get('feedback_loops', 'N/A')}회")
            print(f"📁 결과 저장 위치: {manager.file_storage.get_session_directory(manager.session_id)}\n")
            
            # 결과 요약 표시
            if args.show_summary:
                answer = result.get("answer", "")
                print("\n" + "=" * 50)
                print("📝 연구 결과 요약 (처음 500자)")
                print("=" * 50)
                print(answer[:500] + "...\n")
                
        except KeyboardInterrupt:
            print("\n👋 프로그램을 종료합니다")
            break
        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
    
    return 0


async def main():
    # 상위 수준 파서 생성
    parser = argparse.ArgumentParser(
        description='근육 관련 건강기능식품 연구 시스템 CLI',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # 공통 인자
    parser.add_argument('--model', '-m', type=str, default='gemma3:4b',
                      help='사용할 Ollama 모델')
    parser.add_argument('--output-dir', '-o', type=str, default='./research_outputs',
                      help='연구 결과 저장 디렉토리')
    parser.add_argument('--temperature', '-t', type=float, default=0.7,
                      help='생성 온도 (0.1~1.0, 높을수록 창의적)')
    parser.add_argument('--depth', '-d', type=int, default=2,
                      help='피드백 루프 깊이 (1-10)')
    parser.add_argument('--width', '-w', type=int, default=2,
                      help='피드백 루프 너비 (1-10)')
    parser.add_argument('--concurrent', '-c', type=int, default=2,
                      help='동시 처리할 최대 질문 수')
    parser.add_argument('--show-summary', '-s', action='store_true',
                      help='응답 요약 표시')
    parser.add_argument('--version', '-v', action='version',
                      version=f'근육 관련 건강기능식품 연구 시스템 v{VERSION}')
    
    # 서브파서 설정
    subparsers = parser.add_subparsers(dest='command', help='명령어')
    
    # 단일 질문 명령어
    question_parser = subparsers.add_parser('question', help='단일 질문 연구')
    question_parser.add_argument('question', type=str, help='연구할 질문')
    
    # 파일 기반 질문 명령어
    file_parser = subparsers.add_parser('file', help='파일에서 질문 로드 및 연구')
    file_parser.add_argument('file', type=str, help='질문이 포함된 파일 (텍스트 또는 JSON)')
    
    # 대화형 모드 명령어
    interactive_parser = subparsers.add_parser('interactive', help='대화형 모드')
    
    # 인자 파싱
    args = parser.parse_args()
    
    # 명령어에 따라 처리
    if args.command == 'question':
        return await handle_single_question(args)
    elif args.command == 'file':
        return await handle_questions_file(args)
    elif args.command == 'interactive':
        return await handle_interactive_mode(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
