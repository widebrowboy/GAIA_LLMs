# GAIA-BT v3.84 - 신약개발 AI 연구 어시스턴트

## 📋 프로젝트 개요

GAIA-BT는 Ollama LLM과 MCP(Model Context Protocol)를 활용한 신약개발 전문 AI 연구 어시스턴트 시스템입니다.

## 🎯 현재 상태 - Production Ready ✅

- **개발 상태**: 완전 완성 (100% 완료)
- **배포 상태**: Production Ready
- **접속 정보**: 
  - **WebUI**: http://localhost:3003 (Next.js Frontend)
  - **API**: http://localhost:8000 (FastAPI Backend) 
  - **API 문서**: http://localhost:8000/docs (Swagger UI)
  - **Milvus 관리 UI**: http://localhost:3000 (Attu 전용 인터페이스)
  - **Milvus API**: http://localhost:9091 (Milvus 직접 접근)

## 🚀 핵심 완성 기능

### WebUI 시스템 ✅
- ✅ **실시간 스트리밍 채팅** - 단어별 점진적 표시
- ✅ **모드 전환 시스템** - 일반 ↔ 딥리서치 원클릭 전환
- ✅ **응답 피드백 시스템** - 썸업/썸다운 버튼으로 응답 품질 평가
- ✅ **클립보드 복사 기능** - 원클릭 응답 내용 복사 및 시각적 피드백
- ✅ **인터랙티브 UI** - 타임스탬프 앞 액션 버튼 배치 및 반응형 디자인
- ✅ **사이드바 토글** - 데스크톱/모바일 대응
- ✅ **대화 제목 자동 추천 및 수정** - 실시간 편집 가능
- ✅ **반응형 레이아웃** - 모바일/데스크톱 최적화
- ✅ **마크다운 렌더링** - 코드 하이라이팅 지원
- ✅ **사이드바 대화 기록 최적화** - 제목 15자 제한 및 툴팁 지원

### API 서버 시스템 ✅
- ✅ **RESTful API** - 완전 분리된 백엔드 서비스
- ✅ **WebSocket 지원** - 실시간 통신
- ✅ **Service Layer Pattern** - CLI-Web 완전 통합
- ✅ **Swagger 문서** - 자동 생성된 API 문서
- ✅ **에러 처리** - 강화된 예외 처리 시스템

### MCP 통합 시스템 ✅
- ✅ **이중 모드 시스템** - 일반/딥리서치 모드
- ✅ **MCP 서버 관리** - 자동 시작/중지
- ✅ **Deep Search** - 다중 데이터베이스 검색
- ✅ **프롬프트 관리** - 파일 기반 시스템

### RAG 시스템 ✅
- ✅ **Milvus Lite 벡터 데이터베이스** - 로컬 임베디드 벡터 저장소
- ✅ **mxbai-embed-large 임베딩** - 334M 파라미터 의미론적 유사성 모델
- ✅ **문서 처리 파이프라인** - 청킹, 벡터화, 저장 자동화
- ✅ **RAG 응답 생성** - gemma3-12b를 활용한 컨텍스트 기반 답변
- ✅ **RESTful API** - 문서 추가, 검색, 쿼리 엔드포인트

### RAG 시스템 고도화 (v3.77) ✅
- ✅ **PyMilvus 통합 Reranker** - BGE Reranker 기반 검색 결과 개선
- ✅ **2단계 검색 아키텍처** - Retrieval + Cross Encoder Reranking
- ✅ **Gemma 기반 Cross Encoder** - BAAI/bge-reranker-v2-gemma 모델 적용
- ✅ **성능 최적화** - 배치 처리 및 CPU/GPU 가속 지원
- ✅ **API 확장** - 리랭킹 기능 포함 고급 검색 엔드포인트
- ✅ **완전한 Swagger 문서** - 상세한 예시 및 사용법 포함

### 🧠 AI 학습 및 피드백 시스템 (v3.80 완성) ✅
- ✅ **피드백 벡터 저장소** - 썸업/썸다운 데이터 임베딩 기반 저장
- ✅ **질문-응답-피드백 관계 매핑** - 사용자 평가 데이터 구조화
- ✅ **실시간 피드백 알림** - 저장 완료 및 학습 기여도 표시
- ✅ **피드백 API 시스템** - RESTful API로 피드백 수집 및 분석
- ✅ **Milvus 웹 UI 통합** - 벡터 데이터베이스 시각적 관리
- 🚧 **피드백 기반 RAG 개선** - 부정 피드백 패턴 학습 및 회피
- 🚧 **Gemma 파인튜닝 데이터셋** - 고품질 응답 우선 학습 데이터 구축
- 🚧 **자동 품질 평가 시스템** - 피드백 패턴 기반 응답 품질 예측

