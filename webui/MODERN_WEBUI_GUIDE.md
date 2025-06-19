# GAIA-BT Modern WebUI v2.1 - 사용자 가이드

## 🎯 개요

GAIA-BT Modern WebUI는 참고 프로젝트 [nextjs-fastapi-your-chat](https://github.com/mazzasaverio/nextjs-fastapi-your-chat)의 모던 UI/UX 패턴을 적용하여 완전히 새로 개발된 웹 인터페이스입니다.

## ✨ 주요 특징

### 🚀 모던 웹 기술 스택
- **Next.js 15** + **React 19** + **TypeScript**
- **Tailwind CSS** + **shadcn/ui** 디자인 시스템
- **Zustand** 상태 관리 + **Local Storage** 영속성
- **실시간 스트리밍** + **WebSocket** 지원

### 🎨 전문가급 UI/UX
- **글래스모피즘** 디자인 + **동적 그라디언트**
- **실시간 타이핑 효과** (단어별 점진적 표시)
- **원클릭 모드 전환** (일반 ↔ Deep Research)
- **모바일 반응형** 디자인 (터치 최적화)
- **다크 테마** 기본 + **애니메이션** 효과

### 🔬 신약개발 특화 기능
- **Deep Research 모드**: 다중 데이터베이스 통합 검색
- **전문 프롬프트**: clinical/research/chemistry/regulatory
- **MCP 서버 통합**: PubMed, ChEMBL, DrugBank, OpenTargets
- **세션 관리**: 멀티 세션 + 대화 히스토리 저장
- **실시간 시스템 상태**: API 연결 + MCP 서버 모니터링

## 🚀 빠른 시작

### 1. 서버 실행

```bash
# 1. FastAPI 백엔드 서버 시작
cd /home/gaia-bt/workspace/GAIA_LLMs
python -m uvicorn app.api_server.main:app --host 0.0.0.0 --port 8000

# 2. Next.js 프론트엔드 서버 시작
cd webui/nextjs-webui
npm run dev
```

### 2. 웹 브라우저 접속

```
📍 Modern WebUI: http://localhost:3001/modern
📍 기존 WebUI:   http://localhost:3001
📍 API 문서:     http://localhost:8000/docs
```

## 🎮 사용법

### 기본 채팅
1. **일반 질문**: 신약개발 관련 질문 입력
2. **명령어**: `/help`, `/mcp start`, `/prompt clinical` 등
3. **모드 전환**: 상단 토글 스위치로 즉시 전환

### Deep Research 모드
1. **활성화**: 토글 스위치 또는 `/mcp start` 명령어
2. **특징**: 
   - 🔬 다중 데이터베이스 동시 검색
   - 📊 과학적 근거 기반 답변
   - 📚 검색 소스 표시 (PubMed, ChEMBL 등)
   - ⚡ 실시간 검색 진행 상황

### 전문 프롬프트 모드
```
/prompt clinical    # 🏥 임상시험 전문가
/prompt research    # 📊 연구분석 전문가  
/prompt chemistry   # ⚗️ 의약화학 전문가
/prompt regulatory  # 📋 규제 전문가
```

## 🧪 통합 테스트

### 자동 테스트 실행
```bash
cd /home/gaia-bt/workspace/GAIA_LLMs
python webui/test_modern_webui.py
```

### 테스트 커버리지
- ✅ API 서버 상태 확인
- ✅ 세션 생성/관리
- ✅ 일반 채팅 메시지
- ✅ 명령어 처리
- ✅ MCP 모드 활성화
- ✅ Deep Research 채팅
- ✅ 실시간 스트리밍
- ✅ 모드/프롬프트 전환
- ✅ 세션 정보 조회

**결과**: 🎉 **100% 테스트 통과**

## 🏗️ 아키텍처

### 프론트엔드 구조
```
webui/nextjs-webui/src/
├── app/
│   ├── modern/page.tsx              # Modern WebUI 메인 페이지
│   ├── page.tsx                     # 기존 WebUI 페이지
│   └── layout.tsx                   # 전역 레이아웃
├── components/
│   ├── chat/
│   │   ├── ModernChatInterface.tsx  # 🆕 모던 채팅 인터페이스
│   │   ├── WebChatInterface.tsx     # 기존 채팅 인터페이스
│   │   ├── StartupBanner.tsx        # CLI 스타일 배너
│   │   └── SystemStatus.tsx         # 시스템 상태 표시
│   └── ui/                          # shadcn/ui 컴포넌트
├── store/
│   └── chatStore.ts                 # 🔄 향상된 Zustand 상태 관리
├── hooks/
│   └── useResponsive.ts             # 🆕 반응형 Hook
└── types/
    └── index.ts                     # TypeScript 타입 정의
```

### 백엔드 API 구조
```
app/api_server/
├── main.py                          # FastAPI 메인 앱
├── services/
│   └── chatbot_service.py           # 챗봇 핵심 서비스
├── routers/
│   ├── chat.py                      # 채팅 API
│   ├── system.py                    # 시스템 API
│   ├── mcp.py                       # MCP API
│   └── session.py                   # 세션 API
└── dependencies.py                  # 의존성 주입
```

## 🔧 기술적 개선사항

### 1. 실시간 스트리밍 향상
```typescript
// 실제 Server-Sent Events 구현
const reader = response.body?.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  // 실시간 UI 업데이트
}
```

### 2. 상태 관리 개선
```typescript
// Zustand + Local Storage 영속성
export const useChatStore = create<ChatState>()(
  devtools(
    persist(
      (set, get) => ({
        // 세션, 메시지, 설정 상태 관리
      }),
      { name: 'gaia-bt-chat-store' }
    )
  )
);
```

### 3. 모바일 반응형 지원
```typescript
// 커스텀 Responsive Hook
export function useResponsive() {
  return {
    isMobile: screenSize.width < 768,
    isTablet: screenSize.width >= 768 && screenSize.width < 1024,
    isDesktop: screenSize.width >= 1024,
  };
}
```

### 4. 향상된 오류 처리
```python
# FastAPI 전역 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )
```

## 🎨 UI/UX 특징

### 글래스모피즘 디자인
- **반투명 효과**: `backdrop-blur-xl`
- **그라디언트 테두리**: `border-gradient`
- **부드러운 그림자**: `shadow-2xl shadow-purple-500/10`

### 실시간 애니메이션
- **DNA 나선 패턴**: 60초 회전 애니메이션
- **분자 구조**: 4초 펄스 애니메이션  
- **떠다니는 파티클**: 8초 float 애니메이션
- **타이핑 효과**: 50ms 단어별 점진적 표시

### 신약개발 테마
```css
/* 전문 색상 팔레트 */
clinical: from-green-500 to-emerald-500    /* 임상 */
research: from-blue-500 to-cyan-500        /* 연구 */
chemistry: from-orange-500 to-yellow-500   /* 화학 */
regulatory: from-purple-500 to-pink-500    /* 규제 */
```

## 🚀 성능 최적화

### 1. Next.js 15 최적화
- **Turbopack**: 빌드 성능 개선
- **App Router**: 최신 라우팅 시스템
- **코드 분할**: 자동 lazy loading

### 2. API 라우팅 최적화
```typescript
// Next.js API rewrites로 효율적인 프록시
async rewrites() {
  return [
    {
      source: '/api/gaia-bt/:path*',
      destination: 'http://localhost:8000/api/:path*',
    },
  ];
}
```

### 3. 상태 관리 최적화
- **Selective Updates**: 필요한 상태만 업데이트
- **Memoization**: React.memo + useMemo 활용
- **Local Storage**: 세션 영속성

## 🔮 향후 개발 계획

### Phase 1: 고급 기능
- [ ] **실시간 협업**: 멀티 유저 세션 공유
- [ ] **음성 인터페이스**: Speech-to-Text + Text-to-Speech
- [ ] **파일 업로드**: 논문 PDF, 분자 구조 파일 지원
- [ ] **시각화**: 분자 구조 3D 렌더링

### Phase 2: AI 고도화  
- [ ] **RAG 시스템**: 개인화된 지식베이스
- [ ] **멀티모달**: 이미지 + 텍스트 통합 분석
- [ ] **워크플로우**: 연구 파이프라인 자동화
- [ ] **예측 모델**: 약물 특성 예측 AI

### Phase 3: 플랫폼 확장
- [ ] **모바일 앱**: React Native 포팅
- [ ] **데스크톱 앱**: Electron 패키징  
- [ ] **클라우드 배포**: Docker + Kubernetes
- [ ] **API 생태계**: 서드파티 통합

## 🤝 기여 가이드

### 개발 환경 설정
```bash
# 1. 저장소 클론
git clone <repository>
cd GAIA_LLMs

# 2. Python 환경
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Node.js 환경  
cd webui/nextjs-webui
npm install
npm run dev

# 4. 서버 실행
python -m uvicorn app.api_server.main:app --reload
```

### 개발 가이드라인
1. **TypeScript 강제**: 모든 컴포넌트 타입 정의
2. **ESLint + Prettier**: 코드 품질 유지
3. **테스트 필수**: 새 기능은 테스트 포함
4. **문서 업데이트**: 주요 변경사항은 문서 반영

## 📞 지원 및 피드백

### 이슈 리포팅
- **버그 리포트**: GitHub Issues 활용
- **기능 요청**: Feature Request 템플릿 사용
- **질문/토론**: GitHub Discussions

### 연락처
- **개발팀**: GAIA-BT Development Team
- **이메일**: support@gaia-bt.com
- **문서**: [전체 문서 사이트]

---

**🎉 GAIA-BT Modern WebUI를 사용해주셔서 감사합니다!**  
*신약개발의 미래를 함께 만들어갑시다.*