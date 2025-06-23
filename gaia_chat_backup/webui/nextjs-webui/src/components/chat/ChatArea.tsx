'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChatStore } from '@/store/chatStore';
import WelcomeSection from './WelcomeSection';
import MessageArea from './MessageArea';
import InputArea from './InputArea';
import { pageVariants, staggerContainerVariants } from '@/utils/animations';

interface ChatAreaProps {
  layoutConfig?: {
    mode: 'compact' | 'normal' | 'spacious';
    density: 'compact' | 'normal' | 'comfortable';
    fontSize: 'small' | 'medium' | 'large';
    gridConfig: {
      columns: number;
      gap: string;
      containerWidth: string;
      padding: string;
    };
  };
}

export default function ChatArea({ layoutConfig }: ChatAreaProps) {
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { 
    currentSessionId, 
    sessions, 
    sendMessage,
    isTyping 
  } = useChatStore();
  
  const currentSession = currentSessionId ? sessions[currentSessionId] : null;
  const messages = currentSession?.messages || [];

  // 메시지 자동 스크롤
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // 메시지 전송 핸들러
  const handleSendMessage = async () => {
    if (!input.trim() || !currentSessionId || isProcessing) return;
    
    setIsProcessing(true);
    const messageText = input.trim();
    setInput('');
    
    try {
      await sendMessage(currentSessionId, messageText);
    } catch (error) {
      console.error('메시지 전송 실패:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  // 추천 질문 핸들러
  const handleSuggestedQuestion = async (question: string) => {
    if (!currentSessionId || isProcessing) return;
    
    setIsProcessing(true);
    
    try {
      await sendMessage(currentSessionId, question);
    } catch (error) {
      console.error('추천 질문 전송 실패:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <motion.div 
      className="flex flex-col h-full bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900"
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      {/* 메인 채팅 영역 */}
      <motion.div 
        className="flex-1 flex flex-col min-h-0"
        variants={staggerContainerVariants}
        initial="initial"
        animate="animate"
      >
        
        {/* 환영 섹션과 메시지 영역 전환 애니메이션 */}
        <AnimatePresence mode="wait">
          {messages.length === 0 ? (
            <motion.div
              key="welcome"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="flex-1"
            >
              <WelcomeSection 
                onSuggestedQuestion={handleSuggestedQuestion}
                layoutConfig={layoutConfig}
                isProcessing={isProcessing}
              />
            </motion.div>
          ) : (
            <motion.div
              key="messages"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="flex-1"
            >
              <MessageArea 
                messages={messages}
                layoutConfig={layoutConfig}
                messagesEndRef={messagesEndRef}
              />
            </motion.div>
          )}
        </AnimatePresence>
        
        {/* 입력 영역 - 항상 하단에 고정 */}
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <InputArea
            input={input}
            setInput={setInput}
            onSendMessage={handleSendMessage}
            isProcessing={isProcessing || isTyping}
            layoutConfig={layoutConfig}
          />
        </motion.div>
      </motion.div>
    </motion.div>
  );
}