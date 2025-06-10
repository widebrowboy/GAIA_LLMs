# 근육 관련 건강기능식품 연구 시스템 CLI 명령어 요약

이 문서는 근육 관련 건강기능식품 연구 시스템의 CLI 도구 명령어를 요약합니다.

## 통합 CLI 도구 (cli_tool.py)

### 기본 명령어

```bash
# 사용 가능한 모듈 목록 표시
./cli/cli_tool.py --show-modules

# 버전 확인
./cli/cli_tool.py --version
```

### API 모듈

```bash
# API 가용성 및 모델 목록 확인
./cli/cli_tool.py api check

# 텍스트 생성 (프롬프트 직접 입력)
./cli/cli_tool.py api generate --prompt "질문 내용" --model Gemma3:latest

# 텍스트 생성 (프롬프트 파일 사용)
./cli/cli_tool.py api generate --prompt-file prompt.txt --temperature 0.8
```

### 답변 생성기 모듈

```bash
# 구조화된 답변 생성 (단순 형식)
./cli/cli_tool.py generate "질문 내용"

# 구조화된 답변 생성 (상세 옵션)
./cli/cli_tool.py generate "질문 내용" --model Gemma3:latest --temperature 0.7 --output answer.md

# 대체 답변 여러 개 생성
./cli/cli_tool.py generate "질문 내용" --alternatives 3 --model Gemma3:latest
```

### 답변 평가기 모듈

```bash
# 답변 평가 (직접 입력)
./cli/cli_tool.py evaluate "질문 내용" --answer "답변 내용" --show-result

# 답변 평가 (파일 입력)
./cli/cli_tool.py evaluate "질문 내용" --file answer.md --output evaluation.json

# 피드백 루프 실행
./cli/cli_tool.py evaluate "질문 내용" --file answer.md --feedback --depth 3 --width 2
```

### 연구 관리자 모듈

```bash
# 단일 질문 연구
./cli/cli_tool.py research --question "질문 내용" --model Gemma3:latest --show-result

# 여러 질문 연구
./cli/cli_tool.py research --questions "질문1" "질문2" --depth 2 --width 2

# JSON 파일에서 질문 로드
./cli/cli_tool.py research --file questions.json --concurrent 3 --output-dir ./results
```

## 모듈별 직접 사용

### Ollama 클라이언트 (ollama_client_cli.py)

```bash
# API 가용성 확인
./cli/ollama_client_cli.py check

# 텍스트 생성
./cli/ollama_client_cli.py generate --prompt "질문 내용" --temperature 0.7

# 병렬 텍스트 생성
./cli/ollama_client_cli.py generate --prompt "질문 내용" --parallel 3 --concurrent 2
```

### 답변 생성기 (answer_generator_cli.py)

```bash
# 기본 사용법
./cli/answer_generator_cli.py "질문 내용"

# 상세 옵션
./cli/answer_generator_cli.py "질문 내용" --model Gemma3:latest --temperature 0.7 --output result.md
```

### 답변 평가기 (answer_evaluator_cli.py)

```bash
# 직접 입력한 답변 평가
./cli/answer_evaluator_cli.py "질문 내용" --answer "답변 내용"

# 파일 답변 평가
./cli/answer_evaluator_cli.py "질문 내용" --file answer.md --show-result
```

### 연구 관리자 (research_manager_cli.py)

```bash
# 단일 질문 연구
./cli/research_manager_cli.py --question "질문 내용" --model Gemma3:latest

# 파일에서 여러 질문 일괄 처리
./cli/research_manager_cli.py --file questions.json --concurrent 2 --depth 2 --width 2
```

## 테스트 결과 요약

- **API 기능**: Ollama API 연결 성공, Gemma3:latest 모델 확인 완료
- **답변 생성**: 정상적으로 구조화된 답변 생성 확인 (평균 응답 시간: 10-15초)
- **피드백 루프**: 일부 모델에서 동작 확인. `FileStorage` 객체의 `get_session_directory` 참조 문제 수정 완료
- **병렬 처리**: 동시에 여러 질문 처리 기능 확인
- **GPU 가속**: GPU 파라미터 적용 확인 (num_gpu: 99, num_thread: 8)

## 주요 설정 및 옵션

| 옵션 | 설명 | 기본값 |
|------|------|-------|
| `--model`, `-m` | 사용할 Ollama 모델 | gemma3:4b |
| `--temperature`, `-t` | 생성 온도 (0.1~1.0) | 0.7 |
| `--depth`, `-d` | 피드백 루프 깊이 | 2 |
| `--width`, `-w` | 피드백 루프 너비 | 2 |
| `--concurrent`, `-c` | 동시 처리 최대 수 | 2 |
| `--output`, `-o` | 결과 저장 파일 경로 | - |
| `--output-dir` | 결과 저장 디렉토리 | ./research_outputs |
| `--show-result`, `-s` | 결과 상세 표시 | False |

## 환경 변수

- `OLLAMA_BASE_URL`: Ollama API URL (기본값: http://localhost:11434)
- `OLLAMA_MODEL`: 기본 모델 (예: gemma3:4b, Gemma3:latest)
- `OUTPUT_DIR`: 기본 결과 저장 디렉토리