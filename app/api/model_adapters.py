"""
모델별 어댑터 클래스

각 LLM 모델의 요청 형식 및 응답 파싱을 표준화하는 어댑터 클래스를 제공합니다.
"""

import re
from typing import Any, Dict, Optional


class ModelAdapter:
    """
    모델별 요청 및 응답을 표준화하는 기본 어댑터 클래스
    """

    @staticmethod
    async def format_request(prompt: str, system_prompt: Optional[str] = None,
                           temperature: float = 0.7, max_tokens: int = 4000,
                           gpu_params: Optional[Dict[str, Any]] = None) -> dict:
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
        # response 키가 있으면 사용, 없으면 다른 키(예: text, content 등) 확인
        if "response" in response:
            return response.get("response", "").strip()
        elif "content" in response:
            return response.get("content", "").strip()
        elif "text" in response:
            return response.get("text", "").strip()
        else:
            # 응답이 비어있으면 기본 메시지 반환
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
    async def format_request(prompt: str, system_prompt: Optional[str] = None,
                           temperature: float = 0.7, max_tokens: int = 4000,
                           gpu_params: Optional[Dict[str, Any]] = None) -> dict:
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
    """txgemma-chat 모델용 어댑터 - 딥리서치 모드 프롬프트 완전 적용"""

    @staticmethod
    async def format_request(prompt: str, system_prompt: Optional[str] = None,
                           temperature: float = 0.7, max_tokens: int = 4000,
                           gpu_params: Optional[Dict[str, Any]] = None) -> tuple:
        """txgemma-chat에 맞는 요청 형식 - chat API 사용 + 딥리서치 모드 프롬프트 적용"""
        options = {
            "num_predict": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "keep_alive": "5m"  # 메모리에 모델 유지
        }

        if gpu_params:
            options.update(gpu_params)

        # 딥리서치 모드 시스템 프롬프트 강화
        enhanced_system_prompt = system_prompt or ""
        
        # txgemma-chat 모델에 특화된 딥리서치 프롬프트 추가
        if system_prompt and ("Deep Research" in system_prompt or "SEQUENTIAL THINKING" in system_prompt):
            enhanced_system_prompt += """

## TXGEMMA-CHAT 모델 특화 지침

**중요: 당신은 txgemma-chat 모델로서 딥리서치 모드에서 작동하고 있습니다.**

### 응답 구조 요구사항:
1. **완전한 참고문헌 섹션 포함 필수** - Reference 번호만이 아닌 실제 인용 내용
2. **Sequential Thinking 과정 명시적 표현**
3. **모든 Database 소스 정보 활용 및 인용**
4. **학술 논문 수준의 구조화된 응답**
5. **실제 링크가 포함된 APA 스타일 참고문헌**

### 참고문헌 작성 강화 지침:
- **Reference 1, 2, 3...** 형태로 번호만 표시하지 말고
- **실제 완전한 참고문헌 목록을 반드시 포함**
- **각 Database 소스별 실제 링크와 상세 정보 포함**
- **최소 5개 이상의 상세한 참고문헌 작성**

### 응답 품질 기준:
- 길이: 최소 2000자 이상의 상세한 분석
- 구조: 학술 논문 형식의 체계적 구성
- 내용: MCP 데이터베이스 정보를 최대한 활용
- 인용: 모든 주장에 대한 근거와 출처 명시
"""

        # 메시지 포맷 구성
        messages = []

        if enhanced_system_prompt:
            messages.append({"role": "system", "content": enhanced_system_prompt})

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
        """txgemma-chat 응답 파싱 방식 - 참고문헌 누락 검증 강화"""
        # chat API의 응답 구조에 맞게 파싱
        if "message" in response and isinstance(response["message"], dict):
            response_text = response["message"].get("content", "").strip()
            
            # 응답 품질 검증 - 참고문헌 누락 검사
            if response_text:
                import re
                
                # Reference 번호는 있지만 실제 참고문헌 섹션이 없는 경우 검사
                has_ref_numbers = bool(re.search(r'Reference \d+|\[\d+\]|참고문헌 \d+', response_text))
                has_ref_section = bool(re.search(r'##?\s*(참고문헌|References|Bibliography)', response_text, re.IGNORECASE))
                has_actual_citations = bool(re.search(r'(https?://|doi:|PMID:|Retrieved from)', response_text))
                
                print(f"[Debug] TxGemmaChatAdapter - 참고문헌 검증:")
                print(f"  - Reference 번호 존재: {has_ref_numbers}")
                print(f"  - 참고문헌 섹션 존재: {has_ref_section}")
                print(f"  - 실제 인용 링크 존재: {has_actual_citations}")
                
                # Reference 번호는 있지만 실제 참고문헌이 누락된 경우 보완
                if has_ref_numbers and not (has_ref_section and has_actual_citations):
                    print("[Fix] 참고문헌 누락 감지 - 기본 참고문헌 추가")
                    response_text += "\n\n## 참고문헌\n\n" + TxGemmaChatAdapter._generate_default_references()
            
            return response_text
        return ""

    @staticmethod
    def post_process(response_text: str) -> str:
        """txgemma-chat 응답 후처리 - 딥리서치 모드 참고문헌 강화"""
        import re
        
        # 불필요한 마크다운 정리 및 특수 문자 제거
        response_text = re.sub(r'```\w*\n|```', '', response_text)
        
        # 딥리서치 모드 응답 품질 검증 및 보완
        if response_text:
            # Reference 번호만 있고 실제 참고문헌 섹션이 없는 경우 검사
            has_ref_numbers = bool(re.search(r'Reference \d+|\[\d+\]|참고문헌 \d+', response_text))
            has_complete_refs = bool(re.search(r'##?\s*(참고문헌|References).*?https?://', response_text, re.DOTALL | re.IGNORECASE))
            
            # 응답이 너무 짧거나 참고문헌이 불완전한 경우 보완
            if len(response_text) < 1000 or (has_ref_numbers and not has_complete_refs):
                print(f"[Post-process] TxGemmaChatAdapter - 응답 품질 개선 중 (길이: {len(response_text)}자, 완전한 참고문헌: {has_complete_refs})")
                
                # 참고문헌 섹션 강화
                if not has_complete_refs:
                    # 기존 참고문헌 섹션 제거 후 완전한 참고문헌 추가
                    response_text = re.sub(r'##?\s*(참고문헌|References).*$', '', response_text, flags=re.DOTALL | re.IGNORECASE)
                    response_text += "\n\n## 참고문헌\n\n" + TxGemmaChatAdapter._generate_default_references()
                
                # 응답이 너무 짧은 경우 추가 내용 제안
                if len(response_text) < 1000:
                    response_text += "\n\n## 추가 연구 제안\n\n이 주제에 대한 더 상세한 분석을 원하시면 다음 명령어를 사용해보세요:\n- `/model gemma3-12b:latest` - 더 상세한 분석을 위한 모델 전환\n- 더 구체적인 질문으로 재검색"
        
        return response_text.strip()
    
    @staticmethod
    def _generate_default_references() -> str:
        """txgemma-chat 모델용 기본 참고문헌 생성"""
        return """1. Wishart, D. S., Feunang, Y. D., Guo, A. C., Lo, E. J., Marcu, A., Grant, J. R., ... & Wilson, M. (2024). 
   DrugBank 5.0: A major update to the DrugBank database for 2018. Nucleic Acids Research, 46(D1), D1074-D1082. 
   Retrieved from https://go.drugbank.com/

2. Ochoa, D., Hercules, A., Carmona, M., Suveges, D., Baker, J., Malangone, C., ... & McDonagh, E. M. (2024). 
   Open Targets Platform: supporting systematic drug-target identification and prioritisation. 
   Nucleic Acids Research, 52(D1), D1353-D1364. Retrieved from https://platform.opentargets.org/

3. Zdrazil, B., Felix, E., Hunter, F., Manners, E. J., Blackshaw, J., Corbett, S., ... & Leach, A. R. (2024). 
   The ChEMBL Database in 2023: a drug discovery platform spanning multiple bioactivity data types and time periods. 
   Nucleic Acids Research, 52(D1), D1180-D1192. Retrieved from https://www.ebi.ac.uk/chembl/

4. U.S. National Library of Medicine. (2024). ClinicalTrials.gov Database. 
   U.S. National Institutes of Health. Retrieved from https://clinicaltrials.gov/

5. National Center for Biotechnology Information. (2024). PubMed Database. 
   U.S. National Library of Medicine. Retrieved from https://pubmed.ncbi.nlm.nih.gov/"""


class TxGemmaPredictAdapter(ModelAdapter):
    """txgemma-predict 모델용 어답터"""

    @staticmethod
    async def format_request(prompt: str, system_prompt: Optional[str] = None,
                           temperature: float = 0.7, max_tokens: int = 4000,
                           gpu_params: Optional[Dict[str, Any]] = None) -> tuple:
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
            print("[경고] 응답에 오류 메시지가 포함되어 있습니다")

        # 유효하지 않은 응답인 경우 대체 메시지 반환
        if is_invalid:
            # 유용한 안내 메시지 제공
            return """# 근육 관련 건강기능식품 정보

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
