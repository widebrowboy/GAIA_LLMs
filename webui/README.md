# GAIA-BT WebUI v2.0 Alpha

GAIA-BT 신약개발 연구 시스템의 웹 기반 사용자 인터페이스

## 📋 개요

GAIA-BT WebUI는 기존 CLI 시스템의 모든 기능을 웹 브라우저에서 사용할 수 있도록 하는 현대적인 인터페이스를 제공합니다.

### 주요 특징

- 🌐 **웹 기반 접근성**: 모든 플랫폼에서 브라우저를 통한 접근
- 📱 **반응형 디자인**: 데스크톱, 태블릿, 모바일 지원
- 🔄 **실시간 통신**: WebSocket 기반 실시간 채팅 및 연구 진행 모니터링
- 📊 **데이터 시각화**: MCP 검색 결과 및 연구 데이터 차트 표시
- 🎯 **CLI 호환성**: 기존 CLI 시스템과 완벽한 호환성

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────┐
│                 Frontend                         │
│            Next.js + TypeScript                  │
│        Tailwind CSS + Shadcn/ui                 │
└─────────────────────────────────────────────────┘
                       │
              ┌─────────────────┐
              │   WebSocket     │ (실시간 통신)
              │   REST API      │ (데이터 조회)
              └─────────────────┘
                       │
┌─────────────────────────────────────────────────┐
│              Backend API Layer                   │
│               FastAPI + Python                   │
└─────────────────────────────────────────────────┘
                       │
┌─────────────────────────────────────────────────┐
│           Existing CLI System                    │
│         DrugDevelopmentChatbot                   │
│            MCP Manager                           │
└─────────────────────────────────────────────────┘
```

## 🚀 빠른 시작

### 전제 조건

- Node.js 18.0.0 이상
- Python 3.13 이상
- Docker (선택사항)

### 개발 환경 설정

1. **의존성 설치**
```bash
# Frontend 의존성 설치
cd webui/frontend
npm install

# Backend 의존성 설치
cd ../backend
pip install -r requirements.txt
```

2. **개발 서버 실행**
```bash
# Backend 서버 시작 (터미널 1)
cd webui/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend 서버 시작 (터미널 2)
cd webui/frontend
npm run dev
```

3. **접속**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs

### Docker 실행

```bash
# Docker Compose로 전체 스택 실행
cd webui
docker-compose -f docker-compose.webui.yml up -d

# 로그 확인
docker-compose -f docker-compose.webui.yml logs -f
```

## 📁 프로젝트 구조

```
webui/
├── frontend/                    # Next.js Frontend
│   ├── src/
│   │   ├── components/          # React 컴포넌트
│   │   │   ├── chat/           # 채팅 인터페이스
│   │   │   ├── research/       # 연구 관련 UI
│   │   │   ├── settings/       # 설정 UI
│   │   │   └── common/         # 공통 컴포넌트
│   │   ├── hooks/              # React Hooks
│   │   ├── store/              # Zustand 상태 관리
│   │   ├── utils/              # 유틸리티 함수
│   │   └── types/              # TypeScript 타입
│   ├── package.json
│   ├── next.config.js
│   └── tailwind.config.js
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── main.py             # FastAPI 메인 앱
│   │   ├── api/                # API 엔드포인트
│   │   ├── core/               # 핵심 로직
│   │   │   ├── cli_adapter.py  # CLI 통합 어댑터
│   │   │   └── bridge.py       # 브리지 패턴
│   │   ├── models/             # 데이터 모델
│   │   └── utils/              # 유틸리티
│   └── requirements.txt
├── docker-compose.webui.yml     # Docker Compose 설정
└── README.md
```

## 🔧 주요 기능

### 1. 채팅 인터페이스
- 실시간 채팅 시스템
- 메시지 히스토리 관리
- 마크다운 지원
- 코드 하이라이팅

### 2. 이중 모드 시스템
- **일반 모드**: 기본 AI 답변
- **Deep Research 모드**: MCP 통합 검색

### 3. 연구 진행 모니터링
- 실시간 진행률 표시
- 단계별 상세 정보
- 시각적 진행 바

### 4. MCP 검색 결과 시각화
- 탭 기반 결과 표시 (PubMed, ChEMBL, Clinical, Variants)
- 검색 결과 필터링 및 정렬
- 상세 정보 모달

### 5. 설정 관리
- 프롬프트 모드 변경
- UI 테마 설정
- MCP 출력 제어

## 🎨 UI/UX 특징

### 디자인 시스템
- **컬러 팔레트**: 신약개발 도메인 특화 색상
- **타이포그래피**: 과학적 데이터 가독성 최적화
- **아이콘**: Lucide React 아이콘 세트

### 반응형 지원
- 모바일 우선 설계
- 태블릿 최적화
- 데스크톱 전체 화면 활용

### 접근성 (a11y)
- WCAG 2.1 AA 수준 준수
- 키보드 네비게이션 지원
- 스크린 리더 호환성

## 🔌 API 명세

### REST API 엔드포인트

```typescript
// 채팅
POST /api/chat
GET /api/sessions
DELETE /api/sessions/{session_id}

