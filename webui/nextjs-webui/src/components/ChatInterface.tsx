'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Settings, Zap, Beaker, FileText, Shield, Stethoscope } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  mode?: string;
  promptMode?: string;
  mock?: boolean;
}

interface ChatSettings {
  mode: 'normal' | 'deep_research';
  promptMode: 'default' | 'clinical' | 'research' | 'chemistry' | 'regulatory';
  model: string;
}

const PROMPT_MODES = {
  default: { icon: Bot, label: '🧬 Default Drug Development', description: '신약개발 전반에 대한 균형잡힌 AI 어시스턴트' },
  clinical: { icon: Stethoscope, label: '🏥 Clinical Trial Expert', description: '임상시험 및 환자 중심 약물 개발 전문가' },
  research: { icon: FileText, label: '🔬 Research Analysis Expert', description: '문헌 분석 및 과학적 증거 종합 전문가' },
  chemistry: { icon: Beaker, label: '⚗️ Medicinal Chemistry Expert', description: '의약화학 및 분자 설계 전문가' },
  regulatory: { icon: Shield, label: '📋 Regulatory Expert', description: '글로벌 의약품 규제 및 승인 전문가' }
};

const MODELS = [
  'gemma3:27b-it-q4_K_M',
  'txgemma-chat:latest',
  'txgemma-predict:latest'
];

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState<ChatSettings>({
    mode: 'normal',
    promptMode: 'default',
    model: 'gemma3:27b-it-q4_K_M'
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('/api/gaia-bt', {
        type: 'chat',
        message: input.trim(),
        mode: settings.mode,
        prompt_mode: settings.promptMode,
        model: settings.model
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.data.response,
        timestamp: new Date(response.data.timestamp),
        mode: response.data.mode,
        promptMode: response.data.prompt_mode,
        mock: response.data.mock
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: '⚠️ 메시지 전송 중 오류가 발생했습니다. 나중에 다시 시도해주세요.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getModeIcon = (mode: string) => {
    return mode === 'deep_research' ? '🔬' : '💬';
  };

  const getModeLabel = (mode: string) => {
    return mode === 'deep_research' ? 'Deep Research Mode' : 'Normal Mode';
  };

  const getCurrentPromptMode = () => {
    return PROMPT_MODES[settings.promptMode as keyof typeof PROMPT_MODES];
  };

  return (
    <div className=\"flex flex-col h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50\">
      {/* Header */}
      <div className=\"bg-white border-b border-gray-200 p-4 shadow-sm\">
        <div className=\"flex items-center justify-between\">
          <div className=\"flex items-center space-x-3\">
            <div className=\"w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center\">
              <Bot className=\"w-6 h-6 text-white\" />
            </div>
            <div>
              <h1 className=\"text-xl font-bold text-gray-900\">🧬 GAIA-BT v2.0 Alpha</h1>
              <p className=\"text-sm text-gray-600\">신약개발 연구 어시스턴트</p>
            </div>
          </div>
          
          <div className=\"flex items-center space-x-4\">
            <div className=\"text-right\">
              <div className=\"text-sm font-medium text-gray-700\">
                {getModeIcon(settings.mode)} {getModeLabel(settings.mode)}
              </div>
              <div className=\"text-xs text-gray-500\">
                📋 {getCurrentPromptMode().label}
              </div>
            </div>
            
            <button
              onClick={() => setShowSettings(!showSettings)}
              className=\"p-2 hover:bg-gray-100 rounded-lg transition-colors\"
            >
              <Settings className=\"w-5 h-5 text-gray-600\" />
            </button>
          </div>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className=\"mt-4 p-4 bg-gray-50 rounded-lg border\">
            <div className=\"grid grid-cols-1 md:grid-cols-3 gap-4\">
              {/* Mode Selection */}
              <div>
                <label className=\"block text-sm font-medium text-gray-700 mb-2\">
                  Operation Mode
                </label>
                <select
                  value={settings.mode}
                  onChange={(e) => setSettings(prev => ({ ...prev, mode: e.target.value as 'normal' | 'deep_research' }))}
                  className=\"w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent\"
                >
                  <option value=\"normal\">💬 Normal Mode</option>
                  <option value=\"deep_research\">🔬 Deep Research Mode</option>
                </select>
              </div>

              {/* Prompt Mode Selection */}
              <div>
                <label className=\"block text-sm font-medium text-gray-700 mb-2\">
                  Prompt Specialization
                </label>
                <select
                  value={settings.promptMode}
                  onChange={(e) => setSettings(prev => ({ ...prev, promptMode: e.target.value as any }))}
                  className=\"w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent\"
                >
                  {Object.entries(PROMPT_MODES).map(([key, mode]) => (
                    <option key={key} value={key}>
                      {mode.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Model Selection */}
              <div>
                <label className=\"block text-sm font-medium text-gray-700 mb-2\">
                  Model
                </label>
                <select
                  value={settings.model}
                  onChange={(e) => setSettings(prev => ({ ...prev, model: e.target.value }))}
                  className=\"w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent\"
                >
                  {MODELS.map(model => (
                    <option key={model} value={model}>
                      🤖 {model}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className=\"mt-3 text-xs text-gray-600\">
              💡 <strong>Normal Mode</strong>: 빠른 신약개발 상담 | 
              <strong> Deep Research Mode</strong>: MCP 통합 심층 분석
            </div>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className=\"flex-1 overflow-y-auto p-4\">
        <div className=\"max-w-4xl mx-auto space-y-6\">
          {messages.length === 0 && (
            <div className=\"text-center py-12\">
              <div className=\"w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4\">
                <Bot className=\"w-8 h-8 text-white\" />
              </div>
              <h3 className=\"text-lg font-semibold text-gray-900 mb-2\">
                🧬 GAIA-BT와 대화를 시작하세요
              </h3>
              <p className=\"text-gray-600 mb-6\">
                신약개발에 관한 질문을 하거나 전문 기능을 활용해보세요.
              </p>
              
              <div className=\"grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto\">
                <div className=\"p-4 bg-white rounded-lg border border-gray-200 shadow-sm\">
                  <h4 className=\"font-medium text-gray-900 mb-2\">💬 Normal Mode</h4>
                  <p className=\"text-sm text-gray-600\">\"아스피린의 작용 메커니즘을 설명해주세요\"</p>
                </div>
                <div className=\"p-4 bg-white rounded-lg border border-gray-200 shadow-sm\">
                  <h4 className=\"font-medium text-gray-900 mb-2\">🔬 Deep Research Mode</h4>
                  <p className=\"text-sm text-gray-600\">\"BRCA1 타겟 유방암 치료제 개발 전략\"</p>
                </div>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl ${
                  message.type === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-white border border-gray-200'
                } rounded-lg p-4 shadow-sm`}
              >
                <div className=\"flex items-start space-x-3\">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.type === 'user'
                        ? 'bg-blue-600'
                        : 'bg-gradient-to-r from-blue-500 to-purple-600'
                    }`}
                  >
                    {message.type === 'user' ? (
                      <User className=\"w-4 h-4 text-white\" />
                    ) : (
                      <Bot className=\"w-4 h-4 text-white\" />
                    )}
                  </div>
                  
                  <div className=\"flex-1 min-w-0\">
                    {message.type === 'assistant' && (
                      <div className=\"flex items-center space-x-2 mb-2\">
                        <span className=\"text-xs font-medium text-gray-500\">
                          {message.mode && getModeIcon(message.mode)} GAIA-BT
                        </span>
                        {message.mock && (
                          <span className=\"px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full\">
                            Mock Mode
                          </span>
                        )}
                      </div>
                    )}
                    
                    <div
                      className={`prose prose-sm max-w-none ${
                        message.type === 'user' ? 'text-white prose-invert' : 'text-gray-900'
                      }`}
                    >
                      {message.type === 'user' ? (
                        <p className=\"whitespace-pre-wrap\">{message.content}</p>
                      ) : (
                        <ReactMarkdown
                          components={{
                            pre: ({ children }) => (
                              <pre className=\"bg-gray-100 p-3 rounded overflow-x-auto\">
                                {children}
                              </pre>
                            ),
                            code: ({ children }) => (
                              <code className=\"bg-gray-100 px-1 py-0.5 rounded text-sm\">
                                {children}
                              </code>
                            ),
                          }}
                        >
                          {message.content}
                        </ReactMarkdown>
                      )}
                    </div>
                    
                    <div className=\"flex items-center justify-between mt-2\">
                      <span
                        className={`text-xs ${
                          message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                        }`}
                      >
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className=\"flex justify-start\">
              <div className=\"bg-white border border-gray-200 rounded-lg p-4 shadow-sm\">
                <div className=\"flex items-center space-x-3\">
                  <div className=\"w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center\">
                    <Bot className=\"w-4 h-4 text-white\" />
                  </div>
                  <div className=\"flex space-x-1\">
                    <div className=\"w-2 h-2 bg-gray-400 rounded-full animate-bounce\"></div>
                    <div className=\"w-2 h-2 bg-gray-400 rounded-full animate-bounce\" style={{ animationDelay: '0.1s' }}></div>
                    <div className=\"w-2 h-2 bg-gray-400 rounded-full animate-bounce\" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className=\"border-t border-gray-200 bg-white p-4\">
        <div className=\"max-w-4xl mx-auto\">
          <div className=\"flex space-x-4\">
            <div className=\"flex-1\">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={`${getModeIcon(settings.mode)} ${getModeLabel(settings.mode)}에서 신약개발에 관해 질문하세요...`}
                className=\"w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none\"
                rows={3}
                disabled={isLoading}
              />
              <div className=\"mt-2 text-xs text-gray-500\">
                💡 Shift + Enter로 줄바꿈, Enter로 전송
              </div>
            </div>
            
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                !input.trim() || isLoading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-500 hover:bg-blue-600 text-white'
              }`}
            >
              {isLoading ? (
                <div className=\"w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin\" />
              ) : (
                <Send className=\"w-5 h-5\" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}