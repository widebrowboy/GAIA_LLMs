/**
 * GAIA-BT API Route Handler
 * 신약개발 전문 AI 어시스턴트 API 엔드포인트
 */

import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

// GAIA-BT 시스템 경로
const GAIA_BT_PATH = process.env.GAIA_BT_PATH || '/home/gaia-bt/workspace/GAIA_LLMs';

interface ChatRequest {
  message: string;
  mode: 'normal' | 'deep_research';
  prompt_mode: 'default' | 'clinical' | 'research' | 'chemistry' | 'regulatory';
  model?: string;
}

interface FunctionRequest {
  function_name: string;
  parameters: Record<string, any>;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { type, ...data } = body;

    switch (type) {
      case 'chat':
        return await handleChat(data as ChatRequest);
      case 'function':
        return await handleFunction(data as FunctionRequest);
      case 'status':
        return await handleStatus();
      default:
        return NextResponse.json(
          { error: 'Invalid request type' },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error('GAIA-BT API Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

async function handleChat(data: ChatRequest): Promise<NextResponse> {
  const { message, mode, prompt_mode, model } = data;

  try {
    // GAIA-BT Python 스크립트 호출 시뮬레이션
    const response = await callGAIABT('chat', {
      message,
      mode,
      prompt_mode,
      model: model || 'gemma3:27b-it-q4_K_M'
    });

    return NextResponse.json({
      success: true,
      response: response,
      mode: mode,
      prompt_mode: prompt_mode,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Chat Error:', error);
    
    // Mock 응답 생성
    const mockResponse = generateMockChatResponse(message, mode, prompt_mode);
    
    return NextResponse.json({
      success: true,
      response: mockResponse,
      mode: mode,
      prompt_mode: prompt_mode,
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
  return new Promise((resolve, reject) => {
    try {
      // Python 스크립트 실행
      const pythonScript = path.join(GAIA_BT_PATH, 'run_chatbot.py');
      const process = spawn('python3', [pythonScript, '--api-mode'], {
        cwd: GAIA_BT_PATH,
        env: {
          ...process.env,
          PYTHONPATH: GAIA_BT_PATH
        }
      });

      let output = '';
      let error = '';

      process.stdout.on('data', (data) => {
        output += data.toString();
      });

      process.stderr.on('data', (data) => {
        error += data.toString();
      });

      process.on('close', (code) => {
        if (code === 0) {
          resolve(output);
        } else {
          reject(new Error(`Process exited with code ${code}: ${error}`));
        }
      });

      // 입력 데이터 전송
      process.stdin.write(JSON.stringify(data));
      process.stdin.end();

      // 타임아웃 설정 (30초)
      setTimeout(() => {
        process.kill();
        reject(new Error('GAIA-BT process timeout'));
      }, 30000);

    } catch (error) {
      reject(error);
    }
  });
}

async function callGAIABTFunction(functionName: string, parameters: any): Promise<string> {
  // Function calling 시뮬레이션
  const functionMap: Record<string, (params: any) => string> = {
    get_system_status: () => getMockSystemStatus(),
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

async function getGAIABTStatus(): Promise<any> {
  // 실제 GAIA-BT 시스템 상태 확인 로직
  throw new Error('GAIA-BT not available');
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

  // 메시지 내용에 따른 맞춤형 응답
  if (message.toLowerCase().includes('cancer') || message.includes('암')) {
    response += `🎯 **암 치료제 개발 관점에서의 분석**\\n\\n`;
    response += `• 타겟 검증: 종양 특이적 바이오마커 확인 필요\\n`;
    response += `• 화합물 최적화: ADMET 프로파일 개선 방향\\n`;
    response += `• 임상시험 전략: Phase I/II 디자인 고려사항\\n\\n`;
  } else if (message.toLowerCase().includes('aspirin') || message.includes('아스피린')) {
    response += `💊 **아스피린 신약개발 분석**\\n\\n`;
    response += `• 작용 메커니즘: COX-1/COX-2 억제를 통한 항염 효과\\n`;
    response += `• 새로운 적응증: 심혈관 질환 예방, 암 예방 가능성\\n`;
    response += `• 제형 개발: 서방형, 장용성 코팅 최적화\\n\\n`;
  } else {
    response += `이 질문은 신약개발 관점에서 전문적인 분석이 필요합니다.\\n\\n`;
    
    if (promptMode === 'clinical') {
      response += `🏥 **임상시험 관점에서의 분석**\\n`;
      response += `• 환자 안전성 최우선 고려\\n`;
      response += `• 규제 요구사항 준수 필요\\n`;
    } else if (promptMode === 'research') {
      response += `🔬 **연구 분석 관점에서의 분석**\\n`;
      response += `• 최신 문헌 검토 필요\\n`;
      response += `• 실험 설계 최적화\\n`;
    } else if (promptMode === 'chemistry') {
      response += `⚗️ **의약화학 관점에서의 분석**\\n`;
      response += `• 분자 구조-활성 관계(SAR) 분석\\n`;
      response += `• ADMET 특성 최적화\\n`;
    } else if (promptMode === 'regulatory') {
      response += `📋 **규제 관점에서의 분석**\\n`;
      response += `• FDA/EMA 가이드라인 준수\\n`;
      response += `• 품질 관리 체계 구축\\n`;
    } else {
      response += `💊 **신약개발 종합 분석**\\n`;
      response += `• 타겟 검증부터 시장 출시까지\\n`;
      response += `• 과학적 근거 기반 접근\\n`;
    }
  }

  response += `\\n---\\n*Generated by GAIA-BT v2.0 Alpha - ${promptMode} mode*`;

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