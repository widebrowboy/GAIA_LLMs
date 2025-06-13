# GAIA-BT 신약개발 연구 시스템

Ollama LLM과 MCP(Model Context Protocol)를 활용한 신약개발 연구 및 분석 시스템입니다. GPU 가속, 병렬 처리, 피드백 루프, 그리고 DrugBank/OpenTargets/ChEMBL/PubMed/ClinicalTrials.gov/BioRxiv/Sequential Thinking 통합을 통해 높은 품질의 과학적 근거 기반 신약개발 분석을 제공합니다.

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
- **통합 MCP 서버**: DrugBank, OpenTargets, ChEMBL, PubMed, ClinicalTrials.gov, BioMCP, BioRxiv/medRxiv, Sequential Thinking
- **스마트 Deep Search**: 질문 키워드 분석 기반 적응형 다중 데이터베이스 검색
- **실시간 분석**: 최신 논문, 임상시험, 약물-타겟 상호작용 데이터 실시간 조회
- **AI 통합 분석**: Sequential Thinking + 다중 데이터소스 조합으로 포괄적 연구 수행
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
# 기본 MCP 관리
/mcp start                 # MCP 서버 시작
/mcp status               # MCP 상태 확인

# DrugBank 약물 데이터베이스
/mcp drugbank search <약물명>          # 약물 검색
/mcp drugbank indication <적응증>      # 적응증별 약물 검색
/mcp drugbank interaction <drugbank_id> # 약물 상호작용

# OpenTargets 타겟-질병 연관성
/mcp opentargets targets <유전자>      # 타겟 검색
/mcp opentargets diseases <질병>       # 질병 검색
/mcp opentargets target_diseases <타겟ID> # 타겟-질병 연관성

# ChEMBL 화학 데이터베이스
/mcp chembl molecule <분자명>         # 분자 정보 검색
/mcp smiles <SMILES>                 # SMILES 구조 분석

# PubMed 과학 문헌 데이터베이스
/mcp pubmed search <검색어> <개수>     # 논문 검색
/mcp pubmed author <저자명> <개수>     # 저자별 논문 검색
/mcp pubmed details <PMID>           # 논문 상세 정보
/mcp pubmed related <PMID> <개수>     # 관련 논문 검색
/mcp pubmed citations <PMID>         # 인용 논문 검색

# ClinicalTrials.gov 임상시험 데이터베이스
/mcp clinical search <질병> <상태> <개수>  # 임상시험 검색
/mcp clinical details <NCT_ID>            # 시험 상세 정보
/mcp clinical sponsor <스폰서명> <개수>     # 스폰서별 시험 검색
/mcp clinical condition <조건> <개수>      # 조건별 시험 검색
/mcp clinical results <NCT_ID>            # 시험 결과 조회

# BioMCP 생의학 데이터베이스
/mcp bioarticle <검색어>              # 논문 검색
/mcp biotrial <조건>                 # 임상시험 검색

# BioRxiv 프리프린트 저장소
/mcp biorxiv recent <interval>       # 최근 프리프린트 검색
/mcp biorxiv search <날짜범위>        # 기간별 프리프린트 검색
/mcp biorxiv doi <DOI>               # DOI로 프리프린트 상세 정보

# Sequential Thinking AI 추론
/mcp think <문제>                    # 단계별 추론 분석

# Deep Research (새로운 기능)
/mcp deep_research <주제>            # 통합 심층 연구 (중복 제거 포함)

# 통합 테스트
/mcp test deep                       # Deep Search 통합 테스트
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

GAIA-BT는 9개의 전문 MCP 서버를 통합하여 포괄적인 신약개발 연구를 지원합니다.

### 1. 💊 DrugBank - 약물 데이터베이스
- **약물 검색 및 정보**: 15,000+ 승인된 약물 및 실험적 화합물
- **약물 상호작용**: 약물-약물, 약물-음식 상호작용 분석
- **적응증 매핑**: 질병별 치료제 검색 및 분석
- **타겟 정보**: 약물-타겟 관계 및 작용 메커니즘
- **ADMET 데이터**: 흡수, 분포, 대사, 배설, 독성 정보

```bash
# DrugBank 명령어 예제
/mcp drugbank search "aspirin"          # 아스피린 검색
/mcp drugbank indication "cancer"       # 암 치료제 검색
/mcp drugbank interaction "DB00945"     # 약물 상호작용 조회
```

### 2. 🎯 OpenTargets - 타겟-질병 연관성
- **타겟 발굴**: 60,000+ 유전자 타겟 정보
- **질병 연관성**: 27,000+ 질병과 타겟 간 연관성 분석
- **증거 기반 분석**: 유전학적, 약물학적, 병리학적 증거 통합
- **약물 재창출**: 기존 약물의 새로운 적응증 발굴
- **유전체 분석**: GWAS, 체세포 변이, 발현 데이터

