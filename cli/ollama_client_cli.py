#!/usr/bin/env python3
"""
Ollama 클라이언트 CLI 도구
OllamaClient 모듈을 위한 독립적인 명령행 인터페이스
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


async def generate_text(args):
    """
    Ollama API를 사용하여 텍스트 생성
    """
    try:
        # 클라이언트 초기화
        client = OllamaClient(
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            min_response_length=args.min_length
        )
        
        # API 가용성 확인
        print("🔄 Ollama API 가용성 확인 중...")
        status = await client.check_availability()
        
        if status["status"] != "available":
            print(f"❌ Ollama API를 사용할 수 없습니다: {status.get('error', '알 수 없는 오류')}")
            return 1
            
        print(f"✅ API 사용 가능: {status.get('current_model', client.model)} 모델")
        
        if "models" in status:
            print(f"🧠 사용 가능한 모델: {', '.join(status.get('models', [])[:5])}")
            if len(status.get('models', [])) > 5:
                print(f"   (외 {len(status.get('models', [])) - 5}개 모델 사용 가능)")
        
        # 프롬프트 준비
        prompt = args.prompt
        system_prompt = args.system
        
        # 프롬프트가 파일에서 오는 경우
        if args.prompt_file:
            if not os.path.exists(args.prompt_file):
                print(f"❌ 파일을 찾을 수 없습니다: {args.prompt_file}")
                return 1
                
            with open(args.prompt_file, 'r', encoding='utf-8') as f:
                prompt = f.read()
        
        # 시스템 프롬프트가 파일에서 오는 경우
        if args.system_file:
            if not os.path.exists(args.system_file):
                print(f"❌ 파일을 찾을 수 없습니다: {args.system_file}")
                return 1
                
            with open(args.system_file, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
        
        # GPU 가속 파라미터 출력
        print(f"🚀 GPU 가속 파라미터:")
        for key, value in client.gpu_params.items():
            print(f"  - {key}: {value}")
        
        # 단일 또는 병렬 생성
        start_time = datetime.now()
        
        if args.parallel > 1:
            # 병렬 생성
            print(f"🔄 프롬프트를 {args.parallel}개 병렬 처리 중...")
            
            # 다양한 온도 설정을 사용하여 여러 프롬프트 생성
            prompts = []
            for i in range(args.parallel):
                temp_variation = args.temperature * (0.8 + 0.4 * (i / args.parallel))
                prompts.append({
                    "prompt": prompt,
                    "system": system_prompt,
                    "temperature": temp_variation
                })
                
            responses = await client.generate_parallel(prompts, max_concurrent=args.concurrent)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"✅ 응답 {len(responses)}개 생성 완료 (소요 시간: {elapsed:.1f}초)")
            
            # 결과 출력
            for i, resp in enumerate(responses):
                print(f"\n===== 응답 #{i+1} =====")
                if isinstance(resp, Exception):
                    print(f"❌ 오류 발생: {str(resp)}")
                else:
                    print(resp[:args.max_display] + ("..." if len(resp) > args.max_display else ""))
            
            # 결과 저장
            if args.output:
                output_file = args.output
                dir_path = os.path.dirname(output_file) if os.path.dirname(output_file) else '.'
                os.makedirs(dir_path, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    for i, resp in enumerate(responses):
                        f.write(f"===== 응답 #{i+1} =====\n\n")
                        if isinstance(resp, Exception):
                            f.write(f"오류: {str(resp)}\n\n")
                        else:
                            f.write(f"{resp}\n\n")
                
                print(f"📁 응답을 '{output_file}' 파일로 저장했습니다.")
        
        else:
            # 단일 생성
            print(f"🔄 응답 생성 중...")
            response = await client.generate(prompt, system_prompt, args.temperature)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"✅ 응답 생성 완료 (소요 시간: {elapsed:.1f}초)")
            
            # 결과 출력
            print(f"\n===== 생성된 응답 =====")
            print(response[:args.max_display] + ("..." if len(response) > args.max_display else ""))
            
            # 결과 저장
            if args.output:
                output_file = args.output
                dir_path = os.path.dirname(output_file) if os.path.dirname(output_file) else '.'
                os.makedirs(dir_path, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(response)
                
                print(f"📁 응답을 '{output_file}' 파일로 저장했습니다.")
        
        return 0
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return 1


async def check_api(args):
    """
    Ollama API 가용성과 모델 목록 확인
    """
    try:
        client = OllamaClient(model=args.model)
        
        print("🔄 Ollama API 가용성 확인 중...")
        status = await client.check_availability()
        
        if status["status"] != "available":
            print(f"❌ Ollama API를 사용할 수 없습니다: {status.get('error', '알 수 없는 오류')}")
            return 1
        
        print(f"✅ Ollama API 사용 가능")
        print(f"🌐 API URL: {client.ollama_url}")
        print(f"🧠 현재 선택된 모델: {client.model}")
        
        if "current_model_available" in status:
            if status["current_model_available"]:
                print(f"✅ 선택된 모델이 사용 가능합니다")
            else:
                print(f"⚠️ 선택된 모델을 찾을 수 없습니다. 사용 가능한 모델 중 하나를 선택하세요.")
        
        if "models" in status:
            print(f"\n사용 가능한 모델 목록 ({len(status.get('models', []))}개):")
            for i, model in enumerate(status.get("models", [])):
                print(f"{i+1}. {model}")
        
        # GPU 가속 파라미터 출력
        print(f"\n🚀 GPU 가속 파라미터:")
        for key, value in client.gpu_params.items():
            print(f"  - {key}: {value}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return 1


async def main():
    parser = argparse.ArgumentParser(
        description='Ollama 클라이언트 CLI 도구',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # 서브파서 설정
    subparsers = parser.add_subparsers(dest='command', help='명령어')
    
    # 텍스트 생성 명령어
    gen_parser = subparsers.add_parser('generate', help='텍스트 생성')
    
    # 프롬프트 입력 방식 (둘 중 하나 필요)
    prompt_group = gen_parser.add_argument_group('프롬프트 입력 옵션 (하나를 선택)')
    prompt_ex = prompt_group.add_mutually_exclusive_group(required=True)
    prompt_ex.add_argument('--prompt', '-p', type=str, help='생성에 사용할 프롬프트')
    prompt_ex.add_argument('--prompt-file', '-pf', type=str, help='프롬프트가 포함된 파일 경로')
    
    # 시스템 프롬프트 옵션
    gen_parser.add_argument('--system', '-s', type=str, default='',
                          help='시스템 프롬프트 (선택사항)')
    gen_parser.add_argument('--system-file', '-sf', type=str, default='',
                          help='시스템 프롬프트가 포함된 파일 경로')
    
    # 생성 매개변수
    gen_parser.add_argument('--model', '-m', type=str, default='gemma3:4b',
                          help='사용할 Ollama 모델')
    gen_parser.add_argument('--temperature', '-t', type=float, default=0.7,
                          help='생성 온도 (0.1~1.0, 높을수록 창의적)')
    gen_parser.add_argument('--max-tokens', '-mt', type=int, default=4000,
                          help='생성할 최대 토큰 수')
    gen_parser.add_argument('--min-length', '-ml', type=int, default=1000,
                          help='응답의 최소 길이')
    gen_parser.add_argument('--parallel', '-pr', type=int, default=1,
                          help='병렬 생성할 응답 수')
    gen_parser.add_argument('--concurrent', '-c', type=int, default=2,
                          help='최대 동시 요청 수')
    gen_parser.add_argument('--output', '-o', type=str, default='',
                          help='결과를 저장할 파일 경로 (생략 시 저장하지 않음)')
    gen_parser.add_argument('--max-display', '-md', type=int, default=1000,
                          help='표시할 최대 문자 수')
    
    # API 확인 명령어
    check_parser = subparsers.add_parser('check', help='API 가용성 및 모델 목록 확인')
    check_parser.add_argument('--model', '-m', type=str, default='gemma3:4b',
                            help='사용할 Ollama 모델')
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        return await generate_text(args)
    elif args.command == 'check':
        return await check_api(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
