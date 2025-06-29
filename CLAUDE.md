# GAIA-BT v3.26 - 신약개발 AI 연구 어시스턴트

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

### ⚠️ 테스트 전 필수 절차 (중요!)
```bash
# WebUI나 API 서버 테스트 시작 전 반드시 수행
./scripts/server_manager.sh restart-all    # 모든 서버 재시작
./scripts/server_manager.sh status         # 상태 확인
curl -s http://localhost:8000/health        # API 서버 헬스체크
```

### 포트 충돌 해결
```bash
./scripts/server_manager.sh clean-ports    # 포트 강제 정리
./scripts/server_manager.sh restart        # 서버 재시작
```

### 🔒 SSH 서비스 보호 규칙 (필수)
포트 충돌 해결 시 SSH 관련 프로세스는 절대 종료하지 않음:
- **보호 대상**: `sshd`, `ssh-agent`, `ssh`, `sftp`, `scp`
- **포트 22**: SSH 데몬 절대 종료 금지
- **포트 정리 시**: SSH 관련 프로세스 자동 제외
- **안전장치**: 시스템 원격 접속 유지 보장

#### 포트 정리 안전 규칙
- 포트 강제 정리 시 SSH 프로세스 자동 필터링
- 원격 서버 운영 시 SSH 연결 끊김 방지
- 개발 환경과 SSH 서비스 간 격리 유지

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

### Todo 관리 규칙 (필수)
- **Todo 생성**: 새로운 작업 시작 전 반드시 TodoWrite로 작업 목록 생성
- **진행 상태**: 작업 시작 시 `in_progress`로 변경, 완료 시 즉시 `completed`로 변경
- **문서화**: 완료된 Todo는 지침에 기록 후 삭제 또는 완료 표시
- **단계별 처리**: 복잡한 작업은 세부 단계로 나누어 각각 Todo로 관리

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
- **UTF-8 인코딩 안전성**  
  - 모든 HTTP 요청/응답 `Content-Type`·`Accept`·`Accept-Charset` 헤더에 `charset=utf-8` 명시  
  - `TextDecoder('utf-8')`·`TextEncoder()` 사용 시 인코딩 고정  
  - 파일 I/O(`open`, `writeFile`, DB 저장 등) 시 반드시 `encoding='utf-8'` 파라미터 지정  
  - 특수문자·이모지 사용 최소화, ASCII·기본 기호 우선  
  - UTF-8 바이트 경계가 청크 단위로 분리될 수 있으므로 스트리밍 파서에 버퍼링 로직 필수  
  - Git/EditorConfig/로케일에 `charset=utf-8`·`commitencoding=utf-8` 유지  
  - 인코딩 오류 감지 시 즉시 로그 기록 후 단계별 복구 프로세스 수행

### 레이아웃 최적화
- **DOM 구조 최적화**
  - 실제 DOM 구조와 렌더링 결과를 직접 확인하며 개발
  - min-w-0, h-full, flex-1, overflow-hidden 등 Tailwind 속성 조합 반복 테스트
  - 오른쪽 및 하단 빈 공간 완전 제거를 위한 체계적 접근
  - 불필요한 div 중첩 제거 및 구조 단순화

## 🔄 버전 관리 규칙 (필수 준수)

### 버전 관리 시스템
- **버전 형식**: `GAIA-BT v2.X` (X는 순차 증가)
- **업데이트 규칙**: 코드/내용 수정 시마다 버전 증가 필수
- **커밋 메시지**: `GAIA-BT v2.X - [변경사항 요약]` 형식 사용
- **복구 포인트**: 각 버전은 안정된 복구 포인트로 관리

### 필수 작업 절차
1. **수정 전**: 현재 버전 확인 (CLAUDE.md 첫 줄)
2. **수정 후**: 버전 번호 +1 증가
3. **커밋**: `git commit -m "GAIA-BT v2.X - [변경사항]"`
4. **푸시**: `git push origin webui`
5. **복구 포인트 출력**: 완료 시 반드시 복구 포인트 이름 표시
6. **문서화**: 주요 변경사항 기록

### 복구 포인트 출력 규칙 (필수)
- **모든 수정/추가 완료 시**: 복구 포인트 이름을 명확히 출력
- **출력 형식**: `🔖 복구 포인트: GAIA-BT v2.X - [변경사항 요약]`
- **커밋 해시**: 함께 표시하여 정확한 복구 가능
- **예시**: `🔖 복구 포인트: GAIA-BT v2.2 - 복구 포인트 출력 규칙 추가 (커밋: a1b2c3d)`

