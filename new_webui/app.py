import streamlit as st
import time
import os
import requests
from datetime import datetime
from typing import List, Dict, Any
import json

# Ollama API 설정
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def get_available_models():
    """Ollama에서 사용 가능한 모델 목록 가져오기"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        else:
            return ["llama3.2:latest", "gemma2:latest", "qwen2.5:latest"]  # 기본값
    except Exception as e:
        st.error(f"GAIA GPT 서버 연결 실패: {e}")
        return ["llama3.2:latest", "gemma2:latest", "qwen2.5:latest"]  # 기본값

def generate_ollama_response(prompt: str, model: str, mode: str, expert_mode: str = "default"):
    """Ollama API를 통해 응답 생성 (개선된 에러 처리 및 타임아웃 관리)"""
    try:
        # 전문가 모드별 시스템 프롬프트
        expert_prompts = {
            "default": "당신은 신약개발 전반에 대한 균형잡힌 AI 어시스턴트입니다. 사용자의 질문에 대해 명확하고 실용적인 답변을 제공해주세요.",
            "clinical": "당신은 임상시험 및 환자 중심 약물 개발 전문가입니다. 임상시험 설계, 환자 안전성, 효능 평가, 규제 요구사항을 중심으로 답변해주세요.",
            "research": "당신은 문헌 분석 및 과학적 증거 종합 전문가입니다. 최신 연구 동향, 논문 분석, 과학적 근거를 바탕으로 심층적인 분석을 제공해주세요.",
            "chemistry": "당신은 의약화학 및 분자 설계 전문가입니다. 화학 구조, 분자 메커니즘, SAR(구조-활성 관계), 약물 최적화를 중심으로 답변해주세요.",
            "regulatory": "당신은 글로벌 의약품 규제 및 승인 전문가입니다. FDA, EMA, MFDS 등 규제 기관의 요구사항, 승인 과정, 규제 전략을 중심으로 답변해주세요."
        }
        
        # 모드별 시스템 프롬프트 (2개 모드)
        mode_prompts = {
            "Normal": expert_prompts.get(expert_mode, expert_prompts["default"]),
            "Deep Research": f"{expert_prompts.get(expert_mode, expert_prompts['default'])} 과학적 근거를 바탕으로 심층적인 분석을 제공하고, 연구 배경, 핵심 발견사항, 실용적 제안을 포함하여 포괄적으로 답변해주세요."
        }
        
        system_prompt = mode_prompts.get(mode, mode_prompts["Normal"])
        
        # 토큰 수 제한 (타임아웃 방지)
        max_tokens = min(st.session_state.get("max_tokens", 1000), 1500)
        
        payload = {
            "model": model,
            "prompt": f"{system_prompt}\n\n질문: {prompt}\n\n답변:",
            "stream": False,
            "options": {
                "temperature": st.session_state.get("temperature", 0.7),
                "num_predict": max_tokens,
                "top_k": 40,
                "top_p": 0.9,
                "repeat_penalty": 1.1
            }
        }
        
        # 단계적 타임아웃 처리
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate", 
            json=payload, 
            timeout=300  # 5분으로 증가
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "").strip()
            
            if not answer:
                return "모델에서 응답을 생성하지 못했습니다. 다시 시도해주세요."
            
            return answer
        else:
            return f"서버 오류 (상태 코드: {response.status_code}). 잠시 후 다시 시도해주세요."
            
    except requests.exceptions.Timeout:
        return """⏰ **응답 시간 초과**
        
현재 질문이 처리하기에 너무 복잡하거나 서버가 바쁜 상태입니다.

**해결 방법**:
1. 더 간단하고 구체적인 질문으로 다시 시도
2. 사이드바에서 최대 토큰 수를 1000 이하로 줄이기
3. 잠시 후 다시 시도해보기

**추천 질문 형태**:
- "신약개발 과정을 간단히 설명해주세요"
- "임상시험 1상의 목적은 무엇인가요?"
        """
    except requests.exceptions.ConnectionError:
        return """🔌 **서버 연결 실패**
        
