'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Conversation, Message, ChatContextType } from '@/types/chat';
import { getApiUrl } from '@/config/api';

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

// 기본 설정
const DEFAULT_MODEL = 'gemma3-12b:latest';
const DEFAULT_MODE = 'normal';

export const ChatProvider = ({ children }: ChatProviderProps) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState('gaia_gpt_web_' + Date.now());
  
  // 시스템 상태
  const [currentModel, setCurrentModel] = useState(DEFAULT_MODEL);
  const [currentMode, setCurrentMode] = useState(DEFAULT_MODE);
  const [mcpEnabled, setMcpEnabled] = useState(false);
  const [currentPromptType, setCurrentPromptType] = useState('default');
  
  // 로딩 상태 (각 작업별로 분리)
  const [isModelChanging, setIsModelChanging] = useState(false);
  const [isModeChanging, setIsModeChanging] = useState(false);
  const [isPromptChanging, setIsPromptChanging] = useState(false);
  
  // AbortController 관리
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  
  // 진행 중인 요청 정리 함수
  const cleanupPendingRequests = async () => {
    try {
      if (abortController && !abortController.signal.aborted) {
        console.log('이전 요청 정리 중...');
        abortController.abort('사용자 요청으로 정리됨');
        setAbortController(null);
        await new Promise(resolve => setTimeout(resolve, 200));
      }
    } catch (error: unknown) {
      if (error instanceof Error) {
        if (error.name !== 'AbortError') {
          console.error('요청 정리 중 오류 발생:', error);
        }
      } else {
        console.error('요청 정리 중 알 수 없는 오류 발생:', error);
      }
    } finally {
      setIsWaitingForResponse(false);
      setWaitingTimer(0);
    }
  };
  
  // 대기 상태 관리
  const [waitingTimer, setWaitingTimer] = useState<number>(0);
  const [isWaitingForResponse, setIsWaitingForResponse] = useState<boolean>(false);
  
  // 스트리밍 응답 처리
  const [streamingResponse, setStreamingResponse] = useState<string>('');
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  
  // 간단한 스트리밍 메시지 전송 함수
  const sendStreamingMessage = async (content: string): Promise<void> => {
    if (!content.trim()) return;

    try {
      setIsLoading(true);
      setError(null);
      setIsStreaming(true);
      setStreamingResponse('');
      
      // 기존 요청 취소
      await cleanupPendingRequests();
      
      // 새로운 AbortController 생성
      const controller = new AbortController();
      setAbortController(controller);
      
      // 메시지 히스토리 구성
      const conversationHistory = currentConversation?.messages.map(msg => ({
        role: msg.role,
        content: msg.content
      })) || [];
      
      // 스트리밍 요청 시작
      const response = await fetch(getApiUrl('/api/chat/stream'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          session_id: sessionId,
          conversation_history: conversationHistory,
        }),
        signal: controller.signal,
      });
      
      if (!response.ok) {
        throw new Error(`스트리밍 요청 실패: ${response.status}`);
      }
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) {
        throw new Error('응답 스트림을 읽을 수 없습니다');
      }
      
      let fullResponse = '';
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            
            if (data === '[DONE]') {
              // 스트리밍 완료
              setIsStreaming(false);
              
              // 메시지를 대화에 추가
              if (fullResponse.trim()) {
                addMessageToConversation(content, fullResponse.trim());
              }
              
              setStreamingResponse('');
              break;
            } else if (data.trim()) {
              // 청크 데이터 누적
              fullResponse += data;
              setStreamingResponse(fullResponse);
            }
          }
        }
        
        if (controller.signal.aborted) {
          break;
        }
      }
      
    } catch (error: unknown) {
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          console.log('스트리밍 요청이 취소되었습니다');
        } else {
          console.error('스트리밍 오류:', error);
          setError(`메시지 전송 실패: ${error.message}`);
        }
      } else {
        setError('알 수 없는 오류가 발생했습니다');
      }
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
      setAbortController(null);
    }
  };

  // 간단한 세션 초기화 함수 (연결 체크 없음)
  const [sessionInitialized, setSessionInitialized] = useState(false);
  
  const ensureSession = async () => {
    if (sessionInitialized) {
      return true;
    }
    
    try {
      console.log('세션 초기화:', sessionId);
      setSessionInitialized(true);
      return true;
    } catch (error: unknown) {
      console.error('세션 초기화 실패:', error);
      return false;
    }
  };

  // 대화에 메시지 추가
  const addMessageToConversation = (userMessage: string, assistantResponse: string) => {
    const conversationId = currentConversation?.id || '';
    
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
      timestamp: new Date(),
      conversationId,
    };

    const assistantMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: assistantResponse,
      timestamp: new Date(),
      conversationId,
    };

    if (currentConversation) {
      const updatedConversation = {
        ...currentConversation,
        messages: [...currentConversation.messages, userMsg, assistantMsg],
        lastMessage: assistantMsg,
        updatedAt: new Date(),
      };

      setCurrentConversation(updatedConversation);
      setConversations(prev => 
        prev.map(conv => conv.id === updatedConversation.id ? updatedConversation : conv)
      );
    } else {
      // 새 대화 생성
      const newConversation: Conversation = {
        id: Date.now().toString(),
        title: userMessage.slice(0, 50) + (userMessage.length > 50 ? '...' : ''),
        messages: [userMsg, assistantMsg],
        lastMessage: assistantMsg,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      setCurrentConversation(newConversation);
      setConversations(prev => [newConversation, ...prev]);
    }
  };

  // 메시지 전송 함수
  const sendMessage = async (content: string): Promise<void> => {
    await ensureSession();
    await sendStreamingMessage(content);
  };

  // 새 대화 시작
  const startNewConversation = () => {
    // 새로운 빈 대화 생성
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: '새 대화',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    setCurrentConversation(newConversation);
    setConversations(prev => [newConversation, ...prev]);
    setError(null);
  };

  // 대화 선택
  const selectConversation = (conversationId: string) => {
    if (!conversationId) {
      // 빈 ID인 경우 환영 페이지로 이동 (currentConversation을 null로 설정)
      setCurrentConversation(null);
      setError(null);
      return;
    }
    
    const conversation = conversations.find(conv => conv.id === conversationId);
    if (conversation) {
      setCurrentConversation(conversation);
      setError(null);
    }
  };

  // 대화 삭제
  const deleteConversation = (conversationId: string) => {
    setConversations(prev => prev.filter(conv => conv.id !== conversationId));
    if (currentConversation?.id === conversationId) {
      setCurrentConversation(null);
    }
  };

  // 모델 변경
  const changeModel = async (modelName: string): Promise<boolean> => {
    try {
      setIsModelChanging(true);
      setCurrentModel(modelName);
      return true;
    } catch (error: unknown) {
      console.error('모델 변경 실패:', error);
      return false;
    } finally {
      setIsModelChanging(false);
    }
  };

  // 모드 변경
  const changeMode = async (mode: string): Promise<boolean> => {
    try {
      setIsModeChanging(true);
      setCurrentMode(mode);
      setMcpEnabled(mode === 'deep_research');
      return true;
    } catch (error: unknown) {
      console.error('모드 변경 실패:', error);
      return false;
    } finally {
      setIsModeChanging(false);
    }
  };

  // 프롬프트 변경
  const changePrompt = async (promptType: string): Promise<boolean> => {
    try {
      setIsPromptChanging(true);
      setCurrentPromptType(promptType);
      return true;
    } catch (error: unknown) {
      console.error('프롬프트 변경 실패:', error);
      return false;
    } finally {
      setIsPromptChanging(false);
    }
  };

  // 컴포넌트 마운트 시 세션 초기화
  useEffect(() => {
    ensureSession();
  }, [ensureSession]);

  const value: ChatContextType = {
    // 대화 상태
    conversations,
    currentConversation,
    isLoading,
    error,
    sessionId,
    
    // 시스템 상태
    currentModel,
    currentMode,
    mcpEnabled,
    currentPromptType,
    
    // 로딩 상태
    isModelChanging,
    isModeChanging,
    isPromptChanging,
    
    // 스트리밍 상태
    isStreaming,
    streamingResponse,
    isConnecting: false,
    
    // 액션
    sendMessage,
    startNewConversation,
    selectConversation,
    deleteConversation,
    changeModel,
    changeMode,
    changePrompt,
    resetSession: () => {}, // 기본 구현
    
    // 대기 상태
    isWaitingForResponse,
    waitingTimer,
    
    // 연결 상태 (항상 true로 설정)
    isConnected: true,
    reconnectAttempts: 0,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};