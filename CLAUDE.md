# GAIA-BT v3.82 - 신약개발 AI 연구 어시스턴트

## 📋 프로젝트 개요

GAIA-BT는 Ollama LLM과 MCP(Model Context Protocol)를 활용한 신약개발 전문 AI 연구 어시스턴트 시스템입니다.

## 🎯 현재 상태 - Production Ready ✅

- **개발 상태**: 완전 완성 (100% 완료)
- **배포 상태**: Production Ready
- **접속 정보**: 
  - **WebUI**: http://localhost:3003 (Next.js Frontend)
  - **API**: http://localhost:8000 (FastAPI Backend) 
  - **API 문서**: http://localhost:8000/docs (Swagger UI)
  - **벡터 DB 웹 UI**: http://localhost:9091/webui (Milvus 관리 인터페이스)

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

## 🧠 AI 학습 및 피드백 시스템 상세 계획

### 벡터 데이터베이스 스키마 설계

#### 피드백 컬렉션 (feedback_collection)
```python
{
    "id": "unique_feedback_id",
    "question_embedding": [768차원 벡터],  # 사용자 질문 임베딩
    "answer_embedding": [768차원 벡터],    # AI 응답 임베딩  
    "feedback_type": "positive|negative",  # 썸업/썸다운
    "question_text": "원본 질문 텍스트",
    "answer_text": "원본 응답 텍스트",
    "timestamp": "2025-01-03T12:00:00Z",
    "session_id": "대화_세션_ID",
    "user_id": "사용자_ID_해시",
    "context_sources": ["참조된 RAG 소스들"],
    "model_version": "gemma3-12b",
    "response_time": 3.2,  # 응답 생성 시간
    "confidence_score": 0.85  # 모델 자신감 점수
}
```

#### 질문-응답 쌍 컬렉션 (qa_pairs_collection)
```python
{
    "id": "unique_qa_id", 
    "question_embedding": [768차원 벡터],
    "answer_embedding": [768차원 벡터],
    "question_text": "원본 질문",
    "answer_text": "원본 응답",
    "positive_feedback_count": 5,
    "negative_feedback_count": 1,
    "quality_score": 0.83,  # 계산된 품질 점수
    "is_training_candidate": true,  # 파인튜닝 후보 여부
    "domain_tags": ["EGFR", "oncology", "clinical_trial"]
}
```

### 피드백 기반 RAG 개선 전략

#### 1. 부정 피드백 패턴 학습
- **벡터 유사성 분석**: 부정 피드백이 많은 질문들의 임베딩 클러스터 식별
- **응답 품질 예측**: 새로운 질문이 부정 패턴과 유사한지 사전 검증
- **동적 리랭킹**: 부정 피드백 패턴과 유사한 검색 결과는 우선순위 하향 조정

#### 2. 긍정 피드백 강화
- **고품질 응답 우선**: 썸업이 많은 응답과 유사한 패턴 우선 검색
- **컨텍스트 최적화**: 긍정 피드백이 많은 RAG 소스 조합 학습
- **응답 템플릿 개선**: 높은 평가를 받은 응답 구조 분석 및 적용

#### 3. 실시간 피드백 적용
- **즉시 반영**: 피드백 받은 질문-응답 쌍을 벡터 DB에 즉시 저장
- **세션 내 학습**: 같은 대화 세션 내에서 이전 피드백 패턴 고려
- **점진적 개선**: 피드백 누적에 따른 응답 품질 지속적 향상

#### 4. 중복 피드백 방지 시스템 (v3.81 신규)
- **벡터 유사도 검사**: 질문 및 답변 임베딩 기반 중복 감지
- **유사도 임계값**: 0.95 이상 유사도 시 중복으로 판단하여 저장 방지
- **자동 중복 제거**: 중복 피드백 시도 시 기존 데이터 정보와 함께 안내 메시지 제공
- **데이터 품질 보장**: 고유한 피드백만 저장하여 학습 데이터 품질 향상

### Gemma 파인튜닝 데이터셋 구축

#### 데이터 필터링 기준
1. **긍정 피드백 비율**: 80% 이상 썸업을 받은 응답만 선별
2. **응답 품질 점수**: 0.8 이상의 계산된 품질 점수
3. **도메인 다양성**: 신약개발 전 영역의 균형 잡힌 분포
4. **응답 완성도**: 완전한 문장과 구조를 가진 응답

#### 파인튜닝 데이터 포맷
```json
{
  "instruction": "신약개발 전문 AI로서 다음 질문에 답변하세요.",
  "input": "EGFR 돌연변이 폐암의 1차 치료제는 무엇인가요?",
  "output": "EGFR 돌연변이 폐암의 1차 치료제로는...",
  "quality_score": 0.92,
  "feedback_count": 8,
  "domain": "oncology"
}
```

### 자동 품질 평가 시스템

#### 품질 점수 계산 알고리즘
```python
quality_score = (
    positive_feedback_ratio * 0.4 +
    response_coherence_score * 0.3 +
    domain_accuracy_score * 0.2 +
    user_engagement_score * 0.1
)
```

#### 실시간 평가 지표
- **피드백 비율**: 긍정/부정 피드백 비율
- **응답 일관성**: 임베딩 기반 의미적 일관성 점수
- **도메인 정확성**: 신약개발 전문 용어 및 내용 정확도
- **사용자 참여도**: 후속 질문, 복사 횟수 등

## 📈 향후 확장

### 단기 목표 (v3.79-v3.82)
- 피드백 벡터 저장소 구현
- 실시간 피드백 수집 및 알림 시스템
- 피드백 기반 RAG 개선 프로토타입
- 데이터 품질 평가 시스템

### 중기 목표 (v3.83-v3.90)
- Gemma 파인튜닝 파이프라인 구축
- 자동 품질 평가 시스템 완성
- A/B 테스트를 통한 개선 효과 검증
- 피드백 분석 대시보드

### 장기 목표 (v3.91+)
- 완전 자동화된 모델 개선 시스템
- 다중 모델 앙상블 및 동적 선택
- 개인화된 응답 생성
- 연구 도메인별 전문화

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

- **v3.82**: 서버 관리자 시스템 완성 - 벡터 데이터베이스 상태 자동 확인, 웹 UI 주소 표시 개선, Swagger UI 접속 정보 강화, 피드백 오류 수정 완료
- **v3.81**: 피드백 중복 검사 시스템 완성 - 벡터 유사도 기반 중복 피드백 자동 감지, 중복 저장 방지, Milvus 웹 UI 데이터 시각화 확인 완료
- **v3.80**: Milvus 웹 UI 통합 및 피드백 시스템 완성 - Docker Compose Milvus 서버, 웹 UI 관리 시스템, 피드백 벡터 저장소, 실시간 알림 완성
- **v3.79**: AI 학습 및 피드백 시스템 설계 완성 - 벡터 데이터베이스 스키마, Gemma 파인튜닝 계획, 피드백 기반 RAG 개선 전략 수립
- **v3.78**: WebUI 사용자 경험 대폭 개선 - 응답 피드백 시스템(썸업/썸다운), 클립보드 복사 기능, 인터랙티브 액션 버튼 추가
- **v3.77**: PyMilvus 통합 Reranker 완성 - BGE Reranker 2단계 검색 아키텍처, API 테스트 시스템, Swagger 문서 완전 업데이트
- **v3.76**: CLAUDE.md 구조 최적화 및 중복 제거 완료

---

**GAIA-BT v3.82** - 신약개발 연구의 새로운 패러다임 🧬✨