#!/usr/bin/env python3
import asyncio
import argparse
import json
import sys
import os
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple, Union
from datetime import datetime
import httpx
from research_agent import ResearchAgent, ResearchConfig

def print_banner():
    """Print the application banner"""
    banner = """
    ██████╗ ███████╗ █████╗ ██████╗  ██████╗██╗  ██╗    ███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗
    ██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║
    ██████╔╝█████╗  ███████║██████╔╝██║     ███████║    ███████╗█████╗  ███████║██████╔╝██║     ███████║
    ██╔══██╗██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║    ╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║
    ██║  ██║███████╗██║  ██║██║  ██║╚██████╗██║  ██║    ███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║
    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
    """
    print(banner)
    print("딥 리서치 에이전트에 오신 것을 환영합니다! (v1.0.0)\n")

def print_help():
    """Print help information"""
    help_text = """
사용 방법:
  python cli.py research <주제> [옵션]     주제에 대한 연구 수행
  python cli.py list-models              사용 가능한 Ollama 모델 목록 표시
  python cli.py --help                   도움말 표시

옵션:
  -q, --questions [QUESTIONS ...]     연구 질문 목록 (공백으로 구분)
  -f, --file FILE                     JSON 파일에서 질문 목록 로드
  -d, --depth DEPTH                   피드백 루프 깊이 (기본값: 10)
  -b, --breadth BREADTH               각 단계의 대체 답변 수 (기본값: 10)
  -o, --output DIR                    출력 디렉토리 (기본값: ./research_outputs)
  -v, --verbose                       자세한 출력 표시
    """

