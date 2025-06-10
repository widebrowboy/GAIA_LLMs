#!/usr/bin/env python3
"""
HealthSupplementChatbot 클래스에 save_research_result 메서드를 직접 추가하는 스크립트
"""

import os
import sys

def add_save_method():
    # 타겟 파일 경로
    file_path = 'src/cli/chatbot.py'
    backup_path = 'src/cli/chatbot.py.bak'
    
    # 백업 파일 생성
    os.system(f'cp {file_path} {backup_path}')
    print(f"원본 파일 백업됨: {backup_path}")
    
    # 새 메서드 텍스트
    new_method = """
    async def save_research_result(self, question: str, response: str, rating_info: dict = None) -> None:
        # 연구 결과를 파일로 저장
        import datetime
        import json
        from pathlib import Path
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
    
    # 파일 내용 읽기
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 메서드 추가 위치 찾기 - process_command 메서드 다음에 추가
    target_pattern = "            return True  # 오류가 있어도 계속 실행"
    if target_pattern in content:
        # 새 메서드 추가
        new_content = content.replace(target_pattern, target_pattern + new_method)
        
        # 파일 저장
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
            
        print(f"save_research_result 메서드가 성공적으로 추가되었습니다.")
        return True
    else:
        print("대상 패턴을 찾을 수 없습니다.")
        return False

if __name__ == "__main__":
    add_save_method()
