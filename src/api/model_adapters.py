"""
모델별 어댑터 클래스

각 LLM 모델의 요청 형식 및 응답 파싱을 표준화하는 어댑터 클래스를 제공합니다.
"""

import re
import json
from typing import Dict, Any, Optional, List

class ModelAdapter:
    """
    모델별 요청 및 응답을 표준화하는 기본 어댑터 클래스
    """
    
    @staticmethod
    async def format_request(prompt: str, system_prompt: str = None, 
                           temperature: float = 0.7, max_tokens: int = 4000, 
                           gpu_params: Dict[str, Any] = None) -> dict:
        """
        요청 형식 표준화
        
        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트
            temperature: 생성 온도
            max_tokens: 최대 토큰 수
            gpu_params: GPU 최적화 파라미터
            
        Returns:
            dict: 표준화된 API 요청 페이로드
        """
        options = {
            "num_predict": max_tokens,
        }
        
        if gpu_params:
            options.update(gpu_params)
            
        payload = {
            "prompt": prompt,
            "stream": False,
            "temperature": temperature,
            "options": options
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        return payload, "/api/generate"  # 엔드포인트와 함께 반환
        
    @staticmethod
    def parse_response(response: dict) -> str:
        """
        응답 파싱 표준화
        
        Args:
            response: API 응답
            
        Returns:
            str: 파싱된 응답 텍스트
        """
        # 디버깅용 출력
        print(f"[디버그 응답] 응답 키: {list(response.keys())}")
        
        # response 키가 있으면 사용, 없으면 다른 키(예: text, content 등) 확인
        if "response" in response:
            return response.get("response", "").strip()
        elif "content" in response:
            return response.get("content", "").strip()
        elif "text" in response:
            return response.get("text", "").strip()
        else:
            # 응답이 비어있으면 기본 메시지 반환
            print(f"[경고] 응답에서 텍스트를 찾을 수 없습니다: {str(response)[:200]}")
            return "[응답을 파싱할 수 없습니다. 다시 시도해주세요.]"            
    
    @staticmethod
    def post_process(response_text: str) -> str:
        """
        모델별 응답 후처리
        
        Args:
            response_text: 원본 응답 텍스트
            
        Returns:
            str: 후처리된 응답 텍스트
        """
        # 응답이 비어있는 경우 처리
        if not response_text or response_text.isspace():
            return "[응답이 비어있습니다. 다시 시도해주세요.]"
            
        # 마크다운 형식이 없는 경우 기본 구조 추가
        if "#" not in response_text and len(response_text.split("\n\n")) < 3:
            formatted_text = f"# 응답\n\n{response_text}\n\n## 참고 문헌\n\n- 추가 참고 문헌 필요"
            return formatted_text
            
        return response_text


class GemmaAdapter(ModelAdapter):
    """Gemma3 모델용 어댑터"""
    
    @staticmethod
    async def format_request(prompt: str, system_prompt: str = None, 
                           temperature: float = 0.7, max_tokens: int = 4000, 
                           gpu_params: Dict[str, Any] = None) -> dict:
        """Gemma3에 맞는 요청 형식"""
        # Gemma3는 기본 포맷 사용
        return await ModelAdapter.format_request(
            prompt=prompt, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            max_tokens=max_tokens, 
            gpu_params=gpu_params
        )
        
    @staticmethod
    def parse_response(response: dict) -> str:
        """Gemma3 응답 파싱 방식"""
        return ModelAdapter.parse_response(response)
        
    @staticmethod
    def post_process(response_text: str) -> str:
        """Gemma3 응답 후처리"""
        # 불필요한 시작 태그 제거
        response_text = re.sub(r'^<answer>', '', response_text)
        response_text = re.sub(r'</answer>$', '', response_text)
        
        return response_text.strip()


class TxGemmaChatAdapter(ModelAdapter):
    """txgemma-chat 모델용 어댑터"""
    
    @staticmethod
    async def format_request(prompt: str, system_prompt: str = None, 
                           temperature: float = 0.7, max_tokens: int = 4000, 
                           gpu_params: Dict[str, Any] = None) -> tuple:
        """txgemma-chat에 맞는 요청 형식 - chat API 사용"""
        options = {
            "num_predict": max_tokens,
        }
        
        if gpu_params:
            options.update(gpu_params)
            
        # 메시지 포맷 구성
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "messages": messages,
            "stream": False,
            "temperature": temperature,
            "options": options
        }
        
        return payload, "/api/chat"  # chat 엔드포인트 사용
        
    @staticmethod
    def parse_response(response: dict) -> str:
        """txgemma-chat 응답 파싱 방식"""
        # chat API의 응답 구조에 맞게 파싱
        if "message" in response and isinstance(response["message"], dict):
            return response["message"].get("content", "").strip()
        return ""
    
    @staticmethod
    def post_process(response_text: str) -> str:
        """txgemma-chat 응답 후처리"""
        # 불필요한 마크다운 정리 및 특수 문자 제거
        response_text = re.sub(r'```\w*\n|```', '', response_text)
        
        return response_text.strip()


