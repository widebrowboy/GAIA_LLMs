'use client';

import React, { memo } from 'react';
import Image from 'next/image';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import rehypeRaw from 'rehype-raw';
import { Message } from '@/types/chat';

interface MessageItemProps {
  message: Message;
}

const MessageItem: React.FC<MessageItemProps> = memo(({ message }) => {
  const isUserMessage = message.role === 'user';
  const isAssistantMessage = message.role === 'assistant';
  const isSystemMessage = message.role === 'system';
  const isCompleteResponse = isAssistantMessage && message.isComplete;
  const isStreamingMessage = isAssistantMessage && !message.isComplete;

  // 고급 마크다운 전처리 함수 - 컨텍스트 인식 처리
  const advancedMarkdownProcessor = (text: string): string => {
    const lines = text.split('\n');
    let inCodeBlock = false;
    let inListContext = false;
    
    return lines.map((line, index) => {
      // 코드 블록 감지
      if (line.startsWith('```')) {
        inCodeBlock = !inCodeBlock;
        return line;
      }
      
      if (inCodeBlock) return line; // 코드 블록 내부는 건드리지 않음
      
      const trimmedLine = line.trim();
      const isListItem = /^\s*[*\-+]\s+/.test(line);
      const prevLine = index > 0 ? lines[index - 1].trim() : '';
      const nextLine = index < lines.length - 1 ? lines[index + 1].trim() : '';
      
      // 리스트 컨텍스트 추적
      if (isListItem) {
        inListContext = true;
      } else if (trimmedLine === '' && !nextLine.match(/^\s*[*\-+]\s+/)) {
        inListContext = false;
      }
      
      // * 기호 분석 및 처리
      if (trimmedLine.includes('*')) {
        // 리스트 아이템인 경우
        if (isListItem) {
          return handleListItem(line, nextLine);
        }
        
        // 강조 텍스트인 경우
        if (trimmedLine.match(/\*[^*]+\*/)) {
          return line + (nextLine ? '  ' : '');
        }
        
        // 볼드 텍스트인 경우  
        if (trimmedLine.match(/\*\*[^*]+\*\*/)) {
          return line + (nextLine ? '  ' : '');
        }
      }
      
      return handleRegularText(line, nextLine, inListContext);
    }).join('\n');
  };

  const handleListItem = (line: string, nextLine: string): string => {
    const isNextListItem = /^\s*[*\-+]\s+/.test(nextLine);
    
    // 다음 줄도 리스트면 자연스러운 연결
    if (isNextListItem) return line;
    
    // 리스트 항목이 길면 줄바꿈 추가
    if (line.length > 80) return line + '  ';
    
    return line;
  };

  const handleRegularText = (line: string, nextLine: string, inListContext: boolean): string => {
    if (!line.trim()) return line; // 빈 줄 유지
    
    // 리스트 컨텍스트에서는 자연스러운 흐름 유지
    if (inListContext && nextLine && !nextLine.match(/^\s*[*\-+]\s+/)) {
      return line + '  ';
    }
    
    // 일반 텍스트 처리
    if (nextLine && nextLine.trim()) {
      return line + '  ';
    }
    
    return line;
  };

  // 다중 줄바꿈 지원
  const handleMultipleLineBreaks = (content: string): string => {
    // \n\n을 강제 줄바꿈으로 변환
    return content.replace(/\n\n/g, '\n &nbsp;\n &nbsp;\n');
  };
  
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
            ? 'bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 border-2 border-blue-300 shadow-lg'
            : 'bg-gradient-to-r from-gray-50 to-slate-50 border border-gray-200'
      } rounded-2xl px-6 py-5 shadow-sm`}>

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

        {/* 메시지 텍스트 - 완료된 응답만 마크다운 렌더링 적용 */}
        <div className="break-words leading-relaxed text-gray-900 overflow-wrap-anywhere word-break-break-word max-w-full">
          {isCompleteResponse ? (
            // 완료된 응답: 전처리된 마크다운 렌더링 적용
            <div className="markdown-content prose prose-slate max-w-none overflow-hidden">
              <ReactMarkdown
                remarkPlugins={[remarkBreaks, remarkGfm]}
                rehypePlugins={[rehypeRaw]}
                components={{
                  // 제목 스타일링 개선 - 자연스러운 간격과 색상
                  h1: ({children}) => (
                    <h1 className="text-2xl font-bold text-emerald-800 mb-4 mt-6 pb-2 border-b-2 border-emerald-200">{children}</h1>
                  ),
                  h2: ({children}) => (
                    <h2 className="text-xl font-semibold text-blue-800 mb-3 mt-5">{children}</h2>
                  ),
                  h3: ({children}) => (
                    <h3 className="text-lg font-medium text-gray-800 mb-2 mt-4">{children}</h3>
                  ),
                  h4: ({children}) => (
                    <h4 className="text-base font-medium text-gray-700 mb-2 mt-3">{children}</h4>
                  ),
                  h5: ({children}) => (
                    <h5 className="text-sm font-medium text-gray-600 mb-1 mt-2">{children}</h5>
                  ),
                  h6: ({children}) => (
                    <h6 className="text-sm font-medium text-gray-500 mb-1 mt-2">{children}</h6>
                  ),
                  // 강조 스타일링 - 가이드 기반 개선
                  strong: ({children}) => (
                    <strong className="font-semibold text-emerald-700 markdown-strong">{children}</strong>
                  ),
                  em: ({children}) => (
                    <em className="italic text-gray-700 markdown-emphasis">{children}</em>
                  ),
                  // 리스트 스타일링 - 가이드 기반 개선
                  ul: ({children, ...props}) => (
                    <ul className="list-block markdown-list" {...props}>{children}</ul>
                  ),
                  ol: ({children, ...props}) => (
                    <ol className="list-block markdown-list" {...props}>{children}</ol>
                  ),
                  li: ({children, ...props}) => (
                    <li className="list-item-block markdown-list-item" {...props}>{children}</li>
                  ),
                  // 표 스타일링
                  table: ({children}) => (
                    <div className="overflow-x-auto my-4">
                      <table className="min-w-full divide-y divide-gray-200 border border-gray-300 rounded-lg overflow-hidden">{children}</table>
                    </div>
                  ),
                  thead: ({children}) => (
                    <thead className="bg-emerald-50">{children}</thead>
                  ),
                  th: ({children}) => (
                    <th className="px-4 py-2 text-left text-sm font-semibold text-emerald-800 border-b border-emerald-200">{children}</th>
                  ),
                  td: ({children}) => (
                    <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-200">{children}</td>
                  ),
                  // 인용구 스타일링
                  blockquote: ({children}) => (
                    <blockquote className="border-l-4 border-emerald-400 bg-emerald-50/50 pl-4 py-2 my-4 italic text-emerald-800">{children}</blockquote>
                  ),
                  // 코드 스타일링
                  code: ({className, children, ...props}) => {
                    const match = /language-(\w+)/.exec(className || '');
                    return !match ? (
                      <code className="bg-gray-100 text-gray-800 px-1 py-0.5 rounded text-sm font-mono" {...props}>
                        {children}
                      </code>
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    );
                  },
                  // 단락 스타일링 - 자연스러운 간격과 줄바꿈 처리
                  p: ({children}) => (
                    <p className="mb-3 leading-relaxed text-gray-800">{children}</p>
                  ),
                  // 수평선 스타일링
                  hr: () => (
                    <hr className="my-6 border-t border-gray-300" />
                  ),
                  // 링크 스타일링
                  a: ({children, href}) => (
                    <a href={href} className="text-blue-600 hover:text-blue-800 underline" target="_blank" rel="noopener noreferrer">{children}</a>
                  ),
                }}
              >
                {(() => {
                  let processed = advancedMarkdownProcessor(message.content);
                  processed = handleMultipleLineBreaks(processed);
                  return processed;
                })()}
              </ReactMarkdown>
            </div>
          ) : isStreamingMessage ? (
            // 스트리밍 중: 고급 전처리 로직 적용
            <div className="streaming-text text-gray-700 markdown-container" style={{ whiteSpace: 'pre-line' }}>
              {(() => {
                let processed = advancedMarkdownProcessor(message.content);
                processed = handleMultipleLineBreaks(processed);
                return processed;
              })()}
            </div>
          ) : (
            // 사용자 메시지: 고급 전처리 로직 적용
            <div className="user-text markdown-container" style={{ whiteSpace: 'pre-line' }}>
              {(() => {
                let processed = advancedMarkdownProcessor(message.content);
                processed = handleMultipleLineBreaks(processed);
                return processed;
              })()}
            </div>
          )}
        </div>
        
        {/* 타임스탬프 */}
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