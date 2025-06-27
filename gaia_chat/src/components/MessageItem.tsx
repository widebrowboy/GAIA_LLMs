'use client';

import React, { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import Image from 'next/image';
import { Message } from '@/types/chat';

interface MessageItemProps {
  message: Message;
}

const MessageItem: React.FC<MessageItemProps> = memo(({ message }) => {
  const isUserMessage = message.role === 'user';
  const isAssistantMessage = message.role === 'assistant';
  const isSystemMessage = message.role === 'system';
  const isCompleteResponse = isAssistantMessage && message.isComplete;
  const hasResearchKeywords = isAssistantMessage && (
    message.content.toLowerCase().includes('연구') ||
    message.content.toLowerCase().includes('임상') ||
    message.content.toLowerCase().includes('신약') ||
    message.content.toLowerCase().includes('화학') ||
    message.content.toLowerCase().includes('research') ||
    message.content.toLowerCase().includes('clinical') ||
    message.content.toLowerCase().includes('drug')
  );
  
  const timestamp = new Date(message.timestamp).toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
  });

  // 마크다운 컴포넌트 커스터마이징
  const markdownComponents = {
    // 헤딩 스타일링
    h1: ({ children, ...props }: any) => (
      <h1 className="text-xl font-bold mb-3 text-gray-900 border-b pb-2" {...props}>{children}</h1>
    ),
    h2: ({ children, ...props }: any) => (
      <h2 className="text-lg font-bold mb-2 text-gray-800" {...props}>{children}</h2>
    ),
    h3: ({ children, ...props }: any) => (
      <h3 className="text-md font-semibold mb-2 text-gray-800" {...props}>{children}</h3>
    ),
    
    // 단락 스타일링
    p: ({ children, ...props }: any) => (
      <p className="mb-3 leading-relaxed text-sm sm:text-base" {...props}>{children}</p>
    ),
    
    // 리스트 스타일링
    ul: ({ children, ...props }: any) => (
      <ul className="list-disc pl-5 mb-3 space-y-1" {...props}>{children}</ul>
    ),
    ol: ({ children, ...props }: any) => (
      <ol className="list-decimal pl-5 mb-3 space-y-1" {...props}>{children}</ol>
    ),
    li: ({ children, ...props }: any) => (
      <li className="text-sm sm:text-base leading-relaxed pl-1" {...props}>{children}</li>
    ),
    
    // 코드 블록 스타일링
    pre: ({ children, ...props }: any) => (
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto max-h-96 overflow-y-auto text-xs sm:text-sm mb-4 border border-gray-700 shadow-inner max-w-full" {...props}>
        {children}
      </pre>
    ),
    code: ({ inline, children, ...props }: any) => {
      if (inline) {
        return (
          <code className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded-md text-sm font-mono break-words whitespace-normal" {...props}>
            {children}
          </code>
        );
      }
      return (
        <code className="text-gray-100 font-mono text-xs sm:text-sm break-words whitespace-pre-wrap" {...props}>
          {children}
        </code>
      );
    },
    
    // 인용구 스타일링
    blockquote: ({ children, ...props }: any) => (
      <blockquote className="border-l-4 border-blue-400 pl-4 py-3 bg-blue-50 text-gray-700 mb-3 rounded-r-md text-sm sm:text-base italic" {...props}>
        {children}
      </blockquote>
    ),
    
    // 테이블 스타일링
    table: ({ children, ...props }: any) => (
      <div className="overflow-x-auto mb-2">
        <table className="min-w-full border border-gray-300 rounded" {...props}>
          {children}
        </table>
      </div>
    ),
    thead: ({ children, ...props }: any) => (
      <thead className="bg-gray-100" {...props}>{children}</thead>
    ),
    th: ({ children, ...props }: any) => (
      <th className="border border-gray-300 px-3 py-2 text-left font-semibold text-sm" {...props}>
        {children}
      </th>
    ),
    td: ({ children, ...props }: any) => (
      <td className="border border-gray-300 px-3 py-2 text-sm" {...props}>
        {children}
      </td>
    ),
    
    // 링크 스타일링
    a: ({ href, children, ...props }: any) => (
      <a 
        href={href} 
        target="_blank" 
        rel="noopener noreferrer"
        className="text-blue-600 hover:text-blue-800 underline"
        {...props}
      >
        {children}
      </a>
    ),
    
    // 강조 스타일링
    strong: ({ children, ...props }: any) => (
      <strong className="font-bold text-gray-900" {...props}>{children}</strong>
    ),
    em: ({ children, ...props }: any) => (
      <em className="italic text-gray-700" {...props}>{children}</em>
    ),
    
    // 수평선 스타일링
    hr: ({ ...props }: any) => (
      <hr className="border-gray-300 my-4" {...props} />
    ),
  };

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
            <div className="text-blue-900 leading-relaxed">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
                components={{
                  ...markdownComponents,
                  // 시스템 메시지용 스타일 오버라이드
                  h1: ({ children, ...props }: any) => (
                    <h1 className="text-lg font-bold mb-2 text-blue-900" {...props}>{children}</h1>
                  ),
                  h2: ({ children, ...props }: any) => (
                    <h2 className="text-md font-bold mb-2 text-blue-800" {...props}>{children}</h2>
                  ),
                  strong: ({ children, ...props }: any) => (
                    <strong className="font-bold text-blue-900" {...props}>{children}</strong>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start space-x-4 mb-6">
      {/* 아바타 - 개선된 GAIA-BT 로고 적용 */}
      <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shadow-xl border-2 flex-shrink-0 ${
        isUserMessage
          ? 'bg-gradient-to-br from-emerald-400 via-green-500 to-emerald-600 border-emerald-300/50'
          : isSystemMessage
          ? 'bg-gradient-to-br from-purple-400 via-indigo-500 to-purple-600 border-purple-300/50'
          : isCompleteResponse
          ? 'bg-gradient-to-br from-white via-emerald-50 to-blue-50 border-emerald-300/70 p-1'
          : 'bg-gradient-to-br from-blue-400 via-cyan-500 to-blue-600 border-blue-300/50'
      }`}>
        {isUserMessage ? (
          <span className="text-2xl">🔬</span>
        ) : isSystemMessage ? (
          <span className="text-2xl">⚙️</span>
        ) : isCompleteResponse ? (
          <Image
            src="/GAIABT_Logo.png"
            alt="GAIA-BT Logo"
            width={40}
            height={40}
            className="w-10 h-10 object-contain"
          />
        ) : (
          <span className="text-2xl">🧬</span>
        )}
      </div>
      {/* 메시지 컨테이너 */}
      <div className={`${
        isUserMessage
          ? 'bg-gradient-to-br from-emerald-50/90 to-blue-50/90 border-2 border-emerald-200/70'
          : isCompleteResponse
          ? 'bg-gradient-to-br from-white via-blue-50/30 to-emerald-50/50 border-2 border-blue-300/50 shadow-2xl'
          : hasResearchKeywords
          ? 'bg-gradient-to-br from-blue-50/90 via-cyan-50/90 to-emerald-50/90 border-2 border-cyan-200/70'
          : 'bg-gradient-to-br from-gray-50/90 to-slate-50/90 border-2 border-gray-200/70'
      } rounded-3xl px-6 py-4 shadow-xl flex-1 backdrop-blur-sm`}>
        {/* 헤더 - 완전한 응답에 대해서만 표시 */}
        {isCompleteResponse && (
          <div className="mb-6 pb-4 border-b-2 border-gradient-to-r from-emerald-200 to-blue-200">
            <div className="flex items-center space-x-3 mb-2">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-bold text-emerald-700">📝 연구 보고서</span>
              </div>
              <div className="flex-1 h-px bg-gradient-to-r from-emerald-300 via-blue-300 to-transparent"></div>
              <span className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
                완료됨 {timestamp}
              </span>
            </div>
            {message.userQuestion && (
              <div className="bg-gradient-to-r from-emerald-50 to-blue-50 p-3 rounded-xl border border-emerald-200/50 mb-4">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-sm">🔍</span>
                  <span className="text-xs font-semibold text-emerald-700">연구 주제</span>
                </div>
                <p className="text-sm text-gray-700 font-medium italic">"{message.userQuestion}"</p>
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

        {/* 메시지 텍스트/마크다운 */}
        {isUserMessage ? (
          <div className="whitespace-pre-wrap break-words leading-relaxed text-gray-900">
            {message.content}
          </div>
        ) : (
          <div className={`prose prose-sm max-w-none overflow-wrap-anywhere break-words text-gray-900 ${
            isCompleteResponse ? 'prose-lg' : ''
          }`}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
              components={{
                // 완전한 응답에 대한 헤더 스타일 개선
                h1: ({ children, ...props }: any) => (
                  <h1 className={`${
                    isCompleteResponse 
                      ? 'text-2xl font-bold bg-gradient-to-r from-emerald-700 to-blue-700 bg-clip-text text-transparent mb-6 pb-3 border-b-2 border-emerald-200' 
                      : 'text-xl font-bold text-gray-800 mb-4'
                  } mt-6`} {...props}>
                    {isCompleteResponse && <span className="mr-2">📄</span>}{children}
                  </h1>
                ),
                h2: ({ children, ...props }: any) => (
                  <h2 className={`${
                    isCompleteResponse 
                      ? 'text-xl font-bold text-emerald-700 mb-4 mt-8 flex items-center'
                      : 'text-lg font-bold text-gray-700 mb-3 mt-6'
                  }`} {...props}>
                    {isCompleteResponse && <span className="mr-2">📋</span>}{children}
                  </h2>
                ),
                h3: ({ children, ...props }: any) => (
                  <h3 className={`${
                    isCompleteResponse 
                      ? 'text-lg font-semibold text-blue-700 mb-3 mt-6 flex items-center'
                      : 'text-base font-semibold text-gray-700 mb-2 mt-4'
                  }`} {...props}>
                    {isCompleteResponse && <span className="mr-2">🔹</span>}{children}
                  </h3>
                ),
                ...markdownComponents,
                // 완전한 응답에 대한 추가 스타일링
                blockquote: ({ children, ...props }: any) => (
                  <blockquote className={`border-l-4 border-emerald-400 pl-6 py-3 my-4 italic text-emerald-800 rounded-r-lg ${
                    isCompleteResponse 
                      ? 'bg-gradient-to-r from-emerald-50 to-blue-50/50 shadow-md'
                      : 'bg-emerald-50/50'
                  }`} {...props}>
                    {isCompleteResponse && <span className="mr-2">💬</span>}{children}
                  </blockquote>
                ),
                p: ({ children, ...props }: any) => (
                  <p className={`${
                    isCompleteResponse ? 'mb-4 leading-relaxed text-gray-800' : 'mb-3'
                  }`} {...props}>
                    {children}
                  </p>
                )
              }}
            >
              {message.content}
            </ReactMarkdown>
            
            {/* 완전한 응답의 푸터 */}
            {isCompleteResponse && (
              <div className="mt-8 pt-4 border-t border-emerald-200">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <div className="flex items-center space-x-2">
                    <span>✓</span>
                    <span>연구 보고서 완료</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>📅</span>
                    <span>{new Date(message.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* 타임스탬프 및 상태 표시 */}
        {isAssistantMessage && !isCompleteResponse && (
          <div className="flex items-center space-x-2 mt-3 text-xs text-gray-500">
            <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
            <span>GAIA-BT 응답</span>
            <span className="text-gray-400">•</span>
            <span>{timestamp}</span>
          </div>
        )}
      </div>
    </div>
  );
});

MessageItem.displayName = 'MessageItem';

export default MessageItem;