# GAIA-BT API Documentation v3.84

## 📋 개요

GAIA-BT는 신약개발 전문 AI 연구 어시스턴트 시스템으로, FastAPI 기반의 완전한 RESTful API를 제공합니다. 모든 기능이 API로 구현되어 있어 웹UI, CLI, 외부 시스템에서 동일하게 사용할 수 있습니다.

## 🌐 Base URL & 접속 정보

- **API 서버**: `http://localhost:8000`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **WebUI**: `http://localhost:3003`
- **Milvus 관리 UI**: `http://localhost:3000` (Attu)

## 🔗 API 엔드포인트 전체 목록

### 1. Chat API (`/api/chat/*`) - 대화형 AI 기능

#### 일반 채팅
```http
POST /api/chat/message
Content-Type: application/json

{
  "message": "EGFR 돌연변이 폐암의 1차 치료제는 무엇인가요?",
  "session_id": "session_123",
  "mode": "normal"
}
```

**응답:**
```json
{
  "response": "EGFR 돌연변이 폐암의 1차 치료제로는...",
  "session_id": "session_123",
  "timestamp": "2025-01-03T12:00:00Z",
  "model": "gemma3-12b"
}
```

#### 스트리밍 채팅
```http
POST /api/chat/stream
Content-Type: application/json

{
  "message": "임상시험 프로토콜을 설명해주세요",
  "session_id": "session_123",
  "stream": true
}
```

**응답:** Server-Sent Events (SSE) 스트림

#### 시스템 명령어
```http
POST /api/chat/command
Content-Type: application/json

{
  "command": "/mcp start",
  "session_id": "session_123"
}
```

