# GAIA-BT v2.0 - 신약개발 AI 연구 어시스턴트

## 📋 프로젝트 개요
GAIA-BT v2.0은 Ollama LLM과 MCP(Model Context Protocol)를 활용한 신약개발 전문 AI 연구 어시스턴트 시스템입니다.

## 🎯 현재 상태 - Production Ready ✅
- **개발 상태**: 1차 완성 (100% 완료)
- **배포 상태**: Production Ready
- **접속 정보**: 
  - **WebUI**: http://localhost:3003 (Next.js Frontend)
  - **API**: http://localhost:8000 (FastAPI Backend) 
  - **API 문서**: http://localhost:8000/docs (Swagger UI)

## 🚀 핵심 완성 기능

### WebUI 시스템 (완료)
- ✅ **실시간 스트리밍 채팅** - 단어별 점진적 표시
- ✅ **모드 전환 시스템** - 일반 ↔ 딥리서치 원클릭 전환
- ✅ **사이드바 토글** - 데스크톱/모바일 대응
- ✅ **대화 제목 자동 추천 및 수정** - 실시간 편집 가능
- ✅ **반응형 레이아웃** - 모바일/데스크톱 최적화
- ✅ **마크다운 렌더링** - 코드 하이라이팅 지원
- ✅ **SSR/CSR 호환성** - hydration 오류 해결

### API 서버 시스템 (완료)
- ✅ **RESTful API** - 완전 분리된 백엔드 서비스
- ✅ **WebSocket 지원** - 실시간 통신
- ✅ **Service Layer Pattern** - CLI-Web 완전 통합
- ✅ **Swagger 문서** - 자동 생성된 API 문서
- ✅ **에러 처리** - 강화된 예외 처리 시스템

### MCP 통합 시스템 (완료)
- ✅ **이중 모드 시스템** - 일반/딥리서치 모드
- ✅ **MCP 서버 관리** - 자동 시작/중지
- ✅ **Deep Search** - 다중 데이터베이스 검색
- ✅ **프롬프트 관리** - 파일 기반 시스템

## 🏗️ 프로젝트 구조

```
GAIA_LLMs/
├── app/                      # 메인 애플리케이션
│   ├── core/                 # 핵심 비즈니스 로직  
│   ├── cli/                  # CLI 인터페이스
│   ├── api/                  # API 클라이언트
│   ├── api_server/           # FastAPI 서버
│   └── utils/                # 유틸리티
├── gaia_chat/                # Next.js WebUI
│   ├── src/app/              # App Router
│   ├── src/components/       # React 컴포넌트
│   ├── src/contexts/         # Context API
│   ├── src/hooks/            # Custom Hooks
│   └── src/types/            # TypeScript 타입
├── mcp/                      # MCP 통합
├── prompts/                  # 프롬프트 템플릿
├── scripts/                  # 실행 스크립트
└── config/                   # 설정 파일
```

## 🛠️ 사용 가이드

### 서버 실행
```bash
# 모든 서버 시작 (권장)
./scripts/server_manager.sh start-all

# 서버 재시작 
./scripts/server_manager.sh restart-all

# 서버 상태 확인
./scripts/server_manager.sh status

# 서버 중지
./scripts/server_manager.sh stop
```

### CLI 실행
```bash
# CLI 챗봇 실행
python run_chatbot.py

# API 서버만 실행
python run_api_server.py
```

### 주요 명령어
```bash
/help                   # 도움말 표시
/mcp start             # 딥리서치 모드 시작
/normal                # 일반 모드로 전환  
/prompt clinical       # 임상시험 전문 모드
/mcpshow              # MCP 출력 표시 토글
```

## 🔧 기술 스택

### Frontend
- **Next.js 15** - React 기반 풀스택 프레임워크
- **TypeScript** - 타입 안정성
- **Tailwind CSS** - 유틸리티 CSS 프레임워크
- **Lucide React** - 아이콘 라이브러리

### Backend  
- **FastAPI** - 고성능 Python 웹 프레임워크
- **Python 3.13+** - 최신 Python
- **Ollama** - 로컬 LLM 서비스
- **WebSocket** - 실시간 통신

### AI & MCP
- **Gemma3-12B** - 메인 LLM 모델
- **MCP Protocol** - 모델 컨텍스트 프로토콜
- **BioMCP** - 생명과학 전용 MCP 서버

## 📊 시스템 모니터링

### 포트 관리
- **WebUI**: 3003
- **API**: 8000  
- **Ollama**: 11434

### 로그 위치
- **API 서버**: `/tmp/gaia-bt-api.log`
- **WebUI**: `/tmp/gaia-bt-webui.log`

## 🎛️ 모드 시스템

### 일반 모드
- 기본 AI 응답만 제공
- MCP 비활성화
- 빠른 응답 속도

### 딥리서치 모드  
- MCP 통합 검색 활성화
- 다중 데이터베이스 검색
- 상세한 연구 정보 제공

## 🔍 문제 해결

### 포트 충돌 해결
```bash
./scripts/server_manager.sh clean-ports    # 포트 강제 정리
./scripts/server_manager.sh restart        # 서버 재시작
```

### 로그 확인
```bash
tail -f /tmp/gaia-bt-api.log     # API 서버 로그
tail -f /tmp/gaia-bt-webui.log   # WebUI 서버 로그
```

### 서버 관리
```bash
./scripts/server_manager.sh open           # 브라우저로 WebUI 열기
./scripts/server_manager.sh status         # 전체 상태 확인
```

## 💻 개발 환경 설정

### Python 환경
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 환경변수 설정
export PYTHONPATH=/home/gaia-bt/workspace/GAIA_LLMs
export OLLAMA_BASE_URL=http://localhost:11434
```

### WebUI 개발
```bash
cd gaia_chat
npm install
npm run dev
```

## 🎯 주요 특징

### 사용자 경험
- **즉시 사용 가능** - 복잡한 설정 불필요
- **직관적 UI** - 모던한 채팅 인터페이스
- **실시간 피드백** - 스트리밍 응답
- **모바일 지원** - 반응형 디자인

### 개발자 경험
- **완전한 API** - RESTful + WebSocket
- **TypeScript 지원** - 완전한 타입 안정성
- **자동 문서화** - Swagger/OpenAPI
- **모듈형 구조** - 확장 가능한 아키텍처

## 📈 향후 확장

### 계획된 기능
- 실제 DrugBank/OpenTargets API 연결
- 캐싱 시스템 구현
- 실시간 분석 대시보드
- 다국어 지원

## 📝 개발 원칙

### 코드 품질
- TypeScript 100% 적용
- 컴포넌트 단위 테스트
- ESLint/Prettier 적용
- Git 기반 버전 관리

### 보안 및 성능
- API 키 환경변수 관리  
- CORS 설정 적용
- 메모리 효율적 스트리밍
- 포트 충돌 자동 해결

---

**GAIA-BT v2.0** - 신약개발 연구의 새로운 패러다임 🧬✨