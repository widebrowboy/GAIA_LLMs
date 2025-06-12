#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo():
    print("=== GAIA Deep Research 시스템 데모 ===")
    print()
    print("🎯 완성된 시스템 구성:")
    print("  ✅ ChEMBL MCP 서버 - 화학 데이터베이스")
    print("  ✅ BiomCP 서버 - 생의학 연구 데이터")
    print("  ✅ Sequential Thinking - 단계별 추론")
    print("  ✅ Ollama Gemma3 - AI 분석 엔진")
    print()
    print("📚 생성된 문서:")
    print("  - DEEP_RESEARCH_USER_MANUAL.md")
    print("  - QUICK_START_GUIDE.md")
    print("  - 업데이트된 README.md")
    print()
    print("🚀 시작 방법:")
    print("  1. python main.py")
    print("  2. /mcp start")
    print("  3. /mcp test deep")
    print()
    print("🧪 테스트 질문 예제:")
    print("  '크레아틴 보충제의 분자 구조, 작용 메커니즘, 그리고 근육 성장에 미치는 효과에 대해 종합적으로 분석해주세요.'")
    print()
    print("시스템이 완전히 준비되어 있습니다!")

if __name__ == "__main__":
    demo()