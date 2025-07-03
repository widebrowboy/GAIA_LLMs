import asyncio

from research_agent import ResearchAgent


async def main():
    # 연구 에이전트 초기화
    agent = ResearchAgent(
        model="gemma3:4b",  # Ollama에서 사용할 모델
        temperature=0.7,    # 창의성 조절 (0.1~1.0)
        max_tokens=4000     # 최대 토큰 수
    )

    # 연구 주제
    topic = "근육 성장을 위한 최적의 단백질 보충제"

    # 연구할 질문 목록
    questions = [
        "근육 성장을 위한 최적의 단백질 보충제 종류와 그 효과는 무엇인가요?",
        "근육 회복을 촉진하는 아미노산과 영양소는 무엇이 있나요?"
    ]

    try:
        # 연구 수행
        print(f"🔍 '{topic}' 주제로 연구를 시작합니다...")
        report, metadata = await agent.conduct_research(
            topic=topic,
            questions=questions,
            depth=2,     # 피드백 루프 깊이 (기본값: 2)
            breadth=2    # 대체 답변 생성 수 (기본값: 2)
        )

        # 결과 출력
        print("\n✅ 연구가 완료되었습니다!")
        print(f"📄 보고서 길이: {len(report)}자")
        print(f"⏱️ 소요 시간: {metadata['duration_seconds']:.1f}초")
        print(f"📊 성공한 질문: {len([q for q in metadata['question_details'] if q['status'] == 'success'])}/{len(questions)}")

        # 보고서 저장
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"research_report_{timestamp}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n📂 보고서가 저장되었습니다: {report_file}")

    except Exception as e:
        print(f"❌ 연구 중 오류가 발생했습니다: {e!s}")
        import traceback
        traceback.print_exc()

# 비동기 메인 함수 실행
if __name__ == "__main__":
    asyncio.run(main())