GAIA GPT 서버에 연결할 수 없습니다.

**해결 방법**:
1. 사이드바의 "서버 상태 확인" 버튼 클릭
2. GAIA GPT 서버 재시작: `ollama serve`
3. 터미널에서 서버 상태 확인: `curl http://localhost:11434/api/tags`
        """
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            return """⏰ **처리 시간 초과**
            
응답 생성에 시간이 너무 오래 걸리고 있습니다.

**즉시 해결 방법**:
1. 사이드바에서 최대 토큰 수를 500-1000으로 줄이기
2. 더 짧고 구체적인 질문으로 변경
3. 다른 모델 선택해보기 (txgemma-chat 추천)
            """
        else:
            return f"""❌ **오류 발생**
            
예상치 못한 오류가 발생했습니다: {error_msg}

**해결 방법**:
1. 페이지 새로고침 후 다시 시도
2. 사이드바에서 "서버 상태 확인" 버튼 클릭
3. 문제가 지속되면 다른 모델 선택
            """

def check_ollama_status():
    """Ollama 서버 상태 확인"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return response.status_code == 200
    except:
        return False

def check_mcp_status():
    """MCP 서버 상태 확인"""
    try:
        # GAIA-BT 시스템의 MCP 서버 확인 (포트 8080)
        response = requests.get("http://localhost:8080/health", timeout=3)
        return response.status_code == 200
    except:
        try:
            # 대안: MCP 프로세스 확인
            import subprocess
            result = subprocess.run(['pgrep', '-f', 'mcp'], capture_output=True, text=True)
            return len(result.stdout.strip()) > 0
        except:
            return False

