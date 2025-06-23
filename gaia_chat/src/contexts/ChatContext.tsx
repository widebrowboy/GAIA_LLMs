'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Conversation, Message, ChatContextType } from '@/types/chat';

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

// GAIA-BT API 서버 URL
const API_BASE_URL = 'http://localhost:8000';

// 기본 설정
const DEFAULT_MODEL = 'gemma3-12b:latest';
const DEFAULT_MODE = 'normal';

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
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

  // 세션 생성 또는 확인 + 기본 모델 설정
  const ensureSession = async () => {
    try {
      // 세션 생성
      const sessionResponse = await fetch(`${API_BASE_URL}/api/session/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
      });
      
      if (!sessionResponse.ok) {
        console.log('세션이 이미 존재하거나 생성에 실패했습니다');
      }

      // 기본 모델 설정
      try {
        await fetch(`${API_BASE_URL}/api/system/model`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            model: DEFAULT_MODEL,
            session_id: sessionId 
          }),
        });
        console.log(`기본 모델 설정: ${DEFAULT_MODEL}`);
      } catch (modelError) {
        console.warn('기본 모델 설정 실패:', modelError);
      }
      
    } catch (err) {
      console.warn('세션 생성 확인 실패:', err);
    }
  };

  // 대화 목록 새로고침 (GAIA-BT API에서는 대화 히스토리를 관리하지 않으므로 로컬에서 관리)
  const refreshConversations = async () => {
    // 로컬 스토리지에서 대화 목록 복원 (클라이언트 사이드에서만)
    if (typeof window !== 'undefined') {
      try {
        const stored = localStorage.getItem('gaia_gpt_conversations');
        if (stored) {
          const data = JSON.parse(stored);
          setConversations(data);
        }
      } catch (err) {
        console.warn('대화 목록 로드 실패:', err);
      }
    }
  };

  // 새 대화 생성
  const createConversation = async (title?: string): Promise<Conversation> => {
    try {
      setIsLoading(true);
      
      const newConversation: Conversation = {
        id: 'conv_' + Date.now(),
        title: title || '새 대화',
        messages: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      
      const updatedConversations = [newConversation, ...conversations];
      setConversations(updatedConversations);
      setCurrentConversation(newConversation);
      
      // 로컬 스토리지에 저장 (클라이언트 사이드에서만)
      if (typeof window !== 'undefined') {
        localStorage.setItem('gaia_gpt_conversations', JSON.stringify(updatedConversations));
      }
      
      return newConversation;
    } catch (err) {
      setError('Failed to create conversation');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // 대화 선택
  const selectConversation = (id: string) => {
    const conversation = conversations.find(conv => conv.id === id);
    if (conversation) {
      setCurrentConversation(conversation);
    }
  };

  // 메시지 전송
  const sendMessage = async (content: string) => {
    if (!currentConversation || isLoading) return;

    // 이전 요청이 진행 중이면 취소
    if (abortController && !abortController.signal.aborted) {
      abortController.abort();
    }

    let controller: AbortController | null = null;
    let timeoutId: NodeJS.Timeout | null = null;

    try {
      setIsLoading(true);
      setError(null);
      
      // 새로운 AbortController 생성
      controller = new AbortController();
      setAbortController(controller);
      
      // 사용자 메시지 추가
      const userMessage: Message = {
        id: 'msg_' + Date.now(),
        content,
        role: 'user',
        timestamp: new Date(),
        conversationId: currentConversation.id,
      };

      // 중단된 신호 체크
      if (controller.signal.aborted) {
        throw new Error('요청이 중단되었습니다.');
      }

      // GAIA-BT API 호출 (타임아웃 추가)
      timeoutId = setTimeout(() => {
        if (controller && !controller.signal.aborted) {
          controller.abort();
        }
      }, 30000); // 30초 타임아웃
      
      const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          session_id: sessionId,
        }),
        signal: controller.signal,
      });
      
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      setAbortController(null);

      if (response.ok) {
        const data = await response.json();
        
        // AI 응답 메시지 생성
        const assistantMessage: Message = {
          id: 'msg_' + (Date.now() + 1),
          content: data.response || '응답을 받지 못했습니다.',
          role: 'assistant',
          timestamp: new Date(),
          conversationId: currentConversation.id,
        };

        // 대화 업데이트
        const updatedConversation = {
          ...currentConversation,
          messages: [...currentConversation.messages, userMessage, assistantMessage],
          updatedAt: new Date(),
          title: currentConversation.title === '새 대화' && content.length > 0 
            ? content.length > 30 ? content.substring(0, 30) + '...' : content
            : currentConversation.title
        };

        // 대화 목록 업데이트
        const updatedConversations = conversations.map(conv =>
          conv.id === currentConversation.id ? updatedConversation : conv
        );

        setCurrentConversation(updatedConversation);
        setConversations(updatedConversations);
        
        // 로컬 스토리지에 저장 (클라이언트 사이드에서만)
        if (typeof window !== 'undefined') {
          localStorage.setItem('gaia_gpt_conversations', JSON.stringify(updatedConversations));
        }
        
      } else {
        throw new Error(`API 오류: ${response.status}`);
      }
    } catch (err) {
      let errorMsg = '메시지 전송에 실패했습니다.';
      
      if (err instanceof Error) {
        if (err.name === 'AbortError') {
          console.log('메시지 전송이 취소되었습니다.');
          return; // AbortError는 UI에 표시하지 않음
        } else if (err.message.includes('NetworkError') || err.message.includes('fetch')) {
          errorMsg = '네트워크 연결을 확인해주세요.';
        } else {
          errorMsg = `오류: ${err.message}`;
        }
      }
      
      setError(errorMsg);
      console.error('메시지 전송 오류:', err);
      
      // AbortError가 아닌 경우에만 오류 메시지 추가
      if (!(err instanceof Error && err.name === 'AbortError') && currentConversation) {
        const userMessage: Message = {
          id: 'msg_' + Date.now(),
          content,
          role: 'user',
          timestamp: new Date(),
          conversationId: currentConversation.id,
        };
        
        const errorMessage: Message = {
          id: 'msg_' + (Date.now() + 1),
          content: `❌ ${errorMsg}`,
          role: 'assistant',
          timestamp: new Date(),
          conversationId: currentConversation.id,
        };
        
        const updatedConversation = {
          ...currentConversation,
          messages: [...currentConversation.messages, userMessage, errorMessage],
          updatedAt: new Date(),
        };
        
        const updatedConversations = conversations.map(conv =>
          conv.id === currentConversation.id ? updatedConversation : conv
        );
        
        setCurrentConversation(updatedConversation);
        setConversations(updatedConversations);
        
        // 로컬 스토리지에 저장 (클라이언트 사이드에서만)
        if (typeof window !== 'undefined') {
          localStorage.setItem('gaia_gpt_conversations', JSON.stringify(updatedConversations));
        }
      }
    } finally {
      // cleanup
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      setIsLoading(false);
      setAbortController(null);
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    const initializeApp = async () => {
      await ensureSession();
      await refreshConversations();
    };
    initializeApp();
  }, []);

  // 컴포넌트 언마운트 시 진행 중인 요청 취소
  useEffect(() => {
    return () => {
      if (abortController) {
        abortController.abort();
      }
    };
  }, [abortController]);

  // 모드 전환 함수
  const toggleMode = async () => {
    if (isModeChanging || isLoading) return; // 이미 진행 중이면 무시
    
    let controller: AbortController | null = null;
    let timeoutId: NodeJS.Timeout | null = null;
    
    try {
      setIsModeChanging(true);
      setError(null);
      const newMode = currentMode === 'normal' ? 'deep_research' : 'normal';
      
      // AbortController 생성
      controller = new AbortController();
      timeoutId = setTimeout(() => {
        if (controller && !controller.signal.aborted) {
          controller.abort();
        }
      }, 15000); // 15초 타임아웃
      
      if (newMode === 'deep_research') {
        // Deep Research 모드 활성화
        const response = await fetch(`${API_BASE_URL}/api/system/mode/deep_research`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            session_id: sessionId 
          }),
          signal: controller.signal,
        });
        
        if (response.ok) {
          setCurrentMode('deep_research');
          setMcpEnabled(true);
          console.log('✅ Deep Research 모드 활성화됨');
        } else {
          throw new Error(`Deep Research 모드 전환 실패: ${response.status}`);
        }
      } else {
        // 일반 모드로 전환
        const response = await fetch(`${API_BASE_URL}/api/system/mode/normal`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            session_id: sessionId 
          }),
          signal: controller.signal,
        });
        
        if (response.ok) {
          setCurrentMode('normal');
          setMcpEnabled(false);
          console.log('✅ 일반 모드로 전환됨');
        } else {
          throw new Error(`일반 모드 전환 실패: ${response.status}`);
        }
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        console.log('모드 전환 요청이 취소되었습니다.');
        return;
      }
      console.error('모드 전환 실패:', err);
      setError('모드 전환에 실패했습니다. 다시 시도해주세요.');
    } finally {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      setIsModeChanging(false);
    }
  };

  // 모델 변경 함수
  const changeModel = async (model: string) => {
    if (isModelChanging || isLoading || model === currentModel) return; // 이미 진행 중이거나 같은 모델이면 무시
    
    let controller: AbortController | null = null;
    let timeoutId: NodeJS.Timeout | null = null;
    
    try {
      setIsModelChanging(true);
      setError(null);
      
      // AbortController 생성
      controller = new AbortController();
      timeoutId = setTimeout(() => {
        if (controller && !controller.signal.aborted) {
          controller.abort();
        }
      }, 10000); // 10초 타임아웃
      
      const response = await fetch(`${API_BASE_URL}/api/system/model`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          model,
          session_id: sessionId 
        }),
        signal: controller.signal,
      });
      
      if (response.ok) {
        setCurrentModel(model);
        console.log(`✅ 모델이 '${model}'로 변경됨`);
      } else {
        throw new Error(`모델 변경 실패: ${response.status}`);
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        console.log('모델 변경 요청이 취소되었습니다.');
        return;
      }
      console.error('모델 변경 실패:', err);
      setError('모델 변경에 실패했습니다.');
    } finally {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      setIsModelChanging(false);
    }
  };

  // 프롬프트 타입 변경 함수
  const changePromptType = async (promptType: string) => {
    if (isPromptChanging || isLoading || promptType === currentPromptType) return; // 이미 진행 중이거나 같은 프롬프트면 무시
    
    let controller: AbortController | null = null;
    let timeoutId: NodeJS.Timeout | null = null;
    
    try {
      setIsPromptChanging(true);
      setError(null);
      
      // AbortController 생성
      controller = new AbortController();
      timeoutId = setTimeout(() => {
        if (controller && !controller.signal.aborted) {
          controller.abort();
        }
      }, 10000); // 10초 타임아웃
      
      const response = await fetch(`${API_BASE_URL}/api/system/prompt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          prompt_type: promptType,
          session_id: sessionId 
        }),
        signal: controller.signal,
      });
      
      if (response.ok) {
        setCurrentPromptType(promptType);
        console.log(`✅ 프롬프트 타입이 '${promptType}'로 변경됨`);
      } else {
        throw new Error(`프롬프트 변경 실패: ${response.status}`);
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        console.log('프롬프트 변경 요청이 취소되었습니다.');
        return;
      }
      console.error('프롬프트 변경 실패:', err);
      setError('프롬프트 변경에 실패했습니다.');
    } finally {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      setIsPromptChanging(false);
    }
  };

  const value: ChatContextType = {
    conversations,
    currentConversation,
    isLoading,
    error,
    currentModel,
    currentMode,
    mcpEnabled,
    currentPromptType,
    isModelChanging,
    isModeChanging,
    isPromptChanging,
    createConversation,
    selectConversation,
    sendMessage,
    refreshConversations,
    toggleMode,
    changeModel,
    changePromptType,
    setConversations,
    setCurrentConversation,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};