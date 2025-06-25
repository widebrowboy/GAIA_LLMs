'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Send, Plus, Menu, Edit2, Check } from 'lucide-react';
import Image from 'next/image';
import { useChatContext } from '@/contexts/SimpleChatContext';
import { useResponsive } from '@/hooks/useResponsive';
import MessageItem from './MessageItem';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';

interface ChatAreaProps {
  onToggleSidebar?: () => void;
  isSidebarOpen?: boolean;
}

const ChatArea: React.FC<ChatAreaProps> = ({ onToggleSidebar, isSidebarOpen }) => {
  const { 
    currentConversation, 
    sendMessage, 
    isLoading, 
    startNewConversation,
    isModelChanging,
    isModeChanging,
    isPromptChanging,
    isStreaming,
    streamingResponse,
    isConnecting,
    setCurrentConversation
  } = useChatContext();
  const { isMobile } = useResponsive();
  const [message, setMessage] = useState<string>('');
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editedTitle, setEditedTitle] = useState('');
  const titleInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 메시지 변경 시 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentConversation?.messages, streamingResponse]);

  // 제목 편집 모드 진입 시 포커스
  useEffect(() => {
    if (isEditingTitle && titleInputRef.current) {
      titleInputRef.current.focus();
      titleInputRef.current.select();
    }
  }, [isEditingTitle]);

  // 현재 대화의 제목이 변경되면 편집 제목 상태 업데이트
  useEffect(() => {
    if (currentConversation) {
      setEditedTitle(currentConversation.title);
    }
  }, [currentConversation?.title]);

  const handleSendMessage = async () => {
    if (!message.trim() || isLoading || isModelChanging || isModeChanging || isPromptChanging) return;
    
    const messageToSend = message;
    setMessage('');
    
    try {
      await sendMessage(messageToSend);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!currentConversation) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className={`text-center ${isMobile ? 'p-4' : 'p-8'} max-w-md`}>
          <h3 className={`${isMobile ? 'text-xl' : 'text-2xl'} font-bold text-gray-800 mb-4`}>
            환영합니다
          </h3>
          <p className="text-gray-600 mb-6 leading-relaxed">
            신약개발 전문 AI 어시스턴트와 대화를 시작해보세요. 
            {isMobile ? '상단 메뉴에서' : '왼쪽 사이드바에서'} &ldquo;새 대화&rdquo; 버튼을 클릭하여 시작할 수 있습니다.
          </p>
          <div className="bg-white/50 backdrop-blur-sm rounded-lg p-4 border">
            <h4 className="font-semibold text-gray-700 mb-2">주요 기능</h4>
            <ul className="text-sm text-gray-600 space-y-1 text-left">
              <li>• 신약개발 전문 지식 제공</li>
              <li>• 딥리서치 모드 (MCP 통합)</li>
              <li>• 전문 프롬프트 시스템</li>
              <li>• 실시간 시스템 모니터링</li>
            </ul>
          </div>
          
          {/* 모바일 새 대화 버튼 */}
          {isMobile && (
            <button
              onClick={startNewConversation}
              disabled={isLoading || isModelChanging || isModeChanging || isPromptChanging}
              className="mt-6 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-6 py-3 rounded-full flex items-center space-x-2 shadow-lg disabled:shadow-none transition-all duration-200"
            >
              <Plus className="w-5 h-5" />
              <span>
                {isModelChanging || isModeChanging || isPromptChanging ? '설정 변경 중...' : '새 대화 시작'}
              </span>
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* 헤더 */}
      <div className="sticky top-0 z-30 bg-white/90 backdrop-blur-sm border-b border-gray-200 px-4 py-2">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <button
              onClick={onToggleSidebar}
              className="p-2 hover:bg-gray-100 rounded-md transition-colors duration-200 flex items-center justify-center"
              title={isSidebarOpen ? "사이드바 숨기기" : "사이드바 표시"}
              aria-label={isSidebarOpen ? "사이드바 숨기기" : "사이드바 표시"}
            >
              <Menu className="w-5 h-5 text-gray-600" />
            </button>
            
            {/* GAIA-GPT 로고 및 타이틀 - 환영 페이지로 이동 */}
            <div 
              className="flex items-center space-x-2 cursor-pointer hover:bg-gray-100 p-2 rounded-md transition-colors"
              onClick={() => setCurrentConversation && setCurrentConversation(null)}
              title="홈으로 이동"
            >
              <Image src="/gaia-mark.png" alt="GAIA-GPT" width={20} height={20} />
              <span className="font-semibold text-gray-800">GAIA-GPT</span>
            </div>
          </div>

          <div className="flex-1">
            {isEditingTitle && currentConversation ? (
              <div className="flex items-center space-x-2">
                <input
                  ref={titleInputRef}
                  type="text"
                  className="flex-1 text-lg font-semibold text-gray-800 border-b border-blue-500 bg-transparent focus:outline-none"
                  value={editedTitle}
                  onChange={(e) => setEditedTitle(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      const updatedConversation = {
                        ...currentConversation,
                        title: editedTitle.trim() || '새 대화'
                      };
                      if (setCurrentConversation) {
                        setCurrentConversation(updatedConversation);
                      }
                      setIsEditingTitle(false);
                      // 로컬스토리지에 저장
                      if (typeof window !== 'undefined') {
                        const conversations = JSON.parse(localStorage.getItem('gaia-gpt-conversations') || '[]');
                        const updatedConversations = conversations.map((conv: any) => 
                          conv.id === currentConversation.id ? updatedConversation : conv
                        );
                        localStorage.setItem('gaia-gpt-conversations', JSON.stringify(updatedConversations));
                      }
                    } else if (e.key === 'Escape') {
                      setIsEditingTitle(false);
                      setEditedTitle(currentConversation.title);
                    }
                  }}
                />
                <button
                  onClick={() => {
                    const updatedConversation = {
                      ...currentConversation,
                      title: editedTitle.trim() || '새 대화'
                    };
                    if (setCurrentConversation) {
                      setCurrentConversation(updatedConversation);
                    }
                    setIsEditingTitle(false);
                    // 로컬스토리지에 저장
                    if (typeof window !== 'undefined') {
                      const conversations = JSON.parse(localStorage.getItem('gaia-gpt-conversations') || '[]');
                      const updatedConversations = conversations.map((conv: any) => 
                        conv.id === currentConversation.id ? updatedConversation : conv
                      );
                      localStorage.setItem('gaia-gpt-conversations', JSON.stringify(updatedConversations));
                    }
                  }}
                  className="p-1 bg-blue-500 rounded text-white"
                  title="제목 저장"
                >
                  <Check className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <h2 
                className="text-lg font-semibold text-gray-800 truncate flex items-center"
                onClick={() => {
                  if (currentConversation) {
                    setIsEditingTitle(true);
                    setEditedTitle(currentConversation.title);
                  }
                }}
              >
                {currentConversation ? (
                  <>
                    <span className="cursor-pointer">{currentConversation.title}</span>
                    <Edit2 className="w-4 h-4 ml-2 text-gray-500 cursor-pointer" />
                  </>
                ) : '새 대화'}
              </h2>
            )}
          </div>

          <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
            {currentConversation.messages.length}개 메시지
          </div>
        </div>
      </div>

      {/* 메시지 목록 */}
      <div className={`flex-1 overflow-y-auto ${isMobile ? 'p-4' : 'p-6'}`}>
        <div className={`${isMobile ? 'max-w-full' : 'max-w-4xl'} mx-auto space-y-6`}>
          {currentConversation.messages.map((msg) => (
            <MessageItem key={msg.id} message={msg} />
          ))}
          
          {/* 실시간 스트리밍 응답 표시 */}
          {(isStreaming || isConnecting) && streamingResponse && (
            <div className="flex items-start space-x-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white text-sm font-bold shadow-lg">
                🧬
              </div>
              
              <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm flex-1">
                <div className="prose prose-sm max-w-none overflow-wrap-anywhere break-words">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    rehypePlugins={[rehypeHighlight]}
                  >
                    {streamingResponse}
                  </ReactMarkdown>
                  <span className="inline-block w-2 h-4 bg-blue-500 animate-pulse ml-1"></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>
      
      {/* 메시지 입력 */}
      <div className={`border-t border-gray-200 ${isMobile ? 'py-3 px-4' : 'py-4 px-6'} bg-white/90 backdrop-blur-sm sticky bottom-0 z-20 pb-[env(safe-area-inset-bottom)]`}>
        <div className={`${isMobile ? 'max-w-full' : 'max-w-4xl'} mx-auto`}>
          <div className="flex items-end space-x-3">
            <div className="flex-1">
              <textarea
                className="w-full resize-none border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm transition-all duration-200 bg-white disabled:bg-gray-100 disabled:cursor-not-allowed"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  isModelChanging ? "모델 변경 중..." :
                  isModeChanging ? "모드 변경 중..." :
                  isPromptChanging ? "프롬프트 변경 중..." :
                  isLoading ? "응답 처리 중..." :
                  "신약개발에 대해 질문해보세요..."
                }
                rows={1}
                disabled={isLoading || isModelChanging || isModeChanging || isPromptChanging}
                style={{
                  minHeight: '48px',
                  maxHeight: '120px',
                }}
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!message.trim() || isLoading || isModelChanging || isModeChanging || isPromptChanging}
              className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-300 disabled:to-gray-400 text-white p-3 rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 shadow-lg disabled:shadow-none disabled:cursor-not-allowed"
              title={
                isModelChanging ? "모델 변경 중..." :
                isModeChanging ? "모드 변경 중..." :
                isPromptChanging ? "프롬프트 변경 중..." :
                isLoading ? "응답 처리 중..." :
                "메시지 전송"
              }
            >
              {isLoading || isModelChanging || isModeChanging || isPromptChanging ? (
                <div className="w-5 h-5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          
          {/* 도움말 텍스트 */}
          <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
            <span>Enter로 전송, Shift+Enter로 줄바꿈</span>
            <span className={message.length > 1000 ? 'text-orange-500' : ''}>
              {message.length}/2000
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatArea;