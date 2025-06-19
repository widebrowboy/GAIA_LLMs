# GAIA-BT v2.0 Alpha WebUI 개발 프로세스

## 📋 프로젝트 개요
GAIA-BT v2.0 Alpha 신약개발 연구 시스템에 웹 기반 사용자 인터페이스(WebUI)를 추가하여 더 직관적이고 접근성 높은 연구 환경을 제공합니다.

## 🎯 현재 상황 및 WebUI 필요성

### 현재 CLI 시스템 강점
- ✅ 완성도 높은 핵심 기능 (92-97% 완료)
- ✅ MCP 통합 다중 데이터베이스 접근
- ✅ 이중 모드 시스템 (일반/Deep Research)
- ✅ 프롬프트 관리 시스템
- ✅ 신약개발 전문 AI 어시스턴트

### WebUI 추가 필요성
- 🌐 웹 브라우저를 통한 범용 접근성
- 📊 시각적 데이터 표현 및 차트
- 🖱️ 직관적인 GUI 상호작용
- 📱 모바일/태블릿 반응형 지원
- 👥 다중 사용자 세션 관리
- 📈 실시간 연구 진행 상황 모니터링

## 🏗️ WebUI 아키텍처 설계

### 1. 기술 스택 선택

#### Frontend 기술 스택
```
Primary Stack:
- Framework: Next.js 14 (React 18 기반)
- UI Library: Tailwind CSS + Shadcn/ui
- State Management: Zustand
- HTTP Client: Axios
- WebSocket: Socket.io-client
- Charts: Recharts / Chart.js
- Markdown: react-markdown
- Icons: Lucide React
```

#### Backend API 계층
```
FastAPI 기반 REST API + WebSocket:
- Framework: FastAPI (Python 3.13+)
- WebSocket: FastAPI WebSocket
- CORS: FastAPI-CORS
- Authentication: JWT (옵션)
- API Documentation: OpenAPI/Swagger
```

#### 데이터베이스 (옵션)
```
Session & Chat History:
- SQLite (개발/소규모)
- PostgreSQL (프로덕션)
- Redis (세션 캐시)
```

### 2. 시스템 아키텍처

```
┌─────────────────────────────────────────────────┐
│                 Frontend                         │
│  ┌─────────────┐  ┌─────────────┐               │
│  │   Chat UI   │  │ Research UI │               │
│  └─────────────┘  └─────────────┘               │
│  ┌─────────────┐  ┌─────────────┐               │
│  │ Settings UI │  │ History UI  │               │
│  └─────────────┘  └─────────────┘               │
└─────────────────────────────────────────────────┘
                       │
              ┌─────────────────┐
              │   WebSocket     │ (실시간 통신)
              │   REST API      │ (데이터 조회)
              └─────────────────┘
                       │
┌─────────────────────────────────────────────────┐
│              Backend API Layer                   │
│  ┌─────────────┐  ┌─────────────┐               │
│  │ Chat API    │  │ Research API│               │
│  └─────────────┘  └─────────────┘               │
│  ┌─────────────┐  ┌─────────────┐               │
│  │ Config API  │  │ History API │               │
│  └─────────────┘  └─────────────┘               │
└─────────────────────────────────────────────────┘
                       │
┌─────────────────────────────────────────────────┐
│           Existing CLI System                    │
│  ┌─────────────┐  ┌─────────────┐               │
│  │ DrugDevelopment │ MCP Manager │               │
│  │   Chatbot    │               │               │
│  └─────────────┘  └─────────────┘               │
│  ┌─────────────┐  ┌─────────────┐               │
│  │ Ollama Client│ Research Mgr  │               │
│  └─────────────┘  └─────────────┘               │
└─────────────────────────────────────────────────┘
```

## 🔧 WebUI 개발 단계별 프로세스

### Phase 1: 기반 인프라 구축 (1-2주)

#### 1.1 프로젝트 구조 설정
```bash
# 디렉토리 구조 생성
mkdir -p webui/
cd webui/

# Frontend 구조
mkdir -p frontend/{src/{components,pages,hooks,utils,types,store},public}
mkdir -p frontend/src/components/{chat,research,settings,common}

# Backend API 구조
mkdir -p backend/{app/{api,core,models,utils},tests}
```

