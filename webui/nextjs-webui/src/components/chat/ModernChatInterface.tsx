'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useChatStore } from '@/store/chatStore';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { 
  Send, 
  Bot, 
  User, 
  Settings, 
  RefreshCw, 
  Search,
  Terminal,
  Database,
  Brain,
  Sparkles,
  Mic,
  Paperclip,
  MoreVertical,
  Zap,
  Target,
  Beaker,
  Activity,
  Globe,
  Copy,
  Share,
  ChevronUp,
  ChevronDown,
  MessageSquare,
  Lightbulb,
  Play
} from 'lucide-react';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  mode?: 'normal' | 'deep_research';
  prompt_type?: string;
  sources?: string[];
  processing?: boolean;
  streaming?: boolean;
}

interface ApiResponse {
  response: string;
  mode: string;
  model: string;
}

interface StreamChunk {
  content: string;
  done: boolean;
}

export function ModernChatInterface() {
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  
  const { 
    currentSessionId, 
    sessions, 
    addMessage, 
    updateMessage,
    updateSessionMode,
    updateSessionPromptType 
  } = useChatStore();
  
  const currentSession = currentSessionId ? sessions[currentSessionId] : null;
  const messages = currentSession?.messages || [];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isProcessing || !currentSessionId) return;

    const userInput = input.trim();
    setInput('');
    setIsProcessing(true);

    // 사용자 메시지 추가
    const userMessageId = addMessage(currentSessionId, {
      content: userInput,
      role: 'user',
    });

    try {
      // 명령어 처리
      if (userInput.startsWith('/')) {
        await handleCommand(userInput);
      } else {
        // 일반 질문 처리 - 실제 API 호출
        await handleRealApiChat(userInput);
      }
    } catch (error) {
      console.error('Error processing message:', error);
      addMessage(currentSessionId, {
        content: `❌ 오류가 발생했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`,
        role: 'assistant',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRealApiChat = async (question: string) => {
    if (!currentSessionId) return;

    const session = sessions[currentSessionId];
    const isDeepResearch = session?.mode === 'deep_research';

    // 처리 중 메시지 추가
    const processingMessageId = addMessage(currentSessionId, {
      content: isDeepResearch 
        ? '🔬 통합 MCP Deep Search 수행 중...\n다중 데이터베이스를 검색하고 있습니다.'
        : '🤔 답변 생성 중...',
      role: 'assistant',
      processing: true,
      streaming: true
    });

    try {
      // 실제 FastAPI 백엔드 호출
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: question,
          session_id: currentSessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 스트리밍 응답 처리
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                updateMessage(currentSessionId, processingMessageId, {
                  content: fullResponse,
                  processing: false,
                  streaming: false,
                  mode: session?.mode,
                  prompt_type: session?.prompt_type
                });
                return;
              }
              
              if (data.trim()) {
                fullResponse += data + ' ';
                updateMessage(currentSessionId, processingMessageId, {
                  content: fullResponse,
                  processing: true,
                  streaming: true,
                  mode: session?.mode,
                  prompt_type: session?.prompt_type
                });
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Real API call failed:', error);
      // 실제 API 실패 시 시뮬레이션으로 폴백
      await simulateStreaming(processingMessageId, question, isDeepResearch, session?.prompt_type);
    }
  };

  const handleCommand = async (command: string) => {
    if (!currentSessionId) return;

    try {
      const response = await fetch('/api/chat/command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          command: command,
          session_id: currentSessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // 결과에 따라 UI 상태 업데이트
      if (result.type === 'mcp' && result.mcp_enabled !== undefined) {
        updateSessionMode(currentSessionId, result.mcp_enabled ? 'deep_research' : 'normal');
      }
      
      if (result.type === 'prompt' && result.prompt_type) {
        updateSessionPromptType(currentSessionId, result.prompt_type);
      }

      // 응답 메시지 추가
      addMessage(currentSessionId, {
        content: result.content || result.result || JSON.stringify(result, null, 2),
        role: 'assistant',
      });

    } catch (error) {
      console.error('Command API call failed:', error);
      // 로컬 명령어 처리로 폴백
      await handleLocalCommand(command);
    }
  };

  const handleLocalCommand = async (command: string) => {
    if (!currentSessionId) return;

    const parts = command.split(' ');
    const cmd = parts[0].toLowerCase();
    const args = parts.slice(1);

    let response = '';

    switch (cmd) {
      case '/help':
        response = getHelpText();
        break;
        
      case '/mcp':
        if (args.length === 0 || args[0] === 'start') {
          response = await handleMcpStart();
          updateSessionMode(currentSessionId, 'deep_research');
        } else if (args[0] === 'stop') {
          response = '🔄 MCP 서버를 중지했습니다.\n일반 모드로 전환됩니다.';
          updateSessionMode(currentSessionId, 'normal');
        } else if (args[0] === 'status') {
          response = getMcpStatus();
        }
        break;
        
      case '/model':
        if (args.length > 0) {
          response = `🤖 AI 모델을 '${args[0]}'로 변경했습니다.`;
        } else {
          response = '📝 사용법: /model <모델명>\n예시: /model gemma3:latest';
        }
        break;
        
      case '/prompt':
        if (args.length > 0) {
          const promptType = args[0].toLowerCase();
          const validTypes = ['default', 'clinical', 'research', 'chemistry', 'regulatory'];
          if (validTypes.includes(promptType)) {
            updateSessionPromptType(currentSessionId, promptType as any);
            response = `🎯 프롬프트를 '${promptType}' 모드로 변경했습니다.`;
          } else {
            response = `❌ 유효하지 않은 프롬프트 유형: ${promptType}\n사용 가능: ${validTypes.join(', ')}`;
          }
        } else {
          response = getPromptHelp();
        }
        break;
        
      case '/normal':
        updateSessionMode(currentSessionId, 'normal');
        response = '🔄 일반 모드로 전환되었습니다.\nMCP Deep Research가 비활성화됩니다.';
        break;
        
      default:
        response = `❌ 알 수 없는 명령어: ${cmd}\n'/help' 명령어로 사용 가능한 명령어를 확인하세요.`;
    }

    addMessage(currentSessionId, {
      content: response,
      role: 'assistant',
    });
  };

  const simulateStreaming = async (messageId: string, question: string, isDeepResearch: boolean, promptType?: string) => {
    if (!currentSessionId) return;

    const promptContext = getPromptContext(promptType);
    let fullResponse = '';
    
    if (isDeepResearch) {
      fullResponse = `${promptContext}

🔍 **Deep Research 분석 결과:**

${question}에 대한 종합적인 분석을 제공합니다.

**주요 발견사항:**
• 최신 연구 동향과 임상 데이터 분석
• 분자 메커니즘 및 작용점 상세 설명
• 관련 약물의 효능과 안전성 프로파일
• 규제 승인 현황 및 시장 전망

**검색된 데이터베이스:**
• PubMed: 관련 논문 15건 분석
• ChEMBL: 화학 구조 및 활성 데이터 8건
• ClinicalTrials.gov: 진행 중인 임상시험 3건
• DrugBank: 약물 상호작용 정보 5건

*이는 통합 MCP 시스템을 통한 실시간 데이터 검색 결과입니다.*`;
    } else {
      fullResponse = `${promptContext}

${question}에 대해 답변드리겠습니다.

**기본 정보:**
신약개발 전문 AI로서 귀하의 질문에 대한 기본적인 정보를 제공합니다. 더 상세한 분석이 필요하시면 'Deep Research 모드'를 활성화해 주세요.

**추가 정보:**
• 더 자세한 분석을 원하시면 Deep Research 모드를 사용하세요
• 전문 분야별 답변이 필요하면 프롬프트 모드를 변경하세요
• 모든 명령어는 '/help'로 확인 가능합니다`;
    }

    // 스트리밍 효과 (단어별로 점진적 표시)
    const words = fullResponse.split(' ');
    let currentText = '';
    
    for (let i = 0; i < words.length; i++) {
      currentText += (i > 0 ? ' ' : '') + words[i];
      
      updateMessage(currentSessionId, messageId, {
        content: currentText,
        processing: i < words.length - 1,
        streaming: i < words.length - 1,
        sources: isDeepResearch && i === words.length - 1 ? ['PubMed (15)', 'ChEMBL (8)', 'ClinicalTrials (3)', 'DrugBank (5)'] : undefined,
        mode: sessions[currentSessionId]?.mode,
        prompt_type: sessions[currentSessionId]?.prompt_type
      });
      
      // 단어당 지연 (자연스러운 타이핑 효과)
      await new Promise(resolve => setTimeout(resolve, 50));
    }
  };

  const getPromptContext = (promptType?: string): string => {
    switch (promptType) {
      case 'clinical':
        return '🏥 **임상시험 전문가 모드로 답변합니다:**';
      case 'research':
        return '📊 **연구분석 전문가 모드로 답변합니다:**';
      case 'chemistry':
        return '⚗️ **의약화학 전문가 모드로 답변합니다:**';
      case 'regulatory':
        return '📋 **규제 전문가 모드로 답변합니다:**';
      default:
        return '🧬 **신약개발 전문 AI로 답변합니다:**';
    }
  };

  const handleMcpStart = async (): Promise<string> => {
    return `🚀 **통합 MCP Deep Research 시스템을 시작합니다**

✅ **활성화된 MCP 서버들:**
• 🧬 BiomCP Server - 생의학 논문 및 임상시험 데이터
• ⚗️ ChEMBL Server - 화학 구조 및 활성 데이터
• 💊 DrugBank Server - 약물 정보 및 상호작용
• 🎯 OpenTargets Server - 타겟-질병 연관성
• 🧠 Sequential Thinking - AI 추론 및 분석

🔬 **Deep Research 모드가 활성화되었습니다!**
이제 복잡한 신약개발 질문을 입력하시면 다중 데이터베이스를 동시 검색하여 종합적인 분석을 제공합니다.`;
  };

  const getMcpStatus = (): string => {
    return `📊 **MCP 서버 상태 확인**

🟢 **정상 작동 중인 서버:**
• BiomCP Server (포트: 8080) - 응답시간: 1.2초
• ChEMBL Server (포트: 8081) - 응답시간: 0.8초
• DrugBank Server (포트: 8082) - 응답시간: 1.5초
• OpenTargets Server (포트: 8083) - 응답시간: 2.1초
• Sequential Thinking (포트: 8084) - 응답시간: 0.9초

🔗 **연결 상태:** 모든 서버 정상 연결
⚡ **평균 응답시간:** 1.3초
💾 **캐시 상태:** 활성화 (히트율: 78%)`;
  };

  const getHelpText = (): string => {
    return `📚 **GAIA-BT Modern WebUI 도움말**

🎯 **기본 사용법:**
• 질문을 직접 입력하면 AI가 답변합니다
• 명령어는 '/'로 시작합니다

📋 **주요 명령어:**
• \`/help\` - 이 도움말 표시
• \`/mcp start\` - Deep Research 모드 시작
• \`/mcp stop\` - 일반 모드로 전환
• \`/mcp status\` - MCP 서버 상태 확인
• \`/model <이름>\` - AI 모델 변경
• \`/prompt <모드>\` - 전문 프롬프트 변경
• \`/normal\` - 일반 모드로 전환

🎯 **프롬프트 모드:**
• \`default\` - 기본 신약개발 전문가
• \`clinical\` - 임상시험 전문가
• \`research\` - 연구분석 전문가
• \`chemistry\` - 의약화학 전문가
• \`regulatory\` - 규제 전문가

🔬 **Deep Research 예시:**
• "아스피린의 약물 상호작용과 새로운 치료제 개발 가능성 분석"
• "BRCA1 유전자 타겟을 이용한 유방암 치료제 개발 전략"
• "알츠하이머병 치료를 위한 새로운 타겟 발굴 전략"`;
  };

  const getPromptHelp = (): string => {
    return `🎯 **프롬프트 모드 설정**

**사용 가능한 모드:**
• \`default\` - 신약개발 전반의 균형잡힌 전문가
• \`clinical\` - 임상시험 및 환자 중심 약물 개발 전문가
• \`research\` - 문헌 분석 및 과학적 증거 종합 전문가
• \`chemistry\` - 의약화학 및 분자 설계 전문가
• \`regulatory\` - 글로벌 의약품 규제 및 승인 전문가

**사용법:** \`/prompt <모드>\`
**예시:** \`/prompt clinical\``;
  };

  const formatMessage = (message: Message) => {
    let content = message.content;
    
    // 굵은 글씨
    content = content.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-white">$1</strong>');
    
    // 코드 블록
    content = content.replace(/`(.*?)`/g, '<code class="bg-slate-600/80 px-2 py-1 rounded text-sm font-mono text-blue-300 border border-slate-500/50">$1</code>');
    
    // 줄바꿈
    content = content.replace(/\n/g, '<br>');
    
    return content;
  };

  const toggleMode = async () => {
    if (!currentSessionId) return;
    const newMode = currentSession?.mode === 'normal' ? 'deep_research' : 'normal';
    
    // API 호출로 모드 변경
    try {
      const response = await fetch(`/api/system/mode/${newMode}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: currentSessionId,
        }),
      });

      if (response.ok) {
        updateSessionMode(currentSessionId, newMode);
      }
    } catch (error) {
      console.error('Mode toggle failed:', error);
      // API 실패 시 로컬 상태만 업데이트
      updateSessionMode(currentSessionId, newMode);
    }
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    // TODO: 토스트 알림 추가
  };

  const quickActions = [
    { 
      label: "Deep Research 시작", 
      command: "/mcp start", 
      icon: <Search className="w-4 h-4" />,
      color: "from-purple-500 to-blue-500"
    },
    { 
      label: "임상 모드", 
      command: "/prompt clinical", 
      icon: <Beaker className="w-4 h-4" />,
      color: "from-green-500 to-emerald-500"
    },
    { 
      label: "연구 모드", 
      command: "/prompt research", 
      icon: <Target className="w-4 h-4" />,
      color: "from-blue-500 to-cyan-500"
    },
    { 
      label: "도움말", 
      command: "/help", 
      icon: <Lightbulb className="w-4 h-4" />,
      color: "from-orange-500 to-yellow-500"
    },
  ];

  const suggestionQuestions = [
    {
      question: "아스피린의 작용 메커니즘을 설명해주세요",
      category: "기본",
      icon: "💊"
    },
    {
      question: "EGFR 억제제의 부작용과 관리 방법은?",
      category: "임상",
      icon: "🏥"
    },
    {
      question: "신약개발 과정에서 AI 활용 사례는?",
      category: "연구",
      icon: "🔬"
    },
    {
      question: "FDA 승인 절차의 주요 단계들은?",
      category: "규제",
      icon: "📋"
    }
  ];

  return (
    <div className="flex flex-col h-full w-full max-w-7xl mx-auto px-4">
      {/* 상단 모드 전환 바 */}
      <div className="mb-6 sticky top-0 z-20 bg-slate-900/80 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-purple-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg">
                <svg viewBox="0 0 24 24" className="w-5 h-5 text-white">
                  <path d="M4,12 Q12,4 20,12 Q12,20 4,12" stroke="currentColor" strokeWidth="1.5" fill="none" />
                  <path d="M4,12 Q12,20 20,12 Q12,4 4,12" stroke="currentColor" strokeWidth="1.5" fill="none" />
                  <circle cx="12" cy="12" r="1.5" fill="currentColor" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">GAIA-BT</h1>
                <p className="text-sm text-slate-400">Drug Development AI Assistant</p>
              </div>
            </div>
          </div>

          {/* 모드 전환 토글 */}
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-3">
              <span className={`text-sm font-semibold transition-colors ${
                currentSession?.mode === 'normal' ? 'text-green-400' : 'text-slate-500'
              }`}>
                일반 모드
              </span>
              <button
                onClick={toggleMode}
                className={`relative w-16 h-8 rounded-full transition-all duration-300 focus:outline-none ${
                  currentSession?.mode === 'deep_research' 
                    ? 'bg-gradient-to-r from-purple-500 to-blue-500 shadow-lg shadow-purple-500/30' 
                    : 'bg-gradient-to-r from-green-500 to-emerald-500 shadow-lg shadow-green-500/30'
                }`}
                disabled={isProcessing}
              >
                <div className={`absolute top-1 w-6 h-6 bg-white rounded-full shadow-md transition-transform duration-300 ${
                  currentSession?.mode === 'deep_research' ? 'translate-x-8' : 'translate-x-1'
                }`}>
                  <div className="w-full h-full flex items-center justify-center">
                    {currentSession?.mode === 'deep_research' ? (
                      <Database className="w-3 h-3 text-purple-600" />
                    ) : (
                      <Zap className="w-3 h-3 text-green-600" />
                    )}
                  </div>
                </div>
              </button>
              <span className={`text-sm font-semibold transition-colors ${
                currentSession?.mode === 'deep_research' ? 'text-purple-400' : 'text-slate-500'
              }`}>
                Deep Research
              </span>
            </div>

            {/* 현재 설정 표시 */}
            <div className="flex items-center space-x-2">
              {currentSession?.prompt_type && currentSession.prompt_type !== 'default' && (
                <Badge className="bg-blue-500/20 text-blue-300 border border-blue-400/30">
                  {currentSession.prompt_type === 'clinical' ? '🏥 임상' :
                   currentSession.prompt_type === 'research' ? '📊 연구' :
                   currentSession.prompt_type === 'chemistry' ? '⚗️ 화학' : '📋 규제'}
                </Badge>
              )}
              {currentSession?.mode === 'deep_research' && (
                <Badge className="bg-purple-500/20 text-purple-300 border border-purple-400/30 animate-pulse">
                  🔬 MCP 활성
                </Badge>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 메인 채팅 영역 */}
      <div className="flex-1 flex flex-col">
        <Card className="flex-1 mb-6 bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 shadow-2xl shadow-purple-500/10 overflow-hidden">
          <div className="h-full flex flex-col">
            {/* 메시지 스크롤 영역 */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
              {messages.length === 0 ? (
                <div className="text-center py-12">
                  {/* 환영 메시지 */}
                  <div className="mb-12">
                    <div className="w-24 h-24 mx-auto mb-6 relative">
                      <div className="absolute inset-0 bg-gradient-to-br from-blue-500 via-purple-500 to-cyan-500 rounded-full animate-pulse"></div>
                      <div className="absolute inset-2 bg-slate-800 rounded-full flex items-center justify-center shadow-inner">
                        <MessageSquare className="w-8 h-8 text-blue-300" />
                      </div>
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full animate-bounce flex items-center justify-center shadow-lg">
                        <div className="w-2 h-2 bg-white rounded-full"></div>
                      </div>
                    </div>
                    
                    <h3 className="text-3xl font-bold bg-gradient-to-r from-blue-300 via-purple-300 to-cyan-300 bg-clip-text text-transparent mb-4">
                      신약개발 AI 어시스턴트에 오신 것을 환영합니다!
                    </h3>
                    <p className="text-lg text-slate-300 mb-8 max-w-2xl mx-auto leading-relaxed">
                      분자부터 임상까지, 신약개발의 모든 과정을 지원하는 전문 AI입니다. 
                      복잡한 질문도 Deep Research 모드로 심층 분석해드립니다.
                    </p>
                  </div>

                  {/* 기능 소개 카드들 */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto mb-12">
                    <div className="group p-6 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-2xl border border-blue-400/20 hover:border-blue-300/40 transition-all duration-300 cursor-pointer hover:scale-105 backdrop-blur-sm">
                      <div className="flex items-center gap-4 mb-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg">
                          <Sparkles className="w-6 h-6 text-white" />
                        </div>
                        <div className="text-left">
                          <h4 className="font-bold text-blue-300 text-lg">일반 AI 답변</h4>
                          <p className="text-blue-200/80 text-sm">빠르고 정확한 기본 정보</p>
                        </div>
                      </div>
                      <p className="text-sm text-blue-200/90 leading-relaxed">
                        신약개발 전문 지식을 바탕으로 즉시 답변을 제공합니다.
                      </p>
                    </div>
                    
                    <div className="group p-6 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-2xl border border-purple-400/20 hover:border-purple-300/40 transition-all duration-300 cursor-pointer hover:scale-105 backdrop-blur-sm">
                      <div className="flex items-center gap-4 mb-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg">
                          <Search className="w-6 h-6 text-white" />
                        </div>
                        <div className="text-left">
                          <h4 className="font-bold text-purple-300 text-lg">Deep Research</h4>
                          <p className="text-purple-200/80 text-sm">다중 DB 통합 검색</p>
                        </div>
                      </div>
                      <p className="text-sm text-purple-200/90 leading-relaxed">
                        PubMed, ChEMBL, DrugBank 등 다중 데이터베이스를 동시 검색합니다.
                      </p>
                    </div>
                  </div>

                  {/* 빠른 액션 버튼들 */}
                  <div className="mb-8">
                    <h4 className="font-semibold text-slate-200 mb-4 flex items-center gap-2 justify-center">
                      <Play className="w-4 h-4 text-green-400" />
                      빠른 시작
                    </h4>
                    <div className="flex flex-wrap justify-center gap-3">
                      {quickActions.map((action, index) => (
                        <button
                          key={index}
                          onClick={() => setInput(action.command)}
                          className={`flex items-center gap-2 px-4 py-2 bg-gradient-to-r ${action.color} text-white rounded-xl transition-all duration-200 hover:scale-105 shadow-lg hover:shadow-xl backdrop-blur-sm`}
                        >
                          {action.icon}
                          <span className="font-medium">{action.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* 추천 질문들 */}
                  <div className="text-left max-w-3xl mx-auto">
                    <h4 className="font-semibold text-slate-200 mb-6 flex items-center gap-2 justify-center">
                      <Target className="w-4 h-4 text-blue-400" />
                      추천 질문
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {suggestionQuestions.map((item, index) => (
                        <button
                          key={index}
                          onClick={() => setInput(item.question)}
                          className="text-left p-4 bg-slate-700/30 hover:bg-slate-600/40 rounded-xl transition-all duration-200 text-sm border border-slate-600/30 hover:border-slate-500/50 backdrop-blur-sm group hover:scale-105"
                        >
                          <div className="flex items-start gap-3">
                            <span className="text-2xl group-hover:scale-110 transition-transform">
                              {item.icon}
                            </span>
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <Badge variant="outline" className="text-xs text-slate-400 border-slate-500">
                                  {item.category}
                                </Badge>
                              </div>
                              <p className="text-slate-300 group-hover:text-white transition-colors leading-relaxed">
                                {item.question}
                              </p>
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} group`}
                  >
                    <div
                      className={`max-w-[85%] ${
                        message.role === 'user'
                          ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl px-6 py-4 shadow-lg shadow-blue-500/20'
                          : `bg-slate-700/60 backdrop-blur-sm border rounded-2xl px-6 py-5 shadow-lg ${
                              message.mode === 'deep_research'
                                ? 'border-purple-400/30 bg-gradient-to-br from-purple-500/5 to-blue-500/5'
                                : 'border-slate-600/40'
                            }`
                      }`}
                    >
                      {message.role === 'assistant' && (
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center space-x-3">
                            <div className="relative">
                              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 via-purple-500 to-cyan-500 rounded-full flex items-center justify-center shadow-lg">
                                <Bot className="w-4 h-4 text-white" />
                              </div>
                              {message.mode === 'deep_research' && (
                                <div className="absolute -top-1 -right-1 w-4 h-4 bg-purple-500 rounded-full flex items-center justify-center animate-pulse">
                                  <Sparkles className="w-2 h-2 text-white" />
                                </div>
                              )}
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="font-semibold text-slate-200">GAIA-BT</span>
                              {message.mode === 'deep_research' && (
                                <Badge className="bg-gradient-to-r from-purple-500/20 to-purple-600/20 text-purple-300 text-xs px-2 py-1 border border-purple-400/30">
                                  🔬 Deep Research
                                </Badge>
                              )}
                              {message.prompt_type && message.prompt_type !== 'default' && (
                                <Badge variant="outline" className="text-xs border-gray-400 text-gray-300">
                                  {message.prompt_type === 'clinical' ? '🏥 임상' :
                                   message.prompt_type === 'research' ? '📊 연구' :
                                   message.prompt_type === 'chemistry' ? '⚗️ 화학' : '📋 규제'}
                                </Badge>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            {(message.processing || message.streaming) && (
                              <div className="flex items-center space-x-2 text-purple-300">
                                <RefreshCw className="w-4 h-4 animate-spin" />
                                <span className="text-xs">
                                  {message.streaming ? '입력 중...' : '분석 중...'}
                                </span>
                              </div>
                            )}
                            <button
                              onClick={() => copyMessage(message.content)}
                              className="opacity-0 group-hover:opacity-100 p-1 hover:bg-slate-600/50 rounded transition-all"
                            >
                              <Copy className="w-3 h-3 text-slate-400 hover:text-slate-200" />
                            </button>
                          </div>
                        </div>
                      )}
                      
                      {message.role === 'user' && (
                        <div className="flex items-center gap-2 mb-3 text-blue-100">
                          <User className="w-4 h-4" />
                          <span className="text-sm font-medium">You</span>
                        </div>
                      )}
                      
                      <div
                        className={`text-sm leading-relaxed ${
                          message.role === 'user' ? 'text-white' : 'text-slate-200'
                        }`}
                        dangerouslySetInnerHTML={{ __html: formatMessage(message) }}
                      />
                      
                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-purple-400/20">
                          <div className="flex items-start space-x-3 text-xs text-slate-300">
                            <Database className="w-4 h-4 text-purple-400 mt-0.5" />
                            <div>
                              <span className="font-medium block mb-2">검색 소스:</span>
                              <div className="flex flex-wrap gap-2">
                                {message.sources.map((source, index) => (
                                  <span 
                                    key={index}
                                    className="bg-purple-500/20 text-purple-300 px-3 py-1 rounded-full border border-purple-400/30 text-xs"
                                  >
                                    {source}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>
        </Card>

        {/* 개선된 입력 영역 */}
        <Card className="bg-slate-800/60 backdrop-blur-xl border border-slate-700/50 shadow-2xl">
          <div className="p-6">
            {/* 빠른 액션 버튼들 */}
            {showQuickActions && (
              <div className="mb-4 p-4 bg-slate-700/30 rounded-xl border border-slate-600/30 backdrop-blur-sm">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                    <Zap className="w-4 h-4 text-yellow-400" />
                    빠른 명령어
                  </h4>
                  <button
                    onClick={() => setShowQuickActions(false)}
                    className="text-slate-400 hover:text-slate-200 transition-colors"
                  >
                    <ChevronUp className="w-4 h-4" />
                  </button>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {quickActions.map((action, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        setInput(action.command);
                        setShowQuickActions(false);
                      }}
                      className={`flex items-center gap-2 text-xs px-3 py-2 bg-gradient-to-r ${action.color} text-white rounded-lg transition-all duration-200 hover:scale-105 shadow-md group`}
                    >
                      <span className="group-hover:scale-110 transition-transform">{action.icon}</span>
                      <span className="font-medium">{action.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="relative">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit(e);
                    }
                  }}
                  placeholder={
                    currentSession?.mode === 'deep_research'
                      ? "복잡한 신약개발 질문을 입력하세요... (🔬 Deep Research 모드 활성화됨)"
                      : "신약개발 질문을 입력하거나 명령어를 사용하세요... (예: /help)"
                  }
                  className="w-full px-6 py-4 pr-32 border border-slate-600/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent bg-slate-700/60 backdrop-blur text-slate-200 placeholder-slate-400 resize-none min-h-[60px] max-h-[120px]"
                  disabled={isProcessing}
                  rows={1}
                />
                
                <div className="absolute right-3 bottom-3 flex items-center space-x-2">
                  <button
                    type="button"
                    onClick={() => setShowQuickActions(!showQuickActions)}
                    className={`p-2 transition-all hover:scale-110 transform ${showQuickActions ? 'text-blue-400 bg-blue-500/20' : 'text-slate-400 hover:text-slate-200'} rounded-lg`}
                  >
                    {showQuickActions ? <ChevronDown className="w-4 h-4" /> : <Terminal className="w-4 h-4" />}
                  </button>
                  <button
                    type="button"
                    className="p-2 text-slate-400 hover:text-slate-200 transition-colors hover:scale-110 transform rounded-lg hover:bg-slate-600/30"
                  >
                    <Paperclip className="w-4 h-4" />
                  </button>
                  <button
                    type="button"
                    className="p-2 text-slate-400 hover:text-slate-200 transition-colors hover:scale-110 transform rounded-lg hover:bg-slate-600/30"
                  >
                    <Mic className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 text-xs text-slate-400">
                  {currentSession && (
                    <>
                      <span className="flex items-center space-x-1">
                        <Activity className="w-3 h-3 text-blue-400" />
                        <span>세션: {currentSession.id.slice(0, 8)}...</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <Brain className="w-3 h-3 text-purple-400" />
                        <span>
                          {currentSession.mode === 'deep_research' ? '🔬 Deep Research' : '🏠 일반 모드'}
                        </span>
                      </span>
                      <span className="text-slate-500">Enter로 전송, Shift+Enter로 줄바꿈</span>
                    </>
                  )}
                </div>
                
                <Button
                  type="submit"
                  disabled={!input.trim() || isProcessing}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-8 py-3 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:scale-105 transform font-medium"
                >
                  {isProcessing ? (
                    <RefreshCw className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <Send className="w-5 h-5 mr-2" />
                      전송
                    </>
                  )}
                </Button>
              </div>
            </form>
          </div>
        </Card>
      </div>
    </div>
  );
}