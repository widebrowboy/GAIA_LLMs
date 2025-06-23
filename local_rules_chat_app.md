# GAIA 채팅 애플리케이션 개발 정리

## 프로젝트 개요

본 문서는 GAIA 채팅 애플리케이션 개발 과정을 정리한 것으로, 피그마 웹페이지 디자인 연결 및 채팅 기능 구현에 관한 작업 내용을 담고 있습니다.

## 기본 환경 설정

- **운영체제**: Ubuntu 24.04
- **Python 버전**: 3.13.2
- **출력 언어**: 한국어
- **웹 서버 포트**: 3055
- **프론트엔드 포트**: 3000

## 주요 구현 내용

### 1. 피그마 연동

- 피그마 연결을 위한 채널 접근 시도 (tes2xpv3, 0ifpoy9j)
- TalkToFigma MCP를 활용한 피그마 채널 연결 시도
- 포트 3055를 통한 연결 시도 및 디버깅

### 2. 백엔드 구현 (NestJS)

- 백엔드 구조 설계 및 생성
  - `src/main.ts`: NestJS 앱 부트스트랩, CORS 설정 (프론트엔드 원본 허용)
  - `src/app.module.ts`: ChatModule 임포트
  - `src/chat/chat.module.ts`: 컨트롤러, 서비스, 게이트웨이 선언
  - `src/chat/chat.controller.ts`: `/api/chat` 경로의 REST API 엔드포인트
  - `src/chat/chat.service.ts`: 인메모리 대화 및 메시지 저장, AI 응답 시뮬레이션
  - `src/chat/chat.gateway.ts`: Socket.IO 기반 WebSocket 게이트웨이
  - `src/chat/dto/create-message.dto.ts`: 메시지 DTO 정의
  - `src/common/interfaces/message.interface.ts`: 메시지 및 대화 인터페이스

- 주요 기능:
  - 인메모리 데이터 저장 (데이터베이스 미통합)
  - 비동기적 AI 응답 생성 시뮬레이션
  - 대화별 WebSocket 룸을 통한 메시지 브로드캐스팅
  - CORS 설정을 통한 프론트엔드 연결 허용

- 의존성:
  - @nestjs/common, @nestjs/core, @nestjs/websockets, socket.io, class-validator, uuid

### 3. 프론트엔드 구현 (React)

- 프론트엔드 구조 설계 및 생성
  - `public/index.html`: 기본 HTML 문서
  - `src/index.tsx`: React 앱 진입점
  - `src/index.css`: 글로벌 스타일
  - `src/App.tsx`: 메인 앱 컴포넌트
  - `src/App.css`: 앱 스타일
  - `src/types/types.ts`: 타입 정의
  - `src/components/Sidebar.tsx`: 사이드바 컴포넌트
  - `src/components/ChatArea.tsx`: 채팅 영역 컴포넌트
  - `src/components/MessageItem.tsx`: 메시지 아이템 컴포넌트
  - `src/services/socketService.ts`: 소켓 통신 서비스

- 주요 기능:
  - 대화 목록 및 새 대화 생성 기능
  - 메시지 전송 및 표시 기능
  - Socket.IO 클라이언트를 통한 실시간 통신
  - 반응형 디자인 적용

- 의존성:
  - react, react-dom, typescript, socket.io-client, lucide-react

### 4. 프로젝트 구조 변경

- `.gitignore`에 `webui/new_page` 디렉토리 추가
- 접근성 향상을 위해 `gaia_chat` 디렉토리 생성 및 HTML 파일 배치
- SlothGPT → GAIAGPT 명칭 변경 적용

## 테스트 및 프로토타입

- 정적 HTML/CSS/JavaScript를 활용한 채팅 인터페이스 프로토타입 구현
- 기본적인 채팅 기능 구현 (메시지 전송, 응답 생성, 대화 전환)
- 브라우저를 통한 직접 접근 테스트 완료

## 파일 경로 구조

```
/home/gaia-bt/workspace/GAIA_LLMs/
├── .gitignore (webui/new_page/ 포함)
├── gaia_chat/
│   └── index.html (GAIAGPT 채팅 인터페이스)
├── webui/new_page/ (.gitignore에 의해 제외됨)
│   ├── backend/
│   │   ├── src/
│   │   │   ├── main.ts
│   │   │   ├── app.module.ts
│   │   │   └── chat/
│   │   │       ├── chat.module.ts
│   │   │       ├── chat.controller.ts
│   │   │       ├── chat.service.ts
│   │   │       ├── chat.gateway.ts
│   │   │       ├── dto/
│   │   │       │   └── create-message.dto.ts
│   │   │       └── common/interfaces/
│   │   │           └── message.interface.ts
│   │   └── package.json
│   └── frontend/
│       ├── public/
│       │   └── index.html
│       ├── src/
│       │   ├── index.tsx
│       │   ├── index.css
│       │   ├── App.tsx
│       │   ├── App.css
│       │   ├── types/
│       │   │   └── types.ts
│       │   ├── components/
│       │   │   ├── Sidebar.tsx
│       │   │   ├── ChatArea.tsx
│       │   │   └── MessageItem.tsx
│       │   └── services/
│       │       └── socketService.ts
│       └── package.json
```

## 향후 작업 계획

1. 프론트엔드-백엔드 통합 테스트 진행
2. 빌드 및 배포 스크립트 추가
3. 사용자 인증 기능 구현 (필요시)
4. 첨부 파일, 코드 하이라이팅 등 추가 기능 구현
5. 단위 테스트 추가

## 참고사항

- 포트 3055는 백엔드 서버로 사용 중
- 포트 3000은 프론트엔드 개발 서버로 사용 예정
- CORS 설정을 통해 프론트엔드에서 백엔드 API 호출 가능
- Socket.IO를 통한 실시간 양방향 통신 구현
