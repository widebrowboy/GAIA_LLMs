#!/usr/bin/env python3
"""
파일 저장 모듈
연구 결과를 마크다운 및 메타데이터 파일로 저장
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import aiofiles

class FileStorage:
    """
    연구 결과 파일 저장 클래스
    마크다운 형식 연구 결과 및 JSON 메타데이터 저장
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        파일 저장 관리자 초기화
        
        Args:
            base_dir: 기본 저장 디렉토리 (없으면 환경 변수 또는 기본값 사용)
        """
        # 기본 저장 디렉토리 설정
        self.base_dir = base_dir or os.getenv('OUTPUT_DIR', './research_outputs')
        
        # 디렉토리 존재 확인 및 생성
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir, exist_ok=True)
    
    async def create_session_directory(self, session_id: Optional[str] = None) -> str:
        """
        연구 세션 디렉토리 생성
        
        Args:
            session_id: 세션 식별자 (없으면 현재 시간 사용)
            
        Returns:
            str: 생성된 디렉토리 경로
        """
        # 세션 ID 없으면 현재 시간으로 생성
        if not session_id:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
        # 세션 디렉토리 경로 생성
        session_dir = os.path.join(self.base_dir, session_id)
        
        # 디렉토리 생성
        os.makedirs(session_dir, exist_ok=True)
        
        return session_dir
    
    async def save_research_result(self, 
                                 content: str, 
                                 metadata: Dict[str, Any],
                                 session_id: Optional[str] = None,
                                 filename_base: Optional[str] = None) -> Dict[str, str]:
        """
        연구 결과 및 메타데이터 저장
        
        Args:
            content: 저장할 마크다운 내용
            metadata: 저장할 메타데이터
            session_id: 세션 식별자 (없으면 현재 시간 사용)
            filename_base: 파일명 기본 부분 (없으면 메타데이터에서 생성)
            
        Returns:
            Dict[str, str]: 저장된 파일 경로들
        """
        # 세션 디렉토리 생성
        session_dir = await self.create_session_directory(session_id)
        
        # 파일명 기본 부분 생성
        if not filename_base:
            question = metadata.get('question', '')
            question_id = metadata.get('question_id', '')
            
            if question:
                # 질문에서 알파벳과 숫자만 추출하여 파일명 생성
                import re
                safe_name = ''.join(filter(str.isalnum, question[:30]))
                filename_base = f"{question_id}_{safe_name}" if question_id else safe_name
            else:
                # 메타데이터가 없는 경우 타임스탬프 사용
                filename_base = datetime.now().strftime("result_%Y%m%d_%H%M%S")
        
        # 파일 경로 설정
        md_filename = f"{filename_base}.md"
        json_filename = f"{filename_base}_meta.json"
        
        md_path = os.path.join(session_dir, md_filename)
        json_path = os.path.join(session_dir, json_filename)
        
        # 타임스탬프 추가
        metadata['timestamp'] = datetime.now().isoformat()
        metadata['saved_files'] = {
            'markdown': md_filename,
            'metadata': json_filename
        }
        
        try:
            # 비동기로 파일 저장
            async with aiofiles.open(md_path, 'w', encoding='utf-8') as f:
                await f.write(content)
                
            async with aiofiles.open(json_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(metadata, ensure_ascii=False, indent=2))
                
            return {
                'markdown': md_path,
                'metadata': json_path,
                'session_dir': session_dir
            }
            
        except Exception as e:
            print(f"파일 저장 중 오류 발생: {str(e)}")
            # 동기 방식으로 재시도
            try:
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                with open(json_path, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(metadata, ensure_ascii=False, indent=2))
                    
                return {
                    'markdown': md_path,
                    'metadata': json_path,
                    'session_dir': session_dir
                }
            except Exception as e:
                print(f"파일 저장 재시도 중 오류 발생: {str(e)}")
                return {
                    'error': str(e),
                    'session_dir': session_dir
                }
    
    async def save_summary(self, 
                         summary: Dict[str, Any],
                         session_id: Optional[str] = None) -> str:
        """
        연구 요약 정보 저장
        
        Args:
            summary: 저장할 요약 정보
            session_id: 세션 식별자 (없으면 현재 시간 사용)
            
        Returns:
            str: 저장된 파일 경로
        """
        # 세션 디렉토리 생성
        session_dir = await self.create_session_directory(session_id)
        
        # 파일명 설정
        summary_filename = "research_summary.json"
        summary_path = os.path.join(session_dir, summary_filename)
        
        # 타임스탬프 추가
        if 'timestamp' not in summary:
            summary['timestamp'] = datetime.now().isoformat()
            
        try:
            # 비동기로 파일 저장
            async with aiofiles.open(summary_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(summary, ensure_ascii=False, indent=2))
                
            return summary_path
            
        except Exception as e:
            print(f"요약 정보 저장 중 오류 발생: {str(e)}")
            # 동기 방식으로 재시도
            try:
                with open(summary_path, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(summary, ensure_ascii=False, indent=2))
                return summary_path
            except Exception as e:
                print(f"요약 정보 저장 재시도 중 오류 발생: {str(e)}")
                return ''
    
    async def read_research_result(self, 
                                 md_path: str) -> Dict[str, Any]:
        """
        저장된 연구 결과 읽기
        
        Args:
            md_path: 마크다운 파일 경로
            
        Returns:
            Dict[str, Any]: 연구 결과 및 메타데이터
        """
        # 마크다운 파일 경로에서 메타데이터 파일 경로 유추
        json_path = md_path.replace('.md', '_meta.json')
        if not os.path.exists(json_path):
            # 파일명이 다른 경우 동일 디렉토리에서 검색
            dirname = os.path.dirname(md_path)
            basename = os.path.basename(md_path).replace('.md', '')
            
            # 가능한 메타데이터 파일명 패턴
            possible_names = [
                f"{basename}_meta.json",
                f"{basename}.meta.json",
                f"{basename}_metadata.json"
            ]
            
            for name in possible_names:
                test_path = os.path.join(dirname, name)
                if os.path.exists(test_path):
                    json_path = test_path
                    break
        
        try:
            # 마크다운 내용 읽기
            if os.path.exists(md_path):
                async with aiofiles.open(md_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
            else:
                content = "파일을 찾을 수 없습니다."
                
            # 메타데이터 읽기
            metadata = {}
            if os.path.exists(json_path):
                async with aiofiles.open(json_path, 'r', encoding='utf-8') as f:
                    json_content = await f.read()
                    metadata = json.loads(json_content)
            
            return {
                'content': content,
                'metadata': metadata,
                'md_path': md_path,
                'json_path': json_path if os.path.exists(json_path) else None
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'md_path': md_path,
                'json_path': json_path if os.path.exists(json_path) else None
            }


# 모듈 직접 실행 시 테스트
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='파일 저장 모듈 테스트')
    parser.add_argument('--dir', '-d', type=str, default=None,
                       help='저장 디렉토리 (기본값: ./research_outputs)')
    parser.add_argument('--read', '-r', type=str, default=None,
                       help='읽을 마크다운 파일 경로')
    
    args = parser.parse_args()
    
    async def test():
        # 파일 저장 관리자 생성
        storage = FileStorage(args.dir)
        
        # 파일 읽기 테스트
        if args.read:
            if os.path.exists(args.read):
                print(f"파일 읽기: {args.read}")
                result = await storage.read_research_result(args.read)
                
                if 'error' in result:
                    print(f"❌ 파일 읽기 오류: {result['error']}")
                else:
                    print(f"✅ 파일 읽기 성공")
                    print(f"마크다운 길이: {len(result['content'])} 자")
                    print(f"메타데이터: {json.dumps(result['metadata'], ensure_ascii=False, indent=2)}")
            else:
                print(f"❌ 파일이 존재하지 않습니다: {args.read}")
                return
        
        # 파일 쓰기 테스트
        else:
            # 테스트 데이터
            test_content = """# 테스트 연구 결과

