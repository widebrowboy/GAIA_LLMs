# GAIA-BT 신약개발 연구 시스템

Ollama LLM과 MCP(Model Context Protocol)를 활용한 신약개발 연구 및 분석 시스템입니다. GPU 가속, 병렬 처리, 피드백 루프, 그리고 ChEMBL/PubMed/PubTator3/ClinicalTrials.gov/Sequential Thinking 통합을 통해 높은 품질의 과학적 근거 기반 신약개발 분석을 제공합니다.

<div align="center">

**최신 버전: 2.0.0 (2025-06-12)**  
**신약개발 전문 AI 연구 어시스턴트**
</div>

## 🎯 주요 특징

### 신약개발 전문 AI 어시스턴트
- **타겟 발굴**: 분자 타겟 식별 및 검증
- **화합물 분석**: ChEMBL 기반 분자 구조 및 물리화학적 특성 분석
- **임상 연구**: 임상시험 데이터 및 개발 단계 분석
- **약물 상호작용**: 분자 수준 약물-타겟 상호작용 연구

### 고성능 연구 플랫폼
- **MCP 통합**: ChEMBL, Biomedical 데이터베이스, Sequential Thinking 데이터 접근
- **Deep Search**: 통합 연구 수행으로 포괄적 분석 제공
- **실시간 분석**: 최신 논문 및 임상시험 데이터 실시간 조회
- **과학적 근거**: 모든 답변에 참고문헌 및 데이터 소스 포함

