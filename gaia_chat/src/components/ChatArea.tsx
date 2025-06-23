'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Send, Plus, Menu, Edit3, Check, X } from 'lucide-react';
import { useChatContext } from '@/contexts/ChatContext';
import { useResponsive } from '@/hooks/useResponsive';
import MessageItem from './MessageItem';
import Image from 'next/image';

interface ChatAreaProps {
  onToggleSidebar?: () => void;
  isSidebarOpen?: boolean;
}

const ChatArea: React.FC<ChatAreaProps> = ({ onToggleSidebar, isSidebarOpen }) => {
  const { 
    currentConversation, 
    sendMessage, 
    isLoading, 
    currentMode, 
    createConversation, 
    conversations, 
    setConversations, 
    setCurrentConversation,
    isModelChanging,
    isModeChanging,
    isPromptChanging
  } = useChatContext();
  const { isMobile, isDesktop } = useResponsive();
  const [message, setMessage] = useState<string>('');
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const [isEditingTitle, setIsEditingTitle] = useState<boolean>(false);
  const [editTitle, setEditTitle] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 메시지 변경 시 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentConversation?.messages]);

  const handleSendMessage = async () => {
    // 메시지가 비어있거나, 대화가 없거나, 어떤 작업이 진행 중이면 return
    if (!message.trim() || !currentConversation || isLoading || isModelChanging || isModeChanging || isPromptChanging) return;
    
    const messageToSend = message;
    setMessage('');
    setIsTyping(true);
    
    try {
      await sendMessage(messageToSend);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // 제목 편집 시작
  const startEditingTitle = () => {
    if (currentConversation) {
      setEditTitle(currentConversation.title);
      setIsEditingTitle(true);
    }
  };

  // 제목 저장
  const saveTitle = () => {
    if (currentConversation && editTitle.trim()) {
      const updatedConversation = {
        ...currentConversation,
        title: editTitle.trim()
      };

      const updatedConversations = conversations.map(conv =>
        conv.id === currentConversation.id ? updatedConversation : conv
      );

      setCurrentConversation(updatedConversation);
      setConversations(updatedConversations);

      // 로컬 스토리지에 저장
      if (typeof window !== 'undefined') {
        localStorage.setItem('gaia_gpt_conversations', JSON.stringify(updatedConversations));
      }
    }
    setIsEditingTitle(false);
  };

  // 제목 편집 취소
  const cancelEditingTitle = () => {
    setIsEditingTitle(false);
    setEditTitle('');
  };

  // 제목 편집 키 처리
  const handleTitleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      saveTitle();
    } else if (e.key === 'Escape') {
      cancelEditingTitle();
    }
  };

  if (!currentConversation) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">        
        <div className={`text-center ${isMobile ? 'p-4' : 'p-8'} max-w-md`}>
          <div className={`${isMobile ? 'mb-4' : 'mb-6'} flex justify-center`}>
            <Image 
              src="/gaia-logo.png" 
              alt="GAIA-GPT Logo" 
              width={isMobile ? 64 : 96} 
              height={isMobile ? 64 : 96} 
              className="opacity-80"
            />
          </div>
          <h3 className={`${isMobile ? 'text-xl' : 'text-2xl'} font-bold text-gray-800 mb-4`}>
            GAIA-GPT에 오신 것을 환영합니다
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
              onClick={createConversation}
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
    <div className="flex-1 flex flex-col bg-gradient-to-b from-gray-50 to-white">
      {/* 채팅 헤더 - 데스크톱에서만 표시 */}
      {!isMobile && (
        <div className="border-b border-gray-200 p-4 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {/* 사이드바 토글 버튼 (데스크톱) */}
            {onToggleSidebar && (
              <button
                onClick={onToggleSidebar}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                title={isSidebarOpen ? "사이드바 숨기기" : "사이드바 보이기"}
              >
                <Menu className="w-5 h-5 text-gray-600" />
              </button>
            )}
            {isEditingTitle ? (
              <div className="flex items-center space-x-2 flex-1">
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  onKeyPress={handleTitleKeyPress}
                  className="flex-1 text-lg font-semibold text-gray-800 bg-white border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  autoFocus
                />
                <button
                  onClick={saveTitle}
                  className="p-1 text-green-600 hover:text-green-800 transition-colors"
                  title="제목 저장"
                >
                  <Check className="w-4 h-4" />
                </button>
                <button
                  onClick={cancelEditingTitle}
                  className="p-1 text-red-600 hover:text-red-800 transition-colors"
                  title="편집 취소"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2 flex-1">
                <h3 className="text-lg font-semibold text-gray-800 truncate">
                  {currentConversation.title}
                </h3>
                <button
                  onClick={startEditingTitle}
                  className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                  title="제목 편집"
                >
                  <Edit3 className="w-4 h-4" />
                </button>
              </div>
            )}
            <div className={`px-2 py-1 rounded-full text-xs font-medium ${
              currentMode === 'deep_research' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              {currentMode === 'deep_research' ? '딥리서치' : '기본'}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
              {currentConversation.messages.length}개 메시지
            </div>
          </div>
        </div>
        </div>
      )}
      
      {/* 메시지 목록 */}
      <div className={`flex-1 overflow-y-auto ${isMobile ? 'p-4' : 'p-6'}`}>
        <div className={`${isMobile ? 'max-w-full' : 'max-w-4xl'} mx-auto space-y-6`}>
          {currentConversation.messages.map((msg) => (
            <MessageItem key={msg.id} message={msg} />
          ))}
          
          {isTyping && (
            <div className="flex items-start space-x-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white text-sm font-bold shadow-lg">
                🧬
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>
      
      {/* 메시지 입력 */}
      <div className={`border-t border-gray-200 ${isMobile ? 'p-3' : 'p-4'} bg-white/90 backdrop-blur-sm sticky bottom-0`}>
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