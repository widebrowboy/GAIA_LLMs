# 🔄 MCP 자동 제어 시스템 업데이트 가이드

## ✅ 완료된 업데이트

### 🎯 모드 연동 자동 MCP 제어
**핵심 기능**: 작업 모드 선택에 따른 MCP 서버 자동 시작/중지

#### Normal 모드 선택 시
```
사용자가 "Normal" 모드 선택
    ↓
MCP 서버 상태 확인
    ↓
MCP 서버가 실행 중이면 자동 중지
    ↓
"✅ Normal 모드로 전환 완료" 메시지 표시
```

#### Deep Research 모드 선택 시
```
사용자가 "Deep Research" 모드 선택
    ↓
MCP 서버 상태 확인
    ↓
MCP 서버가 중지 상태이면 자동 시작
    ↓
"✅ Deep Research 모드로 전환 완료 - MCP 서버 연결됨" 메시지 표시
```

## 🔧 새로운 기능들

### 1. 자동 MCP 제어 함수
```python
def start_mcp_servers():
    """MCP 서버 시작"""
    script_path = "/home/gaia-bt/workspace/GAIA_LLMs/scripts/run_mcp_servers.sh"
    result = subprocess.run([script_path], capture_output=True, text=True, timeout=30)
    return result.returncode == 0

def stop_mcp_servers():
    """MCP 서버 중지"""
    script_path = "/home/gaia-bt/workspace/GAIA_LLMs/scripts/stop_mcp_servers.sh"
    result = subprocess.run([script_path], capture_output=True, text=True, timeout=30)
    return result.returncode == 0
```

### 2. 모드 변경 감지 및 자동 제어
```python
# 모드 변경 시 MCP 서버 자동 제어
if mode != st.session_state.mode:
    st.session_state.mode = mode
    
    if mode == "Normal":
        # Normal 모드: MCP 서버 중지
        if st.session_state.mcp_status:
            with st.spinner("Normal 모드로 전환 중... MCP 서버 중지"):
                if stop_mcp_servers():
                    st.session_state.mcp_status = False
                    st.success("✅ Normal 모드로 전환 완료")
    
    elif mode == "Deep Research":
        # Deep Research 모드: MCP 서버 시작
        if not st.session_state.mcp_status:
            with st.spinner("Deep Research 모드로 전환 중... MCP 서버 시작"):
                if start_mcp_servers():
                    st.session_state.mcp_status = True
                    st.success("✅ Deep Research 모드로 전환 완료 - MCP 서버 연결됨")
    
    st.rerun()
```

### 3. 수동 MCP 제어 인터페이스
```python
# MCP 수동 제어 버튼
st.markdown("#### 🔬 MCP 서버 제어")
col1, col2 = st.columns(2)

with col1:
    if st.button("🔌 MCP 시작", help="MCP 서버를 수동으로 시작"):
        # MCP 서버 시작 로직

with col2:
    if st.button("🔌 MCP 중지", help="MCP 서버를 수동으로 중지"):
        # MCP 서버 중지 로직
```

## 🎨 사용자 인터페이스 개선

### 새로 추가된 UI 요소

#### 1. 진행 상황 표시
- **Normal 모드 전환**: "Normal 모드로 전환 중... MCP 서버 중지"
- **Deep Research 모드 전환**: "Deep Research 모드로 전환 중... MCP 서버 시작"

#### 2. 상태 피드백 메시지
- **성공**: ✅ "Normal 모드로 전환 완료" / "Deep Research 모드로 전환 완료 - MCP 서버 연결됨"
- **경고**: ⚠️ "MCP 서버 시작/중지에 실패했지만 모드로 전환됩니다"
- **오류**: ❌ "MCP 서버 시작/중지 실패"

#### 3. 수동 제어 섹션
```
🔬 MCP 서버 제어
┌─────────────┬─────────────┐
│ 🔌 MCP 시작 │ 🔌 MCP 중지 │
└─────────────┴─────────────┘
```

### 기존 UI와의 통합
- **시스템 상태**: MCP 서버 연결 상태 실시간 표시
- **모드 설명**: 모드별 MCP 연동 상태 안내
- **추천 질문**: 모드에 따른 맞춤 질문 표시

## 🔄 동작 시나리오

### 시나리오 1: Normal 모드로 전환
```
현재 상태: Deep Research 모드, MCP 서버 실행 중
사용자 액션: Normal 모드 선택
시스템 동작:
1. 스피너 표시: "Normal 모드로 전환 중... MCP 서버 중지"
2. stop_mcp_servers.sh 실행
3. MCP 서버 중지 확인
4. 성공 메시지: "✅ Normal 모드로 전환 완료"
5. 페이지 새로고침
결과: Normal 모드, MCP 서버 중지 상태
```

### 시나리오 2: Deep Research 모드로 전환
```
현재 상태: Normal 모드, MCP 서버 중지 상태
사용자 액션: Deep Research 모드 선택
시스템 동작:
1. 스피너 표시: "Deep Research 모드로 전환 중... MCP 서버 시작"
2. run_mcp_servers.sh 실행
3. MCP 서버 시작 확인 (6개 서버)
4. 성공 메시지: "✅ Deep Research 모드로 전환 완료 - MCP 서버 연결됨"
5. 페이지 새로고침
결과: Deep Research 모드, MCP 서버 실행 상태
```

