#!/usr/bin/env python3
"""
Ollama API 클라이언트

이 모듈은 Ollama API와 상호작용하여 텍스트 생성 및 처리를 담당합니다.
Ollama API 클라이언트 클래스는 비동기 HTTP 요청을 사용하여 텍스트 생성을 수행합니다.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv
import aiohttp

# 어댑터 클래스 임포트
from app.api.model_adapters import get_adapter_for_model

# 환경 변수 로드
load_dotenv()

class OllamaClient:
    """
    Ollama API 클라이언트

    Ollama LLM API와 상호작용하는 클래스입니다.
    텍스트 생성, 병렬 생성 등의 기능을 제공합니다.
    """

    def __init__(self,
                 model: str = "Gemma3:latest",
                 temperature: float = 0.7,
                 max_tokens: int = 4000,
                 min_response_length: int = 500,
                 ollama_url: Optional[str] = None,
                 debug_mode: bool = False):
        """
        Ollama API 클라이언트 초기화

        Args:
            model: 사용할 모델명 (기본값: "Gemma3:latest")
            temperature: 생성 온도 (기본값: 0.7)
            max_tokens: 최대 토큰 수 (기본값: 4000)
            min_response_length: 최소 응답 길이 (기본값: 500)
            ollama_url: Ollama API 엔드포인트 URL (기본값: 환경 변수에서 로드)
            debug_mode: 디버그 모드 활성화 여부 (기본값: False)
        """
        # 환경 변수에서 Ollama URL 로드 (지정되지 않은 경우)
        self.ollama_url = ollama_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.min_response_length = min_response_length
        self.max_retries = 3

        # GPU 최적화 파라미터 (windsurfrules에 따름)
        self.gpu_params = {
            "num_gpu": 99,       # 사용 가능한 모든 GPU 활용
            "num_thread": 8,     # 병렬 스레드 활용
            "f16_kv": True,      # 메모리 효율성
            "mirostat": 2        # 고급 샘플링
        }

        # 모델별 어댑터 설정
        self._set_adapter(model)

        # HTTP 클라이언트 세션
        self._http_client = None

        # 디버그 모드 설정
        self.debug_mode = debug_mode

        # 디버그 모드 초기화 상태 정보 출력
        print(f"[OllamaClient] 초기화 - 디버그 모드: {self.debug_mode}")
        if self.debug_mode:
            print(f"[OllamaClient] 사용할 모델: {self.model}")
            print(f"[OllamaClient] Ollama URL: {self.ollama_url}")
            print(f"[OllamaClient] GPU 파라미터: {self.gpu_params}")


    def _set_adapter(self, model_name: str):
        """
        모델에 맞는 어댑터 설정

        Args:
            model_name: 모델 이름
        """
        self.adapter = get_adapter_for_model(model_name)

    async def _get_http_client(self):
        """
        HTTP 클라이언트 세션 반환 (필요시 생성)

        Returns:
            httpx.AsyncClient: 비동기 HTTP 클라이언트 인스턴스
        """
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=120.0)
        return self._http_client

    async def close(self):
        """
        HTTP 클라이언트 연결 종료
        """
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    async def generate(self,
                       prompt: str,
                       system_prompt: Optional[str] = None,
                       temperature: Optional[float] = None,
                       max_retries: Optional[int] = None) -> str:
        """
        어댑터 패턴을 사용하여 현재 모델에 맞게 텍스트 생성

        Args:
            prompt: 입력 프롬프트
            system_prompt: 시스템 프롬프트 (선택사항)
            temperature: 생성 온도 (None이면 기본값 사용)
            max_retries: 최대 재시도 횟수

        Returns:
            str: 생성된 텍스트
        """
        max_retries = max_retries or self.max_retries
        temp = temperature if temperature is not None else self.temperature

        # 어댑터를 사용하여 현재 모델에 맞는 요청 형식 생성
        payload, endpoint_path = await self.adapter.format_request(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temp,
            max_tokens=self.max_tokens,
            gpu_params=self.gpu_params
        )

        # 모델 이름 추가
        payload["model"] = self.model

        # 디버깅 로그 추가 (디버그 모드일 때만)
        if self.debug_mode:
            print(f"[디버그] OllamaClient.generate 호출: 모델={self.model}, 엔드포인트={endpoint_path}")
            print(f"[디버그] 프롬프트 길이: {len(prompt)} 자")
            print(f"[디버그] 페이로드: {str(payload)[:300]}...")

        # 재시도 메커니즘
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                # HTTP 클라이언트 가져오기
                client = await self._get_http_client()

                # API 요청
                if self.debug_mode:
                    print(f"[디버그] API 요청 시작 (시도 {attempt+1}/{max_retries+1})")
                response = await client.post(
                    f"{self.ollama_url}{endpoint_path}",  # 어댑터가 제공한 엔드포인트 사용
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                response.raise_for_status()  # HTTP 오류 확인

                # 응답 파싱
                result = response.json()

                # 디버그 모드일 때만 로그 출력
                if self.debug_mode:
                    print(f"[디버그] API 응답 수신: 상태 코드={response.status_code}")
                    print(f"[디버그] 응답 키: {list(result.keys())}")

                    # raw 응답 로그
                    raw_snippet = str(result.get('response', ''))[:50]
                    print(f"[디버그] 원시 응답 일부: {raw_snippet}...")

                # 어댑터를 사용하여 모델별 응답 파싱
                generated_text = self.adapter.parse_response(result)

                # 응답 품질 검사
                is_invalid_response = False
                reason = ""

                # 1. 숫자만 있는 경우 검사 (예: "356")
                if generated_text.isdigit() or (
                    generated_text.replace('.', '', 1).isdigit() and generated_text.count('.') <= 1
                ):
                    is_invalid_response = True
                    reason = f"숫자만 반환됨 ({generated_text})"

                # 2. 너무 짧은 응답 검사 (특히 txgemma-predict 모델)
                elif len(generated_text.strip()) < 100 and self.model == "txgemma-predict:latest":
                    is_invalid_response = True
                    reason = f"응답이 너무 짧음 ({len(generated_text.strip())} 문자)"

                # 3. txgemma-predict 모델에 대한 특별 검사
                elif self.model == "txgemma-predict:latest":
                    # 근육/건강 관련 키워드가 포함되어 있는지 검사
                    keywords = ['근육', '건강', '보충제', '영양', '단백질', '효과', '참고문헌']
                    has_keywords = any(keyword in generated_text.lower() for keyword in keywords)

                    # 메타데이터 변경 이후 유효한 출력이 없을 때
                    if not has_keywords:
                        is_invalid_response = True
                        reason = "관련 키워드가 포함되지 않음"

                    # 오류 메시지 검사
                    error_terms = ['error', 'exception', '오류', '실패', '\\n\\n\\n']
                    if any(term in generated_text.lower() for term in error_terms):
                        is_invalid_response = True
                        reason = "오류 메시지 포함"

                # 마크다운 형식 검증 (특히 txgemma 모델)
                if self.model.startswith("txgemma") and "#" not in generated_text and "\n\n" not in generated_text:
                    is_invalid_response = True
                    reason = "마크다운 형식이 아님"

                if is_invalid_response and self.debug_mode:
                    print(f"[디버그] 유효하지 않은 응답: {reason}")
                    # 사용자 친화적인 대체 메시지 반환
                    generated_text = f"""
