#!/usr/bin/env python3
"""
GAIA-BT 신약개발 연구 시스템 메인 모듈
CLI를 통한 연구 시스템 실행
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from app.cli.chatbot import main

if __name__ == "__main__":
    # 커맨드라인 인자 파서 생성
    parser = argparse.ArgumentParser(description="GAIA-BT 신약개발 연구 챗봇")
    parser.add_argument("--debug", action="store_true", help="디버그 모드 활성화")
    args = parser.parse_args()

    try:
        asyncio.run(main(debug_mode=args.debug))
    except KeyboardInterrupt:
        print("\n프로그램이 종료되었습니다.")
    except Exception as e:
        print(f"\n오류가 발생하여 프로그램이 종료되었습니다: {e!s}")

