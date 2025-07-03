# Reasoning RAG API Specification v3.84+

## 📋 개요

Reasoning RAG API는 GAIA-BT v3.84부터 구현될 예정인 고급 추론 기반 검색 증강 생성 시스템입니다. Self-RAG, CoT-RAG, MCTS-RAG 패턴을 통합하여 복잡한 신약개발 질문에 대한 다단계 추론을 제공합니다.

## 🎯 핵심 기능

### 1. **Multi-Pattern Reasoning**
- **Self-RAG**: 자기반성 기반 반복적 검색
- **CoT-RAG**: 사고의 연쇄 기반 단계별 추론
- **MCTS-RAG**: 몬테카를로 트리 탐색 기반 최적 경로 찾기

### 2. **3단계 아키텍처**
- **Phase 1**: Reasoning Agent (추론 계획)
- **Phase 2**: Multi-Step Search (검색 최적화)
- **Phase 3**: Cross Encoder + Synthesis (답변 생성)

### 3. **고급 검색 기능**
- PyMilvus BGE Reranker 통합
- 반복적 쿼리 개선
- 컨텍스트 기반 검색 확장

## 🔗 API 엔드포인트 설계

### Base URL
```
http://localhost:8000/api/reasoning-rag
```

### 1. 추론 기반 쿼리 실행

#### Endpoint
```http
POST /api/reasoning-rag/query
```

#### Request Schema
```json
{
  "query": "EGFR 표적 치료제의 내성 기전과 극복 전략은 무엇인가요?",
  "reasoning_mode": "self_rag",
  "config": {
    "max_iterations": 3,
    "confidence_threshold": 0.8,
    "search_config": {
      "top_k_initial": 30,
      "top_k_final": 5,
      "use_reranking": true
    },
    "reasoning_config": {
      "reflection_threshold": 0.7,
      "support_threshold": 0.8,
      "max_depth": 4
    }
  },
  "session_id": "session_123",
  "stream": false
}
```

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | ✅ | 사용자 질문 |
| `reasoning_mode` | enum | ✅ | `self_rag`, `cot_rag`, `mcts_rag` |
| `config.max_iterations` | integer | ❌ | 최대 추론 반복 횟수 (기본값: 3) |
| `config.confidence_threshold` | float | ❌ | 신뢰도 임계값 (기본값: 0.8) |
| `config.search_config` | object | ❌ | 검색 설정 |
| `config.reasoning_config` | object | ❌ | 추론 설정 |
| `session_id` | string | ❌ | 세션 ID |
| `stream` | boolean | ❌ | 스트리밍 여부 (기본값: false) |

#### Response Schema
```json
{
  "query": "EGFR 표적 치료제의 내성 기전과 극복 전략은 무엇인가요?",
  "reasoning_mode": "self_rag",
  "answer": "EGFR 표적 치료제의 내성 기전은 다음과 같이 분류됩니다...",
  "reasoning_trace": [
    {
      "step": 1,
      "type": "question_analysis",
      "content": "질문을 3개 하위 문제로 분해: 1) 내성 기전, 2) 현재 치료법, 3) 극복 전략",
      "timestamp": "2025-01-03T12:00:01Z"
    },
    {
      "step": 2,
      "type": "retrieval",
      "sub_query": "EGFR 돌연변이 내성 기전",
      "search_results": [
        {
          "content": "T790M 돌연변이는 가장 흔한 EGFR 내성 기전으로...",
          "score": 0.92,
          "rerank_score": 0.89,
          "source": "nature_review_2023.pdf"
        }
      ],
      "relevance_score": 0.85,
      "timestamp": "2025-01-03T12:00:02Z"
    },
    {
      "step": 3,
      "type": "reflection",
      "content": "검색된 정보가 T790M 돌연변이에 집중되어 있음. C797S 돌연변이에 대한 추가 검색 필요",
      "decision": "retrieve_more",
      "timestamp": "2025-01-03T12:00:03Z"
    }
  ],
  "evidence_sources": [
    {
      "content": "관련 문서 내용...",
      "metadata": {
        "source": "clinical_oncology_2024.pdf",
        "page": 15,
        "category": "oncology"
      },
      "score": 0.94,
      "rerank_score": 0.91,
      "used_in_step": 2
    }
  ],
  "metrics": {
    "total_iterations": 3,
    "total_retrievals": 4,
    "final_confidence": 0.89,
    "reasoning_quality": 0.86,
    "search_effectiveness": 0.92,
    "total_time": 8.5,
    "breakdown": {
      "reasoning_time": 2.1,
      "search_time": 3.2,
      "reranking_time": 1.1,
      "generation_time": 2.1
    }
  },
  "session_id": "session_123",
  "timestamp": "2025-01-03T12:00:10Z"
}
```