### 복구 가이드
```bash
# 특정 버전으로 복구
git log --oneline | grep "GAIA-BT v2"
git checkout [커밋해시]

# 브랜치로 복구
git checkout webui
git reset --hard [커밋해시]
```

### 버전 히스토리
- **v2.0**: 1차 완성 - Production Ready
- **v2.1**: 버전 관리 규칙 추가
- **v2.2**: 복구 포인트 출력 규칙 추가
- **v2.3**: API 모듈화 및 코드 리팩토링 시작
- **v2.4**: div 중첩 구조 개선 및 레이아웃 최적화
- **v2.5**: 오른쪽/하단 빈 공간 제거 및 DOM 구조 최적화
- **v2.6**: 환영 메시지 카드 크기 축소 및 UI 개선
- **v2.7**: 바이오/화학 전문 서비스 디자인 적용 및 아이콘/이모지 통합
- **v2.8**: 대화 페이지 완전 바이오 테마 적용 및 일관성 있는 디자인 완성
- **v2.9**: Ollama API 응답 완전성 보장 및 보고서 스타일 마크다운 렌더링 구현
- **v3.0**: 테스트 전 API 서버 재시작 필수 절차 지침 추가
- **v3.1**: Todo 관리 규칙 및 워크플로우 지침 추가
- **v3.2**: API 서버 시작 시 Ollama 모델 자동 검증 및 시작 기능 구현
- **v3.3**: WebUI와 API 서버 간 상태 동기화 문제 해결 시작
- **v3.4**: Ollama 모델 상태 관리 및 자동 시작 로직 완성
- **v3.5**: 실시간 응답, 프론트엔드 오류 안내, API 개선 완료
- **v3.6**: WebUI Sidebar 시스템 상태 새로고침 버튼 추가
- **v3.7**: WebUI 모델 관리 완전 구현 및 API 강화
- **v3.8**: WebUI API 클라이언트 완전 통합 및 fetch 오류 해결
- **v3.9**: apiClient fetch 타입 오류 해결 및 폴백 시스템 구현
- **v3.10**: fetch 타입 오류 완전 해결 및 simpleFetch 전면 적용
- **v3.11**: 직접 API 테스트 버튼 추가 및 디버깅 강화
- **v3.12**: 다중 테스트 버튼 추가로 fetch 문제 완전 진단
- **v3.13**: React 상태 업데이트 및 XHR 디버깅 강화
- **v3.14**: CORS 문제 해결 및 자동 모델 로딩 구현
- **v3.15**: node-fetch 의존성 제거 및 컴파일 오류 해결
- **v3.16**: 즉시 모델 표시 및 백그라운드 API 호출 구현
- **v3.17**: API 응답 스트리밍 문제 진단 시작
- **v3.18**: 가독성 개선 및 fetch 취소 문제 해결
- **v3.19**: 대화 페이지 응답 처리 완전 수정
- **v3.20**: 스트리밍 응답 디버깅 강화 및 Fast Refresh 문제 해결  
- **v3.21**: CORS preflight 문제 해결 및 스트리밍 연결 수정
- **v3.22**: 스트리밍 응답 처리 단순화 및 디버깅 강화
- **v3.23**: SSE 파싱 로직 단순화 및 상세 디버깅 로그 추가
- **v3.24**: 스트리밍 응답 파싱 로직 디버깅 강화 및 청크별 상세 로그 추가
- **v3.25**: SSH 서비스보호 규칙 및 포트 정리 안전장치 추가
- **v3.26**: Sidebar.tsx doInitialLoad 함수 fetch TypeError 해결 - apiClient 미들웨어 완전 적용

### 완료된 Todo 기록 (v3.7)

#### v3.2-3.7: Ollama 모델 관리 시스템 구현
- ✅ API 서버 시작 시 Ollama 모델 상태 검증 기능 구현 (`startup_validator.py`)
- ✅ 최소 1개 이상 모델 실행 보장 로직 추가
- ✅ 우선순위 기반 모델 자동 시작 시스템 (gemma3-12b → txgemma-chat → Gemma3:27b → txgemma-predict)
- ✅ WebUI 시스템 상태에서 모델 정보 표시 문제 해결
- ✅ 사용 가능한 모델 개수가 0개로 표시되던 문제 수정
- ✅ API에 모델 시작/중지 엔드포인트 추가 (`/api/system/models/{model_name}/start|stop`)
- ✅ WebUI Sidebar에 시스템 상태 새로고침 버튼 구현
- ✅ 모델 다이얼로그에 개별 모델 시작/중지 버튼 추가
- ✅ ChatbotService에 `update_current_model` 메서드 추가
- ✅ 실시간 모델 상태 동기화 개선

