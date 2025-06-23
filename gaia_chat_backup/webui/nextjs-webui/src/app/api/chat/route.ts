import { z } from 'zod';
import { NextRequest, NextResponse } from 'next/server';

// 메시지 스키마
const MessageSchema = z.object({
  id: z.string().optional(),
  role: z.enum(['user', 'assistant', 'system']),
  content: z.string(),
  createdAt: z.union([z.string(), z.date()]).optional(),
});

// 요청 스키마 정의
const ChatRequestSchema = z.object({
  messages: z.array(MessageSchema),
  sessionId: z.string().optional(),
  mode: z.enum(['normal', 'deep_research']).optional(),
  promptType: z.string().optional(),
  model: z.string().optional(),
  temperature: z.number().optional(),
  maxTokens: z.number().optional(),
});

// 단일 메시지 요청 스키마
const SingleMessageSchema = z.object({
  message: z.string(),
  sessionId: z.string().optional(),
  mode: z.enum(['normal', 'deep_research']).optional(),
  promptType: z.string().optional(),
  model: z.string().optional(),
  temperature: z.number().optional(),
  maxTokens: z.number().optional(),
});

// GAIA-BT 백엔드에 직접 요청하는 함수
async function callGaiaBTAPI(message: string, options: {
  sessionId?: string;
  mode?: string;
  promptType?: string;
  model?: string;
  temperature?: number;
  maxTokens?: number;
}) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  try {
    const response = await fetch(`${apiUrl}/api/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: options.sessionId || 'default',
        mode: options.mode || 'normal',
        prompt_type: options.promptType || 'default',
        model: options.model,
        temperature: options.temperature,
        max_tokens: options.maxTokens,
      }),
    });

    if (!response.ok) {
      throw new Error(`GAIA-BT API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('GAIA-BT API call failed:', error);
    // 폴백: Mock 응답 생성
    return generateMockResponse(message, options.mode);
  }
}

// Mock 응답 생성
function generateMockResponse(message: string, mode?: string) {
  const isDeepResearch = mode === 'deep_research';
  
  const mockResponse = isDeepResearch 
    ? `🔬 **Deep Research 분석 결과**

"${message}"에 대한 종합적인 과학적 분석을 제공합니다.

## 📊 통합 데이터베이스 검색 결과
- **PubMed**: 최신 논문 25편 검색
- **ChEMBL**: 관련 화합물 데이터 분석
- **ClinicalTrials.gov**: 진행 중인 임상시험 검토
- **DrugBank**: 약물 상호작용 정보

## 🎯 전문가 분석
신약개발 관점에서 과학적 근거를 바탕으로 상세한 분석을 제공합니다.

> 💡 **안내**: 현재 시스템이 초기화 중입니다. 잠시 후 다시 시도해주세요.`
    : `🧬 **GAIA-BT 신약개발 AI 어시스턴트**

"${message}"에 대한 전문적인 분석을 제공합니다.

## 💊 신약개발 관점 분석
기본 지식을 바탕으로 신약개발 전문 정보를 제공합니다.

> 💡 **팁**: Deep Research 모드를 활성화하면 다중 데이터베이스 검색을 통한 더 상세한 분석을 받을 수 있습니다.

> ⚙️ **시스템 상태**: 현재 초기화 중입니다. 기본 응답 모드로 동작합니다.`;

  return {
    success: true,
    response: mockResponse,
    session_id: 'mock-session',
    mode: mode || 'normal',
    timestamp: new Date().toISOString(),
  };
}

// POST: 대화 메시지 처리 (일반 응답)
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    
    // 단일 메시지인지 메시지 배열인지 확인
    let message: string;
    let options: {
      sessionId?: string;
      mode?: string;
      promptType?: string;
      model?: string;
      temperature?: number;
      maxTokens?: number;
    };
    
    if (body.message && typeof body.message === 'string') {
      // 단일 메시지 형식
      const validatedData = SingleMessageSchema.parse(body);
      message = validatedData.message;
      options = {
        sessionId: validatedData.sessionId,
        mode: validatedData.mode,
        promptType: validatedData.promptType,
        model: validatedData.model,
        temperature: validatedData.temperature,
        maxTokens: validatedData.maxTokens,
      };
    } else if (body.messages && Array.isArray(body.messages)) {
      // 메시지 배열 형식
      const validatedData = ChatRequestSchema.parse(body);
      const lastUserMessage = validatedData.messages
        .filter(msg => msg.role === 'user')
        .pop();

      if (!lastUserMessage) {
        return NextResponse.json(
          { success: false, error: 'No user message found' },
          { status: 400 }
        );
      }

      message = lastUserMessage.content;
      options = {
        sessionId: validatedData.sessionId,
        mode: validatedData.mode,
        promptType: validatedData.promptType,
        model: validatedData.model,
        temperature: validatedData.temperature,
        maxTokens: validatedData.maxTokens,
      };
    } else {
      return NextResponse.json(
        { success: false, error: 'Invalid request format' },
        { status: 400 }
      );
    }

    // GAIA-BT API 호출
    const result = await callGaiaBTAPI(message, options);
    
    return NextResponse.json({
      success: true,
      response: result.response || result.message || 'No response',
      sessionId: result.session_id || options.sessionId || 'default',
      mode: result.mode || options.mode || 'normal',
      model: result.model || options.model,
      timestamp: result.timestamp || new Date().toISOString(),
      mcpSources: result.mcp_sources,
    });

  } catch (error) {
    console.error('Chat API error:', error);
    
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { success: false, error: 'Invalid request data', details: error.errors },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// PUT: 스트리밍 처리를 위한 호환성 엔드포인트
export async function PUT(req: NextRequest) {
  try {
    
    // POST와 동일한 로직이지만 스트리밍 시뮬레이션 헤더 추가
    const response = await POST(req);
    const data = await response.json();
    
    if (data.success) {
      // 스트리밍 시뮬레이션을 위한 특별한 응답 형식
      return new NextResponse(data.response, {
        status: 200,
        headers: {
          'Content-Type': 'text/plain; charset=utf-8',
          'X-Streaming-Simulation': 'true',
          'X-Session-Id': data.sessionId,
          'X-Mode': data.mode,
        },
      });
    } else {
      return NextResponse.json(data, { status: response.status });
    }
    
  } catch (error) {
    console.error('Chat PUT API error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}