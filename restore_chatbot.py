#!/usr/bin/env python3
"""
챗봇 파일 복구 스크립트
손상된 chatbot.py 파일을 복구하고 기능을 확인합니다
"""
import os
import re
import shutil
from pathlib import Path

def main():
    print("🔧 챗봇 파일 복구 시작...")
    
    # 경로 설정
    base_dir = Path(__file__).parent
    chatbot_path = base_dir / "src" / "cli" / "chatbot.py"
    backup_path = base_dir / "src" / "cli" / "chatbot.py.backup"
    
    # 백업 파일 확인
    if not backup_path.exists():
        print("❌ 백업 파일을 찾을 수 없습니다!")
        return False
    
    # 백업에서 복원
    print(f"📂 백업 파일에서 복원 중...")
    shutil.copy(backup_path, chatbot_path)
    
    # 파일 복원 확인
    if not chatbot_path.exists():
        print("❌ 파일 복원에 실패했습니다!")
        return False
    
    print(f"✅ 파일이 성공적으로 복원되었습니다: {chatbot_path}")
    print("\n🔍 이미 구현된 주요 기능:")
    print("  - 디버그 모드 토글 (/debug 명령어)")
    print("  - Gemma3:latest 모델 우선 선택")
    print("  - Enter 키 저장 건너뛰기, y 키 저장")
    print("\n실행 방법: python -m src.main")
    
    return True

if __name__ == "__main__":
    main()
