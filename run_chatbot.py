#!/usr/bin/env python3
"""
근육 건강기능식품 연구 챗봇 런처

이 스크립트는 CLI 기반 실시간 챗봇을 실행하기 위한 진입점입니다.
모듈 임포트 경로 문제를 해결하고 챗봇을 실행합니다.
"""
import sys
import os
import asyncio

# 프로젝트 루트 디렉토리 설정
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# CLI 챗봇 임포트 및 실행
from src.cli.chatbot import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n프로그램이 종료되었습니다.")
    except Exception as e:
        print(f"\n오류가 발생하여 프로그램이 종료되었습니다: {str(e)}")