class TxGemmaPredictAdapter(ModelAdapter):
    """txgemma-predict 모델용 어답터"""
    
    @staticmethod
    async def format_request(prompt: str, system_prompt: str = None, 
                           temperature: float = 0.7, max_tokens: int = 4000, 
                           gpu_params: Dict[str, Any] = None) -> tuple:
        """txgemma-predict에 맞는 요청 형식"""
        # txgemma-predict는 chat 아닌 chat-completions 엔드포인트 사용
        options = {
            "num_predict": max_tokens,
            # raw 모드에 문제가 있으므로 끄기
            "raw": False,
            "seed": 42,  # 일관성 있는 응답을 위해 씨드 고정
            "num_ctx": 8192,  # 더 긴 컨텍스트 사용 허용
            "top_k": 40,  # 다양한 토큰 생성 허용
            "top_p": 0.9  # 다양한 토큰 생성 허용
        }
        
        if gpu_params:
            options.update(gpu_params)
            
        # 기본 시스템 프롬프트 강화 - 특히 마크다운 형식을 강조
        enhanced_system_prompt = """당신은 근육 관련 건강기능식품 전문가입니다. 사용자의 질문에 과학적 근거와 참고문헌을 포함하여 상세하게 답변해주세요.

마크다운 형식으로 담긴 정확한 정보를 제공하세요.

다음 형식으로 작성해주세요:
# 답변

## 문제 정의
[질문에 대한 배경 및 정의 설명]

## 핵심 내용
[관련 이론, 개념, 원리 설명]

## 과학적 근거
[관련 연구 결과 및 데이터 포함]

## 복용 방법 및 주의사항
[제품 사용법, 복용량, 주의사항 등]

## 결론
[요약 및 정리]

## 참고문헌
1. [문헌명] (URL 포함)
2. [문헌명] (URL 포함)
"""
        
        # 프롬프트 강화 - 질문-응답 형식으로 구성
        # 이 모델은 채팅용이 아니미로 질문과 응답 형식을 명확히 제시
        enhanced_prompt = f"""질문: {prompt}

응답:
# 근육 관련 건강기능식품 정보

## 문제 정의
"""
        
        # 기본 generate API 사용
        payload = {
            "model": "txgemma-predict:latest",  # 모델을 명시적으로 지정
            "prompt": enhanced_prompt,
            "stream": False,
            "temperature": 0.9,  # 다양한 응답을 위해 온도 증가
            "options": options
        }
        
        # 시스템 프롬프트 사용
        if system_prompt:
            payload["system"] = system_prompt
        else:
            payload["system"] = enhanced_system_prompt
            
        print(f"[디버그] TxGemmaPredictAdapter - 생성 요청: \n"
              f"  프롬프트: {enhanced_prompt[:50]}...\n"
              f"  시스템: {enhanced_system_prompt[:50]}...")
        
        return payload, "/api/generate"  # 기본 generate 엔드포인트 사용
        
    @staticmethod
    def parse_response(response: dict) -> str:
        """txgemma-predict 응답 파싱 방식"""
        response_text = ModelAdapter.parse_response(response)
        
        # 디버그 로그 추가
        print(f"[디버그] TxGemmaPredictAdapter 응답 길이: {len(response_text)} 문자")
        if len(response_text) < 50:
            print(f"[디버그] TxGemmaPredictAdapter 응답 내용: {response_text}")
        
        # 응답 품질 검증 - 다양한 케이스 처리
        is_invalid = False
        
        # 1. 숫자만 반환되는 경우 검사
        if response_text.isdigit() or (response_text.replace('.', '', 1).isdigit() and response_text.count('.') <= 1):
            is_invalid = True
            print(f"[경고] 숫자만 반환되었습니다: {response_text}")
        
        # 2. 너무 짧은 응답 검사
        elif len(response_text.strip()) < 100:
            is_invalid = True
            print(f"[경고] 응답이 너무 짧습니다 ({len(response_text.strip())} 문자)")
            
        # 3. 응답 내용에 제대로된 내용이 포함되어 있는지 검사
        elif not any(keyword in response_text.lower() for keyword in ['근육', '건강', '보충제', '영양', '단백질', '효과']):
            is_invalid = True
            print("[경고] 응답에 관련 키워드가 없습니다")
        
        # 4. 시스템 오류 메시지가 포함되어 있는지 검사
        elif any(err_msg in response_text for err_msg in ['error', 'exception', 'failed', '오류', '실패']):
            is_invalid = True
            print(f"[경고] 응답에 오류 메시지가 포함되어 있습니다")
            
        # 유효하지 않은 응답인 경우 대체 메시지 반환
        if is_invalid:
            # 유용한 안내 메시지 제공
            return f"""# 근육 관련 건강기능식품 정보

안녕하세요, 제가 도움을 드리겠습니다.

현재 TxGemma-predict 모델이 이 질문에 대해 충분히 자세한 응답을 생성하지 못했습니다. 이는 모델의 한계나 기술적 문제일 수 있습니다.

## 해결 방법

다음 방법으로 더 나은 결과를 얻을 수 있습니다:

1. **다른 모델로 변경해보세요**:
   - `/model Gemma3` - 기본 Gemma 모델 (더 안정적)
   - `/model txgemma-chat` - 대화용 모델 (다른 형식)

2. **질문을 더 구체적으로 작성해보세요**:
   - 특정 보충제나 성분에 대한 정보를 요청
   - 구체적인 건강 목표나 상황을 설명

3. **피드백 모드를 사용해보세요**:
   - `/feedback` 명령어로 더 깊은 연구 수행

도움이 필요하시면 `/help` 명령어로 사용 가능한 옵션을 확인하세요.
"""
            
        # 응답 품질이 양호한 경우 원본 반환
        return response_text
    
    @staticmethod
    def post_process(response_text: str) -> str:
        """txgemma-predict 특화 후처리"""
        # 특정 패턴 제거 (화학식 등 불필요한 출력)
        response_text = re.sub(r'[A-Z]\([^)]*\)', '', response_text)
        response_text = re.sub(r'1\.B\(O\)\(O\)O\.C\(.*?\)', '', response_text)
        
        # 마크다운 형식이 없는 경우 기본 구조 추가
        if "#" not in response_text and len(response_text.split("\n\n")) < 3 and len(response_text) > 50:
            response_text = f"# 근육과 건강기능식품 정보\n\n{response_text}\n\n## 참고 문헌\n\n1. Journal of the International Society of Sports Nutrition (https://jissn.biomedcentral.com/)\n2. American Journal of Clinical Nutrition (https://academic.oup.com/ajcn)\n"
        
        return response_text.strip()


# 모델명에 따라 적절한 어댑터를 선택하는 팩토리 함수
def get_adapter_for_model(model_name: str) -> ModelAdapter:
    """
    모델에 맞는 어댑터 반환
    
    Args:
        model_name: 모델 이름
        
    Returns:
        ModelAdapter: 해당 모델용 어댑터 인스턴스
    """
    model_name = model_name.lower()
    
    if "gemma3" in model_name:
        return GemmaAdapter()
    elif "txgemma-chat" in model_name:
        return TxGemmaChatAdapter()
    elif "txgemma-predict" in model_name:
        return TxGemmaPredictAdapter()
    else:
        # 기본 어댑터
        return ModelAdapter()