## 문제 정의
이것은 테스트를 위한 샘플 마크다운 파일입니다.

## 핵심 내용
파일 저장 모듈 테스트를 위한 내용입니다.

## 참고 문헌
1. 테스트 참고 문헌 (https://example.com)
2. 샘플 URL (https://sample.org)
"""
            test_metadata = {
                "question": "테스트 질문입니다",
                "question_id": "TEST01",
                "score": 8.5,
                "feedback_loops": 2
            }
            
            # 세션 디렉토리 생성 테스트
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S_test")
            session_dir = await storage.create_session_directory(session_id)
            print(f"생성된 세션 디렉토리: {session_dir}")
            
            # 파일 저장 테스트
            print("파일 저장 중...")
            result = await storage.save_research_result(
                test_content,
                test_metadata,
                session_id
            )
            
            if 'error' in result:
                print(f"❌ 파일 저장 오류: {result['error']}")
            else:
                print(f"✅ 파일 저장 성공")
                print(f"마크다운 파일: {result['markdown']}")
                print(f"메타데이터 파일: {result['metadata']}")
                
                # 요약 정보 저장 테스트
                summary = {
                    "session_id": session_id,
                    "total_questions": 1,
                    "completed_questions": 1,
                    "total_feedback_loops": 2,
                    "results": [{"question_id": "TEST01", "status": "completed"}]
                }
                
                summary_path = await storage.save_summary(summary, session_id)
                print(f"요약 정보 저장: {summary_path}")
                
                # 저장된 파일 읽기 테스트
                print("\n저장된 파일 읽기 테스트...")
                read_result = await storage.read_research_result(result['markdown'])
                
                if 'error' in read_result:
                    print(f"❌ 파일 읽기 오류: {read_result['error']}")
                else:
                    print(f"✅ 파일 읽기 성공")
                    print(f"마크다운 내용 일치: {read_result['content'] == test_content}")
                    
    asyncio.run(test())
