# 근육 관련 건강기능식품 연구 시스템

Ollama LLM을 활용한 근육 건강기능식품 연구 및 추천 시스템입니다. GPU 가속, 병렬 처리, 피드백 루프를 통해 높은 품질의 과학적 근거 기반 답변을 생성합니다.

<div align="center">

**최신 버전: 1.2.0 (2025-06-10)**
</div>

## 주요 기능

### 고성능 AI 응답 생성
- **GPU 가속**: RTX 4090 최적화 파라미터 적용 (`num_gpu: 99`, `num_thread: 8`, `f16_kv: true`, `mirostat: 2`)
- **모델 우선순위**: `Gemma3:latest`를 우선 사용, 자동 폴백 메커니즘
- **병렬 처리**: 답변 병렬 생성 (최대 `FEEDBACK_WIDTH` 값만큼 동시 생성)
- **비동기 I/O**: `asyncio`를 활용한 응답성 높은 인터페이스

### 연구 품질 최적화
- **피드백 루프**: 자체 평가 및 개선 과정 (깊이/너비 설정 가능)
- **품질 지표**: 응답 길이, 참고 문헌 수, 구조적 완성도 자동 평가
- **마크다운 포맷**: 체계적인 응답 구조 및 가독성 높은 결과 제공
  - 문제 정의, 핵심 내용, 과학적 근거, 복용 방법, 결론, 참고 문헌 포함

### 사용자 경험
- **대화형 CLI**: 직관적인 명령어 시스템 (`/debug`, `/model`, `/feedback` 등)
- **디버그 모드**: 실시간 디버깅 정보 토글 기능 (v1.2.0 추가)
- **저장 시스템**: 사용자 친화적 저장 프롬프트 및 명확한 경로 표시
- **배치 처리**: JSON 또는 텍스트 파일을 통한 다중 질문 처리

## 시스템 요구사항

