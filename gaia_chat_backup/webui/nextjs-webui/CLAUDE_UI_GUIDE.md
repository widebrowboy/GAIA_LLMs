# 🎨 GAIA-BT Claude Style UI Guide

## 📋 개요

GAIA-BT Modern WebUI가 Claude와 유사한 전문적인 디자인으로 업그레이드되었습니다. 이 가이드는 새로운 UI의 주요 특징과 사용법을 설명합니다.

## 🚀 주요 개선사항

### 1. **Claude 스타일 테마 시스템**
- **claude-theme.css**: 완전한 Claude 스타일 디자인 시스템
- 라이트/다크 모드 자동 지원
- 부드러운 색상 전환과 그라디언트
- 전문적인 타이포그래피

### 2. **새로운 컴포넌트: ClaudeChatInterface**
```typescript
// 사용법
import { ClaudeChatInterface } from '@/components/chat/ClaudeChatInterface';

// Modern 페이지에서 사용
<ClaudeChatInterface />
```

### 3. **주요 UI/UX 특징**

#### 사이드바 (Session Management)
- 세션 목록 관리
- 새 대화 시작
- 모바일 반응형 (햄버거 메뉴)
- 부드러운 슬라이드 애니메이션

#### 헤더 (Mode & Prompt Controls)
- **모드 토글**: 일반 ↔ Deep Research 모드 전환
- **프롬프트 선택기**: 드롭다운 메뉴로 쉬운 전환
  - 기본 (Sparkles 아이콘)
  - 임상시험 (FileText 아이콘)
  - 연구분석 (Flask 아이콘)
  - 의약화학 (Beaker 아이콘)
  - 규제전문 (Code 아이콘)

#### 메시지 영역
- Claude 스타일 메시지 버블
- 사용자/AI 구분된 레이아웃
- Markdown 렌더링 지원
- 타임스탬프 표시
- Deep Research 모드 배지

#### 입력 영역
- 자동 크기 조절 textarea
- 실시간 글자 수 표시
- 전송 버튼 활성화 상태 표시
- Shift+Enter 줄바꿈 지원

### 4. **애니메이션 & 인터랙션**

#### 로딩 애니메이션
```css
.claude-loading-dot {
  animation: claude-bounce 1.4s ease-in-out infinite;
}
```

#### 호버 효과
- `claude-hover-lift`: 호버 시 살짝 올라가는 효과
- `claude-hover-glow`: 호버 시 빛나는 효과

#### 페이드/슬라이드 애니메이션
- `claude-animate-fade-in`: 부드러운 페이드인
- `claude-animate-slide-up`: 아래에서 위로 슬라이드

### 5. **색상 시스템**

#### 주요 색상 변수
```css
/* 라이트 모드 */
--claude-bg-primary: #ffffff
--claude-bg-secondary: #f8f9fa
--claude-bg-tertiary: #f3f4f6

/* 다크 모드 */
--claude-bg-primary: #111827
--claude-bg-secondary: #1f2937
--claude-bg-tertiary: #374151
```

#### 유틸리티 클래스
- `claude-bg-primary/secondary/tertiary`: 배경색
- `claude-text-primary/secondary/tertiary`: 텍스트 색상
- `claude-border`: 보더 색상
- `claude-btn-primary/secondary/ghost`: 버튼 스타일

### 6. **반응형 디자인**
- 모바일 최적화 레이아웃
- 태블릿/데스크톱 자동 조정
- 터치 친화적 인터페이스

## 📱 사용법

### 접속 방법
```bash
# 개발 서버 실행
cd webui/nextjs-webui
npm run dev

# 브라우저에서 접속
http://localhost:3001/modern
```

### 주요 기능 사용

#### 1. 새 대화 시작
- 좌측 사이드바의 "새 대화" 버튼 클릭
- 자동으로 새 세션 생성

#### 2. 모드 전환
- 헤더의 토글 스위치로 모드 변경
- 일반 모드: 빠른 AI 응답
- Deep Research: 다중 데이터베이스 검색

#### 3. 프롬프트 타입 변경
- 헤더의 드롭다운 메뉴 클릭
- 원하는 전문 분야 선택
- 즉시 적용되어 AI 응답 스타일 변경

#### 4. 메시지 전송
- 입력창에 질문 입력
- Enter 키 또는 전송 버튼 클릭
- Shift+Enter로 줄바꿈

## 🛠️ 커스터마이징

### 색상 변경
`src/styles/claude-theme.css` 파일에서 CSS 변수 수정:

```css
:root {
  --claude-accent: 79 70 229; /* 원하는 RGB 값으로 변경 */
}
```

### 애니메이션 속도 조정
```css
.claude-animate-fade-in {
  animation: claude-fade-in 0.3s ease-out; /* 0.3s를 원하는 값으로 */
}
```

### 새로운 프롬프트 타입 추가
`ClaudeChatInterface.tsx`의 `promptTypeConfig` 객체에 추가:

```typescript
const promptTypeConfig = {
  // ... 기존 설정
  custom: {
    label: '커스텀',
    icon: CustomIcon,
    color: 'indigo',
    bgColor: 'bg-indigo-50 dark:bg-indigo-950/20',
    borderColor: 'border-indigo-200 dark:border-indigo-800',
    description: '커스텀 프롬프트 설명'
  }
};
```

## 🔍 디버깅

### 콘솔 로그 확인
```javascript
// 개발자 도구 콘솔에서
console.log(useChatStore.getState());
```

### 스타일 문제 해결
1. 브라우저 개발자 도구로 요소 검사
2. Claude 클래스가 적용되었는지 확인
3. CSS 변수가 올바르게 로드되었는지 확인

## 📈 성능 최적화

1. **메모이제이션**: React.memo 사용으로 불필요한 리렌더링 방지
2. **지연 로딩**: 큰 컴포넌트는 dynamic import 사용
3. **디바운싱**: 입력 이벤트 최적화

## 🎯 향후 개선 계획

1. **더 많은 애니메이션 효과**
   - 메시지 전송 시 물결 효과
   - 스켈레톤 로딩
   
2. **고급 기능**
   - 코드 하이라이팅 개선
   - 파일 업로드 UI
   - 음성 입력 지원
   
3. **접근성 개선**
   - ARIA 레이블 추가
   - 키보드 네비게이션 강화

## 💡 팁

1. **빠른 시작**: 홈 화면의 퀵 액션 버튼 활용
2. **키보드 단축키**: Tab으로 UI 요소 간 이동
3. **세션 관리**: 중요한 대화는 다운로드 버튼으로 백업

이 가이드를 참고하여 GAIA-BT의 새로운 Claude 스타일 UI를 최대한 활용하세요!