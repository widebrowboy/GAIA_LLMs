# GAIA-BT v2.0 Alpha 신약개발 연구 시스템

Ollama LLM과 MCP(Model Context Protocol)를 활용한 **프로덕션 레디** 신약개발 전문 AI 연구 어시스턴트 시스템입니다. CLI, WebUI, RESTful API를 모두 지원하며 포트 충돌 방지 시스템과 완전한 변경 확인 기능을 갖춘 엔터프라이즈급 솔루션입니다.

<div align="center">

**🎉 최신 버전: v2.0.2 Alpha (2025-06-19)** 
**✅ 프로덕션 레디 (Production Ready)**  
**🧬 신약개발 전문 AI 연구 어시스턴트**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.13+-green.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)](https://fastapi.tiangolo.com)

</div>

## 🎯 주요 특징

### 🧬 신약개발 전문 AI 어시스턴트
- **타겟 발굴**: 분자 타겟 식별 및 검증
- **화합물 분석**: ChEMBL 기반 분자 구조 및 물리화학적 특성 분석  
- **임상 연구**: 임상시험 데이터 및 개발 단계 분석
- **약물 상호작용**: 분자 수준 약물-타겟 상호작용 연구
- **규제 분석**: FDA, EMA 등 글로벌 승인 프로세스

### 🚀 멀티 플랫폼 지원 (v2.0.2 신규)
- **CLI 인터페이스**: Rich UI 기반 터미널 실행
- **Modern WebUI**: Next.js 15 + React 19 + TypeScript
- **RESTful API**: FastAPI 기반 완전 분리된 API 서버
- **WebSocket**: 실시간 스트리밍 지원
- **포트 충돌 방지**: 자동 프로세스 관리 시스템

### 🔬 고성능 연구 플랫폼
- **통합 MCP 서버**: DrugBank, OpenTargets, ChEMBL, PubMed, ClinicalTrials.gov, BioMCP, BioRxiv/medRxiv, Sequential Thinking, Playwright
- **스마트 Deep Search**: 질문 키워드 분석 기반 적응형 다중 데이터베이스 검색
- **실시간 분석**: 최신 논문, 임상시험, 약물-타겟 상호작용 데이터 실시간 조회
- **AI 통합 분석**: Sequential Thinking + 다중 데이터소스 조합으로 포괄적 연구 수행
- **과학적 근거**: 모든 답변에 참고문헌 및 데이터 소스 포함

## 📋 목차
- [시스템 구성](#시스템-구성)
- [빠른 시작](#빠른-시작)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [API 문서](#api-문서)
- [MCP 통합 기능](#mcp-통합-기능)
- [신약개발 활용 사례](#신약개발-활용-사례)
- [고급 설정](#고급-설정)
- [문제 해결](#문제-해결)

## 🏗️ 시스템 구성

### 📦 전체 아키텍처
```
GAIA-BT v2.0 Alpha
├── 🖥️  CLI 인터페이스 (app/cli/)
├── 🌐 Modern WebUI (webui/nextjs-webui/)
├── 🔗 RESTful API 서버 (app/api_server/)
├── 🔬 MCP 통합 시스템 (mcp/)
└── 🛠️  서버 관리 도구 (scripts/)
```

### 🎯 주요 컴포넌트
- **DrugDevelopmentChatbot**: 메인 챗봇 클래스
- **ChatbotService**: API 서버용 서비스 레이어
- **MCPManager**: MCP 서버 통합 관리
- **WebSocketManager**: 실시간 통신 관리
- **ServerManager**: 포트 충돌 방지 시스템

## 🔧 시스템 요구사항

### 필수 환경
- **운영체제**: Ubuntu 24.04 이상 또는 macOS 12+
- **파이썬**: Python 3.13+ (비동기 기능 지원)
- **Ollama**: [Ollama](https://ollama.ai/) 0.2.1 이상
- **Node.js**: 18.0+ (WebUI용)

### 권장 환경
- **GPU**: NVIDIA GPU (CUDA 12.0+) 또는 Apple Silicon
- **메모리**: 16GB 이상 권장 (32GB 최적)
- **저장공간**: 20GB 이상 (모델 파일 포함)

## 🚀 빠른 시작

### 1단계: 저장소 클론
```bash
git clone https://github.com/widebrowboy/GAIA_LLMs.git
cd GAIA_LLMs
```

### 2단계: 의존성 설치
```bash
# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Python 의존성 설치
pip install -r config/requirements.txt

# Node.js 의존성 설치 (WebUI용)
cd webui/nextjs-webui
npm install
cd ../..
```

### 3단계: Ollama 모델 설치
```bash
# 추천 모델 (고성능)
ollama pull gemma2:27b

# 또는 빠른 테스트용
ollama pull gemma2:9b
```

### 4단계: 서버 시작 (포트 충돌 방지)
```bash
# 🔥 원클릭 서버 시작 (추천)
./scripts/server_manager.sh start

# 서버 상태 확인
./scripts/server_manager.sh status
```

### 5단계: 접속 및 사용
```bash
# 🌐 WebUI 접속 (추천)
# http://localhost:3001

# 📖 API 문서 접속
# http://localhost:8000/docs

# 🖥️ CLI 실행
python run_chatbot.py
```

## 🛠️ 설치 방법

### 자동 설치 (추천)
```bash
# 전체 시스템 자동 설정
git clone https://github.com/widebrowboy/GAIA_LLMs.git
cd GAIA_LLMs
chmod +x scripts/server_manager.sh
./scripts/server_manager.sh start
```

### 수동 설치
```bash
# 1. Python 환경 설정
python -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt

# 2. Node.js 환경 설정
cd webui/nextjs-webui
npm install
npm run build
cd ../..

# 3. 환경변수 설정
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export OLLAMA_BASE_URL="http://localhost:11434"

# 4. 개별 서버 시작
python run_api_server.py &
cd webui/nextjs-webui && npm run dev &
```

## 🎮 사용 방법

### 🔥 서버 관리 (포트 충돌 방지)
```bash
# 모든 서버 시작
./scripts/server_manager.sh start

# 서버 상태 확인
./scripts/server_manager.sh status

# 서버 재시작 (문제 발생 시)
./scripts/server_manager.sh restart

# 서버 중지
./scripts/server_manager.sh stop

# 로그 확인
./scripts/server_manager.sh logs
```

### 🌐 WebUI 사용법
```bash
# 브라우저에서 접속
http://localhost:3001

# 지원되는 명령어 (WebUI에서)
/help                    # 도움말 표시
/mcp start              # Deep Research 모드 시작  
/normal                 # 일반 모드로 전환
/prompt clinical        # 임상시험 전문 모드
/model gemma2:27b       # AI 모델 변경
/debug                  # 디버그 모드 토글
```

### 🖥️ CLI 사용법
```bash
# 기본 실행
python run_chatbot.py

# 디버그 모드
python main.py --debug

# MCP 포함 실행
python main.py --enable-mcp
```

### 🔗 API 사용법
```bash
# 채팅 메시지 전송
curl -X POST "http://localhost:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "아스피린의 작용 메커니즘은?", "session_id": "default"}'

# Deep Research 모드 시작
curl -X POST "http://localhost:8000/api/mcp/start" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "default"}'

# 시스템 정보 조회
curl -X GET "http://localhost:8000/api/system/info"
```

## 📖 API 문서

### Swagger UI 접속
- **주소**: http://localhost:8000/docs
- **대안**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 주요 API 엔드포인트

#### 💬 채팅 시스템 (/api/chat)
- `POST /message`: 일반 채팅 메시지 전송
- `POST /stream`: 실시간 스트리밍 채팅
- `POST /command`: 시스템 명령어 실행

#### ⚙️ 시스템 관리 (/api/system)
- `GET /info`: 시스템 정보 조회
- `POST /model`: AI 모델 변경
- `POST /prompt`: 프롬프트 타입 변경
- `POST /debug`: 디버그 모드 토글
- `POST /mode/{mode}`: 모드 전환 (normal/deep_research)

#### 🔬 MCP 제어 (/api/mcp)
- `GET /status`: MCP 상태 조회
- `POST /start`: Deep Research 모드 시작
- `POST /stop`: MCP 서버 중지
- `POST /command`: MCP 명령어 실행
- `GET /servers`: 사용 가능한 MCP 서버 목록

#### 👥 세션 관리 (/api/session)
- `POST /create`: 새 세션 생성
- `GET /{session_id}`: 세션 정보 조회
- `DELETE /{session_id}`: 세션 삭제
- `GET /`: 모든 세션 목록

### WebSocket 연결
```javascript
// 실시간 스트리밍 연결
const ws = new WebSocket('ws://localhost:8000/ws/my_session_id');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

ws.send(JSON.stringify({
    type: 'chat',
    message: '아스피린의 부작용은?'
}));
```

## 🔬 MCP 통합 기능

### 지원되는 데이터베이스
- **DrugBank**: 약물 정보 및 상호작용
- **ChEMBL**: 화학 구조 및 생물활성 데이터
- **OpenTargets**: 타겟-질병 연관성 분석
- **PubMed**: 의학 논문 검색 (BioMCP)
- **ClinicalTrials.gov**: 임상시험 데이터
- **BioRxiv/medRxiv**: 최신 프리프린트 논문
- **Sequential Thinking**: AI 기반 단계별 추론
- **Playwright**: 웹 자동화 및 데이터 수집

### Deep Search 사용법
```bash
# CLI에서
/mcp start
질문: "EGFR 억제제의 최신 연구 동향을 분석해주세요"

# API에서
curl -X POST "http://localhost:8000/api/mcp/start" \
  -d '{"session_id": "my_session"}'

curl -X POST "http://localhost:8000/api/chat/message" \
  -d '{"message": "EGFR 억제제의 최신 연구 동향을 분석해주세요", "session_id": "my_session"}'
```

## 🧬 신약개발 활용 사례

### 1. 타겟 발굴 및 검증
```
질문: "알츠하이머병의 새로운 치료 타겟을 분석해주세요"

Deep Research 결과:
- OpenTargets: 타겟-질병 연관성 분석
- PubMed: 최신 연구 동향
- ClinicalTrials.gov: 현재 진행 중인 임상시험
- Sequential Thinking: 통합 분석 및 추천
```

### 2. 화합물 분석
```
질문: "아스피린의 분자 구조와 약물동태학적 특성을 분석해주세요"

Deep Search 결과:
- ChEMBL: 화학 구조 및 물리화학적 특성
- DrugBank: 약물동태학 및 상호작용
- PubMed: 관련 연구 논문
- 구조화된 분석 보고서 생성
```

### 3. 임상시험 분석
```
질문: "COVID-19 치료제의 임상시험 현황을 분석해주세요"

Deep Research 결과:
- ClinicalTrials.gov: 진행 중인 임상시험 목록
- PubMed: 임상 결과 논문
- BioRxiv: 최신 프리프린트 연구
- 임상시험 단계별 통계 분석
```

## ⚙️ 고급 설정

### 프롬프트 모드 설정
```bash
# 사용 가능한 프롬프트 모드
/prompt clinical      # 임상시험 전문 모드
/prompt research      # 연구 분석 전문 모드  
/prompt chemistry     # 의약화학 전문 모드
/prompt regulatory    # 규제 전문 모드
/prompt default       # 기본 모드

# 🆕 WebUI 전용 기능 (v2.0.2)
# 사이드바 모드 버튼을 통한 원클릭 모드 전환
- 일반 모드 ↔ Deep Research 모드 토글 버튼
- 실시간 모드 상태 표시 (색상 코드)
- 프롬프트 타입 변경 (clinical/research/chemistry/regulatory)
- 모델 선택 및 변경 인터페이스
- 시스템 상태 모니터링 (API 연결, MCP 서버 상태)
```

### MCP 출력 제어
```bash
# MCP 검색 과정 표시/숨김
/mcpshow             # 토글 명령어

# 설정 파일에서 (app/utils/config.py)
show_mcp_output = True  # 검색 과정 표시
show_mcp_output = False # 최종 결과만 표시 (기본값)
```

### 환경변수 설정
```bash
# 필수 환경변수
export PYTHONPATH="/path/to/GAIA_LLMs"
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="gemma2:27b"

# 선택적 환경변수
export DEBUG_MODE="true"
export OUTPUT_DIR="./outputs/research"
export MCP_ENABLED="true"
```

## 🛠️ 문제 해결

### 포트 충돌 문제
```bash
# 🔥 최우선 해결 방법
./scripts/server_manager.sh restart
./scripts/server_manager.sh clean-ports

# 특정 포트 정리
./scripts/server_manager.sh kill-port 3001  # WebUI
./scripts/server_manager.sh kill-port 8000  # API
```

### 서버 접속 문제
```bash
# 서버 상태 확인
./scripts/server_manager.sh status

# 로그 확인
./scripts/server_manager.sh logs

# 브라우저 접속 테스트
curl -s http://localhost:3001 | head -n 5
curl -s http://localhost:8000/health
```

### Ollama 연결 문제
```bash
# Ollama 서비스 확인
curl http://localhost:11434/api/tags

# Ollama 재시작
ollama serve
```

### Python 모듈 import 오류
```bash
# 환경변수 설정
export PYTHONPATH="${PYTHONPATH}:/path/to/GAIA_LLMs"

# 가상환경 활성화 확인
source venv/bin/activate
which python
```

## 📂 프로젝트 구조

```
GAIA_LLMs/
├── 📁 app/                          # 메인 애플리케이션
│   ├── 📁 cli/                      # CLI 인터페이스
│   ├── 📁 api/                      # Ollama API 클라이언트
│   ├── 📁 api_server/               # FastAPI 서버 (신규)
│   ├── 📁 core/                     # 핵심 비즈니스 로직
│   └── 📁 utils/                    # 유틸리티
├── 📁 webui/                        # WebUI 시스템 (신규)
│   ├── 📁 nextjs-webui/             # Next.js Frontend
│   ├── 📁 backend/                  # FastAPI Backend
│   └── run_webui.sh                 # WebUI 실행 스크립트
├── 📁 mcp/                          # MCP 통합 시스템
├── 📁 scripts/                      # 실행 스크립트
│   └── server_manager.sh            # 서버 관리 도구 (신규)
├── 📁 prompts/                      # 프롬프트 템플릿
├── 📁 config/                       # 설정 파일
├── run_chatbot.py                   # CLI 실행 파일
├── run_api_server.py                # API 서버 실행 파일 (신규)
└── README.md                        # 이 문서
```

## 🔗 관련 링크

- **GitHub Repository**: https://github.com/widebrowboy/GAIA_LLMs
- **Ollama**: https://ollama.ai/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/
- **MCP Specification**: https://modelcontextprotocol.io/

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제가 발생하거나 질문이 있으시면:
- GitHub Issues를 통해 문의
- 문서의 [문제 해결](#문제-해결) 섹션 참조
- `./scripts/server_manager.sh --help` 명령어로 도움말 확인

---

<div align="center">

**🧬 GAIA-BT v2.0 Alpha - 신약개발 연구의 새로운 패러다임**

*Built with ❤️ for Drug Discovery Research*

</div>