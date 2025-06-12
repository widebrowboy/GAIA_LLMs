# GAIA-BT 신약개발 연구 챗봇 실행 가이드

**신약개발 전문 AI 연구 어시스턴트 실행 매뉴얼** 🧬💊

## 🚀 빠른 실행 (30초)

### 기본 실행
```bash
cd /home/gaia-bt/workspace/GAIA_LLMs
python run_chatbot.py
```

### 고급 모드 실행
```bash
python main.py -i
```

## 🔧 실행 옵션

### 1. 메인 챗봇 (권장)
```bash
# 안정적이고 사용하기 쉬운 버전
python run_chatbot.py

# 특징:
# - GAIA-BT GPT 전문 배너
# - 간단한 명령어 구조
# - 안정적인 MCP 통합
# - 신약개발 예제 포함
```

### 2. 고급 모드
```bash
# 연구자를 위한 고급 기능
python main.py -i

# 특징:
# - 배치 처리 가능
# - 피드백 루프 조정 가능
# - 다양한 설정 옵션
# - 전문 연구자용
```

### 3. 배치 모드 (자동화)
```bash
# 여러 질문을 한 번에 처리
python main.py -f drug_questions.json -d 3 -w 2
```

## 🎯 실행 후 기본 사용법

### 1단계: 챗봇 시작 확인
실행하면 다음과 같은 GAIA-BT 배너가 표시됩니다:

```
 ██████╗  █████╗ ██╗ █████╗       ██████╗ ████████╗
██╔════╝ ██╔══██╗██║██╔══██╗      ██╔══██╗╚══██╔══╝
██║  ███╗███████║██║███████║█████╗██████╔╝   ██║   
██║   ██║██╔══██║██║██╔══██║╚════╝██╔══██╗   ██║   
╚██████╔╝██║  ██║██║██║  ██║      ██████╔╝   ██║   
 ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝      ╚═════╝    ╚═╝   
                     G P T

🔬 신약개발 전문 AI 연구 어시스턴트

MCP(Model Context Protocol) 기반 Deep Search로 ChEMBL, PubMed/PubTator3, 
ClinicalTrials.gov, 유전체 변이 데이터베이스(CIViC, ClinVar, COSMIC, dbSNP), 
Sequential Thinking을 통합하여 과학적 근거가 풍부한 전문적인 답변을 제공합니다.
```

### 2단계: 기본 명령어 확인
```bash
> /help    # 도움말 확인
> /mcp status    # MCP 상태 확인
```

### 3단계: MCP 고급 기능 활성화 (권장)
```bash
> /mcp start
```

### 4단계: 신약개발 질문하기
```bash
# 즉시 사용 가능한 예제 질문들
> 항암제 개발에서 분자 타겟팅 치료법의 원리를 설명해주세요
> 신약개발에서 분자 타겟 발굴의 주요 접근법은 무엇인가요?
> 전임상 독성시험의 주요 단계와 평가 항목은 무엇인가요?
```

## 📋 주요 명령어 참조

### 기본 명령어
```bash
/help              # 전체 도움말
/mcp start         # MCP 고급 연구 기능 활성화
/mcp status        # 연결 상태 확인
/mcp test deep     # Deep Search 기능 테스트
/model <모델명>     # AI 모델 변경
/debug             # 디버그 모드 토글
/exit              # 챗봇 종료
```

### MCP 연구 명령어
```bash
/mcp bioarticle <키워드>     # 논문 검색
/mcp biotrial <조건>        # 임상시험 검색
/mcp chembl molecule <분자> # 화학 분자 분석
/mcp think <문제>          # Sequential Thinking
```

## 🧪 테스트 질문 예제

### 즉시 복사해서 사용하세요:

#### 🎯 타겟 발굴 및 검증
```
알츠하이머병 치료를 위한 새로운 분자 타겟은 무엇이 있나요?
```

#### 🧬 화합물 분석 및 최적화
```
키나제 억제제의 구조-활성 관계를 어떻게 분석하나요?
```

#### 🧪 임상시험 설계
```
PD-1 억제제의 임상시험 설계 시 고려사항은 무엇인가요?
```

#### ⚠️ 약물 안전성 평가
```
새로운 항암제의 독성 프로파일을 어떻게 평가해야 하나요?
```

#### 📊 바이오마커 활용
```
정밀의학에서 바이오마커의 역할과 개발 전략은 무엇인가요?
```

## 🔍 MCP Deep Search 예제

