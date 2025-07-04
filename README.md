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
- **완전 구성된 MCP 서버 (v3.34)**: 
  - **BioMCP**: 통합 생명과학 연구 도구 (PubMed, ClinicalTrials, MyVariant)
  - **OpenTargets**: 타겟 검증 및 질환-타겟 연관성 분석
  - **DrugBank**: 약물 정보 데이터베이스 및 상호작용 분석
  - **ChEMBL**: 화학 생물활성 데이터베이스
  - **PubMed**: 생명과학 문헌 검색
  - **ClinicalTrials**: 임상시험 레지스트리
- **Claude Code 호환성**: MCP 구성 파일 자동 생성 (claude_code_config.json)
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

### 🌐 WebUI 사용 가이드

#### 1. WebUI 접속
```bash
# 서버 시작 (자동으로 모든 필요 서비스 시작)
./scripts/server_manager.sh start

# 브라우저에서 접속
http://localhost:3001
```

#### 2. WebUI 주요 기능
- **채팅 인터페이스**: 실시간 스트리밍으로 응답 표시
- **모드 전환**: 사이드바에서 일반 모드 ↔ Deep Research 모드 원클릭 전환
- **프롬프트 선택**: clinical, research, chemistry, regulatory 중 선택
- **모델 변경**: gemma2:9b, gemma2:27b 등 모델 선택
- **대화 기록**: 사이드바에서 이전 대화 기록 확인 및 관리

#### 3. WebUI에서 사용 가능한 명령어
```
/help                    # 도움말 표시
/mcp start              # Deep Research 모드 시작  
/normal                 # 일반 모드로 전환
/prompt clinical        # 임상시험 전문 모드
/model gemma2:27b       # AI 모델 변경
/debug                  # 디버그 모드 토글
/mcpshow                # MCP 검색 과정 표시 토글
```

#### 4. Deep Research 모드 사용법
1. 사이드바의 "Deep Research" 버튼 클릭 또는 `/mcp start` 명령어 입력
2. 연구 관련 질문 입력 (예: "EGFR 억제제의 최신 연구 동향")
3. MCP 서버가 자동으로 다음 데이터베이스 검색:
   - PubMed: 최신 논문
   - ClinicalTrials: 진행 중인 임상시험
   - DrugBank: 약물 정보
   - ChEMBL: 화학 구조 및 생물활성
   - OpenTargets: 타겟-질병 연관성

### 🖥️ CLI 사용 가이드

#### 1. CLI 시작
```bash
# 가상환경 활성화
source venv/bin/activate

# CLI 챗봇 실행
python run_chatbot.py
```

#### 2. CLI 명령어
```
/help                    # 도움말 표시
/mcp start              # Deep Research 모드 시작
/normal                 # 일반 모드로 전환
/prompt [type]          # 프롬프트 타입 변경
/model [name]           # AI 모델 변경
/mcpshow                # MCP 출력 표시 토글
/debug                  # 디버그 모드 토글
/exit                   # 프로그램 종료
```

#### 3. CLI 고급 옵션
```bash
# 디버그 모드로 실행
python main.py --debug

# MCP 활성화하여 실행
python main.py --enable-mcp

# 특정 모델로 실행
python main.py --model gemma2:27b
```

#### 4. CLI Deep Research 예제
```bash
# CLI 시작
python run_chatbot.py

# Deep Research 모드 시작
> /mcp start

# 연구 질문 입력
> 알츠하이머병의 최신 치료 타겟과 임상시험 현황을 분석해주세요

# 결과는 다음 형식으로 제공:
# 1. PubMed 최신 논문 요약
# 2. ClinicalTrials 진행 중인 시험
# 3. DrugBank 관련 약물 정보
# 4. 통합 분석 및 권장사항
```

### 🔗 API 사용 가이드

#### 1. API 서버 접속
```bash
# API 문서 (Swagger UI)
http://localhost:8000/docs

# 대안 문서 (ReDoc)
http://localhost:8000/redoc
```