#### 1.2 패키지 초기화
```bash
# Frontend 패키지 설정
cd frontend/
npm create next-app@latest . --typescript --tailwind --eslint
npm install zustand axios socket.io-client react-markdown recharts lucide-react

# Backend 패키지 설정
cd ../backend/
pip install fastapi uvicorn websockets python-multipart
```

#### 1.3 개발 환경 설정
```yaml
# docker-compose.webui.yml
version: '3.8'
services:
  webui-frontend:
    build: ./webui/frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
  
  webui-backend:
    build: ./webui/backend
    ports:
      - "8000:8000"
    environment:
      - GAIA_CLI_PATH=/app
    volumes:
      - ./:/app
```

### Phase 2: 핵심 컴포넌트 개발 (2-3주)

#### 2.1 Backend API 개발
```python
# webui/backend/app/main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# GAIA-BT CLI 시스템 경로 추가
sys.path.append('/app')
from app.cli.chatbot import DrugDevelopmentChatbot
from mcp.integration.mcp_manager import MCPManager

app = FastAPI(title="GAIA-BT WebUI API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 챗봇 인스턴스
chatbot = None
mcp_manager = None

@app.on_event("startup")
async def startup_event():
    global chatbot, mcp_manager
    mcp_manager = MCPManager()
    chatbot = DrugDevelopmentChatbot(mcp_manager=mcp_manager)

# API 엔드포인트
@app.post("/api/chat")
async def chat_endpoint(message: dict):
    """채팅 메시지 처리"""
    response = await chatbot.process_message(message["content"])
    return {"response": response}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """실시간 채팅 WebSocket"""
    await websocket.accept()
    # 실시간 채팅 처리 로직
```

#### 2.2 Frontend 핵심 컴포넌트
```typescript
// webui/frontend/src/components/chat/ChatInterface.tsx
import { useState, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { ResearchPanel } from '../research/ResearchPanel';

export const ChatInterface = () => {
  const { messages, sendMessage, isLoading, currentMode } = useChat();

  return (
    <div className="flex h-screen">
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-4">
          <MessageList messages={messages} />
        </div>
        <MessageInput 
          onSendMessage={sendMessage}
          disabled={isLoading}
          currentMode={currentMode}
        />
      </div>
      {currentMode === 'deep_research' && (
        <ResearchPanel className="w-80 border-l" />
      )}
    </div>
  );
};
```

#### 2.3 상태 관리 시스템
```typescript
// webui/frontend/src/store/chatStore.ts
import { create } from 'zustand';

interface ChatState {
  messages: Message[];
  currentMode: 'normal' | 'deep_research';
  isLoading: boolean;
  mcpOutputVisible: boolean;
  currentPromptMode: string;
  // Actions
  addMessage: (message: Message) => void;
  setMode: (mode: 'normal' | 'deep_research') => void;
  toggleMCPOutput: () => void;
  setPromptMode: (mode: string) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  currentMode: 'normal',
  isLoading: false,
  mcpOutputVisible: false,
  currentPromptMode: 'default',
  // Actions implementation
}));
```

### Phase 3: 통합 및 고급 기능 (2-3주)

#### 3.1 CLI 시스템 통합 어댑터
```python
# webui/backend/app/core/cli_adapter.py
import asyncio
from typing import Dict, Any, AsyncGenerator
from app.cli.chatbot import DrugDevelopmentChatbot
from app.utils.config import Config

class CLIAdapter:
    """CLI 시스템과 WebUI 간의 어댑터 클래스"""
    
    def __init__(self):
        self.chatbot = None
        self.config = Config()
    
    async def initialize(self):
        """챗봇 초기화"""
        self.chatbot = DrugDevelopmentChatbot()
        await self.chatbot.initialize()
    
    async def process_message(self, message: str, mode: str = 'normal') -> AsyncGenerator[Dict[str, Any], None]:
        """메시지 처리 및 스트리밍 응답"""
        if not self.chatbot:
            await self.initialize()
        
        # 모드 설정
        if mode == 'deep_research':
            await self.chatbot.enable_mcp()
        else:
            await self.chatbot.disable_mcp()
        
        # 스트리밍 응답 생성
        async for chunk in self.chatbot.stream_response(message):
            yield {
                'type': 'response_chunk',
                'content': chunk,
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_research_progress(self) -> Dict[str, Any]:
        """연구 진행 상황 조회"""
        if self.chatbot and hasattr(self.chatbot, 'research_manager'):
            return await self.chatbot.research_manager.get_progress()
        return {}
```