#### WebSocket 연결
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/session_123');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('실시간 응답:', data.content);
};
```

### 2. System API (`/api/system/*`) - 시스템 관리

#### 시스템 정보 조회
```http
GET /api/system/info
```

**응답:**
```json
{
  "current_model": "gemma3-12b",
  "mode": "normal",
  "prompt_type": "default",
  "debug_mode": false,
  "version": "v3.84",
  "status": "ready"
}
```

#### 모델 관리
```http
# 사용 가능한 모델 목록
GET /api/system/models

# 상세한 모델 정보
GET /api/system/models/detailed

# 실행 중인 모델 목록
GET /api/system/models/running

# 특정 모델 시작
POST /api/system/models/gemma3-12b/start

# 특정 모델 중지
POST /api/system/models/gemma3-12b/stop

# 빠른 모델 전환
POST /api/system/models/switch/gemma3-12b

# 모든 모델 중지
POST /api/system/models/stop-all
```

#### 모드 및 설정 변경
```http
# 모드 변경 (normal/deep_research)
POST /api/system/mode/deep_research

# 프롬프트 타입 변경
POST /api/system/prompt
Content-Type: application/json
{
  "prompt_type": "clinical"
}

# 프롬프트 파일 리로드
POST /api/system/prompts/reload

# 디버그 모드 토글
POST /api/system/debug
```

#### 시스템 상태 및 시작
```http
# 시스템 상태 체크
GET /api/system/health

# 시스템 시작 시 모델 자동 시작
POST /api/system/startup

# 시작 시 Ollama 검증 결과
GET /api/system/startup-validation

# 시작 배너 정보
GET /api/system/startup-banner
```

### 3. RAG API (`/api/rag/*`) - RAG 시스템

#### 문서 관리
```http
# 문서 추가
POST /api/rag/documents
Content-Type: application/json

{
  "documents": [
    {
      "content": "EGFR 억제제는 비소세포폐암 치료에 효과적입니다...",
      "metadata": {
        "source": "clinical_guideline.pdf",
        "category": "oncology"
      }
    }
  ]
}

# 모든 문서 삭제
DELETE /api/rag/documents
```

#### RAG 쿼리 (리랭킹 지원)
```http
POST /api/rag/query
Content-Type: application/json

{
  "query": "EGFR 돌연변이 폐암의 치료법",
  "top_k": 5,
  "use_reranking": true,
  "top_k_initial": 20,
  "generate_answer": true
}
```

**응답:**
```json
{
  "query": "EGFR 돌연변이 폐암의 치료법",
  "answer": "EGFR 돌연변이 폐암의 주요 치료법은...",
  "sources": [
    {
      "content": "관련 문서 내용...",
      "metadata": {...},
      "score": 0.95,
      "rerank_score": 0.89
    }
  ],
  "retrieval_time": 0.15,
  "reranking_time": 0.08,
  "generation_time": 2.3
}
```

#### 문서 검색만 수행
```http
GET /api/rag/search?query=EGFR&top_k=10&use_reranking=true&top_k_initial=30
```

#### RAG 시스템 통계
```http
GET /api/rag/stats
```

**응답:**
```json
{
  "total_documents": 1250,
  "total_vectors": 1250,
  "collection_size": "45.2 MB",
  "embedding_model": "mxbai-embed-large",
  "dimension": 512,
  "index_type": "HNSW",
  "reranker_model": "BAAI/bge-reranker-v2-m3"
}
```

### 4. Feedback API (`/api/feedback/*`) - 피드백 시스템

#### 피드백 제출 (중복 검사 포함)
```http
POST /api/feedback/submit
Content-Type: application/json

{
  "question": "EGFR 돌연변이 폐암의 1차 치료제는 무엇인가요?",
  "answer": "EGFR 돌연변이 폐암의 1차 치료제로는 게피티닙...",
  "feedback_type": "positive",
  "check_duplicates": true,
  "similarity_threshold": 0.95,
  "session_id": "session_123",
  "user_id": "anonymous",
  "model_version": "gemma3-12b",
  "response_time": 3.2,
  "confidence_score": 0.85
}
```

**응답:**
```json
{
  "status": "success",
  "message": "피드백이 저장되었습니다.",
  "feedback_id": "feedback_456",
  "duplicate_check": {
    "performed": true,
    "duplicates_found": 0
  }
}
```

#### 유사한 피드백 검색
```http
POST /api/feedback/search
Content-Type: application/json

{
  "query": "EGFR 치료제",
  "limit": 5,
  "feedback_type": "positive"
}
```

#### 파인튜닝용 학습 데이터 조회
```http
POST /api/feedback/training-data
Content-Type: application/json

{
  "min_quality_score": 0.8,
  "limit": 100,
  "feedback_type": "positive"
}
```

#### 피드백 시스템 통계
```http
GET /api/feedback/stats
```

**응답:**
```json
{
  "total_feedback": 156,
  "positive_feedback": 128,
  "negative_feedback": 28,
  "average_quality_score": 0.82,
  "collection_size": "12.3 MB",
  "duplicates_prevented": 23
}
```

#### 기타 피드백 관리
```http
# 피드백 데이터 초기화
DELETE /api/feedback/reset

# 피드백 시스템 상태 확인
GET /api/feedback/health
```

### 5. MCP API (`/api/mcp/*`) - Database 검색

#### MCP 상태 관리
```http
# MCP 상태 조회
GET /api/mcp/status

# MCP 시작 (Deep Research 모드)
POST /api/mcp/start

# MCP 중지
POST /api/mcp/stop

# 사용 가능한 MCP 서버 목록
GET /api/mcp/servers
```

**MCP 서버 목록:**
```json
{
  "servers": [
    {
      "name": "biomcp",
      "description": "생명과학 전용 MCP 서버",
      "status": "active"
    },
    {
      "name": "drugbank",
      "description": "DrugBank 약물 데이터베이스",
      "status": "active"
    },
    {
      "name": "opentargets", 
      "description": "OpenTargets 유전자-질병 연관성",
      "status": "active"
    },
    {
      "name": "chembl",
      "description": "ChEMBL 화합물 데이터베이스", 
      "status": "active"
    },
    {
      "name": "pubmed",
      "description": "PubMed 학술 논문 검색",
      "status": "active"
    }
  ]
}
```

#### MCP 명령 실행
```http
POST /api/mcp/command
Content-Type: application/json

{
  "command": "search_drugbank",
  "parameters": {
    "query": "gefitinib",
    "limit": 10
  }
}
```

#### MCP 출력 표시 토글
```http
POST /api/mcp/toggle-output
```

### 6. Session API (`/api/session/*`) - 세션 관리

#### 세션 관리
```http
# 새 세션 생성
POST /api/session/create
Content-Type: application/json
{
  "title": "EGFR 치료제 연구",
  "mode": "normal"
}

# 세션 정보 조회
GET /api/session/session_123

# 모든 세션 목록 조회
GET /api/session/

# 세션 삭제
DELETE /api/session/session_123
```

### 7. 기본 엔드포인트

#### 서버 상태
```http
# API 루트 정보
GET /

# 서버 상태 확인
GET /health
HEAD /health
```

**응답:**
```json
{
  "status": "healthy",
  "version": "v3.84",
  "timestamp": "2025-01-03T12:00:00Z",
  "services": {
    "ollama": "connected",
    "milvus": "connected", 
    "mcp": "ready"
  }
}
```

## 🔧 고급 기능

### 리랭킹 시스템 (v3.77+)

**2단계 검색 아키텍처:**
1. **Retrieval**: Milvus 벡터 검색 (k=20)
2. **Reranking**: BGE Cross Encoder (k=5)

```http
POST /api/rag/query
Content-Type: application/json

{
  "query": "신약개발 프로세스",
  "use_reranking": true,
  "top_k_initial": 30,  # 1단계 검색 결과 수
  "top_k": 5,           # 최종 결과 수
  "reranking_model": "BAAI/bge-reranker-v2-m3"
}
```

### 피드백 시스템 (v3.80+)

**벡터 기반 중복 검사:**
- 질문/답변 임베딩 유사도 계산
- 임계값 0.95 이상 시 중복으로 판단
- 자동 중복 방지 및 안내

```http
POST /api/feedback/submit
Content-Type: application/json

{
  "question": "질문 내용",
  "answer": "답변 내용",
  "feedback_type": "positive",
  "check_duplicates": true,        # 중복 검사 활성화
  "similarity_threshold": 0.95     # 유사도 임계값
}
```

### MCP 통합 (Deep Research)

**Sequential Thinking 4단계:**
1. **Problem Analysis**: 문제 분석 및 분해
2. **Data Collection**: 다중 데이터베이스 검색
3. **Evidence Synthesis**: 증거 통합 및 분석  
4. **Conclusion**: 결론 및 권고사항

```http
POST /api/mcp/start
# Deep Research 모드 활성화

POST /api/chat/message
Content-Type: application/json
{
  "message": "EGFR 표적 치료제의 최신 연구 동향을 분석해주세요",
  "session_id": "session_123",
  "mode": "deep_research"
}
```

## 📊 모니터링 및 통계

### 시스템 상태 모니터링
```bash
# 전체 상태 확인
curl http://localhost:8000/health

# 시스템 정보
curl http://localhost:8000/api/system/info

# RAG 통계
curl http://localhost:8000/api/rag/stats

# 피드백 통계  
curl http://localhost:8000/api/feedback/stats

# MCP 상태
curl http://localhost:8000/api/mcp/status
```

### 성능 지표
- **검색 속도**: 평균 150ms (벡터 검색)
- **리랭킹 속도**: 평균 80ms (Cross Encoder)
- **응답 생성**: 평균 2-5초 (모델 크기별)
- **스트리밍 지연**: 50-100ms (첫 토큰)

## 🔒 인증 및 보안

### CORS 설정
```python
# 허용된 오리진
origins = [
    "http://localhost:3003",  # WebUI
    "http://localhost:3000",  # 개발 서버
    "http://127.0.0.1:*"      # 로컬 접근
]
```

### 에러 처리
모든 API는 표준 HTTP 상태 코드를 사용합니다:

- **200**: 성공
- **400**: 잘못된 요청
- **404**: 리소스 없음
- **500**: 서버 내부 오류
- **503**: 서비스 사용 불가

```json
{
  "detail": "에러 메시지",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2025-01-03T12:00:00Z"
}
```

## 🧪 테스트 및 예제

### API 테스트 스크립트
```bash
# RAG API 테스트
python test_rag_api.py

# 리랭킹 기능 테스트
python test_reranking_api.py

# 통합 API 테스트
python test_api_integration.py

# 모드 전환 테스트
python test_mode_switch_api.py
```

### cURL 예제
```bash
# 간단한 채팅
curl -X POST "http://localhost:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕하세요",
    "session_id": "test_session"
  }'

# RAG 쿼리 (리랭킹 포함)
curl -X POST "http://localhost:8000/api/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "신약개발 프로세스",
    "use_reranking": true,
    "top_k": 5,
    "generate_answer": true
  }'

# 피드백 제출
curl -X POST "http://localhost:8000/api/feedback/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "테스트 질문",
    "answer": "테스트 답변",
    "feedback_type": "positive"
  }'
```

## 🚀 향후 계획 (v3.84+)

### Reasoning RAG API (v3.84 계획)
```http
# 추론 기반 RAG 쿼리
POST /api/reasoning-rag/query
Content-Type: application/json

{
  "query": "복잡한 연구 질문",
  "reasoning_mode": "self_rag",  # self_rag, cot_rag, mcts_rag
  "max_iterations": 3,
  "confidence_threshold": 0.8
}
```

### 추론 과정 스트리밍 (v3.88 계획)
```javascript
// WebSocket으로 실시간 추론 과정 확인
const ws = new WebSocket('ws://localhost:8000/ws/reasoning/session_123');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'reasoning_step') {
    console.log('추론 단계:', data.step, data.content);
  }
};
```

---

**GAIA-BT v3.84** - 신약개발 연구를 위한 완전한 API 생태계 🧬✨

이 문서는 GAIA-BT 시스템의 모든 API 기능을 포괄적으로 다루며, 개발자와 연구자가 시스템을 효과적으로 활용할 수 있도록 구성되었습니다.