// 시스템
GET /api/health
GET /api/status

// 설정
GET /api/config
PUT /api/config
```

### WebSocket 이벤트

```typescript
// 클라이언트 → 서버
{
  type: 'chat_message',
  content: string,
  sessionId: string
}

// 서버 → 클라이언트
{
  type: 'chat_response' | 'research_progress' | 'mcp_results',
  data: any,
  timestamp: string
}
```

## 📊 성능 최적화

### Frontend
- Code Splitting (Next.js 자동)
- 이미지 최적화 (Next.js Image)
- Tree Shaking
- 상태 관리 최적화 (Zustand)

### Backend
- 비동기 처리 (FastAPI + asyncio)
- 커넥션 풀링
- 요청 캐싱
- 세션 관리 최적화

## 🔒 보안

### 인증 및 권한
- JWT 토큰 기반 인증 (옵션)
- Session 기반 인증
- Rate Limiting

### 데이터 보호
- CORS 정책 설정
- XSS 방지
- CSRF 보호
- 입력 검증 및 이스케이핑

## 🧪 테스트

### Frontend 테스트
```bash
cd frontend
npm run test          # Jest + React Testing Library
npm run test:e2e       # Playwright E2E 테스트
npm run lint           # ESLint
npm run type-check     # TypeScript 타입 체크
```

### Backend 테스트
```bash
cd backend
pytest                # API 테스트
pytest --cov          # 커버리지 포함
```

## 📦 배포

### 개발 환경
```bash
# 통합 스크립트 사용
./scripts/run_webui.sh
```

### 프로덕션 환경
```bash
# Docker Compose 프로덕션 모드
docker-compose -f docker-compose.webui.yml --profile production up -d
```

### 환경 변수

```bash
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Backend (.env)
ENVIRONMENT=development
LOG_LEVEL=info
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379
```

## 🛠️ 개발 가이드

### 컴포넌트 추가
```typescript
// components/example/ExampleComponent.tsx
import { FC } from 'react';

interface ExampleComponentProps {
  title: string;
}

export const ExampleComponent: FC<ExampleComponentProps> = ({ title }) => {
  return (
    <div className="p-4 bg-card rounded-lg">
      <h2 className="text-xl font-semibold">{title}</h2>
    </div>
  );
};
```

### API 엔드포인트 추가
```python
# backend/app/api/example.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/example", tags=["example"])

@router.get("/")
async def get_example():
    return {"message": "Example endpoint"}
```

### 상태 관리
```typescript
// store/exampleStore.ts
import { create } from 'zustand';

interface ExampleState {
  data: any[];
  loading: boolean;
  setData: (data: any[]) => void;
  setLoading: (loading: boolean) => void;
}

export const useExampleStore = create<ExampleState>((set) => ({
  data: [],
  loading: false,
  setData: (data) => set({ data }),
  setLoading: (loading) => set({ loading }),
}));
```

## 🐛 문제 해결

### 자주 발생하는 문제

1. **CLI 시스템 연결 실패**
   ```bash
   # PYTHONPATH 확인
   export PYTHONPATH=/path/to/GAIA_LLMs
   ```

2. **WebSocket 연결 문제**
   ```javascript
   // 브라우저 개발자 도구에서 확인
   console.log('WebSocket status:', socket.readyState);
   ```

3. **빌드 오류**
   ```bash
   # 캐시 클리어
   npm run clean
   rm -rf .next node_modules
   npm install
   ```

## 📞 지원 및 기여

### 이슈 리포팅
GitHub Issues를 사용하여 버그 리포트 및 기능 요청

### 개발 기여
1. Fork 및 Clone
2. Feature Branch 생성
3. 변경사항 커밋
4. Pull Request 생성

### 코드 스타일
- Frontend: ESLint + Prettier
- Backend: Black + isort
- 커밋 메시지: Conventional Commits

---

## 📄 라이선스

GAIA-BT 프로젝트 라이선스와 동일

---

**GAIA-BT WebUI v2.0 Alpha** - 신약개발 연구의 새로운 웹 경험