#### 3.2 실시간 연구 진행 모니터링
```typescript
// webui/frontend/src/components/research/ResearchMonitor.tsx
import { useEffect, useState } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export const ResearchMonitor = () => {
  const [progress, setProgress] = useState(null);
  const { socket } = useWebSocket();

  useEffect(() => {
    if (socket) {
      socket.on('research_progress', setProgress);
    }
  }, [socket]);

  if (!progress) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>🔬 Deep Research 진행 상황</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {progress.steps.map((step, index) => (
            <div key={index} className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>{step.name}</span>
                <span>{step.progress}%</span>
              </div>
              <Progress value={step.progress} className="h-2" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
```

#### 3.3 MCP 검색 결과 시각화
```typescript
// webui/frontend/src/components/research/MCPResults.tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export const MCPResults = ({ results }) => {
  return (
    <Tabs defaultValue="pubmed" className="w-full">
      <TabsList className="grid w-full grid-cols-4">
        <TabsTrigger value="pubmed">PubMed</TabsTrigger>
        <TabsTrigger value="chembl">ChEMBL</TabsTrigger>
        <TabsTrigger value="clinical">Clinical</TabsTrigger>
        <TabsTrigger value="variants">Variants</TabsTrigger>
      </TabsList>
      
      {Object.entries(results).map(([source, data]) => (
        <TabsContent key={source} value={source}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {source.toUpperCase()} 검색 결과
                <Badge variant="secondary">{data.count}건</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {data.items.map((item, index) => (
                  <div key={index} className="border-l-4 border-blue-500 pl-4">
                    <h4 className="font-semibold">{item.title}</h4>
                    <p className="text-sm text-gray-600">{item.summary}</p>
                    <div className="flex gap-2 mt-2">
                      {item.tags?.map(tag => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      ))}
    </Tabs>
  );
};
```

### Phase 4: 고급 기능 및 최적화 (2-3주)

#### 4.1 대화 히스토리 관리
```python
# webui/backend/app/models/chat_history.py
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(50), unique=True, index=True)
    title = Column(String(200))
    mode = Column(String(20), default='normal')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(50), index=True)
    role = Column(String(20))  # 'user' or 'assistant'
    content = Column(Text)
    metadata = Column(JSON)  # MCP 결과, 연구 데이터 등
    timestamp = Column(DateTime, default=datetime.utcnow)
```

#### 4.2 반응형 UI 컴포넌트
```typescript
// webui/frontend/src/components/layout/ResponsiveLayout.tsx
import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

export const ResponsiveLayout = ({ children }) => {
  const [isMobile, setIsMobile] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div className="h-screen flex">
      {/* Sidebar */}
      <aside className={cn(
        "bg-gray-50 border-r transition-all duration-300",
        isMobile ? (sidebarOpen ? "w-64" : "w-0") : "w-64"
      )}>
        <ChatHistory />
        <Settings />
      </aside>
      
      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        <header className="border-b p-4 flex items-center gap-4">
          {isMobile && (
            <button onClick={() => setSidebarOpen(!sidebarOpen)}>
              ☰
            </button>
          )}
          <h1>GAIA-BT 신약개발 연구 어시스턴트</h1>
        </header>
        <div className="flex-1">
          {children}
        </div>
      </main>
    </div>
  );
};
```

#### 4.3 데이터 시각화 컴포넌트
```typescript
// webui/frontend/src/components/visualization/ResearchChart.tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const ResearchChart = ({ data, title }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
```

## 🔗 기존 CLI 시스템과의 통합 방안

