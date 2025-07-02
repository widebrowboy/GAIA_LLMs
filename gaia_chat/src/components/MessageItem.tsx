'use client';

import React, { memo } from 'react';
import Image from 'next/image';
import { Message } from '@/types/chat';
import AcademicMarkdownRenderer from './AcademicMarkdownRenderer';

interface MessageItemProps {
  message: Message;
}


const MessageItem: React.FC<MessageItemProps> = memo(({ message }) => {
  const isUserMessage = message.role === 'user';
  const isAssistantMessage = message.role === 'assistant';
  const isSystemMessage = message.role === 'system';
  const isCompleteResponse = isAssistantMessage && message.isComplete;

  
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
          : isCompleteResponse
            ? 'bg-white border-2 border-emerald-300 shadow-lg'
            : 'bg-gradient-to-r from-gray-50 to-slate-50 border border-gray-200'
      } rounded-2xl px-6 py-5 shadow-sm`}>

        {/* 헤더 - 완료된 응답에는 학술 보고서 헤더 표시 */}
        {isCompleteResponse && (
          <div className="mb-6 pb-4 border-b-2 border-emerald-200">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-blue-600 rounded-full flex items-center justify-center shadow-md">
                  <span className="text-white text-lg">📄</span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-800">Research Analysis Report</h3>
                  <p className="text-xs text-gray-600">GAIA-BT Academic Response</p>
                </div>
              </div>
              <div className="text-xs text-gray-500">
                {timestamp}
              </div>
            </div>
            {message.userQuestion && (
              <div className="bg-emerald-50 border border-emerald-200 p-3 rounded-lg">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-sm">🔍</span>
                  <span className="text-xs font-semibold text-emerald-700">Research Question</span>
                </div>
                <p className="text-sm text-gray-700 italic">"{message.userQuestion}"</p>
              </div>
            )}
          </div>
        )}
        
        {/* 메시지 내용 */}
        {isUserMessage ? (
          <div className="flex items-center space-x-3 mb-3">
            <span className="text-sm">🔬</span>
            <span className="text-xs font-bold text-emerald-700">연구자</span>
          </div>
        ) : isAssistantMessage && !isCompleteResponse && (
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

        {/* 메시지 텍스트 - 모든 assistant 응답에 마크다운 렌더링 적용 */}
        {isAssistantMessage ? (
          <div className="academic-response">
            <AcademicMarkdownRenderer 
              content={message.content} 
              className="text-gray-800"
            />
          </div>
        ) : (
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
        )}
        
        {/* 타임스탬프 - 완료된 응답은 헤더에 표시되므로 제외 */}
        {!isCompleteResponse && (
          <div className="flex justify-end mt-3">
            <span className="text-xs text-gray-500">{timestamp}</span>
          </div>
        )}
      </div>
    </div>
  );
});

MessageItem.displayName = 'MessageItem';

export default MessageItem;