## 🏗️ 프로젝트 구조

```
GAIA_LLMs/
├── app/                      # 메인 애플리케이션
│   ├── core/                 # 핵심 비즈니스 로직  
│   ├── cli/                  # CLI 인터페이스
│   ├── api/                  # API 클라이언트
│   ├── api_server/           # FastAPI 서버
│   ├── rag/                  # RAG 시스템
│   │   ├── embeddings.py     # 임베딩 서비스
│   │   ├── vector_store_lite.py  # Milvus Lite 벡터 스토어
│   │   ├── rag_pipeline.py   # RAG 파이프라인
│   │   ├── feedback_store.py # 피드백 벡터 저장소 (신규)
│   │   ├── feedback_rag.py   # 피드백 기반 RAG 개선 (신규)
│   │   └── rule_1.md         # Reranker 구현 가이드
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
├── config/                   # 설정 파일
├── test_rag_api.py           # RAG API 테스트
└── test_reranking_api.py     # 리랭킹 API 테스트
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

### Milvus 웹 UI 사용 (v3.80 신규)
```bash
# Milvus 서버 및 웹 UI 시작
./scripts/milvus_manager.sh start

# 웹 UI 접속 (브라우저)
./scripts/milvus_manager.sh webui

# Milvus 서버 상태 확인
./scripts/milvus_manager.sh status

# 서버 중지
./scripts/milvus_manager.sh stop

# 웹 UI 직접 접속
# http://localhost:9091/webui (Milvus 관리)
# http://localhost:9001 (MinIO 콘솔 - 스토리지)
```

### CLI 실행
```bash
# CLI 챗봇 실행
python run_chatbot.py

# API 서버만 실행
python run_api_server.py
```

### RAG 시스템 사용법
```bash
# RAG API 테스트  
python test_rag_api.py

# 리랭킹 기능 테스트
python test_reranking_api.py

# API 엔드포인트
# 문서 추가: POST /api/rag/documents
# RAG 쿼리: POST /api/rag/query  
# 문서 검색: GET /api/rag/search
# 시스템 통계: GET /api/rag/stats
```

### 피드백 시스템 사용법 (v3.81 업데이트)
```bash
# 중복 검사 포함 피드백 API 테스트 (v3.81 신규)
curl -X POST "http://localhost:8000/api/feedback/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "EGFR 돌연변이 폐암의 1차 치료제는 무엇인가요?",
    "answer": "EGFR 돌연변이 폐암의 1차 치료제로는 게피티닙...",
    "feedback_type": "positive",
    "check_duplicates": true,
    "similarity_threshold": 0.95
  }'

# 중복 검사 비활성화 (기존 동작)
curl -X POST "http://localhost:8000/api/feedback/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "질문 내용",
    "answer": "응답 내용", 
    "feedback_type": "positive",
    "check_duplicates": false
  }'

# 피드백 통계 조회
curl http://localhost:8000/api/feedback/stats

# 유사 피드백 검색
curl -X POST "http://localhost:8000/api/feedback/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "EGFR 치료제", "limit": 5}'

# 파인튜닝 데이터 추출
curl -X POST "http://localhost:8000/api/feedback/training-data" \
  -H "Content-Type: application/json" \
  -d '{"min_quality_score": 0.8, "limit": 100}'

# Milvus 웹 UI에서 데이터 시각화 (v3.81 신규)
# 1. Milvus 서버 시작
./scripts/milvus_manager.sh start

# 2. 웹 UI 접속 (자동으로 브라우저에서 열림)
./scripts/milvus_manager.sh webui

# 3. 직접 URL 접속
# - Milvus 웹 UI: http://localhost:9091/webui  
# - MinIO 콘솔: http://localhost:9001 (minioadmin/minioadmin)

# 4. 저장된 컬렉션 확인
# - feedback_collection: 피드백 데이터
# - qa_pairs_collection: 질문-응답 쌍 및 품질 데이터
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

### AI & RAG
- **Gemma3-12B** - 메인 LLM 모델
- **mxbai-embed-large** - 의미론적 유사성 최적화 임베딩 모델 (334M)
- **Milvus Lite** - 벡터 데이터베이스 (RAG 시스템용)
- **BGE Reranker** - BAAI/bge-reranker-v2-gemma Cross Encoder
- **MCP Protocol** - 모델 컨텍스트 프로토콜
- **BioMCP** - 생명과학 전용 MCP 서버

