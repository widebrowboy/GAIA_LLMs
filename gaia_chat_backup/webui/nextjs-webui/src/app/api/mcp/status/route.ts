import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  try {
    // GAIA-BT 백엔드 API에서 MCP 상태 가져오기
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/mcp/status`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('MCP status API error:', error);
    
    // 백엔드 연결 실패 시 기본값 반환
    return NextResponse.json({
      servers: [
        {
          name: 'ChEMBL',
          status: 'stopped',
          description: '화학 데이터베이스 검색',
          tools: ['search_compounds', 'get_targets']
        },
        {
          name: 'PubMed',
          status: 'stopped', 
          description: '의학 문헌 검색',
          tools: ['search_papers', 'get_abstracts']
        },
        {
          name: 'ClinicalTrials',
          status: 'stopped',
          description: '임상시험 데이터',
          tools: ['search_trials', 'get_trial_details']
        },
        {
          name: 'Sequential Thinking',
          status: 'stopped',
          description: '단계별 추론 AI',
          tools: ['think_step_by_step', 'analyze_problem']
        }
      ]
    });
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { action, serverName } = body;
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    let endpoint = '';
    switch (action) {
      case 'start':
        endpoint = '/api/mcp/start';
        break;
      case 'stop':
        endpoint = '/api/mcp/stop';
        break;
      case 'restart':
        endpoint = '/api/mcp/restart';
        break;
      default:
        throw new Error('Invalid action');
    }

    const response = await fetch(`${apiUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ server: serverName }),
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('MCP control API error:', error);
    return NextResponse.json(
      { error: 'Failed to control MCP server' },
      { status: 500 }
    );
  }
}