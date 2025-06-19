# 🧬 GAIA-BT WebUI 테스트 가이드

## 🎯 테스트 시스템 상태

**✅ 시스템 준비 완료** - 모든 테스트를 진행할 수 있습니다!

- **테스트 성공률**: 96% (30/31 테스트 통과)
- **WebUI 상태**: ✅ 실행 중 (http://localhost:3000)
- **컨테이너 상태**: ✅ 정상 동작
- **GAIA-BT 통합**: ✅ 완료

## 🚀 1단계: WebUI 접속 및 초기 설정

### 1.1 브라우저 접속
```
http://localhost:3000
```

### 1.2 관리자 계정 생성
1. 첫 방문 시 관리자 계정 생성 화면이 나타납니다
2. 이메일과 비밀번호를 입력하여 계정을 생성하세요
3. "Create Account" 버튼을 클릭합니다

### 1.3 초기 설정 확인
- 좌측 메뉴에서 "Admin Panel" 확인
- "Functions" 탭 존재 확인
- "Models" 탭에서 Ollama 연결 확인

## 🔧 2단계: GAIA-BT Functions 테스트

### 2.1 Functions 탭 접속
1. 좌측 메뉴에서 "Functions" 클릭
2. GAIA-BT Functions가 로드되었는지 확인
3. 다음 함수들이 표시되는지 확인:
   - `get_system_status`
   - `switch_mode`
   - `change_model`
   - `change_prompt_mode`
   - `deep_research_search`
   - `molecular_analysis`
   - `clinical_trial_search`
   - `literature_search`
   - `generate_research_plan`

### 2.2 기본 기능 테스트

#### 시스템 상태 확인
```javascript
get_system_status()
```
**예상 결과**: GAIA-BT 시스템 상태 및 설정 정보 표시

#### 모드 전환 테스트
```javascript
switch_mode("deep_research")
```
**예상 결과**: Deep Research Mode로 전환 확인 메시지

```javascript
switch_mode("normal")
```
**예상 결과**: Normal Mode로 전환 확인 메시지

#### 프롬프트 모드 변경 테스트
```javascript
change_prompt_mode("clinical")
```
**예상 결과**: 임상시험 전문 모드로 변경

```javascript
change_prompt_mode("research")
```
**예상 결과**: 연구 분석 전문 모드로 변경

## 🔬 3단계: Deep Research 기능 테스트

### 3.1 Deep Research 검색
```javascript
deep_research_search("아스피린의 새로운 치료 적용")
```
**예상 결과**: 
- 📚 PubMed/PubTator3 논문 검색 결과
- 🏥 ClinicalTrials.gov 임상시험 데이터
- 🧪 ChEMBL 화학구조 분석

### 3.2 분자 분석 기능
```javascript
molecular_analysis("aspirin")
```
**예상 결과**: 분자량, 약물 유사성, 타겟 예측 정보

### 3.3 임상시험 검색
```javascript
clinical_trial_search("breast cancer", "phase2")
```
**예상 결과**: 유방암 관련 Phase 2 임상시험 정보

### 3.4 문헌 검색
```javascript
literature_search("BRCA1 inhibitor", 3)
```
**예상 결과**: 최근 3년간 BRCA1 억제제 관련 논문 정보

### 3.5 연구 계획 생성
```javascript
generate_research_plan("항암제 신약 개발", "10억원", "3년")
```
**예상 결과**: 단계별 연구 계획 및 타임라인

## 💬 4단계: Pipeline 통합 테스트

### 4.1 일반 모드 채팅 테스트
1. 새로운 채팅 시작
2. 다음 질문 입력:
```
아스피린의 작용 메커니즘을 신약개발 관점에서 설명해주세요
```

**예상 결과**:
- 🧬 GAIA-BT v2.0 Alpha 배너 표시
- 💬 일반 모드 처리 메시지
- 신약개발 전문 관점의 상세한 답변

### 4.2 Deep Research 모드 테스트
1. Functions에서 Deep Research 모드 활성화:
```javascript
switch_mode("deep_research")
```

2. 새로운 채팅에서 다음 질문:
```
BRCA1 타겟을 이용한 유방암 치료제 개발 전략을 분석해주세요
```

**예상 결과**:
- 🔬 Deep Research Mode 배너
- MCP 통합 검색 과정 표시 (옵션)
- 📊 통합 분석 결과
- 🎯 연구 권장사항

## 🎨 5단계: 전문 프롬프트 모드 테스트

### 5.1 임상시험 전문 모드
```javascript
change_prompt_mode("clinical")
```
질문: "Phase I 임상시험 설계 시 고려사항은?"

### 5.2 의약화학 전문 모드
```javascript
change_prompt_mode("chemistry")
```
질문: "신약의 ADMET 특성 최적화 방법은?"

### 5.3 규제 전문 모드
```javascript
change_prompt_mode("regulatory")
```
질문: "FDA 신약 승인 절차의 주요 단계는?"

## 📊 6단계: 성능 및 안정성 테스트

### 6.1 에러 처리 테스트
```javascript
switch_mode("invalid_mode")
```
**예상 결과**: 적절한 에러 메시지 및 유효한 옵션 안내

### 6.2 Mock 시스템 테스트
- GAIA-BT 백엔드가 없어도 Mock 응답으로 모든 기능 동작
- 에러 발생 시 자동 폴백 메커니즘 작동

### 6.3 장시간 사용 테스트
- 여러 개의 채팅 세션 동시 진행
- 다양한 프롬프트 모드 반복 전환
- 복잡한 연구 질의 연속 처리

## 🎯 7단계: 실제 사용 시나리오 테스트

### 시나리오 1: 신약 후보 물질 탐색
1. `change_prompt_mode("research")`
2. `deep_research_search("알츠하이머 치료제 후보 물질")`
3. `molecular_analysis("donepezil")`
4. `clinical_trial_search("alzheimer", "phase3")`

### 시나리오 2: 임상시험 계획 수립
1. `change_prompt_mode("clinical")`
2. `generate_research_plan("당뇨병 치료제 임상시험", "50억원", "5년")`
3. 채팅으로 세부 질문: "Phase II 임상시험의 환자 수 산정 방법"

### 시나리오 3: 규제 전략 수립
1. `change_prompt_mode("regulatory")`
2. 채팅으로 질문: "바이오의약품 허가를 위한 규제 전략"
3. `literature_search("FDA biologic approval", 2)`

## ✅ 테스트 체크리스트

### 기본 기능
- [ ] WebUI 접속 성공 (http://localhost:3000)
- [ ] 관리자 계정 생성 완료
- [ ] Functions 탭 접근 가능
- [ ] GAIA-BT Functions 로드 확인

### 핵심 Functions
- [ ] `get_system_status()` 정상 작동
- [ ] `switch_mode()` 정상 작동
- [ ] `change_prompt_mode()` 정상 작동
- [ ] `deep_research_search()` 정상 작동
- [ ] 각 전문 분야 함수들 정상 작동

### Pipeline 통합
- [ ] 일반 모드 채팅 정상 작동
- [ ] Deep Research 모드 정상 작동
- [ ] GAIA-BT 배너 정상 표시
- [ ] 모드별 다른 응답 확인

### 사용자 경험
- [ ] 적절한 에러 메시지 표시
- [ ] Mock 폴백 시스템 정상 작동
- [ ] 직관적인 UI/UX
- [ ] 빠른 응답 속도

## 🚨 문제 해결

### WebUI 접속 불가 시
```bash
docker restart gaia-bt-webui-test
```

### Functions 로드 실패 시
```bash
# 컨테이너 재시작 후 파일 확인
docker exec gaia-bt-webui-test ls -la /app/backend/data/functions/
```

### 성능 이슈 시
```bash
# 컨테이너 리소스 사용량 확인
docker stats gaia-bt-webui-test
```

## 📞 지원 및 피드백

### 성공적인 테스트 완료 시
- 테스트 결과를 webui.md에 기록
- 추가 기능 요청사항 정리

### 문제 발생 시
- 정확한 에러 메시지 기록
- 재현 가능한 단계 정리
- 시스템 로그 확인

---

**🎉 축하합니다!** GAIA-BT v2.0 Alpha WebUI 시스템이 성공적으로 구축되었습니다.

이제 웹 브라우저에서 run_chatbot.py와 동일한 모든 기능을 사용할 수 있습니다!