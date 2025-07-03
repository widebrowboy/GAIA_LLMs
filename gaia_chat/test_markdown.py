#!/usr/bin/env python3
"""
마크다운 렌더링 테스트 스크립트
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_markdown_rendering():
    print("🧪 마크다운 렌더링 테스트")
    print("=" * 50)
    
    # 마크다운 컨텐츠가 포함된 질문들
    test_questions = [
        "아스피린의 작용 메커니즘을 단계별로 자세히 설명해주세요",
        "신약개발 과정에서 임상시험 1상, 2상, 3상의 차이점을 표로 정리해주세요",
        "EGFR 억제제의 종류와 특징을 코드 예시와 함께 설명해주세요",
        "분자 타겟팅 치료제 개발 과정을 다음과 같은 형식으로 설명해주세요: 1. 타겟 발견, 2. 리드 화합물, 3. 최적화"
    ]
    
    session_id = f"markdown_test_{int(time.time())}"
    
    # 세션 생성
    try:
        requests.post(f"{API_BASE_URL}/api/session/create", 
                     json={"session_id": session_id}, timeout=10)
        print(f"✅ 테스트 세션 생성: {session_id}")
    except:
        pass
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 테스트 {i}: {question[:50]}...")
        
        try:
            response = requests.post(f"{API_BASE_URL}/api/chat/message",
                                   json={"message": question, "session_id": session_id},
                                   timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                content = result['response']
                
                # 마크다운 요소 확인
                has_headers = any(line.startswith('#') for line in content.split('\n'))
                has_lists = '•' in content or '-' in content or any(line.strip().startswith(('1.', '2.', '3.')) for line in content.split('\n'))
                has_bold = '**' in content
                has_code = '`' in content
                
                print(f"   응답 길이: {len(content)}자")
                print(f"   헤더 포함: {'✅' if has_headers else '❌'}")
                print(f"   리스트 포함: {'✅' if has_lists else '❌'}")
                print(f"   굵은글씨: {'✅' if has_bold else '❌'}")
                print(f"   코드: {'✅' if has_code else '❌'}")
                
                # 응답 미리보기
                preview = content[:200].replace('\n', ' ')
                print(f"   미리보기: {preview}...")
                
            else:
                print(f"   ❌ API 오류: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 예외: {e}")
        
        time.sleep(2)  # API 부하 방지
    
    print("\n" + "=" * 50)
    print("✅ 마크다운 렌더링 테스트 완료!")
    print("🌐 웹 인터페이스에서 확인: http://localhost:3000")
    print("\n💡 확인할 점:")
    print("  • 헤더(#, ##, ###)가 올바르게 스타일링되는지")
    print("  • 리스트(-, •, 1.)가 들여쓰기와 함께 표시되는지")
    print("  • 굵은글씨(**text**)가 볼드 처리되는지")
    print("  • 인라인 코드(`code`)가 회색 배경으로 표시되는지")
    print("  • 코드 블록(```)이 어두운 배경으로 표시되는지")

if __name__ == "__main__":
    test_markdown_rendering()