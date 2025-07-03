# GAIA-BT Documentation v3.84

## 📚 문서 개요

GAIA-BT (Generative AI for Advanced Biomedical Technologies) 시스템의 포괄적인 문서 모음입니다. 신약개발 전문 AI 연구 어시스턴트의 모든 기능과 구조를 상세히 설명합니다.

## 📑 문서 목록

### 1. 🏗️ [시스템 아키텍처 문서](./System_Architecture_Documentation.md)
- **전체 시스템 구조** - 마이크로서비스 아키텍처 설계
- **컴포넌트 간 상호작용** - 데이터 플로우 및 통신 구조
- **기술 스택** - Frontend, Backend, AI, Database 계층
- **보안 및 성능** - 인증, 모니터링, 최적화 전략
- **확장성 계획** - 향후 마이크로서비스 분리 방안

### 2. 🔗 [API 문서](./API_Documentation.md)
- **완전한 REST API 레퍼런스** - 모든 엔드포인트 상세 설명
- **7개 주요 API 그룹** - Chat, System, RAG, Feedback, MCP, Session
- **실제 사용 예제** - cURL, JavaScript, Python 코드 샘플
- **WebSocket 지원** - 실시간 스트리밍 통신
- **고급 기능** - 리랭킹, 피드백 시스템, MCP 통합

### 3. 🧠 [Reasoning RAG API 설계서](./Reasoning_RAG_API_Specification.md)
- **3단계 추론 아키텍처** - Self-RAG, CoT-RAG, MCTS-RAG
- **고급 검색 기능** - PyMilvus BGE Reranker 통합
- **스트리밍 추론** - 실시간 추론 과정 확인
- **성능 모니터링** - 벤치마크 및 A/B 테스트
- **v3.84+ 구현 계획** - 단계별 개발 로드맵

### 4. 📋 [프로젝트 메인 문서](../CLAUDE.md)
- **현재 시스템 상태** - Production Ready 기능 목록
- **사용 가이드** - 설치, 실행, 사용법
- **기술 스택 상세** - AI, RAG, Vector DB 구성
- **버전 히스토리** - v3.81까지의 발전 과정
- **향후 계획** - Reasoning RAG 통합 로드맵

## 🎯 문서 사용 가이드

### 👩‍💻 개발자용
1. **[시스템 아키텍처](./System_Architecture_Documentation.md)** - 전체 구조 이해
2. **[API 문서](./API_Documentation.md)** - 구체적인 구현 방법
3. **[Reasoning RAG 설계서](./Reasoning_RAG_API_Specification.md)** - 고급 기능 개발

### 🔬 연구자용
1. **[프로젝트 메인 문서](../CLAUDE.md)** - 기능 개요 및 사용법
2. **[API 문서](./API_Documentation.md)** - 연구 도구로서의 활용
3. **[Reasoning RAG 설계서](./Reasoning_RAG_API_Specification.md)** - 고급 추론 기능

### 🎛️ 관리자용
1. **[시스템 아키텍처](./System_Architecture_Documentation.md)** - 배포 및 운영
2. **[프로젝트 메인 문서](../CLAUDE.md)** - 설정 및 모니터링

## 🚀 빠른 시작

### 1. 시스템 실행
```bash
# 모든 서버 시작
./scripts/server_manager.sh start-all

# 상태 확인
./scripts/server_manager.sh status
```

### 2. 주요 접속 주소
- **WebUI**: http://localhost:3003
- **API 문서**: http://localhost:8000/docs
- **Milvus 관리**: http://localhost:3000

### 3. API 테스트
```bash
# 간단한 채팅 테스트
curl -X POST "http://localhost:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요", "session_id": "test"}'

# RAG 쿼리 테스트
curl -X POST "http://localhost:8000/api/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "EGFR 치료제", "use_reranking": true}'
```

## 🔧 주요 기능

### ✅ 현재 구현된 기능 (v3.81)
- **실시간 스트리밍 채팅** - WebSocket 기반
- **2단계 RAG 시스템** - Milvus + BGE Reranker
- **피드백 시스템** - 벡터 기반 중복 검사
- **MCP 통합** - 5개 생의학 데이터베이스
- **모드 전환** - 일반 ↔ 딥리서치
- **Swagger 자동 문서화** - 완전한 API 레퍼런스

