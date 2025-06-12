# GAIA-BT 신약개발 연구 시스템 - 프로젝트 구축 가이드

## 📋 프로젝트 개요
GAIA-BT는 Ollama LLM과 MCP(Model Context Protocol)를 활용한 신약개발 전문 AI 연구 어시스턴트 시스템입니다.

## 🏗️ 최종 프로젝트 구조

```
GAIA_LLMs/
├── 📁 app/                      # 메인 애플리케이션
│   ├── __init__.py
│   ├── 📁 core/                 # 핵심 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── answer_evaluator.py  # 답변 품질 평가
│   │   ├── answer_generator.py  # AI 답변 생성
│   │   ├── biomcp_integration.py # BiomCP 통합
│   │   ├── file_storage.py      # 파일 저장 관리
│   │   ├── question_handler.py  # 질문 처리
│   │   ├── research_manager.py  # 연구 관리
│   │   └── research_parallel.py # 병렬 처리
│   ├── 📁 cli/                  # CLI 인터페이스
│   │   ├── __init__.py
│   │   ├── chatbot.py           # 메인 챗봇 클래스
│   │   ├── interface.py         # Rich UI 인터페이스
│   │   └── mcp_commands.py      # MCP 명령어 처리
│   ├── 📁 api/                  # API 클라이언트
│   │   ├── __init__.py
│   │   ├── ollama_client.py     # Ollama API 클라이언트
│   │   └── model_adapters.py    # 모델 어댑터
│   └── 📁 utils/                # 유틸리티
│       ├── __init__.py
│       ├── config.py            # 설정 관리
│       ├── config_manager.py    # 설정 파일 관리
│       └── text_utils.py        # 텍스트 처리
├── 📁 docs/                     # 문서
│   ├── 📁 guides/               # 사용자 가이드
│   │   ├── QUICK_START_GUIDE.md
│   │   └── START_CHATBOT.md
│   └── 📁 manuals/              # 상세 매뉴얼
│       ├── DEEP_RESEARCH_USER_MANUAL.md
│       └── USAGE_GUIDE_KO.md
├── 📁 config/                   # 설정 파일
│   ├── requirements.txt         # Python 의존성
│   ├── mcp.json                # MCP 서버 설정
│   ├── ruff.toml              # 코드 포맷터 설정
│   ├── docker-compose.mcp.yml  # MCP Docker 설정
│   └── docker-compose.biomcp.yml
├── 📁 mcp/                      # MCP 통합
│   ├── 📁 server/               # MCP 서버
│   │   ├── __init__.py
│   │   ├── mcp_server.py
│   │   └── handlers/
│   │       └── gaia_tools.py
│   ├── 📁 client/               # MCP 클라이언트
│   │   ├── __init__.py
│   │   └── mcp_client.py
│   ├── 📁 integration/          # MCP 통합
│   │   ├── __init__.py
│   │   ├── mcp_manager.py
│   │   └── gaia_mcp_server.py
│   ├── 📁 protocol/             # MCP 프로토콜
│   │   ├── __init__.py
│   │   └── messages.py
│   ├── 📁 transport/            # 전송 계층
│   │   ├── __init__.py
│   │   ├── stdio_transport.py
│   │   └── websocket_transport.py
│   ├── 📁 drugbank/             # DrugBank MCP 서버 (신규)
│   │   ├── __init__.py
│   │   └── drugbank_mcp.py      # 약물 데이터베이스 서버
│   ├── 📁 opentargets/          # OpenTargets MCP 서버 (신규)
│   │   ├── __init__.py
│   │   └── opentargets_mcp.py   # 타겟-질병 연관성 서버
│   ├── 📁 biomcp/               # BiomCP 서버 (서브모듈)
│   ├── 📁 chembl/               # ChEMBL 서버 (서브모듈)
│   ├── 📁 sequential-thinking/  # 추론 서버
│   └── run_server.py           # MCP 서버 실행
├── 📁 scripts/                  # 실행 스크립트
│   ├── run_mcp_servers.sh      # MCP 서버 시작
│   ├── stop_mcp_servers.sh     # MCP 서버 중지
│   ├── status_mcp_servers.sh   # MCP 상태 확인
│   └── build-mcp.sh            # MCP 빌드
├── 📁 outputs/                  # 출력 디렉토리
│   └── 📁 research/             # 연구 결과
│       └── .gitkeep
├── 📁 examples/                 # 예제
│   ├── example_usage.py
│   ├── demo_hnscc_research.py
│   ├── demo_integrated_mcp.py
│   └── quick_demo.py
├── 📁 tests/                    # 테스트
│   └── 📁 integration/
│       ├── test_hnscc_research.py
│       ├── test_integrated_mcp.py
│       └── test_mcp_hnscc.py
├── 📁 model/                    # AI 모델 (Git 제외)
│   ├── Modelfile-txgemma-chat
│   └── Modelfile-txgemma-predict
├── run_chatbot.py              # 메인 실행 파일
├── main.py                     # 고급 실행 파일
├── README.md                   # 프로젝트 문서
├── EXECUTION_GUIDE.md          # 실행 가이드
├── .gitignore                  # Git 제외 설정
└── task.md                     # 작업 목록

```

