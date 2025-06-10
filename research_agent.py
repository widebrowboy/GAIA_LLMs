import os
import json
import asyncio
import traceback
from typing import Dict, List, Optional, Tuple, TypedDict, Any
import httpx
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv
from datetime import datetime
import markdown
from bs4 import BeautifulSoup
import re

# 파일명 생성을 위한 slugify 함수 추가
def slugify(text: str) -> str:
    """
    URL이나 파일명으로 사용할 수 있게 텍스트를 변환합니다.
    
    Args:
        text: 변환할 텍스트
        
    Returns:
        str: 변환된 텍스트
    """
    # 한글 특수 처리 (한글은 그대로 유지)
    text = re.sub(r'[^\w가-힣\s-]', '', text.lower())
    # 공백을 하이픈으로 변경
    text = re.sub(r'[\s]+', '-', text.strip())
    # 중복된 하이픈 제거
    text = re.sub(r'-+', '-', text)
    # 너무 긴 파일명 방지
    return text[:50] if len(text) > 50 else text

# Type definitions for better code clarity
class ResearchQuestion(TypedDict):
    question: str
    depth: int
    breadth: int
    feedback_cycles: List[Dict[str, Any]]
    final_answer: str

class ResearchFeedback(TypedDict):
    quality_score: int  # 1-5 scale
    feedback_notes: str
    suggested_improvements: List[str]
    improved_answer: str

class ResearchConfig(TypedDict):
    default_depth: int
    default_breadth: int
    max_retries: int
    min_response_length: int
    output_dir: str

# Load environment variables
load_dotenv()