### 🔄 개발 중인 기능 (v3.84+)
- **Reasoning RAG** - Self/CoT/MCTS 추론 패턴
- **고급 피드백 학습** - Gemma 파인튜닝
- **시각화 인터페이스** - 추론 과정 표시
- **도메인 특화** - 신약개발 전용 기능

## 📊 시스템 통계

### 성능 지표
- **검색 속도**: 평균 150ms
- **리랭킹 속도**: 평균 80ms  
- **응답 생성**: 2-5초
- **스트리밍 지연**: 50-100ms

### 지원 모델
- **메인 LLM**: Gemma3-12B
- **임베딩**: mxbai-embed-large (512차원)
- **리랭커**: BAAI/bge-reranker-v2-m3

### 데이터베이스
- **벡터 DB**: Milvus Lite
- **피드백 저장소**: Milvus 컬렉션
- **문서 수**: 1,250+ 의학 문서

## 🎛️ 관리 도구

### Swagger UI
- **주소**: http://localhost:8000/docs
- **기능**: 
  - 전체 API 테스트
  - 자동 스키마 문서
  - 인터랙티브 예제

### Milvus 관리 (Attu)
- **주소**: http://localhost:3000
- **기능**:
  - 벡터 컬렉션 관리
  - 검색 성능 모니터링
  - 데이터 시각화

### 서버 관리 스크립트
```bash
# 전체 서버 관리
./scripts/server_manager.sh [start-all|stop|restart-all|status]

# Milvus 관리
./scripts/milvus_manager.sh [start|stop|webui|status]
```

## 🔍 문제해결

### 자주 발생하는 문제
1. **포트 충돌** - `./scripts/server_manager.sh clean-ports`
2. **Ollama 연결 실패** - Ollama 서비스 상태 확인
3. **Milvus 연결 오류** - Docker 컨테이너 상태 확인

### 로그 확인
```bash
# API 서버 로그
tail -f /tmp/gaia-bt-api.log

# WebUI 로그  
tail -f /tmp/gaia-bt-webui.log

# Milvus 로그
./scripts/milvus_manager.sh logs
```

### 상태 점검
```bash
# 전체 시스템 상태
curl http://localhost:8000/health

# RAG 시스템 통계
curl http://localhost:8000/api/rag/stats

# 피드백 시스템 통계
curl http://localhost:8000/api/feedback/stats
```

## 🤝 기여 방법

### 개발 환경 설정
```bash
# Python 가상환경
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# WebUI 개발
cd gaia_chat
npm install
npm run dev
```

### 코딩 규칙
- **TypeScript** 100% 적용
- **FastAPI** 표준 구조 따르기
- **테스트 코드** 필수 작성
- **API 문서** 자동 생성

### 버전 관리
- **형식**: `GAIA-BT v3.X - [변경사항 요약]`
- **커밋 메시지**: 상세한 변경 내용 기록
- **브랜치**: `webui` 브랜치 사용

## 📞 지원 및 문의

### 기술 지원
- **GitHub Issues**: 버그 리포트 및 기능 요청
- **API 문서**: http://localhost:8000/docs
- **시스템 로그**: `/tmp/gaia-bt-*.log`

### 커뮤니티
- **개발자 가이드**: [시스템 아키텍처](./System_Architecture_Documentation.md)
- **API 레퍼런스**: [API 문서](./API_Documentation.md)
- **고급 기능**: [Reasoning RAG](./Reasoning_RAG_API_Specification.md)

## 🔮 향후 계획

### 단기 목표 (Q1 2025)
- ✅ Reasoning RAG 기본 인프라 (v3.84)
- 🔄 CoT-RAG 및 다단계 추론 (v3.85)
- 🔄 MCTS-RAG 및 성능 최적화 (v3.86)

### 중기 목표 (Q2-Q3 2025)
- 🔄 WebUI 통합 및 시각화 (v3.88)
- 🔄 도메인 특화 기능 (v3.89)
- 🔄 완전 자동화 시스템 (v3.90)

### 장기 목표 (Q4 2025+)
- 🔄 Gemma 파인튜닝 시스템
- 🔄 다중 모델 앙상블
- 🔄 개인화된 연구 어시스턴트
- 🔄 클라우드 배포 및 엔터프라이즈 기능

---

**GAIA-BT Documentation v3.84** - 신약개발 연구를 위한 완전한 가이드 📚🧬✨

이 문서들은 GAIA-BT 시스템의 모든 측면을 다루며, 개발자, 연구자, 관리자가 시스템을 효과적으로 이해하고 활용할 수 있도록 구성되었습니다.