## 📊 시스템 모니터링

### 포트 관리
- **WebUI**: 3003
- **API**: 8000  
- **Swagger UI**: 8000/docs
- **벡터 DB 웹 UI**: 9091/webui
- **Ollama**: 11434
- **Milvus Lite**: 파일 기반 (./milvus_lite.db)
- **Milvus 서버**: 19530 (gRPC), 9091 (웹 UI)
- **MinIO**: 9000 (API), 9001 (콘솔)

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

### ⚠️ 테스트 전 필수 절차
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

### 🔒 SSH 및 포트 포워딩 보호 규칙
포트 충돌 해결 시 중요 시스템 프로세스는 절대 종료하지 않음:

#### 보호 대상 프로세스
- **SSH 관련**: `sshd`, `ssh-agent`, `ssh`, `sftp`, `scp`, `remote-ssh`
- **IDE 포트포워딩**: `code`, `windsurf`, `cursor`, `code-tunnel`, `code-server`
- **JetBrains IDEs**: `webstorm`, `intellij`, `phpstorm`, `pycharm`, `goland`, `clion`, `datagrip`, `rider`, `rubymine`, `appcode`, `mps`, `gateway`
- **포트 22**: SSH 데몬 절대 종료 금지
- **IDE 포트**: VS Code/Windsurf/Cursor/JetBrains 포트포워딩 연결 유지

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

## 📝 개발 원칙

### Todo 관리 규칙
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
- UTF-8 인코딩 안전성 보장

## 🔄 버전 관리 규칙

### 버전 관리 시스템
- **버전 형식**: `GAIA-BT v3.X` (X는 순차 증가)
- **업데이트 규칙**: 코드/내용 수정 시마다 버전 증가 필수
- **커밋 메시지**: `GAIA-BT v3.X - [변경사항 요약]` 형식 사용
- **복구 포인트**: 각 버전은 안정된 복구 포인트로 관리

### 복구 가이드
```bash
# 특정 버전으로 복구
git log --oneline | grep "GAIA-BT v3"
git checkout [커밋해시]

# 브랜치로 복구
git checkout webui
git reset --hard [커밋해시]
```

## 📈 주요 버전 히스토리

### 최신 버전
- **v3.77**: PyMilvus 통합 Reranker 완전 구현 - 2단계 검색 아키텍처, BGE Cross Encoder
- **v3.76**: Milvus RAG 시스템 완전 구현 - Milvus Lite 기반 벡터 DB, 문서 처리 파이프라인
- **v3.75**: Milvus RAG 시스템 구축 계획 수립 - mxbai-embed-large, gemma3-12b 설계
- **v3.74**: 사이드바 대화 기록 제목 15자 제한 및 UI 최적화
- **v3.73**: 모드 전환 시 모델 자동 변경 완전 방지

### 주요 마일스톤
- **v3.0-v3.25**: 네트워크 통신 안정성 확보, 스트리밍 완성, SSH 보안 강화
- **v3.26-v3.50**: WebUI 개선, 마크다운 렌더링, 모델 관리 시스템
- **v3.51-v3.74**: 딥리서치 모드 고도화, 이중 언어 지원, UI/UX 최적화
- **v3.75-v3.77**: RAG 시스템 구축 및 고도화, PyMilvus Reranker 통합

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

### 신약개발 특화
- **전문 MCP 서버** - DrugBank, OpenTargets, ChEMBL, PubMed 통합
- **고급 RAG 시스템** - 2단계 검색, Cross Encoder Reranking
- **학술 논문 포맷** - APA 인용, Sequential Thinking
- **다국어 지원** - 한국어/영어 자동 감지

## 🧠 Reasoning RAG + PyMilvus Reranker 통합 시스템 (v3.84+ 계획)

### 3단계 RAG 아키텍처 설계

#### Phase 1: Reasoning Agent (추론 계획)
```python
class ReasoningRAGPipeline:
    """Self-RAG, CoT-RAG, MCTS-RAG 통합 추론 파이프라인"""
    
    def __init__(self):
        self.milvus_client = MilvusClient("tcp://localhost:19530")
        self.embedder = OllamaEmbeddings(model="mxbai-embed-large")
        self.reranker = BGERerankFunction(
            model_name="BAAI/bge-reranker-v2-m3",
            device="cuda:0", use_fp16=True
        )
        self.llm = OllamaLLM(model="gemma3-12b")
    
    async def reasoning_search(self, query: str, mode: str = "self_rag"):
        """다단계 추론 검색 실행"""
        if mode == "self_rag":
            return await self._self_rag_pipeline(query)
        elif mode == "cot_rag":
            return await self._cot_rag_pipeline(query)
        elif mode == "mcts_rag":
            return await self._mcts_rag_pipeline(query)
```