## 📝 개발 작업 순서

### 1단계: 프로젝트 기본 구조 설정
☐ 프로젝트 디렉토리 생성
☐ Python 가상환경 설정
☐ 기본 의존성 설치 (requirements.txt)
☐ .gitignore 파일 설정

### 2단계: 핵심 애플리케이션 구조 구축
☐ app/ 디렉토리 구조 생성
  ☐ app/__init__.py 작성
  ☐ app/core/ 디렉토리 생성
  ☐ app/cli/ 디렉토리 생성
  ☐ app/api/ 디렉토리 생성
  ☐ app/utils/ 디렉토리 생성

### 3단계: 설정 시스템 구현
☐ app/utils/config.py 구현
  ☐ Ollama 설정 (BASE_URL, MODEL)
  ☐ 출력 디렉토리 설정
  ☐ 피드백 설정 (DEPTH, WIDTH)
  ☐ 품질 기준 설정 (MIN_RESPONSE_LENGTH, MIN_REFERENCES)
☐ app/utils/config_manager.py 구현
☐ app/utils/text_utils.py 구현

### 4단계: API 클라이언트 구현
☐ app/api/ollama_client.py 구현
  ☐ OllamaClient 클래스
  ☐ 비동기 API 호출
  ☐ 모델 관리 기능
  ☐ 디버그 모드 지원
☐ app/api/model_adapters.py 구현
  ☐ 모델별 어댑터 패턴
  ☐ 프롬프트 최적화

### 5단계: 핵심 비즈니스 로직 구현
☐ app/core/file_storage.py 구현
  ☐ 연구 결과 저장
  ☐ 메타데이터 관리
☐ app/core/answer_generator.py 구현
  ☐ AI 답변 생성 로직
  ☐ 구조화된 답변 포맷
☐ app/core/answer_evaluator.py 구현
  ☐ 답변 품질 평가
  ☐ 피드백 생성
☐ app/core/question_handler.py 구현
  ☐ 질문 전처리
  ☐ 컨텍스트 생성
☐ app/core/research_manager.py 구현
  ☐ 전체 연구 프로세스 관리
  ☐ 피드백 루프 구현
☐ app/core/research_parallel.py 구현
  ☐ 병렬 처리 최적화

### 6단계: CLI 인터페이스 구현
☐ app/cli/interface.py 구현
  ☐ Rich 라이브러리 활용
  ☐ GAIA-BT 배너
  ☐ 진행 상황 표시
☐ app/cli/chatbot.py 구현
  ☐ DrugDevelopmentChatbot 클래스
  ☐ 대화형 루프
  ☐ 명령어 처리
  ☐ 설정 관리

### 7단계: MCP 통합 시스템 구축
☐ mcp/ 폴더 구조 생성
☐ MCP 프로토콜 구현
  ☐ mcp/protocol/messages.py
☐ MCP 전송 계층 구현
  ☐ mcp/transport/stdio_transport.py
  ☐ mcp/transport/websocket_transport.py
☐ MCP 서버 구현
  ☐ mcp/server/mcp_server.py
  ☐ mcp/server/handlers/gaia_tools.py
☐ MCP 클라이언트 구현
  ☐ mcp/client/mcp_client.py
☐ MCP 통합 관리자 구현
  ☐ mcp/integration/mcp_manager.py
  ☐ mcp/integration/gaia_mcp_server.py

