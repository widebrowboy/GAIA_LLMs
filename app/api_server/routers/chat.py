"""
Chat Router - 채팅 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.api_server.dependencies import get_chatbot_service
from app.api_server.services.chatbot_service import ChatbotService

router = APIRouter()

class ChatRequest(BaseModel):
    """💬 채팅 요청 모델"""
    message: str = Field(
        ..., 
        description="사용자가 입력한 메시지",
        example="아스피린의 작용 메커니즘을 설명해주세요",
        min_length=1,
        max_length=4000
    )
    session_id: str = Field(
        default="default",
        description="세션 ID (다중 대화 세션 지원)",
        example="my_research_session",
        pattern="^[a-zA-Z0-9_-]+$"
    )
    stream: bool = Field(
        default=False,
        description="스트리밍 응답 여부 (이 엔드포인트에서는 미지원)"
    )
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="대화 히스토리 (role과 content를 포함하는 메시지 목록)",
        example=[
            {"role": "user", "content": "안녕하세요"},
            {"role": "assistant", "content": "안녕하세요! 신약개발에 대해 무엇을 도와드릴까요?"}
        ]
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "message": "아스피린의 작용 메커니즘을 설명해주세요",
                    "session_id": "default"
                },
                {
                    "message": "BRCA1 유전자 변이와 유방암 치료제 개발에 대해 알려주세요",
                    "session_id": "cancer_research"
                },
                {
                    "message": "임상시험 1상과 2상의 차이점은 무엇인가요?",
                    "session_id": "clinical_study"
                }
            ]
        }

class ChatResponse(BaseModel):
    """✅ 채팅 응답 모델"""
    response: str = Field(
        ...,
        description="AI가 생성한 응답 텍스트",
        example="아스피린은 COX-1과 COX-2 효소를 억제하여..."
    )
    mode: str = Field(
        ...,
        description="현재 모드 (normal/deep_research)",
        example="normal"
    )
    model: str = Field(
        ...,
        description="사용된 AI 모델명",
        example="Gemma3:27b-it-q4_K_M"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "response": "아스피린(아세틸살리실산)은 비스테로이드성 항염제(NSAID)로, 주요 작용 메커니즘은 시클로옥시게나제(COX) 효소의 억제입니다...",
                "mode": "normal", 
                "model": "Gemma3:27b-it-q4_K_M"
            }
        }

class CommandRequest(BaseModel):
    """⚡ 명령어 요청 모델"""
    command: str = Field(
        ...,
        description="실행할 명령어",
        example="/mcp start",
        min_length=1
    )
    session_id: str = Field(
        default="default",
        description="세션 ID",
        example="default",
        pattern="^[a-zA-Z0-9_-]+$"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "command": "/mcp start",
                    "session_id": "default"
                },
                {
                    "command": "/prompt clinical",
                    "session_id": "research_session"
                },
                {
                    "command": "/model gemma3:latest",
                    "session_id": "default"
                }
            ]
        }

@router.post("/message", 
             response_model=ChatResponse,
             summary="💬 채팅 메시지 전송",
             description="""
## 📝 채팅 메시지 전송

AI와 일반적인 대화를 진행합니다. 신약개발 관련 질문에 전문적인 답변을 제공합니다.

### 🎯 주요 기능
- **전문 AI 답변**: 신약개발 도메인에 특화된 응답
- **세션 관리**: 독립적인 대화 컨텍스트 유지
- **즉시 응답**: 실시간 텍스트 응답 (비스트리밍)

### 📊 응답 모드
- **Normal Mode**: 빠른 기본 AI 응답
- **Deep Research Mode**: MCP 활성화 시 데이터베이스 검색 포함

### 💡 사용 예시

**기본 질문:**
```json
{
  "message": "아스피린의 부작용은 무엇인가요?",
  "session_id": "default"
}
```

**연구 질문:**
```json
{
  "message": "EGFR 표적 항암제의 최신 임상시험 결과를 분석해주세요",
  "session_id": "oncology_research"
}
```

