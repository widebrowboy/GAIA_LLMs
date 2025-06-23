'use client';

import { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { 
  User, 
  Bot, 
  Clock, 
  Database, 
  CheckCircle,
  AlertCircle,
  Loader2 
} from 'lucide-react';
import { staggerContainerVariants, staggerItemVariants } from '@/utils/animations';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date | number;
  mode?: 'normal' | 'deep_research' | 'mcp';
  prompt_type?: string;
  sources?: string[];
  processing?: boolean;
  streaming?: boolean;
  error?: string;
  enhanced?: boolean;
}

interface MessageAreaProps {
  messages: Message[];
  mainPageLayout: {
    columns: number;
    cardSize: string;
    gridGap: string;
    textSize: string;
    containerMaxWidth: string;
    padding: string;
  };
  messagesEndRef: React.RefObject<HTMLDivElement>;
}

export default function MessageArea({ messages, mainPageLayout, messagesEndRef }: MessageAreaProps) {
  
  // 메시지 콘텐츠 렌더링 (마크다운 스타일)
  const renderMessageContent = useMemo(() => {
    return (content: string) => {
      if (!content) return null;
      
      // 마크다운 스타일 처리
      let processedContent = content;
      
      // 줄바꿈 처리
      processedContent = processedContent.replace(/\\n/g, '\n');
      processedContent = processedContent.replace(/([^\n])\n(#{1,6}\s)/g, '$1\n\n$2');
      
      // HTML로 변환하지 않고 텍스트로 표시 (보안상 안전)
      return processedContent.split('\n').map((line, index) => {
        // 헤딩 처리
        if (line.startsWith('### ')) {
          return <h3 key={index} className="text-lg font-semibold text-white mt-4 mb-2">{line.substring(4)}</h3>;
        }
        if (line.startsWith('## ')) {
          return <h2 key={index} className="text-xl font-bold text-white mt-4 mb-2">{line.substring(3)}</h2>;
        }
        if (line.startsWith('# ')) {
          return <h1 key={index} className="text-2xl font-bold text-white mt-4 mb-2">{line.substring(2)}</h1>;
        }
        
        // 리스트 처리
        if (line.startsWith('- ')) {
          return <li key={index} className="text-gray-200 ml-4 list-disc">{line.substring(2)}</li>;
        }
        
        // 코드 블록 처리
        if (line.startsWith('```')) {
          return <div key={index} className="bg-gray-800 p-3 rounded-lg font-mono text-sm text-green-400 mt-2 mb-2 border border-gray-700">{line.substring(3)}</div>;
        }
        
        // 인용구 처리
        if (line.startsWith('> ')) {
          return <blockquote key={index} className="border-l-4 border-blue-500 pl-4 italic text-blue-200 my-2">{line.substring(2)}</blockquote>;
        }
        
        // 굵은 글씨 처리
        if (line.includes('**')) {
          const parts = line.split('**');
          return (
            <p key={index} className="text-gray-200 mb-2">
              {parts.map((part, partIndex) => 
                partIndex % 2 === 1 ? <strong key={partIndex} className="font-bold text-white">{part}</strong> : part
              )}
            </p>
          );
        }
        
        // 빈 줄
        if (line.trim() === '') {
          return <br key={index} />;
        }
        
        // 일반 텍스트
        return <p key={index} className="text-gray-200 mb-2">{line}</p>;
      });
    };
  }, []);

  // 타임스탬프 포맷팅
  const formatTimestamp = (timestamp: Date | number) => {
    const date = typeof timestamp === 'number' ? new Date(timestamp) : timestamp;
    return date.toLocaleTimeString();
  };

  // 카드 크기에 따른 스타일 조정
  const getMessageCardClasses = () => {
    switch (mainPageLayout.cardSize) {
      case 'large':
        return 'p-6 mb-6';
      case 'compact':
        return 'p-4 mb-4';
      case 'minimal':
        return 'p-3 mb-3';
      default:
        return 'p-5 mb-5';
    }
  };

  const messageCardClasses = getMessageCardClasses();

  return (
    <motion.div 
      className="flex-1 overflow-y-auto p-6 space-y-4"
      variants={staggerContainerVariants}
      initial="initial"
      animate="animate"
    >
      <AnimatePresence>
        {Array.isArray(messages) && messages.length > 0 ? messages.map((message) => (
          <motion.div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} w-full`}
            variants={staggerItemVariants}
            layout
            exit={{ opacity: 0, x: message.role === 'user' ? 100 : -100, scale: 0.8 }}
            transition={{ duration: 0.3 }}
          >
          <div className={`max-w-4xl w-full ${message.role === 'user' ? 'ml-16' : 'mr-16'}`}>
            <Card className={`${messageCardClasses} ${
              message.role === 'user' 
                ? 'bg-blue-600/20 border-blue-500/30' 
                : 'bg-gray-800/80 border-gray-600/50'
            } backdrop-blur-sm`}>
              
              {/* 메시지 헤더 */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  {message.role === 'user' ? (
                    <User className="h-4 w-4 text-blue-400" />
                  ) : (
                    <Bot className="h-4 w-4 text-green-400" />
                  )}
                  
                  <span className="text-sm font-medium text-white">
                    {message.role === 'user' ? '사용자' : 'GAIA-BT'}
                  </span>
                  
                  {/* 모드 및 프롬프트 타입 표시 */}
                  {message.role === 'assistant' && (
                    <div className="flex items-center space-x-2">
                      {message.mode === 'deep_research' && (
                        <Badge variant="outline" className="text-green-400 border-green-500 text-xs">
                          <Database className="h-2 w-2 mr-1" />
                          Deep Research
                        </Badge>
                      )}
                      
                      {message.prompt_type && message.prompt_type !== 'default' && (
                        <Badge variant="outline" className="text-blue-400 border-blue-500 text-xs">
                          {message.prompt_type === 'clinical' && '🏥 임상'}
                          {message.prompt_type === 'research' && '🔬 연구'}
                          {message.prompt_type === 'chemistry' && '⚗️ 화학'}
                          {message.prompt_type === 'regulatory' && '📋 규제'}
                        </Badge>
                      )}
                      
                      {message.enhanced && (
                        <Badge variant="outline" className="text-yellow-400 border-yellow-500 text-xs">
                          <CheckCircle className="h-2 w-2 mr-1" />
                          Enhanced
                        </Badge>
                      )}
                    </div>
                  )}
                </div>
                
                {/* 타임스탬프 및 상태 */}
                <div className="flex items-center space-x-2">
                  {message.processing && (
                    <Loader2 className="h-3 w-3 animate-spin text-blue-400" />
                  )}
                  
                  {message.error && (
                    <AlertCircle className="h-3 w-3 text-red-400" />
                  )}
                  
                  <div className="flex items-center space-x-1 text-xs text-gray-400">
                    <Clock className="h-3 w-3" />
                    <span>{formatTimestamp(message.timestamp)}</span>
                  </div>
                </div>
              </div>
              
              {/* 메시지 콘텐츠 */}
              <div className="prose prose-invert max-w-none">
                {message.content ? (
                  <div className="whitespace-pre-wrap">
                    {renderMessageContent(message.content)}
                  </div>
                ) : message.processing ? (
                  <div className="flex items-center space-x-2 text-gray-400">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>응답 생성 중...</span>
                  </div>
                ) : (
                  <div className="text-gray-400">메시지를 기다리는 중...</div>
                )}
                
                {/* 스트리밍 인디케이터 */}
                {message.streaming && (
                  <div className="inline-block w-2 h-4 bg-blue-400 animate-pulse ml-1"></div>
                )}
              </div>
              
              {/* 소스 및 에러 정보 */}
              {message.sources && Array.isArray(message.sources) && message.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-600">
                  <div className="text-xs text-gray-400 mb-1">검색 소스:</div>
                  <div className="flex flex-wrap gap-1">
                    {message.sources.map((source, index) => (
                      <Badge key={index} variant="outline" className="text-xs text-gray-300 border-gray-500">
                        {source}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {message.error && (
                <div className="mt-3 pt-3 border-t border-red-600/30">
                  <div className="flex items-center space-x-2 text-red-400 text-sm">
                    <AlertCircle className="h-4 w-4" />
                    <span>오류: {message.error}</span>
                  </div>
                </div>
              )}
            </Card>
          </div>
        </motion.div>
      )) : (
        <motion.div 
          className="flex-1 flex items-center justify-center"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="text-center text-gray-400">
            <motion.div 
              className="text-lg mb-2"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              💬
            </motion.div>
            <div>메시지가 없습니다. 대화를 시작해보세요!</div>
          </div>
        </motion.div>
      )}
      </AnimatePresence>
      
      {/* 스크롤 앵커 */}
      <div ref={messagesEndRef} />
    </motion.div>
  );
}