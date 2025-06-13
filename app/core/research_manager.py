#!/usr/bin/env python3
"""
연구 관리 모듈
신약개발 연구 프로세스 총괄 관리
"""

import asyncio
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.api.ollama_client import OllamaClient
from app.core.answer_evaluator import AnswerEvaluator
from app.core.file_storage import FileStorage
from app.core.answer_generator import AnswerGenerator
from app.core.question_handler import QuestionHandler
from app.core.research_parallel import ResearchParallel
from app.core.biomcp_integration import BioMCPIntegration


class ResearchManager:
    """
    신약개발 연구 프로세스 관리 클래스
    질문 처리부터 답변 생성, 피드백, 저장까지 전체 프로세스 관리
    """

    def __init__(self,
                ollama_client: Optional[OllamaClient] = None,
                feedback_depth: int = 2,
                feedback_width: int = 2,
                concurrent_research: int = 2,
                output_dir: Optional[str] = None,
                mcp_manager=None):
        """
        연구 관리자 초기화

        Args:
            ollama_client: OllamaClient 인스턴스 (없으면 새로 생성)
            feedback_depth: 피드백 루프 깊이 (기본값: 2)
            feedback_width: 피드백 루프 너비 (기본값: 2)
            concurrent_research: 동시 연구 프로세스 수 (기본값: 2)
            output_dir: 결과 저장 디렉토리 (기본값: environment OUTPUT_DIR)
            mcp_manager: MCP Manager 인스턴스 (옵션)
        """
        # 컴포넌트 초기화
        self.client = ollama_client or OllamaClient()
        self.question_handler = QuestionHandler(self.client)
        self.answer_generator = AnswerGenerator(self.client)
        self.evaluator = AnswerEvaluator(self.client)
        self.parallel_executor = ResearchParallel(self.client, concurrent_research)
        
        # MCP 통합 초기화
        self.mcp_manager = mcp_manager
        self.biomcp = BioMCPIntegration(mcp_manager) if mcp_manager else None

        # 환경 설정
        self.output_dir = output_dir or os.getenv('OUTPUT_DIR', './research_outputs')
        self.file_storage = FileStorage(self.output_dir)

        # 피드백 설정
        self.feedback_depth = max(1, min(feedback_depth, 10))  # 1~10 범위 확인
        self.feedback_width = max(1, min(feedback_width, 10))  # 1~10 범위 확인
        self.concurrent_research = concurrent_research

        # 세션 식별자 설정 (타임스탬프)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 실행 통계
        self.stats = {
            "start_time": None,
            "end_time": None,
            "total_questions": 0,
            "completed_questions": 0,
            "failed_questions": 0,
            "total_feedback_loops": 0
        }

    async def load_questions(self, questions_file: Optional[str] = None, questions: Optional[List[str]] = None) -> List[str]:
        """
        연구 질문 로드

        Args:
            questions_file: 질문 목록 파일 경로 (JSON 또는 텍스트)
            questions: 직접 제공된 질문 목록

        Returns:
            List[str]: 로드된 질문 목록
        """
        if questions:
            return list(questions)

        if questions_file:
            return await self.question_handler.load_questions_from_file(questions_file)

        # 기본 예시 질문
        return [
            "신약개발에서 분자 타겟 발굴의 주요 접근법은 무엇인가요?",
            "전임상 독성시험의 주요 단계와 평가 항목은 무엇인가요?",
            "항암제 개발에서 바이오마커의 역할과 중요성은 무엇인가요?"
        ]

    async def run_research(self, questions: Optional[List[str]] = None, questions_file: Optional[str] = None) -> Dict[str, Any]:
        """
        질문 목록에 대한 연구 진행

        Args:
            questions: 직접 제공된 질문 목록
            questions_file: 질문 목록 파일 경로

        Returns:
            Dict[str, Any]: 연구 결과 요약
        """
        # 타이머 시작
        self.stats["start_time"] = time.time()

        # 질문 로드
        research_questions = await self.load_questions(questions_file, questions)
        self.stats["total_questions"] = len(research_questions)

        print(f"===== 신약개발 연구 시작 ({len(research_questions)}개 질문) =====")
        print(f"- 피드백 루프: 깊이={self.feedback_depth}, 너비={self.feedback_width}")
        print(f"- 동시 연구 진행: {self.concurrent_research}개")

        # 결과를 저장할 디렉토리 생성
        research_dir = await self.file_storage.create_session_directory(self.session_id)
        print(f"- 결과 저장 위치: {research_dir}")

        # API 가용성 확인
        status = await self.client.check_availability()
        if status["status"] != "available":
            print(f"❌ Ollama API를 사용할 수 없습니다: {status.get('error', '알 수 없는 오류')}")
            return {"error": "API 사용 불가", "stats": self.stats}

        print(f"\n🚀 {status['current_model']} 모델 사용 중...\n")

        # 세마포어를 사용하여 동시 연구 수 제한
        semaphore = asyncio.Semaphore(self.concurrent_research)

        # 각 질문에 대한 연구 프로세스 실행
        async def research_question(idx: int, question: str):
            async with semaphore:
                qid = f"Q{idx+1:02d}"
                try:
                    print(f"\n[{qid}] 연구 시작: '{question[:50]}...'")

                    # 연구 질문에 대한 처리 수행
                    result = await self.research_question(question, question_id=qid)

                    if 'error' in result:
                        print(f"[{qid}] ❌ 연구 실패: {result['error']}")
                        self.stats["failed_questions"] += 1
                        return {"question": question, "error": result['error'], "question_id": qid, "status": "failed"}

                    self.stats["total_feedback_loops"] += result.get("feedback_loops", 0)
                    self.stats["completed_questions"] += 1

                    print(f"[{qid}] ✅ 연구 완료 (점수: {result.get('score', 'N/A')}, 루프: {result.get('feedback_loops', 0)}회)")

                    return result

                except Exception as e:
                    print(f"[{qid}] ❌ 오류 발생: {e!s}")
                    self.stats["failed_questions"] += 1
                    return {"question": question, "question_id": qid, "error": str(e), "status": "failed"}

        # 모든 질문 동시 연구 수행
        time.time()
        tasks = [research_question(i, q) for i, q in enumerate(research_questions)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 통계 정보 업데이트
        self.stats["end_time"] = time.time()
        elapsed = self.stats["end_time"] - self.stats["start_time"]

        # 요약 정보
        summary = {
            "session_id": self.session_id,
            "output_directory": research_dir,
            "total_questions": self.stats["total_questions"],
            "completed_questions": self.stats["completed_questions"],
            "failed_questions": self.stats["failed_questions"],
            "total_feedback_loops": self.stats["total_feedback_loops"],
            "elapsed_seconds": elapsed,
            "model": status["current_model"],
            "feedback_settings": {
                "depth": self.feedback_depth,
                "width": self.feedback_width
            },
            "results": results
        }

        # 요약 정보 저장
        await self.file_storage.save_summary(summary, self.session_id)

        # 완료 정보 출력
        print("\n===== 연구 완료 =====")
        print(f"- 총 질문: {self.stats['total_questions']}개")
        print(f"- 완료: {self.stats['completed_questions']}개")
        print(f"- 실패: {self.stats['failed_questions']}개")
        print(f"- 총 피드백 루프: {self.stats['total_feedback_loops']}회")
        print(f"- 소요 시간: {elapsed:.1f}초")
        print(f"- 결과 저장 위치: {research_dir}")

        return summary

    async def research_question(self, question: str, question_id: Optional[str] = None) -> Dict[str, Any]:
        """
        단일 질문에 대한 연구 수행

        Args:
            question: 연구 질문
            question_id: 질문 식별자 (기본값: 자동 생성)

        Returns:
            Dict[str, Any]: 연구 결과
        """
        # 질문 ID가 없으면 생성
        qid = question_id or f"Q{int(time.time())%1000:03d}"

        try:
            # 대체 답변 병렬 생성 (width만큼)
            print(f"[{qid}] {self.feedback_width}개의 대체 답변 병렬 생성 중...")
            template = "다음 질문에 대해 신약개발 전문가로서 과학적 근거와 참고문헌을 포함하여 상세히 답변해주세요:\n\n{question}"
            system_prompt = """당신은 신약개발 전문가입니다. 다음 형식으로 답변하세요:
            1. 문제 정의
            2. 핵심 내용 (이론, 개념, 원리)
            3. 과학적 근거 (연구 결과, 데이터)
            4. 임상시험 및 개발 단계
            5. 결론 및 요약
            6. 참고 문헌 (최소 2개)

            답변은 최소 1000자 이상이어야 하며, 항상 과학적 근거와 참고문헌을 포함해야 합니다."""

            alternative_answers = await self.parallel_executor.generate_alternative_answers(
                question=question,
                prompt_template=template,
                system_prompt=system_prompt,
                width=self.feedback_width
            )

            # 각 답변 평가 (병렬)
            print(f"[{qid}] 대체 답변 평가 중...")
            evaluation_tasks = []
            for answer in alternative_answers:
                evaluation_tasks.append(
                    self.evaluator.evaluate_answer(question=question, answer=answer)
                )

            evaluations = await asyncio.gather(*evaluation_tasks)

            # 최고 점수의 답변 선택
            scores = [evaluation.get("score", 0) for evaluation in evaluations]
            best_idx = scores.index(max(scores))

            # 현재 답변 설정 (최고 점수)
            current_answer = alternative_answers[best_idx]
            current_score = scores[best_idx]
            current_feedback = evaluations[best_idx].get("feedback", "")

            print(f"[{qid}] 최고 점수 답변 선택: {current_score}/10")

            # 답변 히스토리 초기화
            answer_history = [
                {
                    "iteration": 0,
                    "answer": current_answer,
                    "feedback": current_feedback,
                    "score": current_score,
                    "timestamp": datetime.now().isoformat()
                }
            ]

            # 피드백 루프 실행
            for i in range(1, self.feedback_depth + 1):
                # 종료 조건: 충분히 높은 점수
                if current_score >= 9.0:  # 9점 이상이면 충분히 좋은 답변
                    print(f"[{qid}] ✨ 충분히 높은 점수 달성 ({current_score}/10), 피드백 루프 종료")
                    break

                # 마지막 루프가 아닌 경우 개선된 답변 생성
                print(f"[{qid}] 피드백 루프 {i}/{self.feedback_depth}: 답변 개선 중...")
                improved_answer = await self.answer_generator.improve_answer(
                    question=question,
                    previous_answer=current_answer,
                    feedback=current_feedback
                )

                # 개선된 답변 평가
                evaluation = await self.evaluator.evaluate_answer(
                    question=question,
                    answer=improved_answer
                )

                # 점수 및 피드백 추출
                score = evaluation.get("score", 0)
                feedback = evaluation.get("feedback", "")

                # 점수가 더 높아졌으면 업데이트
                if score > current_score:
                    current_answer = improved_answer
                    current_score = score
                    current_feedback = feedback
                    print(f"[{qid}] 점수 향상: {score}/10 ⬆️")
                else:
                    print(f"[{qid}] 점수 유지/감소: {score}/10 (이전 답변 유지)")

                # 히스토리에 추가
                answer_history.append({
                    "iteration": i,
                    "answer": improved_answer,
                    "feedback": feedback,
                    "score": score,
                    "timestamp": datetime.now().isoformat()
                })

            # 결과 저장
            result = {
                "question_id": qid,
                "question": question,
                "final_answer": current_answer,
                "score": current_score,
                "feedback_loops": len(answer_history) - 1,  # 초기 답변 제외
                "answer_history": answer_history,
                "timestamp": datetime.now().isoformat()
            }

            # 파일로 저장
            await self.file_storage.save_research_result(result, self.session_id, qid)

            return result

        except Exception as e:
            # 오류 처리
            error_msg = f"연구 오류: {e!s}"
            return {
                "question_id": qid,
                "question": question,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }

    async def conduct_research(self, questions: List[str], concurrent_limit: Optional[int] = None) -> Dict[str, Any]:
        """
        질문 목록에 대한 심층 연구 수행 - GPU 가속 및 병렬 처리 최적화

        Args:
            questions: 연구할 질문 목록
            concurrent_limit: 동시 연구 수 제한 (기본값: self.concurrent_research)

        Returns:
            Dict[str, Any]: 연구 결과 요약
        """
        start_time = time.time()

        # 연구 작업 디렉토리 준비
        research_dir = os.path.join(self.output_dir, self.session_id)
        os.makedirs(research_dir, exist_ok=True)

        # 각 질문에 대한 결과를 저장할 디렉토리
        os.makedirs(os.path.join(research_dir, "questions"), exist_ok=True)

        # 총 질문 수 기록
        stats = {
            "total_questions": len(questions),
            "completed": 0,
            "failed": 0,
            "total_loops": 0
        }

        # 각 질문에 대한 연구 프로세스 정의
        async def process_question(idx: int, q: str):
            qid = f"Q{idx+1:02d}"
            print(f"\n[{qid}] 연구 시작: '{q[:50]}...'")

            result = await self.research_question(q, qid)

            if 'error' in result:
                stats["failed"] += 1
                print(f"[{qid}] ❌ 연구 실패: {result['error']}")
            else:
                stats["completed"] += 1
                stats["total_loops"] += result.get("feedback_loops", 0)
                print(f"[{qid}] ✅ 연구 완료 (점수: {result.get('score', 'N/A')}/10)")

            return result

        # ResearchParallel을 사용한 병렬 처리
        limit = concurrent_limit or self.concurrent_research
        results = await self.parallel_executor.process_questions_parallel(
            questions, process_question, limit
        )

        # 요약 정보
        elapsed = time.time() - start_time
        summary = {
            "session_id": self.session_id,
            "output_directory": research_dir,
            "total_questions": stats["total_questions"],
            "completed_questions": stats["completed"],
            "failed_questions": stats["failed"],
            "total_feedback_loops": stats["total_loops"],
            "elapsed_seconds": elapsed,
            "model": self.client.model,
            "feedback_settings": {
                "depth": self.feedback_depth,
                "width": self.feedback_width
            },
            "results": results
        }

        # 요약 정보 저장
        await self.file_storage.save_summary(summary, self.session_id)

        # 완료 정보 출력
        print("\n===== 심층 연구 완료 =====")
        print(f"- 총 질문: {stats['total_questions']}개")
        print(f"- 완료: {stats['completed']}개")
        print(f"- 실패: {stats['failed']}개")
        print(f"- 총 피드백 루프: {stats['total_loops']}회")
        print(f"- 소요 시간: {elapsed:.1f}초")
        print(f"- 결과 저장 위치: {research_dir}")

        return summary
    
    async def deep_research(
        self,
        topic: str,
        include_articles: bool = True,
        include_trials: bool = True,
        include_variants: bool = False,
        max_results_per_type: int = 10,
        deduplicate: bool = True
    ) -> Dict[str, Any]:
        """
        특정 주제에 대한 심층 연구 수행 (MCP 서버 활용)
        
        Args:
            topic: 연구 주제
            include_articles: 논문 검색 포함 여부
            include_trials: 임상시험 검색 포함 여부
            include_variants: 유전자 변이 검색 포함 여부
            max_results_per_type: 각 유형별 최대 결과 수
            deduplicate: 중복 제거 여부
            
        Returns:
            Dict[str, Any]: 심층 연구 결과
        """
        if not self.biomcp:
            return {
                "success": False,
                "error": "MCP 통합이 초기화되지 않았습니다. MCP Manager가 필요합니다.",
                "topic": topic
            }
        
        print(f"\n🔬 심층 연구 시작: {topic}")
        start_time = time.time()
        
        # BiomCP를 통한 종합 연구
        research_results = await self.biomcp.comprehensive_biomedical_research(
            topic=topic,
            include_articles=include_articles,
            include_trials=include_trials,
            include_variants=include_variants,
            max_results_per_type=max_results_per_type
        )
        
        # 중복 제거 처리
        if deduplicate and research_results.get("success"):
            print("🔄 중복 제거 처리 중...")
            
            # 각 카테고리별 중복 제거
            data = research_results.get("data", {})
            
            # 논문 중복 제거
            if "articles" in data and data["articles"].get("results"):
                original_count = len(data["articles"]["results"])
                data["articles"]["results"] = await self.biomcp.deduplicate_research_results(
                    data["articles"]["results"]
                )
                dedup_count = len(data["articles"]["results"])
                if original_count > dedup_count:
                    print(f"  📄 논문: {original_count} → {dedup_count} (중복 {original_count - dedup_count}개 제거)")
            
            # 임상시험 중복 제거
            if "trials" in data and data["trials"].get("results"):
                original_count = len(data["trials"]["results"])
                data["trials"]["results"] = await self.biomcp.deduplicate_research_results(
                    data["trials"]["results"]
                )
                dedup_count = len(data["trials"]["results"])
                if original_count > dedup_count:
                    print(f"  🏥 임상시험: {original_count} → {dedup_count} (중복 {original_count - dedup_count}개 제거)")
            
            # 유전자 변이 중복 제거
            if "variants" in data and data["variants"].get("results"):
                original_count = len(data["variants"]["results"])
                data["variants"]["results"] = await self.biomcp.deduplicate_research_results(
                    data["variants"]["results"]
                )
                dedup_count = len(data["variants"]["results"])
                if original_count > dedup_count:
                    print(f"  🧬 유전자 변이: {original_count} → {dedup_count} (중복 {original_count - dedup_count}개 제거)")
            
            research_results["data"] = data
        
        # AI 기반 요약 생성
        if research_results.get("success") and research_results.get("data"):
            print("\n📝 AI 기반 종합 요약 생성 중...")
            
            # 연구 결과를 텍스트로 변환
            research_text = self._format_research_results(research_results["data"])
            
            # AI에게 요약 요청
            summary_prompt = f"""다음은 '{topic}'에 대한 심층 연구 결과입니다:

{research_text}

위 연구 결과를 바탕으로 다음 형식으로 종합 요약을 작성해주세요:

1. 핵심 발견사항 (3-5개)
2. 주요 연구 동향
3. 임상적 의의
4. 향후 연구 방향
5. 결론

각 섹션은 구체적이고 과학적인 근거를 포함해야 합니다."""

            summary_response = await self.client.generate(
                prompt=summary_prompt,
                system="당신은 신약개발 연구 전문가입니다. 과학적 정확성을 유지하면서 핵심 내용을 명확하게 요약해주세요.",
                model=self.client.model
            )
            
            research_results["ai_summary"] = summary_response.get("response", "요약 생성 실패")
        
        # 실행 시간 기록
        elapsed_time = time.time() - start_time
        research_results["elapsed_seconds"] = elapsed_time
        
        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"deep_research_{topic.replace(' ', '_')}_{timestamp}"
        
        # 세션 디렉토리에 저장
        session_dir = os.path.join(self.output_dir, self.session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        filepath = os.path.join(session_dir, f"{filename}.json")
        await self.file_storage._save_json(research_results, filepath)
        
        print(f"\n✅ 심층 연구 완료 (소요시간: {elapsed_time:.1f}초)")
        print(f"📁 결과 저장: {filepath}")
        
        return research_results
    
    def _format_research_results(self, data: Dict[str, Any]) -> str:
        """연구 결과를 텍스트 형식으로 변환"""
        formatted_text = []
        
        # 논문 결과
        if "articles" in data and data["articles"].get("results"):
            formatted_text.append("=== 연구 논문 ===")
            for i, article in enumerate(data["articles"]["results"][:5], 1):
                if isinstance(article, dict):
                    title = article.get("title", "제목 없음")
                    formatted_text.append(f"{i}. {title}")
                elif isinstance(article, str):
                    formatted_text.append(f"{i}. {article[:200]}...")
            formatted_text.append("")
        
        # 임상시험 결과
        if "trials" in data and data["trials"].get("results"):
            formatted_text.append("=== 임상시험 ===")
            for i, trial in enumerate(data["trials"]["results"][:5], 1):
                if isinstance(trial, dict):
                    title = trial.get("title", trial.get("brief_title", "제목 없음"))
                    status = trial.get("status", "상태 불명")
                    formatted_text.append(f"{i}. {title} (상태: {status})")
                elif isinstance(trial, str):
                    formatted_text.append(f"{i}. {trial[:200]}...")
            formatted_text.append("")
        
        # 유전자 변이 결과
        if "variants" in data and data["variants"].get("results"):
            formatted_text.append("=== 유전자 변이 ===")
            for i, variant in enumerate(data["variants"]["results"][:5], 1):
                if isinstance(variant, dict):
                    gene = variant.get("gene", "유전자 불명")
                    variant_type = variant.get("type", "타입 불명")
                    formatted_text.append(f"{i}. {gene} - {variant_type}")
                elif isinstance(variant, str):
                    formatted_text.append(f"{i}. {variant[:200]}...")
        
        return "\n".join(formatted_text)


# 모듈 직접 실행 시 테스트
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='신약개발 연구 시스템')
    parser.add_argument('--questions', '-q', type=str, default=None,
                       help='질문 목록 파일 경로 (JSON 또는 텍스트)')
    parser.add_argument('--depth', '-d', type=int, default=2,
                       help='피드백 루프 깊이 (기본값: 2, 범위: 1-10)')
    parser.add_argument('--width', '-w', type=int, default=2,
                       help='피드백 루프 너비 (기본값: 2, 범위: 1-10)')
    parser.add_argument('--concurrent', '-c', type=int, default=2,
                       help='동시 연구 프로세스 수 (기본값: 2)')

    args = parser.parse_args()

    async def main():
        # 연구 관리자 생성
        manager = ResearchManager(
            feedback_depth=args.depth,
            feedback_width=args.width,
            concurrent_research=args.concurrent
        )

        # 연구 실행
        await manager.run_research(questions_file=args.questions)

    asyncio.run(main())
