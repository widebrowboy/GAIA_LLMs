import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  try {
    // Ollama에서 사용 가능한 모델 목록 가져오기
    const getOllamaModels = async (): Promise<string[]> => {
      try {
        const ollamaUrl = process.env.OLLAMA_BASE_URL || 'http://localhost:11434';
        const response = await fetch(`${ollamaUrl}/api/tags`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Ollama API error: ${response.status}`);
        }

        const data = await response.json();
        return data.models?.map((model: any) => model.name) || [];
      } catch (error) {
        console.error('Failed to fetch Ollama models:', error);
        // Ollama 연결 실패 시 기본 모델 반환
        return ['gemma3:latest', 'llama3.2:latest', 'mistral:latest'];
      }
    };

    // GAIA-BT 백엔드 API에서 시스템 정보 가져오기 (선택사항)
    let backendData = null;
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/system/info`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        backendData = await response.json();
      }
    } catch (error) {
      console.log('Backend not available, using Ollama-only configuration');
    }

    // Ollama 모델 목록 가져오기
    const availableModels = await getOllamaModels();
    
    // 시스템 정보 조합
    const systemInfo = {
      version: backendData?.version || '2.1.0-alpha',
      model: backendData?.model || availableModels[0] || 'gemma3:latest',
      mode: backendData?.mode || 'normal',
      mcp_enabled: backendData?.mcp_enabled || false,
      debug: backendData?.debug || false,
      available_models: availableModels.length > 0 ? availableModels : [
        'gemma3:latest',
        'llama3.2:latest', 
        'mistral:latest'
      ],
      available_prompts: backendData?.available_prompts || [
        'default',
        'clinical',
        'research',
        'chemistry',
        'regulatory'
      ]
    };
    
    return NextResponse.json(systemInfo);
  } catch (error) {
    console.error('System info API error:', error);
    
    // 모든 연결 실패 시 기본값 반환
    return NextResponse.json({
      version: '2.1.0-alpha',
      model: 'Gemma3:27b-it-q4_K_M',
      mode: 'normal',
      mcp_enabled: false,
      debug: false,
      available_models: [
        'Gemma3:27b-it-q4_K_M',
        'txgemma-predict:latest',
        'txgemma-chat:latest',
        'Gemma3:latest'
      ],
      available_prompts: [
        'default',
        'clinical',
        'research',
        'chemistry',
        'regulatory'
      ]
    });
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // 백엔드로 설정 변경 요청 전달
    const response = await fetch(`${apiUrl}/api/system/config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('System config API error:', error);
    return NextResponse.json(
      { error: 'Failed to update system configuration' },
      { status: 500 }
    );
  }
}