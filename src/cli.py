#!/usr/bin/env python3
"""
CLI 인터페이스 모듈
근육 관련 건강기능식품 연구 시스템의 명령줄 인터페이스
"""

import os
import sys
import asyncio
import argparse
from typing import Dict, Any, List, Optional

# 내부 모듈 임포트
from src.api.ollama_client import OllamaClient
from src.research.research_manager import ResearchManager
from src.utils.config_manager import ConfigManager

async def check_api_availability(config_manager: ConfigManager) -> bool:
    """
    Ollama API 가용성 확인
    
    Args:
        config_manager: 설정 관리자
    
    Returns:
        bool: API 사용 가능 여부
    """
    print("Ollama API 가용성 확인 중...")
    
    client = OllamaClient(
        model=config_manager.get_ollama_model()
    )
    
    status = await client.check_availability()
    
    if status["status"] == "available":
        print(f"✅ Ollama API 사용 가능 ({status['models_count']}개 모델 사용 가능)")
        print(f"   모델: {status['current_model']} " + 
              ("✅ 사용 가능" if status.get('current_model_available') else "⚠️ 사용 불가능"))
        return True
    else:
        print(f"❌ Ollama API 사용 불가: {status.get('error', '알 수 없는 오류')}")
        print(f"   API URL: {client.ollama_url}")
        print(f"   Ollama 서버가 실행 중인지 확인하세요. (기본 URL: http://localhost:11434)")
        return False

async def run_research(args: argparse.Namespace, config_manager: ConfigManager) -> None:
    """
    연구 실행
    
    Args:
        args: 명령줄 인수
        config_manager: 설정 관리자
    """
    # API 가용성 확인
    if not await check_api_availability(config_manager):
        sys.exit(1)
    
    # 설정에서 깊이와 너비 가져오기
    depth = args.depth or config_manager.get_feedback_depth()
    width = args.width or config_manager.get_feedback_width()
    concurrent = args.concurrent or config_manager.get_concurrent_research()
    
    # 출력 디렉토리 설정
    output_dir = args.output_dir or config_manager.get_output_dir()
    
    # 연구 관리자 생성
    manager = ResearchManager(
        feedback_depth=depth,
        feedback_width=width,
        concurrent_research=concurrent,
        output_dir=output_dir
    )
    
    # 질문 처리
    questions = None
    if args.question:
        questions = [args.question]
    
    # 연구 실행
    result = await manager.run_research(questions=questions, questions_file=args.file)
    
    # 연구 결과 정보 출력
    if result:
        print(f"\n===== 연구 완료 =====")
        print(f"- 총 질문: {result['total_questions']}개")
        print(f"- 완료: {result['completed_questions']}개")
        print(f"- 실패: {result['failed_questions']}개")
        print(f"- 결과 저장 위치: {result['output_directory']}")
        
        if args.verbose and 'results' in result:
            print("\n--- 개별 질문 결과 ---")
            for i, res in enumerate(result['results']):
                status = res.get('status', '실패')
                emoji = "✅" if status == "completed" else "❌"
                print(f"{emoji} [{res.get('question_id', f'Q{i+1}')}] " + 
                      f"{res.get('question', '')[:50]}... " +
                      f"(점수: {res.get('score', 'N/A')})")

async def run_interactive_mode(config_manager: ConfigManager) -> None:
    """
    대화형 모드 실행
    
    Args:
        config_manager: 설정 관리자
    """
    print("\n===== 근육 건강기능식품 연구 시스템 대화형 모드 =====")
    
    # API 가용성 확인
    if not await check_api_availability(config_manager):
        print("Ollama API를 사용할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        sys.exit(1)
        
    # Ollama 클라이언트 생성
    client = OllamaClient(
        model=config_manager.get_ollama_model()
    )
    
    # 연구 관리자 생성
    manager = ResearchManager(
        ollama_client=client,
        feedback_depth=config_manager.get_feedback_depth(),
        feedback_width=config_manager.get_feedback_width(),
        concurrent_research=config_manager.get_concurrent_research(),
        output_dir=config_manager.get_output_dir()
    )
    
    print("\n현재 설정:")
    print(f"- 모델: {client.model}")
    print(f"- 피드백 깊이: {manager.feedback_depth}")
    print(f"- 피드백 너비: {manager.feedback_width}")
    print(f"- 저장 위치: {manager.output_dir}")
    
    print("\n연구를 시작하려면 질문을 입력하세요 ('q'를 입력하면 종료):")
    
    while True:
        try:
            question = input("\n질문> ").strip()
            
            if not question:
                continue
                
            if question.lower() in ['q', 'quit', 'exit']:
                print("프로그램을 종료합니다.")
                break
                
            # 연구 수행
            print(f"\n연구를 시작합니다: '{question}'")
            result = await manager.research_question(question)
            
            if 'error' in result:
                print(f"\n❌ 연구 실패: {result.get('error')}")
            else:
                print(f"\n✅ 연구 완료 (점수: {result.get('score', 'N/A')}/10)")
                print(f"- 피드백 루프: {result.get('feedback_loops', 0)}회")
                print(f"- 결과 저장 위치: {manager.output_dir}")
                
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
            break
            
        except Exception as e:
            print(f"\n❌ 오류 발생: {str(e)}")

def main():
    """CLI 메인 함수"""
    # 명령줄 인수 파싱
    parser = argparse.ArgumentParser(
        description='근육 관련 건강기능식품 연구 시스템',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python -m src.cli -q "근육 발달에 가장 중요한 아미노산은 무엇인가요?"
  python -m src.cli -f questions.json -d 3 -w 2
  python -m src.cli --interactive
"""
    )
    
    # 모드 선택 인수 그룹
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('-q', '--question', type=str,
                         help='연구할 단일 질문')
    mode_group.add_argument('-f', '--file', type=str,
                         help='질문 목록 파일 경로 (JSON 또는 텍스트)')
    mode_group.add_argument('-i', '--interactive', action='store_true',
                         help='대화형 모드')
    
    # 선택적 인수
    parser.add_argument('-d', '--depth', type=int,
                       help='피드백 루프 깊이 (기본값: 설정값)')
    parser.add_argument('-w', '--width', type=int,
                       help='피드백 루프 너비 (기본값: 설정값)')
    parser.add_argument('-c', '--concurrent', type=int,
                       help='동시 연구 프로세스 수 (기본값: 설정값)')
    parser.add_argument('-m', '--model', type=str,
                       help='사용할 Ollama 모델 (기본값: 설정값)')
    parser.add_argument('-o', '--output-dir', type=str,
                       help='결과 저장 디렉토리 (기본값: 설정값)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='상세 출력 모드')
    
    args = parser.parse_args()
    
    # 설정 관리자 생성
    config_manager = ConfigManager()
    
    # 비동기 이벤트 루프
    try:
        if args.interactive:
            asyncio.run(run_interactive_mode(config_manager))
        else:
            asyncio.run(run_research(args, config_manager))
    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
