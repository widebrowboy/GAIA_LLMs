# GAIA-BT 신약개발 연구 시스템 - 빠른 시작 가이드

**5분 만에 신약개발 AI 연구 어시스턴트 시작하기** 🚀

## 📋 간단 버전 (3분)

### 1단계: 기본 설정
```bash
# 저장소 다운로드
git clone https://github.com/yourusername/GAIA_LLMs.git
cd GAIA_LLMs

# 의존성 설치
pip install -r requirements.txt

# Ollama 모델 설치
ollama pull gemma3:latest
```

### 2단계: 챗봇 실행
```bash
python run_chatbot.py
```

### 3단계: 바로 사용하기
```bash
# 챗봇에서 입력
> 항암제 개발에서 분자 타겟팅 치료법의 원리를 설명해주세요

# MCP 활성화 (고급 기능)
> /mcp start
> 신약개발에서 분자 타겟 발굴의 주요 접근법은 무엇인가요?
```

## 🔬 자세한 버전 (10분)

### 1단계: 환경 준비 (3분)

#### A. 프로젝트 설정
```bash
# 1. 저장소 복제
git clone https://github.com/yourusername/GAIA_LLMs.git
cd GAIA_LLMs

# 2. 가상환경 생성 (권장)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. 의존성 설치
pip install -r requirements.txt
```

#### B. Ollama 설정
```bash
# 1. Ollama 설치 (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# 2. 권장 LLM 모델 설치 (성능 순)
ollama pull gemma3:latest        # 🥇 최고 성능 (권장)
ollama pull llama3.1:latest      # 🥈 균형잡힌 성능  
ollama pull txgemma-predict:latest  # 🧬 신약개발 특화

# 3. 시스템 사양별 선택
# 고성능 (16GB+): gemma3:latest
# 중급 (12GB+): llama3.1:latest  
# 기본 (8GB+): llama3:8b
```

#### 모델 성능 비교
| 모델 | 메모리 | 신약개발 적합성 | 추천 용도 |
|------|--------|----------------|-----------|
| **gemma3:latest** | 16GB | ⭐⭐⭐⭐⭐ | 전문 연구, Deep Research |
| **llama3.1:latest** | 12GB | ⭐⭐⭐⭐ | 일반 질문, 교육용 |
| **txgemma-predict:latest** | 14GB | ⭐⭐⭐⭐ | 독성 예측, 분자 분석 |

```

#### C. 환경 변수 구성 (선택사항)
```bash
# 기본 설정 복사
cp .env.example .env

# 필요시 .env 파일 편집
nano .env
```

### 2단계: 시스템 실행 (2분)

#### A. 기본 챗봇 실행
```bash
# 메인 챗봇 실행
python run_chatbot.py

# 또는 고급 모드
python main.py -i
```

#### B. 시스템 확인
```bash
# 챗봇에서 다음 명령어 입력
> /help        # 도움말 확인
> /mcp status  # MCP 상태 확인
```

### 3단계: MCP 고급 기능 활성화 (3분)

#### A. MCP 서버 시작
```bash
# 챗봇에서 입력
> /mcp start
```

**예상 출력:**
```
MCP 서버를 시작하는 중...
✓ GAIA MCP 서버가 성공적으로 시작되었습니다.
✓ PubMed/PubTator3 서버가 연결되었습니다.
✓ ClinicalTrials.gov 서버가 연결되었습니다.
✓ 유전체 변이 DB 서버가 연결되었습니다.
✓ ChEMBL 서버가 연결되었습니다.
✓ Sequential Thinking 서버가 연결되었습니다.
```

#### B. 기능 테스트
```bash
# 1. 기본 테스트
> /mcp test deep

# 2. 개별 기능 테스트
> /mcp bioarticle "cancer drug development"
> /mcp chembl molecule "imatinib"
> /mcp think "drug discovery process"
```

### 4단계: 실제 연구 수행 (2분)

#### A. 신약개발 질문하기
```bash
# 타겟 발굴 관련
> 신약개발에서 분자 타겟 발굴의 주요 접근법은 무엇인가요?

