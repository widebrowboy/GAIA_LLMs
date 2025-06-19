'use client';

import { useState, useRef, useEffect } from 'react';
import { useChatStore } from '@/store/chatStore';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { TypingIndicator } from './TypingIndicator';
import { EmptyState } from './EmptyState';

export function ChatInterface() {
  const { 
    currentSessionId, 
    sessions, 
    isTyping,
    sendMessage 
  } = useChatStore();

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const currentSession = currentSessionId ? sessions[currentSessionId] : null;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentSession?.messages, isTyping]);

  const handleSendMessage = async (content: string) => {
    if (!currentSessionId || !content.trim()) return;
    
    try {
      await sendMessage(currentSessionId, content);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  if (!currentSession) {
    return <EmptyState />;
  }

  return (
    <div className="flex flex-col h-full">
      {/* 메시지 영역 */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto custom-scrollbar p-4">
          {currentSession.messages.length === 0 ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 mx-auto bg-gradient-to-br from-research-500 to-biotech-500 rounded-full flex items-center justify-center">
                  <span className="text-2xl text-white">🧬</span>
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-foreground mb-2">
                    GAIA-BT 신약개발 AI 어시스턴트
                  </h2>
                  <p className="text-muted-foreground">
                    신약개발 관련 질문을 입력해보세요.
                    {currentSession.mode === 'mcp' || currentSession.mode === 'deep_research' 
                      ? ' Deep Research 모드가 활성화되어 있습니다.' 
                      : ' Deep Research 모드를 활성화하면 더 상세한 분석을 받을 수 있습니다.'}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <MessageList messages={currentSession.messages} />
          )}
          
          {/* 타이핑 인디케이터 */}
          {isTyping && <TypingIndicator />}
          
          {/* 스크롤 하단 참조점 */}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* 입력 영역 */}
      <div className="border-t border-border bg-background/80 backdrop-blur-sm">
        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={isTyping}
          mode={currentSession.mode}
          promptType={currentSession.prompt_type}
        />
      </div>
    </div>
  );
}