## 📋 목차
- [시스템 요구사항](#시스템-요구사항)
- [빠른 시작](#빠른-시작)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [MCP 통합 기능](#mcp-통합-기능)
- [LLM 모델 선택 가이드](#llm-모델-선택-가이드)
- [신약개발 활용 사례](#신약개발-활용-사례)
- [출력 형식](#출력-형식)
- [고급 설정](#고급-설정)
- [문제 해결](#문제-해결)

## 🔧 시스템 요구사항

### 필수 환경
- **운영체제**: Ubuntu 24.04 이상 또는 macOS 12+
- **파이썬**: Python 3.13+ (비동기 기능 지원)
- **Ollama**: [Ollama](https://ollama.ai/) 0.2.1 이상

### 권장 환경
- **GPU**: NVIDIA GPU (CUDA 12.0+) 또는 Apple Silicon
- **메모리**: 16GB 이상 권장 (32GB 최적)
- **저장공간**: 20GB 이상 (모델 파일 포함)

## 🚀 빠른 시작

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/GAIA_LLMs.git
cd GAIA_LLMs

# 2. 의존성 설치
pip install -r requirements.txt

# 3. Ollama 모델 다운로드
ollama pull gemma3:latest

# 4. 챗봇 실행
python run_chatbot.py

# 5. MCP 활성화 (챗봇 내에서)
> /mcp start

# 6. 신약개발 질문하기
> 항암제 개발에서 분자 타겟팅 치료법의 원리를 설명해주세요
```

## 📦 설치 방법

### 1. 환경 설정
```bash
# 가상 환경 생성
python -m venv .venv
source .venv/bin/activate  # Linux/macOS

# 의존성 설치
pip install -r requirements.txt
```

### 2. Ollama 설정
```bash
# Ollama 설치
curl -fsSL https://ollama.com/install.sh | sh

# 권장 모델 설치 (성능 순)
ollama pull gemma3:latest        # 최고 성능 (권장)
ollama pull llama3.1:latest      # 균형잡힌 성능
ollama pull txgemma-predict:latest  # 특화 모델
```

### 3. 환경 변수 구성
```bash
cp .env.example .env
# .env 파일 편집하여 설정 조정
```

## 🎮 사용 방법

### 대화형 챗봇 실행
```bash
# 메인 챗봇 실행
python run_chatbot.py

# 또는 고급 모드
python main.py -i
```

### 주요 명령어

#### 기본 명령어
```bash
/help          # 도움말 표시
/mcp start     # MCP 서버 시작
/mcp status    # 연결 상태 확인
/model <name>  # AI 모델 변경
/debug         # 디버그 모드 토글
/exit          # 종료
```

#### MCP 연구 명령어
```bash
/mcp bioarticle <검색어>     # 논문 검색
/mcp biotrial <조건>        # 임상시험 검색
/mcp chembl molecule <분자> # 화학 분자 분석
/mcp think <문제>          # 단계별 추론
/mcp test deep            # Deep Search 테스트
```

### 배치 처리
```bash
# JSON 파일로 여러 질문 처리
python main.py -f questions.json

# 텍스트 파일 사용
python main.py -f questions.txt

# 피드백 설정과 함께
python main.py -f questions.json -d 3 -w 2
```

## 🔬 MCP 통합 기능

### 1. ChEMBL 화학 데이터베이스
- **분자 구조 분석**: SMILES, InChI 등 화학 구조 정보
- **물리화학적 특성**: 분자량, logP, 용해도 등
- **약물-타겟 상호작용**: 결합 친화도, IC50 값
- **개발 단계 정보**: 임상 단계 및 승인 상태

### 2. Biomedical 데이터베이스 통합
- **PubMed & PubTator3**: 최신 연구 논문 및 생의학 문헌 검색
- **ClinicalTrials.gov**: 임상시험 데이터 및 치료법 정보
- **유전체 변이 분석**: CIViC, ClinVar, COSMIC, dbSNP 등
- **바이오마커**: 진단, 예후, 치료 반응 바이오마커

### 3. Sequential Thinking
- **문제 분해**: 복잡한 연구 질문을 단계별로 분석
- **논리적 추론**: 체계적 사고 과정 추적
- **대안 탐색**: 다양한 접근법 검토
- **결론 도출**: 종합적 분석 결과

## 🤖 LLM 모델 선택 가이드

### 권장 모델 순위 (성능 기준)

| 순위 | 모델명 | 성능 | 메모리 요구량 | 신약개발 적합성 | 설치 명령어 |
|------|--------|------|---------------|----------------|-------------|
| 🥇 | **gemma3:latest** | ⭐⭐⭐⭐⭐ | 16GB | 최적 | `ollama pull gemma3:latest` |
| 🥈 | **llama3.1:latest** | ⭐⭐⭐⭐ | 12GB | 우수 | `ollama pull llama3.1:latest` |
| 🥉 | **txgemma-predict:latest** | ⭐⭐⭐⭐ | 14GB | 특화 | `ollama pull txgemma-predict:latest` |
| 4위 | **llama3:8b** | ⭐⭐⭐ | 8GB | 양호 | `ollama pull llama3:8b` |

### 모델별 특징

#### 🏆 Gemma3 (권장)
```bash
ollama pull gemma3:latest
```
- **장점**: 최고 성능, 정확한 과학적 분석, 구조화된 답변
- **적용**: 복합적 신약개발 질문, Deep Research, 전문 보고서 생성
- **메모리**: 16GB RAM 권장
- **속도**: 빠름 (GPU 가속 시)

#### 🥈 Llama3.1 (균형형)
```bash
ollama pull llama3.1:latest
```
- **장점**: 균형잡힌 성능, 안정적 응답, 다양한 주제 커버
- **적용**: 일반적 신약개발 질문, 교육용, 개념 설명
- **메모리**: 12GB RAM 권장
- **속도**: 중간

#### 🧬 TxGemma-Predict (특화형)
```bash
ollama pull txgemma-predict:latest
```
- **장점**: 생명과학 특화, 독성 예측, 분자 분석 특화
- **적용**: ADMET 예측, 독성 분석, 분자 설계
- **메모리**: 14GB RAM 권장
- **속도**: 중간

### 모델 선택 기준

#### 🎯 사용 목적별 추천

**🔬 전문 연구용**
- **Gemma3**: 논문 수준의 정확한 분석 필요시
- **TxGemma-Predict**: 독성/ADMET 분석 특화

**📚 학습/교육용**
- **Llama3.1**: 개념 이해, 기초 학습
- **Llama3:8b**: 빠른 응답이 필요한 경우

**⚡ 성능별 추천**

| 시스템 사양 | 권장 모델 | 성능 기대치 |
|-------------|-----------|-------------|
| **고성능** (32GB+, GPU) | Gemma3 | 최고 품질 답변 |
| **중급** (16GB, CPU) | Llama3.1 | 우수한 답변 |
| **기본** (8GB) | Llama3:8b | 기본적 답변 |

### 모델 변경 방법

#### 챗봇 실행 중 변경
```bash
# 현재 모델 확인
/model

# 모델 변경
/model gemma3:latest
/model llama3.1:latest
/model txgemma-predict:latest
```

#### 기본 모델 설정 (.env)
```bash
# .env 파일 편집
OLLAMA_MODEL="gemma3:latest"
```

### 성능 비교 테스트

#### 테스트 질문
```bash
# 복합적 신약개발 질문으로 모델 성능 비교
> EGFR 억제제의 내성 메커니즘과 차세대 치료 전략을 분석해주세요
```

#### 평가 기준
- ✅ **정확성**: 과학적 사실의 정확도
- ✅ **완성도**: 답변의 구조화 및 포괄성  
- ✅ **전문성**: 신약개발 전문 용어 및 개념 이해
- ✅ **참고문헌**: 신뢰할 수 있는 출처 제시

### 모델 최적화 팁

#### 🚀 성능 향상
```bash
# GPU 가속 활성화 (NVIDIA GPU)
export CUDA_VISIBLE_DEVICES=0

# 메모리 최적화
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
```

#### 🔧 문제 해결
```bash
# 모델 다운로드 실패 시
ollama pull gemma3:latest --insecure

# 메모리 부족 시
ollama pull llama3:8b  # 더 작은 모델 사용

# 속도 개선
ollama serve --models-path /fast-ssd/models
```

## 💊 신약개발 활용 사례

### 1. 타겟 발굴 및 검증
```bash
# 질문 예시
> 알츠하이머병 치료를 위한 새로운 분자 타겟은 무엇이 있나요?

# MCP 활용
/mcp bioarticle "Alzheimer drug targets 2024"
/mcp biotrial "Alzheimer disease"
/mcp think "Novel Alzheimer therapeutic targets"
```

### 2. 화합물 분석 및 최적화
```bash
# 질문 예시  
> 이 화합물의 구조-활성 관계를 분석해주세요: CC(C)CC(C(=O)O)N

# MCP 활용
/mcp chembl molecule "leucine"
/mcp smiles "CC(C)CC(C(=O)O)N"
/mcp bioarticle "structure activity relationship"
```

### 3. 임상시험 설계
```bash
# 질문 예시
> PD-1 억제제의 임상시험 설계 시 고려사항은 무엇인가요?

# MCP 활용
/mcp biotrial "PD-1 inhibitor"
/mcp bioarticle "PD-1 clinical trial design"
/mcp think "Clinical trial design considerations"
```

### 4. 약물 안전성 평가
```bash
# 질문 예시
> 새로운 키나제 억제제의 독성 프로파일을 어떻게 평가해야 하나요?

# MCP 활용
/mcp bioarticle "kinase inhibitor toxicity"
/mcp chembl molecule "kinase inhibitor"
/mcp think "Drug safety evaluation strategy"
```

## 📄 출력 형식

### 연구 보고서 구조
모든 연구 결과는 다음 형식으로 제공됩니다:

```markdown
# 신약개발 연구: [질문]

## 1. 문제 정의
[연구 문제 및 배경]

## 2. 핵심 내용
[이론, 개념, 원리]

## 3. 과학적 근거
[연구 결과, 데이터]

## 4. 화학 구조 및 분자 분석
[ChEMBL 데이터 활용 시]

## 5. 임상시험 및 개발 단계
[개발 현황 및 임상 데이터]

## 6. 결론 및 요약
[핵심 내용 정리]

## 7. 참고 문헌
[최소 2개 이상의 참고문헌]
```

### 저장 구조
```
research_outputs/
├── 20250612_143025_항암제개발/
│   ├── 20250612_143025_항암제개발.md
│   └── 20250612_143025_항암제개발_meta.json
```

## ⚙️ 고급 설정

### 환경 변수 설정 (.env)
```ini
# Ollama 설정
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="Gemma3:latest"

# 연구 품질 설정
MIN_RESPONSE_LENGTH=1000
MIN_REFERENCES=2
FEEDBACK_DEPTH=2
FEEDBACK_WIDTH=2

# 출력 설정
OUTPUT_DIR="./research_outputs"
```

### MCP 서버 구성 (mcp.json)
```json
{
  "mcpServers": {
    "chembl": {
      "command": "node",
      "args": ["./mcp/chembl/build/index.js"]
    },
    "biomcp": {
      "command": "npx",
      "args": ["biomcp"]
    },
    "sequential-thinking": {
      "command": "python",
      "args": ["./mcp/sequential-thinking/server.py"]
    }
  }
}
```

## 🔧 문제 해결

### 일반적인 문제

#### 1. Ollama 연결 실패
```bash
# Ollama 서버 확인
ollama serve

# 포트 확인
curl http://localhost:11434/api/version
```

#### 2. MCP 서버 오류
```bash
# MCP 상태 확인
./scripts/status_mcp_servers.sh

# 서버 재시작
./scripts/stop_mcp_servers.sh
./scripts/run_mcp_servers.sh
```

#### 3. 모델 응답 품질 개선
```bash
# 더 나은 모델 사용
/model gemma3:latest

# MCP 활성화
/mcp start

# 피드백 설정 조정
python main.py -d 3 -w 3
```

### 로그 확인
```bash
# MCP 서버 로그
tail -f .mcp_pids/*.log

# 시스템 로그
python main.py --debug
```

## 📚 추가 문서

- [QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md) - 5분 빠른 시작
- [DEEP_RESEARCH_USER_MANUAL.md](./DEEP_RESEARCH_USER_MANUAL.md) - 상세 사용자 매뉴얼
- [START_CHATBOT.md](./START_CHATBOT.md) - 챗봇 실행 가이드

## 🏗️ 프로젝트 구조

```
GAIA_LLMs/
├── app/                   # 메인 애플리케이션
│   ├── core/             # 핵심 비즈니스 로직
│   ├── cli/              # CLI 인터페이스
│   ├── api/              # API 클라이언트
│   └── utils/            # 유틸리티
├── docs/                  # 문서 통합
│   ├── guides/           # 사용자 가이드
│   └── manuals/          # 상세 매뉴얼
├── mcp/                   # MCP 통합
│   ├── biomcp/           # 생의학 연구 서버
│   ├── chembl/           # 화학 데이터 서버
│   └── sequential-thinking/ # 추론 서버
├── config/               # 설정 파일
├── scripts/              # 실행 스크립트
├── outputs/              # 연구 결과 출력
├── examples/             # 예제 및 데모
├── tests/                # 테스트 파일
├── run_chatbot.py       # 메인 실행 파일
└── main.py              # 고급 실행 파일
```

## 🎯 테스트 예제

### 신약개발 질문 예시
```bash
# 타겟 발굴
> "신약개발에서 분자 타겟 발굴의 주요 접근법은 무엇인가요?"

# 화합물 분석
> "이 화합물의 약물 유사성과 ADMET 특성을 평가해주세요"

# 임상시험
> "항암제 개발에서 바이오마커의 역할과 중요성은 무엇인가요?"

# 안전성 평가
> "전임상 독성시험의 주요 단계와 평가 항목은 무엇인가요?"
```

## 📄 라이선스

이 프로젝트는 MIT 라이선스에 따라 제공됩니다.

---

**GAIA-BT 신약개발 연구 시스템으로 더 정확하고 과학적인 신약개발 연구를 경험하세요!** 🧬🔬