### 2. 추론 모드별 특화 엔드포인트

#### Self-RAG 실행
```http
POST /api/reasoning-rag/self-rag
Content-Type: application/json

{
  "query": "신약개발 프로세스의 주요 단계와 각 단계별 위험 요소",
  "max_iterations": 4,
  "reflection_tokens": ["[Retrieve]", "[Relevant]", "[Support]", "[Continue]"],
  "confidence_threshold": 0.85
}
```

#### CoT-RAG 실행
```http
POST /api/reasoning-rag/cot-rag
Content-Type: application/json

{
  "query": "mRNA 백신 개발 과정에서 고려해야 할 기술적 도전과제",
  "decomposition_strategy": "temporal",  # temporal, causal, hierarchical
  "max_steps": 5,
  "step_confidence_threshold": 0.8
}
```

#### MCTS-RAG 실행
```http
POST /api/reasoning-rag/mcts-rag
Content-Type: application/json

{
  "query": "항암제 병용요법의 최적 조합 설계 방법론",
  "exploration_config": {
    "c_puct": 1.4,
    "max_simulations": 100,
    "max_depth": 6
  },
  "evaluation_criteria": ["efficacy", "safety", "feasibility"]
}
```

### 3. 스트리밍 추론 과정

#### WebSocket 연결
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/reasoning-rag/session_123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'reasoning_start':
      console.log('추론 시작:', data.query, data.mode);
      break;
      
    case 'reasoning_step':
      console.log(`단계 ${data.step}:`, data.content);
      displayReasoningStep(data);
      break;
      
    case 'retrieval_result':
      console.log('검색 결과:', data.results.length, '개 문서');
      displaySearchResults(data.results);
      break;
      
    case 'reflection':
      console.log('반성:', data.decision, data.reasoning);
      break;
      
    case 'partial_answer':
      console.log('부분 답변:', data.content);
      updateAnswer(data.content);
      break;
      
    case 'reasoning_complete':
      console.log('추론 완료');
      displayFinalAnswer(data.answer);
      break;
  }
};
```

#### Server-Sent Events (SSE)
```http
GET /api/reasoning-rag/stream/{session_id}?query=신약개발+프로세스
```

### 4. 추론 과정 조회 및 관리

#### 추론 기록 조회
```http
GET /api/reasoning-rag/trace/{session_id}
```

#### 특정 추론 단계 재실행
```http
POST /api/reasoning-rag/replay-step
Content-Type: application/json

{
  "session_id": "session_123",
  "step_number": 2,
  "alternative_query": "수정된 검색 쿼리"
}
```

#### 추론 중단 및 재개
```http
# 추론 중단
POST /api/reasoning-rag/pause/{session_id}

# 추론 재개
POST /api/reasoning-rag/resume/{session_id}

# 추론 취소
DELETE /api/reasoning-rag/cancel/{session_id}
```

### 5. 설정 및 모니터링

#### 추론 설정 관리
```http
# 기본 설정 조회
GET /api/reasoning-rag/config

# 설정 업데이트
PUT /api/reasoning-rag/config
Content-Type: application/json

{
  "default_mode": "self_rag",
  "max_iterations_global": 5,
  "timeout_seconds": 300,
  "cache_enabled": true,
  "performance_monitoring": true
}
```

#### 성능 통계
```http
GET /api/reasoning-rag/stats
```

**응답:**
```json
{
  "total_queries": 1524,
  "by_mode": {
    "self_rag": 856,
    "cot_rag": 445,
    "mcts_rag": 223
  },
  "performance": {
    "average_time": 7.2,
    "average_iterations": 2.8,
    "average_retrievals": 3.4,
    "success_rate": 0.94
  },
  "quality_metrics": {
    "average_confidence": 0.87,
    "average_reasoning_quality": 0.85,
    "user_satisfaction": 0.91
  }
}
```

## 🔧 고급 기능

### 1. 다중 모드 추론
```http
POST /api/reasoning-rag/multi-mode
Content-Type: application/json