### 1. API 브리지 패턴
```python
# webui/backend/app/core/bridge.py
from typing import Dict, Any, Optional
import asyncio
from contextlib import asynccontextmanager

class GaiaCLIBridge:
    """CLI 시스템과 WebUI 간의 브리지 클래스"""
    
    def __init__(self):
        self.cli_instance = None
        self.active_sessions = {}
    
    @asynccontextmanager
    async def get_cli_session(self, session_id: str):
        """CLI 세션 컨텍스트 매니저"""
        if session_id not in self.active_sessions:
            from app.cli.chatbot import DrugDevelopmentChatbot
            self.active_sessions[session_id] = DrugDevelopmentChatbot()
            await self.active_sessions[session_id].initialize()
        
        try:
            yield self.active_sessions[session_id]
        finally:
            # 세션 정리 로직 (필요시)
            pass
    
    async def execute_command(self, session_id: str, command: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
        """CLI 명령어 실행"""
        async with self.get_cli_session(session_id) as cli:
            if command == 'chat':
                return await cli.process_message(args.get('message', ''))
            elif command == 'mcp_start':
                return await cli.enable_mcp()
            elif command == 'mcp_stop':
                return await cli.disable_mcp()
            elif command == 'prompt_change':
                return await cli.change_prompt_mode(args.get('mode', 'default'))
            else:
                raise ValueError(f"Unknown command: {command}")
```

### 2. 상태 동기화 시스템
```typescript
// webui/frontend/src/hooks/useCliSync.ts
import { useEffect, useRef } from 'react';
import { useChatStore } from '@/store/chatStore';

export const useCliSync = (sessionId: string) => {
  const { setMode, setPromptMode, toggleMCPOutput } = useChatStore();
  const wsRef = useRef<WebSocket>();

  useEffect(() => {
    // CLI 상태 동기화 WebSocket 연결
    wsRef.current = new WebSocket(`ws://localhost:8000/ws/sync/${sessionId}`);
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'mode_changed':
          setMode(data.mode);
          break;
        case 'prompt_changed':
          setPromptMode(data.prompt_mode);
          break;
        case 'mcp_output_toggled':
          toggleMCPOutput();
          break;
      }
    };

    return () => {
      wsRef.current?.close();
    };
  }, [sessionId]);

  const syncCommand = (command: string, args?: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ command, args }));
    }
  };

  return { syncCommand };
};
```

### 3. 설정 공유 시스템
```python
# webui/backend/app/core/config_sync.py
import json
from pathlib import Path
from app.utils.config import Config

class ConfigSync:
    """CLI와 WebUI 간 설정 동기화"""
    
    def __init__(self):
        self.cli_config = Config()
        self.webui_config_path = Path("webui/config/webui.json")
    
    def sync_from_cli(self) -> Dict[str, Any]:
        """CLI 설정을 WebUI로 동기화"""
        return {
            'ollama_url': self.cli_config.OLLAMA_BASE_URL,
            'default_model': self.cli_config.DEFAULT_MODEL,
            'mcp_enabled': self.cli_config.MCP_ENABLED,
            'show_mcp_output': self.cli_config.show_mcp_output,
            'current_prompt_mode': self.cli_config.current_prompt_mode,
        }
    
    def sync_to_cli(self, webui_config: Dict[str, Any]):
        """WebUI 설정을 CLI로 동기화"""
        # CLI 설정 업데이트 로직
        pass
```

## 📦 배포 및 실행 방안

### 1. Docker 컨테이너화
```dockerfile
# webui/Dockerfile
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.13-slim AS backend-builder
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.13-slim
WORKDIR /app

# Copy backend
COPY webui/backend/ ./webui/backend/
COPY app/ ./app/
COPY mcp/ ./mcp/
COPY config/ ./config/
COPY prompts/ ./prompts/

# Copy frontend build
COPY --from=frontend-builder /app/frontend/out ./webui/frontend/out

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "webui.backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 통합 실행 스크립트
```bash
#!/bin/bash
# scripts/run_webui.sh

echo "🌐 GAIA-BT WebUI 시작 중..."

# MCP 서버 시작
echo "🔧 MCP 서버 시작 중..."
./scripts/run_mcp_servers.sh

# WebUI 서버 시작
echo "🚀 WebUI 서버 시작 중..."
if [ "$1" = "--docker" ]; then
    docker-compose -f docker-compose.webui.yml up -d
else
    # 개발 모드
    cd webui/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    cd webui/frontend && npm run dev &
fi

echo "✅ GAIA-BT WebUI가 실행되었습니다:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API 문서: http://localhost:8000/docs"
```

