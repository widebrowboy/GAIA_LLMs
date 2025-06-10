#!/usr/bin/env python3
"""
챗봇 코드 구조 수정용 스크립트

HealthSupplementChatbot 클래스의 save_research_result 메서드가
외부 함수로 잘못 정의되어 있는 문제를 해결합니다.
"""

import os
import sys
import re

# 현재 스크립트 경로 기준으로 프로젝트 루트 디렉토리 설정
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
chatbot_file = os.path.join(project_root, "src", "cli", "chatbot.py")

# 수정할 코드 내용
def fix_chatbot_code():
    """
    챗봇 클래스의 코드 구조 수정
    """
    # 파일 읽기
    with open(chatbot_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 백업 파일 생성
    backup_file = chatbot_file + ".bak"
    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"원본 파일 백업 완료: {backup_file}")
    
    # 클래스 내부에 save_research_result 메서드 추가
    # 패턴 1: 마지막 클래스 메서드 뒤에 새 메서드 추가
    pattern_class_end = re.compile(r'(\s+)async def process_command.*?\n(\s+)return True  # 오류가 있어도 계속 실행', re.DOTALL)
    
    save_research_method = """
    async def save_research_result(self, question: str, response: str, rating_info: dict = None) -> None:
        \"\"\"
        연구 결과를 파일로 저장
        
        Args:
            question: 사용자 질문
            response: 생성된 응답
            rating_info: 사용자 평가 정보 (선택사항)
        \"\"\"
"""
        import datetime
        from pathlib import Path
        import json
        from src.utils.config import OUTPUT_DIR
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 질문에서 파일명 생성 (간단하게)
        title_words = question.split()[:5]  # 처음 5개 단어만 사용
        title = "_".join(title_words).replace("/", "").replace("\\\\", "").replace("?", "").replace("!", "")
        
        # 저장 폴더 생성
        output_dir = Path(OUTPUT_DIR) / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 결과 파일 경로
        output_file = output_dir / f"{timestamp}_{title}.md"
        
        # 메타데이터 파일 경로
        meta_file = output_dir / f"{timestamp}_{title}_meta.json"
        
        # 마크다운 파일 저장
        with open(output_file, "w", encoding="utf-8") as f:
            # 제목 추가
            f.write(f"# 근육 건강기능식품 연구: {question}\\n\\n")
            
            # 생성된 결과 추가
            f.write(response)
        
        # 메타데이터 저장
        metadata = {
            "timestamp": timestamp,
            "question": question,
            "settings": self.settings,
            "model": self.settings["model"],
            "feedback_loop": {
                "depth": self.settings["feedback_depth"],
                "width": self.settings["feedback_width"]
            }
        }
        
        # 평가 정보 추가 (있는 경우)
        if rating_info:
            metadata["user_rating"] = rating_info
        
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # 저장 알림 표시
        self.interface.display_saved_notification(str(output_file))
    """
    
    if pattern_class_end.search(content):
        modified_content = pattern_class_end.sub(r'\1async def process_command.*?\n\2return True  # 오류가 있어도 계속 실행\n' + save_research_method, content, count=1)
    else:
        # 패턴을 찾지 못한 경우 클래스 정의 끝에 메서드 추가
        pattern_class = re.compile(r'class HealthSupplementChatbot:.*?(\n\s*)(# 챗봇 런처 구현)', re.DOTALL)
        modified_content = pattern_class.sub(r'class HealthSupplementChatbot:\1' + save_research_method + r'\1\2', content)
    
    # 수정된 내용을 파일에 저장
    with open(chatbot_file, "w", encoding="utf-8") as f:
        f.write(modified_content)
    
    print(f"챗봇 코드 구조가 수정되었습니다. save_research_result 메서드가 클래스에 추가되었습니다.")
    print(f"원본 파일이 {backup_file}에 백업되었습니다.")

if __name__ == "__main__":
    fix_chatbot_code()
