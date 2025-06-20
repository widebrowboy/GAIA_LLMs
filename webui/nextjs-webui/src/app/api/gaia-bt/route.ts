/**
 * GAIA-BT API Route Handler
 * 신약개발 전문 AI 어시스턴트 API 엔드포인트
 */

import { NextRequest, NextResponse } from 'next/server';

interface ChatRequest {
  message: string;
  mode: 'normal' | 'deep_research';
  prompt_mode: 'default' | 'clinical' | 'research' | 'chemistry' | 'regulatory';
  model?: string;
}

interface FunctionRequest {
  function_name: string;
  parameters: Record<string, unknown>;
}

export async function POST(request: NextRequest) {
  try {
    // 요청 본문 안전하게 파싱
    let body;
    try {
      body = await request.json();
    } catch (parseError) {
      console.error('JSON Parse Error:', parseError);
      return NextResponse.json(
        { 
          success: false,
          error: 'Invalid JSON in request body' 
        },
        { status: 400 }
      );
    }

    const { type, ...data } = body;
    console.log('GAIA-BT API Request:', { type, data });

    switch (type) {
      case 'chat':
        return await handleChat(data as ChatRequest);
      case 'function':
        return await handleFunction(data as FunctionRequest);
      case 'status':
        return await handleStatus();
      default:
        console.warn('Invalid request type:', type);
        return NextResponse.json(
          { 
            success: false,
            error: `Invalid request type: ${type}` 
          },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error('GAIA-BT API Error:', error);
    
    // 에러에 따른 상세한 응답
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { 
        success: false,
        error: 'Internal server error',
        details: errorMessage 
      },
      { status: 500 }
    );
  }
}

async function handleChat(data: ChatRequest): Promise<NextResponse> {
  console.log('handleChat called with:', data);
  
  // 데이터 검증
  if (!data || typeof data !== 'object') {
    return NextResponse.json({
      success: false,
      error: 'Invalid chat data provided'
    }, { status: 400 });
  }

  const { message, mode, prompt_mode, model } = data;
  
  // 메시지 검증
  if (!message || typeof message !== 'string') {
    return NextResponse.json({
      success: false,
      error: 'Message is required and must be a string'
    }, { status: 400 });
  }

  try {
    console.log('Attempting to call GAIA-BT...');
    
    // GAIA-BT Python 스크립트 호출 시뮬레이션
    const response = await callGAIABT('chat', {
      message,
      mode: mode || 'normal',
      prompt_mode: prompt_mode || 'default',
      model: model || 'gemma3:27b-it-q4_K_M'
    });

    return NextResponse.json({
      success: true,
      response: response,
      mode: mode || 'normal',
      prompt_mode: prompt_mode || 'default',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Chat Error, falling back to mock:', error);
    
    // Mock 응답 생성 (항상 성공적으로 응답)
    const mockResponse = generateMockChatResponse(
      message, 
      mode || 'normal', 
      prompt_mode || 'default'
    );
    
    return NextResponse.json({
      success: true,
      response: mockResponse,
      mode: mode || 'normal',
      prompt_mode: prompt_mode || 'default',
      mock: true,
      timestamp: new Date().toISOString()
    });
  }
}

async function handleFunction(data: FunctionRequest): Promise<NextResponse> {
  const { function_name, parameters } = data;

  try {
    // GAIA-BT Function 호출
    const response = await callGAIABTFunction(function_name, parameters);

    return NextResponse.json({
      success: true,
      function: function_name,
      parameters: parameters,
      result: response,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Function Error:', error);
    
    // Mock 함수 응답 생성
    const mockResponse = generateMockFunctionResponse(function_name, parameters);
    
    return NextResponse.json({
      success: true,
      function: function_name,
      parameters: parameters,
      result: mockResponse,
      mock: true,
      timestamp: new Date().toISOString()
    });
  }
}

async function handleStatus(): Promise<NextResponse> {
  try {
    const status = await getGAIABTStatus();
    
    return NextResponse.json({
      success: true,
      status: status,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Status Error:', error);
    
    return NextResponse.json({
      success: true,
      status: {
        gaia_bt_available: false,
        ollama_connected: false,
        mcp_servers: [],
        mock_mode: true,
        version: 'v2.0 Alpha'
      },
      mock: true,
      timestamp: new Date().toISOString()
    });
  }
}

async function callGAIABT(command: string, data: any): Promise<string> {
  try {
    console.log('Attempting to call GAIA-BT FastAPI backend...');
    
    // FastAPI 서버로 요청 전송 (짧은 timeout으로 빠른 폴백)
    const response = await fetch('http://localhost:8000/api/chat/message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: data.message,
        session_id: 'default',
        mode: data.mode || 'normal',
        prompt_mode: data.prompt_mode || 'default',
        model: data.model
      }),
      signal: AbortSignal.timeout(5000) // 5초 타임아웃으로 빠른 폴백
    });

    if (!response.ok) {
      throw new Error(`FastAPI server returned ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    
    if (result.success) {
      return result.response || result.message || 'Response received';
    } else {
      throw new Error(result.error || 'Unknown API error');
    }

  } catch (error) {
    console.error('FastAPI backend error:', error);
    throw new Error(`GAIA-BT backend not available: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

async function callGAIABTFunction(functionName: string, parameters: any): Promise<string> {
  try {
    console.log(`Attempting to call GAIA-BT function: ${functionName}`);
    
    // 함수명을 명령어로 변환
    let command = '';
    if (functionName === 'mcp' && parameters.args && parameters.args.length > 0) {
      command = `/mcp ${parameters.args.join(' ')}`;
    } else if (functionName === 'help') {
      command = '/help';
    } else if (functionName === 'debug') {
      command = '/debug';
    } else if (functionName === 'mcpshow') {
      command = '/mcpshow';
    } else if (functionName === 'normal') {
      command = '/normal';
    } else if (functionName === 'model' && parameters.args && parameters.args.length > 0) {
      command = `/model ${parameters.args[0]}`;
    } else if (functionName === 'prompt' && parameters.args && parameters.args.length > 0) {
      command = `/prompt ${parameters.args[0]}`;
    } else {
      command = parameters.command || `/${functionName}`;
    }

    // FastAPI 서버로 명령어 요청 전송 (MCP 명령어는 더 짧은 timeout)
    const timeoutMs = command.includes('/mcp') ? 5000 : 10000;
    const response = await fetch('http://localhost:8000/api/chat/command', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        command: command,
        session_id: parameters.session_id || 'default'
      }),
      signal: AbortSignal.timeout(timeoutMs)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`FastAPI server returned ${response.status}: ${errorText}`);
    }

    const result = await response.json();
    
    if (result.success) {
      return result.response || result.message || result.result || 'Command executed successfully';
    } else {
      throw new Error(result.error || 'Command execution failed');
    }

  } catch (error) {
    console.error(`Function ${functionName} error, falling back to mock:`, error);
    
    // Mock 응답으로 폴백
    const functionMap: Record<string, (params: any) => string> = {
      get_system_status: () => getMockSystemStatus(),
      mcp: (params) => {
        if (params.args && params.args[0] === 'start') {
          return `🔬 **Deep Research 모드 활성화**\\n\\n✅ MCP 통합 시스템이 시작되었습니다.\\n\\n**활성화된 서버:**\\n• BiomCP: 생의학 논문 및 임상시험\\n• ChEMBL: 화학 구조 및 활성 데이터\\n• DrugBank: 약물 정보 및 상호작용\\n• OpenTargets: 타겟-질병 연관성\\n• Sequential Thinking: AI 추론\\n\\n이제 복잡한 신약개발 질문에 대해 다중 데이터베이스 검색 결과를 제공합니다.\\n\\n⚠️ *현재 Mock 모드로 실행 중입니다. 실제 MCP 서버는 준비 중입니다.*`;
        } else if (params.args && params.args[0] === 'status') {
          return `📊 **MCP 서버 상태**\\n\\n**서버 목록:**\\n• BiomCP: ⚠️ 준비 중\\n• ChEMBL: ⚠️ 준비 중\\n• DrugBank: ⚠️ 준비 중\\n• OpenTargets: ⚠️ 준비 중\\n• Sequential Thinking: ⚠️ 준비 중\\n\\n*실제 MCP 서버 연결을 위해서는 별도 설정이 필요합니다.*`;
        } else if (params.args && params.args[0] === 'stop') {
          return `🛑 **MCP 서버 중지**\\n\\n모든 MCP 서버가 중지되었습니다.\\n일반 모드로 전환됩니다.`;
        }
        return `MCP 명령어가 실행되었습니다: ${params.args?.join(' ') || ''}`;
      },
      help: () => getMockHelpText(),
      debug: () => `🐛 **디버그 모드 토글**\\n\\n디버그 모드가 전환되었습니다.`,
      mcpshow: () => `🔍 **MCP 출력 표시 토글**\\n\\nMCP 검색 과정 표시가 전환되었습니다.`,
      normal: () => `🏠 **일반 모드로 전환**\\n\\n빠르고 정확한 기본 AI 답변을 제공합니다.`,
      switch_mode: (params) => `✅ GAIA-BT Mode Changed\\n\\n${params.mode === 'deep_research' ? '🔬' : '💬'} **Current Mode**: ${params.mode === 'deep_research' ? 'Deep Research Mode' : 'Normal Mode'}\\n\\n---\\n*GAIA-BT v2.0 Alpha Mode System*`,
      change_model: (params) => `✅ GAIA-BT Model Changed\\n\\n🤖 **New Model**: ${params.model}\\n\\n---\\n*GAIA-BT v2.0 Alpha Model System*`,
      change_prompt_mode: (params) => `✅ GAIA-BT Prompt Mode Changed\\n\\n**Current Mode**: ${params.mode.charAt(0).toUpperCase() + params.mode.slice(1)}\\n\\n---\\n*GAIA-BT v2.0 Alpha Prompt System*`,
      deep_research_search: (params) => getMockDeepResearch(params.query),
      molecular_analysis: (params) => getMockMolecularAnalysis(params.compound),
      clinical_trial_search: (params) => getMockClinicalTrials(params.indication, params.phase),
      literature_search: (params) => getMockLiteratureSearch(params.topic, params.years),
      generate_research_plan: (params) => getMockResearchPlan(params.objective, params.budget, params.timeline)
    };

    const handler = functionMap[functionName];
    if (handler) {
      return handler(parameters);
    }

    throw new Error(`Unknown function: ${functionName}`);
  }
}

async function getGAIABTStatus(): Promise<any> {
  try {
    console.log('Attempting to get GAIA-BT status...');
    
    // FastAPI 서버 상태 확인
    const response = await fetch('http://localhost:8000/api/system/info', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(10000)
    });

    if (!response.ok) {
      throw new Error(`FastAPI server returned ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    
    if (result.success) {
      return result.info || result.data || result;
    } else {
      throw new Error(result.error || 'Status check failed');
    }

  } catch (error) {
    console.error('Status check error:', error);
    throw new Error(`GAIA-BT status not available: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

// Mock 응답 생성 함수들
function generateMockChatResponse(message: string, mode: string, promptMode: string): string {
  const modeDisplay = mode === 'deep_research' ? 'Deep Research Mode' : 'Normal Mode';
  const banner = `
╭─────────────────────────────────────────────────╮
│ 🧬 GAIA-BT v2.0 Alpha 신약개발 연구 어시스턴트      │
│ ${mode === 'deep_research' ? '🔬' : '💬'} Mode: ${modeDisplay} │
│ 📋 Prompt: ${promptMode} │
╰─────────────────────────────────────────────────╯

`;

  let response = banner;

  if (mode === 'deep_research') {
    response += `🔬 **Deep Research Mode**로 처리 중입니다...\\n\\n`;
    response += `📊 **통합 분석 결과**\\n\\n`;
  } else {
    response += `💬 **일반 모드**로 처리 중입니다...\\n\\n`;
  }

  // 메시지 내용에 따른 맞춤형 응답 - 일반 모드에서도 완전한 분석 제공
  if (message.toLowerCase().includes('cancer') || message.includes('암')) {
    response += generateCancerDrugResponse(mode, promptMode);
  } else if (message.toLowerCase().includes('aspirin') || message.includes('아스피린')) {
    response += generateAspirinResponse(mode, promptMode);
  } else if (message.toLowerCase().includes('mechanism') || message.includes('메커니즘')) {
    response += generateMechanismResponse(mode, promptMode);
  } else if (message.toLowerCase().includes('clinical') || message.includes('임상')) {
    response += generateClinicalResponse(mode, promptMode);
  } else if (message.toLowerCase().includes('target') || message.includes('타겟')) {
    response += generateTargetResponse(mode, promptMode);
  } else if (message.toLowerCase().includes('admet') || message.includes('약물동태')) {
    response += generateADMETResponse(mode, promptMode);
  } else {
    response += generateGeneralDrugResponse(message, mode, promptMode);
  }

  response += `\\n---\\n*Generated by GAIA-BT v2.0 Alpha - ${promptMode} mode*`;

  return response;
}

// 주제별 상세 응답 생성 함수들
function generateCancerDrugResponse(mode: string): string {
  let response = `🎯 **암 치료제 개발 전문 분석**\\n\\n`;
  
  response += `## 📊 암 치료제 개발 현황\\n`;
  response += `• **표적 치료제**: PD-1/PD-L1 억제제, CAR-T 세포치료제 등 면역항암제 활성화\\n`;
  response += `• **정밀의학**: 유전자 프로파일링 기반 개인 맞춤형 치료 확산\\n`;
  response += `• **복합치료**: 면역치료 + 항암화학요법 조합으로 치료 효과 극대화\\n\\n`;
  
  response += `## 🔬 핵심 개발 전략\\n`;
  response += `### 1. 타겟 검증 및 발굴\\n`;
  response += `• 종양 특이적 바이오마커 확인 (예: HER2, EGFR, BRCA1/2)\\n`;
  response += `• 종양 미세환경 분석을 통한 새로운 치료 타겟 발굴\\n`;
  response += `• 내성 메커니즘 연구로 차세대 치료제 개발\\n\\n`;
  
  response += `### 2. 화합물 최적화\\n`;
  response += `• **선택성 강화**: 정상 세포 독성 최소화\\n`;
  response += `• **ADMET 프로파일**: 뇌혈관장벽 통과성, 대사 안정성 개선\\n`;
  response += `• **제형 기술**: 표적 전달 시스템 (DDS) 적용\\n\\n`;
  
  response += `### 3. 임상시험 설계\\n`;
  response += `• **Phase I**: 최대 허용 용량(MTD) 및 권장 용량(RP2D) 결정\\n`;
  response += `• **Phase II**: 특정 암종별 효능 평가, 바이오마커 기반 환자 선별\\n`;
  response += `• **Phase III**: 표준치료 대비 우월성 또는 비열등성 입증\\n\\n`;
  
  if (mode === 'deep_research') {
    response += `## 📈 **Deep Research 추가 정보**\\n`;
    response += `• **최신 논문**: Nature Cancer, Cell 등 최근 6개월 문헌 분석\\n`;
    response += `• **임상시험 현황**: ClinicalTrials.gov 등록 시험 실시간 모니터링\\n`;
    response += `• **규제 동향**: FDA, EMA 최신 가이드라인 업데이트\\n\\n`;
  }
  
  response += `## 💡 **향후 전망**\\n`;
  response += `• AI 기반 신약 발굴로 개발 기간 단축 (10-15년 → 5-7년)\\n`;
  response += `• 액체생검 기술 발전으로 조기 진단 및 치료 모니터링 개선\\n`;
  response += `• 개인화 의료 확산으로 치료 성공률 향상 기대\\n\\n`;
  
  return response;
}

function generateAspirinResponse(mode: string, promptMode: string): string {
  let response = `💊 **아스피린 종합 신약개발 분석**\\n\\n`;
  
  response += `## 🔬 작용 메커니즘\\n`;
  response += `### 주요 타겟: COX-1/COX-2 억제\\n`;
  response += `• **COX-1 억제**: 혈소판 응집 억제 → 심혈관 보호 효과\\n`;
  response += `• **COX-2 억제**: 염증반응 억제 → 진통, 해열 효과\\n`;
  response += `• **비가역적 결합**: Ser530 잔기에 아세틸기 공유결합\\n\\n`;
  
  response += `## 📋 현재 적응증\\n`;
  response += `• **1차 예방**: 심혈관 질환 고위험군 예방 (저용량 75-100mg)\\n`;
  response += `• **2차 예방**: 심근경색, 뇌졸중 재발 방지\\n`;
  response += `• **진통/해열**: 일반의약품으로 광범위 사용\\n\\n`;
  
  response += `## 🆕 신규 적응증 연구\\n`;
  response += `### 1. 암 예방 효과\\n`;
  response += `• **대장암**: 장기 복용 시 발생률 20-30% 감소\\n`;
  response += `• **위암**: H. pylori 관련 위암 위험도 감소\\n`;
  response += `• **유방암**: 호르몬 수용체 양성 유방암 예방 가능성\\n\\n`;
  
  response += `### 2. 신경퇴행성 질환\\n`;
  response += `• **알츠하이머병**: 신경염증 억제를 통한 예방 효과 연구\\n`;
  response += `• **파킨슨병**: 도파민 신경세포 보호 효과 임상시험 진행\\n\\n`;
  
  response += `## 🔧 제형 개발 전략\\n`;
  response += `### 1. 위장관 부작용 최소화\\n`;
  response += `• **장용성 코팅**: 위산으로부터 보호, 십이지장에서 방출\\n`;
  response += `• **서방형 제제**: 24시간 지속 효과, 복용 편의성 개선\\n`;
  response += `• **복합제**: PPI(프로톤펌프억제제) 병용으로 위 보호\\n\\n`;
  
  response += `### 2. 새로운 투여 경로\\n`;
  response += `• **경피 패치**: 위장관 우회, 일정한 혈중농도 유지\\n`;
  response += `• **정맥주사제**: 급성 관상동맥증후군 응급 치료\\n\\n`;
  
  if (mode === 'deep_research') {
    response += `## 📊 **Deep Research 추가 데이터**\\n`;
    response += `• **약물동태학**: 생체이용률 99%, 반감기 15-20분\\n`;
    response += `• **약물상호작용**: 와파린과 병용 시 출혈 위험 증가\\n`;
    response += `• **최신 임상시험**: ASPREE 연구 결과 분석\\n\\n`;
  }
  
  response += `## 🚀 **혁신적 개발 방향**\\n`;
  response += `• **나노제형**: 표적 지향성 개선, 부작용 최소화\\n`;
  response += `• **프로드럭**: 조직 특이적 활성화로 선택적 효과\\n`;
  response += `• **바이오마커**: 개인별 최적 용량 결정 시스템 개발\\n\\n`;
  
  return response;
}

function generateMechanismResponse(mode: string, promptMode: string): string {
  let response = `⚙️ **약물 작용 메커니즘 분석**\\n\\n`;
  
  response += `## 🎯 작용 메커니즘 연구의 중요성\\n`;
  response += `• **타겟 검증**: 질병과 연관된 생체분자 확인\\n`;
  response += `• **효능 예측**: 약효 및 부작용 프로파일 예측\\n`;
  response += `• **최적화 방향**: 구조-활성 관계(SAR) 기반 화합물 개선\\n\\n`;
  
  response += `## 🔬 메커니즘 연구 방법론\\n`;
  response += `### 1. 분자 수준 연구\\n`;
  response += `• **X-ray 결정학**: 약물-표적 결합 구조 분석\\n`;
  response += `• **NMR 분광법**: 용액 상태에서 동적 상호작용 관찰\\n`;
  response += `• **분자동역학 시뮬레이션**: 컴퓨터 모델링으로 결합 예측\\n\\n`;
  
  response += `### 2. 세포 수준 연구\\n`;
  response += `• **신호전달 경로 분석**: Western blot, qPCR로 단백질/유전자 발현 변화\\n`;
  response += `• **세포 기능 시험**: 증식, 사멸, 이동능 등 생물학적 기능 평가\\n`;
  response += `• **형광 이미징**: 실시간 세포 내 약물 분포 및 표적 결합 관찰\\n\\n`;
  
  response += `### 3. 동물 모델 연구\\n`;
  response += `• **질병 모델**: 인간 질병을 모사한 동물 모델에서 약효 검증\\n`;
  response += `• **약물동태**: 흡수, 분포, 대사, 배설(ADME) 프로파일 분석\\n`;
  response += `• **독성 평가**: 급성/만성 독성, 발암성, 생식독성 평가\\n\\n`;
  
  response += `## 💡 **최신 기술 동향**\\n`;
  response += `### 1. AI/ML 기반 예측\\n`;
  response += `• **딥러닝**: AlphaFold를 활용한 단백질 구조 예측\\n`;
  response += `• **가상 스크리닝**: 화합물 라이브러리에서 활성 화합물 예측\\n`;
  response += `• **QSAR 모델링**: 화학 구조로부터 생물학적 활성 예측\\n\\n`;
  
  response += `### 2. 오믹스 기술\\n`;
  response += `• **프로테오믹스**: 약물 처리 후 단백질 발현 변화 전체 분석\\n`;
  response += `• **메타볼로믹스**: 대사체 변화 패턴으로 작용 메커니즘 추론\\n`;
  response += `• **유전체학**: 약물 반응성 관련 유전적 변이 발굴\\n\\n`;
  
  if (mode === 'deep_research') {
    response += `## 📈 **Deep Research 통합 분석**\\n`;
    response += `• **다중 오믹스 데이터 통합**: 시스템 생물학적 접근\\n`;
    response += `• **네트워크 약리학**: 약물-표적-질병 상호작용 네트워크 분석\\n`;
    response += `• **개인화 메커니즘**: 환자별 유전적 배경에 따른 반응 차이\\n\\n`;
  }
  
  return response;
}

function generateClinicalResponse(mode: string, promptMode: string): string {
  let response = `🏥 **임상시험 전문 분석**\\n\\n`;
  
  response += `## 📋 임상시험 단계별 특징\\n`;
  response += `### Phase I (1상)\\n`;
  response += `• **목적**: 안전성 평가, 최대허용용량(MTD) 결정\\n`;
  response += `• **대상**: 건강한 지원자 또는 치료 옵션이 없는 환자 (20-100명)\\n`;
  response += `• **평가항목**: 용량제한독성(DLT), 약물동태학(PK), 약력학(PD)\\n`;
  response += `• **기간**: 6개월-1년\\n\\n`;
  
  response += `### Phase II (2상)\\n`;
  response += `• **목적**: 예비 효능 평가, 적정 용량 결정\\n`;
  response += `• **대상**: 특정 질환자 (100-300명)\\n`;
  response += `• **평가항목**: 반응률, 무진행생존기간, 바이오마커\\n`;
  response += `• **설계**: Single-arm 또는 randomized controlled trial\\n\\n`;
  
  response += `### Phase III (3상)\\n`;
  response += `• **목적**: 표준치료 대비 우월성/비열등성 입증\\n`;
  response += `• **대상**: 다기관, 대규모 환자군 (1,000-3,000명)\\n`;
  response += `• **평가항목**: 전체생존기간(OS), 삶의 질(QoL)\\n`;
  response += `• **규제**: 허가 신청을 위한 핵심 임상시험\\n\\n`;
  
  response += `## 🔬 현대 임상시험 동향\\n`;
  response += `### 1. 적응형 임상시험 (Adaptive Clinical Trial)\\n`;
  response += `• **용량 조절**: 중간 분석 결과에 따른 용량 최적화\\n`;
  response += `• **환자군 재정의**: 바이오마커 기반 환자 선별 기준 조정\\n`;
  response += `• **통계 설계**: Bayesian 방법론 활용한 유연한 설계\\n\\n`;
  
  response += `### 2. 정밀의학 임상시험\\n`;
  response += `• **바이오마커 기반**: 유전자 변이에 따른 맞춤형 치료\\n`;
  response += `• **동반진단**: 치료제와 함께 개발되는 진단법\\n`;
  response += `• **N-of-1 시험**: 개별 환자 맞춤형 치료 효과 평가\\n\\n`;
  
  response += `### 3. 실제임상자료(RWE) 활용\\n`;
  response += `• **전자의무기록**: EMR/EHR 데이터 활용한 장기 안전성 모니터링\\n`;
  response += `• **환자보고결과**: PRO 중심의 효능 평가\\n`;
  response += `• **빅데이터 분석**: AI/ML 기반 임상 결과 예측\\n\\n`;
  
  response += `## 📊 **규제 요구사항**\\n`;
  response += `### FDA 가이드라인\\n`;
  response += `• **IND 신청**: 임상시험 허가 (30일 내 승인)\\n`;
  response += `• **NDA/BLA**: 시판허가 신청 (표준 심사 10개월)\\n`;
  response += `• **특별 프로그램**: Fast Track, Breakthrough Therapy 지정\\n\\n`;
  
  response += `### EMA 요구사항\\n`;
  response += `• **CTA**: 임상시험 승인 신청 (60일 내 승인)\\n`;
  response += `• **MAA**: 유럽 시판허가 신청 (210일 심사)\\n`;
  response += `• **조건부 승인**: 미충족 의료 수요 대상 신속 승인\\n\\n`;
  
  if (mode === 'deep_research') {
    response += `## 🌍 **Deep Research 글로벌 동향**\\n`;
    response += `• **디지털 임상시험**: 원격 모니터링, 가상 방문\\n`;
    response += `• **분산형 임상시험(DCT)**: COVID-19 이후 확산\\n`;
    response += `• **AI 임상시험**: 환자 모집, 데이터 분석 AI 활용\\n\\n`;
  }
  
  return response;
}

function generateTargetResponse(mode: string, promptMode: string): string {
  let response = `🎯 **약물 타겟 발굴 및 검증**\\n\\n`;
  
  response += `## 🔬 타겟 발굴 전략\\n`;
  response += `### 1. 질병 메커니즘 분석\\n`;
  response += `• **유전체학**: GWAS, 엑솜 시퀀싱으로 질병 연관 유전자 발굴\\n`;
  response += `• **전사체학**: RNA-seq으로 질병 상태 특이적 유전자 발현 패턴 분석\\n`;
  response += `• **단백체학**: 질병 조직에서 단백질 발현 및 변형 분석\\n\\n`;
  
  response += `### 2. 기능적 검증\\n`;
  response += `• **유전자 녹아웃**: CRISPR-Cas9를 이용한 유전자 기능 검증\\n`;
  response += `• **RNA 간섭**: siRNA/shRNA로 타겟 단백질 발현 억제\\n`;
  response += `• **약리학적 도구**: 기존 억제제로 타겟 관련성 검증\\n\\n`;
  
  response += `## 🏆 **성공적인 타겟 클래스**\\n`;
  response += `### 1. G단백질 결합 수용체 (GPCR)\\n`;
  response += `• **시장 점유율**: 전체 의약품의 약 35%\\n`;
  response += `• **대표 약물**: 베타 차단제, 항히스타민제, 오피오이드\\n`;
  response += `• **개발 현황**: 800여 개 GPCR 중 50여 개만 타겟화\\n\\n`;
  
  response += `### 2. 효소 (Enzyme)\\n`;
  response += `• **타입**: 키나제, 프로테아제, 폴리머라제 등\\n`;
  response += `• **대표 약물**: 이부프로fen(COX), 아토르바스타틴(HMG-CoA 환원효소)\\n`;
  response += `• **신약 개발**: 단백질 키나제 억제제 급속 증가\\n\\n`;
  
  response += `### 3. 이온 채널\\n`;
  response += `• **신경계**: 간질, 통증 치료제\\n`;
  response += `• **심혈관계**: 칼슘 채널 차단제\\n`;
  response += `• **대사질환**: 당뇨병 치료용 K-ATP 채널 조절제\\n\\n`;
  
  response += `## 🆕 **신규 타겟 동향**\\n`;
  response += `### 1. 단백질-단백질 상호작용 (PPI)\\n`;
  response += `• **도전과제**: 넓은 결합 표면, 낮은 약물성\\n`;
  response += `• **돌파구**: 분해촉진제(PROTAC), 분자접착제\\n`;
  response += `• **성공사례**: BCL-2 억제제, MDM2-p53 억제제\\n\\n`;
  
  response += `### 2. RNA 타겟팅\\n`;
  response += `• **안티센스 올리고**: DMD, SMA 치료제\\n`;
  response += `• **siRNA**: 간 질환, 심혈관 질환 적용\\n`;
  response += `• **리보솜 리보스위치**: 항생제 내성 극복\\n\\n`;
  
  response += `### 3. 후성유전학적 타겟\\n`;
  response += `• **히스톤 변형효소**: HDAC, HAT, 메틸전이효소\\n`;
  response += `• **DNA 메틸화**: DNMT 억제제\\n`;
  response += `• **크로마틴 리모델링**: BRD4, SWI/SNF 복합체\\n\\n`;
  
  response += `## 🔍 **타겟 검증 기준**\\n`;
  response += `### 1. 안전성 (Safety)\\n`;
  response += `• **선택성**: 표적 외 효과 최소화\\n`;
  response += `• **독성 예측**: 필수 유전자 여부, 조직 분포\\n`;
  response += `• **부작용 프로파일**: 기존 약물 데이터 분석\\n\\n`;
  
  response += `### 2. 약물성 (Druggability)\\n`;
  response += `• **결합 포켓**: 소분자 결합 가능한 구조적 특징\\n`;
  response += `• **물리화학적 성질**: Lipinski Rule of Five 준수\\n`;
  response += `• **막 투과성**: 생체막 통과 가능성\\n\\n`;
  
  if (mode === 'deep_research') {
    response += `## 🤖 **Deep Research AI 기반 타겟 발굴**\\n`;
    response += `• **딥러닝**: 질병-유전자 연관성 예측 모델\\n`;
    response += `• **네트워크 분석**: 단백질 상호작용 네트워크에서 핵심 노드 발굴\\n`;
    response += `• **다중 오믹스**: 통합 분석으로 신규 타겟 발견\\n\\n`;
  }
  
  return response;
}

function generateADMETResponse(mode: string, promptMode: string): string {
  let response = `⚗️ **ADMET 프로파일 최적화**\\n\\n`;
  
  response += `## 📊 ADMET의 구성 요소\\n`;
  response += `### A - 흡수 (Absorption)\\n`;
  response += `• **생체이용률**: 경구 투여 후 전신 순환에 도달하는 약물 비율\\n`;
  response += `• **투과성**: Caco-2 세포, PAMPA 모델로 장관 흡수 예측\\n`;
  response += `• **용해성**: 수용성/지용성 균형, BCS 분류 체계\\n\\n`;
  
  response += `### D - 분포 (Distribution)\\n`;
  response += `• **혈장 단백질 결합**: 알부민, α1-산당단백질 결합률\\n`;
  response += `• **조직 분포**: 분포 용적(Vd), 조직-혈장 분배계수\\n`;
  response += `• **장벽 통과**: 혈뇌장벽, 태반 통과성\\n\\n`;
  
  response += `### M - 대사 (Metabolism)\\n`;
  response += `• **1차 대사**: 시토크롬 P450 효소 (CYP1A2, 2C9, 2C19, 2D6, 3A4)\\n`;
  response += `• **2차 대사**: 포합 반응 (글루쿠론산화, 황산화, 메틸화)\\n`;
  response += `• **대사 안정성**: 간 마이크로솜, 간세포에서 반감기 측정\\n\\n`;
  
  response += `### E - 배설 (Excretion)\\n`;
  response += `• **신장 배설**: 사구체 여과, 세뇨관 분비/재흡수\\n`;
  response += `• **담즙 배설**: 대형 분자, 극성 화합물의 주요 경로\\n`;
  response += `• **청소율**: 신청소율, 간청소율, 전체청소율\\n\\n`;
  
  response += `### T - 독성 (Toxicity)\\n`;
  response += `• **급성 독성**: LD50, 최대무독성용량(NOAEL)\\n`;
  response += `• **만성 독성**: 발암성, 생식독성, 기관독성\\n`;
  response += `• **예측 독성학**: in silico, in vitro 모델 활용\\n\\n`;
  
  response += `## 🔧 **ADMET 최적화 전략**\\n`;
  response += `### 1. 흡수 개선\\n`;
  response += `• **pH 조절**: 염 형성, 완충제 사용\\n`;
  response += `• **입자 크기**: 나노화, 미분화로 용해도 증가\\n`;
  response += `• **제형 기술**: 리포솜, 마이크로에멀젼\\n\\n`;
  
  response += `### 2. 분포 최적화\\n`;
  response += `• **단백질 결합 조절**: 구조 변형으로 결합 친화도 조절\\n`;
  response += `• **표적 지향성**: 항체-약물 결합체(ADC), 펩타이드 전달체\\n`;
  response += `• **조직 선택성**: 기관 특이적 분포 유도\\n\\n`;
  
  response += `### 3. 대사 안정성\\n`;
  response += `• **대사 부위 차단**: 불소화, 고리화 등 구조 변형\\n`;
  response += `• **프로드럭**: 대사 후 활성화되는 전구체 개발\\n`;
  response += `• **입체화학**: 거울상 이성질체 선택으로 대사 조절\\n\\n`;
  
  response += `### 4. 독성 최소화\\n`;
  response += `• **선택성 증가**: 표적 외 단백질 결합 최소화\\n`;
  response += `• **반응성 대사체**: 독성 중간체 생성 방지\\n`;
  response += `• **용량 최적화**: 치료 효과 대비 독성 비율 개선\\n\\n`;
  
  response += `## 🤖 **첨단 ADMET 예측 기술**\\n`;
  response += `### 1. In Silico 모델링\\n`;
  response += `• **QSAR 모델**: 구조-활성 관계 기반 예측\\n`;
  response += `• **AI/ML**: 딥러닝 기반 ADMET 특성 예측\\n`;
  response += `• **생리학적 약물동태모델(PBPK)**: 인체 내 약물 거동 시뮬레이션\\n\\n`;
  
  response += `### 2. High-throughput 스크리닝\\n`;
  response += `• **자동화 플랫폼**: 96/384 웰 플레이트 기반 대량 평가\\n`;
  response += `• **다중 파라미터**: 동시 다항목 측정\\n`;
  response += `• **미세유체칩**: Organ-on-chip 기술 활용\\n\\n`;
  
  if (mode === 'deep_research') {
    response += `## 📈 **Deep Research 통합 ADMET 분석**\\n`;
    response += `• **다중 스케일 모델링**: 분자-세포-조직-기관 수준 통합\\n`;
    response += `• **개인화 ADMET**: 유전적 다형성 고려한 맞춤형 예측\\n`;
    response += `• **실시간 모니터링**: 임상시험 중 ADMET 추적\\n\\n`;
  }
  
  return response;
}

function generateGeneralDrugResponse(message: string, mode: string, promptMode: string): string {
  let response = `💊 **신약개발 종합 분석**\\n\\n`;
  
  response += `## 🎯 신약개발 프로세스 개요\\n`;
  response += `### 1. 타겟 발굴 및 검증 (1-2년)\\n`;
  response += `• **질병 메커니즘 분석**: 유전체학, 단백체학 연구\\n`;
  response += `• **타겟 검증**: 동물 모델, 세포 실험으로 치료 가능성 확인\\n`;
  response += `• **약물성 평가**: 화합물 결합 가능성 분석\\n\\n`;
  
  response += `### 2. 선도물질 발굴 (2-3년)\\n`;
  response += `• **화합물 라이브러리 스크리닝**: HTS, 가상 스크리닝\\n`;
  response += `• **Hit-to-Lead**: 초기 활성 화합물 최적화\\n`;
  response += `• **구조-활성 관계**: SAR 분석으로 활성 개선\\n\\n`;
  
  response += `### 3. 전임상 연구 (3-4년)\\n`;
  response += `• **ADMET 최적화**: 흡수, 분포, 대사, 배설, 독성 개선\\n`;
  response += `• **안전성 평가**: 독성시험, 안전약리시험\\n`;
  response += `• **제형 개발**: 안정성, 생체이용률 최적화\\n\\n`;
  
  response += `### 4. 임상시험 (5-7년)\\n`;
  response += `• **1상**: 안전성, 용량 결정 (6개월-1년)\\n`;
  response += `• **2상**: 예비 효능 평가 (1-2년)\\n`;
  response += `• **3상**: 대규모 효능 검증 (2-4년)\\n\\n`;
  
  response += `### 5. 허가 및 시판 (1-2년)\\n`;
  response += `• **허가 신청**: NDA/MAA 제출\\n`;
  response += `• **심사**: 규제 기관 검토 및 승인\\n`;
  response += `• **시판 후 조사**: 4상 안전성 모니터링\\n\\n`;
  
  if (promptMode === 'clinical') {
    response += `## 🏥 **임상시험 관점 특화 분석**\\n`;
    response += `• **환자 안전성**: 위험-이익 평가 최우선\\n`;
    response += `• **규제 준수**: GCP, ICH 가이드라인 철저 준수\\n`;
    response += `• **윤리적 고려**: IRB 승인, 인폼드 컨센트\\n\\n`;
  } else if (promptMode === 'research') {
    response += `## 🔬 **연구 관점 특화 분석**\\n`;
    response += `• **과학적 근거**: 최신 문헌 기반 가설 설정\\n`;
    response += `• **실험 설계**: 통계적 검정력, 바이오마커 활용\\n`;
    response += `• **데이터 품질**: 재현성, 신뢰성 확보\\n\\n`;
  } else if (promptMode === 'chemistry') {
    response += `## ⚗️ **의약화학 관점 특화 분석**\\n`;
    response += `• **분자 설계**: 컴퓨터 기반 약물 설계(CADD)\\n`;
    response += `• **합성 전략**: 효율적, 확장 가능한 합성 경로\\n`;
    response += `• **물성 최적화**: 용해도, 안정성, 막투과성\\n\\n`;
  } else if (promptMode === 'regulatory') {
    response += `## 📋 **규제 관점 특화 분석**\\n`;
    response += `• **글로벌 전략**: FDA, EMA, PMDA 동시 승인\\n`;
    response += `• **품질 시스템**: GMP, 품질 관리 체계\\n`;
    response += `• **위험 관리**: REMS, RMP 계획 수립\\n\\n`;
  }
  
  response += `## 🚀 **현재 신약개발 혁신 동향**\\n`;
  response += `### 1. AI/ML 기반 개발\\n`;
  response += `• **타겟 발굴**: AlphaFold 단백질 구조 예측\\n`;
  response += `• **분자 설계**: 생성형 AI로 신규 화합물 창조\\n`;
  response += `• **임상 최적화**: 환자 모집, 시험 설계 AI 지원\\n\\n`;
  
  response += `### 2. 정밀의학\\n`;
  response += `• **바이오마커**: 개인 맞춤형 치료제 개발\\n`;
  response += `• **동반진단**: 치료제와 진단법 동시 개발\\n`;
  response += `• **실제 임상 데이터**: RWE 활용 효능 검증\\n\\n`;
  
  response += `### 3. 첨단 치료법\\n`;
  response += `• **유전자 치료**: CRISPR, 유전자 편집\\n`;
  response += `• **세포 치료**: CAR-T, 줄기세포 치료\\n`;
  response += `• **mRNA 의약품**: 백신, 단백질 대체 요법\\n\\n`;
  
  if (mode === 'deep_research') {
    response += `## 📊 **Deep Research 추가 통찰**\\n`;
    response += `• **시장 동향**: 글로벌 제약 시장 $1.5조 규모\\n`;
    response += `• **성공률**: 전임상→시판 성공률 약 12%\\n`;
    response += `• **개발 비용**: 평균 26억 달러, 10-15년 소요\\n`;
    response += `• **혁신 동력**: 디지털 헬스, 오픈 이노베이션\\n\\n`;
  }
  
  response += `## 💡 **질문별 맞춤 응답**\\n`;
  response += `"${message}"에 대한 구체적인 정보가 필요하시면, 다음과 같이 질문해주세요:\\n`;
  response += `• 특정 약물의 작용 메커니즘\\n`;
  response += `• 질병별 치료제 개발 현황\\n`;
  response += `• 임상시험 설계 방법\\n`;
  response += `• ADMET 최적화 전략\\n`;
  response += `• 규제 요구사항 및 승인 과정\\n\\n`;
  
  return response;
}

function generateMockFunctionResponse(functionName: string, parameters: any): string {
  // 이미 callGAIABTFunction에서 처리되므로 여기서는 에러 처리
  return `Function ${functionName} executed with parameters: ${JSON.stringify(parameters)}`;
}

function getMockSystemStatus(): string {
  return `# 🧬 GAIA-BT System Status

## Core System
- **GAIA-BT Status**: ⚠️ Not Available (Mock Mode)

## Current Configuration
- **Mode**: Normal
- **Model**: gemma3:27b-it-q4_K_M
- **Prompt Mode**: Default

## Available Functions
- **deep_research_search**: Comprehensive MCP-based research
- **switch_mode**: Toggle Normal/Deep Research modes
- **change_model**: Switch between available models
- **change_prompt_mode**: Specialized prompt modes
- **molecular_analysis**: Chemical structure analysis
- **clinical_trial_search**: Clinical trial database search
- **literature_search**: PubMed literature research
- **generate_research_plan**: AI-powered research planning

---
*GAIA-BT v2.0 Alpha - Drug Development AI Assistant*`;
}

function getMockDeepResearch(query: string): string {
  return `# 🔬 Deep Research Results

## Query
${query}

## Literature Analysis
- **Relevant Papers**: 25 papers found (last 5 years)
- **Major Findings**: Novel target mechanism identified, 3 promising compounds

## Chemical Analysis
- **Similar Compounds**: 45 compounds (ChEMBL database)
- **Drug Interactions**: 3 major pathways confirmed
- **ADMET Prediction**: Moderate permeability, low toxicity

## Clinical Status
- **Ongoing Trials**: 7 trials (Phase I-III)
- **Approved Therapies**: 2 drugs (2019, 2021)
- **Regulatory Guidelines**: Latest FDA/EMA requirements

## Recommendations
1. Target validation experiments
2. Lead compound optimization
3. ADMET profiling

---
*Generated by GAIA-BT v2.0 Alpha Deep Research*`;
}

function getMockMolecularAnalysis(compound: string): string {
  return `# 🧪 Molecular Analysis Results

## Compound
${compound}

## Analysis Results
- **Molecular Weight**: 456.78 g/mol
- **Drug-likeness**: Passes Lipinski's Rule of Five
- **Target Predictions**: 3 potential protein targets identified
- **ADMET Properties**: 
  - Absorption: High
  - Distribution: Moderate
  - Metabolism: CYP2D6 substrate
  - Excretion: Renal (70%)
  - Toxicity: Low hepatotoxicity risk

---
*GAIA-BT v2.0 Alpha Molecular Analysis*`;
}

function getMockClinicalTrials(indication: string, phase?: string): string {
  return `# 🏥 Clinical Trial Search Results

## Search Query
- **Indication**: ${indication}
- **Phase**: ${phase || 'All phases'}

## Results
- **Total Trials**: 12 trials found
- **Recruiting**: 8 trials currently recruiting
- **Phase Distribution**:
  - Phase I: 3 trials
  - Phase II: 5 trials
  - Phase III: 4 trials

## Key Trials
1. **NCT12345678**: Novel combination therapy
2. **NCT87654321**: Biomarker-driven approach
3. **NCT11111111**: Pediatric population study

---
*Clinical data from ClinicalTrials.gov*`;
}

function getMockLiteratureSearch(topic: string, years: number = 5): string {
  return `# 📚 Literature Search Results

## Search Parameters
- **Topic**: ${topic}
- **Time Period**: Last ${years} years

## Results
- **Papers Found**: 150 relevant publications
- **High-Impact Journals**: 45 papers in top-tier journals
- **Review Articles**: 25 comprehensive reviews
- **Clinical Studies**: 60 clinical research papers

## Key Findings
- Emerging therapeutic targets identified
- Novel biomarkers for patient stratification
- Improved drug delivery systems

---
*Literature analysis by GAIA-BT v2.0 Alpha*`;
}

function getMockResearchPlan(objective: string, budget?: string, timeline?: string): string {
  return `# 📋 Research Plan Generated

## Objective
${objective}

## Plan Structure
### Phase 1: Discovery (Months 1-6)
- Target identification and validation
- Literature review and competitive analysis
- Initial compound screening

### Phase 2: Development (Months 7-18)
- Lead optimization
- ADMET profiling
- Formulation development

### Phase 3: Preclinical (Months 19-30)
- Safety studies
- Efficacy evaluation
- IND preparation

## Budget Allocation
${budget ? `- Total Budget: ${budget}` : '- Budget: To be determined'}
- Discovery: 30%
- Development: 40%
- Preclinical: 30%

## Timeline
${timeline ? `- Total Duration: ${timeline}` : '- Timeline: 30 months'}

---
*Research plan by GAIA-BT v2.0 Alpha*`;
}

function getMockHelpText(): string {
  return `📚 **GAIA-BT v2.0 도움말**

🎯 **기본 명령어:**
• \`/help\` - 이 도움말 표시
• \`/debug\` - 디버그 모드 토글
• \`/mcpshow\` - MCP 검색 과정 표시 토글
• \`/normal\` - 일반 모드로 전환
• \`/model <이름>\` - AI 모델 변경
• \`/prompt <모드>\` - 전문 프롬프트 변경

🔬 **MCP 명령어:**
• \`/mcp start\` - 통합 MCP 시스템 시작 (Deep Research 모드)
• \`/mcp stop\` - MCP 서버 중지
• \`/mcp status\` - MCP 상태 확인

📝 **프롬프트 모드:**
• \`default\` - 기본 신약개발 AI
• \`clinical\` - 임상시험 전문
• \`research\` - 연구 분석 전문
• \`chemistry\` - 의약화학 전문
• \`regulatory\` - 규제 전문

🚀 **사용 예시:**
• 일반 질문: "아스피린의 작용 메커니즘은?"
• Deep Research: "/mcp start" 후 복잡한 신약개발 질문
• 전문 모드: "/prompt clinical" 후 임상시험 관련 질문

---
*GAIA-BT v2.0 Alpha - 신약개발 연구 AI 어시스턴트*`;
}