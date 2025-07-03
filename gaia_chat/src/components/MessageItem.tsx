'use client';

import React, { memo, useState } from 'react';
import Image from 'next/image';
import { Message } from '@/types/chat';
import { formatRelativeTime } from '@/utils/helpers';
import AcademicMarkdownRenderer from './AcademicMarkdownRenderer';
import RelativeTime from './RelativeTime';
import { Copy, ThumbsUp, ThumbsDown, Check } from 'lucide-react';

interface MessageItemProps {
  message: Message;
}


const MessageItem: React.FC<MessageItemProps> = memo(({ message }) => {
  const isUserMessage = message.role === 'user';
  const isAssistantMessage = message.role === 'assistant';
  const isSystemMessage = message.role === 'system';
  const isCompleteResponse = isAssistantMessage && message.isComplete;
  
  // 피드백 및 복사 상태 관리
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);
  const [copied, setCopied] = useState(false);
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState<string>('');

  // 복사 기능
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000); // 2초 후 아이콘 복원
    } catch (error) {
      console.error('복사 실패:', error);
      // 폴백: 텍스트 선택 방식
      const textArea = document.createElement('textarea');
      textArea.value = message.content;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // 피드백 처리
  const handleFeedback = async (type: 'up' | 'down') => {
    if (feedback === type) {
      setFeedback(null); // 같은 버튼 클릭 시 취소
      setFeedbackMessage('');
      return;
    }

    setFeedbackSubmitting(true);
    setFeedback(type);

    try {
      // 피드백을 서버에 전송
      const response = await fetch('http://localhost:8000/api/feedback/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: message.userQuestion || "사용자 질문 정보 없음",
          answer: message.content,
          feedback_type: type === 'up' ? 'positive' : 'negative',
          session_id: `session_${Date.now()}`,
          user_id: 'anonymous',
          model_version: 'gemma3-12b',
          response_time: 0,
          confidence_score: 0.8
        }),
      });

      if (response.ok) {
        const result = await response.json();
        
        // 새로운 API 응답 구조 처리 (v3.81)
        if (result.status === 'success') {
          setFeedbackMessage(result.message || '피드백이 저장되었습니다.');
        } else if (result.status === 'duplicate') {
          setFeedbackMessage(result.message || '🔄 유사한 피드백이 이미 존재합니다.');
          // 중복인 경우 피드백 상태 복원
          setFeedback(null);
        } else if (result.status === 'error') {
          setFeedbackMessage(result.message || '❌ 피드백 저장에 실패했습니다.');
          setFeedback(null);
        } else {
          setFeedbackMessage(result.message || '피드백이 저장되었습니다.');
        }
        
        // 3초 후 메시지 숨김
        setTimeout(() => {
          setFeedbackMessage('');
        }, 3000);
      } else {
        // HTTP 오류 응답 처리
        const errorResult = await response.json().catch(() => ({}));
        setFeedbackMessage(errorResult.detail || '피드백 저장에 실패했습니다.');
        setFeedback(null);
      }
    } catch (error) {
      console.error('피드백 전송 오류:', error);
      setFeedbackMessage('피드백 저장에 실패했습니다. 나중에 다시 시도해주세요.');
      
      // 오류 시 피드백 상태 복원
      setFeedback(null);
      
      // 5초 후 오류 메시지 숨김
      setTimeout(() => {
        setFeedbackMessage('');
      }, 5000);
    } finally {
      setFeedbackSubmitting(false);
    }
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
              <RelativeTime date={message.timestamp} className="text-blue-600 text-xs ml-auto" />
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
      <div className={`${isUserMessage ? 'max-w-2xl' : 'max-w-3xl w-full'} ${
        isUserMessage 
          ? 'bg-gradient-to-l from-blue-50 to-cyan-50 border border-blue-200' 
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
              <div className="flex items-center space-x-3">
                {/* 피드백 및 복사 버튼 */}
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleFeedback('up')}
                    disabled={feedbackSubmitting}
                    className={`p-2 rounded-lg transition-all duration-200 hover:bg-green-50 ${
                      feedback === 'up' 
                        ? 'bg-green-100 text-green-600' 
                        : 'text-gray-400 hover:text-green-500'
                    } ${feedbackSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
                    title="도움이 되었습니다"
                  >
                    <ThumbsUp size={16} />
                  </button>
                  <button
                    onClick={() => handleFeedback('down')}
                    disabled={feedbackSubmitting}
                    className={`p-2 rounded-lg transition-all duration-200 hover:bg-red-50 ${
                      feedback === 'down' 
                        ? 'bg-red-100 text-red-600' 
                        : 'text-gray-400 hover:text-red-500'
                    } ${feedbackSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
                    title="개선이 필요합니다"
                  >
                    <ThumbsDown size={16} />
                  </button>
                  <button
                    onClick={handleCopy}
                    className={`p-2 rounded-lg transition-all duration-200 hover:bg-blue-50 ${
                      copied 
                        ? 'bg-blue-100 text-blue-600' 
                        : 'text-gray-400 hover:text-blue-500'
                    }`}
                    title={copied ? '복사 완료!' : '응답 복사'}
                  >
                    {copied ? <Check size={16} /> : <Copy size={16} />}
                  </button>
                </div>
                
                {/* 피드백 메시지 표시 */}
                {feedbackMessage && (
                  <div className={`mt-2 p-2 rounded-lg text-xs transition-all duration-300 ${
                    feedbackMessage.includes('실패') || feedbackMessage.includes('오류')
                      ? 'bg-red-50 text-red-700 border border-red-200'
                      : 'bg-green-50 text-green-700 border border-green-200'
                  }`}>
                    {feedbackMessage}
                  </div>
                )}
                <RelativeTime date={message.timestamp} className="text-xs text-gray-500" />
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
          <div className="flex items-center justify-end space-x-3 mb-3">
            <span className="text-xs font-bold text-blue-700">연구자</span>
            <span className="text-sm">🔬</span>
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
          <div className="break-words leading-relaxed text-gray-900 overflow-wrap-anywhere word-break-break-word max-w-full text-right">
            <div 
              className="raw-text korean-text prose prose-slate max-w-none text-right"
              style={{ 
                whiteSpace: 'pre-wrap', 
                lineHeight: '1.8',
                color: '#374151',
                fontFamily: '"Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans KR", "Malgun Gothic", "맑은 고딕", sans-serif',
                wordBreak: 'break-word',
                overflowWrap: 'break-word',
                textAlign: 'right'
              }}
            >
              {message.content}
            </div>
          </div>
        )}
        
        {/* 타임스탬프 및 액션 버튼 - 완료된 응답은 헤더에 표시되므로 제외 */}
        {!isCompleteResponse && (
          <div className={`flex mt-3 ${isUserMessage ? 'justify-start' : 'justify-between'}`}>
            {/* Assistant 메시지의 경우 왼쪽에 액션 버튼, 오른쪽에 타임스탬프 */}
            {isAssistantMessage && (
              <div className="flex flex-col">
                <div className="flex items-center space-x-2 mb-2">
                  <button
                    onClick={() => handleFeedback('up')}
                    disabled={feedbackSubmitting}
                    className={`p-1.5 rounded-md transition-all duration-200 hover:bg-green-50 ${
                      feedback === 'up' 
                        ? 'bg-green-100 text-green-600' 
                        : 'text-gray-400 hover:text-green-500'
                    } ${feedbackSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
                    title="도움이 되었습니다"
                  >
                    <ThumbsUp size={14} />
                  </button>
                  <button
                    onClick={() => handleFeedback('down')}
                    disabled={feedbackSubmitting}
                    className={`p-1.5 rounded-md transition-all duration-200 hover:bg-red-50 ${
                      feedback === 'down' 
                        ? 'bg-red-100 text-red-600' 
                        : 'text-gray-400 hover:text-red-500'
                    } ${feedbackSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
                    title="개선이 필요합니다"
                  >
                    <ThumbsDown size={14} />
                  </button>
                  <button
                    onClick={handleCopy}
                    className={`p-1.5 rounded-md transition-all duration-200 hover:bg-blue-50 ${
                      copied 
                        ? 'bg-blue-100 text-blue-600' 
                        : 'text-gray-400 hover:text-blue-500'
                    }`}
                    title={copied ? '복사 완료!' : '응답 복사'}
                  >
                    {copied ? <Check size={14} /> : <Copy size={14} />}
                  </button>
                </div>
                
                {/* 피드백 메시지 표시 (스트리밍용) */}
                {feedbackMessage && (
                  <div className={`p-2 rounded-lg text-xs transition-all duration-300 mb-2 ${
                    feedbackMessage.includes('실패') || feedbackMessage.includes('오류')
                      ? 'bg-red-50 text-red-700 border border-red-200'
                      : 'bg-green-50 text-green-700 border border-green-200'
                  }`}>
                    {feedbackMessage}
                  </div>
                )}
              </div>
            )}
            <RelativeTime date={message.timestamp} className="text-xs text-gray-500" />
          </div>
        )}
      </div>
    </div>
  );
});

MessageItem.displayName = 'MessageItem';

export default MessageItem;