'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';
import { Message } from '@/types/chat';

interface MessageItemProps {
  message: Message;
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const timestamp = new Date(message.timestamp).toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
  });

  // 마크다운 컴포넌트 커스터마이징
  const markdownComponents = {
    // 헤딩 스타일링
    h1: ({ children }: { children: React.ReactNode }) => (
      <h1 className="text-xl font-bold mb-3 text-gray-900 border-b pb-2">{children}</h1>
    ),
    h2: ({ children }: { children: React.ReactNode }) => (
      <h2 className="text-lg font-bold mb-2 text-gray-800">{children}</h2>
    ),
    h3: ({ children }: { children: React.ReactNode }) => (
      <h3 className="text-md font-semibold mb-2 text-gray-800">{children}</h3>
    ),
    
    // 단락 스타일링
    p: ({ children }: { children: React.ReactNode }) => (
      <p className="mb-2 leading-relaxed">{children}</p>
    ),
    
    // 리스트 스타일링
    ul: ({ children }: { children: React.ReactNode }) => (
      <ul className="list-disc list-inside mb-2 space-y-1 ml-2">{children}</ul>
    ),
    ol: ({ children }: { children: React.ReactNode }) => (
      <ol className="list-decimal list-inside mb-2 space-y-1 ml-2">{children}</ol>
    ),
    li: ({ children }: { children: React.ReactNode }) => (
      <li className="text-sm leading-relaxed">{children}</li>
    ),
    
    // 코드 블록 스타일링
    pre: ({ children }: { children: React.ReactNode }) => (
      <pre className="bg-gray-800 text-gray-100 p-3 rounded-md overflow-x-auto text-sm mb-2 border">
        {children}
      </pre>
    ),
    code: ({ inline, children }: { inline?: boolean; children: React.ReactNode }) => {
      if (inline) {
        return (
          <code className="bg-gray-200 text-gray-800 px-1 py-0.5 rounded text-sm font-mono">
            {children}
          </code>
        );
      }
      return (
        <code className="text-gray-100 font-mono text-sm">
          {children}
        </code>
      );
    },
    
    // 인용구 스타일링
    blockquote: ({ children }: { children: React.ReactNode }) => (
      <blockquote className="border-l-4 border-blue-400 pl-4 py-2 bg-blue-50 text-gray-700 mb-2 rounded-r">
        {children}
      </blockquote>
    ),
    
    // 테이블 스타일링
    table: ({ children }: { children: React.ReactNode }) => (
      <div className="overflow-x-auto mb-2">
        <table className="min-w-full border border-gray-300 rounded">
          {children}
        </table>
      </div>
    ),
    thead: ({ children }: { children: React.ReactNode }) => (
      <thead className="bg-gray-100">{children}</thead>
    ),
    th: ({ children }: { children: React.ReactNode }) => (
      <th className="border border-gray-300 px-3 py-2 text-left font-semibold text-sm">
        {children}
      </th>
    ),
    td: ({ children }: { children: React.ReactNode }) => (
      <td className="border border-gray-300 px-3 py-2 text-sm">
        {children}
      </td>
    ),
    
    // 링크 스타일링
    a: ({ href, children }: { href?: string; children: React.ReactNode }) => (
      <a 
        href={href} 
        target="_blank" 
        rel="noopener noreferrer"
        className="text-blue-600 hover:text-blue-800 underline"
      >
        {children}
      </a>
    ),
    
    // 강조 스타일링
    strong: ({ children }: { children: React.ReactNode }) => (
      <strong className="font-bold text-gray-900">{children}</strong>
    ),
    em: ({ children }: { children: React.ReactNode }) => (
      <em className="italic text-gray-700">{children}</em>
    ),
    
    // 수평선 스타일링
    hr: () => (
      <hr className="border-gray-300 my-4" />
    ),
  };

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
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypeHighlight, rehypeRaw]}
                  components={markdownComponents as any}
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
};

export default MessageItem;