### 3. 개발 환경 설정
```json
{
  "scripts": {
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\"",
    "dev:backend": "cd webui/backend && uvicorn app.main:app --reload",
    "dev:frontend": "cd webui/frontend && next dev",
    "build": "cd webui/frontend && npm run build",
    "start": "cd webui/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000",
    "docker:build": "docker build -t gaia-bt-webui .",
    "docker:run": "docker run -p 8000:8000 gaia-bt-webui"
  }
}
```

## 🎯 우선순위 및 마일스톤

### 🚀 Phase 1: MVP (Minimum Viable Product) - 2주
- [ ] 기본 채팅 인터페이스
- [ ] CLI 시스템 통합 어댑터
- [ ] 일반/Deep Research 모드 전환
- [ ] 기본 설정 관리

### 🔧 Phase 2: 핵심 기능 - 3주
- [ ] MCP 검색 결과 시각화
- [ ] 실시간 연구 진행 모니터링
- [ ] 대화 히스토리 관리
- [ ] 프롬프트 모드 관리

### 📊 Phase 3: 고급 기능 - 2주
- [ ] 데이터 시각화 대시보드
- [ ] 반응형 모바일 지원
- [ ] 연구 보고서 내보내기
- [ ] 사용자 세션 관리

### 🚀 Phase 4: 최적화 및 배포 - 1주
- [ ] 성능 최적화
- [ ] Docker 컨테이너화
- [ ] 배포 자동화
- [ ] 문서화 완료

## 📋 기술적 고려사항

### 보안
- JWT 기반 인증 (옵션)
- CORS 정책 설정
- API 요청 제한 (Rate Limiting)
- 민감한 정보 암호화

### 성능
- 프론트엔드 코드 스플리팅
- API 응답 캐싱
- WebSocket 연결 최적화
- 대용량 데이터 페이지네이션

### 확장성
- 모듈화된 컴포넌트 설계
- 플러그인 아키텍처
- 다중 언어 지원 준비
- 테마 시스템

## 🎨 UI/UX 설계 원칙

### 1. 신약개발 도메인 특화
- 과학적 데이터 중심의 시각적 표현
- 의학/생물학 용어 도움말 시스템
- 연구 워크플로우 기반 네비게이션

### 2. 사용자 경험 최적화
- 직관적인 채팅 인터페이스
- 실시간 피드백 시스템
- 모바일 친화적 반응형 디자인
- 접근성 (a11y) 준수

### 3. 기존 CLI 사용자 고려
- 키보드 단축키 지원
- CLI 명령어 호환성
- 설정 마이그레이션 도구

## 🔄 마이그레이션 전략

### 단계적 도입
1. **병행 운영**: CLI와 WebUI 동시 지원
2. **점진적 기능 이관**: 핵심 기능부터 순차 이관
3. **사용자 피드백 반영**: 베타 테스트 기반 개선

### 데이터 호환성
- 기존 연구 결과 파일 호환
- 설정 파일 자동 마이그레이션
- 대화 히스토리 가져오기

## 📚 문서화 계획

### 개발 문서
- API 문서 (OpenAPI/Swagger)
- 컴포넌트 스토리북
- 개발 환경 설정 가이드

### 사용자 문서
- WebUI 사용자 매뉴얼
- 기능별 튜토리얼
- 마이그레이션 가이드

## 🎯 성공 지표 (KPI)

### 기술적 지표
- [ ] 응답 시간 < 2초
- [ ] 모바일 성능 점수 > 85
- [ ] API 가용성 > 99%
- [ ] 메모리 사용량 최적화

### 사용자 경험 지표
- [ ] 사용자 만족도 조사
- [ ] 기능 사용률 분석
- [ ] 에러 발생률 < 1%
- [ ] 학습 곡선 단축

---

## 📞 연락처 및 지원

개발 과정에서 질문이나 지원이 필요한 경우:
- GitHub Issues 활용
- 개발 문서 참조
- 팀 내 코드 리뷰 진행

---

이 문서는 GAIA-BT v2.0 Alpha WebUI 개발의 전체 로드맵을 제시하며, 개발 진행에 따라 지속적으로 업데이트됩니다.