**의약화학 질문:**
```json
{
  "message": "벤조디아제핀 계열의 구조-활성 관계를 설명해주세요",
  "session_id": "medicinal_chemistry"
}
```
             """,
             response_description="AI가 생성한 답변과 메타데이터")
async def send_message(
    request: ChatRequest,
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """
    AI와의 채팅 메시지 교환을 처리합니다.
    
    - **message**: 사용자 질문 (1-4000자)
    - **session_id**: 세션 식별자 (영문, 숫자, _, - 만 허용)
    - **stream**: False 고정 (스트리밍은 /stream 사용)
    """
    if request.stream:
        # 스트리밍 응답은 별도 엔드포인트 사용
        raise HTTPException(400, "스트리밍은 /stream 엔드포인트를 사용하세요")
    
    result = await service.generate_response(request.session_id, request.message, request.conversation_history)
    
    if "error" in result:
        raise HTTPException(400, result["error"])
    
    return result

@router.post("/stream",
             summary="🌊 스트리밍 채팅",
             description="""
## 🌊 실시간 스트리밍 채팅

AI 응답을 실시간으로 스트리밍하여 자연스러운 대화 경험을 제공합니다.

### ⚡ 스트리밍 특징
- **실시간 응답**: 단어별 점진적 표시
- **자연스러운 UX**: 마치 사람과 대화하는 듯한 경험
- **중단 가능**: 클라이언트에서 연결 종료 시 즉시 중단

### 📡 응답 형식
Server-Sent Events (SSE) 형식으로 데이터 전송:

```
data: 아스피린은
data: 비스테로이드성
data: 항염제로서
data: [DONE]
```

### 🔌 JavaScript 사용 예시
```javascript
const response = await fetch('/api/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "아스피린의 작용 메커니즘은?",
    session_id: "default"
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = line.slice(6);
      if (data === '[DONE]') {
        console.log('응답 완료');
        break;
      }
      console.log('받은 청크:', data);
    }
  }
}
```
             """,
             response_class=StreamingResponse)
async def stream_message(
    request: ChatRequest,
    service: ChatbotService = Depends(get_chatbot_service)
):
    """
    실시간 스트리밍으로 AI 응답을 전송합니다.
    
    Server-Sent Events (SSE) 형식으로 응답을 스트리밍하며,
    클라이언트에서 실시간으로 AI의 사고 과정을 확인할 수 있습니다.
    """
    async def generate():
        async for chunk in service.generate_streaming_response(
            request.message, 
            request.session_id
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept"
        }
    )

@router.options("/stream", 
                summary="CORS Preflight for streaming",
                response_class=JSONResponse)
async def stream_options():
    """CORS preflight 요청 처리"""
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept",
            "Access-Control-Max-Age": "3600"
        }
    )

@router.post("/command",
             summary="⚡ 명령어 실행",
             description="""
## ⚡ 시스템 명령어 실행

챗봇의 다양한 기능을 제어하는 명령어를 실행합니다.

### 🛠️ 사용 가능한 명령어

#### 기본 제어
- `/help` - 도움말 표시
- `/debug` - 디버그 모드 토글
- `/normal` - 일반 모드로 전환

#### 모델 관리  
- `/model gemma3:latest` - AI 모델 변경
- `/model list` - 사용 가능한 모델 목록

#### 프롬프트 관리
- `/prompt clinical` - 임상시험 전문 모드
- `/prompt research` - 연구 분석 전문 모드  
- `/prompt chemistry` - 의약화학 전문 모드
- `/prompt regulatory` - 규제 전문 모드

#### MCP Deep Research
- `/mcp start` - Deep Research 모드 활성화
- `/mcp stop` - MCP 서버 중지
- `/mcp status` - MCP 상태 확인
- `/mcpshow` - MCP 출력 표시 토글

### 💡 사용 예시
```bash
curl -X POST "/api/chat/command" \\
  -H "Content-Type: application/json" \\
  -d '{"command": "/mcp start", "session_id": "research_session"}'
```
             """)
async def send_command(
    request: CommandRequest,
    service: ChatbotService = Depends(get_chatbot_service)
) -> Dict[str, Any]:
    """
    시스템 명령어를 실행하여 챗봇의 동작을 제어합니다.
    
    명령어를 통해 모드 전환, 설정 변경, MCP 제어 등의 작업을 수행할 수 있습니다.
    """
    result = await service.process_command(request.command, request.session_id)
    
    if "error" in result:
        raise HTTPException(400, result["error"])
    
    return result