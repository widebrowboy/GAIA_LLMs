# 근육 관련 건강기능식품 연구 시스템 CLI 사용 가이드

본 문서는 근육 관련 건강기능식품 연구 시스템의 CLI(명령줄 인터페이스) 도구 사용 방법을 설명합니다. 이 시스템은 GPU 가속화 및 병렬 처리를 활용하여 연구 질문에 대한 깊이 있는 답변을 생성합니다.

## 목차

1. [시스템 구조](#시스템-구조)
2. [통합 CLI 도구](#통합-cli-도구)
3. [모듈별 CLI 도구](#모듈별-cli-도구)
   - [Ollama 클라이언트](#ollama-클라이언트)
   - [답변 생성기](#답변-생성기)
   - [답변 평가기](#답변-평가기)
   - [연구 관리자](#연구-관리자)
4. [사용 예시](#사용-예시)
5. [오류 해결](#오류-해결)
6. [환경 설정](#환경-설정)

## 시스템 구조

이 CLI 시스템은 다음과 같은 모듈로 구성되어 있습니다:

- **Ollama 클라이언트**: Ollama API와 직접 상호작용하여 텍스트 생성
- **답변 생성기**: 구조화된 답변 생성
- **답변 평가기**: 답변 품질 평가 및 피드백 루프
- **연구 관리자**: 질문 일괄 처리 및 연구 과정 관리

각 모듈은 독립적으로 실행할 수 있으며, 통합 CLI 도구를 통해 편리하게 접근할 수도 있습니다.

## 통합 CLI 도구

통합 CLI 도구(`cli_tool.py`)는 모든 기능에 대한 단일 진입점을 제공합니다.

### 기본 사용법

```bash
./cli/cli_tool.py <모듈> [명령어] [인자...]
```

### 모듈 목록 확인

```bash
./cli/cli_tool.py --show-modules
```

### 사용 가능한 모듈

- `api`: Ollama API 클라이언트 (텍스트 생성, API 확인)
- `generate`: 답변 생성기 (구조화된 답변 생성)
- `evaluate`: 답변 평가기 (답변 평가 및 개선)
- `research`: 연구 관리자 (단일 또는 배치 연구 수행)

## 모듈별 CLI 도구

각 모듈은 독립적으로 실행할 수 있는 CLI 도구를 제공합니다.

### Ollama 클라이언트

Ollama API와 직접 상호작용하여 텍스트를 생성하거나 API 가용성을 확인합니다.

#### API 가용성 확인

```bash
./cli/ollama_client_cli.py check [--model MODEL]
```

#### 텍스트 생성

```bash
./cli/ollama_client_cli.py generate --prompt "프롬프트" [옵션...]
./cli/ollama_client_cli.py generate --prompt-file file.txt [옵션...]
```

#### 주요 옵션

- `--model`, `-m`: 사용할 모델 (기본값: gemma3:4b)
- `--temperature`, `-t`: 생성 온도 (0.1~1.0)
- `--system`, `-s`: 시스템 프롬프트
- `--parallel`, `-pr`: 병렬 생성 수
- `--output`, `-o`: 출력 파일 경로

### 답변 생성기

연구 질문에 대한 구조화된 답변을 생성합니다.

#### 기본 사용법

```bash
./cli/answer_generator_cli.py "질문" [옵션...]
```

#### 주요 옵션

- `--model`, `-m`: 사용할 모델 (기본값: gemma3:4b)
- `--temperature`, `-t`: 생성 온도 (0.1~1.0)
- `--alternatives`, `-a`: 생성할 대체 답변 수
- `--output`, `-o`: 결과 저장 파일 경로
- `--max-length`, `-l`: 출력할 최대 문자 수

### 답변 평가기

생성된 답변의 품질을 평가하고 피드백을 통한 개선을 수행합니다.

#### 기본 사용법

```bash
./cli/answer_evaluator_cli.py "질문" --answer "답변" [옵션...]
./cli/answer_evaluator_cli.py "질문" --file answer.md [옵션...]
```

#### 피드백 루프 실행

```bash
./cli/answer_evaluator_cli.py "질문" --file answer.md --feedback --depth 3 --width 2
```

#### 주요 옵션

- `--answer`, `-a`: 평가할 답변 (직접 입력)
- `--file`, `-f`: 답변이 포함된 파일
- `--model`, `-m`: 사용할 모델
- `--feedback`, `-fb`: 피드백 루프 실행
- `--depth`, `-d`: 피드백 루프 깊이 (기본값: 2)
- `--width`, `-w`: 피드백 루프 너비 (기본값: 2)
- `--output`, `-o`: 결과 저장 파일 경로
- `--show-result`, `-s`: 결과 표시

### 연구 관리자

질문에 대한 연구를 수행하고 결과를 저장합니다. 단일 질문 또는 여러 질문을 일괄 처리할 수 있습니다.

#### 단일 질문 연구

```bash
./cli/research_manager_cli.py --question "질문" [옵션...]
```

#### 여러 질문 연구

```bash
./cli/research_manager_cli.py --questions "질문1" "질문2" [옵션...]
./cli/research_manager_cli.py --file questions.json [옵션...]
```

#### 주요 옵션

- `--model`, `-m`: 사용할 모델
- `--depth`, `-d`: 피드백 루프 깊이 (기본값: 2)
- `--width`, `-w`: 피드백 루프 너비 (기본값: 2)
- `--concurrent`, `-c`: 동시 처리 질문 수 (기본값: 2)
- `--output-dir`, `-o`: 결과 저장 디렉토리
- `--batch`, `-b`: 단일 질문도 배치 모드로 처리
- `--show-result`, `-s`: 결과 요약 표시
- `--save-json`, `-j`: 결과를 JSON으로 저장

## 사용 예시

### 기본 연구 수행

```bash
# 단일 질문 연구
./cli/cli_tool.py research --question "크레아틴은 근육 성장에 어떤 영향을 미치나요?" --model Gemma3:latest

# 여러 질문 일괄 연구
./cli/cli_tool.py research --file test_questions.json --concurrent 2 --depth 2 --width 2
```

### 답변 생성 및 평가

```bash
# 단일 질문에 대한 답변 생성
./cli/cli_tool.py generate "근육 회복을 위한 최적의 단백질 섭취 타이밍은?" --model Gemma3:latest --output answer.md

# 생성된 답변 평가
./cli/cli_tool.py evaluate "근육 회복을 위한 최적의 단백질 섭취 타이밍은?" --file answer.md --show-result

# 피드백 루프를 통한 답변 개선
./cli/cli_tool.py evaluate "근육 회복을 위한 최적의 단백질 섭취 타이밍은?" --file answer.md --feedback --depth 3
```

### Ollama API 직접 사용

```bash
# API 가용성 확인
./cli/cli_tool.py api check

# 텍스트 생성
./cli/cli_tool.py api generate --prompt "크레아틴의 효과 요약" --temperature 0.8
```

## 오류 해결

자주 발생하는 오류와 해결 방법:

1. **모델을 찾을 수 없음**: `./cli/ollama_client_cli.py check`를 실행하여 사용 가능한 모델 확인 후 `--model` 옵션으로 정확한 모델명 지정

2. **Ollama API 연결 실패**: Ollama 서비스가 실행 중인지 확인. `ollama serve` 명령어로 서비스 시작

3. **메모리 부족 오류**: `--concurrent` 값을 낮추어 동시 처리 수 줄이기

## 환경 설정

### 환경 변수

다음과 같은 환경 변수를 설정하여 기본 동작을 변경할 수 있습니다:

- `OLLAMA_BASE_URL`: Ollama API URL (기본값: http://localhost:11434)
- `OLLAMA_MODEL`: 기본 모델
- `OUTPUT_DIR`: 결과 저장 디렉토리

### GPU 가속화 설정

GPU 가속화는 기본적으로 활성화되어 있으며, 다음과 같은 매개변수를 사용합니다:

- `num_gpu`: 99 (가능한 모든 GPU 활용)
- `num_thread`: 8 (병렬 스레드)
- `f16_kv`: true (메모리 효율성)
- `mirostat`: 2 (고급 샘플링)

이 설정은 `src/api/ollama_client.py`에서 변경할 수 있습니다.