# 근육 관련 건강기능식품 정보

안녕하세요, 도움이 필요하신 내용을 정확히 이해했습니다.

죄송합니다. 현재 모델({self.model})이 이 질문에 대해 적절한 응답을 생성하지 못했습니다. 이는 모델의 한계일 수 있습니다.

## 다른 대안

1. **다른 모델 사용**:
   - `/model Gemma3` - 더 안정적이고 다양한 정보 제공 가능
   - `/model txgemma-chat` - 대화형 모델로 다른 형식의 응답 제공

2. **질문 구체화**:
   - 더 구체적인 질문을 해보세요 (ex: "특정 보충제의 효과는 무엇인가요?")

3. **피드백 모드 사용**:
   - `/feedback` 명령어로 더 깊은 연구 수행 가능

## 참고 문헌

1. Journal of the International Society of Sports Nutrition (https://jissn.biomedcentral.com/)
2. American Journal of Clinical Nutrition (https://academic.oup.com/ajcn)
"""

                # 응답 후처리
                generated_text = self.adapter.post_process(generated_text)

                # 최소 길이 확인
                if not generated_text or generated_text.isspace():
                    print("[경고] 빈 응답이 반환되었습니다")
                    generated_text = "[응답이 생성되지 않았습니다. 다시 시도하거나 다른 모델을 사용해보세요. `/model Gemma3`]"

                if len(generated_text) < self.min_response_length:
                    print(f"⚠️ 경고: 생성된 텍스트가 너무 짧습니다 ({len(generated_text)} 자)")

                    # 너무 짧은 응답에 대한 처리 (숫자만 있는 경우)
                    if len(generated_text) < 10 and (generated_text.isdigit() or generated_text.replace('.', '', 1).isdigit()):
                        generated_text = "[응답이 너무 짧습니다. 다시 질문하거나 `/model Gemma3` 명령어로 모델을 변경해보세요.]"

                # 응답 내용 미리보기 로그
                if self.debug_mode:
                    print(f"[디버그] 최종 응답 길이: {len(generated_text)} 자")
                    print(f"[디버그] 응답 미리보기: {generated_text[:200]}...")

                return generated_text

            except httpx.HTTPStatusError as e:
                last_error = f"HTTP 오류: {e.response.status_code} - {e.response.text}"
                print(f"API 요청 실패 (시도 {attempt + 1}/{max_retries + 1}): {last_error}")

                # 429 Too Many Requests와 같은 경우에만 재시도
                if e.response.status_code == 429:
                    backoff_time = 2 ** attempt
                    print(f"⏱️ {backoff_time}초 후 재시도합니다...")
                    await asyncio.sleep(backoff_time)
                    continue
                raise

            except (httpx.RequestError, json.JSONDecodeError, ValueError) as e:
                last_error = str(e)
                print(f"시도 {attempt + 1}/{max_retries + 1} 실패: {last_error}")
                if attempt < max_retries:
                    backoff_time = 1 + attempt * 2
                    print(f"⏱️ {backoff_time}초 후 재시도합니다...")
                    await asyncio.sleep(backoff_time)
                else:
                    print(f"⛔ 최대 재시도 횟수 초과: {last_error}")

        # 모든 시도 실패
        error_msg = f"모든 시도가 실패했습니다. 마지막 오류: {last_error}"
        print(f"❌ {error_msg}")
        return f"[응답 생성 실패: {error_msg}]"

    async def generate_parallel(self, prompts: List[Dict[str, Any]], max_concurrent: int = 2) -> List[str]:
        """
        여러 프롬프트에 대해 병렬로 텍스트 생성

        Args:
            prompts: 프롬프트 목록 (각각 'prompt', 'system' 키 포함 가능)
            max_concurrent: 최대 동시 요청 수 (기본값: 2)

        Returns:
            List[str]: 생성된 텍스트 목록
        """
        results = []

        # 세마포어를 사용하여 동시 요청 제한
        semaphore = asyncio.Semaphore(max_concurrent)

        async def _generate_with_limit(prompt_data):
            # 세마포어 사용하여 병렬 요청 제한
            async with semaphore:
                if isinstance(prompt_data, dict):
                    prompt = prompt_data.get('prompt', "")
                    system = prompt_data.get('system', None)
                    temp = prompt_data.get('temperature', None)
                else:
                    prompt = str(prompt_data)
                    system = None
                    temp = None

                return await self.generate(prompt, system_prompt=system, temperature=temp)

        # 병렬 작업 실행
        tasks = [_generate_with_limit(prompt_data) for prompt_data in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 예외 처리
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                results[i] = f"[오류: {result!s}]"

        return results

    def update_model(self, model_name: str):
        """
        모델 변경 및 어댑터 업데이트

        Args:
            model_name: 새로운 모델 이름
        """
        self.model = model_name
        self._set_adapter(model_name)

    def set_debug_mode(self, debug_mode: bool):
        """
        디버그 모드 설정

        Args:
            debug_mode: 디버그 모드 활성화 여부
        """
        self.debug_mode = debug_mode

    async def check_availability(self) -> dict:
        """Ollama API 연결 및 모델 가용성 확인"""
        try:
            # API 연결 확인
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_url}/api/tags") as response:
                    if response.status == 200:
                        print("✅ Ollama API 연결 성공")
                        
                        # 모델 확인
                        data = await response.json()
                        models = [model["name"] for model in data.get("models", [])]
                        if self.model in models:
                            print(f"✅ 모델 '{self.model}' 확인됨")
                            return {"available": True, "models": models}
                        else:
                            print(f"❌ 모델 '{self.model}'을 찾을 수 없습니다.")
                            print(f"🔧 해결방법: ollama pull {self.model}")
                            return {"available": False, "error": f"모델 '{self.model}'을 찾을 수 없습니다.", "models": models}
                    else:
                        print("❌ Ollama API 연결 실패")
                        return {"available": False, "error": "Ollama API 연결 실패"}
        except Exception as e:
            print(f"❌ 모델 확인 중 오류 발생: {str(e)}")
            return {"available": False, "error": str(e)}

    async def list_models(self) -> List[Dict[str, Any]]:
        """
        사용 가능한 모델 목록 가져오기

        Returns:
            List[Dict[str, Any]]: 사용 가능한 모델 목록
        """
        try:
            client = await self._get_http_client()
            response = await client.get(f"{self.ollama_url}/api/tags")
            response.raise_for_status()

            # API 응답에서 모델 목록 추출
            return response.json().get("models", [])
        except Exception as e:
            print(f"모델 목록 가져오기 오류: {e!s}")
            return []

    async def check_model_availability(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        특정 모델이 사용 가능한지 확인

        Args:
            model_name: 확인할 모델 이름 (기본값: 현재 모델)

        Returns:
            Dict[str, Any]: 모델 가용성 정보
        """
        model = model_name or self.model

        try:
            # 사용 가능한 모델 목록 가져오기
            models_list = await self.list_models()

            # 모델명만 추출 (대소문자 무관)
            available_models = []
            for m in models_list:
                name = m.get("name", "")
                if name:  # 빈 경우 처리
                    available_models.append(name)

            # 대소문자 구분 없이 비교
            is_available = False
            matched_model = None

            for avail_model in available_models:
                # 정확히 동일한 경우
                if model == avail_model:
                    is_available = True
                    matched_model = avail_model
                    break
                # 대소문자 무관하고 비교
                elif model.lower() == avail_model.lower():
                    is_available = True
                    matched_model = avail_model
                    break

            if is_available:
                # 적합한 어댑터 추가 확인
                adapter_class = get_adapter_for_model(model).__class__.__name__

                return {
                    "available": True,
                    "model": matched_model,  # 실제 설치된 모델명 반환
                    "adapter": adapter_class
                }
            else:
                return {
                    "available": False,
                    "model": model,
                    "message": f"모델 '{model}'이(가) 설치되어 있지 않습니다.",
                    "available_models": available_models
                }

        except Exception as e:
            return {
                "available": False,
                "model": model,
                "error": str(e),
                "message": f"모델 가용성 확인 중 오류 발생: {e!s}"
            }


# 모듈 직접 실행 시 테스트
if __name__ == "__main__":
    async def test():
        client = OllamaClient()

        # API 가용성 확인
        status = await client.check_availability()
        print(f"Ollama API 상태: {status}")

        if status:
            # 단일 생성 테스트
            response = await client.generate(
                prompt="근육 발달에 가장 중요한 영양소 3가지를 간단히 설명해주세요.",
                system_prompt="당신은 근육 관련 건강기능식품 전문가입니다. 간결하고 정확하게 답변해주세요."
            )
            print(f"\n생성된 응답:\n{response}")

    asyncio.run(test())
