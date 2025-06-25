"""
System Router - 시스템 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel

from app.api_server.dependencies import get_chatbot_service
from app.api_server.services.chatbot_service import ChatbotService
from app.utils.config import OLLAMA_MODEL, DEBUG_MODE
import httpx
from app.utils.ollama_manager import ensure_single_model_running
from app.utils.prompt_manager import get_prompt_manager

router = APIRouter()

# 공통 함수
async def _get_ollama_models() -> List[str]:
    """Ollama에서 사용 가능한 모델 목록 조회"""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
    except Exception:
        # 기본 모델 목록으로 폴백
        return ["gemma3:latest", "llama3.2:latest", "mistral:latest"]

class SystemInfo(BaseModel):
    """시스템 정보 모델"""
    version: str = "2.0.0"
    model: str
    mode: str
    mcp_enabled: bool
    debug: bool
    available_models: List[str]
    available_prompts: List[str]

class ModelChangeRequest(BaseModel):
    """모델 변경 요청"""
    model: str
    session_id: str = "default"

class PromptChangeRequest(BaseModel):
    """프롬프트 변경 요청"""
    prompt_type: str
    session_id: str = "default"

@router.get("/info", response_model=SystemInfo)
async def get_system_info(
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """시스템 정보 조회"""
    prompt_manager = get_prompt_manager()
    
    # 사용 가능한 모델 목록 동적 조회
    available_models = await _get_ollama_models()
    
    return {
        "version": "2.0.0",
        "model": service.current_model,
        "mode": service.current_mode,
        "mcp_enabled": service.mcp_enabled,
        "debug": service.debug_mode,
        "available_models": available_models,
        "available_prompts": list(prompt_manager.templates.keys())
    }

@router.post("/model")
async def change_model(
    request: ModelChangeRequest,
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """AI 모델 변경"""
    chatbot = service.get_session(request.session_id)
    if not chatbot:
        raise HTTPException(404, f"세션 {request.session_id}를 찾을 수 없습니다")
    
    try:
        # 1) Chatbot 내부 모델 교체
        result = await chatbot.change_model(request.model)
        # 2) Ollama 프로세스 보장 – 요청한 모델만 실행되도록 관리
        try:
            from app.utils.ollama_manager import ensure_models_running
            await ensure_models_running(["gemma3-12b:latest", chatbot.client.model_name])
        except Exception as proc_err:
            raise HTTPException(500, f"모델 프로세스 관리 실패: {proc_err}")
        return {
            "success": True,
            "model": chatbot.client.model_name,
            "message": result
        }
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/prompt")
async def change_prompt(
    request: PromptChangeRequest,
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """프롬프트 타입 변경"""
    chatbot = service.get_session(request.session_id)
    if not chatbot:
        raise HTTPException(404, f"세션 {request.session_id}를 찾을 수 없습니다")
    
    try:
        # 프롬프트 매니저 다시 로드하여 최신 프롬프트 파일 적용
        from app.utils.prompt_manager import get_prompt_manager
        prompt_manager = get_prompt_manager()
        prompt_manager.reload_prompts()
        
        result = await chatbot.change_prompt(request.prompt_type)
        return {
            "success": True,
            "prompt_type": chatbot.current_prompt_type,
            "message": result
        }
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/debug")
async def toggle_debug(
    session_id: str = "default",
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """디버그 모드 토글"""
    result = await service.process_command("/debug", session_id)
    return result

@router.post("/mode/{mode}")
async def change_mode(
    mode: str,
    session_id: str = "default",
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """모드 변경 (normal/deep_research)"""
    if mode not in ["normal", "deep_research"]:
        raise HTTPException(400, "유효하지 않은 모드입니다")
    
    if mode == "normal":
        result = await service.process_command("/normal", session_id)
    else:
        result = await service.process_command("/mcp start", session_id)
    
    return result

@router.get("/models")
async def get_available_models(
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """사용 가능한 모델 목록 가져오기"""
    models = await _get_ollama_models()
    
    return {
        "models": models,
        "default": service.current_model,
        "status": "success"
    }

@router.get("/health")
async def health_check(
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """시스템 상태 체크 엔드포인트"""
    prompt_manager = get_prompt_manager()
    
    return {
        "status": "ok",
        "model": service.current_model,
        "mode": service.current_mode,
        "mcp_enabled": service.mcp_enabled,
        "debug": service.debug_mode
    }

@router.get("/startup-banner")
async def get_startup_banner(
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """시작 배너 정보 가져오기"""
    prompt_manager = get_prompt_manager()
    default_prompt = prompt_manager.get_prompt_template("default")
    prompt_desc = default_prompt.description if default_prompt else "신약개발 전문 AI"
    
    return {
        "version": "2.0.0",
        "model": service.current_model,
        "prompt_type": "default",
        "prompt_description": prompt_desc,
        "features": [
            "💊 신약개발 전문 AI - 분자부터 임상까지 전 과정 지원",
            "🧬 과학적 근거 기반 답변 - 참고문헌과 함께 제공",
            "🎯 전문 프롬프트 시스템 - 목적에 맞는 전문화된 응답"
        ]
    }