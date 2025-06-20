'use client';

import { useState, useRef, useEffect } from 'react';
import { Sparkles, Beaker, Code, FileText, FlaskConical, Brain, Settings, Download, ChevronDown } from 'lucide-react';
import { useChatStore } from '@/store/chatStore';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import MessageArea from './MessageArea';
import InputArea from './InputArea';
import { TypingIndicator } from './TypingIndicator';
import { EmptyState } from './EmptyState';

interface UnifiedChatInterfaceProps {
  className?: string;
  variant?: 'simple' | 'gaia' | 'professional' | 'web';
  mode?: 'normal' | 'deep_research';
  features?: {
    mcp?: boolean;
    markdown?: boolean;
    voiceInput?: boolean;
    fileUpload?: boolean;
    promptSelector?: boolean;
    modeToggle?: boolean;
  };
}


const promptTypeConfig = {
  default: {
    label: '기본',
    icon: Sparkles,
    color: 'blue',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    borderColor: 'border-blue-200 dark:border-blue-800',
    description: '신약개발 전반에 대한 균형잡힌 AI 어시스턴트'
  },
  clinical: {
    label: '임상시험',
    icon: FileText,
    color: 'green',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    borderColor: 'border-green-200 dark:border-green-800',
    description: '임상시험 및 환자 중심 약물 개발'
  },
  research: {
    label: '연구분석',
    icon: FlaskConical,
    color: 'purple',
    bgColor: 'bg-purple-50 dark:bg-purple-950/20',
    borderColor: 'border-purple-200 dark:border-purple-800',
    description: '문헌 분석 및 과학적 증거 종합'
  },
  chemistry: {
    label: '의약화학',
    icon: Beaker,
    color: 'orange',
    bgColor: 'bg-orange-50 dark:bg-orange-950/20',
    borderColor: 'border-orange-200 dark:border-orange-800',
    description: '분자 설계 및 구조 분석'
  },
  regulatory: {
    label: '규제승인',
    icon: Code,
    color: 'red',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    borderColor: 'border-red-200 dark:border-red-800',
    description: '글로벌 의약품 규제 및 승인'
  }
};