class ResearchAgent:
    def __init__(self, model: str = None, temperature: float = 0.7, max_tokens: int = 4000):
        """
        근육 관련 건강기능식품 연구를 위한 ResearchAgent 초기화
        
        Args:
            model: 사용할 Ollama 모델 (기본값: gemma3:4b)
            temperature: 생성 온도 (0.1~1.0, 높을수록 창의적)
            max_tokens: 최대 토큰 수 (기본값: 4000)
        """
        load_dotenv()  # 환경 변수 로드
        
        self.ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = model or os.getenv('OLLAMA_MODEL', 'gemma3:4b')
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.output_dir = os.getenv('OUTPUT_DIR', 'research_outputs')
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 연구 에이전트 설정
        self.config = {
            'min_response_length': 1000,  # 최소 응답 길이 (문자 수)
            'default_depth': 2,           # 피드백 반복 깊이 (.windsurfrules에 따라 2으로 설정)
            'default_breadth': 2,         # 각 단계별 대체 답변 수 (.windsurfrules에 따라 2으로 설정)
            'max_retries': 3,             # 요청 실패 시 재시도 횟수
            'output_dir': self.output_dir,
            'required_sections': [        # 필수 섹션 목록
                '## 1. 문제 정의',
                '## 2. 핵심 내용',
                '## 3. 과학적 근거',
                '## 4. 복용 방법 및 주의사항',
                '## 5. 결론 및 요약',
                '## 참고 문헌'
            ]
        }

    async def generate_with_ollama(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        max_retries: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Ollama API를 사용하여 상세한 한국어 텍스트 생성. GPU 가속 및 병렬 처리 최적화 적용.
        
        Args:
            prompt: 입력 프롬프트
            system_prompt: 모델 지침을 위한 시스템 프롬프트 (선택사항)
            max_retries: 최대 재시도 횟수
            temperature: 생성 온도 (None이면 기본값 사용)
            
        Returns:
            생성된 텍스트 응답
        """
        max_retries = max_retries or self.config['max_retries']
        current_temp = temperature if temperature is not None else self.temperature
        
        # GPU 최적화 파라미터 설정 (.windsurfrules에 따름)
        gpu_params = {
            "num_gpu": 99,       # 가용한 모든 GPU 활용
            "num_thread": 8,     # 병렬 스레드 수
            "f16_kv": True,      # 16비트 부동소수점 메모리 최적화
            "mirostat": 2        # 고급 샘플링 알고리즘
        }
        
        # 프롬프트 설정
                

        
    def _is_response_adequate(self, response: str) -> bool:
        """
        응답이 최소 품질 기준을 충족하는지 확인합니다.
        
        Args:
            response: 검사할 응답 텍스트
            
        Returns:
            bool: 응답이 최소 품질 기준을 충족하면 True, 그렇지 않으면 False
        """
        # 응답 길이 확인
        if len(response) < self.config['min_response_length']:
            print(f"\033[33m경고: 응답이 너무 짧습니다. ({len(response)} 문자, 최소 {self.config['min_response_length']} 필요)\033[0m")
            return False
        
        # 필수 섹션 확인
        missing_sections = []
        for section in self.config['required_sections']:
            if section not in response:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"\033[33m경고: 다음 필수 섹션이 누락되었습니다: {', '.join(missing_sections)}\033[0m")
            return False
        
        # 인용 및 참고문헌 확인
        if "참고 문헌" not in response:
            print("\033[33m경고: 참고 문헌이 없습니다.\033[0m")
            return False
        
        # 최소한의 참고문헌 항목 수 확인
        references_section = response.split("## 참고 문헌")[1] if "## 참고 문헌" in response else ""
        reference_count = references_section.count('- ')
        
        if reference_count < 2:
            print(f"\033[33m경고: 참고 문헌이 부족합니다. (찾음: {reference_count}, 최소 2개 필요)\033[0m")
            return False
            
        return True

    def clean_html_content(self, html_content: str) -> str:
        """Clean and extract text from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text and clean up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text

    def save_research(self, topic: str, content: str, format: str = "markdown"):
        """Save research output to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{topic.lower().replace(' ', '_')}_{timestamp}.{format}"
        filepath = os.path.join(self.config['output_dir'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return filepath

    def format_research_output(self, topic: str, research_data: Dict[str, str]) -> str:
        """Format the research data into a well-structured markdown report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create table of contents
        toc = ["## 목차", ""]
        content = [
            f"# {topic} 연구 보고서",
            f"**작성일:** {timestamp}",
            ""
        ]
        
        # Add sections for each question
        for i, (question, answer) in enumerate(research_data.items(), 1):
            section_id = f"section-{i}"
            toc.append(f"{i}. [{question}](#{section_id})")
            
            content.extend([
                f"<a id='{section_id}'></a>",
                f"## {i}. {question}",
                "",
                answer,
                "",
                "---\n"  # Add horizontal rule between sections
            ])
        
        # Add references section (참고 문헌 섹션은 각 질문에 이미 포함되어 있음)
        
        # 목차를 본문 앞에 추가
        return "\n".join(content)
        
    async def conduct_research(self, topic: str, questions: List[str], depth: Optional[int] = None, 
                           breadth: Optional[int] = None, references: Optional[List[str]] = None) -> Tuple[str, Dict]:
        """
        주제와 질문 목록을 기반으로 딥 리서치를 수행합니다. 
        .windsurfrules에 따른 GPU 가속 및 병렬 처리를 적용하여 성능을 최적화합니다.
        
        Args:
            topic: 연구 주제
            questions: 연구할 질문 목록
            depth: 피드백 루프 수행 깊이 (기본값: 2, 범위: 1-10)
            breadth: 각 단계에서 생성할 대체 답변 수 (기본값: 2, 범위: 1-10)
            references: 참고 자료 URL 목록 (선택사항)
            
        Returns:
            Tuple[str, Dict]: (마크다운 형식의 연구 보고서, 메타데이터)
        """
        start_time = datetime.now()
        
        # 매개변수 검증 및 기본값 설정
        if depth is None:
            depth = self.config['default_depth']
        else:
            depth = max(1, min(10, depth))  # 1-10 사이 값으로 제한
            
        if breadth is None:
            breadth = self.config['default_breadth']
        else:
            breadth = max(1, min(10, breadth))  # 1-10 사이 값으로 제한
            
        # 병렬 처리를 위한 세마포어 설정 (동시 2개 질문 처리)
        semaphore = asyncio.Semaphore(2)
        
        # 메타데이터 초기화
        metadata = {
            'topic': topic,
            'questions': questions,
            'depth': depth,
            'breadth': breadth,
            'start_time': start_time.isoformat(),
            'end_time': None,
            'duration_seconds': None,
            'model': self.model,
            'config': self.config,
            'question_details': []
        }
        
        # 결과 저장용 디렉토리 생성 (타임스탬프 사용)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(self.config['output_dir'], timestamp)
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n🔎 총 {len(questions)}개의 질문에 대해 연구를 시작합니다.\n")
        print(f"⚡ GPU 가속 및 병렬 처리로 속도 최적화를 적용했습니다.\n")
        
        research_results = []
        total_questions = len(questions)
        start_time = datetime.now()
        
        # 동시 처리할 최대 질문 수 설정 (GPU 메모리 고려)
        max_concurrent = 2  # 병렬 처리할 질문 수
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # 병렬 처리를 위한 비동기 질문 처리 함수
        async def process_question(q_idx: int, question: str):
            async with semaphore:  # 동시 처리 제한
                print(f"\n✅ 질문 {q_idx+1}/{total_questions} 연구 중: {question}")
                
                if references:
                    print("참고 문헌:")
                    for ref in references[:3]:  # 처음 3개만 표시
                        print(f"- {ref[:30]}...")
                
                print(f"   깊이: {depth}, 너비: {breadth}")
                print(f"   🔍 초기 연구 진행 중...")
                
                try:
                    q_start_time = datetime.now()
                    current_answer = await self._research_question(question)
                    
                    # 연구 품질 향상을 위한 피드백 루프
                    feedback_cycles = []
                    
                    for cycle in range(depth):
                        print(f"   🔄 질문 {q_idx+1} - 피드백 루프 {cycle+1}/{depth} 수행 중...")
                        
                        # 현재 답변에 대한 피드백 생성
                        feedback = await self._generate_feedback(question, current_answer)
                        
                        # 병렬로 대체 답변 생성 작업 준비
                        alt_tasks = []
                        for b in range(breadth):
                            alt_tasks.append(self._generate_improved_answer(
                                question, current_answer, feedback['feedback_notes']
                            ))
                        
                        # 대체 답변 병렬 생성 (GPU 부하 분산)
                        print(f"      🌿 {breadth}개의 대체 답변을 병렬 생성 중...")
                        alt_results = await asyncio.gather(*alt_tasks, return_exceptions=True)
                        
                        # 결과 처리
                        alternative_answers = []
                        for b, result in enumerate(alt_results):
                            if isinstance(result, Exception):
                                print(f"      ⚠️ 대체 답변 {b+1} 생성 중 오류: {result}")
                            else:
                                alternative_answers.append(result)
                                print(f"      ✓ 대체 답변 {b+1} 생성 완료")
                        
                        # 최적의 답변 선택
                        if alternative_answers:
                            improved_answer = await self._improve_with_feedback(
                                question, current_answer, depth=depth, breadth=breadth
                            )
                            research_results[question] = improved_answer
                        else:
                            research_results[question] = current_answer
                            
                    # 결과 저장
                    research_results[question] = improved_answer
                    research_results[question] = improved_response
                    
                    # 메타데이터 업데이트
                    question_duration = datetime.now() - question_start_time
                    minutes, seconds = divmod(question_duration.seconds, 60)
                    print(f"   ✨ 질문 {q_idx + 1} 완료! (소요 시간: {minutes}분 {seconds}초)")
                    
                    return {
                        'question': question,
                        'duration_seconds': question_duration.total_seconds(),
                        'start_time': question_start_time.isoformat(),
                        'end_time': datetime.now().isoformat(),
                        'response_length': len(improved_response),
                        'status': 'completed'
                    }
                    
                except Exception as e:
                    error_msg = f"질문 처리 중 오류 발생: {str(e)}"
                    print(f"\n❌ {error_msg}")
                    traceback.print_exc()
                    return {
                        'question': question,
                        'error': error_msg,
                        'traceback': traceback.format_exc(),
                        'status': 'failed'
                    }
        
        # 모든 질문에 대해 병렬 처리 (최대 2개 동시 실행)
        print(f"\n🚀 총 {len(questions)}개 질문에 대한 연구를 시작합니다 (병렬 처리: 최대 2개 동시 실행)...")
        tasks = [process_question(i, q) for i, q in enumerate(questions)]
        results = await asyncio.gather(*tasks)
        
        # 메타데이터에 질문별 결과 추가
        metadata['question_details'] = results
        
        # 전체 소요 시간 계산
        total_duration = datetime.now() - start_time
        metadata['end_time'] = datetime.now().isoformat()
        metadata['duration_seconds'] = total_duration.total_seconds()
        
        # 최종 보고서 생성
        print("\n📝 최종 보고서 생성 중...")
        report = self.format_research_output(topic, research_results)
        
        # 결과 저장
        report_file = os.path.join(output_dir, f"{slugify(topic)}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        output_file = os.path.join(output_dir, f"{slugify(topic)}.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {topic} 연구 결과\n\n")
            f.write(f"- 연구 시작: {metadata['start_time'].split('T')[0]} {metadata['start_time'].split('T')[1].split('.')[0]}\n")
            f.write(f"- 연구 깊이: {depth}, 너비: {breadth}\n")
            f.write(f"- 사용 모델: {self.model}\n\n")
            
            for i, (question, answer) in enumerate(results.items(), 1):
                f.write(f"## 질문 {i}: {question}\n\n")
                f.write(f"{answer}\n\n")
                f.write("---\n\n")
        
        # 메타데이터 저장
        metadata_file = os.path.join(output_dir, f"{slugify(topic)}_metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"✅ 연구가 완료되었습니다!")
        print(f"📚 총 {len(research_questions)}개 질문, 소요 시간: {minutes}분 {seconds}초")
        print(f"📄 결과 파일: {output_file}")
        print(f"📊 메타데이터: {metadata_file}")
        print(f"{'='*60}")
        
        return output_file, metadata
    
    async def _research_question(self, question: str) -> str:
        """
        단일 질문에 대한 초기 연구 수행
        
        Args:
            question: 연구할 질문
            
        Returns:
            구조화된 연구 결과 (마크다운 형식)
        """
        # 시스템 프롬프트 설정
        system_prompt = (
            "당신은 스포츠 영양학 전문가입니다. "
            "근육 성장과 회복에 관한 건강기능식품에 대한 질문에 과학적 근거를 바탕으로 정확하고 상세하게 답변해주세요.\n\n"
            "다음 사항을 반드시 지켜주세요:\n"
            "1. 모든 답변은 과학적 연구 결과를 기반으로 해야 합니다.\n"
            "2. 구체적인 수치와 연구 결과를 인용할 때는 출처를 명시해주세요.\n"
            "3. 마크다운 형식을 사용하여 가독성을 높여주세요.\n"
            "4. 전문 용어를 사용할 때는 초보자도 이해할 수 있도록 설명을 추가해주세요."
        )
        
        # 사용자 프롬프트 설정
        prompt = (
            f"{question}\n\n"
            "위 질문에 대해 체계적이고 자세한 답변을 작성해주세요. 다음의 구조를 따라주세요:\n\n"
            "## 1. 문제 정의\n"
            "- 질문의 핵심 내용과 중요성 설명\n\n"
            "## 2. 핵심 내용\n"
            "- 주요 개념과 이론 설명\n"
            "- 관련된 생리학적/생화학적 메커니즘\n\n"
            "## 3. 과학적 근거\n"
            "- 최신 연구 결과 요약 (연구명, 참여자 수, 주요 결과)\n"
            "- 메타분석이 있는 경우 그 결과 포함\n\n"
            "## 4. 복용 방법 및 주의사항\n"
            "- 권장 용량과 복용 시기\n"
            "- 잠재적 부작용과 주의사항\n\n"
            "## 5. 결론 및 요약\n"
            "- 주요 내용 요약\n"
            "- 실용적인 조언\n\n"
            "## 참고 문헌\n"
            "- 인용한 연구 및 자료 목록 (저자, 연도, 저널명, DOI/링크)\n\n"
            "답변은 최소 1500자 이상으로 자세히 작성해주시고, "
            "마크다운 형식을 사용해 구조화해주세요. "
            "과학적 연구 결과를 인용할 때는 반드시 출처를 명시해주세요."
        )
        
        return await self.generate_with_ollama(prompt, system_prompt=system_prompt)
    
    async def _generate_feedback(self, question: str, current_answer: str) -> Dict[str, Any]:
        """
        현재 답변에 대한 피드백을 생성합니다.
        
        Args:
            question: 연구 질문
            current_answer: 현재 답변
            
        Returns:
            Dict: 피드백 내용과 메타데이터
        """
        try:
            # 피드백 프롬프트 생성
            system_prompt, feedback_prompt = self._create_feedback_prompt(question, current_answer, [])
            
            # 피드백 생성
            feedback_text = await self.generate_with_ollama(
                prompt=feedback_prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            return {
                "feedback_notes": feedback_text,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"      ⚠️ 피드백 생성 중 오류: {str(e)}")
            return {
                "feedback_notes": "피드백 생성 중 오류가 발생했습니다.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _improve_with_feedback(self, question: str, initial_answer: str, depth: int, breadth: int) -> Dict[str, Any]:
        """
        피드백 루프를 통해 답변을 반복적으로 개선합니다.
        
        Args:
            question: 연구 질문
            initial_answer: 초기 답변
            depth: 피드백 루프 깊이
            breadth: 대체 답변 생성 수
            
        Returns:
            Dict: 최종 답변과 메타데이터
        """
        current_answer = initial_answer
        best_answers = []
        improvement_history = []
        
        for d in range(depth):
            print(f"   🔄 질문 {d+1}/{depth} - 피드백 루프 {d+1}/{depth} 수행 중...")
            
            try:
                # 현재 답변에 대한 피드백 생성
                feedback = await self._generate_feedback(question, current_answer)
                
                # 병렬로 대체 답변 생성 작업 준비
                alt_tasks = []
                for b in range(breadth):
                    alt_tasks.append(self._generate_improved_answer(
                        question, current_answer, feedback['feedback_notes']
                    ))
                
                # 대체 답변 병렬 생성 (GPU 부하 분산)
                print(f"      🌿 {breadth}개의 대체 답변을 병렬 생성 중...")
                alt_results = await asyncio.gather(*alt_tasks, return_exceptions=True)
                
                # 결과 처리
                alternative_answers = []
                for b, result in enumerate(alt_results):
                    if isinstance(result, Exception):
                        print(f"      ⚠️ 대체 답변 {b+1} 생성 중 오류: {result}")
                    else:
                        alternative_answers.append(result)
                        print(f"      ✓ 대체 답변 {b+1} 생성 완료")
                
                # 최적의 답변 선택
                if alternative_answers:
                    # 대체 답변 중 최적의 답변 선택
                    selection_result = await self._select_best_answer(question, current_answer, alternative_answers)
                    current_answer = selection_result.get('best_answer', current_answer)
                    
                # 개선 이력 추가
                improvement_history.append({
                    "iteration": d + 1,
                    "answer": current_answer,
                    "feedback": feedback.get('feedback_notes', ''),
                    "alternatives_count": len(alternative_answers),
                    "timestamp": datetime.now().isoformat()
                })
                
                # 최적의 답변 저장
                best_answers.append(current_answer)
                    
            except Exception as e:
                print(f"      ⚠️ 피드백 루프 중 오류: {str(e)}")
                return {
                    "answer": current_answer,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        # 최종 결과 반환
        return {
            "answer": current_answer,  # 최종 개선된 답변
            "best_answers": best_answers,  # 각 반복에서의 최적 답변들
            "improvement_history": improvement_history,  # 개선 이력
            "iterations_completed": len(improvement_history),  # 완료된 반복 횟수
            "timestamp": datetime.now().isoformat()
        }
        
    async def _generate_improved_answer(self, question: str, current_answer: str, feedback: str) -> str:
        """
        피드백을 기반으로 개선된 답변을 생성합니다.
        
        Args:
            question: 연구 질문
            current_answer: 현재 답변
            feedback: 피드백 내용
            
        Returns:
            str: 개선된 답변
        """
        try:
            # 개선 프롬프트 생성
            system_prompt = (
                "당신은 근육 관련 건강기능식품 전문가입니다. "
                "주어진 질문에 대해 과학적 근거에 기반한 정확하고 상세한 답변을 제공해주세요."
            )
            
            prompt = (
                f"### 질문\n{question}\n\n"
                f"### 현재 답변\n{current_answer}\n\n"
                f"### 피드백\n{feedback}\n\n"
                "### 지시사항\n"
                "위의 피드백을 바탕으로 개선된 답변을 작성해주세요. "
                "다음 구조를 반드시 따라주세요:\n\n"
                "## 1. 문제 정의\n"
                "## 2. 핵심 내용\n"
                "## 3. 과학적 근거\n"
                "## 4. 복용 방법 및 주의사항\n"
                "## 5. 결론 및 요약\n"
                "## 참고 문헌\n\n"
                "답변은 최소 1500자 이상으로 자세히 작성해주시고, "
                "모든 과학적 주장은 반드시 출처를 명시해주세요."
            )
            
            # 개선된 답변 생성 (GPU 가속 파라미터 적용)
            improved_answer = await self.generate_with_ollama(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            return improved_answer
            
        except Exception as e:
            print(f"      ⚠️ 개선된 답변 생성 중 오류: {str(e)}")
            return f"개선된 답변 생성 중 오류가 발생했습니다: {str(e)}"
    
    def _create_feedback_prompt(
        self, 
        question: str, 
        current_answer: str, 
        alternatives: List[str]
    ) -> str:
        """
        연구 답변에 대한 피드백을 생성하기 위한 프롬프트를 생성합니다.
        
        Args:
            question: 연구 질문
            current_answer: 현재 답변
            alternatives: 대체 답변 목록
            
        Returns:
            str: 피드백 프롬프트
        """
        # 피드백 프롬프트 생성
        feedback_prompt = (
            "## 연구 답변 평가 요청\n\n"
            f"### 연구 질문\n{question}\n\n"
            "### 평가 요청 사항\n"
            "아래 답변들을 종합적으로 분석하여 다음 사항을 포함한 피드백을 제공해주세요:\n"
            "1. 각 답변의 강점과 약점 분석\n"
            "2. 과학적 정확성에 대한 평가\n"
            "3. 내용의 포괄성 검토\n"
            "4. 구조와 명확성 평가\n"
            "5. 참고 문헌의 적절성 검토\n\n"
            "### 답변 목록\n"
            f"#### [현재 답변]\n{current_answer[:500]}...\n\n"
        )
        
        # 대체 답변 추가
        for i, alt in enumerate(alternatives, 1):
            # 대체 답변 요약 (처음 200자 + ... + 마지막 100자)
            alt_summary = alt[:200]
            if len(alt) > 300:
                alt_summary += "..." + alt[-100:] if len(alt) > 100 else ""
            
            feedback_prompt += f"#### [대체 답변 {i}]\n{alt_summary}\n\n"
        
        # 평가 기준 추가
        feedback_prompt += (
            "### 평가 기준\n"
            "- **과학적 정확성** (40%): 최신 연구 결과와의 일치성, 사실 기반 정보\n"
            "- **포괄성** (25%): 모든 필수 섹션 포함, 중요 측면 누락 여부\n"
            "- **명확성** (20%): 설명의 명확성, 전문 용어 설명, 예시 활용\n"
            "- **참고 문헌** (15%): 최소 2개 이상의 신뢰할 수 있는 출처\n"
            "   - 적절한 인용 형식 준수\n"
            "   - 최신 연구 결과 반영 (가능한 최근 5년 이내)\n\n"
            "### 개선 제안\n"
            "가장 좋은 답변을 기반으로 구체적인 개선 방안을 3-5가지 제시해주세요."
        )
        
        return feedback_prompt
        
    def _create_alternative_prompt(self, question: str, current_answer: str, feedback: str) -> Tuple[str, str]:
        """
        대체 답변 생성을 위한 프롬프트를 생성합니다.
        .windsurfrules에 따른 요구사항을 반영하여 다양한 관점에서의 답변 생성을 유도합니다.
        
        Args:
            question: 연구 질문
            current_answer: 현재 답변
            feedback: 개선을 위한 피드백
            
        Returns:
            Tuple[str, str]: (시스템 프롬프트, 사용자 프롬프트)
        """
        # 시스템 프롬프트 설정
        system_prompt = (
            "## 역할: 스포츠 영양학 연구 조언자\n\n"
            "### 주요 임무\n"
            "1. 제공된 질문과 피드백을 바탕으로 기존 답변을 개선한 새로운 답변을 생성합니다.\n"
            "2. 과학적 정확성과 최신 연구 결과를 반영합니다.\n"
            "3. 다양한 관점에서의 분석과 해석을 제공합니다.\n\n"
            "### 작성 지침\n"
            "1. **과학적 정확성**: 최신 연구 결과와 일치하는 정보만 포함합니다.\n"
            "2. **포괄성**: 모든 필수 섹션을 포함하고 중요한 측면이 누락되지 않도록 합니다.\n"
            "3. **명확성**: 복잡한 개념도 이해하기 쉽게 설명합니다.\n"
            "4. **참고 문헌**: 최소 2개 이상의 신뢰할 수 있는 출처를 인용합니다.\n"
            "5. **형식**: 마크다운 형식을 사용하여 가독성을 높입니다."
        )
        
        # 다양한 관점을 위한 접근 방식 목록
        perspectives = [
            "임상적 관점에서",
            "분자생물학적 메커니즘을 중심으로",
            "체계적 문헌고찰을 바탕으로",
            "최신 메타분석 연구 결과를 반영하여",
            "실제 임상 사례를 중심으로",
            "예방의학적 관점에서",
            "영양학적 접근법을 강조하여"
        ]
        
        import random
        selected_perspective = random.choice(perspectives)
        
        # 사용자 프롬프트 설정
        prompt = (
            "## 연구 답변 개선 요청\n\n"
            f"### 연구 질문\n{question}\n\n"
            "### 기존 답변 요약\n"
            f"{current_answer[:500]}...\n\n"
            "### 개선을 위한 피드백\n"
            f"{feedback}\n\n"
            "### 요청 사항\n"
            f"위 피드백을 바탕으로 {selected_perspective} 답변을 개선해주세요.\n\n"
            "### 작성 가이드라인\n"
            "1. **과학적 정확성**: 최신 연구 결과를 반영하고, 모든 주장은 신뢰할 수 있는 출처로 뒷받침되어야 합니다.\n"
            "2. **포괄성**: 다음 모든 필수 섹션을 포함하세요.\n"
            "   - 문제 정의\n"
            "   - 핵심 내용 (이론, 개념, 원리)\n"
            "   - 과학적 근거 (연구 결과, 데이터)\n"
            "   - 복용 방법 및 주의사항\n"
            "   - 결론 및 요약\n"
            "   - 참고 문헌 (최소 2개 이상, 최신 연구 우선)\n"
            "3. **명확성**: 전문 용어는 반드시 설명하고, 복잡한 개념은 예시를 들어 설명하세요.\n"
            "4. **참고 문헌**: 최신 연구(가능한 최근 5년 이내)를 우선으로 인용하세요.\n\n"
            "### 주의사항\n"
            "- 반드시 한국어로 답변해주세요.\n"
            "- 최소 1,000자 이상 작성해주세요.\n"
            "- 마크다운 형식을 사용하여 가독성을 높여주세요.\n"
            "- 인용은 [1], [2] 형식으로 표기하고, 하단에 상세 출처를 기재해주세요."
        )
        
        return system_prompt, prompt


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