### 통합 연구 질문 (MCP 활성화 후 사용):
```bash
# 복합적인 신약개발 질문
EGFR 억제제의 내성 메커니즘과 차세대 치료 전략을 분석해주세요

# 차세대 기술 분석
PROTAC 기술을 이용한 undruggable 타겟 분해 전략은 무엇인가요?

# 조합 치료 전략
면역항암제와 표적 치료제의 합리적 병용 전략은 무엇인가요?
```

## 📊 시스템 구성

### ✅ 통합된 구성 요소
1. **ChEMBL** - 화학 데이터베이스 및 분자 구조 분석
2. **PubMed/PubTator3** - 생의학 연구 논문 및 문헌 데이터
3. **ClinicalTrials.gov** - 임상시험 데이터 및 치료법 정보
4. **유전체 변이 DB** - CIViC, ClinVar, COSMIC, dbSNP 등
3. **Sequential Thinking** - 단계별 추론 엔진
4. **Ollama Gemma3** - AI 분석 엔진

### 🔬 Deep Research 프로세스
```
사용자 질문 (신약개발 관련)
    ↓
Sequential Thinking (연구 계획 수립)
    ↓  
ChEMBL (화학 구조 및 분자 데이터)
    ↓
PubMed/PubTator3 (생의학 연구 논문)
    ↓
ClinicalTrials.gov (임상시험 데이터)
    ↓
유전체 변이 DB (CIViC, ClinVar, COSMIC, dbSNP)
    ↓
통합 컨텍스트 생성
    ↓
Ollama Gemma3 (최종 AI 분석)
    ↓
구조화된 신약개발 연구 보고서
```

## 🛠️ 실행 환경 요구사항

### 필수 사항
- **Python**: 3.13+
- **Ollama**: gemma3:latest 모델 설치됨
- **메모리**: 8GB 이상 (16GB 권장)

### 확인 방법
```bash
# Python 버전 확인
python --version

# Ollama 모델 확인
ollama list

# 필요시 모델 설치
ollama pull gemma3:latest
```

## 🤖 LLM 모델 선택 가이드

### 신약개발 연구용 권장 모델

#### 성능 순위 (신약개발 특화)
| 순위 | 모델명 | 메모리 | 설치 명령어 | 추천 용도 |
|------|--------|--------|-------------|-----------|
| 🥇 | **gemma3:latest** | 16GB | `ollama pull gemma3:latest` | 전문 연구, Deep Research |
| 🥈 | **llama3.1:latest** | 12GB | `ollama pull llama3.1:latest` | 교육, 일반 질문 |
| 🥉 | **txgemma-predict:latest** | 14GB | `ollama pull txgemma-predict:latest` | 독성 예측, ADMET 분석 |

### 시스템 사양별 권장 모델

#### 🔥 고성능 시스템 (16GB+ RAM)
```bash
# 최고 성능 모델 설치
ollama pull gemma3:latest

# 챗봇에서 모델 변경
> /model gemma3:latest
```

#### ⚡ 중급 시스템 (12GB RAM)
```bash
# 균형잡힌 성능 모델
ollama pull llama3.1:latest

# 챗봇에서 모델 변경
> /model llama3.1:latest
```

#### 💻 기본 시스템 (8GB RAM)
```bash
# 경량 모델
ollama pull llama3:8b

# 챗봇에서 모델 변경
> /model llama3:8b
```

### 신약개발 분야별 최적 모델

#### 🔬 **전문 연구 분석**
- **모델**: Gemma3
- **활용**: 복합적 신약개발 질문, 논문 수준 분석
- **예제**: "EGFR 억제제의 내성 메커니즘과 차세대 치료 전략"

#### 📚 **학습 및 교육**  
- **모델**: Llama3.1
- **활용**: 기본 개념 설명, 신약개발 프로세스 이해
- **예제**: "신약개발의 전임상 단계는 어떤 과정인가요?"

#### ⚠️ **독성 및 안전성 분석**
- **모델**: TxGemma-Predict
- **활용**: ADMET 예측, 독성 메커니즘 분석
- **예제**: "새로운 키나제 억제제의 심독성 위험 평가"

### 모델 변경 방법

#### 챗봇 실행 중 모델 변경
```bash
# 현재 사용 중인 모델 확인
> /model

# 전문 분석용으로 변경
> /model gemma3:latest

# 교육용으로 변경  
> /model llama3.1:latest

# 독성 분석용으로 변경
> /model txgemma-predict:latest
```

#### 성능 최적화 팁
```bash
# GPU 가속 활성화
export CUDA_VISIBLE_DEVICES=0

# 메모리 최적화
export OLLAMA_NUM_PARALLEL=1
```

## 🚨 문제 해결

### 1. 챗봇이 시작되지 않는 경우
```bash
# 의존성 재설치
pip install -r requirements.txt

# Ollama 서버 시작
ollama serve
```