# 화합물 분석 관련
> 항암제 개발에서 바이오마커의 역할과 중요성은 무엇인가요?

# 임상시험 관련
> 전임상 독성시험의 주요 단계와 평가 항목은 무엇인가요?
```

#### B. 결과 저장
```bash
# 답변 생성 후 저장 여부 묻는 프롬프트에서
y  # 저장하려면 'y' 입력
   # 저장하지 않으려면 Enter만 입력
```

## 🎯 즉시 사용 가능한 예제

### 신약개발 연구 질문 샘플

복사해서 바로 사용하세요:

```bash
# 🎯 타겟 발굴 및 검증
알츠하이머병 치료를 위한 새로운 분자 타겟은 무엇이 있나요?

# 🧬 화합물 분석 및 최적화
키나제 억제제의 구조-활성 관계를 어떻게 분석하나요?

# 🧪 임상시험 설계
PD-1 억제제의 임상시험 설계 시 고려사항은 무엇인가요?

# ⚠️ 약물 안전성 평가
새로운 항암제의 독성 프로파일을 어떻게 평가해야 하나요?

# 📊 바이오마커 활용
정밀의학에서 바이오마커의 역할과 개발 전략은 무엇인가요?
```

### MCP 고급 기능 예제

```bash
# 📚 논문 검색
/mcp bioarticle "CRISPR drug discovery"

# 🧪 임상시험 검색
/mcp biotrial "immunotherapy cancer"

# 🔬 분자 분석
/mcp chembl molecule "pembrolizumab"

# 🧠 단계별 분석
/mcp think "How to develop personalized cancer therapy"

# 🔍 통합 연구
/mcp research "CAR-T cell therapy development challenges"
```

## 📊 예상 결과 형태

### Deep Research 출력 예시:
```markdown
# 신약개발 연구: 항암제 개발에서 분자 타겟팅 치료법

## 1. 문제 정의
분자 타겟팅 치료법은 암세포의 특정 분자를 선택적으로 공격하여 정상 세포에 미치는 영향을 최소화하는 치료 전략입니다.

## 2. 핵심 내용 (이론, 개념, 원리)
### 분자 타겟팅의 원리
1. **선택성**: 암세포에만 존재하거나 과발현되는 타겟 선택
2. **특이성**: 타겟과 약물의 특이적 결합
3. **효능**: 최소 독성으로 최대 효과 달성

### 주요 타겟 유형
- **성장인자 수용체**: EGFR, HER2, VEGFR
- **키나제**: BCR-ABL, ALK, ROS1
- **면역 체크포인트**: PD-1, PD-L1, CTLA-4

## 3. 과학적 근거 (PubMed/ClinicalTrials.gov 연구 결과)
- **이매티닙**: CML 치료에서 90% 이상의 관해율 (Druker et al., 2006)
- **트라스투주맙**: HER2 양성 유방암에서 생존율 37% 향상 (Piccart-Gebhart et al., 2005)

## 4. 화학 구조 및 분자 분석 (ChEMBL 데이터)
### 이매티닙 (Imatinib)
- **분자식**: C29H31N7O
- **분자량**: 493.6 g/mol
- **작용기전**: BCR-ABL 키나제 억제

## 5. 임상시험 및 개발 단계
### 개발 과정
1. **타겟 발굴**: 분자생물학적 연구
2. **리드 최적화**: 구조-활성 관계 분석
3. **전임상 시험**: 독성 및 효능 평가
4. **임상시험**: Phase I-III 단계적 진행

## 6. 결론 및 요약
분자 타겟팅 치료법은 정밀의학의 핵심으로, 환자 맞춤형 치료를 가능하게 합니다.