#### Phase 2: Multi-Step Search (검색 최적화)
```python
async def _multi_step_search(self, query, history=[]):
    """반복적 검색 및 컨텍스트 확장"""
    # 1) 검색 필요성 판단
    if not await self._should_retrieve(query, history):
        return await self._synthesize_from_history(history)
    
    # 2) 컨텍스트 기반 쿼리 개선
    refined_query = await self._refine_query(query, history)
    
    # 3) 벡터 검색 (k=20)
    embeddings = await self.embedder.embed(refined_query)
    candidates = await self.milvus_client.search(
        collection_name="documents",
        data=[embeddings],
        limit=20
    )
    
    # 4) Cross Encoder 리랭킹 (k=5)
    reranked = self.reranker(refined_query, candidates, top_k=5)
    
    # 5) 관련성 평가 및 반성
    relevance = await self._evaluate_relevance(query, reranked)
    
    return reranked, relevance
```

#### Phase 3: Cross Encoder + Synthesis (답변 생성)
```python
async def _synthesize_answer(self, query, contexts, reasoning_history):
    """추론 기반 최종 답변 합성"""
    synthesis_prompt = f"""
    Research Question: {query}
    
    Reasoning Steps:
    {self._format_reasoning_history(reasoning_history)}
    
    Retrieved Evidence:
    {self._format_contexts(contexts)}
    
    Provide a comprehensive answer following academic standards.
    """
    
    return await self.llm.generate(synthesis_prompt)
```

### 주요 Reasoning RAG 패턴 구현

#### 1. Self-RAG (자기반성 RAG)
- **반성 토큰**: [Retrieve], [Relevant], [Support], [Continue]
- **반복적 검색**: 답변 품질이 임계값 미달 시 추가 검색
- **자기 평가**: 생성된 응답의 지지도 및 관련성 평가

#### 2. CoT-RAG (사고의 연쇄 RAG)  
- **단계별 계획**: 복잡한 질문을 하위 문제로 분해
- **순차적 추론**: 각 단계별 검색 및 부분 답변 생성
- **연쇄적 합성**: 단계별 결과를 최종 답변으로 통합

#### 3. MCTS-RAG (몬테카를로 트리 RAG)
- **탐색 공간**: 가능한 검색 경로를 트리 구조로 모델링
- **UCB 선택**: Upper Confidence Bound로 최적 검색 경로 선택
- **시뮬레이션**: 각 경로의 예상 답변 품질 평가

### 벡터 데이터베이스 확장 설계

#### Reasoning Context Collection
```python
reasoning_schema = {
    "id": "reasoning_step_id",
    "query_embedding": [512],  # mxbai-embed-large 차원
    "reasoning_type": "self_rag|cot_rag|mcts_rag",
    "step_number": 3,
    "sub_query": "세부 질문",
    "search_results": ["문서1", "문서2"],
    "relevance_score": 0.85,
    "support_score": 0.78,
    "reasoning_chain": ["단계1", "단계2", "단계3"],
    "final_confidence": 0.91
}
```

#### Enhanced Feedback Collection
```python
enhanced_feedback_schema = {
    "id": "feedback_id",
    "reasoning_mode": "self_rag",
    "reasoning_steps": 4,
    "search_iterations": 2,
    "total_latency": 8.5,  # 초
    "user_satisfaction": "positive|negative",
    "reasoning_quality": 0.88,  # 추론 품질 점수
    "search_effectiveness": 0.92  # 검색 효과성 점수
}
```

### v3.84-v3.90 구현 로드맵

#### v3.84: 기본 Reasoning RAG 인프라
- 🔄 **ReasoningRAGPipeline 클래스 구현**
  - Self-RAG 기본 패턴 구현
  - LangChain Agent 통합
  - 추론 단계별 로깅 시스템

- 🔄 **PyMilvus Reranker 통합**
  - rule_2.md 기반 BGE Reranker 적용
  - 2단계 검색 파이프라인 완성
  - 성능 벤치마킹 시스템

- 🔄 **API 확장**
  - `/api/reasoning-rag/query` 엔드포인트
  - 추론 모드 선택 파라미터
  - 실시간 추론 과정 스트리밍