```bash
# OpenTargets 명령어 예제
/mcp opentargets targets "BRCA1"        # BRCA1 타겟 정보
/mcp opentargets diseases "cancer"      # 암 관련 타겟 검색
/mcp opentargets target_diseases "ENSG00000012048"  # 타겟-질병 연관성
```

### 3. 🧪 ChEMBL - 화학 데이터베이스
- **분자 구조 분석**: SMILES, InChI 등 화학 구조 정보
- **물리화학적 특성**: 분자량, logP, 용해도 등
- **약물-타겟 상호작용**: 결합 친화도, IC50 값
- **개발 단계 정보**: 임상 단계 및 승인 상태
- **SAR 분석**: 구조-활성 관계 연구

```bash
# ChEMBL 명령어 예제
/mcp chembl molecule "aspirin"          # 분자 정보 검색
/mcp smiles "CC(=O)OC1=CC=CC=C1C(=O)O"  # SMILES 구조 분석
```

### 4. 📄 PubMed - 과학 문헌 데이터베이스
- **논문 검색**: 35M+ 의학 및 생명과학 논문 검색
- **저자 기반 검색**: 특정 연구자의 논문 검색
- **관련 논문 추천**: 논문 간 연관성 분석
- **인용 분석**: 논문 인용 관계 추적
- **상세 정보**: 초록, 저자, 저널, DOI 등 완전한 메타데이터

```bash
# PubMed 명령어 예제
/mcp pubmed search "immunotherapy cancer" 10    # 면역치료 암 논문 검색
/mcp pubmed author "John Smith" 5               # 저자별 논문 검색
/mcp pubmed details "PMID:12345678"             # 논문 상세 정보
/mcp pubmed related "PMID:12345678" 5           # 관련 논문 검색
/mcp pubmed citations "PMID:12345678"           # 인용 논문 검색
```

### 5. 🏥 ClinicalTrials.gov - 임상시험 데이터베이스
- **임상시험 검색**: 450,000+ 전 세계 임상시험 정보
- **조건별 검색**: 질병/조건별 임상시험 현황
- **스폰서별 검색**: 제약회사별 임상시험 추적
- **시험 단계 분석**: Phase I/II/III/IV 단계별 분석
- **결과 데이터**: 완료된 임상시험의 결과 및 부작용 정보

```bash
# ClinicalTrials 명령어 예제
/mcp clinical search "breast cancer" "RECRUITING" 10  # 모집 중인 유방암 시험
/mcp clinical details "NCT12345678"                   # 시험 상세 정보
/mcp clinical sponsor "Pfizer" 5                      # 스폰서별 시험 검색
/mcp clinical condition "Alzheimer" 10                # 조건별 시험 검색
/mcp clinical results "NCT12345678"                   # 시험 결과 조회
```

### 6. 📄 BioMCP - 생의학 데이터베이스 통합
- **유전체 변이 분석**: CIViC, ClinVar, COSMIC, dbSNP 등
- **바이오마커**: 진단, 예후, 치료 반응 바이오마커
- **통합 검색**: 다중 데이터베이스 통합 검색

```bash
# BioMCP 명령어 예제
/mcp bioarticle "immunotherapy cancer"  # 논문 검색
/mcp biotrial "breast cancer"           # 임상시험 검색
```

### 7. 📑 BioRxiv - 프리프린트 논문 저장소
- **bioRxiv & medRxiv**: 최신 프리프린트 논문 및 연구 동향
- **출판 전 연구**: 출판 전 최신 연구 결과 접근
- **신속한 정보**: 빠른 과학적 정보 획득 및 동향 파악
- **연구 추적**: DOI 기반 프리프린트 상세 정보 조회

```bash
# BioRxiv 명령어 예제
/mcp biorxiv recent 7                    # 최근 7일 프리프린트
/mcp biorxiv search "2024-12-01" "2024-12-12"  # 기간별 검색
/mcp biorxiv doi "10.1101/2024.12.01.123456"   # DOI 상세 정보
```

### 8. 🧠 Sequential Thinking - AI 추론
- **문제 분해**: 복잡한 연구 질문을 단계별로 분석
- **논리적 추론**: 체계적 사고 과정 추적
- **대안 탐색**: 다양한 접근법 검토
- **결론 도출**: 종합적 분석 결과

```bash
# Sequential Thinking 명령어 예제
/mcp think "새로운 항암제 개발 전략"   # 단계별 사고 분석
```

### 9. 📊 통합 Deep Search
질문 키워드를 자동 분석하여 관련 MCP 서버들을 지능적으로 선택하고 통합 검색을 수행합니다.