def start_mcp_servers():
    """MCP 서버 시작"""
    try:
        import subprocess
        # GAIA-BT MCP 서버 시작 스크립트 실행
        script_path = "/home/gaia-bt/workspace/GAIA_LLMs/scripts/run_mcp_servers.sh"
        result = subprocess.run([script_path], capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        st.error(f"MCP 서버 시작 실패: {e}")
        return False

def stop_mcp_servers():
    """MCP 서버 중지"""
    try:
        import subprocess
        # GAIA-BT MCP 서버 중지 스크립트 실행
        script_path = "/home/gaia-bt/workspace/GAIA_LLMs/scripts/stop_mcp_servers.sh"
        result = subprocess.run([script_path], capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        st.error(f"MCP 서버 중지 실패: {e}")
        return False

# GAIA-BT GPT 챗봇 설정
st.set_page_config(
    page_title="GAIA-BT GPT",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for GAIA-BT theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .chat-container {
        background: #f8fafc;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #3b82f6;
    }
    
    .user-message {
        background: linear-gradient(135deg, #3b82f6, #1e40af);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
        color: #1e293b;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        max-width: 80%;
        border-left: 4px solid #06b6d4;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    .status-online { background-color: #10b981; }
    .status-processing { background-color: #f59e0b; }
    .status-offline { background-color: #ef4444; }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .mode-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .mode-normal {
        background-color: #e5e7eb;
        color: #374151;
    }
    
    .mode-research {
        background-color: #dcfce7;
        color: #166534;
    }
    
    .expert-default {
        background-color: #e5e7eb;
        color: #374151;
    }
    
    .expert-clinical {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .expert-research {
        background-color: #dbeafe;
        color: #1e40af;
    }
    
    .expert-chemistry {
        background-color: #fecaca;
        color: #dc2626;
    }
    
    .expert-regulatory {
        background-color: #e9d5ff;
        color: #7c3aed;
    }
    
    .sidebar-section {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .stButton > button[disabled] {
        background-color: #f1f5f9 !important;
        color: #94a3b8 !important;
        border-color: #e2e8f0 !important;
        cursor: not-allowed !important;
    }
    
    .stButton > button[disabled]:hover {
        background-color: #f1f5f9 !important;
        color: #94a3b8 !important;
        border-color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "Normal"

if "available_models" not in st.session_state:
    st.session_state.available_models = get_available_models()

if "model" not in st.session_state:
    # 기본 모델을 Gemma3:27b-it-q4_K_M로 설정
    default_model = "Gemma3:27b-it-q4_K_M"
    if st.session_state.available_models and default_model in st.session_state.available_models:
        st.session_state.model = default_model
    elif st.session_state.available_models:
        st.session_state.model = st.session_state.available_models[0]
    else:
        st.session_state.model = "Gemma3:27b-it-q4_K_M"

if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{int(time.time())}"

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 800  # 기본값을 낮춤

if "ollama_status" not in st.session_state:
    st.session_state.ollama_status = check_ollama_status()

if "mcp_status" not in st.session_state:
    # 처음 시작할 때는 MCP 서버에 연결하지 않음
    st.session_state.mcp_status = False

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1>🧬 GAIA-BT GPT</h1>
    <p>신약개발 전문 AI 어시스턴트 | 차세대 의약품 연구 지원</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.markdown("### 🔧 시스템 설정")
    
    # 시스템 상태
    ollama_status = "온라인" if st.session_state.ollama_status else "오프라인"
    ollama_class = "status-online" if st.session_state.ollama_status else "status-offline"
    
    mcp_status = "연결됨" if st.session_state.mcp_status else "연결 안됨"
    mcp_class = "status-online" if st.session_state.mcp_status else "status-offline"
    
    st.markdown(f"""
    <div class="sidebar-section">
        <h4>📊 시스템 상태</h4>
        <p><span class="status-indicator {ollama_class}"></span>GAIA GPT 서버: {ollama_status}</p>
        <p><span class="status-indicator status-online"></span>모델: 활성화</p>
        <p><span class="status-indicator {mcp_class}"></span>MCP 서버: {mcp_status}</p>
        <p><span class="status-indicator status-processing"></span>세션: {st.session_state.session_id}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 서버 상태 새로고침 버튼
    if st.button("🔄 서버 상태 확인"):
        st.session_state.ollama_status = check_ollama_status()
        st.session_state.mcp_status = check_mcp_status()
        st.session_state.available_models = get_available_models()
        st.rerun()
    
    # MCP 수동 제어 버튼
    st.markdown("#### 🔬 MCP 서버 제어")
    col1, col2 = st.columns(2)
    
    with col1:
        # MCP 서버가 중지된 상태일 때만 시작 버튼 활성화
        start_disabled = st.session_state.mcp_status
        start_help = "MCP 서버가 이미 실행 중입니다" if start_disabled else "MCP 서버를 수동으로 시작"
        
        if st.button("🔌 MCP 시작", 
                    disabled=start_disabled, 
                    help=start_help):
            with st.spinner("MCP 서버 시작 중..."):
                if start_mcp_servers():
                    st.session_state.mcp_status = True
                    st.success("✅ MCP 서버 시작 완료")
                else:
                    st.error("❌ MCP 서버 시작 실패")
                    st.session_state.mcp_status = check_mcp_status()
            st.rerun()
    
    with col2:
        # MCP 서버가 실행 중일 때만 중지 버튼 활성화
        stop_disabled = not st.session_state.mcp_status
        stop_help = "MCP 서버가 이미 중지되어 있습니다" if stop_disabled else "MCP 서버를 수동으로 중지"
        
        if st.button("🔌 MCP 중지", 
                    disabled=stop_disabled, 
                    help=stop_help):
            with st.spinner("MCP 서버 중지 중..."):
                if stop_mcp_servers():
                    st.session_state.mcp_status = False
                    st.success("✅ MCP 서버 중지 완료")
                else:
                    st.error("❌ MCP 서버 중지 실패")
                    st.session_state.mcp_status = check_mcp_status()
            st.rerun()
    
    # 모드 선택
    st.markdown("#### 🎯 작업 모드")
    modes = ["Normal", "Deep Research"]
    current_mode_index = 0
    if st.session_state.mode in modes:
        current_mode_index = modes.index(st.session_state.mode)
    elif st.session_state.mode in ["Clinical Analysis", "Molecular Design"]:
        # 기존 4개 모드 사용자를 Deep Research로 매핑
        current_mode_index = 1
        st.session_state.mode = "Deep Research"
    
    mode = st.selectbox(
        "모드 선택:",
        modes,
        index=current_mode_index,
        help="Normal: 일반 신약개발 질문 | Deep Research: MCP 연동 심층 분석"
    )
    
    # 모드 변경 시 MCP 서버 및 모델 자동 제어
    if mode != st.session_state.mode:
        st.session_state.mode = mode
        
        if mode == "Normal":
            # Normal 모드: MCP 서버 중지 + Gemma3 모델로 변경
            with st.spinner("Normal 모드로 전환 중..."):
                # MCP 서버 중지
                if st.session_state.mcp_status:
                    if stop_mcp_servers():
                        st.session_state.mcp_status = False
                    else:
                        st.session_state.mcp_status = check_mcp_status()
                
                # 모델을 Gemma3:27b-it-q4_K_M로 변경
                target_model = "Gemma3:27b-it-q4_K_M"
                if target_model in st.session_state.available_models:
                    st.session_state.model = target_model
                    st.success("✅ Normal 모드로 전환 완료 - Gemma3 모델 활성화")
                else:
                    st.success("✅ Normal 모드로 전환 완료")
                    st.warning("⚠️ Gemma3 모델을 찾을 수 없어 현재 모델을 유지합니다")
        
        elif mode == "Deep Research":
            # Deep Research 모드: MCP 서버 시작 + txgemma-chat 모델로 변경
            with st.spinner("Deep Research 모드로 전환 중..."):
                # MCP 서버 시작
                if not st.session_state.mcp_status:
                    if start_mcp_servers():
                        st.session_state.mcp_status = True
                    else:
                        st.session_state.mcp_status = check_mcp_status()
                
                # 모델을 txgemma-chat:latest로 변경
                target_model = "txgemma-chat:latest"
                if target_model in st.session_state.available_models:
                    st.session_state.model = target_model
                    st.success("✅ Deep Research 모드로 전환 완료 - txgemma-chat 모델 활성화")
                else:
                    st.success("✅ Deep Research 모드로 전환 완료")
                    st.warning("⚠️ txgemma-chat 모델을 찾을 수 없어 현재 모델을 유지합니다")
        
        st.rerun()
    else:
        st.session_state.mode = mode
    
    # 모드별 설명
    if mode == "Normal":
        st.info("💬 일반 모드: 신약개발 기본 질문에 대한 직접적인 AI 응답")
    else:
        mcp_info = "🔬 Deep Research 모드: "
        if st.session_state.mcp_status:
            mcp_info += "MCP 서버 연동으로 논문, 임상시험 데이터 기반 심층 분석"
        else:
            mcp_info += "MCP 서버 미연결 상태 - AI 분석 중심 응답"
        st.info(mcp_info)
    
    # 모델 선택
    st.markdown("#### 🤖 GAIA GPT 모델")
    if st.session_state.available_models:
        current_index = 0
        if st.session_state.model in st.session_state.available_models:
            current_index = st.session_state.available_models.index(st.session_state.model)
        
        model = st.selectbox(
            "모델 선택:",
            st.session_state.available_models,
            index=current_index,
            help="GAIA GPT 서버에서 사용 가능한 모델 목록"
        )
        st.session_state.model = model
        
        # 선택된 모델 정보 표시
        if "txgemma-chat" in model:
            st.info("💬 신약개발 특화형 모델 (Deep Research 최적화)")
        elif "txgemma-predict" in model:
            st.info("📊 분석 특화 모델 - 예측/분석")
        elif "Gemma3" in model:
            st.info("🧠 최신 모델 - 고품질 응답 (Normal 모드 최적화)")
    else:
        st.warning("사용 가능한 모델이 없습니다. GAIA GPT 서버를 확인해주세요.")
        st.session_state.model = "llama3.2:latest"
    
    # 전문가 모드 설정
    st.markdown("#### 👨‍🔬 전문가 모드")
    expert_modes = {
        "default": "신약개발 전반에 대한 균형잡힌 AI 어시스턴트",
        "clinical": "임상시험 및 환자 중심 약물 개발 전문가", 
        "research": "문헌 분석 및 과학적 증거 종합 전문가",
        "chemistry": "의약화학 및 분자 설계 전문가",
        "regulatory": "글로벌 의약품 규제 및 승인 전문가"
    }
    
    if "expert_mode" not in st.session_state:
        st.session_state.expert_mode = "default"
    
    expert_mode = st.selectbox(
        "전문가 모드 선택:",
        list(expert_modes.keys()),
        format_func=lambda x: expert_modes[x],
        index=list(expert_modes.keys()).index(st.session_state.expert_mode),
        help="AI의 전문성 방향을 설정합니다"
    )
    st.session_state.expert_mode = expert_mode
    
    # 선택된 전문가 모드 정보 표시
    st.info(f"🎯 {expert_modes[expert_mode]}")
    
    # 관심 분야 (기존 유지)
    st.markdown("#### 🔬 관심 분야")
    specialty = st.multiselect(
        "세부 관심 분야:",
        ["신약개발", "임상시험", "의약화학", "생물정보학", "규제과학", "약물동태학"],
        default=["신약개발", "임상시험"]
    )
    
    # 고급 설정
    with st.expander("⚙️ 고급 설정"):
        st.session_state.temperature = st.slider(
            "창의성 (Temperature)", 
            0.0, 1.0, 
            st.session_state.temperature, 
            0.1,
            help="높을수록 창의적, 낮을수록 일관된 응답"
        )
        st.session_state.max_tokens = st.slider(
            "최대 토큰 수", 
            100, 4000, 
            st.session_state.max_tokens, 
            100,
            help="응답의 최대 길이"
        )
        show_sources = st.checkbox("출처 표시", value=True)
        realtime_mode = st.checkbox("실시간 모드", value=False)
        
        # 빠른 설정 프리셋
        st.markdown("##### 🎛️ 빠른 설정")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("⚡ 빠른 응답", help="빠른 응답용 설정"):
                st.session_state.temperature = 0.5
                st.session_state.max_tokens = 500
                st.rerun()
        
        with col2:
            if st.button("🔬 상세 분석", help="상세 분석용 설정"):
                st.session_state.temperature = 0.7
                st.session_state.max_tokens = 1200
                st.rerun()
    
    # 빠른 액션
    st.markdown("#### ⚡ 빠른 액션")
    if st.button("🔄 새 세션 시작"):
        st.session_state.messages = []
        st.session_state.session_id = f"session_{int(time.time())}"
        st.rerun()
    
    if st.button("💾 대화 저장"):
        chat_data = {
            "session_id": st.session_state.session_id,
            "timestamp": datetime.now().isoformat(),
            "mode": st.session_state.mode,
            "model": st.session_state.model,
            "messages": st.session_state.messages
        }
        st.download_button(
            label="💾 다운로드",
            data=json.dumps(chat_data, ensure_ascii=False, indent=2),
            file_name=f"gaia-bt-chat-{st.session_state.session_id}.json",
            mime="application/json"
        )
    
    # 통계
    st.markdown(f"""
    <div class="sidebar-section">
        <h4>📈 세션 통계</h4>
        <p>메시지 수: {len(st.session_state.messages)}</p>
        <p>활성 시간: {datetime.now().strftime('%H:%M:%S')}</p>
        <p>현재 모드: <span class="mode-badge mode-{'research' if 'Research' in st.session_state.mode else 'normal'}">{st.session_state.mode}</span></p>
        <p>전문가 모드: <span class="mode-badge expert-{st.session_state.get('expert_mode', 'default')}">
        {'신약개발 전반에 대한 균형잡힌 AI 어시스턴트' if st.session_state.get('expert_mode', 'default') == 'default' 
         else '임상시험 및 환자 중심 약물 개발 전문가' if st.session_state.get('expert_mode', 'default') == 'clinical'
         else '문헌 분석 및 과학적 증거 종합 전문가' if st.session_state.get('expert_mode', 'default') == 'research'
         else '의약화학 및 분자 설계 전문가' if st.session_state.get('expert_mode', 'default') == 'chemistry'
         else '글로벌 의약품 규제 및 승인 전문가' if st.session_state.get('expert_mode', 'default') == 'regulatory'
         else '신약개발 전반에 대한 균형잡힌 AI 어시스턴트'}
        </span></p>
    </div>
    """, unsafe_allow_html=True)

# 메인 채팅 영역
st.markdown("### 💬 대화")

# 모드별 안내 메시지
if st.session_state.mode == "Normal":
    st.info("**Normal 모드**: 신약개발 전반에 대한 기본적인 AI 답변을 제공합니다.")
else:  # Deep Research
    if st.session_state.mcp_status:
        st.info("**Deep Research 모드**: MCP 서버 연동으로 논문, 임상시험 데이터를 활용한 심층 분석을 제공합니다.")
    else:
        st.warning("**Deep Research 모드**: MCP 서버가 연결되지 않아 AI 중심 분석을 제공합니다. 완전한 기능을 위해서는 MCP 서버 연결이 필요합니다.")

# 추천 질문 (처음 시작할 때만 표시)
if len(st.session_state.messages) == 0:
    st.markdown("#### 💡 추천 질문")
    
    # 전문가 모드별 추천 질문
    expert_questions = {
        "default": {
            "Normal": [
                ("🧪 신약개발 기초", "신약개발의 기본 과정을 쉽게 설명해주세요."),
                ("💊 임상시험이란?", "임상시험이 왜 필요하고 어떻게 진행되나요?"),
                ("⚗️ 약물 작용원리", "약물이 우리 몸에서 어떻게 작용하나요?"),
                ("🏥 FDA 승인과정", "신약이 승인받는 과정을 알려주세요.")
            ],
            "Deep Research": [
                ("🔬 mRNA 백신 연구", "mRNA 백신 기술의 최신 연구 동향과 신약개발 적용 가능성을 분석해주세요."),
                ("🧬 항암제 저항성", "항암제 저항성 극복을 위한 최신 연구 현황과 해결 방안을 분석해주세요."),
                ("🎯 정밀의학 동향", "정밀의학 기반 신약개발의 현황과 미래 전망을 분석해주세요."),
                ("🔬 AI 신약개발", "AI와 머신러닝을 활용한 신약개발의 최신 동향과 성과를 분석해주세요.")
            ]
        },
        "clinical": {
            "Normal": [
                ("🏥 임상시험 설계", "임상시험은 어떻게 설계하고 계획하나요?"),
                ("👥 환자 모집", "임상시험에서 적절한 환자를 모집하는 방법은?"),
                ("📊 임상 데이터", "임상시험 데이터는 어떻게 분석하나요?"),
                ("⚖️ 윤리적 고려", "임상시험에서 환자 안전과 윤리는 어떻게 보장하나요?")
            ],
            "Deep Research": [
                ("🔬 바이오마커 개발", "임상시험에서 바이오마커 개발과 검증 전략을 분석해주세요."),
                ("📈 적응적 설계", "적응적 임상시험 설계의 최신 동향과 장점을 분석해주세요."),
                ("🌍 글로벌 임상", "다국가 임상시험의 도전과제와 해결 방안을 분석해주세요."),
                ("💡 혁신적 시험법", "혁신적 임상시험 방법론의 현황과 미래를 분석해주세요.")
            ]
        },
        "research": {
            "Normal": [
                ("📚 문헌 검색", "신약개발 연구를 위한 효과적인 문헌 검색 방법은?"),
                ("📊 연구 방법론", "신약개발 연구에서 사용되는 주요 방법론은?"),
                ("🔗 연구 동향", "최근 신약개발 연구의 주요 트렌드는?"),
                ("📋 연구 설계", "효과적인 신약개발 연구는 어떻게 설계하나요?")
            ],
            "Deep Research": [
                ("🧬 오믹스 연구", "오믹스 기술을 활용한 신약개발 연구의 최신 동향을 분석해주세요."),
                ("🤖 AI 연구 동향", "AI를 활용한 신약개발 연구의 현황과 성과를 분석해주세요."),
                ("🔬 트랜스레이셔널", "트랜스레이셔널 연구의 신약개발에서의 역할을 분석해주세요."),
                ("🌐 국제 협력", "국제 신약개발 연구 협력의 현황과 전망을 분석해주세요.")
            ]
        },
        "chemistry": {
            "Normal": [
                ("⚗️ 분자 설계", "신약의 분자 구조는 어떻게 설계하나요?"),
                ("🧪 화학 합성", "신약 후보물질은 어떻게 합성하나요?"),
                ("📈 SAR 분석", "구조-활성 관계(SAR) 분석이란 무엇인가요?"),
                ("🎯 타겟 결합", "약물이 타겟 단백질에 결합하는 원리는?")
            ],
            "Deep Research": [
                ("💊 약물 최적화", "lead 화합물의 약물성 최적화 전략을 분석해주세요."),
                ("🔬 컴퓨터 설계", "컴퓨터 기반 약물 설계(CADD)의 최신 동향을 분석해주세요."),
                ("⚡ 프로텍 분해", "PROTAC과 분자접착제 기술의 현황과 전망을 분석해주세요."),
                ("🧬 화학 생물학", "화학 생물학 접근법의 신약개발 적용을 분석해주세요.")
            ]
        },
        "regulatory": {
            "Normal": [
                ("📋 규제 가이드", "신약 승인을 위한 규제 요구사항은?"),
                ("🌍 글로벌 규제", "FDA, EMA, MFDS의 승인 과정 차이점은?"),
                ("📄 서류 준비", "신약 승인 신청 시 필요한 서류는?"),
                ("⏰ 승인 절차", "신약 승인까지 걸리는 시간과 과정은?")
            ],
            "Deep Research": [
                ("🚀 혁신 경로", "혁신적 신약을 위한 규제 경로(패스트트랙, 돌파구)를 분석해주세요."),
                ("🌐 국제 조화", "ICH 가이드라인과 국제 규제 조화의 현황을 분석해주세요."),
                ("📊 실제 증거", "실제 임상 증거(RWE) 활용의 규제 동향을 분석해주세요."),
                ("🔮 미래 규제", "디지털 치료제와 AI 기반 의료기기의 규제 전망을 분석해주세요.")
            ]
        }
    }
    
    current_expert = st.session_state.get('expert_mode', 'default')
    questions = expert_questions.get(current_expert, expert_questions['default'])[st.session_state.mode]
    
    cols = st.columns(2)
    for i, (title, content) in enumerate(questions):
        with cols[i % 2]:
            if st.button(title):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": content
                })
                st.rerun()

# 메시지 표시
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="user-message">
            <strong>👤 사용자:</strong><br>
            {message["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="bot-message">
            <strong>🧬 GAIA-BT:</strong><br>
            {message["content"]}
        </div>
        """, unsafe_allow_html=True)

# 사용자 입력
user_input = st.chat_input("신약개발에 대해 궁금한 것을 물어보세요...")

if user_input:
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Ollama API를 통한 봇 응답 생성
    if st.session_state.ollama_status:
        # 진행 상황 표시
        status_container = st.container()
        progress_bar = status_container.progress(0)
        status_text = status_container.empty()
        
        try:
            # 진행 상황 업데이트 (시간 기반)
            import threading
            
            # 응답 생성을 별도 스레드에서 실행
            response_result = {"completed": False, "response": None}
            
            def generate_response():
                response_result["response"] = generate_ollama_response(
                    user_input, 
                    st.session_state.model, 
                    st.session_state.mode,
                    st.session_state.expert_mode
                )
                response_result["completed"] = True
            
            # 응답 생성 스레드 시작
            response_thread = threading.Thread(target=generate_response)
            response_thread.start()
            
            # 진행 상황 표시 (5분 = 300초)
            status_text.text(f"🔄 모델 준비 중... ({st.session_state.model})")
            progress_bar.progress(5)
            time.sleep(1)
            
            status_text.text(f"🧠 {st.session_state.mode} 모드로 분석 중...")
            progress_bar.progress(10)
            time.sleep(1)
            
            status_text.text("⚡ 응답 생성 중... (최대 5분 소요)")
            
            # 시간 기반 프로그레스 바 (10% ~ 90% 까지)
            start_time = time.time()
            max_wait_time = 300  # 5분
            
            while not response_result["completed"]:
                elapsed_time = time.time() - start_time
                if elapsed_time >= max_wait_time:
                    break
                
                # 10%에서 90%까지 시간에 비례하여 증가
                progress = min(10 + (elapsed_time / max_wait_time) * 80, 90)
                progress_bar.progress(int(progress))
                
                # 남은 시간 표시
                remaining_time = max(0, max_wait_time - elapsed_time)
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                status_text.text(f"⚡ 응답 생성 중... (남은 시간: {minutes:02d}:{seconds:02d})")
                
                time.sleep(0.5)  # 0.5초마다 업데이트
            
            # 응답 완료 대기
            response_thread.join()
            bot_response = response_result["response"]
            
            # 완료 상태
            progress_bar.progress(100)
            status_text.text("✅ 응답 생성 완료!")
            
            # 진행 상황 표시 제거
            time.sleep(1)
            status_container.empty()
            
        except Exception as e:
            # 에러 발생 시 처리
            progress_bar.progress(100)
            status_text.text(f"❌ 오류 발생: {str(e)}")
            
            bot_response = f"""
❌ **응답 생성 중 오류 발생**

요청 처리 중 문제가 발생했습니다.

**시도해볼 해결책**:
1. **간단한 질문으로 재시도**: "{user_input[:30]}..." → "신약개발이란 무엇인가요?"
2. **설정 조정**: 사이드바에서 최대 토큰 수를 500-800으로 줄이기
3. **모델 변경**: 다른 Ollama 모델 선택해보기
4. **서버 확인**: "서버 상태 확인" 버튼 클릭

**현재 설정**:
- 모델: {st.session_state.model}
- 모드: {st.session_state.mode}
- 최대 토큰: {st.session_state.get("max_tokens", 1000)}
            """
            
            time.sleep(2)
            status_container.empty()
    else:
        # Ollama 서버 연결 불가 시 폴백 응답
        bot_response = f"""
⚠️ **GAIA GPT 서버 연결 불가**

현재 GAIA GPT 서버에 연결할 수 없습니다.

**요청하신 질문**: "{user_input}"

**해결 방법**:
1. **서버 시작**: 터미널에서 `ollama serve` 실행
2. **상태 확인**: 사이드바의 "🔄 서버 상태 확인" 버튼 클릭
3. **포트 확인**: http://localhost:11434/api/tags 접속 테스트

**서버 시작 후 이 질문을 다시 입력해주세요.**
        """
    
    # 봇 응답 추가
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    st.rerun()

# 하단 정보
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.875rem;">
    🧬 GAIA-BT GPT v2.0 | 신약개발 전문 AI 어시스턴트<br>
    Powered by Advanced Language Models | © 2024 GAIA-BT Labs
</div>
""", unsafe_allow_html=True)