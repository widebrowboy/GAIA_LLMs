#!/usr/bin/env python3
"""
근육 관련 건강기능식품 연구 시스템 통합 CLI 도구
모든 모듈별 CLI 도구를 통합하여 단일 진입점 제공
"""

import os
import sys
import json
import asyncio
import argparse
import importlib.util
from datetime import datetime
from typing import List, Dict, Any, Optional

# 상위 디렉토리를 모듈 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 모듈 패스 정의
MODULE_PATHS = {
    "ollama_client": os.path.join(os.path.dirname(os.path.abspath(__file__)), "ollama_client_cli.py"),
    "answer_generator": os.path.join(os.path.dirname(os.path.abspath(__file__)), "answer_generator_cli.py"),
    "answer_evaluator": os.path.join(os.path.dirname(os.path.abspath(__file__)), "answer_evaluator_cli.py"),
    "research_manager": os.path.join(os.path.dirname(os.path.abspath(__file__)), "research_manager_cli.py")
}


def load_module(name: str, path: str):
    """
    파일 경로로부터 Python 모듈 동적 로드
    """
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise ImportError(f"모듈 로딩 실패: {path}")
        
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def main():
    """
    CLI 도구 메인 함수
    """
    # 메인 파서 설정
    parser = argparse.ArgumentParser(
        description='근육 관련 건강기능식품 연구 시스템 CLI 도구',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # 서브파서 설정
    subparsers = parser.add_subparsers(dest='command', help='사용할 모듈')
    
    # 각 모듈별 서브파서 추가
    subparsers.add_parser('api', help='Ollama API 클라이언트 도구 (텍스트 생성 및 API 확인)')
    subparsers.add_parser('generate', help='답변 생성기 도구 (질문에 대한 구조화된 답변 생성)')
    subparsers.add_parser('evaluate', help='답변 평가기 도구 (생성된 답변 평가 및 피드백 루프)')
    subparsers.add_parser('research', help='연구 관리자 도구 (질문 연구 수행, 단일 또는 배치)')
    
    # 버전 및 정보 인자 추가
    parser.add_argument('-v', '--version', action='version', 
                       version='근육 관련 건강기능식품 연구 시스템 CLI v1.0.0')
    parser.add_argument('--show-modules', action='store_true',
                       help='사용 가능한 모듈 목록 표시')
    
    args, remaining = parser.parse_known_args()
    
    # 모듈 목록만 표시
    if args.show_modules:
        print("📋 사용 가능한 모듈 목록:")
        print("1. api      - Ollama API 클라이언트 (텍스트 생성, API 확인)")
        print("2. generate - 답변 생성기 (질문에 대한 구조화된 답변 생성)")
        print("3. evaluate - 답변 평가기 (생성된 답변 평가 및 피드백 루프)")
        print("4. research - 연구 관리자 (질문 연구 수행, 단일 또는 배치)")
        print("\n사용 예시:")
        print("  ./cli_tool.py api check")
        print("  ./cli_tool.py generate '크레아틴은 근육 성장에 어떤 영향을 미치나요?'")
        print("  ./cli_tool.py evaluate '단백질 보충제의 종류는?' --file answer.txt")
        print("  ./cli_tool.py research --question '근육 회복에 좋은 영양소는?'")
        return 0
    
    # 명령어가 선택되지 않은 경우 도움말 표시
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        # 명령어에 따라 모듈 로드 및 실행
        if args.command == 'api':
            # ollama_client_cli.py 호출
            module_name = 'ollama_client'
            module = load_module(module_name, MODULE_PATHS[module_name])
            
            # main() 직접 호출 (인자 전달)
            if not remaining or remaining[0] not in ['generate', 'check']:
                print("사용 가능한 API 명령어: generate, check")
                print("예시: ./cli_tool.py api generate --prompt '질문'")
                print("      ./cli_tool.py api check")
                return 1
                
            # main에 남은 인자 전달
            old_sys_argv = sys.argv
            sys.argv = [MODULE_PATHS[module_name]] + remaining
            exit_code = await module.main()
            sys.argv = old_sys_argv
            
        elif args.command == 'generate':
            # answer_generator_cli.py 호출
            module_name = 'answer_generator'
            module = load_module(module_name, MODULE_PATHS[module_name])
            
            # 단순화된 호출 지원 (첫 번째 인자를 질문으로 처리)
            if remaining and not remaining[0].startswith('-'):
                question = remaining[0]
                remaining = ['--question', question] + remaining[1:]
            
            # main에 남은 인자 전달
            old_sys_argv = sys.argv
            sys.argv = [MODULE_PATHS[module_name]] + remaining
            exit_code = await module.main()
            sys.argv = old_sys_argv
            
        elif args.command == 'evaluate':
            # answer_evaluator_cli.py 호출
            module_name = 'answer_evaluator'
            module = load_module(module_name, MODULE_PATHS[module_name])
            
            # 단순화된 호출 지원 (첫 번째 인자를 질문으로 처리)
            if remaining and not remaining[0].startswith('-'):
                question = remaining[0]
                remaining = [question] + remaining[1:]
            
            # main에 남은 인자 전달
            old_sys_argv = sys.argv
            sys.argv = [MODULE_PATHS[module_name]] + remaining
            exit_code = await module.main()
            sys.argv = old_sys_argv
            
        elif args.command == 'research':
            # research_manager_cli.py 호출
            module_name = 'research_manager'
            module = load_module(module_name, MODULE_PATHS[module_name])
            
            # main에 남은 인자 전달
            old_sys_argv = sys.argv
            sys.argv = [MODULE_PATHS[module_name]] + remaining
            exit_code = await module.main()
            sys.argv = old_sys_argv
            
        else:
            print(f"❌ 알 수 없는 명령어: {args.command}")
            parser.print_help()
            return 1
            
        return exit_code
        
    except ImportError as e:
        print(f"❌ 모듈 로드 실패: {str(e)}")
        print("모든 모듈 파일이 cli/ 폴더에 존재하는지 확인하세요.")
        return 1
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
