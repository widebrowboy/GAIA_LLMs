"""
GAIA-BT GPT 유틸리티 함수들
"""

import streamlit as st
import time
import json
from datetime import datetime
from typing import Dict, List, Any


def initialize_session_state():
    """세션 상태 초기화"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "mode" not in st.session_state:
        st.session_state.mode = "Normal"
    
    if "model" not in st.session_state:
        st.session_state.model = "GAIA-BT GPT-4"
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"session_{int(time.time())}"
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def get_mode_description(mode: str) -> str:
    """모드별 설명 반환"""
    descriptions = {
        "Normal": "일반적인 신약개발 질문에 대해 답변합니다.",
        "Deep Research": "논문, 임상시험 데이터를 활용한 심층 분석을 제공합니다.",
        "Clinical Analysis": "임상시험 설계 및 분석에 특화된 지원을 제공합니다.",
        "Molecular Design": "분자 설계 및 의약화학 최적화를 지원합니다."
    }
    return descriptions.get(mode, "전문 모드가 활성화되었습니다.")


def generate_bot_response(user_input: str, mode: str) -> str:
    """모드별 봇 응답 생성"""
    
    if mode == "Deep Research":
        return f"""
**[Deep Research 모드 - 심층 분석]**

"{user_input}"에 대한 포괄적 분석 결과:

🔬 **연구 배경**
- 최신 논문 분석 (PubMed, Nature, Science 등)
- 관련 임상시험 데이터 검토 (ClinicalTrials.gov)
- 글로벌 연구 동향 및 특허 분석

📊 **핵심 발견사항**
1. **현재 연구 현황**: 해당 분야의 최신 연구 동향
2. **기술적 도전과제**: 주요 기술적 한계점 및 해결방안
3. **미래 연구 방향**: 유망한 연구 영역 및 기회

💡 **실용적 제안**
- 단계별 실행 방안
- 위험요소 평가 및 완화전략
- 예상 타임라인 및 자원 배분

🔗 **관련 데이터베이스**
- PubMed: 관련 논문 검색
- ClinicalTrials.gov: 임상시험 현황
- DrugBank: 약물 정보
- ChEMBL: 생물학적 활성 데이터

*출처: 최신 과학 문헌 및 임상시험 데이터베이스 (2024)*
        """
    
    elif mode == "Clinical Analysis":
        return f"""
**[Clinical Analysis 모드 - 임상 분석]**

"{user_input}"에 대한 임상적 관점 분석:

🏥 **임상적 의의**
- 환자 치료에 미치는 직접적 영향
- 기존 치료법 대비 효과성 및 안전성
- Target Population 및 적응증 분석

📋 **임상시험 설계 전략**
- **Phase I**: 안전성 및 용량 결정 연구
- **Phase II**: 효능 입증 및 최적 용량 확인
- **Phase III**: 대규모 효과성 검증 시험
- **바이오마커**: 치료 반응 예측 인자
- **엔드포인트**: 주요 및 부차 평가변수

⚖️ **규제 고려사항**
- FDA/EMA 가이드라인 준수 요건
- IND/CTA 신청 전략
- 안전성 모니터링 계획
- 품질관리 및 GCP 준수

📈 **성공 확률 향상 방안**
- 환자 계층화 전략
- 적응적 임상시험 설계
- Real-world evidence 활용

*기반: ICH 가이드라인, FDA/EMA 규제 요구사항*
        """
    
    elif mode == "Molecular Design":
        return f"""
**[Molecular Design 모드 - 분자 설계]**

"{user_input}"에 대한 분자 설계 관점 분석:

⚗️ **분자 설계 전략**
- Structure-Activity Relationship (SAR) 분석
- Lead compound 최적화 방향
- 약물성 (Drug-likeness) 평가

🧪 **약물동태학적 특성**
- **ADME 특성**: 흡수, 분포, 대사, 배설
- **독성 예측**: 간독성, 심독성, 발암성
- **BBB 투과성**: 뇌혈관장벽 통과 능력
- **단백질 결합률**: 혈장 단백질 결합 특성

🎯 **타겟 상호작용**
- 결합 친화도 (Binding affinity) 최적화
- 선택성 (Selectivity) 향상 전략
- Off-target 효과 최소화

