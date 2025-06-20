# GAIA-BT WebUI 현재 디자인 가이드

## 📋 개요
GAIA-BT WebUI는 Next.js 15 + React 19 + TypeScript 기반의 신약개발 전문 AI 채팅 인터페이스입니다.

## 🎨 디자인 구성

### 1. 메인 페이지 (Home Page)
- **위치**: `/src/app/page.tsx`
- **구성 요소**:
  - 웰컴 스크린: 로고, 제목, 주요 기능 소개
  - 로딩 스크린: 브랜드 로고와 애니메이션
  - 메인 채팅 인터페이스로의 전환

### 2. 핵심 컴포넌트 구조

#### WebChatInterface (메인 채팅 UI)
- **위치**: `/src/components/chat/WebChatInterface.tsx`
- **주요 기능**:
  - 실시간 스트리밍 채팅 (단어별 점진적 표시)
  - 일반/Deep Research 모드 토글
  - 프롬프트 타입 선택 (clinical/research/chemistry/regulatory)
  - 명령어 처리 시스템
  - 세션 관리

#### 보조 컴포넌트
- **StartupBanner**: CLI 스타일 시작 배너
- **SystemStatus**: 시스템 상태 실시간 표시
- **GaiaChatInterface**: 대안 채팅 인터페이스

### 3. 색상 테마
- **Primary**: Blue-600 to Purple-600 그라디언트
- **Background**: Slate-50 via Blue-50 to Purple-50 그라디언트
- **Card**: White with subtle shadows
- **Accent Colors**:
  - Blue: 실시간 기능
  - Purple: AI/딥러닝 기능
  - Green: 성공/완료 상태

### 4. UI 스타일
- **글래스모피즘**: 반투명 백그라운드와 블러 효과
- **그라디언트**: 부드러운 색상 전환
- **애니메이션**: 
  - 페이드인/아웃 효과
  - 슬라이드 전환
  - 펄스 애니메이션 (로딩/처리 중)
  - 스핀 애니메이션 (로딩 인디케이터)

### 5. 레이아웃 구조
```
┌─────────────────────────────────────────────────┐
│                   Header                        │
│  ┌─────────────┐  ┌──────────┐  ┌────────────┐│
│  │ GAIA-BT Logo│  │Mode Toggle│  │ Settings   ││
│  └─────────────┘  └──────────┘  └────────────┘│
├─────────────────────────────────────────────────┤
│                                                 │
│              Message Area                       │
│  ┌───────────────────────────────────────────┐ │
│  │ • User Message                            │ │
│  │ • AI Response (Streaming)                 │ │
│  │ • Sources (Deep Research Mode)            │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
├─────────────────────────────────────────────────┤
│                Input Area                       │
│  ┌───────────────────────────────┐ ┌────────┐ │
│  │ Type your message...          │ │  Send  │ │
│  └───────────────────────────────┘ └────────┘ │
└─────────────────────────────────────────────────┘
```

### 6. 반응형 디자인
- **Desktop**: 전체 레이아웃 표시
- **Tablet**: 사이드바 접기, 컴팩트 헤더
- **Mobile**: 단일 컬럼, 터치 최적화 버튼

### 7. 상태 관리 (Zustand)
- **chatStore**: 세션, 메시지, 모드 관리
- **LocalStorage**: 세션 영속성
- **실시간 업데이트**: 메시지 스트리밍

### 8. API 통합
- **Backend**: FastAPI (localhost:8000)
- **Frontend**: Next.js API Routes
- **통신**: REST API + WebSocket (실시간)

## 🔧 주요 기능 특징

### 1. 실시간 스트리밍
- 단어별 점진적 표시 (50-80ms 간격)
- 자연스러운 타이핑 효과
- 처리 중 인디케이터

### 2. 모드 시스템
- **일반 모드**: 빠른 AI 응답
- **Deep Research 모드**: MCP 통합 검색
- 원클릭 토글 전환

### 3. 프롬프트 타입
- clinical (임상시험)
- research (연구분석)
- chemistry (의약화학)
- regulatory (규제)
- default (일반)

### 4. 명령어 시스템
- /help - 도움말
- /mcp start - Deep Research 시작
- /normal - 일반 모드 전환
- /prompt [type] - 프롬프트 변경
- 기타 CLI 호환 명령어

## 📦 컴포넌트 구조
```
src/
├── app/
│   ├── page.tsx (메인 페이지)
│   ├── layout.tsx (레이아웃)
│   └── globals.css (전역 스타일)
├── components/
│   ├── chat/
│   │   ├── WebChatInterface.tsx (메인 채팅)
│   │   ├── StartupBanner.tsx (시작 배너)
│   │   ├── SystemStatus.tsx (상태 표시)
│   │   └── GaiaChatInterface.tsx (대안 UI)
│   └── ui/
│       ├── Button.tsx
│       ├── Card.tsx
│       ├── Badge.tsx
│       └── Textarea.tsx
└── store/
    └── chatStore.ts (상태 관리)
```

## 🎯 디자인 원칙
1. **직관성**: 쉽고 명확한 인터페이스
2. **전문성**: 신약개발 도메인 특화
3. **반응성**: 빠른 피드백과 상태 표시
4. **일관성**: CLI와 동일한 기능성
5. **접근성**: 모바일 친화적 디자인