#### v3.85: CoT-RAG 및 다단계 추론
- 🔄 **Chain-of-Thought RAG 구현**
  - 질문 분해 알고리즘
  - 단계별 검색 및 추론
  - 연쇄적 답변 합성

- 🔄 **고급 쿼리 개선**
  - 컨텍스트 기반 쿼리 리라이팅
  - 의도 분류 및 도메인 특화 검색
  - 검색 다양성 최적화

#### v3.86: MCTS-RAG 및 탐색 최적화
- 🔄 **Monte Carlo Tree Search RAG**
  - UCB 기반 검색 경로 선택
  - 병렬 시뮬레이션 실행
  - 최적 추론 경로 탐색

- 🔄 **성능 최적화**
  - 배치 추론 처리
  - 캐싱 및 메모이제이션
  - GPU 가속 추론

#### v3.87: 피드백 통합 및 자동 학습
- 🔄 **추론 품질 평가**
  - 단계별 추론 평가 지표
  - 사용자 만족도 기반 학습
  - A/B 테스트 프레임워크

- 🔄 **자동 튜닝 시스템**
  - 하이퍼파라미터 자동 최적화
  - 추론 패턴 학습 및 개선
  - 실시간 성능 모니터링

#### v3.88: WebUI 통합 및 시각화
- 🔄 **추론 과정 시각화**
  - 단계별 추론 트리 표시
  - 검색 결과 관련성 히트맵
  - 실시간 추론 진행 상황

- 🔄 **인터랙티브 추론 제어**
  - 사용자 개입 가능한 추론
  - 추론 모드 동적 전환
  - 중간 결과 확인 및 수정

#### v3.89: 도메인 특화 및 확장
- 🔄 **신약개발 특화 추론**
  - 임상시험 데이터 추론 패턴
  - 분자 구조 기반 추론
  - 규제 가이드라인 참조 추론

- 🔄 **멀티모달 RAG**
  - 이미지 + 텍스트 통합 검색
  - 화학 구조식 이해
  - 표 및 그래프 데이터 추론

#### v3.90: 완전 자동화 및 최적화
- 🔄 **완전 자동화 추론**
  - 질문 유형별 최적 추론 모드 자동 선택
  - 실시간 성능 기반 모드 전환
  - 사용자 피드백 기반 지속 학습

- 🔄 **Production Ready**
  - 고가용성 배포 시스템
  - 스케일링 자동화
  - 모니터링 및 알림 시스템

### 기존 피드백 시스템 유지 및 확장

#### 피드백 데이터베이스 스키마 (기존 유지)
```python
{
    "id": "unique_feedback_id",
    "question_embedding": [512],  # mxbai-embed-large로 차원 조정
    "answer_embedding": [512],
    "reasoning_mode": "self_rag|cot_rag|mcts_rag|normal",
    "reasoning_steps": 3,
    "search_iterations": 2,
    "feedback_type": "positive|negative",
    "question_text": "원본 질문 텍스트",
    "answer_text": "원본 응답 텍스트",
    "timestamp": "2025-01-03T12:00:00Z",
    "session_id": "대화_세션_ID",
    "user_id": "사용자_ID_해시",
    "context_sources": ["참조된 RAG 소스들"],
    "model_version": "gemma3-12b",
    "response_time": 8.5,  # 추론 포함 응답 시간
    "confidence_score": 0.91,
    "reasoning_quality": 0.88,  # 추론 품질 점수 (신규)
    "search_effectiveness": 0.92  # 검색 효과성 점수 (신규)
}
```

#### 중복 피드백 방지 (v3.81 기능 유지)
- 벡터 유사도 검사 (임계값 0.95)
- 추론 모드별 별도 중복 검사
- 추론 품질 고려한 중복 판단

## 📚 시스템 문서

### 포괄적 문서 세트
- **📋 [문서 개요](./docs/README.md)** - 전체 문서 가이드 및 빠른 시작
- **🏗️ [시스템 아키텍처](./docs/System_Architecture_Documentation.md)** - 마이크로서비스 구조 및 컴포넌트 설계
- **🔗 [API 문서](./docs/API_Documentation.md)** - 완전한 REST API 레퍼런스 (7개 API 그룹)
- **🧠 [Reasoning RAG 설계서](./docs/Reasoning_RAG_API_Specification.md)** - v3.84+ 고급 추론 시스템 명세

