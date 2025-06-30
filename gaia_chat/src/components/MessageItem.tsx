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

        {/* 메시지 텍스트 - 완료된 assistant 응답만 마크다운 렌더링 적용 */}
        <div className="break-words leading-relaxed text-gray-900 overflow-wrap-anywhere word-break-break-word max-w-full">
          {isAssistantMessage && isCompleteResponse ? (
            // 완료된 Assistant 응답: 의료 문서 스타일의 마크다운 렌더링 적용
            <div className="medical-document prose prose-slate max-w-none overflow-hidden korean-text">
              <ReactMarkdown
                remarkPlugins={[
                  [remarkBreaks, { gfm: true }], // GitHub 스타일 줄바꿈 활성화
                  remarkGfm
                ]}
                rehypePlugins={[rehypeRaw]}
                components={{
                  // 메인 타이틀 - 의료 문서 스타일 (강제 줄바꿈 추가)
                  h1: ({children}) => (
                    <div className="heading-wrapper">
                      <div className="heading-break-before"></div>
                      <h1 className="document-main-title text-2xl font-bold text-slate-900 mb-8 mt-8 pb-3 border-b-3 border-blue-600 leading-tight tracking-tight flex items-center gap-3">
                        <span className="text-2xl">🏥</span>
                        {children}
                      </h1>
                      <div className="heading-break-after"></div>
                    </div>
                  ),
                  // 섹션 타이틀 - 의료 문서 스타일 (강제 줄바꿈 추가)
                  h2: ({children}) => (
                    <div className="heading-wrapper">
                      <div className="heading-break-before"></div>
                      <h2 className="section-title text-xl font-semibold text-slate-800 mb-6 mt-8 pb-2 px-4 py-3 bg-gradient-to-r from-slate-50 to-slate-100 border-l-4 border-blue-500 rounded-r-lg leading-tight flex items-center gap-2">
                        <span className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {(() => {
                            const text = children?.toString() || '';
                            const match = text.match(/^(\d+)\./);
                            return match ? match[1] : '•';
                          })()}
                        </span>
                        {children}
                      </h2>
                      <div className="heading-break-after"></div>
                    </div>
                  ),
                  // 서브섹션 타이틀 (강제 줄바꿈 추가)
                  h3: ({children}) => (
                    <div className="heading-wrapper">
                      <div className="heading-break-before"></div>
                      <h3 className="subsection-title text-lg font-medium text-slate-700 mb-4 mt-6 leading-tight flex items-center gap-2">
                        <span className="text-base">📋</span>
                        {children}
                      </h3>
                      <div className="heading-break-after"></div>
                    </div>
                  ),
                  h4: ({children}) => (
                    <div className="heading-wrapper">
                      <div className="heading-break-before"></div>
                      <h4 className="text-md font-medium text-slate-700 mb-3 mt-5 leading-tight flex items-center gap-2">
                        <span className="text-sm">🔹</span>
                        {children}
                      </h4>
                      <div className="heading-break-after"></div>
                    </div>
                  ),
                  // 의료 경고 박스 (blockquote)
                  blockquote: ({children}) => (
                    <div className="medical-alert bg-gradient-to-r from-red-50 to-red-100 border-2 border-red-300 rounded-xl p-4 my-4 flex gap-3 shadow-sm">
                      <div className="text-xl flex-shrink-0">⚠️</div>
                      <div className="flex-1">
                        <div className="font-semibold text-red-800 mb-1">중요한 안내사항</div>
                        <div className="text-red-700">{children}</div>
                      </div>
                    </div>
                  ),
                  // 의료 리스트 스타일 - 구분 강화 (순서없는 목록)
                  ul: ({children}) => (
                    <div className="list-wrapper">
                      <div className="list-break-before"></div>
                      <ul className="medical-list list-none p-0 my-4 space-y-2">
                        {children}
                      </ul>
                      <div className="list-break-after"></div>
                    </div>
                  ),
                  // 의료 리스트 스타일 - 구분 강화 (순서있는 목록)
                  ol: ({children}) => (
                    <div className="list-wrapper">
                      <div className="list-break-before"></div>
                      <ol className="medical-numbered-list list-none p-0 my-4 space-y-3">
                        {children}
                      </ol>
                      <div className="list-break-after"></div>
                    </div>
                  ),
                  // 의료 리스트 아이템 - 순서없는 목록
                  li: ({children, ...props}) => {
                    // 부모가 ol인지 ul인지 확인하여 다른 스타일 적용
                    const isOrderedList = props.node?.parent?.tagName === 'ol';
                    
                    if (isOrderedList) {
                      return (
                        <li className="medical-numbered-item flex items-start gap-3 p-3 bg-gradient-to-r from-emerald-50 to-blue-50 border-l-4 border-emerald-500 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 hover:translate-x-1">
                          <span className="numbered-marker text-lg flex-shrink-0 w-8 h-8 bg-emerald-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                            {/* 번호는 CSS counter로 자동 생성됨 */}
                          </span>
                          <span className="numbered-content flex-1">{children}</span>
                        </li>
                      );
                    }
                    
                    return (
                      <li className="medical-list-item flex items-start gap-3 p-3 bg-white border-l-4 border-green-500 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 hover:translate-x-1">
                        <span className="list-marker text-lg flex-shrink-0">💊</span>
                        <span className="list-content flex-1">{children}</span>
                      </li>
                    );
                  },
                  // 전문적인 강조 스타일링
                  strong: ({children}) => (
                    <strong className="medical-emphasis font-semibold text-blue-800 bg-gradient-to-r from-blue-50 to-blue-100 px-2 py-1 rounded">{children}</strong>
                  ),
                  em: ({children}) => (
                    <em className="italic text-slate-600 font-medium">{children}</em>
                  ),
                  // 의료 문서 단락 스타일 - 제목과 문단 앞뒤 줄바꿈 강화
                  p: ({children}) => (
                    <div className="paragraph-wrapper">
                      <p className="medical-paragraph mb-6 mt-4 leading-7 text-slate-700 text-justify">{children}</p>
                    </div>
                  ),
                  // 의료 전문 표 스타일링
                  table: ({children}) => (
                    <div className="overflow-x-auto my-6 rounded-lg shadow-sm border border-slate-200">
                      <table className="min-w-full divide-y divide-slate-300 bg-white">{children}</table>
                    </div>
                  ),
                  thead: ({children}) => (
                    <thead className="bg-gradient-to-r from-slate-50 to-slate-100">{children}</thead>
                  ),
                  th: ({children}) => (
                    <th className="px-6 py-4 text-left text-sm font-bold text-slate-800 border-b-2 border-slate-300 tracking-wide uppercase">{children}</th>
                  ),
                  td: ({children}) => (
                    <td className="px-6 py-4 text-sm text-slate-700 border-b border-slate-200 leading-6">{children}</td>
                  ),
                  // 의료 전문 링크 스타일링
                  a: ({href, children}) => (
                    <a 
                      href={href} 
                      className="medical-link text-blue-600 hover:text-blue-800 font-medium underline decoration-2 underline-offset-2 transition-colors duration-200 inline-flex items-center gap-1"
                      target="_blank" 
                      rel="noopener noreferrer"
                    >
                      {children} 
                      <span className="text-xs">🔗</span>
                    </a>
                  ),
                  // 수평선 스타일링
                  hr: () => (
                    <hr className="my-8 border-t-2 border-gradient-to-r from-slate-300 to-slate-400" />
                  ),
                  // 코드 스타일링
                  code: ({className, children, ...props}) => {
                    const match = /language-(\w+)/.exec(className || '');
                    return !match ? (
                      <code className="bg-slate-100 text-slate-800 px-2 py-1 rounded text-sm font-mono border border-slate-200" {...props}>
                        {children}
                      </code>
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    );
                  },
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          ) : (
            // 스트리밍 중이거나 사용자 메시지: 원본 텍스트만 표시
            <div 
              className={`raw-text ${isStreamingMessage ? 'streaming-text' : 'user-text'} korean-text`}
              style={{ 
                whiteSpace: 'pre-line', 
                lineHeight: '1.6',
                color: '#374151'
              }}
            >
              {message.content}
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