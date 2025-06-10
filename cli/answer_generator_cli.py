#!/usr/bin/env python3
"""
답변 생성기 CLI 도구
AnswerGenerator 모듈을 위한 독립적인 명령행 인터페이스
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

# 상위 디렉토리를 모듈 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 모듈 임포트
from src.api.ollama_client import OllamaClient
from src.research.answer_generator import AnswerGenerator


async def generate_answer(args):
    """
    질문에 대한 답변 생성
    """
    try:
        # 시작 메시지 출력
        print(f"📝 답변 생성 시작: '{args.question}'")
        
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
        
        # 생성기 초기화 및 답변 생성
        generator = AnswerGenerator(client)
        
        start_time = datetime.now()
        
        if args.alternatives:
            print(f"🔄 대체 답변 {args.alternatives}개 생성 중...")
            answers = await generator.generate_alternative_answers(args.question, count=args.alternatives)
            for i, answer in enumerate(answers, 1):
                print(f"\n===== 대체 답변 #{i} =====\n")
                print(answer[:args.max_length] + ("..." if len(answer) > args.max_length else ""))
        else:
            print("🔄 답변 생성 중...")
            answer = await generator.generate_answer(args.question)
            print("\n===== 생성된 답변 =====\n")
            print(answer[:args.max_length] + ("..." if len(answer) > args.max_length else ""))
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n✅ 답변 생성 완료 (소요 시간: {elapsed:.1f}초)")
        
        # 파일로 저장
        if args.output:
            output_file = args.output
            dir_path = os.path.dirname(output_file) if os.path.dirname(output_file) else '.'
            os.makedirs(dir_path, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                if args.alternatives:
                    for i, ans in enumerate(answers, 1):
                        f.write(f"===== 대체 답변 #{i} =====\n\n")
                        f.write(ans)
                        f.write("\n\n")
                else:
                    f.write(answer)
            
            print(f"📁 답변을 '{output_file}' 파일로 저장했습니다.")
            
        return 0
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return 1


async def main():
    parser = argparse.ArgumentParser(
        description='답변 생성기 CLI 도구',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # 필수 인자
    parser.add_argument('question', type=str, help='답변을 생성할 질문')
    
    # 선택 인자
    parser.add_argument('--model', '-m', type=str, default='gemma3:4b',
                      help='사용할 Ollama 모델')
    parser.add_argument('--temperature', '-t', type=float, default=0.7,
                      help='생성 온도 (0.1~1.0, 높을수록 창의적)')
    parser.add_argument('--alternatives', '-a', type=int, default=0,
                      help='생성할 대체 답변 수 (0이면 단일 답변 생성)')
    parser.add_argument('--output', '-o', type=str, default='',
                      help='결과를 저장할 파일 경로 (생략 시 저장하지 않음)')
    parser.add_argument('--max-length', '-l', type=int, default=1000,
                      help='출력할 답변의 최대 문자 수')
    
    args = parser.parse_args()
    return await generate_answer(args)


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