### 문서 활용법
- **개발자**: 시스템 아키텍처 → API 문서 → Reasoning RAG 설계서
- **연구자**: 프로젝트 메인 문서 → API 문서 → 고급 기능
- **관리자**: 시스템 아키텍처 → 메인 문서 (설정/모니터링)

### API 문서 하이라이트
- **7개 주요 API 그룹**: Chat, System, RAG, Feedback, MCP, Session
- **완전한 예제 코드**: cURL, JavaScript, Python
- **WebSocket 지원**: 실시간 스트리밍
- **고급 기능**: 2단계 리랭킹, 피드백 시스템, MCP 통합

## 📈 향후 확장

### 완료된 기능 (v3.79-v3.83) ✅
- ✅ 피드백 벡터 저장소 구현 완료
- ✅ 실시간 피드백 수집 및 알림 시스템 완료
- ✅ 중복 피드백 방지 시스템 완료
- ✅ Milvus 웹 UI 통합 및 Attu 관리 인터페이스 완료

### 단기 목표 (v3.84-v3.87) - Reasoning RAG 구현
- 🔄 ReasoningRAGPipeline 클래스 및 Self-RAG 기본 패턴
- 🔄 PyMilvus BGE Reranker 통합 완성
- 🔄 CoT-RAG 및 MCTS-RAG 패턴 구현
- 🔄 추론 품질 평가 및 자동 튜닝 시스템

### 중기 목표 (v3.88-v3.90) - 완전 통합 및 최적화
- 🔄 WebUI 추론 과정 시각화 및 인터랙티브 제어
- 🔄 신약개발 특화 추론 및 멀티모달 RAG
- 🔄 완전 자동화 추론 시스템
- 🔄 Production Ready 배포 및 모니터링

### 장기 목표 (v3.91+) - 고도화 및 확장
- 🔄 Gemma 파인튜닝 파이프라인 구축
- 🔄 다중 모델 앙상블 및 동적 선택
- 🔄 개인화된 응답 생성
- 🔄 연구 도메인별 전문화

### 기존 계획된 기능
- 실제 DrugBank/OpenTargets API 연결
- 캐싱 시스템 구현
- 실시간 분석 대시보드
- 다국어 지원 확장

### 장기 로드맵
- **Q1 2025**: 사용자 경험 완성, 바이오 데이터 기초 통합
- **Q2 2025**: 고급 분석 도구, 멀티 사용자 지원
- **Q3 2025**: 클라우드 배포, 엔터프라이즈 기능
- **Q4 2025**: AI 모델 파인튜닝, 특화 기능 완성

---

### 버전 히스토리

- **v3.84**: Reasoning RAG 시스템 계획 완성 - rule_2.md 기반 Self/CoT/MCTS-RAG 통합 아키텍처 설계, PyMilvus BGE Reranker 통합 플랜, v3.84-v3.90 단계별 구현 로드맵 수립
- **v3.83**: Attu 관리 인터페이스 통합 완성 - Docker 기반 Milvus 웹 UI 관리 시스템, 포트 3000 Attu 서버 자동 시작/중지, 서버 매니저 통합 완료
- **v3.82**: 서버 관리자 시스템 완성 - 벡터 데이터베이스 상태 자동 확인, 웹 UI 주소 표시 개선, Swagger UI 접속 정보 강화, 피드백 오류 수정 완료
- **v3.81**: 피드백 중복 검사 시스템 완성 - 벡터 유사도 기반 중복 피드백 자동 감지, 중복 저장 방지, Milvus 웹 UI 데이터 시각화 확인 완료
- **v3.80**: Milvus 웹 UI 통합 및 피드백 시스템 완성 - Docker Compose Milvus 서버, 웹 UI 관리 시스템, 피드백 벡터 저장소, 실시간 알림 완성
- **v3.79**: AI 학습 및 피드백 시스템 설계 완성 - 벡터 데이터베이스 스키마, Gemma 파인튜닝 계획, 피드백 기반 RAG 개선 전략 수립
- **v3.78**: WebUI 사용자 경험 대폭 개선 - 응답 피드백 시스템(썸업/썸다운), 클립보드 복사 기능, 인터랙티브 액션 버튼 추가
- **v3.77**: PyMilvus 통합 Reranker 완성 - BGE Reranker 2단계 검색 아키텍처, API 테스트 시스템, Swagger 문서 완전 업데이트
- **v3.76**: CLAUDE.md 구조 최적화 및 중복 제거 완료

---

**GAIA-BT v3.84** - 신약개발 연구의 새로운 패러다임 🧬✨