def load_questions_from_file(file_path: str) -> Dict[str, Any]:
    """JSON 파일에서 연구 질문 로드
    
    Args:
        file_path: JSON 파일 경로
        
    Returns:
        Dict: 연구 주제, 질문, 참고문헌 등을 포함한 사전
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 필수 키 확인
        if 'questions' not in data or not data['questions']:
            raise ValueError("JSON 파일에 'questions' 키가 없거나 질문이 비어 있습니다.")
            
        # 주제가 없으면 파일명을 기본값으로 사용
        if 'topic' not in data:
            data['topic'] = Path(file_path).stem.replace('_', ' ').capitalize()
            
        return data
    except json.JSONDecodeError:
        raise ValueError(f"'{file_path}'은 유효한 JSON 파일이 아닙니다.")
    except FileNotFoundError:
        raise FileNotFoundError(f"'{file_path}' 파일을 찾을 수 없습니다.")
        
def validate_arguments(args: argparse.Namespace) -> bool:
    """명령줄 인수 검증
    
    Args:
        args: 파싱된 명령줄 인수
        
    Returns:
        bool: 인수가 유효하면 True, 그렇지 않으면 False
    """
    # 깊이와 너비 검증
    if args.depth < 1 or args.depth > 10:
        print("❌ 오류: 피드백 루프 깊이는 1에서 10 사이여야 합니다.", file=sys.stderr)
        return False
        
    if args.breadth < 1 or args.breadth > 10:
        print("❌ 오류: 피드백 루프 너비는 1에서 10 사이여야 합니다.", file=sys.stderr)
        return False
    
    # 온도 검증
    if args.temperature < 0.1 or args.temperature > 1.0:
        print("❌ 오류: 생성 온도는 0.1에서 1.0 사이여야 합니다.", file=sys.stderr)
        return False
        
    # 파일 검증
    if args.file and not os.path.isfile(args.file):
        print(f"❌ 오류: '{args.file}' 파일을 찾을 수 없습니다.", file=sys.stderr)
        return False
        
    return True

async def run_research(args: argparse.Namespace) -> Tuple[str, Dict[str, Any]]:
    """주어진 인수로 연구 수행
    
    Args:
        args: 파싱된 명령줄 인수
        
    Returns:
        Tuple[str, Dict[str, Any]]: 출력 파일 경로와 연구 메타데이터
    """
    try:
        # 파일에서 질문 로드(지정된 경우)
        if args.file:
            data = load_questions_from_file(args.file)
            topic = data.get('topic', args.topic)
            research_questions = data.get('questions', [])
            references = data.get('references', [])
        else:
            topic = args.topic
            research_questions = args.questions or []
            references = []
        
        if not research_questions:
            print("❌ 오류: 연구할 질문이 없습니다.")
            sys.exit(1)
        
        print(f"\n🔍 '{topic}' 주제로 연구를 시작합니다...")
        print(f"📝 질문 수: {len(research_questions)}개")
        print(f"🔄 깊이(Depth): {args.depth}, 너비(Breadth): {args.breadth}")
        print(f"🌡️  온도: {args.temperature}")
        print(f"💾 출력 디렉토리: {os.path.abspath(args.output or 'research_outputs')}")
        print("\n⏳ 연구를 시작합니다. 시간이 다소 소요될 수 있습니다...\n")
        
        # ResearchAgent 초기화
        agent = ResearchAgent(
            model=args.model,
            temperature=args.temperature,
            max_tokens=4000
        )
        
        # 출력 디렉토리 설정 (지정된 경우)
        if args.output:
            agent.config['output_dir'] = args.output
        
        # 참고 문헌을 첫 질문에 추가 (있는 경우)
        if references and research_questions:
            research_questions[0] += "\n\n참고 문헌:\n" + "\n".join(f"- {ref}" for ref in references)
        
        # 연구 실행 및 시간 측정
        start_time = time.time()
        output_file, metadata = await agent.conduct_research(
            topic=topic,
            research_questions=research_questions,
            depth=args.depth,
            breadth=args.breadth
        )
        
        # Calculate research duration
        duration = time.time() - start_time
        minutes, seconds = divmod(int(duration), 60)
        
        print("\n" + "=" * 50)
        print("✅ 연구가 성공적으로 완료되었습니다!")
        print("=" * 50)
        print(f"📄 결과 파일: {os.path.abspath(output_file)}")
        print(f"⏱️  소요 시간: {minutes}분 {seconds}초")
        print(f"📊 생성된 콘텐츠: {os.path.getsize(output_file) / 1024:.1f} KB")
        print("=" * 50)
        
        # Print a preview of the output
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                preview = ''.join([next(f) for _ in range(10)])
                print("\n📝 결과 미리보기:")
                print("-" * 50)
                print(preview.strip())
                print("...")
                print("-" * 50)
                print(f"전체 내용을 보시려면 다음 파일을 확인하세요: {output_file}")
        except Exception as e:
            print(f"결과 미리보기 중 오류: {e}")
            
    except Exception as e:
        print(f"\n❌ 연구 중 오류가 발생했습니다: {e}")
        raise

async def list_models(show_details: bool) -> int:
    """사용 가능한 Ollama 모델 목록 표시
    
    Args:
        show_details: 상세 정보 표시 여부
        
    Returns:
        int: 성공 시 0, 오류 시 1
    """
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    try:
        print("\n🔄 사용 가능한 Ollama 모델 목록을 가져오는 중...")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{ollama_url}/api/tags")
            response.raise_for_status()
            models = response.json().get('models', [])
            
            if not models:
                print("\n❌ 모델을 찾을 수 없습니다. Ollama가 실행 중이고 모델이 설치되어 있는지 확인하세요.")
                print("   모델을 설치하려면: ollama pull <모델이름>")
                return 1
                return
            
            # 모델 이름 기준 정렬
            models.sort(key=lambda x: x.get('name', ''))
            
            print(f"\n📚 사용 가능한 모델 ({len(models)}개):\n")
            
            if show_details:
                print(f"{'모델 이름':<40} {'사이즈':<15} {'수정일자':<25} {'태그':<20}")
                print("-" * 100)
                
                for model in models:
                    model_name = model.get('name', 'unknown')
                    size_bytes = model.get('size', 0)
                    size_gb = round(size_bytes / (1024**3), 2) if size_bytes > 0 else 0
                    modified = model.get('modified_at', '').split('.')[0].replace('T', ' ') if 'modified_at' in model else 'unknown'
                    tags = model.get('tags', [])
                    tags_str = ', '.join(tags[:3]) + ('...' if len(tags) > 3 else '')
                    
                    print(f"{model_name:<40} {size_gb:>5} GB     {modified:<25} {tags_str:<20}")
                    
                    if 'modelfile' in model:
                        modelfile_display = model['modelfile'][:80]
                        if len(model['modelfile']) > 80:
                            modelfile_display += '...'
                        print(f"  - 모델파일: {modelfile_display}")
                    print()
            else:
                print(f"{'모델 이름':<40} {'사이즈':<15} 수정일자")
                print("-" * 80)
                
                for model in models:
                    model_name = model.get('name', 'unknown')
                    size_bytes = model.get('size', 0)
                    size_gb = round(size_bytes / (1024**3), 2) if size_bytes > 0 else 0
                    modified = model.get('modified_at', '').split('.')[0].replace('T', ' ') if 'modified_at' in model else 'unknown'
                    print(f"{model_name:<40} {size_gb:>5} GB     {modified}")
            
            print("\n모델을 설치하려면: ollama pull <모델이름>")
            print("예: ollama pull gemma3:4b")
    except httpx.ConnectError:
        print("\n❌ Ollama 서버에 연결할 수 없습니다. Ollama가 실행 중인지 확인하세요.", file=sys.stderr)
        print("   Ollama를 시작하려면: ollama serve", file=sys.stderr)
    except Exception as e:
        print(f"\n❌ 모델 목록을 가져오는 중 오류가 발생했습니다: {e}", file=sys.stderr)

async def main():
    # Print banner
    print_banner()
    
    # Main parser
    parser = argparse.ArgumentParser(
        description="근육 건강기능식품 연구를 위한 딥 리서치 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "\n사용 예시:\n"
            "  # 기본 사용 (깊이 3, 너비 3):\n"
            "  python cli.py research '근육 성장을 위한 보충제' -q '크레아틴의 효과는?' '단백질 보충제 종류는?'\n\n"
            "  # 파일에서 질문 로드:\n"
            "  python cli.py research '근육 회복' -f examples/muscle_supplement_questions.json\n\n"
            "  # 사용 가능한 모델 목록 보기:\n"
            "  python cli.py list-models\n\n"
            "  # 고급 옵션 (깊이 5, 너비 3, 사용자 정의 출력 디렉토리):\n"
            "  python cli.py research '운동과 영양' -q '운동 전후 영양소 섭취' -d 5 -b 3 -o ./my_research"
        )
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True, help='실행할 명령')
    
    # Research command
    research_parser = subparsers.add_parser('research', 
        help='새로운 연구 시작',
        description='주어진 주제와 질문으로 새로운 연구를 시작합니다.')
    
    research_parser.add_argument('topic', 
        help='연구 주제 (예: "근육 성장을 위한 보충제")')
        
    question_group = research_parser.add_mutually_exclusive_group(required=True)
    question_group.add_argument('-q', '--questions', nargs='+', 
        help='연구할 질문 목록 (공백으로 구분)')
    question_group.add_argument('-f', '--file', 
        help='JSON 파일에서 질문 목록 로드')
    
    research_parser.add_argument('-d', '--depth', type=int, default=2,
        help='피드백 루프 깊이 (기본값: 2, 범위: 1-10)')
    research_parser.add_argument('-b', '--breadth', type=int, default=2,
        help='각 단계의 대체 답변 수 (기본값: 2, 범위: 1-10)')
    research_parser.add_argument('-o', '--output', 
        help='출력 디렉토리 경로 (기본값: ./research_outputs)')
    research_parser.add_argument('--model', 
        help=f'사용할 Ollama 모델 (기본값: gemma3:4b)')
    research_parser.add_argument('--temperature', type=float, default=0.7,
        help='생성 온도 (0.1-1.0, 높을수록 창의적, 기본값: 0.7)')
    
    # List models command
    list_parser = subparsers.add_parser('list-models', 
        help='사용 가능한 Ollama 모델 목록 표시',
        description='현재 Ollama에 설치된 사용 가능한 모델 목록을 표시합니다.')
    list_parser.add_argument('--details', '--show-details', action='store_true', dest='details',
        help='모델 상세 정보 표시')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    try:
        if args.command == 'research':
            if not validate_arguments(args):
                sys.exit(1)
            await run_research(args)
        elif args.command == 'list-models':
            await list_models(args.details)
    except KeyboardInterrupt:
        print("\n작업이 사용자에 의해 중단되었습니다.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}", file=sys.stderr)
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    return 0

if __name__ == "__main__":
    import httpx
    asyncio.run(main())
