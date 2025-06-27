'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Send, Plus, Menu, Edit2, Check } from 'lucide-react';
import Image from 'next/image';
import { useChatContext } from '@/contexts/SimpleChatContext';
import { useResponsive } from '@/hooks/useResponsive';
import MessageItem from './MessageItem';

interface ChatAreaProps {
  onToggleSidebar?: () => void;
  isSidebarOpen?: boolean;
}

const ChatArea: React.FC<ChatAreaProps> = ({ onToggleSidebar, isSidebarOpen }) => {
  const ctx = useChatContext();
  if (!ctx) throw new Error('useChatContext() 반환값이 undefined입니다. ChatProvider로 감싸져 있는지 확인하세요.');
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
    error,
    setCurrentConversation,
    setConversations
  } = ctx;

  useEffect(() => {
    if (!setCurrentConversation || !setConversations) {
      console.warn('컨텍스트 함수가 undefined입니다. ChatProvider 구조를 점검하세요.');
    }
  }, [setCurrentConversation, setConversations]);
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

  // 제목 직접 수정 핸들러
  const handleEditTitle = () => {
  console.log('handleEditTitle 호출');
  setIsEditingTitle(true);
};
  const handleTitleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  console.log('handleTitleInputChange 호출', e.target.value);
  setEditedTitle(e.target.value);
};
  const handleSaveTitle = () => {
  console.log('handleSaveTitle 호출');
  if (!currentConversation) throw new Error('currentConversation이 없습니다.');
  if (!setCurrentConversation || !setConversations) throw new Error('컨텍스트 함수가 undefined입니다.');
  const trimmed = editedTitle.trim();
  const updatedConversation = {
    ...currentConversation,
    title: trimmed || '새 대화',
  };
  // 상태 동기화
  setCurrentConversation(updatedConversation);
  // 대화 목록 동기화
  if (typeof window !== 'undefined') {
    const conversations = JSON.parse(localStorage.getItem('gaia_gpt_conversations') || '[]');
    const updatedConversations = conversations.map((conv: any) =>
      conv.id === updatedConversation.id ? { ...conv, title: updatedConversation.title } : conv
    );
    localStorage.setItem('gaia_gpt_conversations', JSON.stringify(updatedConversations));
    setConversations(updatedConversations);
  }
  setIsEditingTitle(false);
};

  const handleTitleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
  console.log('handleTitleInputKeyDown 호출', e.key);
  if (e.key === 'Enter') handleSaveTitle();
  if (e.key === 'Escape') setIsEditingTitle(false);
};

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
      <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-emerald-50 via-blue-50 to-purple-100 relative overflow-hidden">
        {/* 사이드바 토글 버튼 (상단 우측 고정) */}
        <button
          onClick={onToggleSidebar}
          className="absolute top-6 right-6 z-20 p-3 rounded-2xl bg-gradient-to-br from-white/95 to-emerald-50/95 hover:from-emerald-50 hover:to-blue-50 shadow-xl hover:shadow-2xl transition-all duration-300 border border-emerald-200/50 backdrop-blur-md group"
          aria-label="사이드바 열기/닫기"
        >
          <Menu className="w-5 h-5 text-emerald-700 group-hover:text-blue-700 transition-colors duration-300" />
        </button>
        <div className="text-center p-6 max-w-md mx-auto bg-gradient-to-br from-white/95 to-blue-50/95 rounded-3xl shadow-2xl backdrop-blur-md border border-emerald-200/50 relative overflow-hidden">
            {/* 배경 데코레이션 */}
            <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-bl from-emerald-200/30 to-transparent rounded-full -translate-y-10 translate-x-10"></div>
            <div className="absolute bottom-0 left-0 w-16 h-16 bg-gradient-to-tr from-blue-200/30 to-transparent rounded-full translate-y-8 -translate-x-8"></div>
            
            {/* 메인 콘텐트 */}
            <div className="relative z-10">
              <div className="mb-4">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-emerald-500 to-blue-600 rounded-2xl mb-3 shadow-lg">
                  <span className="text-2xl">🧬</span>
                </div>
                <h3 className={`${isMobile ? 'text-xl' : 'text-2xl'} font-bold bg-gradient-to-r from-emerald-700 to-blue-700 bg-clip-text text-transparent mb-2`}>
                  GAIA-BT 에 오신 것을 환영합니다
                </h3>
                <p className="text-gray-600 mb-5 text-sm leading-relaxed font-medium">
                  혁신적인 신약개발 AI 연구 어시스턴트와 함께 생명과학의 새로운 차원을 경험하세요.
                </p>
              </div>
              
              <div className="grid grid-cols-2 gap-3 mb-5">
                <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 p-3 rounded-xl border border-emerald-200/50">
                  <div className="text-lg mb-1">🔬</div>
                  <div className="text-xs font-semibold text-emerald-800">신약개발</div>
                  <div className="text-xs text-emerald-600">전문 지식</div>
                </div>
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-3 rounded-xl border border-blue-200/50">
                  <div className="text-lg mb-1">🧠</div>
                  <div className="text-xs font-semibold text-blue-800">딥리서치</div>
                  <div className="text-xs text-blue-600">MCP 통합</div>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-3 rounded-xl border border-purple-200/50">
                  <div className="text-lg mb-1">⚖️</div>
                  <div className="text-xs font-semibold text-purple-800">전문 프롬프트</div>
                  <div className="text-xs text-purple-600">맞춤형 분석</div>
                </div>
                <div className="bg-gradient-to-br from-cyan-50 to-cyan-100 p-3 rounded-xl border border-cyan-200/50">
                  <div className="text-lg mb-1">📊</div>
                  <div className="text-xs font-semibold text-cyan-800">실시간</div>
                  <div className="text-xs text-cyan-600">모니터링</div>
                </div>
              </div>
            </div>
            
            {/* 모바일 새 대화 버튼 */}
            {isMobile && (
              <button
                onClick={startNewConversation}
                disabled={isLoading || isModelChanging || isModeChanging || isPromptChanging}
                className="w-full bg-gradient-to-r from-emerald-500 to-blue-600 hover:from-emerald-600 hover:to-blue-700 disabled:from-gray-300 disabled:to-gray-400 text-white px-6 py-3 rounded-2xl flex items-center justify-center space-x-3 shadow-xl disabled:shadow-none transition-all duration-300 text-sm font-semibold"
              >
                <span className="text-lg">✨</span>
                <span>
                  {isModelChanging || isModeChanging || isPromptChanging ? '설정 변경 중...' : '연구 시작하기'}
                </span>
              </button>
            )}
            
            {/* 데스크톱 안내 */}
            {!isMobile && (
              <div className="bg-gradient-to-r from-emerald-50 to-blue-50 p-3 rounded-xl border border-emerald-200/50">
                <p className="text-xs text-emerald-700 font-medium flex items-center justify-center space-x-2">
                  <span>🐈</span>
                  <span>왼쪽 사이드바에서 “새 대화” 버튼을 클릭하여 연구를 시작하세요</span>
                </p>
              </div>
            )}
          </div>
          
          {/* 배경 애니메이션 요소 */}
          <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-emerald-300/30 rounded-full animate-pulse"></div>
          <div className="absolute bottom-1/3 right-1/3 w-1 h-1 bg-blue-300/30 rounded-full animate-ping"></div>
          <div className="absolute top-2/3 right-1/4 w-1.5 h-1.5 bg-purple-300/30 rounded-full animate-bounce"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col flex-1 h-full overflow-hidden">
      {/* 헤더 */}
      <div className="sticky top-0 z-30 bg-gradient-to-r from-emerald-50/95 via-white/95 to-blue-50/95 backdrop-blur-md border-b border-emerald-200/50 px-4 py-3 shadow-sm">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <button
              onClick={onToggleSidebar}
              className="p-2 hover:bg-emerald-100/50 rounded-xl transition-all duration-200 flex items-center justify-center group"
              title={isSidebarOpen ? "사이드바 숨기기" : "사이드바 표시"}
              aria-label={isSidebarOpen ? "사이드바 숨기기" : "사이드바 표시"}
            >
              <Menu className="w-5 h-5 text-emerald-700 group-hover:text-emerald-800 transition-colors" />
            </button>
            
            {/* GAIA-BT 로고 및 타이틀 - 환영 페이지로 이동 */}
            <div 
              className="flex items-center space-x-2 cursor-pointer hover:bg-emerald-100/50 p-2 rounded-xl transition-all duration-200 group"
              onClick={() => setCurrentConversation && setCurrentConversation(null)}
              title="홈으로 이동"
            >
              <span className="text-xl group-hover:scale-110 transition-transform">🧬</span>
              <span className="font-bold bg-gradient-to-r from-emerald-700 to-blue-700 bg-clip-text text-transparent group-hover:from-emerald-600 group-hover:to-blue-600 transition-all">GAIA-BT</span>
            </div>
          </div>

          <div className="flex-1">
            {currentConversation && (
              <div className="w-full flex flex-row items-center gap-2 min-w-0 bg-gradient-to-r from-white/90 to-emerald-50/30 backdrop-blur-md px-4 py-3 rounded-2xl border border-emerald-200/30 mx-2">
  {isEditingTitle ? (
    <input
      ref={titleInputRef}
      value={editedTitle}
      onChange={handleTitleInputChange}
      onBlur={handleSaveTitle}
      onKeyDown={handleTitleInputKeyDown}
      className="flex-1 min-w-0 font-bold text-lg md:text-xl bg-gradient-to-r from-white to-emerald-50/50 border-2 border-emerald-300/50 px-3 py-2 rounded-xl transition-all duration-200 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200 w-full max-w-xl"
      maxLength={50}
      aria-label="대화 제목 입력"
      autoFocus
    />
  ) : (
    <span className="flex-1 min-w-0 font-bold text-lg md:text-xl bg-gradient-to-r from-emerald-700 to-blue-700 bg-clip-text text-transparent truncate max-w-xl" title={currentConversation.title}>
      {currentConversation.title}
    </span>
  )}
  {isEditingTitle ? (
    <button
      onClick={handleSaveTitle}
      className="flex-shrink-0 ml-2 p-2 rounded-xl hover:bg-emerald-100 text-emerald-600 transition-all duration-200 group"
      aria-label="제목 저장"
      title="제목 저장"
    >
      <Check className="w-4 h-4 group-hover:scale-110 transition-transform" />
    </button>
  ) : (
    <button
      onClick={handleEditTitle}
      className="flex-shrink-0 p-2 rounded-xl hover:bg-blue-100 text-blue-600 transition-all duration-200 group"
      aria-label="제목 수정"
      title="제목 수정"
    >
      <Edit2 className="w-4 h-4 group-hover:scale-110 transition-transform" />
    </button>
  )}
</div>
            )}
          </div>
        </div>
      </div>
      {/* 메시지 목록 */}
      <div className={`flex-1 overflow-y-auto ${isMobile ? 'p-4' : 'p-6'}`}>
        <div className="flex flex-col gap-4 w-full max-w-3xl mx-auto">
          {currentConversation && currentConversation.messages && currentConversation.messages.length > 0 ? (
            currentConversation.messages.map((msg, idx) => (
              <MessageItem key={msg.id || idx} message={msg} />
            ))
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-gray-400 select-none py-24">
              <span className="text-4xl mb-4">💬</span>
              <span className="text-lg">아직 메시지가 없습니다.</span>
            </div>
          )}

          {/* 에러 메시지 표시 */}
          {error && (
            <div className="flex items-start space-x-4 mb-6">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-red-400 via-pink-500 to-red-600 flex items-center justify-center text-2xl shadow-xl border-2 border-red-300/50">
                ⚠️
              </div>
              
              <div className="bg-gradient-to-br from-red-50/90 via-pink-50/90 to-red-100/90 border-2 border-red-200/70 rounded-3xl px-6 py-4 shadow-xl flex-1 backdrop-blur-sm">
                <div className="flex items-center space-x-2 mb-3">
                  <span className="text-sm">❌</span>
                  <span className="text-xs font-bold text-red-700">오류 발생</span>
                </div>
                <div className="text-red-800 text-sm">
                  {error}
                </div>
                <button
                  onClick={() => ctx.setError && ctx.setError(null)}
                  className="mt-3 px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg text-xs transition-colors"
                >
                  닫기
                </button>
              </div>
            </div>
          )}

          {(isStreaming || isConnecting) && streamingResponse && (
            <div className="flex items-start space-x-4 mb-6">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-400 via-cyan-500 to-blue-600 flex items-center justify-center text-2xl shadow-xl border-2 border-blue-300/50 animate-pulse">
                🧬
              </div>
              
              <div className="bg-gradient-to-br from-blue-50/90 via-cyan-50/90 to-blue-100/90 border-2 border-blue-200/70 rounded-3xl px-6 py-4 shadow-xl flex-1 backdrop-blur-sm">
                <div className="flex items-center space-x-2 mb-3">
                  <span className="text-sm">🧠</span>
                  <span className="text-xs font-bold text-blue-700">GAIA-BT 연구지원</span>
                  <div className="flex space-x-1">
                    <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
                    <div className="w-1.5 h-1.5 bg-cyan-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
                <div className="whitespace-pre-wrap break-words leading-relaxed text-gray-900">
                  {streamingResponse}
                  <span className="inline-block w-3 h-5 bg-gradient-to-r from-emerald-500 to-blue-500 animate-pulse ml-1 rounded"></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>
      
      {/* 메시지 입력 */}
      <div className={`border-t border-emerald-200/50 ${isMobile ? 'py-4 px-4' : 'py-5 px-6'} bg-gradient-to-r from-emerald-50/95 via-white/95 to-blue-50/95 backdrop-blur-md sticky bottom-0 z-20 pb-[env(safe-area-inset-bottom)] shadow-lg`}>
        <div className={`${isMobile ? 'max-w-full' : 'max-w-4xl'} mx-auto`}>
          <div className="flex items-end space-x-3">
            <div className="flex-1">
              <textarea
                className="w-full resize-none border-2 border-emerald-300/50 rounded-2xl px-5 py-4 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-500 shadow-lg transition-all duration-300 bg-gradient-to-r from-white to-emerald-50/30 disabled:from-gray-100 disabled:to-gray-200 disabled:cursor-not-allowed placeholder-gray-500 text-black"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  isModelChanging ? "🔄 모델 변경 중..." :
                  isModeChanging ? "🧬 모드 변경 중..." :
                  isPromptChanging ? "⚙️ 프롬프트 변경 중..." :
                  isLoading ? "🧬 응답 처리 중..." :
                  "🔬 신약개발 연구 질문을 입력하세요..."
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
              className="bg-gradient-to-r from-emerald-500 via-blue-500 to-cyan-600 hover:from-emerald-600 hover:via-blue-600 hover:to-cyan-700 disabled:from-gray-300 disabled:via-gray-400 disabled:to-gray-500 text-white p-4 rounded-2xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:ring-offset-2 shadow-xl disabled:shadow-none disabled:cursor-not-allowed group"
              title={
                isModelChanging ? "🔄 모델 변경 중..." :
                isModeChanging ? "🧬 모드 변경 중..." :
                isPromptChanging ? "⚙️ 프롬프트 변경 중..." :
                isLoading ? "🧬 응답 처리 중..." :
                "🚀 연구 질문 전송"
              }
            >
              {isLoading || isModelChanging || isModeChanging || isPromptChanging ? (
                <div className="w-6 h-6 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
              ) : (
                <Send className="w-6 h-6 group-hover:scale-110 transition-transform duration-200" />
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