export function UnifiedChatInterface({ 
  className,
  variant = 'gaia',
  mode: initialMode = 'normal',
  features = {
    mcp: true,
    markdown: true,
    voiceInput: false,
    fileUpload: false,
    promptSelector: true,
    modeToggle: true
  }
}: UnifiedChatInterfaceProps) {
  const { 
    currentSessionId, 
    sessions, 
    isTyping,
    sendMessage,
    currentSession,
    createSession,
    updateSessionMode,
    updateSessionPromptType
  } = useChatStore();

  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentMode, setCurrentMode] = useState<'normal' | 'deep_research'>(initialMode);
  const [currentPromptType, setCurrentPromptType] = useState('default');
  const [showPromptSelector, setShowPromptSelector] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const session = currentSessionId ? sessions[currentSessionId] : null;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [session?.messages, isTyping]);

  useEffect(() => {
    if (!currentSessionId) {
      createSession();
    }
  }, [currentSessionId, createSession]);

  const handleSendMessage = async (content?: string) => {
    const messageContent = content || input;
    if (!currentSessionId || !messageContent.trim() || isProcessing) return;
    
    setIsProcessing(true);
    setInput('');
    
    try {
      await sendMessage(currentSessionId, messageContent);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleModeToggle = () => {
    const newMode = currentMode === 'normal' ? 'deep_research' : 'normal';
    setCurrentMode(newMode);
    if (currentSessionId) {
      updateSessionMode(currentSessionId, newMode);
    }
  };

  const handlePromptTypeChange = (type: string) => {
    setCurrentPromptType(type);
    setShowPromptSelector(false);
    if (currentSessionId) {
      updateSessionPromptType(currentSessionId, type);
    }
  };

  const renderModeBadge = () => {
    if (!features.modeToggle) return null;
    
    return (
      <Button
        variant="outline"
        size="sm"
        onClick={handleModeToggle}
        className={cn(
          "flex items-center gap-1.5 text-xs font-medium transition-all",
          currentMode === 'deep_research' 
            ? "bg-green-100 text-green-700 border-green-300 hover:bg-green-200" 
            : "bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200"
        )}
      >
        {currentMode === 'deep_research' ? (
          <>
            <Brain className="w-3.5 h-3.5" />
            Deep Research
          </>
        ) : (
          <>
            <Sparkles className="w-3.5 h-3.5" />
            일반 모드
          </>
        )}
      </Button>
    );
  };

  const renderPromptSelector = () => {
    if (!features.promptSelector) return null;

    const currentConfig = promptTypeConfig[currentPromptType as keyof typeof promptTypeConfig];
    const IconComponent = currentConfig.icon;

    return (
      <div className="relative">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowPromptSelector(!showPromptSelector)}
          className="flex items-center gap-1.5 text-xs font-medium"
        >
          <IconComponent className="w-3.5 h-3.5" />
          {currentConfig.label}
          <ChevronDown className="w-3 h-3" />
        </Button>
        
        {showPromptSelector && (
          <div className="absolute top-full left-0 mt-1 w-64 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50">
            {Object.entries(promptTypeConfig).map(([key, config]) => {
              const IconComponent = config.icon;
              return (
                <button
                  key={key}
                  onClick={() => handlePromptTypeChange(key)}
                  className={cn(
                    "w-full text-left px-3 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 first:rounded-t-lg last:rounded-b-lg",
                    key === currentPromptType && "bg-blue-50 dark:bg-blue-950/20"
                  )}
                >
                  <div className="flex items-center gap-2">
                    <IconComponent className="w-4 h-4 text-gray-500" />
                    <div>
                      <div className="font-medium">{config.label}</div>
                      <div className="text-xs text-gray-500">{config.description}</div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  // Simple variant (기본 ChatInterface 스타일)
  if (variant === 'simple') {
    if (!session) {
      return <EmptyState />;
    }

    const mockLayoutConfig = {
      columns: 1,
      cardSize: 'normal',
      gridGap: 'gap-4',
      textSize: 'text-sm',
      containerMaxWidth: 'max-w-4xl',
      padding: 'p-4'
    };

    return (
      <div className={cn("flex flex-col h-full", className)}>
        {/* 메시지 영역 */}
        <div className="flex-1 overflow-hidden">
          {session.messages.length === 0 ? (
            <div className="flex-1 flex items-center justify-center">
              <EmptyState />
            </div>
          ) : (
            <MessageArea 
              messages={session.messages} 
              mainPageLayout={mockLayoutConfig}
              messagesEndRef={messagesEndRef}
            />
          )}
          {isTyping && <TypingIndicator />}
        </div>

        {/* 입력 영역 */}
        <div className="border-t border-gray-200 dark:border-gray-700">
          <InputArea
            input={input}
            setInput={setInput}
            onSendMessage={() => handleSendMessage(input)}
            isProcessing={isProcessing}
            layoutConfig={{
              mode: 'normal',
              density: 'normal',
              fontSize: 'medium'
            }}
          />
        </div>
      </div>
    );
  }

  // Gaia/Professional/Web variants (고급 기능 포함)
  return (
    <div className={cn("flex flex-col h-full bg-white dark:bg-gray-900", className)}>
      {/* 헤더 */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            GAIA-BT 채팅
          </h2>
          {renderModeBadge()}
          {renderPromptSelector()}
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm">
            <Settings className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Download className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* 메시지 영역 */}
      <div className="flex-1 overflow-hidden">
        {!session || session.messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center p-8">
            <EmptyState />
          </div>
        ) : (
          <MessageArea 
            messages={session.messages} 
            mainPageLayout={{
              columns: 1,
              cardSize: 'normal',
              gridGap: 'gap-4',
              textSize: 'text-sm',
              containerMaxWidth: 'max-w-4xl',
              padding: 'p-4'
            }}
            messagesEndRef={messagesEndRef}
          />
        )}
        {isTyping && <TypingIndicator />}
      </div>

      {/* 입력 영역 */}
      <div className="border-t border-gray-200 dark:border-gray-700">
        <InputArea
          input={input}
          setInput={setInput}
          onSendMessage={() => handleSendMessage()}
          isProcessing={isProcessing}
          layoutConfig={{
            mode: 'normal',
            density: 'normal',
            fontSize: 'medium'
          }}
        />
      </div>
    </div>
  );
}