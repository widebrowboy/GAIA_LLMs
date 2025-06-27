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

async def _get_ollama_running_models() -> List[Dict[str, Any]]:
    """현재 실행 중인 Ollama 모델 목록 조회"""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get("http://localhost:11434/api/ps")
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
    except Exception:
        return []

async def _get_ollama_model_details() -> Dict[str, Any]:
    """전체 Ollama 모델 정보 조회 (설치된 모델 + 실행 중인 모델)"""
    try:
        available_models = []
        running_models = []
        
        # 설치된 모델 목록
        async with httpx.AsyncClient(timeout=3.0) as client:
            # 설치된 모델
            tags_response = await client.get("http://localhost:11434/api/tags")
            if tags_response.status_code == 200:
                tags_data = tags_response.json()
                for model in tags_data.get("models", []):
                    available_models.append({
                        "name": model["name"],
                        "size": model.get("size", 0),
                        "modified_at": model.get("modified_at", ""),
                        "digest": model.get("digest", "")[:12] + "...",
                        "parameter_size": model.get("details", {}).get("parameter_size", "Unknown")
                    })
            
            # 실행 중인 모델
            ps_response = await client.get("http://localhost:11434/api/ps")
            if ps_response.status_code == 200:
                ps_data = ps_response.json()
                for model in ps_data.get("models", []):
                    running_models.append({
                        "name": model["name"],
                        "size_vram": model.get("size_vram", 0),
                        "expires_at": model.get("expires_at", ""),
                        "is_running": True
                    })
        
        return {
            "available": available_models,
            "running": running_models,
            "status": "success"
        }
    except Exception as e:
        return {
            "available": [],
            "running": [],
            "status": "error",
            "error": str(e)
        }

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
        # templates 프로퍼티 AttributeError 등 모든 예외 방지
        "available_prompts": (lambda: (
            list(prompt_manager.templates.keys()) if hasattr(prompt_manager, 'templates') and isinstance(prompt_manager.templates, dict)
            else []
        ))()
    }

@router.post("/model")
async def change_model(
    request: ModelChangeRequest,
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """AI 모델 변경 및 Ollama 실행 보장"""
    chatbot = service.get_session(request.session_id)
    if not chatbot:
        raise HTTPException(404, f"세션 {request.session_id}를 찾을 수 없습니다")
    
    try:
        # 먼저 요청된 모델이 Ollama에 설치되어 있는지 확인
        available_models = await _get_ollama_models()
        if request.model not in available_models:
            raise HTTPException(400, f"모델 '{request.model}'이 Ollama에 설치되어 있지 않습니다. 설치된 모델: {available_models}")
        
        # 1) Ollama에서 모델 실행 보장 (먼저 실행)
        try:
            from app.utils.ollama_manager import ensure_single_model_running
            await ensure_single_model_running(request.model)
        except Exception as proc_err:
            raise HTTPException(500, f"Ollama 모델 실행 실패: {proc_err}")
        
        # 2) Chatbot 내부 모델 교체
        result = await chatbot.change_model(request.model)
        
        # 3) 모델 실행 상태 재확인
        running_models = await _get_ollama_running_models()
        model_running = any(model["name"] == request.model for model in running_models)
        
        return {
            "success": True,
            "model": chatbot.client.model_name,
            "model_running": model_running,
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

@router.get("/models/detailed")
async def get_detailed_models(
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """상세한 모델 정보 가져오기 (설치된 모델 + 실행 중인 모델)"""
    model_details = await _get_ollama_model_details()
    current_model = service.current_model
    
    # 현재 선택된 모델이 실행 중인지 확인
    current_model_running = any(
        model["name"] == current_model 
        for model in model_details.get("running", [])
    )
    
    return {
        **model_details,
        "current_model": current_model,
        "current_model_running": current_model_running
    }

@router.get("/models/running")
async def get_running_models() -> Dict[str, Any]:
    """현재 실행 중인 모델 목록 가져오기"""
    running_models = await _get_ollama_running_models()
    
    return {
        "running_models": running_models,
        "count": len(running_models),
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

@router.post("/startup")
async def system_startup(
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """시스템 시작 시 기본 모델 자동 시작"""
    try:
        # 기본 세션이 없으면 생성
        chatbot = service.get_session("default")
        if not chatbot:
            session_result = await service.create_session("default")
            if "error" in session_result:
                return {"success": False, "error": session_result["error"]}
            chatbot = service.get_session("default")
        
        # Ollama 연결 상태 확인 및 모델 시작
        if chatbot:
            connection_status = await chatbot.client.check_ollama_connection()
            if connection_status["connected"]:
                if not connection_status.get("current_model_running", False):
                    # 모델이 실행되지 않은 경우 자동 시작
                    start_result = await chatbot.client.ensure_model_running()
                    if start_result["success"]:
                        return {
                            "success": True,
                            "message": f"기본 모델 '{service.current_model}' 시작 완료",
                            "model": service.current_model,
                            "model_started": start_result["model_started"]
                        }
                    else:
                        return {
                            "success": False,
                            "error": start_result["message"]
                        }
                else:
                    return {
                        "success": True,
                        "message": f"모델 '{service.current_model}' 이미 실행 중",
                        "model": service.current_model,
                        "model_started": False
                    }
            else:
                return {
                    "success": False,
                    "error": connection_status["error"]
                }
        
        return {"success": False, "error": "세션 생성 실패"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/startup-validation")
async def get_startup_validation() -> Dict[str, Any]:
    """API 서버 시작 시 Ollama 검증 결과 조회"""
    from fastapi import Request
    from app.api_server.main import app
    
    # 애플리케이션 상태에서 검증 결과 가져오기
    validation_result = getattr(app.state, 'ollama_validation', None)
    
    if validation_result:
        return {
            "status": "success",
            "validation_result": validation_result,
            "message": "시작 시 Ollama 검증 정보 조회 성공"
        }
    else:
        return {
            "status": "not_available",
            "message": "시작 시 검증 정보를 찾을 수 없습니다"
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