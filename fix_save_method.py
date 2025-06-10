#!/usr/bin/env python3
"""
HealthSupplementChatbot 클래스에 save_research_result 메서드를 추가하는 간단한 스크립트
'save_research_result' 속성 오류를 해결합니다
"""

import os
import sys
from pathlib import Path

# 파일 경로
target_file = Path('src/cli/chatbot.py')

def add_save_research_method():
    """
    save_research_result 메서드를 추가합니다
    """
    if not target_file.exists():
        print(f"오류: {target_file} 파일을 찾을 수 없습니다.")
        return False

    # 백업 파일 생성
    backup_file = target_file.with_suffix('.py.bak')
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"원본 파일 백업 완료: {backup_file}")
    
    # 클래스에 save_research_result 메서드 추가
    # process_command 메서드 직후에 추가
    save_method_code = """
    async def save_research_result(self, question: str, response: str, rating_info: dict = None) -> None:
        """
        연구 결과를 파일로 저장
        
        Args:
            question: 사용자 질문
            response: 생성된 응답
            rating_info: 사용자 평가 정보 (선택사항)
        """
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
    
    # process_command 메서드 끝 찾기
    target_pattern = "            return True  # 오류가 있어도 계속 실행"
    
    if target_pattern in content:
        modified_content = content.replace(target_pattern, target_pattern + save_method_code)
        
        # 수정된 내용으로 파일 업데이트
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"{target_file} 파일에 save_research_result 메서드가 성공적으로 추가되었습니다.")
        return True
    else:
        print("타겟 패턴을 찾을 수 없습니다. 파일 구조를 확인해주세요.")
        return False

if __name__ == "__main__":
    add_save_research_method()