### 2. "모델을 찾을 수 없습니다" 오류
```bash
# 기본 모델 설치
ollama pull gemma3:latest

# 챗봇에서 모델 변경
> /model gemma3:latest
```

### 3. MCP 연결 실패
```bash
# MCP 서버 재시작
> /mcp stop
> /mcp start

# 상태 확인
> /mcp status
```

### 4. 응답 품질이 낮은 경우
```bash
# MCP 활성화 (중요!)
> /mcp start

# 더 구체적인 질문 사용
# 나쁜 예: "암 치료법은?"
# 좋은 예: "EGFR 돌연변이 양성 폐암의 1차 치료 옵션과 내성 메커니즘은?"
```

## 📈 성능 향상 팁

### 1. MCP 활성화 필수
```bash
# 항상 MCP를 활성화하여 사용하세요
> /mcp start
```

### 2. 구체적인 질문하기
```bash
# 좋은 질문 예시:
# - 특정 타겟, 질환, 메커니즘 명시
# - 개발 단계 구체화 (전임상, Phase I-III)
# - 목적 명확화 (효능, 안전성, 바이오마커)
```

### 3. 단계별 접근
```bash
# 1단계: 개념 이해
> EGFR이란 무엇이고 왜 중요한 타겟인가요?

# 2단계: 메커니즘 분석
> EGFR 억제제의 작용 메커니즘을 분석해주세요

# 3단계: 임상적 활용
> EGFR 억제제의 임상적 사용과 한계점은 무엇인가요?
```

## 📊 실행 모드별 비교

| 특징 | run_chatbot.py | main.py -i | main.py -f |
|------|----------------|------------|------------|
| **사용 대상** | 일반 사용자 | 연구자 | 자동화 |
| **설정 복잡도** | 낮음 | 중간 | 높음 |
| **배치 처리** | ❌ | ❌ | ✅ |
| **피드백 조정** | ❌ | ✅ | ✅ |
| **MCP 통합** | ✅ | ✅ | ✅ |
| **사용 편의성** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

## 🎓 학습 순서 추천

### 1주차: 기본 사용법
1. `python run_chatbot.py` 실행
2. 기본 명령어 익히기 (`/help`, `/mcp start`)
3. 간단한 신약개발 질문하기
4. 결과 저장 및 확인

### 2주차: MCP 고급 기능
1. MCP 개별 명령어 테스트
2. Deep Search 기능 활용
3. 복합적인 연구 질문 수행
4. 결과 품질 평가 및 개선

### 3주차: 고급 활용
1. `main.py -i` 고급 모드 사용
2. 배치 처리 및 자동화
3. 사용자 정의 워크플로우 구축
4. 성능 최적화 설정

## 📱 실행 스크립트 예제

### Windows 배치 파일 (start_gaia.bat)
```batch
@echo off
cd C:\path\to\GAIA_LLMs
python run_chatbot.py
pause
```

### Linux/macOS 스크립트 (start_gaia.sh)
```bash
#!/bin/bash
cd /home/gaia-bt/workspace/GAIA_LLMs
python run_chatbot.py
```

### 권한 설정 (Linux/macOS)
```bash
chmod +x start_gaia.sh
./start_gaia.sh
```

## 🔗 다음 단계

성공적으로 챗봇을 시작했다면:

1. **[QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md)** - 5분 빠른 시작
2. **[DEEP_RESEARCH_USER_MANUAL.md](./DEEP_RESEARCH_USER_MANUAL.md)** - 고급 기능 가이드
3. **[README.md](./README.md)** - 전체 시스템 문서

## 💡 추가 팁

### 터미널 설정 최적화
- 터미널 창 크기: 최소 120x30
- 인코딩: UTF-8 설정
- 색상 지원 활성화

### 백그라운드 실행
```bash
# 백그라운드에서 실행 (Linux/macOS)
nohup python run_chatbot.py &

# 로그 확인
tail -f nohup.out
```

### 자동 재시작
```bash
# 오류 발생 시 자동 재시작
while true; do
    python run_chatbot.py
    echo "챗봇이 종료되었습니다. 5초 후 재시작..."
    sleep 5
done
```

---

**🎉 모든 준비가 완료되었습니다!**  
터미널에서 `python run_chatbot.py`를 실행하여 과학적 근거 기반의 신약개발 연구를 시작하세요!

**축하합니다! 🎉 GAIA-BT 신약개발 연구 챗봇이 성공적으로 실행되었습니다!**

더 많은 기능과 고급 사용법은 상세 매뉴얼을 참조하세요. 질문이나 문제가 있으면 `/help` 명령어를 사용하세요.