### 시나리오 3: 수동 MCP 제어
```
사용자 액션: "🔌 MCP 시작" 버튼 클릭
시스템 동작:
1. 스피너 표시: "MCP 서버 시작 중..."
2. run_mcp_servers.sh 실행
3. 성공/실패 메시지 표시
4. MCP 상태 업데이트
5. 페이지 새로고침
```

## 🛠️ 기술적 세부사항

### MCP 스크립트 연동
- **시작 스크립트**: `/home/gaia-bt/workspace/GAIA_LLMs/scripts/run_mcp_servers.sh`
- **중지 스크립트**: `/home/gaia-bt/workspace/GAIA_LLMs/scripts/stop_mcp_servers.sh`
- **타임아웃**: 30초 (서버 시작/중지 작업)

### 실행되는 MCP 서버들
1. **GAIA MCP**: 메인 GAIA-BT 서버
2. **BiomCP**: 생물의학 논문 및 데이터베이스
3. **ChEMBL**: 화학 및 약물 데이터베이스
4. **Sequential Thinking**: 순차적 사고 AI
5. **PubMed MCP**: 의학 논문 검색
6. **ClinicalTrials MCP**: 임상시험 데이터

### 에러 처리
```python
try:
    import subprocess
    script_path = "/home/gaia-bt/workspace/GAIA_LLMs/scripts/run_mcp_servers.sh"
    result = subprocess.run([script_path], capture_output=True, text=True, timeout=30)
    return result.returncode == 0
except Exception as e:
    st.error(f"MCP 서버 시작 실패: {e}")
    return False
```

## 📊 상태 관리

### 세션 상태 변수
- **st.session_state.mode**: 현재 작업 모드 ("Normal" | "Deep Research")
- **st.session_state.mcp_status**: MCP 서버 연결 상태 (True | False)
- **st.session_state.expert_mode**: 현재 전문가 모드

### 상태 동기화
```python
# 모드 변경 시
if mode != st.session_state.mode:
    # MCP 제어 로직 실행
    # 상태 업데이트
    # 페이지 새로고침
```

## 🎯 사용자 혜택

### 1. 완전 자동화
- **이전**: 수동으로 MCP 서버 시작/중지 필요
- **이후**: 모드 선택만으로 자동 제어

### 2. 일관성 보장
- **Normal 모드**: 항상 MCP 서버 중지 상태
- **Deep Research 모드**: 항상 MCP 서버 실행 상태

### 3. 사용 편의성
- **원클릭 전환**: 드롭다운 선택만으로 완전한 모드 전환
- **시각적 피드백**: 진행 상황과 결과를 명확히 표시
- **수동 제어**: 필요시 직접 MCP 서버 제어 가능

### 4. 리소스 효율성
- **Normal 모드**: 불필요한 MCP 서버 자동 중지로 리소스 절약
- **Deep Research 모드**: 필요시에만 MCP 서버 실행

## 🚀 업데이트된 사용법

### 1. 자동 모드 전환 (권장)
1. 사이드바 → **"🎯 작업 모드"** 섹션
2. 드롭다운에서 원하는 모드 선택
3. 자동 MCP 제어 진행 상황 확인
4. 성공 메시지 확인 후 사용 시작

### 2. 수동 MCP 제어 (고급 사용자)
1. 사이드바 → **"🔬 MCP 서버 제어"** 섹션
2. "🔌 MCP 시작" 또는 "🔌 MCP 중지" 버튼 클릭
3. 진행 상황 및 결과 메시지 확인

### 3. 상태 확인
1. 사이드바 → **"📊 시스템 상태"** 섹션
2. MCP 서버 연결 상태 확인 (연결됨/연결 안됨)
3. 필요시 "🔄 서버 상태 확인" 버튼으로 새로고침

## 📈 성능 개선

### Before (수동 제어)
```
❌ 사용자가 직접 터미널에서 MCP 서버 시작/중지
❌ 모드와 MCP 상태 불일치 가능
❌ 복잡한 사용법
❌ 리소스 낭비 (불필요한 서버 실행)
```

### After (자동 제어)
```
✅ 모드 선택만으로 자동 MCP 제어
✅ 모드와 MCP 상태 항상 일치
✅ 원클릭 사용법
✅ 효율적 리소스 관리
✅ 시각적 피드백 및 상태 표시
```

## 🎉 업데이트 완료 요약

### ✅ 새로운 기능들
1. **자동 MCP 제어**: 모드 변경 시 자동 서버 시작/중지
2. **수동 MCP 제어**: 직접 서버 제어 버튼
3. **진행 상황 표시**: 스피너 및 상태 메시지
4. **에러 처리**: 실패 시 명확한 안내 메시지
5. **상태 동기화**: 모드와 MCP 상태 자동 일치

### 🎯 사용자 경험 개선
- **원클릭 전환**: 복잡한 설정 없이 모드 변경
- **자동 최적화**: 모드에 맞는 최적 서버 상태
- **명확한 피드백**: 현재 상태와 진행 과정 표시
- **유연한 제어**: 자동 + 수동 제어 옵션

**이제 모드 선택만으로 MCP 서버가 자동으로 제어되어 더욱 편리하고 효율적인 GAIA-BT GPT를 경험하세요!** 🔄✨

---

**최종 업데이트**: 2025년 6월 20일  
**상태**: MCP 자동 제어 시스템 완료  
**사용 준비**: ✅ 완료