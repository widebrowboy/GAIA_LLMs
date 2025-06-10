#!/usr/bin/env python3
"""
챗봇 기능 테스트 실행기
주요 기능들에 대한 자동/수동 테스트 지원
"""
import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# 테스트 시나리오
SCENARIOS = {
    "디버그 모드": [
        {"input": "/debug", "expected": "디버그 모드가 켜짐으로 설정되었습니다", "check": "상태 메시지 확인"},
        {"input": "근육 발달에 좋은 보충제는?", "expected": "[디버그]", "check": "디버그 출력 확인"},
        {"input": "/debug", "expected": "디버그 모드가 꺼짐으로 설정되었습니다", "check": "상태 메시지 확인"},
        {"input": "근육 발달에 좋은 보충제는?", "expected": None, "check": "디버그 출력 없음 확인"}
    ],
    "모델 우선순위": [
        {"input": "/settings", "expected": "model: Gemma3:latest", "check": "기본 모델 확인"},
        {"input": "/model txgemma-predict:latest", "expected": "모델이 변경되었습니다", "check": "모델 변경 확인"},
        {"input": "/settings", "expected": "model: txgemma-predict:latest", "check": "변경된 모델 확인"}
    ],
    "저장 프롬프트": [
        {"input": "근육 단백질 합성에 필요한 아미노산은?", "expected": "저장하시겠습니까", "check": "저장 프롬프트 확인"},
        {"input": "y", "expected": "저장되었습니다", "check": "저장 확인 응답"},
        {"input": "크레아틴 효과는?", "expected": "저장하시겠습니까", "check": "저장 프롬프트 확인"},
        {"input": "", "expected": "건너뛰었습니다", "check": "건너뛰기 확인 응답"}
    ],
    "기본 챗봇 기능": [
        {"input": "/help", "expected": "도움말", "check": "도움말 표시 확인"},
        {"input": "/clear", "expected": None, "check": "화면 지우기 확인"},
        {"input": "BCAA의 효과는?", "expected": "## 과학적 근거", "check": "구조화된 응답 확인"},
        {"input": "/feedback 근육 회복에 좋은 보충제는?", "expected": "피드백 루프", "check": "피드백 루프 실행 확인"}
    ]
}

# 테스트 안내와 질문 예시
TEST_EXAMPLES = {
    "디버그 모드": {
        "설명": "디버그 모드를 켜고 끄는 기능을 테스트합니다. 디버그 모드가 켜져 있으면 상세한 정보가 표시됩니다.",
        "질문 예시": [
            "/debug (모드 켜기)",
            "근육 발달에 좋은 보충제는 무엇인가요? (디버그 정보 표시됨)",
            "/debug (모드 끄기)",
            "근육 발달에 좋은 보충제는 무엇인가요? (디버그 정보 표시되지 않음)"
        ]
    },
    "모델 우선순위": {
        "설명": "기본적으로 Gemma3:latest 모델이 선택되며, 이 모델이 없으면 다른 모델로 자동 전환됩니다.",
        "질문 예시": [
            "/settings (현재 모델 확인)",
            "/model txgemma-predict:latest (다른 모델로 변경)",
            "/model Gemma3:latest (기본 모델로 복귀)"
        ]
    },
    "저장 프롬프트": {
        "설명": "응답 생성 후 저장 여부를 물을 때 'y'를 입력하면 저장하고, Enter만 누르면 건너뜁니다.",
        "질문 예시": [
            "근육 단백질 합성에 필요한 아미노산은 무엇인가요? (응답 후)",
            "y (저장)",
            "크레아틴의 효과는 무엇인가요? (응답 후)",
            "(Enter만 누름) (건너뛰기)"
        ]
    },
    "기본 챗봇 기능": {
        "설명": "챗봇의 기본 응답 생성 및 명령어 처리 기능을 테스트합니다.",
        "질문 예시": [
            "/help (도움말 표시)",
            "/clear (화면 지우기)",
            "BCAA의 효과는 과학적으로 입증되었나요? (구조화된 응답)",
            "/feedback 근육 회복에 좋은 보충제는 무엇인가요? (피드백 루프)"
        ]
    }
}