💻 **컴퓨터 기반 설계**
- Molecular docking 시뮬레이션
- QSAR 모델링
- 가상 스크리닝 (Virtual screening)
- AI/ML 기반 분자 생성

🔬 **합성 가능성**
- 합성 경로 예측
- 반응 조건 최적화
- 스케일업 고려사항

*기반: 의약화학 원리, 계산화학 방법론*
        """
    
    else:  # Normal mode
        return f"""
안녕하세요! GAIA-BT GPT입니다. 🧬

"{user_input}"에 대해 신약개발 전문가 관점에서 답변드리겠습니다.

**🎯 핵심 분석**
- 과학적 근거와 최신 연구 동향을 바탕으로 한 전문적 설명
- 실제 신약개발 프로세스에서의 적용 방안
- 단계별 접근 방법과 핵심 고려사항

**💊 실무 적용 방안**
- 구체적이고 실행 가능한 방법론
- 예상되는 도전과제와 해결책
- 성공 확률을 높이는 핵심 전략

**📚 참고 자료 및 권장사항**
- 관련 연구 논문 및 가이드라인
- 업계 모범 사례 (Best practices)
- 전문가 그룹 권장사항

**🔄 다음 단계**
더 구체적인 분석이나 특정 영역에 대한 심화 상담이 필요하시면:
- Deep Research 모드: 포괄적 문헌 분석
- Clinical Analysis 모드: 임상시험 특화 분석
- Molecular Design 모드: 분자 수준 설계 지원

언제든 추가 질문해 주세요!
        """


def save_chat_session(messages: List[Dict], session_id: str, mode: str, model: str) -> Dict:
    """채팅 세션 저장"""
    chat_data = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "model": model,
        "message_count": len(messages),
        "messages": messages
    }
    return chat_data


def get_suggested_questions() -> Dict[str, List[str]]:
    """카테고리별 추천 질문 반환"""
    return {
        "신약개발 기초": [
            "신약개발의 전체 과정을 단계별로 설명해주세요.",
            "신약 개발에 소요되는 평균 기간과 비용은 얼마인가요?",
            "신약 개발 성공률을 높이는 핵심 요소는 무엇인가요?"
        ],
        "임상시험": [
            "효과적인 임상시험 설계를 위한 핵심 요소들을 알려주세요.",
            "임상시험 각 단계별 목적과 특징을 설명해주세요.",
            "임상시험에서 바이오마커의 역할과 중요성은 무엇인가요?"
        ],
        "분자 설계": [
            "새로운 약물의 작용기전을 어떻게 연구하고 검증할 수 있나요?",
            "Drug-likeness를 평가하는 주요 지표들은 무엇인가요?",
            "AI를 활용한 신약 설계의 현재 수준과 한계는 무엇인가요?"
        ],
        "규제 승인": [
            "FDA 승인을 위한 신약 개발 전략을 수립해주세요.",
            "글로벌 규제 당국별 신약 승인 요구사항의 차이점은 무엇인가요?",
            "희귀질환 치료제 개발을 위한 특별 승인 경로를 알려주세요."
        ]
    }


def format_message_display(message: Dict[str, str]) -> str:
    """메시지 표시 형식 포맷팅"""
    role = message["role"]
    content = message["content"]
    
    if role == "user":
        return f"""
        <div class="user-message">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">👤</span>
                <strong>사용자</strong>
                <span style="margin-left: auto; font-size: 0.8rem; opacity: 0.7;">
                    {datetime.now().strftime('%H:%M')}
                </span>
            </div>
            <div>{content}</div>
        </div>
        """
    else:
        return f"""
        <div class="bot-message">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">🧬</span>
                <strong>GAIA-BT</strong>
                <span style="margin-left: auto; font-size: 0.8rem; opacity: 0.7;">
                    {datetime.now().strftime('%H:%M')}
                </span>
            </div>
            <div>{content}</div>
        </div>
        """


def get_system_status() -> Dict[str, Any]:
    """시스템 상태 정보 반환"""
    return {
        "api_status": "온라인",
        "model_status": "활성화",
        "session_active": True,
        "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "version": "2.0.0"
    }