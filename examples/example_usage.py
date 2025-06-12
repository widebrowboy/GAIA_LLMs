#!/usr/bin/env python3
"""
근육 관련 건강기능식품 연구 에이전트 예제

이 스크립트는 ResearchAgent를 사용하여 근육 관련 건강기능식품에 대한 연구를 수행하는 방법을 보여줍니다.
"""
import asyncio

from research_agent import ResearchAgent


async def main():
    print("🔍 근육 건강기능식품 연구 에이전트를 시작합니다...\n")

    # ResearchAgent 초기화 (Gemma3 모델 사용)
    agent = ResearchAgent()

    # 연구 주제와 질문 정의
    research_topic = "근육 성장과 회복을 위한 건강기능식품"
    research_questions = [
        "근육 성장에 가장 효과적인 단백질 보충제의 종류와 그 작용 메커니즘은 무엇인가요?",
        "크레아틴의 근육 성장에 대한 효과와 복용 방법, 부작용에 대해 자세히 설명해주세요. "
        "(참고 문헌: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3407788/)",
        "BCAA(분기사슬 아미노산)가 근육 회복에 미치는 영향과 과학적 근거는 무엇인가요?",
        "근육 성장을 위한 영양제 복용 시기(타이밍)가 중요한 이유와 최적의 복용 시기는 언제인가요?",
        "근육통 완화에 도움이 되는 천연 성분과 그 작용 원리에 대해 설명해주세요."
    ]

    # 연구 매개변수 설정 (.windsurfrules에 따라 깊이/너비 3/3으로 설정)
    depth = 3  # 피드백 루프 깊이
    breadth = 3  # 각 단계의 대체 답변 수

    # 연구 실행
    try:
        print(f"📌 연구 주제: {research_topic}")
        print(f"📊 깊이(Depth): {depth}, 너비(Breadth): {breadth}")
        print(f"📝 질문 수: {len(research_questions)}개\n")

        # 연구 수행
        output_file, metadata = await agent.conduct_research(
            topic=research_topic,
            research_questions=research_questions,
            depth=depth,
            breadth=breadth
        )

        print(f"\n✅ 연구가 완료되었습니다! 결과 파일: {output_file}")

    except Exception as e:
        print(f"\n❌ 연구 중 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
