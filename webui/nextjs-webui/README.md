# 🧬 GAIA-BT Next.js WebUI v2.0 Alpha

**신약개발 전문 AI 어시스턴트 웹 인터페이스**

## 🎯 프로젝트 개요

GAIA-BT v2.0 Alpha의 Next.js 기반 웹 인터페이스입니다. Docker 없이 로컬에서 직접 실행할 수 있는 완전한 웹 애플리케이션으로 개발되었습니다.

### 핵심 특징

- ✅ **Next.js 15.3** + **TypeScript** + **Tailwind CSS**
- ✅ **Docker 없이 직접 실행** 가능
- ✅ **GAIA-BT 완전 통합** - run_chatbot.py와 동등한 기능
- ✅ **실시간 채팅 인터페이스** 및 **Function Calling 시스템**
- ✅ **Mock 폴백 시스템** - GAIA-BT 없이도 데모 가능
- ✅ **반응형 디자인** 및 **신약개발 특화 UI**

## 🚀 빠른 시작

### 1. 설치 및 실행

```bash
# 의존성 설치 (이미 완료됨)
npm install

# 개발 서버 시작
npm run dev

# 또는 GAIA-BT 특화 명령어
npm run gaia-bt
```

### 2. 브라우저 접속

```
http://localhost:3000
```

## 📋 주요 기능

### 💬 Chat Interface

- **Normal Mode**: 빠른 신약개발 상담
- **Deep Research Mode**: MCP 통합 심층 분석
- **5가지 전문 프롬프트**: default, clinical, research, chemistry, regulatory
- **실시간 마크다운 렌더링** 및 **메시지 히스토리**

### ⚡ Function Panel

**8개 전문 Functions 제공:**

1. **get_system_status** - 시스템 상태 확인
2. **switch_mode** - Normal/Deep Research 모드 전환
3. **change_prompt_mode** - 전문 프롬프트 모드 변경
4. **deep_research_search** - MCP 통합 심층 연구 검색
5. **molecular_analysis** - 분자 구조 및 약물 상호작용 분석
6. **clinical_trial_search** - 임상시험 검색
7. **literature_search** - 과학 문헌 검색
8. **generate_research_plan** - AI 기반 연구 계획 수립

## 🔧 기술 스택

### Frontend
- **Next.js 15.3** (App Router)
- **React 19** + **TypeScript**
- **Tailwind CSS 4** (스타일링)
- **Lucide React** (아이콘)
- **React Markdown** (마크다운 렌더링)

### Backend
- **Next.js API Routes** (서버리스 함수)
- **GAIA-BT Python 스크립트 통합**
- **Mock 폴백 시스템**

## 🎮 사용법

### 1. 채팅 인터페이스 사용

1. **Chat Interface** 탭 선택
2. 상단 설정에서 모드 및 프롬프트 선택
3. 채팅창에 신약개발 관련 질문 입력
4. 실시간으로 GAIA-BT 응답 확인

**예시 질문들:**
```
"아스피린의 새로운 치료 적용 가능성을 분석해주세요"
"BRCA1 타겟을 이용한 유방암 치료제 개발 전략"
"임상시험 Phase I과 Phase II의 주요 차이점은?"
```

### 2. Function Panel 사용

1. **Functions** 탭 선택
2. 왼쪽에서 실행할 함수 선택
3. 필요한 매개변수 입력
4. "Execute Function" 버튼 클릭
5. 오른쪽에서 결과 확인

**예시 Function 호출:**
```javascript
get_system_status()                    // 매개변수 없음
switch_mode("deep_research")           // mode 선택
deep_research_search("cancer therapy") // query 입력
molecular_analysis("aspirin")          // compound 입력
```

## 🧪 Mock 시스템

GAIA-BT가 연결되지 않은 경우 자동으로 Mock 모드로 전환되어 시뮬레이션 응답을 제공합니다.

### Mock 응답 특징

- **신약개발 도메인 특화** 응답
- **프롬프트 모드별 차별화** 내용
- **실제와 유사한 구조화된 출력**
- **타임스탬프 및 Mock 표시**

## 🎯 run_chatbot.py 대비 장점

### 1. 웹 인터페이스
- **그래픽 UI**: 명령어 대신 직관적인 웹 인터페이스
- **멀티탭**: 채팅과 Function을 동시에 사용 가능
- **실시간 렌더링**: 마크다운, 코드 하이라이팅
- **히스토리 관리**: 대화 기록 자동 저장

### 2. 향상된 기능
- **비주얼 피드백**: 진행 상황, 브랜딩, 모드 표시
- **카테고리 분류**: Function들의 체계적 분류
- **매개변수 UI**: 폼 기반 매개변수 입력
- **결과 포맷팅**: 구조화된 결과 표시

### 3. 접근성
- **브라우저 접근**: 어디서나 웹 브라우저로 접근
- **설치 불필요**: Docker 없이 npm 명령어로 실행
- **크로스 플랫폼**: Windows, macOS, Linux 모두 지원

---

**🧬 GAIA-BT v2.0 Alpha Next.js WebUI - Ready for Production!**