{
  "query": "복잡한 연구 질문",
  "modes": ["self_rag", "cot_rag"],
  "combination_strategy": "voting",  # voting, weighted, cascade
  "confidence_weights": {
    "self_rag": 0.6,
    "cot_rag": 0.4
  }
}
```

### 2. 도메인 특화 추론
```http
POST /api/reasoning-rag/domain-specific
Content-Type: application/json

{
  "query": "임상시험 프로토콜 설계 질문",
  "domain": "clinical_trials",
  "specialization": {
    "evidence_hierarchy": ["rct", "meta_analysis", "cohort"],
    "regulatory_context": "fda",
    "therapeutic_area": "oncology"
  }
}
```

### 3. 협력적 추론
```http
POST /api/reasoning-rag/collaborative
Content-Type: application/json

{
  "query": "다학제적 접근이 필요한 질문",
  "agents": [
    {
      "role": "pharmacologist",
      "expertise": ["drug_metabolism", "pharmacokinetics"]
    },
    {
      "role": "clinician", 
      "expertise": ["patient_care", "treatment_protocols"]
    }
  ],
  "collaboration_mode": "parallel"  # parallel, sequential, debate
}
```

## 📊 모니터링 및 디버깅

### 추론 과정 시각화
```http
GET /api/reasoning-rag/visualize/{session_id}
```

### 성능 프로파일링
```http
GET /api/reasoning-rag/profile/{session_id}
```

### A/B 테스트 지원
```http
POST /api/reasoning-rag/ab-test
Content-Type: application/json

{
  "query": "테스트 질문",
  "variants": [
    {"mode": "self_rag", "config": {...}},
    {"mode": "cot_rag", "config": {...}}
  ],
  "evaluation_criteria": ["accuracy", "speed", "user_preference"]
}
```

## 🔒 에러 처리 및 예외

### 추론 실패 처리
```json
{
  "error": "reasoning_timeout",
  "message": "추론 과정이 제한 시간을 초과했습니다",
  "details": {
    "completed_steps": 2,
    "total_planned_steps": 4,
    "elapsed_time": 305.2,
    "timeout_limit": 300
  },
  "recovery_suggestions": [
    "timeout_limit을 늘려서 재시도",
    "max_iterations를 줄여서 재시도",
    "더 단순한 추론 모드 사용"
  ]
}
```

### 검색 실패 처리
```json
{
  "error": "insufficient_evidence",
  "message": "충분한 관련 문서를 찾을 수 없습니다",
  "details": {
    "search_attempts": 3,
    "best_relevance_score": 0.42,
    "required_threshold": 0.7
  },
  "fallback_strategy": "general_knowledge_response"
}
```

## 🧪 테스트 및 검증

### 단위 테스트
```bash
# 추론 모드별 테스트
python -m pytest tests/test_reasoning_rag.py::test_self_rag
python -m pytest tests/test_reasoning_rag.py::test_cot_rag
python -m pytest tests/test_reasoning_rag.py::test_mcts_rag

# 통합 테스트
python -m pytest tests/test_reasoning_integration.py

# 성능 테스트
python -m pytest tests/test_reasoning_performance.py
```

### 벤치마크 데이터셋
```http
POST /api/reasoning-rag/benchmark
Content-Type: application/json

{
  "dataset": "drug_discovery_qa",
  "mode": "self_rag",
  "metrics": ["accuracy", "completeness", "coherence"]
}
```

## 🚀 구현 일정

### v3.84 (Q1 2025)
- ✅ Self-RAG 기본 구현
- ✅ PyMilvus Reranker 통합
- ✅ 기본 API 엔드포인트

### v3.85 (Q1 2025)
- 🔄 CoT-RAG 구현
- 🔄 스트리밍 지원
- 🔄 성능 최적화

### v3.86 (Q2 2025)
- 🔄 MCTS-RAG 구현
- 🔄 다중 모드 추론
- 🔄 도메인 특화

### v3.87 (Q2 2025)
- 🔄 피드백 통합
- 🔄 자동 튜닝
- 🔄 A/B 테스트

### v3.88 (Q3 2025)
- 🔄 WebUI 통합
- 🔄 시각화 기능
- 🔄 협력적 추론

---

**Reasoning RAG API v3.84+** - 신약개발 연구를 위한 차세대 추론 시스템 🧠🔬

이 API 설계서는 GAIA-BT의 고급 추론 기능 구현을 위한 완전한 명세를 제공하며, 복잡한 신약개발 질문에 대한 체계적이고 정확한 답변을 생성할 수 있도록 설계되었습니다.