#### 2. 주요 API 엔드포인트
```bash
# 채팅 메시지 전송
curl -X POST "http://localhost:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "아스피린의 작용 메커니즘은?", "session_id": "default"}'

# 스트리밍 채팅 (Server-Sent Events)
curl -X POST "http://localhost:8000/api/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"message": "EGFR 억제제 연구 동향", "session_id": "default"}'

# Deep Research 모드 시작
curl -X POST "http://localhost:8000/api/mcp/start" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "default"}'

# 시스템 정보 조회
curl -X GET "http://localhost:8000/api/system/info"

# 모델 변경
curl -X POST "http://localhost:8000/api/system/model" \
  -H "Content-Type: application/json" \
  -d '{"model_name": "gemma2:27b", "session_id": "default"}'
```

#### 3. WebSocket 실시간 통신
```javascript
// JavaScript 예제
const ws = new WebSocket('ws://localhost:8000/ws/my_session_id');

ws.onopen = () => {
    console.log('Connected to WebSocket');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

// 메시지 전송
ws.send(JSON.stringify({
    type: 'chat',
    message: 'EGFR 억제제의 부작용은?'
}));

// MCP 명령
ws.send(JSON.stringify({
    type: 'command',
    command: '/mcp start'
}));
```

#### 4. Python API 클라이언트 예제
```python
import requests
import json

# API 기본 URL
BASE_URL = "http://localhost:8000"

# 세션 생성
response = requests.post(f"{BASE_URL}/api/session/create")
session_id = response.json()["session_id"]

# Deep Research 모드 시작
requests.post(f"{BASE_URL}/api/mcp/start", 
              json={"session_id": session_id})

# 연구 질문 전송
response = requests.post(
    f"{BASE_URL}/api/chat/message",
    json={
        "message": "최신 CAR-T 세포치료제 연구 동향",
        "session_id": session_id
    }
)

print(response.json()["response"])
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

## 🔬 MCP 통합 기능 (v3.34 완전 구성)

### 설치된 MCP 서버
1. **BioMCP** (`/mcp/biomcp/`) - 통합 생명과학 연구 도구
   - PubTator3/PubMed 문헌 검색
   - ClinicalTrials.gov 임상시험 데이터
   - MyVariant.info 유전자 변이 정보
   - 도구: `article_searcher`, `article_details`, `trial_searcher`, `variant_searcher`

2. **OpenTargets** (`/mcp/opentargets/`) - 타겟 검증 플랫폼
   - 타겟-질환 연관성 분석
   - 유전적 증거 및 신뢰도 점수
   - 약물 개발 가능성 평가

3. **DrugBank** (`/mcp/drugbank/`) - 약물 정보 데이터베이스
   - 승인된 약물 정보 및 상호작용
   - 약물동력학 및 약물동태학 데이터
   - 도구: `search_drugs`, `get_drug_details`, `find_drugs_by_indication`

4. **ChEMBL** (`/mcp/chembl/`) - 화학 생물활성 데이터베이스
   - 분자 구조 및 생물활성 데이터
   - SAR (구조-활성 관계) 분석
   - 도구: `search_molecule`, `search_target`, `canonicalize_smiles`

5. **PubMed** (`/mcp/pubmed/`) - 생명과학 문헌 검색
   - MEDLINE 데이터베이스 직접 접근
   - 저자별, 주제별 논문 검색

6. **ClinicalTrials** (`/mcp/clinicaltrials/`) - 임상시험 레지스트리
   - ClinicalTrials.gov 데이터 접근
   - 임상시험 프로토콜 및 결과 분석

### Claude Code MCP 구성 파일
- **위치**: `/home/gaia-bt/.config/claude-code/claude_code_config.json`
- **내용**: 모든 MCP 서버 구성 정보 포함
- **사용법**: Claude Code에서 즉시 사용 가능

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