'use client';

import React, { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { Message } from '@/types/chat';

interface MessageItemProps {
  message: Message;
}

const MessageItem: React.FC<MessageItemProps> = memo(({ message }) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';
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
  if (isSystem) {
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
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex items-start space-x-3 max-w-2xl lg:max-w-4xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* 아바타 */}
        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold shadow-lg ${
          isUser ? 'bg-gradient-to-br from-green-500 to-green-600' : 'bg-gradient-to-br from-blue-500 to-blue-600'
        }`}>
          {isUser ? '👤' : '🧬'}
        </div>
        
        {/* 메시지 버블 */}
        <div className="flex flex-col">
          <div className={`rounded-2xl px-4 py-3 shadow-sm ${
            isUser 
              ? 'bg-gradient-to-br from-green-500 to-green-600 text-white' 
              : 'bg-white border border-gray-200 text-gray-800'
          }`}>
            {isUser ? (
              // 사용자 메시지는 일반 텍스트로 표시
              <p className="whitespace-pre-wrap break-words leading-relaxed">
                {message.content}
              </p>
            ) : (
              // AI 메시지는 마크다운으로 렌더링
              <div className="prose prose-sm max-w-none break-words overflow-visible">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypeHighlight]}
                  components={markdownComponents as any}
                  skipHtml={false}
                  unwrapDisallowed={false}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            )}
          </div>
          
          {/* 시간 및 상태 */}
          <div className={`flex items-center space-x-2 mt-1 px-2 ${
            isUser ? 'justify-end' : 'justify-start'
          }`}>
            <span className="text-xs text-gray-500">
              {timestamp}
            </span>
            {isUser && (
              <span className="text-xs text-green-600">✓</span>
            )}
            {!isUser && (
              <span className="text-xs text-blue-600 flex items-center">
                <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mr-1"></span>
                GAIA-BT
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
});

MessageItem.displayName = 'MessageItem';

export default MessageItem;