#### v3.1 이전: 기본 기능
- ✅ Ollama API 연결 상태 및 설정 확인
- ✅ API 서버의 Ollama 통신 로직 분석  
- ✅ WebUI에서 API 서버 통신 흐름 확인
- ✅ 에러 로그 및 응답 처리 로직 점검
- ✅ 해결 방안 제안 및 구현
- ✅ CLAUDE.md 파일 경로 오류 확인 및 수정
- ✅ CLAUDE.md에 API 서버 재시작 지침 추가
- ✅ Todo 관리 규칙을 지침에 추가

## 🚨 중요 문제 해결 및 향후 주의사항

### v3.8에서 해결한 핵심 문제

#### 1. WebUI Fetch 오류 완전 해결 ✅
**문제**: `Sidebar.tsx:111`에서 지속적인 fetch 오류 발생
- 모델 다이얼로그에서 모델 로딩 불가
- "Request timeout" 에러로 모델 제어 불가능
- WebUI와 API 서버 간 연결 불안정

**해결 방법**:
- 모든 fetch 호출을 `apiClient` 미들웨어로 교체
- 30초 타임아웃 및 3회 자동 재시도 로직 적용
- URL 인코딩 자동 처리 (모델명 특수문자 처리)
- 에러 처리 강화 및 사용자 피드백 개선

**적용된 파일**:
- `gaia_chat/src/components/Sidebar.tsx` - 모든 fetch 함수 교체
- `gaia_chat/src/utils/apiClient.ts` - 미들웨어 패턴 적용

#### 2. 이전 v3.7에서 해결한 주요 문제

##### WebUI-Backend 모델 상태 동기화 문제 ✅
**문제**: WebUI에서 모델 상태가 실제와 다르게 표시됨
- 사용 가능한 모델: 0개로 표시 (실제 4개)
- 실행 중인 모델: 표시되지 않음
- 시스템 상태: 비활성화로 표시

**원인 분석**:
- `fetchAvailableModels` 함수의 API 응답 처리 불완전
- 모델 상태 업데이트 이벤트 전파 누락
- Backend에서 모델이 실행되어도 Frontend 상태 미반영

**해결책**:
1. **API 응답 구조 정확한 매핑**:
   ```typescript
   const modelNames = data.available?.map((model: any) => model.name) || [];
   setAvailableModels(modelNames);
   setDetailedModels(data.available || []);
   setRunningModels(data.running || []);
   ```

2. **시스템 상태 새로고침 버튼 추가**:
   - 수동 상태 업데이트 기능 제공
   - `refreshSystemStatus` 함수와 연동

3. **모델 시작/중지 API 엔드포인트 구현**:
   ```python
   @router.post("/models/{model_name}/start")
   @router.post("/models/{model_name}/stop")
   ```

#### 2. 모델 실행 상태 관리 문제
**문제**: Ollama 모델이 실행되지 않아도 시스템이 정상으로 인식

**해결책**:
1. **startup_validator.py 구현**:
   - 서버 시작 시 자동 모델 검증
   - 우선순위 기반 모델 자동 시작
   - 타임아웃 및 에러 처리 강화

2. **ChatbotService 모델 관리 강화**:
   ```python
   def update_current_model(self, model_name: str) -> None:
       if "default" in self.sessions:
           self.sessions["default"].client._model_name = model_name
   ```

### 향후 발생 가능한 문제 및 예방 조치

#### 1. 메모리 관리 문제
**위험**: 여러 대형 모델 동시 실행 시 시스템 리소스 부족
**예방책**:
- 모델별 메모리 사용량 모니터링 추가
- 자동 모델 언로딩 정책 구현 (keep_alive 시간 관리)
- 시스템 리소스 한계치 설정

#### 2. 동시성 문제
**위험**: 여러 사용자가 동시에 모델 변경 시 충돌
**예방책**:
- 모델 변경 요청에 mutex 락 적용
- 대기열 시스템으로 순차 처리
- 사용자별 모델 세션 분리 구현

#### 3. API 타임아웃 및 연결 문제
**위험**: 네트워크 지연이나 서버 부하 시 WebUI 응답성 저하
**예방책 (이미 구현됨)**:
- ✅ `apiClient` 미들웨어 패턴 도입
- ✅ 30초 타임아웃 및 3회 자동 재시도
- ✅ 점진적 백오프 지연 시간 적용
- ✅ 상세한 에러 로깅 및 사용자 피드백