## 7. 참고 문헌
1. Druker, B.J., et al. (2006). Five-year follow-up of patients receiving imatinib...
2. Piccart-Gebhart, M.J., et al. (2005). Trastuzumab after adjuvant chemotherapy...
```

## 🎯 성공 지표

테스트가 성공적으로 작동하면 다음과 같은 출력을 볼 수 있습니다:

### MCP Deep Search 과정:
```
🔍 MCP Deep Search 수행 중...
🔍 ✓ AI 분석 완료
🔍 ✓ 논문 검색 완료
🔍 ✓ 약물 분자 정보 검색 완료
🔍 ✓ Deep Search 완료 - 데이터 통합 중...
```

### 최종 응답 특징:
- ✅ 1000자 이상의 상세한 답변
- ✅ 화학 구조 정보 포함 (ChEMBL)
- ✅ 과학적 근거 제시 (PubMed/PubTator3/ClinicalTrials.gov)
- ✅ 체계적 구조 (Sequential Thinking)
- ✅ 참고문헌 포함

## 🚨 문제 해결

### 일반적인 문제와 해결법

#### 1. Ollama 연결 실패
```bash
# 문제: "Ollama API 연결 실패"
# 해결:
ollama serve  # Ollama 서버 시작
```

#### 2. 모델 없음 오류
```bash
# 문제: "사용 가능한 모델이 없습니다"
# 해결:
ollama pull gemma3:latest
```

#### 3. MCP 서버 오류
```bash
# 문제: MCP 서버 연결 실패
# 해결:
> /mcp stop   # 서버 중지
> /mcp start  # 서버 재시작
```

#### 4. 응답 품질 개선
```bash
# 문제: AI 답변이 부족함
# 해결:
> /mcp start              # MCP 활성화
> /model gemma3:latest    # 더 나은 모델 사용
```

## 📱 주요 명령어 치트시트

### 기본 명령어
```bash
/help          # 도움말
/mcp start     # MCP 활성화
/mcp status    # 상태 확인
/model <name>  # 모델 변경
/debug         # 디버그 모드
/exit          # 종료
```

### MCP 연구 명령어
```bash
/mcp bioarticle <키워드>    # 논문 검색
/mcp biotrial <조건>       # 임상시험 검색
/mcp chembl molecule <분자> # 분자 정보
/mcp think <문제>         # 단계별 분석
/mcp test deep           # Deep Search 테스트
```

## 🎓 학습 경로

### 초급 (1일차)
1. 기본 챗봇 사용법 익히기
2. 간단한 신약개발 질문하기
3. 결과 저장 및 확인하기

### 중급 (2-3일차)
1. MCP 기능 활성화
2. 개별 MCP 도구 사용법
3. 복합적인 연구 질문 수행

### 고급 (1주차)
1. 배치 처리로 여러 질문 동시 처리
2. 고급 설정 및 최적화
3. 사용자 정의 연구 워크플로우 구축

## 🔗 다음 단계

성공적으로 시작했다면:

1. **[DEEP_RESEARCH_USER_MANUAL.md](./DEEP_RESEARCH_USER_MANUAL.md)** - 고급 기능 상세 가이드
2. **[README.md](./README.md)** - 전체 시스템 문서
3. **연구 결과 폴더 확인**: `research_outputs/` 디렉토리

## 💡 추가 팁

### 성능 최적화
- GPU가 있는 경우 더 빠른 처리 가능
- 메모리 16GB 이상 권장
- MCP 활성화로 더 정확한 답변

### 효과적인 질문법
- 구체적이고 명확한 질문하기
- 연구 목적과 배경 설명하기
- 원하는 답변 형식 명시하기

---

**시작 명령어 요약:**
```bash
python run_chatbot.py    # 챗봇 실행
/mcp start              # MCP 활성화
/mcp test deep          # Deep Search 테스트
```

**축하합니다! 🎉 GAIA-BT 신약개발 연구 시스템을 성공적으로 시작했습니다!**

더 자세한 기능은 상세 매뉴얼을 참조하세요. 질문이나 문제가 있으면 언제든지 `/help` 명령어를 사용하세요.