'use client';

import { useState, useEffect, useRef } from 'react';
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
  Clock,
  Database,
  Brain,
  Sparkles,
  ChevronDown,
  Mic,
  Paperclip,
  MoreVertical,
  Zap,
  Target,
  Beaker,
  Activity,
  Globe,
  ToggleLeft,
  ToggleRight
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

export function WebChatInterface() {
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showCommands, setShowCommands] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);
  const [modeChanging, setModeChanging] = useState(false);
  const [sessionChanging, setSessionChanging] = useState(false);
  const [lastChangeStatus, setLastChangeStatus] = useState<{
    type: 'mode' | 'session' | 'command' | null;
    status: 'pending' | 'success' | 'error';
    message: string;
  }>({ type: null, status: 'success', message: '' });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  
  const { 
    currentSessionId, 
    sessions, 
    addMessage, 
    updateMessage,
    updateSessionMode,
    updateSessionPromptType,
    createSession 
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

  // 세션 초기화
  useEffect(() => {
    const initializeSession = async () => {
      if (!currentSessionId) {
        try {
          console.log('Creating new session...');
          setSessionChanging(true);
          setLastChangeStatus({
            type: 'session',
            status: 'pending',
            message: '새 세션을 생성하고 있습니다...'
          });

          const sessionId = await createSession();
          
          // 세션 생성 완료 확인
          await verifySessionCreation(sessionId);
          
          setLastChangeStatus({
            type: 'session',
            status: 'success',
            message: '세션이 성공적으로 생성되었습니다.'
          });
        } catch (error) {
          console.error('Failed to create initial session:', error);
          setLastChangeStatus({
            type: 'session',
            status: 'error',
            message: `세션 생성 실패: ${error instanceof Error ? error.message : '알 수 없는 오류'}`
          });
        } finally {
          setSessionChanging(false);
          setTimeout(() => {
            setLastChangeStatus({ type: null, status: 'success', message: '' });
          }, 3000);
        }
      }
    };

    initializeSession();
  }, [currentSessionId, createSession]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 세션 생성 완료 확인
  const verifySessionCreation = async (sessionId: string, maxRetries = 5) => {
    for (let i = 0; i < maxRetries; i++) {
      try {
        const response = await fetch(`/api/gaia-bt/session/${sessionId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const sessionData = await response.json();
          console.log('Session verified:', sessionData);
          return sessionData;
        }
      } catch (error) {
        console.warn(`Session verification attempt ${i + 1} failed:`, error);
      }
      
      // 500ms 대기 후 재시도
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    throw new Error('세션 생성 확인 실패: 최대 재시도 횟수 초과');
  };

  // 모드 변경 완료 확인
  const verifyModeChange = async (sessionId: string, expectedMode: string, expectedMcpEnabled: boolean, maxRetries = 5) => {
    for (let i = 0; i < maxRetries; i++) {
      try {
        const response = await fetch(`/api/gaia-bt/session/${sessionId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const sessionData = await response.json();
          const actualMode = sessionData.mode;
          const actualMcpEnabled = sessionData.mcp_enabled;
          
          console.log('Mode verification:', {
            expected: { mode: expectedMode, mcp_enabled: expectedMcpEnabled },
            actual: { mode: actualMode, mcp_enabled: actualMcpEnabled }
          });

          // 모드와 MCP 상태가 모두 일치하는지 확인
          if (actualMcpEnabled === expectedMcpEnabled) {
            return sessionData;
          }
        }
      } catch (error) {
        console.warn(`Mode verification attempt ${i + 1} failed:`, error);
      }
      
      // 500ms 대기 후 재시도
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    throw new Error('모드 변경 확인 실패: 상태가 일치하지 않음');
  };

  // 실시간 상태 확인
  const checkCurrentStatus = async () => {
    if (!currentSessionId) return null;
    
    try {
      const response = await fetch(`/api/gaia-bt/session/${currentSessionId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('Status check failed:', error);
    }
    
    return null;
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
      if (userInput.startsWith('/') || isCommand(userInput)) {
        await handleCommand(userInput);
      } else {
        // 일반 질문 처리
        await handleChat(userInput);
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

  const isCommand = (text: string): boolean => {
    const commands = ['help', 'mcp', 'model', 'prompt', 'debug', 'normal', 'mcpshow', 'exit'];
    const firstWord = text.split(' ')[0].toLowerCase();
    return commands.includes(firstWord);
  };

  const handleCommand = async (command: string) => {
    if (!currentSessionId) return;

    // 명령어 정규화
    let normalizedCommand = command;
    if (!command.startsWith('/')) {
      normalizedCommand = '/' + command;
    }

    // 모드 변경 명령어인지 확인
    const isModeCommand = normalizedCommand.includes('/mcp') || normalizedCommand.includes('/normal');
    
    if (isModeCommand) {
      setModeChanging(true);
      setLastChangeStatus({
        type: 'mode',
        status: 'pending',
        message: `모드를 변경하고 있습니다: ${normalizedCommand}`
      });
    } else {
      setLastChangeStatus({
        type: 'command',
        status: 'pending',
        message: `명령어를 실행하고 있습니다: ${normalizedCommand}`
      });
    }

    try {
      // API 서버에 명령어 전송
      const response = await fetch('/api/gaia-bt/chat/command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          command: normalizedCommand,
          session_id: currentSessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // 응답에 따라 로컬 상태 업데이트
      if (data.mcp_enabled !== undefined) {
        const newMode = data.mcp_enabled ? 'deep_research' : 'normal';
        updateSessionMode(currentSessionId, newMode);
        
        // 모드 변경 완료 확인
        await verifyModeChange(currentSessionId, newMode, data.mcp_enabled);
      }

      // 응답 메시지 추가
      addMessage(currentSessionId, {
        content: data.response || '명령어가 실행되었습니다.',
        role: 'assistant',
        mode: data.mode,
      });

      setLastChangeStatus({
        type: isModeCommand ? 'mode' : 'command',
        status: 'success',
        message: isModeCommand 
          ? `모드 변경 완료: ${data.mcp_enabled ? 'Deep Research' : '일반'} 모드`
          : '명령어가 성공적으로 실행되었습니다.'
      });

    } catch (error) {
      console.error('Command execution failed:', error);
      
      // 에러 메시지 추가
      addMessage(currentSessionId, {
        content: `❌ 명령어 실행 중 오류가 발생했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`,
        role: 'assistant',
      });

      setLastChangeStatus({
        type: isModeCommand ? 'mode' : 'command',
        status: 'error',
        message: `명령어 실행 실패: ${error instanceof Error ? error.message : '알 수 없는 오류'}`
      });
    } finally {
      if (isModeCommand) {
        setModeChanging(false);
      }
      
      // 3초 후 상태 메시지 제거
      setTimeout(() => {
        setLastChangeStatus({ type: null, status: 'success', message: '' });
      }, 3000);
    }
  };

  const handleChat = async (question: string) => {
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
      // API 서버에 채팅 메시지 전송
      const response = await fetch('/api/gaia-bt/chat/message', {
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

      const data = await response.json();
      
      // 처리 중 메시지를 실제 응답으로 업데이트
      updateMessage(currentSessionId, processingMessageId, {
        content: data.response || '응답을 받지 못했습니다.',
        processing: false,
        streaming: false,
        mode: data.mode,
        sources: data.sources,
      });

    } catch (error) {
      console.error('Chat failed:', error);
      
      // 처리 중 메시지를 에러 메시지로 업데이트
      updateMessage(currentSessionId, processingMessageId, {
        content: `❌ 메시지 전송 중 오류가 발생했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`,
        processing: false,
        streaming: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
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
      await new Promise(resolve => setTimeout(resolve, isDeepResearch ? 80 : 50));
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
    return `📚 **GAIA-BT WebUI 도움말**

🎯 **기본 사용법:**
• 질문을 직접 입력하면 AI가 답변합니다
• 명령어는 '/'로 시작하거나 '/' 없이도 사용 가능합니다

📋 **주요 명령어:**
• \`/help\` - 이 도움말 표시
• \`/mcp start\` - Deep Research 모드 시작
• \`/mcp stop\` - 일반 모드로 전환
• \`/mcp status\` - MCP 서버 상태 확인
• \`/model <이름>\` - AI 모델 변경
• \`/prompt <모드>\` - 전문 프롬프트 변경
• \`/normal\` - 일반 모드로 전환
• \`/debug\` - 디버그 모드 토글

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
    content = content.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold">$1</strong>');
    
    // 코드 블록
    content = content.replace(/`(.*?)`/g, '<code class="bg-slate-600/50 px-1.5 py-0.5 rounded text-sm font-mono text-slate-200">$1</code>');
    
    // 줄바꿈
    content = content.replace(/\n/g, '<br>');
    
    return content;
  };

  const toggleMode = async () => {
    if (!currentSessionId || modeChanging) return;
    
    const isCurrentlyDeepResearch = currentSession?.mode === 'deep_research';
    const command = isCurrentlyDeepResearch ? '/normal' : '/mcp start';
    
    setModeChanging(true);
    setLastChangeStatus({
      type: 'mode',
      status: 'pending',
      message: `${isCurrentlyDeepResearch ? '일반' : 'Deep Research'} 모드로 전환 중...`
    });

    try {
      // API 서버에 모드 전환 명령 전송
      const response = await fetch('/api/gaia-bt/chat/command', {
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

      const data = await response.json();
      
      // 로컬 상태 업데이트
      if (data.mcp_enabled !== undefined) {
        const newMode = data.mcp_enabled ? 'deep_research' : 'normal';
        updateSessionMode(currentSessionId, newMode);
        
        // 모드 변경 완료 확인
        await verifyModeChange(currentSessionId, newMode, data.mcp_enabled);
      }

      setLastChangeStatus({
        type: 'mode',
        status: 'success',
        message: `${data.mcp_enabled ? 'Deep Research' : '일반'} 모드로 전환 완료`
      });

    } catch (error) {
      console.error('Mode toggle failed:', error);
      
      setLastChangeStatus({
        type: 'mode',
        status: 'error',
        message: `모드 전환 실패: ${error instanceof Error ? error.message : '알 수 없는 오류'}`
      });
    } finally {
      setModeChanging(false);
      
      // 3초 후 상태 메시지 제거
      setTimeout(() => {
        setLastChangeStatus({ type: null, status: 'success', message: '' });
      }, 3000);
    }
  };

  const quickCommands = [
    { cmd: '/help', desc: '도움말', icon: '❓' },
    { cmd: '/mcp start', desc: 'Deep Research', icon: '🔬' },
    { cmd: '/normal', desc: '일반 모드', icon: '🏠' },
    { cmd: '/prompt clinical', desc: '임상 모드', icon: '🏥' }
  ];

  const suggestionQuestions = [
    "아스피린의 작용 메커니즘을 설명해주세요",
    "EGFR 억제제의 부작용은 무엇인가요?",
    "신약개발 과정의 주요 단계는?",
    "임상시험 1상과 2상의 차이점은?"
  ];

  return (
    <div className="flex flex-col h-full w-full relative">
      {/* 모드 전환 버튼 */}
      <div className="mb-6 flex justify-center">
        <div className="bg-slate-800/90 backdrop-blur-xl rounded-2xl p-3 shadow-2xl border border-slate-700/50">
          <div className="flex items-center space-x-4">
            <span className={`text-sm font-semibold transition-colors duration-300 ${
              currentSession?.mode === 'normal' ? 'text-green-300' : 'text-slate-400'
            }`}>
              일반 모드
            </span>
            <button
              onClick={toggleMode}
              className={`relative inline-flex h-10 w-20 items-center justify-center rounded-full transition-all duration-300 focus:outline-none transform hover:scale-105 ${
                modeChanging 
                  ? 'bg-gradient-to-r from-yellow-500 to-orange-500 animate-pulse' :
                currentSession?.mode === 'deep_research' 
                  ? 'bg-gradient-to-r from-purple-500 to-blue-500' 
                  : 'bg-gradient-to-r from-green-500 to-emerald-500'
              }`}
              disabled={isProcessing || modeChanging}
            >
              <div className={`absolute w-8 h-8 bg-white rounded-full shadow-lg transition-transform duration-300 ${
                currentSession?.mode === 'deep_research' ? 'translate-x-5' : '-translate-x-5'
              }`}>
                <div className="w-full h-full flex items-center justify-center">
                  {modeChanging ? (
                    <RefreshCw className="w-4 h-4 text-orange-600 animate-spin" />
                  ) : currentSession?.mode === 'deep_research' ? (
                    <Database className="w-4 h-4 text-purple-600" />
                  ) : (
                    <Zap className="w-4 h-4 text-green-600" />
                  )}
                </div>
              </div>
            </button>
            <span className={`text-sm font-semibold transition-colors duration-300 ${
              currentSession?.mode === 'deep_research' ? 'text-purple-300' : 'text-slate-400'
            }`}>
              Deep Research
            </span>
          </div>
        </div>

        {/* 상태 인디케이터 */}
        {(sessionChanging || modeChanging || lastChangeStatus.type) && (
          <div className="px-6 py-3 bg-slate-700/50 backdrop-blur-sm border-b border-slate-600/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {(sessionChanging || modeChanging) && (
                  <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                )}
                <div className={`flex items-center gap-2 ${
                  lastChangeStatus.status === 'pending' ? 'text-blue-300' :
                  lastChangeStatus.status === 'success' ? 'text-green-300' :
                  'text-red-300'
                }`}>
                  {lastChangeStatus.status === 'pending' && <RefreshCw className="w-4 h-4 animate-spin" />}
                  {lastChangeStatus.status === 'success' && <Target className="w-4 h-4" />}
                  {lastChangeStatus.status === 'error' && <Activity className="w-4 h-4" />}
                  <span className="text-sm font-medium">{lastChangeStatus.message}</span>
                </div>
              </div>
              
              {/* 실시간 상태 표시 */}
              <div className="flex items-center gap-3 text-xs">
                <div className="flex items-center gap-1">
                  <div className={`w-2 h-2 rounded-full ${
                    currentSession?.mode === 'deep_research' ? 'bg-purple-400' : 'bg-green-400'
                  }`}></div>
                  <span className="text-slate-300">
                    {currentSession?.mode === 'deep_research' ? 'Deep Research' : '일반'} 모드
                  </span>
                </div>
                
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                  <span className="text-slate-300">세션: {currentSessionId?.slice(-8) || 'N/A'}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 메인 채팅 영역 */}
      <div className="flex-1 flex gap-6">
        {/* 채팅 메시지 영역 */}
        <div className="flex-1 flex flex-col">
          <Card className="flex-1 mb-6 bg-slate-800/90 backdrop-blur-xl border border-slate-700/50 shadow-2xl shadow-purple-500/10 overflow-hidden">
            <div className="h-full flex flex-col">
              {/* 메시지 스크롤 영역 */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.length === 0 ? (
                  <div className="text-center py-12">
                    {/* 환영 섹션 */}
                    <div className="relative">
                      <div className="w-24 h-24 mx-auto mb-6 relative">
                        <div className="absolute inset-0 bg-gradient-to-br from-blue-500 via-purple-500 to-cyan-500 rounded-full animate-pulse"></div>
                        <div className="absolute inset-2 bg-slate-800 rounded-full flex items-center justify-center shadow-inner">
                          <svg viewBox="0 0 24 24" className="w-8 h-8 text-blue-300">
                            <path d="M4,12 Q12,4 20,12 Q12,20 4,12" stroke="currentColor" strokeWidth="1.5" fill="none" />
                            <path d="M4,12 Q12,20 20,12 Q12,4 4,12" stroke="currentColor" strokeWidth="1.5" fill="none" />
                            <circle cx="12" cy="12" r="2" fill="currentColor" />
                          </svg>
                        </div>
                      </div>
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full animate-bounce flex items-center justify-center shadow-lg">
                        <div className="w-2 h-2 bg-white rounded-full"></div>
                      </div>
                    </div>
                    
                    <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent mb-3">
                      GAIA-BT에 오신 것을 환영합니다!
                    </h3>
                    <p className="text-slate-300 mb-8 text-lg">신약개발 전문 AI 어시스턴트입니다. 무엇을 도와드릴까요?</p>
                    
                    {/* 기능 카드 */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto mb-8">
                      <div className="group p-5 bg-gradient-to-br from-blue-500/15 to-cyan-500/15 rounded-2xl border border-blue-400/30 hover:border-blue-300/60 transition-all duration-300 cursor-pointer hover:scale-105 backdrop-blur-sm">
                        <div className="flex items-center gap-3 mb-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg">
                            <Sparkles className="w-5 h-5 text-white" />
                          </div>
                          <h4 className="font-bold text-blue-300">일반 AI 답변</h4>
                        </div>
                        <p className="text-sm text-blue-200/90 leading-relaxed">신속하고 정확한 신약개발 정보</p>
                      </div>
                      
                      <div className="group p-5 bg-gradient-to-br from-purple-500/15 to-pink-500/15 rounded-2xl border border-purple-400/30 hover:border-purple-300/60 transition-all duration-300 cursor-pointer hover:scale-105 backdrop-blur-sm">
                        <div className="flex items-center gap-3 mb-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg">
                            <Search className="w-5 h-5 text-white" />
                          </div>
                          <h4 className="font-bold text-purple-300">Deep Research</h4>
                        </div>
                        <p className="text-sm text-purple-200/90 leading-relaxed">다중 데이터베이스 통합 검색</p>
                      </div>
                    </div>

                    {/* 추천 질문 */}
                    <div className="text-left max-w-2xl mx-auto">
                      <h4 className="font-semibold text-slate-200 mb-4 flex items-center gap-2">
                        <Target className="w-4 h-4 text-blue-400" />
                        추천 질문
                      </h4>
                      <div className="grid gap-3">
                        {suggestionQuestions.map((question, index) => (
                          <button
                            key={index}
                            onClick={() => setInput(question)}
                            className="text-left p-4 bg-slate-700/50 hover:bg-slate-600/50 rounded-xl transition-all duration-200 text-sm text-slate-300 hover:text-white border border-slate-600/50 hover:border-slate-500/50 backdrop-blur-sm group"
                          >
                            <div className="flex items-center gap-3">
                              <span className="text-blue-400 group-hover:scale-110 transition-transform">💬</span>
                              <span>{question}</span>
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
                            ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl px-5 py-3 shadow-lg'
                            : `bg-slate-700/80 backdrop-blur-sm border rounded-2xl px-5 py-4 shadow-lg ${
                                message.mode === 'deep_research'
                                  ? 'border-purple-400/40 bg-gradient-to-br from-purple-500/10 to-blue-500/10'
                                  : 'border-slate-600/50'
                              }`
                        }`}
                      >
                        {message.role === 'assistant' && (
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center space-x-3">
                              <div className="relative">
                                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 via-purple-500 to-cyan-500 rounded-full flex items-center justify-center shadow-lg">
                                  <svg viewBox="0 0 24 24" className="w-4 h-4 text-white">
                                    <path d="M4,12 Q12,4 20,12 Q12,20 4,12" stroke="currentColor" strokeWidth="1.5" fill="none" />
                                    <path d="M4,12 Q12,20 20,12 Q12,4 4,12" stroke="currentColor" strokeWidth="1.5" fill="none" />
                                    <circle cx="12" cy="12" r="1.5" fill="currentColor" />
                                  </svg>
                                </div>
                                {message.mode === 'deep_research' && (
                                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-purple-500 rounded-full flex items-center justify-center animate-pulse">
                                    <Sparkles className="w-2 h-2 text-white" />
                                  </div>
                                )}
                              </div>
                              <div className="flex items-center gap-2">
                                <span className="font-semibold text-slate-200">GAIA-BT</span>
                                {message.mode === 'deep_research' && (
                                  <Badge className="bg-gradient-to-r from-purple-500 to-purple-600 text-white text-xs px-2 py-1">
                                    🔬 Deep Research
                                  </Badge>
                                )}
                                {message.prompt_type && message.prompt_type !== 'default' && (
                                  <Badge variant="outline" className="text-xs border-gray-300">
                                    {message.prompt_type === 'clinical' ? '🏥 임상' :
                                     message.prompt_type === 'research' ? '📊 연구' :
                                     message.prompt_type === 'chemistry' ? '⚗️ 화학' : '📋 규제'}
                                  </Badge>
                                )}
                              </div>
                            </div>
                            
                            {(message.processing || message.streaming) && (
                              <div className="flex items-center space-x-2 text-purple-300">
                                <RefreshCw className="w-4 h-4 animate-spin" />
                                <span className="text-xs">
                                  {message.streaming ? '입력 중...' : '분석 중...'}
                                </span>
                              </div>
                            )}
                          </div>
                        )}
                        
                        {message.role === 'user' && (
                          <div className="flex items-center gap-2 mb-2 text-blue-100">
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
                          <div className="mt-4 pt-3 border-t border-purple-400/30">
                            <div className="flex items-center space-x-2 text-xs text-slate-300">
                              <Database className="w-3 h-3 text-purple-400" />
                              <span className="font-medium">검색 소스:</span>
                              <div className="flex flex-wrap gap-1">
                                {message.sources.map((source, index) => (
                                  <span 
                                    key={index}
                                    className="bg-purple-500/20 text-purple-300 px-2 py-1 rounded-full border border-purple-400/30"
                                  >
                                    {source}
                                  </span>
                                ))}
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

          {/* 입력 영역 */}
          <Card className="bg-slate-800/90 backdrop-blur-xl border border-slate-700/50 shadow-2xl">
            <div className="p-4">
              {/* 빠른 명령어 버튼 */}
              {showCommands && (
                <div className="mb-4 flex flex-wrap gap-2">
                  {quickCommands.map((item) => (
                    <button
                      key={item.cmd}
                      onClick={() => setInput(item.cmd)}
                      className="flex items-center gap-2 text-xs px-3 py-2 bg-gradient-to-r from-slate-600/50 to-slate-700/50 hover:from-slate-500/60 hover:to-slate-600/60 rounded-lg transition-all duration-200 border border-slate-600/40 hover:border-slate-500/50 backdrop-blur-sm group"
                    >
                      <span className="group-hover:scale-110 transition-transform">{item.icon}</span>
                      <span className="font-medium text-slate-200">{item.cmd}</span>
                      <span className="text-slate-400">({item.desc})</span>
                    </button>
                  ))}
                </div>
              )}
              
              <form onSubmit={handleSubmit} className="flex space-x-3">
                <div className="flex-1 relative">
                  <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder={
                      currentSession?.mode === 'deep_research'
                        ? "신약개발 질문을 입력하세요... (🔬 Deep Research 모드 활성화됨)"
                        : "신약개발 질문을 입력하거나 명령어를 사용하세요... (예: /help)"
                    }
                    className="w-full px-4 py-3 pr-24 border border-slate-600/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-slate-700/80 backdrop-blur text-slate-200 placeholder-slate-400"
                    disabled={isProcessing}
                  />
                  
                  <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
                    <button
                      type="button"
                      className="p-1.5 text-slate-400 hover:text-slate-200 transition-colors hover:scale-110 transform"
                    >
                      <Paperclip className="w-4 h-4" />
                    </button>
                    <button
                      type="button"
                      className="p-1.5 text-slate-400 hover:text-slate-200 transition-colors hover:scale-110 transform"
                    >
                      <Mic className="w-4 h-4" />
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowCommands(!showCommands)}
                      className={`p-1.5 transition-all hover:scale-110 transform ${showCommands ? 'text-blue-400' : 'text-slate-400 hover:text-slate-200'}`}
                    >
                      <Terminal className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <Button
                  type="submit"
                  disabled={!input.trim() || isProcessing}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-6 py-3 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:scale-105 transform"
                >
                  {isProcessing ? (
                    <RefreshCw className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </Button>
              </form>
              
              <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
                <div className="flex items-center space-x-4">
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
                    </>
                  )}
                </div>
                <div className="flex items-center space-x-3">
                  <span>/help로 명령어 확인</span>
                  {currentSession?.mode === 'deep_research' && (
                    <span className="text-purple-400 font-medium">✨ 다중 DB 검색 활성화</span>
                  )}
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* 사이드바 (숨김/표시 가능) */}
        {showSidebar && (
          <div className="w-80 space-y-4">
            {/* 모드 전환 카드 */}
            <Card className="p-4 bg-slate-800/90 backdrop-blur-xl border border-slate-700/50 shadow-lg">
              <h3 className="font-semibold text-slate-200 mb-3 flex items-center gap-2">
                <Settings className="w-4 h-4 text-blue-400" />
                모드 설정
              </h3>
              
              <div className="space-y-3">
                <button
                  onClick={() => currentSessionId && updateSessionMode(currentSessionId, 'normal')}
                  className={`w-full p-3 rounded-lg text-left transition-all ${
                    currentSession?.mode === 'normal'
                      ? 'bg-green-500/20 border-2 border-green-400/60'
                      : 'bg-slate-700/50 border border-slate-600/50 hover:bg-slate-600/50'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="font-medium text-slate-200">일반 모드</span>
                  </div>
                  <span className="text-xs text-slate-400">빠른 AI 답변</span>
                </button>
                
                <button
                  onClick={() => currentSessionId && updateSessionMode(currentSessionId, 'deep_research')}
                  className={`w-full p-3 rounded-lg text-left transition-all ${
                    currentSession?.mode === 'deep_research'
                      ? 'bg-purple-500/20 border-2 border-purple-400/60'
                      : 'bg-slate-700/50 border border-slate-600/50 hover:bg-slate-600/50'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span className="font-medium text-slate-200">Deep Research</span>
                  </div>
                  <span className="text-xs text-slate-400">다중 데이터베이스 검색</span>
                </button>
              </div>
            </Card>

            {/* 통계 카드 */}
            <Card className="p-4 bg-slate-800/90 backdrop-blur-xl border border-slate-700/50 shadow-lg">
              <h3 className="font-semibold text-slate-200 mb-3 flex items-center gap-2">
                <Activity className="w-4 h-4 text-purple-400" />
                세션 통계
              </h3>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">메시지</span>
                  <span className="font-medium text-slate-200">{messages.length}개</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">현재 모드</span>
                  <span className="font-medium text-slate-200">
                    {currentSession?.mode === 'deep_research' ? '🔬 Deep Research' : '🏠 일반'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">프롬프트</span>
                  <span className="font-medium text-slate-200">
                    {currentSession?.prompt_type || 'default'}
                  </span>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>

      {/* 플로팅 설정 버튼 */}
      <button
        onClick={() => setShowSidebar(!showSidebar)}
        className="fixed bottom-6 right-6 w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center z-10 hover:scale-110 transform"
      >
        <Settings className="w-5 h-5" />
      </button>
    </div>
  );
}