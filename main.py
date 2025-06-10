#!/usr/bin/env python3
"""
근육 관련 건강기능식품 연구 시스템 메인 모듈
CLI를 통한 연구 시스템 실행
"""

import sys
import asyncio
from src.cli.chatbot import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n프로그램이 종료되었습니다.")
    except Exception as e:
        print(f"\n오류가 발생하여 프로그램이 종료되었습니다: {str(e)}")