#### 4. 모델명 특수문자 처리 문제
**위험**: 콜론(`:`) 등 특수문자가 포함된 모델명으로 인한 URL 인코딩 오류
**예방책 (이미 구현됨)**:
- ✅ `encodeURIComponent()` 자동 적용
- ✅ API 클라이언트에서 일관된 인코딩 처리
- ✅ 백엔드에서 `unquote()` 디코딩 처리

#### 5. 상태 동기화 지연 문제  
**위험**: 모델 시작/중지 후 WebUI 상태 반영 지연
**예방책**:
- 모델 제어 후 즉시 상태 새로고침 로직 적용
- WebSocket 기반 실시간 상태 업데이트 검토
- 폴링 간격 최적화 (현재 수동 새로고침)

#### 6. 대용량 모델 로딩 시간 문제
**위험**: 27B+ 모델 로딩 시 UI 블로킹 또는 타임아웃
**예방책**:
- 프로그레스 바 또는 로딩 인디케이터 추가
- 비동기 로딩 상태 표시
- 타임아웃 시간 동적 조정 (모델 크기별)

### 핵심 아키텍처 패턴

#### API 클라이언트 미들웨어 패턴 (v3.8)
```typescript
// 표준화된 API 호출 패턴
const result = await apiClient.methodName(params);
if (result.success) {
  // 성공 처리
} else {
  // 에러 처리 및 사용자 피드백
}
```

#### 모델 상태 관리 패턴
```typescript
// 상태 업데이트 후 즉시 동기화
await modelAction();
await refreshSystemStatus();
await checkSystemStatus();
await fetchModelsWithApiClient();
```

#### 에러 처리 표준화
- ✅ 자동 재시도 로직
- ✅ 사용자 친화적 에러 메시지  
- ✅ 콘솔 로깅으로 디버깅 지원
- ✅ 타임아웃 처리 및 취소 가능

### 개발 시 주의사항

#### WebUI 개발 시
1. **API 클라이언트 사용 필수**: 직접 fetch 대신 `apiClient` 사용
2. **에러 처리 패턴 준수**: success/error 체크 후 적절한 피드백
3. **상태 동기화**: 모델 제어 후 즉시 상태 새로고침
4. **URL 인코딩**: 모델명 등 특수문자 포함 파라미터 자동 처리 확인

#### API 서버 개발 시  
1. **타임아웃 관리**: 장시간 작업 시 적절한 타임아웃 설정
2. **모델 상태 검증**: 요청 처리 전 모델 존재 여부 확인
3. **동시성 처리**: 모델 변경 요청 시 락 메커니즘 적용

---

## 🚧 현재 진행 중인 작업 (v3.23)

### 스트리밍 응답 문제 해결 진행 상황 ⚡

#### 문제 해결 완료 ✅
- **API 서버**: Ollama API와 정상 통신 확인 (curl 테스트로 SSE 스트리밍 정상 작동 확인)
- **WebUI 수정 사항**: 
  - SSE 파싱 로직 단순화
  - 상세한 디버깅 로그 추가
  - 불필요한 복잡한 로직 제거

#### 수정된 주요 내용
1. **SimpleChatContext.tsx 스트리밍 로직 개선**:
   ```typescript
   // SSE 형식 파싱 - 더 단순하게
   const trimmedLine = line.trim();
   if (trimmedLine.startsWith('data: ')) {
     const data = trimmedLine.slice(6);
     if (data && data !== '[DONE]') {
       fullResponse += data;
       setStreamingResponse(fullResponse);
     }
   }
   ```

2. **디버깅 로그 강화**:
   - 각 청크 수신 시 상세 로그
   - 라인별 처리 과정 추적
   - 최종 응답 내용 확인

#### 테스트 방법
1. WebUI(http://localhost:3003)에서 메시지 전송
2. 브라우저 개발자 도구 콘솔에서 로그 확인
3. 예상되는 로그 순서:
   - `📡 API 호출 시작`
   - `✅ HTTP 200 OK - 스트리밍 응답 시작`
   - `📖 스트림 리더 시작`
   - `📦 청크 X 수신`
   - `🔍 처리 중인 라인`
   - `📤 data 내용`
   - `💬 응답 누적 길이`

### 향후 개선 사항
- 스트리밍 응답의 실시간 UI 업데이트 최적화
- 네트워크 오류 시 재시도 로직 추가
- 응답 중단 기능 개선

---

**GAIA-BT v3.26** - 신약개발 연구의 새로운 패러다임 🧬✨