**키워드 기반 자동 매핑:**
- **약물 관련** → DrugBank + ChEMBL + PubMed
- **타겟 관련** → OpenTargets + ChEMBL + PubMed
- **질병 관련** → OpenTargets + PubMed + ClinicalTrials + BioRxiv
- **화학 관련** → ChEMBL + DrugBank + PubMed
- **임상 관련** → ClinicalTrials + PubMed + BioMCP
- **최신 연구** → PubMed + BioRxiv + BioMCP
- **모든 경우** → Sequential Thinking + PubMed + ClinicalTrials

**🔄 중복 제거 기능:**
- **지능형 중복 탐지**: 제목, PMID, NCT ID 기반 중복 식별
- **품질 기반 필터링**: 완성도 높은 결과만 유지
- **통합 결과 제공**: 최고 품질의 중복 제거된 통합 결과

**🤖 AI 통합 요약:**
- **종합 분석**: 모든 데이터 소스의 정보를 AI가 종합 분석
- **핵심 발견사항**: 주요 연구 결과 요약
- **임상적 의의**: 실용적 적용 가능성 분석
- **향후 연구 방향**: 추가 연구 제안

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

### 1. 통합 타겟-질병 연구
```bash
# 질문 예시
> BRCA1 타겟을 이용한 유방암 치료제 개발 전략을 분석해주세요

# 자동 Deep Search 수행 (질문만 입력하면 아래가 자동 실행됨)
🧠 Sequential Thinking: 연구 계획 수립
🎯 OpenTargets: BRCA1 타겟-질병 연관성 분석  
💊 DrugBank: BRCA1 관련 기존 치료제 검색
🧪 ChEMBL: BRCA1 화합물 상호작용 데이터
📄 BioMCP: 최신 BRCA1 유방암 연구 논문

# 개별 명령어로도 실행 가능
/mcp opentargets targets "BRCA1"
/mcp drugbank search "breast cancer"
/mcp bioarticle "BRCA1 breast cancer therapy"
```

### 2. 약물 재창출 연구
```bash
# 질문 예시  
> 아스피린의 새로운 적응증 가능성과 분자 메커니즘을 분석해주세요

# 자동 Deep Search 수행
🧠 Sequential Thinking: 약물 재창출 전략 분석
💊 DrugBank: 아스피린 약물 정보 및 상호작용  
🧪 ChEMBL: 아스피린 분자 구조 및 타겟 분석
📄 BioMCP: 아스피린 새로운 적응증 연구

# 개별 명령어 예제
/mcp drugbank search "aspirin"
/mcp drugbank interaction "DB00945"
/mcp chembl molecule "aspirin"
/mcp smiles "CC(=O)OC1=CC=CC=C1C(=O)O"
```

### 3. 신규 타겟 발굴
```bash
# 질문 예시
> 알츠하이머병 치료를 위한 새로운 타겟 발굴 전략을 제시해주세요

# 자동 Deep Search 수행
🧠 Sequential Thinking: 타겟 발굴 체계적 접근
🎯 OpenTargets: 알츠하이머 관련 타겟 및 질병 연관성
💊 DrugBank: 기존 알츠하이머 치료제 분석
📄 BioMCP: 최신 알츠하이머 타겟 연구

# 개별 명령어 예제
/mcp opentargets diseases "Alzheimer"
/mcp drugbank indication "Alzheimer"
/mcp think "Novel Alzheimer therapeutic targets"
```

### 4. 화합물 최적화 연구
```bash
# 질문 예시
> 새로운 키나제 억제제의 구조 최적화와 독성 평가 전략을 분석해주세요

# 자동 Deep Search 수행
🧠 Sequential Thinking: 구조 최적화 전략 수립
🧪 ChEMBL: 키나제 억제제 구조-활성 관계
💊 DrugBank: 키나제 억제제 안전성 프로파일
📄 BioMCP: 키나제 억제제 독성 평가 연구

# 개별 명령어 예제  
/mcp chembl molecule "kinase inhibitor"
/mcp drugbank indication "kinase"
/mcp bioarticle "kinase inhibitor toxicity SAR"
```

### 5. 임상시험 설계 지원
```bash
# 질문 예시
> 면역항암제 병용요법의 임상시험 설계 가이드라인을 제시해주세요

# 자동 Deep Search 수행
🧠 Sequential Thinking: 임상시험 설계 체계적 접근
📄 BioMCP: 면역항암제 임상시험 데이터 검색
🎯 OpenTargets: 면역치료 타겟 정보
💊 DrugBank: 면역항암제 약물 상호작용

# 개별 명령어 예제
/mcp biotrial "immunotherapy combination"
/mcp bioarticle "immunotherapy clinical trial design"
/mcp drugbank interaction "pembrolizumab"
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