# 추가 테스트 질문 목록
SUPPLEMENT_QUESTIONS = [
    "BCAA 보충제가 근육 회복에 미치는 영향은 무엇인가요?",
    "크레아틴 보충제의 최적 복용량과 타이밍은?",
    "운동 전후 단백질 섭취의 효과적인 방법은?",
    "근육 발달에 가장 중요한 아미노산은 무엇인가요?",
    "비타민 D가 근력에 미치는 영향이 있나요?",
    "테스토스테론 수치를 자연적으로 높이는 방법은?",
    "여성이 근육 발달을 위해 특별히 고려해야 할 영양소는?",
    "근육 회복을 위한 최적의 보충제 조합은?",
    "운동 후 근육통 완화에 효과적인 보충제는 무엇인가요?",
    "나이에 따른 보충제 섭취 전략의 차이점이 있나요?"
]

class ChatbotTester:
    """챗봇 테스트 클래스"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async def run_tests(self):
        """테스트 실행"""
        print("=" * 60)
        print("근육 관련 건강기능식품 연구 챗봇 테스트 가이드")
        print("=" * 60)
        
        # 테스트 환경 확인
        env_ok = await self.check_environment()
        if not env_ok:
            print("❌ 테스트 환경 설정에 문제가 있습니다.")
            return
        
        # 테스트 시나리오 표시
        print("\n📋 테스트 시나리오 및 질문 예시:\n")
        for feature, info in TEST_EXAMPLES.items():
            print(f"🔹 {feature} 테스트")
            print(f"  {info['설명']}")
            print("  질문 예시:")
            for q in info['질문 예시']:
                print(f"  - {q}")
            print()
        
        # 추가 테스트 질문 표시
        print("\n📝 추가 테스트 질문 예시:\n")
        for i, question in enumerate(SUPPLEMENT_QUESTIONS, 1):
            print(f"{i}. {question}")
        
        # 테스트 방법 안내
        print("\n🚀 테스트 방법:\n")
        print("1. 다음 명령으로 챗봇을 실행하세요:")
        print("   python -m src.main")
        print("\n2. 위 질문 예시들을 사용하여 각 기능을 테스트하세요.")
        print("   - 디버그 모드 (/debug)")
        print("   - 모델 우선순위 (/settings, /model)")
        print("   - 저장 프롬프트 (질문 후 'y' 또는 Enter)")
        print("\n3. 테스트 결과를 기록하세요.")
        
        # 디버그 모드의 수동 테스트 지침 표시
        print("\n✅ 디버그 모드 테스트 순서:")
        print("1. /debug 입력 (켜짐 메시지 확인)")
        print("2. 질문 입력 (디버그 정보 출력 확인)")
        print("3. /debug 입력 (꺼짐 메시지 확인)")
        print("4. 질문 입력 (디버그 정보 출력 없음 확인)")
        
        # 저장 프롬프트 테스트 지침 표시
        print("\n✅ 저장 프롬프트 테스트 순서:")
        print("1. 질문 입력 (응답 생성)")
        print("2. 저장 프롬프트에 'y' 입력 (저장 확인)")
        print("3. 다른 질문 입력 (응답 생성)")
        print("4. 저장 프롬프트에 Enter만 입력 (건너뛰기 확인)")
        
        print("\n" + "=" * 60)
        
    async def check_environment(self):
        """테스트 환경 확인"""
        print("\n🔍 테스트 환경 확인 중...")
        
        # 필요한 파일 확인
        files_to_check = [
            "src/cli/chatbot.py",
            "src/cli/interface.py",
            "src/api/ollama_client.py",
            "main.py"
        ]
        
        all_ok = True
        for file in files_to_check:
            path = Path(file)
            if path.exists():
                print(f"  ✅ {file} 파일 존재함")
            else:
                print(f"  ❌ {file} 파일이 존재하지 않음")
                all_ok = False
        
        # .env 파일 확인
        env_path = Path(".env")
        if env_path.exists():
            print("  ✅ .env 파일 존재함")
        else:
            print("  ⚠️ .env 파일이 존재하지 않음 (기본값 사용)")
        
        return all_ok

async def main():
    """메인 함수"""
    tester = ChatbotTester()
    await tester.run_tests()

if __name__ == "__main__":
    asyncio.run(main())
