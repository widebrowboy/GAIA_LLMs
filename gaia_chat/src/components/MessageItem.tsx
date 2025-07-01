'use client';

import React, { memo } from 'react';
import Image from 'next/image';
import { Message } from '@/types/chat';

interface MessageItemProps {
  message: Message;
}


const MessageItem: React.FC<MessageItemProps> = memo(({ message }) => {
  const isUserMessage = message.role === 'user';
  const isAssistantMessage = message.role === 'assistant';
  const isSystemMessage = message.role === 'system';
  // 모든 응답을 원본 텍스트로 출력

  
  const timestamp = new Date(message.timestamp).toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
  });

  // 시스템 메시지를 위한 별도 렌더링
  if (isSystemMessage) {
    return (
      <div className="flex justify-center mb-6">
        <div className="max-w-3xl w-full">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg px-6 py-4 shadow-sm">
            <div className="flex items-center mb-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mr-3">
                <span className="text-white text-sm font-bold">🤖</span>
              </div>
              <span className="text-blue-800 font-medium text-sm">시스템 안내</span>
              <span className="text-blue-600 text-xs ml-auto">{timestamp}</span>
            </div>
            <div className="text-blue-900 leading-relaxed whitespace-pre-wrap">
              {message.content}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`mb-6 ${isUserMessage ? 'flex justify-end' : 'flex justify-start'}`}>
      <div className={`max-w-3xl w-full ${
        isUserMessage 
          ? 'bg-gradient-to-r from-emerald-50 to-green-50 border border-emerald-200' 
          : 'bg-gradient-to-r from-gray-50 to-slate-50 border border-gray-200'
      } rounded-2xl px-6 py-5 shadow-sm`}>

        
        {/* 메시지 내용 */}
        {isUserMessage ? (
          <div className="flex items-center space-x-3 mb-3">
            <span className="text-sm">🔬</span>
            <span className="text-xs font-bold text-emerald-700">연구자</span>
          </div>
        ) : isAssistantMessage && (
          <div className="flex items-center space-x-3 mb-3">
            <span className="text-sm">🧠</span>
            <span className="text-xs font-bold text-blue-700">GAIA-BT 연구지원</span>
            <div className="flex space-x-1">
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
              <div className="w-1.5 h-1.5 bg-cyan-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        )}

        {/* 메시지 텍스트 - 모든 응답을 원본 텍스트로 출력 */}
        <div className="break-words leading-relaxed text-gray-900 overflow-wrap-anywhere word-break-break-word max-w-full">
          <div 
            className="raw-text korean-text prose prose-slate max-w-none"
            style={{ 
              whiteSpace: 'pre-wrap', 
              lineHeight: '1.8',
              color: '#374151',
              fontFamily: '"Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans KR", "Malgun Gothic", "맑은 고딕", sans-serif',
              wordBreak: 'break-word',
              overflowWrap: 'break-word'
            }}
          >
            {message.content}
          </div>
        </div>
        
        {/* 타임스탬프 */}
        <div className="flex justify-end mt-3">
          <span className="text-xs text-gray-500">{timestamp}</span>
        </div>
      </div>
    </div>
  );
});

MessageItem.displayName = 'MessageItem';

export default MessageItem;