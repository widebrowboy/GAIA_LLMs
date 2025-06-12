# GAIA-BT 실행 가이드

## 🚀 빠른 시작

### 1. 기본 준비사항 확인
```bash
# Python 버전 확인 (3.13+ 권장)
python --version

# 필요한 패키지 설치
pip install -r config/requirements.txt

# Ollama 설치 및 모델 다운로드
ollama pull gemma3:latest
```

### 2. 챗봇 실행
```bash
# 메인 챗봇 실행 (권장)
python run_chatbot.py

# 또는 고급 모드
python main.py --debug
```

### 3. 시작 테스트
```bash
# 실행 전 시스템 테스트
python test_chatbot_startup.py
```

## 🔧 문제 해결

### Import 오류
```bash
# Python path 확인
python -c "import sys; print(sys.path)"

# 프로젝트 루트에서 실행하는지 확인
pwd
# /home/gaia-bt/workspace/GAIA_LLMs 이어야 함
```

### Ollama 연결 오류
```bash
# Ollama 서버 시작
ollama serve

# 연결 테스트
curl http://localhost:11434/api/version
```

### MCP 관련 오류
- MCP 기능은 선택사항입니다
- MCP 없이도 기본 챗봇 기능은 정상 작동합니다
- MCP 활성화: `/mcp start` 명령어 사용

## 📋 주요 명령어

### 기본 명령어
- `/help` - 도움말
- `/exit` - 종료
- `/model <이름>` - 모델 변경
- `/debug` - 디버그 모드 토글

### MCP 명령어 (MCP 활성화 후)
- `/mcp start` - MCP 서버 시작
- `/mcp status` - 상태 확인
- `/mcp test deep` - Deep Search 테스트

## 🎯 예제 질문

```
신약개발에서 분자 타겟 발굴의 주요 접근법은 무엇인가요?
항암제 개발에서 바이오마커의 역할과 중요성은 무엇인가요?
전임상 독성시험의 주요 단계와 평가 항목은 무엇인가요?
```

## 📁 프로젝트 구조

```
GAIA_LLMs/
├── app/                   # 메인 애플리케이션
├── docs/                  # 문서
├── config/               # 설정 파일
├── outputs/              # 결과 출력
├── examples/             # 예제
├── tests/                # 테스트
├── run_chatbot.py       # 메인 실행
└── main.py              # 고급 실행
```

## ✅ 성공적인 실행 확인

실행이 성공하면 다음과 같은 출력을 볼 수 있습니다:

```
✅ Ollama API 연결 성공
✅ AI 모델 준비 완료

💬 질문을 입력하거나 명령어를 사용하세요:

> 
```

이제 신약개발 관련 질문을 입력하고 AI의 전문적인 답변을 받을 수 있습니다!