#!/usr/bin/env python3
"""
근육 관련 건강기능식품 연구 챗봇 모듈

Ollama LLM을 활용한 CLI 기반 실시간 챗봇
과학적 근거와 참고문헌을 포함하는 상세한 답변 제공
"""

import os
import sys
import time
import json
import asyncio
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union

# 내부 모듈 임포트
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.api.ollama_client import OllamaClient
from src.utils.config import (
    OLLAMA_BASE_URL, 
    OLLAMA_MODEL, 
    OLLAMA_PARAMS, 
    DEFAULT_FEEDBACK_DEPTH,
    DEFAULT_FEEDBACK_WIDTH,
    MIN_RESPONSE_LENGTH,
    MIN_REFERENCES,
    OUTPUT_DIR,
    AVAILABLE_MODELS
)
from src.cli.interface import CliInterface


class HealthSupplementChatbot:
    """
    근육 관련 건강기능식품 연구 챗봇 클래스
    
    사용자 인터페이스 관리 및 AI 응답 생성을 담당합니다.
    """
    
    def __init__(self):
        """
        챗봇 초기화
        """
        # 설정 초기화 - 메모리에서 가져온 값을 사용하되, Gemma3를 우선 사용
        preferred_model = "Gemma3:latest"  # 바로 표준 모델로 지정
        self.settings = {
            "model": preferred_model,  # OLLAMA_MODEL 대신 바로 기본값 지정
            "feedback_depth": DEFAULT_FEEDBACK_DEPTH,
            "feedback_width": DEFAULT_FEEDBACK_WIDTH,
            "min_response_length": MIN_RESPONSE_LENGTH,
            "min_references": MIN_REFERENCES,
            "debug_mode": False  # 디버그 모드 기본값: 끄기
        }
        
        # Ollama API 클라이언트 초기화 (설정 후 생성)
        self.client = OllamaClient(
            model=preferred_model,  # 바로 Gemma3:latest로 지정
            max_tokens=4000,
            min_response_length=self.settings["min_response_length"]
        )
        
        # 모델 가용성 초기 확인을 위한 상태 변수
        self.initial_model_check_done = False
        
        # CLI 인터페이스 초기화
        self.interface = CliInterface()
        
        # 대화 이력
        self.conversation_history = []
        
        # 시스템 프롬프트
        self.system_prompt = """
당신은 근육 관련 건강기능식품 전문가입니다. 과학적 근거와 참고문헌을 포함하여 상세하게 답변해주세요.

답변 형식:
1. 문제 정의
2. 핵심 내용 (이론, 개념, 원리)
3. 과학적 근거 (연구 결과, 데이터)
4. 복용 방법 및 주의사항
5. 결론 및 요약
6. 참고 문헌 (최소 2개, URL 포함)

답변은 마크다운 형식으로 작성하며, 최소 1000자 이상이어야 합니다.
반드시 최소 2개 이상의 참고문헌(URL 포함)을 제공하세요.
"""

    async def auto_select_model(self):
        """
        사용 가능한 모델을 확인하고 자동으로 선택합니다.
        Gemma3:latest를 우선적으로 선택하고, 사용 불가능한 경우 다른 모델을 선택합니다.
        """
        try:
            # 사용 가능한 모델 목록 가져오기
            models = await self.client.list_models()
            available_models = [m.get("name") for m in models]
            
            # 현재 설정된 모델이 사용 가능한지 확인
            if self.settings["model"] not in available_models:
                # 우선 Gemma3:latest가 있는지 확인
                preferred_model = "Gemma3:latest"
                if preferred_model in available_models:
                    self.settings["model"] = preferred_model
                    self.client.model = preferred_model
                    self.interface.console.print(f"[green]모델이 '{preferred_model}'로 설정되었습니다.[/green]")
                # Gemma3가 없으면 다른 사용 가능한 모델 확인
                elif available_models:
                    self.settings["model"] = available_models[0]
                    self.client.model = available_models[0]
                    self.interface.console.print(f"[yellow]Gemma3:latest 모델을 찾을 수 없어 '{available_models[0]}'로 설정되었습니다.[/yellow]")
                else:
                    self.interface.display_error("사용 가능한 Ollama 모델이 없습니다. Ollama를 확인해주세요.")
                    return False
                    
            return True
            
        except Exception as e:
            self.interface.display_error(f"모델 확인 중 오류 발생: {str(e)}")
            return False
    
    async def start(self):
        """
        챗봇 실행
        """
        # 환영 메시지 표시
        self.interface.display_welcome()
        
        try:
            # API 가용성 확인
            status = await self.client.check_availability()
            if not status["available"]:
                self.interface.display_error(f"Ollama API에 연결할 수 없습니다: {status.get('error', '알 수 없는 오류')}")
                return
            
            # 사용 가능한 모델 확인 및 자동 선택
            if not self.initial_model_check_done:
                model_check_result = await self.auto_select_model()
                if not model_check_result:
                    return
                self.initial_model_check_done = True
        except Exception as e:
            self.interface.display_error(f"API 초기화 중 오류 발생: {str(e)}")
            return
        
        # 메인 입력 루프
        while True:
            try:
                # 사용자 입력 받기
                user_input = await self.interface.get_user_input()
                
                if not user_input:
                    continue
                    
                # 명령어 처리
                if user_input.startswith("/"):
                    continue_chat = await self.process_command(user_input)
                    if not continue_chat:
                        break
                else:
                    # 일반 질문 처리
                    await self.generate_response(user_input)
            except KeyboardInterrupt:
                print("\n프로그램이 종료됩니다.")
                break
            except Exception as e:
                self.interface.display_error(f"오류 발생: {str(e)}")
        
        print("프로그램이 종료되었습니다.")
    
    async def generate_response(self, question: str, ask_to_save: bool = True) -> str:
        """
        질문에 대한 AI 응답 생성
        
        Args:
            question: 사용자 질문
            ask_to_save: 저장 여부 확인 프롬프트 표시 여부 (기본값: True)
        
        Returns:
            str: 생성된 응답
        """
        # 응답 생성 중 스피너 표시
        with self.interface.display_thinking():
            try:
                # 디버깅: 요청 정보 출력 (디버그 모드일 때만)
                if self.settings["debug_mode"]:
                    print(f"\n[디버그] 질문 처리 중: {question[:50]}...")
                    print(f"[디버그] 현재 모델: {self.client.model}")
            
                # 응답 생성
                response = await self.client.generate(
                    prompt=question,
                    system_prompt=self.system_prompt
                )
            
                # 디버깅: 응답 길이 확인 (디버그 모드일 때만)
                if self.settings["debug_mode"]:
                    print(f"[디버그] 응답 길이: {len(response)} 자")
                    print(f"[디버그] 응답 시작: {response[:100]}...")
                
                # 응답이 비어있는지 확인
                if not response:
                    response = "[응답이 생성되지 않았습니다. 다시 시도해주세요.]"                
                
                # 대화 이력에 추가
                self.conversation_history.append({"question": question, "answer": response})
                
                # 응답 출력 (디버그 모드일 때만 시작/종료 표시)
                if self.settings["debug_mode"]:
                    print("\n--- AI 응답 시작 ---")
                
                # 항상 응답은 출력
                self.interface.display_response(response)
                
                if self.settings["debug_mode"]:
                    print("--- AI 응답 종료 ---\n")
                    
                # ask_to_save가 True인 경우에만 저장 여부 확인
                if ask_to_save:
                    save_choice = await self.interface.ask_to_save()
                    
                    # 사용자가 저장을 원하는 경우에만 저장
                    if save_choice:
                        # 평가 정보 없이 저장 (빈 딕셔너리 전달)
                        await self.save_research_result(question, response, {})
                
                return response
                
            except Exception as e:
                # 상세한 오류 정보 출력 (디버그 모드일 때만 상세 정보 출력)
                import traceback
                error_msg = f"응답 생성 중 오류 발생: {str(e)}"
                
                if self.settings["debug_mode"]:
                    print(f"\n[오류 상세 정보]\n{traceback.format_exc()}")
                    
                self.interface.display_error(error_msg)
                return error_msg
                
    async def process_command(self, command: str) -> bool:
        """
        사용자 명령어 처리
        
        Args:
            command: 사용자 명령어
            
        Returns:
            bool: 계속 실행 여부
        """
        try:
            # 명령어와 인수 분리
            parts = command.split(None, 1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            # 명령어 처리
            if cmd in ["/exit", "/quit"]:
                return False
                
            elif cmd == "/help":
                self.interface.display_help()
                
            elif cmd == "/clear":
                self.interface.clear_screen()
                
            elif cmd == "/settings":
                if args:
                    await self.update_settings(args)
                else:
                    self.interface.display_settings(self.settings)
                
            elif cmd == "/feedback":
                if not args:
                    self.interface.display_error("/feedback 명령어에는 질문이 필요합니다. 예: /feedback 근육 증강을 위한 최고의 보충제는?")
                else:
                    await self.run_feedback_loop(args)
            
            elif cmd == "/model":
                if not args:
                    self.interface.display_error("/model 명령어에는 모델명이 필요합니다. 사용 가능한 모델: " + ", ".join(AVAILABLE_MODELS))
                else:
                    await self.change_model(args)
            
            elif cmd == "/debug":
                # 디버그 모드 토글
                self.settings["debug_mode"] = not self.settings["debug_mode"]
                state = "켜짐" if self.settings["debug_mode"] else "꺼짐"
                self.interface.console.print(f"[green]디버그 모드가 {state}으로 설정되었습니다.[/green]")
            
            else:
                self.interface.display_error(f"알 수 없는 명령어: {cmd}. 도움말을 보려면 /help를 입력하세요.")
            return True
            
        except Exception as e:
            self.interface.display_error(f"명령어 처리 중 오류 발생: {str(e)}")
            return True  # 오류가 있어도 계속 실행

async def start(self):
    """
    챗봇 실행
    """
    # 환영 메시지 표시
    self.interface.display_welcome()

    try:
        # API 가용성 확인
        status = await self.client.check_availability()
        if not status["available"]:
            self.interface.display_error(f"Ollama API에 연결할 수 없습니다: {status.get('error', '알 수 없는 오류')}")
            return

        # 사용 가능한 모델 확인 및 자동 선택
        if not self.initial_model_check_done:
            model_check_result = await self.auto_select_model()
            if not model_check_result:
                return
            self.initial_model_check_done = True

        # 메인 루프 시작
        running = True
        while running:
            # 사용자 입력 받기
            user_input = await self.interface.get_input()
            
            # 입력이 명령어인지 확인
            if user_input.startswith("/"):
                running = await self.process_command(user_input)
            else:
                # 일반 질문 처리
                await self.process_input(user_input)
                
    except KeyboardInterrupt:
        self.interface.console.print("\n[yellow]프로그램이 중단되었습니다.[/yellow]")
    except Exception as e:
        import traceback
        error_msg = f"오류가 발생하여 프로그램이 중단되었습니다: {str(e)}"
        
        if self.settings["debug_mode"]:
            print(f"\n[오류 상세 정보]\n{traceback.format_exc()}")
            
        self.interface.display_error(error_msg)
            
    async def change_model(self, model_name: str) -> None:
        """
        사용 모델을 변경합니다.
        
        - 업데이트된 기능: 모델별 어댑터 자동 적용
        - 이전 컨텍스트 및 상태 초기화
        
        Args:
            model_name: 사용할 새 모델 이름
        """
        # 모델명 정리 (마지막에 :latest 없으면 추가)
        model_name = model_name.strip()
        if ":latest" not in model_name:
            model_name = f"{model_name}:latest"
        
        try:
            # 1. 모델 사용 가능성 확인
            model_check = await self.client.check_model_availability(model_name)
            if not model_check["available"]:
                self.interface.display_error(
                    f"모델 '{model_name}'을(를) 사용할 수 없습니다. \n"
                    f"오류: {model_check.get('message', '알 수 없는 오류')}"
                )
                return
                
            # 2. 모델 변경 전 이전 컨텍스트 초기화
            prev_model = self.client.model
            adapter_name = model_check.get('adapter', 'Unknown')
            
            # 3. 클라이언트 재초기화 (완전한 컨텍스트 분리를 위해)
            if prev_model != model_name:
                # HTTP 클라이언트 종료
                await self.client.close()
                
                # OllamaClient 연결 초기화
                self.client = OllamaClient(
                    model=model_name,
                    temperature=float(self.settings.get("temperature", 0.7)),
                    max_tokens=int(self.settings.get("max_tokens", 4000)),
                    min_response_length=int(self.settings.get("min_response_length", 500)),
                )
            else:
                # 동일 모델이지만 어댑터 업데이트 필요
                self.client.update_model(model_name)
            
            # 4. 설정 업데이트
            self.settings["model"] = model_name
            
            # 5. 사용자에게 피드백 제공
            self.interface.console.print(
                f"[bold green]모델을 '{model_name}'로 변경했습니다.[/bold green]\n"
                f"[blue]어댑터: {adapter_name}[/blue]"
            )
        except Exception as e:
            self.interface.display_error(f"모델 변경 중 오류 발생: {str(e)}")
            # 오류 발생 시 자세한 로그 출력
            import traceback
            self.interface.console.print(f"[dim]{traceback.format_exc()}[/dim]", highlight=False)
            
    async def update_settings(self, args_str: str) -> None:
        """
        사용자 설정 갱신
        
        Args:
            args_str: 설정 인수 문자열
        """
        try:
            # 설정 문자열 파싱 (형식: key=value)
            parts = args_str.split()
            updates = {}
            
            for part in parts:
                if "=" in part:
                    key, value = part.split("=", 1)
                    key = key.strip()
                    
                    if key in self.settings:
                        # 적절한 값으로 변환
                        if key in ["feedback_depth", "feedback_width", "min_response_length", "min_references"]:
                            updates[key] = int(value)
                        else:
                            updates[key] = value
                    else:
                        self.interface.display_error(f"알 수 없는 설정: {key}")
            
            # 유효성 검사
            if "feedback_depth" in updates and (updates["feedback_depth"] < 1 or updates["feedback_depth"] > 10):
                self.interface.display_error("피드백 깊이는 1에서 10 사이의 값이어야 합니다")
                del updates["feedback_depth"]
                
            if "feedback_width" in updates and (updates["feedback_width"] < 1 or updates["feedback_width"] > 10):
                self.interface.display_error("피드백 너비는 1에서 10 사이의 값이어야 합니다")
                del updates["feedback_width"]
                
            # 설정 갱신 및 표시
            if updates:
                self.settings.update(updates)
                self.interface.display_settings(self.settings)
                
        except ValueError as e:
            self.interface.display_error(f"설정 갱신 오류: {str(e)}")
        except Exception as e:
            self.interface.display_error(f"예상치 못한 오류: {str(e)}")
            
    async def save_research_result(self, question: str, response: str, rating_info: dict = None) -> None:
        """
        연구 결과를 파일로 저장
        
        Args:
            question: 사용자 질문
            response: 생성된 응답
            rating_info: 사용자 평가 정보 (선택사항)
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 질문에서 파일명 생성 (간단하게)
        title_words = question.split()[:5]  # 처음 5개 단어만 사용
        title = "_".join(title_words).replace("/", "").replace("\\", "").replace("?", "").replace("!", "")
        
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
            f.write(f"# 근육 건강기능식품 연구: {question}\n\n")
            
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
    
    async def run_feedback_loop(self, question: str) -> None:
        """
        피드백 루프를 실행하여 고품질 응답 생성 및 저장
        
        Args:
            question: 사용자 질문
        """
        depth = self.settings["feedback_depth"]
        width = self.settings["feedback_width"]
        
        self.interface.display_feedback_progress(0, depth, "피드백 루프 시작...")
        
        # 초기 응답 생성 (저장 여부 확인 없이)
        best_response = await self.generate_response(question, ask_to_save=False)
        
        # 피드백 루프 실행
        for i in range(depth):
            self.interface.display_feedback_progress(i + 1, depth, f"{i + 1}단계: 대체 응답 생성 중...")
            
            # 스피너 표시
            with self.interface.display_thinking():
                try:
                    # 대체 응답 생성 (각 응답은 이전 최서 응답에 대한 피드백 제공)
                    feedback_prompt = f"""
이 질문에 대해 이전에 제공한 답변을 개선해주세요: 

질문: {question}

이전 답변:
{best_response}

개선점:
1. 과학적 근거 강화 (연구와 데이터 추가)
2. 영양소 복용방법 및 주의사항 상세화
3. 최신 참고문헌 추가 (최소 2개 이상)
4. 구체적인 예시 추가

위 개선점을 반영하여 더 완성도 높은 답변을 제공해주세요.
"""

                    # 너비만큼의 대체 응답 병렬 생성
                    prompts = []
                    for j in range(width):
                        prompts.append({
                            "prompt": feedback_prompt,
                            "system": self.system_prompt,
                            "temperature": 0.5 + (j * 0.2)  # 다양성을 위해 다른 온도 적용
                        })
                    
                    # 병렬 응답 생성
                    alternatives = await self.client.generate_parallel(prompts)
                    
                    # 가장 좋은 응답 선택 (간단한 휘리스틱 - 길이, 참고문헌 수 등 고려)
                    best_score = -1
                    for response in alternatives:
                        if isinstance(response, Exception):
                            continue
                            
                        # 점수 계산 (간단한 휘리스틱)
                        score = len(response)  # 길이 가중치
                        refs_count = response.lower().count("http")  # 참고문헌 수 대략 추정
                        score += refs_count * 200  # 참고문헌에 대한 보너스
                        
                        if score > best_score:
                            best_response = response
                            best_score = score
                    
                except Exception as e:
                    self.interface.display_error(f"피드백 루프 오류: {str(e)}")
                    break
        
        # 최종 응답 표시
        self.interface.display_response(best_response, show_references=True)
        
        # 사용자에게 결과 저장 여부 확인
        save_choice = await self.interface.ask_to_save()
        
        # 사용자가 저장을 원하는 경우에만 저장
        if save_choice:
            # 평가 정보 없이 저장 (빈 딕셔너리 전달)
            await self.save_research_result(question, best_response, {})


# 챗봇 런처 구현
async def main():
    """
    메인 함수
    """
    chatbot = HealthSupplementChatbot()
    await chatbot.start()