### 필수 환경
- **운영체제**: Ubuntu 24.04 이상 (Ubuntu 22.04 LTS에서도 테스트 완료)
- **파이썬**: Python 3.13.2 이상 (비동기 기능 지원)
- **Ollama**: [Ollama](https://ollama.ai/) 0.2.1 이상 (로컬 LLM 서버)

### 권장 환경
- **GPU**: NVIDIA GPU, RTX 4090 이상 권장 (CUDA 12.0+)
- **메모리**: 16GB 이상 권장 (32GB 이상 최적)
- **저장공간**: 20GB 이상 여유 공간 (모델 파일 포함)

### LLM 모델
- **기본 모델**: `Gemma3:latest` (권장, 최상의 성능)
- **호환 모델**: `txgemma-predict:latest`, `txgemma-chat:latest` 등

## 설치 방법

### 1. 저장소 복제 및 설정

```bash
# 저장소 복제
git clone https://github.com/yourusername/GAIA_LLMs.git
cd GAIA_LLMs

# 가상 환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows
```

### 2. 의존성 패키지 설치

```bash
# uv 사용 (권장, 최대 5배 빠른 설치)
uv pip install -r requirements.txt

# 또는 일반 pip 사용
# pip install -r requirements.txt
```

### 3. Ollama 설치 및 모델 준비

```bash
# Ollama 설치 (Linux)
curl -fsSL https://ollama.com/install.sh | sh

# 기본 모델 다운로드
ollama pull gemma3:latest

# 추가 모델 설치 (선택사항)
ollama pull txgemma-predict:latest
ollama pull txgemma-chat:latest
```

## 환경 설정

### 기본 환경 변수 구성

1. 환경 변수 템플릿 파일을 복사하여 사용합니다:
   ```bash
   cp .env.example .env
   ```

2. `.env` 파일을 편집하여 환경에 맞게 구성합니다:
   ```ini
   # Ollama API 관련 설정
   OLLAMA_BASE_URL="http://localhost:11434"  # Ollama 서버 주소
   OLLAMA_MODEL="Gemma3:latest"             # 기본 모델
   
   # 응답 생성 품질 관련 설정
   MIN_RESPONSE_LENGTH=1000                # 최소 응답 길이(문자)
   MIN_REFERENCES=2                        # 최소 참고문헌 수
   
   # 피드백 루프 관련 설정
   FEEDBACK_DEPTH=2                        # 피드백 반복 횟수
   FEEDBACK_WIDTH=2                        # 병렬 대안 수
   
   # 결과 저장 관련 설정
   OUTPUT_DIR="./research_outputs"          # 결과 저장 디렉토리
   ```

### 고급 설정

`.env` 파일에서 다음과 같은 추가 환경 변수를 구성할 수 있습니다:

```ini
# GPU 최적화 설정 (선택사항)
NUM_GPU=99                               # 사용할 GPU 수 (99=전체)
NUM_THREAD=8                             # 병렬 스레드 수
F16_KV=true                              # 메모리 효율성
MIROSTAT=2                               # 고급 샘플링 방법
```

## 사용 방법

### 명령행 실행

```bash
# 대화형 모드(가장 일반적인 사용법)
python main.py -i

# 단일 질문 연구 실행
python main.py -q "근육 발달에 가장 중요한 아미노산은 무엇인가요?"

# 피드백 깊이와 너비 지정(응답 품질 상숙)
python main.py -q "크레아틴 모노하이드레이트의 효능은?" -d 3 -w 2

# 여러 질문 배치 처리 (JSON 파일 사용)
python main.py -f questions.json

# 텍스트 파일에서 질문 로드
python main.py -f questions.txt
```

### 전체 명령행 옵션

```
사용법: python main.py [-h] [-i] [-q QUESTION] [-f FILE] [-d DEPTH] [-w WIDTH] [-o OUTPUT_DIR] [-m MODEL]

옵션:
  -h, --help            도움말 표시 후 종료
  -i, --interactive     대화형 모드 실행
  -q QUESTION, --question QUESTION
                        단일 질문 처리
  -f FILE, --file FILE  질문 파일 경로 (JSON 또는 텍스트)
  -d DEPTH, --depth DEPTH
                        피드백 루프 깊이 (1-10, 기본값: 2)
  -w WIDTH, --width WIDTH
                        피드백 루프 너비 (1-10, 기본값: 2)
  -o OUTPUT_DIR, --output OUTPUT_DIR
                        결과 저장 디렉토리
  -m MODEL, --model MODEL
                        사용할 Ollama 모델
```

### 질문 파일 형식

#### JSON 형식 (questions.json)

```json
{
    "questions": [
        "근육 발달에 가장 효과적인 단백질 보충제는 무엇인가요?",
        "BCAA 보충제의 효과는 과학적으로 증명되었나요?",
        "크레아틴과 단백질을 함께 섭취하는 것이 효과적인가요?",
        "운동 전후 카페인 섭취가 근육 성장에 미치는 영향은?"
    ]
}
```

#### 텍스트 형식 (questions.txt)

```
근육 발달에 가장 효과적인 단백질 보충제는 무엇인가요?
BCAA 보충제의 효과는 과학적으로 증명되었나요?
크레아틴과 단백질을 함께 섭취하는 것이 효과적인가요?
운동 전후 카페인 섭취가 근육 성장에 미치는 영향은?
```

## 출력 내용 및 관리

### 결과 저장 구조

연구 결과는 마크다운 형식으로 다음 구조로 저장됩니다:

```
research_outputs/
├── 20250610_102523_근육발달/
│   ├── 20250610_102523_근육발달.md           # 마크다운 형식 결과
│   └── 20250610_102523_근육발달_meta.json     # 메타데이터
├── 20250610_104517_크레아틴효과/
│   ├── 20250610_104517_크레아틴효과.md
│   └── 20250610_104517_크레아틴효과_meta.json
└── ...
```

### 출력 형식 (마크다운)

결과 파일 (.md)는 일관된 마크다운 형식을 가지며, 다음과 같은 구조로 구성됩니다:

```markdown
# 제목: 질문에 대한 정확한 답변

## 1. 문제 정의

[질문과 관련된 문제 정의 및 배경 설명]

## 2. 핵심 내용

[이론, 개념, 원리와 관련된 정보]

## 3. 과학적 근거

[연구 결과, 데이터에 기반한 증거 자료]

## 4. 복용 방법 및 주의사항

[함급품/보충제 사용법 및 주의점]

## 5. 결론 및 요약

[핵심 내용 정리 및 추가 참고사항]

## 6. 참고 문헌

1. Author, A., et al. (2023). Title of study. Journal, 10(2), 45-67. https://doi.org/example
2. Author, B., et al. (2024). Another relevant study. Journal, 11(3), 123-145. https://doi.org/example2
```

### 메타데이터 파일 (JSON)

결과와 함께 저장되는 메타데이터는 다음과 같은 정보를 포함합니다:

```json
{
  "question": "근육 발달에 가장 중요한 아미노산은 무엇인가요?",
  "timestamp": "2025-06-10T10:25:23",
  "model": "Gemma3:latest",
  "feedback_depth": 2,
  "feedback_width": 2,
  "response_length": 3542,
  "quality_score": 0.91,
  "processing_time_seconds": 45.23,
  "references_count": 3,
  "debug_mode": false
}
```

## 프로젝트 구조

```
GAIA_LLMs/
├── src/
│   ├── api/              # API 통신 모듈
│   ├── research/         # 연구 관리 모듈
│   ├── feedback/         # 피드백 및 평가 모듈
│   ├── storage/          # 파일 저장 모듈
│   ├── utils/            # 유틸리티 모듈
│   └── cli.py            # 명령줄 인터페이스
├── main.py               # 메인 실행 파일
├── requirements.txt      # 의존성 정의
├── .env.example          # 환경 변수 예시
└── README.md             # 이 파일
```

## cli 사용법

## Ollama 사용법

## ollama 모델 추가 방법
ollama create txgemma-predict -f model/Modelfile-txgemma-predict
ollama create txgemma-chat -f model/Modelfile-txgemma-chat

## 테스트를 위한 질문 예시
- 일반 질문: "크레아틴은 어떤 근육 효과가 있나요?"
- 상세 질문: "근력 운동 후 단백질 섭취의 최적 타이밍과 양은 얼마인가요?"
- 복합 질문: "BCAA와 프로틴의 차이점과 언제 어떻게 섭취하는 것이 좋은지 알려주세요."
- 기능성 질문: "운동 전후 카페인 섭취가 근육 성장에 미치는 영향은 무엇인가요?"
- 안전성 질문: "단백질 보충제의 부작용과 주의사항에 대해 알려주세요."

## 라이선스

이 프로젝트는 MIT 라이선스에 따라 제공됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.

죄송합니다. 현재 모델(txgemma-predict:latest)이 적절한 응답을 생성하지 못했습니다. 다른    
모델로 변경하여 다시 시도해보세요 가 출력되는데 이부분을 해결하여 제대로된 답변을 얻을 수 있도록 수정해줘.