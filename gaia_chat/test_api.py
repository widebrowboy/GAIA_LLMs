#!/usr/bin/env python3
"""
GAIA Chat Next.js API 테스트 스크립트
"""

import requests
import json
import time

BASE_URL = "http://localhost:3000"

def test_api():
    print("🧪 GAIA Chat Next.js API 테스트 시작")
    print("=" * 50)
    
    # 1. 서버 상태 확인
    try:
        response = requests.get(f"{BASE_URL}")
        print(f"✅ 서버 응답: {response.status_code}")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return
    
    # 2. 빈 대화 목록 확인
    response = requests.get(f"{BASE_URL}/api/chat")
    conversations = response.json()
    print(f"📝 초기 대화 수: {len(conversations)}")
    
    # 3. 새 대화 생성
    new_conversation = {
        "title": "API 테스트 대화"
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=new_conversation)
    conversation = response.json()
    conversation_id = conversation["id"]
    print(f"✨ 새 대화 생성: {conversation['title']} (ID: {conversation_id[:8]}...)")
    
    # 4. 메시지 전송
    messages = [
        "안녕하세요",
        "GAIA Chat이 잘 작동하나요?",
        "도움이 필요합니다",
        "감사합니다"
    ]
    
    for i, message_content in enumerate(messages, 1):
        message = {
            "content": message_content,
            "conversationId": conversation_id
        }
        response = requests.post(f"{BASE_URL}/api/chat/messages", json=message)
        result = response.json()
        
        if response.status_code == 200:
            print(f"💬 메시지 {i}: '{message_content}' → AI 응답 길이: {len(result['assistantMessage']['content'])}자")
        else:
            print(f"❌ 메시지 {i} 전송 실패: {result}")
        
        time.sleep(0.5)  # API 부하 방지
    
    # 5. 최종 대화 목록 확인
    response = requests.get(f"{BASE_URL}/api/chat")
    conversations = response.json()
    print(f"📋 최종 대화 수: {len(conversations)}")
    
    if conversations:
        final_conversation = conversations[0]
        print(f"💭 마지막 대화: '{final_conversation['title']}' - {len(final_conversation['messages'])}개 메시지")
        
        # 마지막 AI 응답 출력
        if final_conversation['messages']:
            last_message = final_conversation['messages'][-1]
            if last_message['role'] == 'assistant':
                print(f"🤖 마지막 AI 응답: {last_message['content'][:100]}...")
    
    print("=" * 50)
    print("✅ 모든 테스트 완료!")
    print(f"🌐 웹 인터페이스: {BASE_URL}")
    print(f"🔗 API 엔드포인트: {BASE_URL}/api")

if __name__ == "__main__":
    test_api()