### 8단계: MCP 명령어 시스템 구현
☐ app/cli/mcp_commands.py 구현
  ☐ MCP 서버 시작/중지
  ☐ 상태 확인
  ☐ 개별 툴 호출
  ☐ Deep Search 기능
☐ app/core/biomcp_integration.py 구현
  ☐ BiomCP 서버 통합
  ☐ 데이터 변환 및 포맷팅

### 9단계: 외부 MCP 서버 통합
☐ BiomCP 서버 통합
  ☐ 논문 검색 (PubMed/PubTator3)
  ☐ 임상시험 데이터 (ClinicalTrials.gov)
  ☐ 유전체 변이 (CIViC, ClinVar, COSMIC, dbSNP)
☐ ChEMBL 서버 통합
  ☐ 화학 구조 분석
  ☐ 약물-타겟 상호작용
☐ Sequential Thinking 서버 통합
  ☐ 단계별 추론
  ☐ 문제 분해

### 10단계: 실행 파일 및 스크립트 작성
☐ run_chatbot.py 작성
  ☐ 간단한 실행 인터페이스
  ☐ 에러 처리
☐ main.py 작성
  ☐ 고급 옵션 지원
  ☐ 배치 처리 기능
☐ 실행 스크립트 작성
  ☐ scripts/run_mcp_servers.sh
  ☐ scripts/stop_mcp_servers.sh
  ☐ scripts/status_mcp_servers.sh

### 11단계: 문서화
☐ README.md 작성
  ☐ 프로젝트 소개
  ☐ 설치 방법
  ☐ 사용 방법
☐ docs/guides/QUICK_START_GUIDE.md 작성
☐ docs/guides/START_CHATBOT.md 작성
☐ docs/manuals/DEEP_RESEARCH_USER_MANUAL.md 작성
☐ EXECUTION_GUIDE.md 작성

### 12단계: 설정 파일 생성
☐ config/requirements.txt 생성
☐ config/mcp.json 생성
☐ config/ruff.toml 생성
☐ config/docker-compose.*.yml 생성
☐ .gitignore 최적화

### 13단계: 예제 및 테스트
☐ examples/ 디렉토리 예제 작성
  ☐ example_usage.py
  ☐ demo_hnscc_research.py
  ☐ demo_integrated_mcp.py
☐ tests/integration/ 테스트 작성
  ☐ test_hnscc_research.py
  ☐ test_integrated_mcp.py

### 14단계: 최종 통합 및 최적화
☐ 모든 import 경로 확인 (app.* 구조)
☐ 클래스명 통일 (DrugDevelopmentChatbot)
☐ 시스템 프롬프트 신약개발 전문화
☐ 에러 처리 및 로깅 개선
☐ 성능 최적화

### 15단계: 배포 준비
☐ 대용량 파일 제외 확인
☐ 민감한 정보 제거
☐ GitHub 리포지토리 정리
☐ 최종 테스트 및 검증

## 🔧 주요 구현 세부사항

### 핵심 클래스 및 모듈
- `DrugDevelopmentChatbot`: 메인 챗봇 클래스
- `OllamaClient`: LLM API 클라이언트
- `MCPManager`: MCP 서버 통합 관리
- `ResearchManager`: 연구 프로세스 관리
- `CliInterface`: Rich UI 인터페이스

### 주요 기능
- 신약개발 전문 AI 답변
- MCP 통합 (ChEMBL, PubMed, ClinicalTrials.gov)
- Deep Search 기능
- 피드백 루프를 통한 답변 개선
- 구조화된 연구 보고서 생성
- 다중 LLM 모델 지원

### 설정 항목
- Ollama 연결 설정
- 출력 디렉토리 설정
- 품질 기준 설정
- 피드백 루프 설정
- MCP 서버 설정

## 📌 중요 참고사항

1. **Python 버전**: 3.13+ 필수
2. **필수 의존성**: ollama, rich, aiohttp, pydantic
3. **MCP 서버**: 선택적 기능 (없어도 기본 동작)
4. **모델 파일**: Git에서 제외 (대용량)
5. **보안**: API 키 및 민감정보 .gitignore에 포함

이 가이드를 따라 전체 프로젝트를 처음부터 재구축할 수 있습니다.