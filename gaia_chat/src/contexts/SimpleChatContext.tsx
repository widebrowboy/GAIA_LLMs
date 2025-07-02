'use client';

import React, { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react';
import { Conversation, Message, ChatContextType } from '@/types/chat';
import { apiClient } from '@/utils/apiClient';

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

// 기본 설정 (로컬 스토리지에서 사용자 설정을 불러오거나 기본값 사용)
const getDefaultModel = (): string => {
  if (typeof window !== 'undefined') {
    const savedDefaultModel = localStorage.getItem('gaia_default_model');
    if (savedDefaultModel) {
      console.log(`📋 저장된 기본 모델 불러오기: ${savedDefaultModel}`);
      return savedDefaultModel;
    }
  }
  return 'gemma3-12b:latest';
};

const DEFAULT_MODEL = getDefaultModel();
const DEFAULT_MODE = 'normal';

// 기본 모델 자동 시작 함수 (최신 기본 모델 설정 반영)
const ensureDefaultModel = async () => {
  try {
    const currentDefault = getDefaultModel(); // 항상 최신 기본 모델 사용
    console.log(`🔄 기본 모델 확인 및 시작: ${currentDefault}`);
    const result = await apiClient.switchModelSafely(currentDefault);
    if (result.success) {
      console.log(`✅ 기본 모델 시작 완료: ${currentDefault}`);
      return true;
    } else {
      console.warn(`⚠️ 기본 모델 시작 실패: ${result.error}`);
      return false;
    }
  } catch (error) {
    console.error(`❌ 기본 모델 시작 오류:`, error);
    return false;
  }
};

export const SimpleChatProvider = ({ children }: ChatProviderProps) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingResponse, setStreamingResponse] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  
  // Context 상태 관리
  const [currentModel, setCurrentModel] = useState<string>(DEFAULT_MODEL);
  const [currentMode, setCurrentMode] = useState<string>(DEFAULT_MODE);
  const [mcpEnabled, setMcpEnabled] = useState(false);
  const [currentPromptType, setCurrentPromptType] = useState<string>('default');
  const [isModelChanging, setIsModelChanging] = useState(false);
  const [isModeChanging, setIsModeChanging] = useState(false);
  const [isPromptChanging, setIsPromptChanging] = useState(false);

  // 제어 참조
  const abortControllerRef = useRef<AbortController | null>(null);

  // 초기화 및 기본 모델 설정
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        // 로컬 스토리지에서 대화 목록 로드
        const savedConversations = localStorage.getItem('gaia_gpt_conversations');
        if (savedConversations) {
          const parsed = JSON.parse(savedConversations);
          if (Array.isArray(parsed)) {
            setConversations(parsed);
            
            // 가장 최근 대화를 현재 대화로 설정
            if (parsed.length > 0) {
              setCurrentConversation(parsed[0]);
            }
          }
        }
        
        // 기본 모델 자동 시작
        const initializeDefaultModel = async () => {
          console.log('🚀 페이지 로드 시 기본 모델 초기화 시작');
          
          // 최신 기본 모델 설정을 가져와서 Context 상태 설정
          const currentDefault = getDefaultModel();
          setCurrentModel(currentDefault);
          console.log(`📝 currentModel 상태를 최신 기본값으로 설정: ${currentDefault}`);
          
          // 3초 지연 후 기본 모델 시작 (서버 안정화 대기)
          setTimeout(async () => {
            const success = await ensureDefaultModel();
            if (success) {
              console.log('✅ 기본 모델 초기화 완료');
            } else {
              console.warn('⚠️ 기본 모델 초기화 실패 - 수동 시작 필요');
            }
          }, 3000);
        };
        
        initializeDefaultModel();
      } catch (error) {
        console.error('초기화 중 오류:', error);
      }
    }
  }, []);

  // 대화 히스토리 저장
  const saveConversations = (conversations: Conversation[]) => {
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem('gaia_gpt_conversations', JSON.stringify(conversations));
      } catch (error) {
        console.error('대화 저장 실패:', error);
      }
    }
  };

  // 새 대화 생성
  const createConversation = (): Conversation => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: '새 대화',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };
    
    setConversations(prev => {
      const updated = [newConversation, ...prev];
      saveConversations(updated);
      return updated;
    });
    
    setCurrentConversation(newConversation);
    return newConversation;
  };

  // 새 대화 시작
  const startNewConversation = async () => {
    const newConversation = createConversation();
    setCurrentConversation(newConversation);
    
    // 스트리밍 상태 초기화
    setIsLoading(false);
    setIsStreaming(false);
    setStreamingResponse('');
    setIsConnecting(false);
    setError(null);
    
    // 새 연구 시작 시 기본 모델 확인 및 설정
    console.log('🆕 새 연구 시작 - 기본 모델 확인 중...');
    try {
      // 최신 기본 모델 설정을 가져와서 Context 상태 재설정
      const currentDefault = getDefaultModel();
      setCurrentModel(currentDefault);
      console.log(`📝 새 연구 시 currentModel 상태를 최신 기본값으로 재설정: ${currentDefault}`);
      
      // 기본 모델이 실행 중인지 확인하고 필요시 시작
      const success = await ensureDefaultModel();
      if (success) {
        console.log('✅ 새 연구 시 기본 모델 설정 완료');
      } else {
        console.warn('⚠️ 새 연구 시 기본 모델 설정 실패');
      }
    } catch (error) {
      console.error('❌ 새 연구 시 모델 설정 오류:', error);
    }
  };

  // 대화 선택
  const selectConversation = (conversationId: string) => {
    if (!conversationId) {
      // 빈 ID면 홈으로 (현재 대화 해제)
      setCurrentConversation(null);
      return;
    }
    
    const conversation = conversations.find(c => c.id === conversationId);
    if (conversation) {
      setCurrentConversation(conversation);
      
      // 스트리밍 상태 초기화
      setIsLoading(false);
      setIsStreaming(false);
      setStreamingResponse('');
      setIsConnecting(false);
      setError(null);
    }
  };

  // 대화 삭제
  const deleteConversation = (conversationId: string) => {
    setConversations(prev => {
      const updated = prev.filter(c => c.id !== conversationId);
      saveConversations(updated);
      
      // 삭제된 대화가 현재 대화라면 다른 대화로 전환
      if (currentConversation?.id === conversationId) {
        if (updated.length > 0) {
          setCurrentConversation(updated[0]);
        } else {
          setCurrentConversation(null);
        }
      }
      
      return updated;
    });
  };

  // 대화 제목 자동 생성
  const generateConversationTitle = (message: string): string => {
    let title = message.trim();
    
    // 만약 메시지가 35자보다 길면 30자로 자르고 말줄임표 추가
    if (title.length > 35) {
      title = title.substring(0, 30) + '...';
    } else if (title.length < 5) { // 너무 짧으면 기본 제목 사용
      return '새 대화';
    }
    
    return title;
  };

  // 메시지 전송 함수 - 스트리밍 상태 관리 및 응답 전체 수신 보장 개선
  const sendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return;

    // 이전 요청 정리
    await cleanupPendingRequests();

    // 현재 대화가 없으면 새로 생성
    let conversation = currentConversation;
    if (!conversation) {
      conversation = await createConversation();
    }

    // 사용자 메시지 추가
    const userMessage: Message = {
      id: 'user_' + Date.now(),
      role: 'user',
      content: message,
      timestamp: new Date()
    };

    // 대화 제목이 '새 대화'라면 첫 메시지로 업데이트
    if (conversation.title === '새 대화') {
      conversation.title = generateConversationTitle(message);
    }

    // 대화에 사용자 메시지 추가
    const updatedConversation = {
      ...conversation,
      messages: [...conversation.messages, userMessage],
      updatedAt: new Date()
    };

    // 상태 업데이트
    setCurrentConversation(updatedConversation);
    
    // 대화 목록 업데이트 (가장 최근 대화를 맨 위로)
    if (conversations.length > 0) {
      const updatedConversations = conversations.map(c => 
        c.id === updatedConversation.id ? updatedConversation : c
      );
      
      // 현재 대화를 맨 위로 이동
      const reorderedConversations = [
        updatedConversation,
        ...updatedConversations.filter(c => c.id !== updatedConversation.id)
      ];
      
      setConversations(reorderedConversations);
      
      // 로컬 스토리지 업데이트
      if (typeof window !== 'undefined') {
        localStorage.setItem('gaia_gpt_conversations', JSON.stringify(reorderedConversations));
      }
    }

    setIsLoading(true);
    setError(null);
    
    // 스트리밍 상태 초기화
    setIsStreaming(true);
    setStreamingResponse(''); // 이전 스트리밍 응답 클리어
    setIsConnecting(true);

    // 새로운 AbortController 생성
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const startTime = Date.now();
      console.log('📡 API 호출 시작:', message.substring(0, 50) + '...');
      
      // 타임아웃 설정 (2분으로 복원)
      const timeoutId = setTimeout(() => {
        if (!controller.signal.aborted) {
          console.warn('⚠️ API 요청 타임아웃 발생 (2분 초과)');
          console.warn(`경과 시간: ${(Date.now() - startTime) / 1000}초`);
          controller.abort(new DOMException('Request timeout', 'AbortError'));
        }
      }, 120000); // 2분으로 복원
      
      console.log('🔄 스트리밍 요청 준비:', {
        url: `${API_BASE_URL}/api/chat/stream`,
        message: message.substring(0, 50),
        sessionId
      });

      console.log('⏰ fetch 요청 시작 - 타임스탬프:', new Date().toISOString());
      console.log('🌐 요청 URL 검증:', `${API_BASE_URL}/api/chat/stream`);
      const requestBody = {
        message: message,
        session_id: sessionId,
        complete_response: true,
        stream: true,
        mode: currentMode, // 현재 모드 정보 추가
        mcp_enabled: mcpEnabled, // MCP 활성화 상태 추가
        // model: currentModel // 제거: 자동 모델 전환 방지를 위해 모델 필드 전송하지 않음
      };
      
      console.log('🏗️ 요청 body:', JSON.stringify(requestBody));
      console.log('🎭 현재 모드:', currentMode, 'MCP 활성화:', mcpEnabled);
      
      // 서버 준비 대기 및 안정성 확인
      console.log('🔄 서버 연결 상태 확인...');
      try {
        // 먼저 서버 health check
        const healthResult = await apiClient.checkHealth();
        if (!healthResult.success) {
          throw new Error('서버 상태 확인 실패');
        }
        console.log('✅ 서버 상태 정상');
      } catch (healthError) {
        console.warn('⚠️ 서버 상태 확인 실패, 그래도 요청 진행:', healthError);
      }
      
      // 기본 fetch로 스트리밍 요청 (단순화)
      let response: Response;
      try {
        console.log('🔄 스트리밍 요청 시작');
        response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
          },
          signal: controller.signal,
          body: JSON.stringify(requestBody)
        });
        
        console.log('✅ fetch 요청 성공:', response.status, response.statusText);
      } catch (fetchError) {
        console.error('❌ fetch 요청 실패:', fetchError);
        
        // 사용자에게 명확한 에러 메시지 표시
        setError('서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.');
        setIsLoading(false);
        setIsStreaming(false);
        setIsConnecting(false);
        
        // 더 이상 진행하지 않고 종료
        return;
      }
      
      // 응답 상태 확인
      
      clearTimeout(timeoutId);
      
      // 연결 완료
      setIsConnecting(false);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('스트리밍 응답 오류:', response.status, response.statusText, errorText);
        throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
      }

      if (response.ok) {
        // 스트리밍 응답 처리 단순화
        const reader = response.body?.getReader();
        const decoder = new TextDecoder('utf-8');
        
        if (!reader) {
          throw new Error('응답 스트림을 읽을 수 없습니다');
        }

        let fullResponse = '';
        let buffer = '';

        try {
          console.log('📖 스트리밍 응답 읽기 시작');
          
          while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
              console.log('✅ 스트리밍 완료');
              break;
            }

            // 새로운 청크를 버퍼에 추가
            buffer += decoder.decode(value, { stream: true });
            
            // 완료된 라인들을 처리
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // 마지막 불완전한 라인은 버퍼에 보관
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6); // 'data: ' 제거
                
                if (data === '[DONE]') {
                  console.log('🏁 [DONE] 신호 수신');
                  break;
                }
                
                try {
                  // JSON 파싱 시도
                  const parsedData = JSON.parse(data);
                  console.log('📥 스트리밍 데이터:', parsedData);
                  
                  if (typeof parsedData === 'string') {
                    fullResponse += parsedData;
                    setStreamingResponse(fullResponse);
                  }
                } catch (parseError) {
                  // JSON이 아닌 경우 직접 텍스트로 처리
                  console.log('📥 스트리밍 텍스트:', data);
                  fullResponse += data;
                  setStreamingResponse(fullResponse);
                }
              }
            }
          }
        } finally {
          reader.releaseLock();
        }

        console.log('📝 최종 응답 길이:', fullResponse.length);
        
        // 스트리밍 상태 종료
        setIsStreaming(false);
        setIsLoading(false);

        // AI 응답 메시지 생성
        const aiMessage: Message = {
          id: 'ai_' + Date.now(),
          role: 'assistant',
          content: fullResponse,
          timestamp: new Date()
        };

        // 대화에 AI 응답 추가
        const finalConversation = {
          ...updatedConversation,
          messages: [...updatedConversation.messages, aiMessage],
          updatedAt: new Date()
        };

        setCurrentConversation(finalConversation);
        
        // 대화 목록 업데이트
        setConversations(prev => {
          const updated = prev.map(c => 
            c.id === finalConversation.id ? finalConversation : c
          );
          saveConversations(updated);
          return updated;
        });

        console.log('✅ 메시지 전송 완료');
      }
    } catch (error) {
      console.error('💥 sendMessage 오류:', error);
      
      setIsLoading(false);
      setIsStreaming(false);
      setIsConnecting(false);
      
      if (error instanceof Error && error.name === 'AbortError') {
        setError('요청이 취소되었습니다.');
      } else {
        setError(`오류가 발생했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
      }
    }
  };

  // 요청 정리 함수
  const cleanupPendingRequests = async () => {
    if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
      console.log('🧹 이전 요청 정리');
      abortControllerRef.current.abort();
    }
    
    // 상태 정리
    setIsLoading(false);
    setIsStreaming(false);
    setIsConnecting(false);
  };

  // 세션 ID (현재는 대화 ID 사용)
  const sessionId = currentConversation?.id || 'default';

  // 모델 변경 함수
  const changeModel = async (modelName: string) => {
    setIsModelChanging(true);
    try {
      console.log(`🔄 모델 변경 요청: ${modelName}`);
      
      // API를 통해 실제로 모델 변경
      const response = await apiClient.xhrFetch(`/api/system/models/switch/${encodeURIComponent(modelName)}`, 'POST');
      
      if (response.data && response.data.success) {
        setCurrentModel(modelName);
        console.log(`✅ 모델 변경 완료: ${modelName}`);
        
        // 시스템 상태 새로고침
        await refreshSystemStatus();
      } else {
        throw new Error(response.data?.error || '모델 변경 실패');
      }
    } catch (error) {
      console.error('❌ 모델 변경 실패:', error);
      throw error;
    } finally {
      setIsModelChanging(false);
    }
  };

  // 모드 변경 함수
  const changeMode = async (mode: string) => {
    setIsModeChanging(true);
    try {
      console.log(`🔄 모드 변경 요청: ${mode}`);
      setCurrentMode(mode);
      setMcpEnabled(mode === 'deep_research');
      console.log(`✅ 모드 변경 완료: ${mode}`);
    } catch (error) {
      console.error('❌ 모드 변경 실패:', error);
      throw error;
    } finally {
      setIsModeChanging(false);
    }
  };

  // 프롬프트 변경 함수
  const changePrompt = async (promptType: string) => {
    setIsPromptChanging(true);
    try {
      console.log(`🔄 프롬프트 변경 요청: ${promptType}`);
      setCurrentPromptType(promptType);
      console.log(`✅ 프롬프트 변경 완료: ${promptType}`);
    } catch (error) {
      console.error('❌ 프롬프트 변경 실패:', error);
      throw error;
    } finally {
      setIsPromptChanging(false);
    }
  };

  // 시스템 상태 새로고침 함수
  const refreshSystemStatus = async () => {
    try {
      console.log('🔄 시스템 상태 새로고침');
      // 여기에 실제 시스템 상태 업데이트 로직 추가
      console.log('✅ 시스템 상태 새로고침 완료');
    } catch (error) {
      console.error('❌ 시스템 상태 새로고침 실패:', error);
    }
  };

  // 기본 모델 변경 함수
  const changeDefaultModel = async (newDefaultModel: string) => {
    try {
      console.log(`🔧 기본 모델 변경 요청: ${newDefaultModel}`);
      
      // 로컬 스토리지에 새로운 기본 모델 저장
      if (typeof window !== 'undefined') {
        localStorage.setItem('gaia_default_model', newDefaultModel);
        console.log(`💾 새로운 기본 모델 저장됨: ${newDefaultModel}`);
      }
      
      // 현재 Context 상태도 즉시 업데이트
      setCurrentModel(newDefaultModel);
      console.log(`📝 currentModel 상태 업데이트: ${newDefaultModel}`);
      
      // 새로운 기본 모델 실행
      const success = await apiClient.switchModelSafely(newDefaultModel);
      if (success && success.success) {
        console.log(`✅ 기본 모델 전환 완료: ${newDefaultModel}`);
        return { success: true, message: `기본 모델이 '${newDefaultModel}'로 변경되었습니다.` };
      } else {
        console.warn(`⚠️ 기본 모델 전환 실패: ${success?.error || 'Unknown error'}`);
        return { success: false, error: success?.error || '모델 전환 실패' };
      }
    } catch (error) {
      console.error('❌ 기본 모델 변경 실패:', error);
      return { success: false, error: error instanceof Error ? error.message : '알 수 없는 오류' };
    }
  };

  // 현재 기본 모델 조회 함수
  const getCurrentDefaultModel = (): string => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('gaia_default_model') || 'gemma3-12b:latest';
    }
    return 'gemma3-12b:latest';
  };

  return (
    <ChatContext.Provider value={{
      conversations,
      currentConversation,
      isLoading,
      error,
      isStreaming,
      streamingResponse,
      startNewConversation,
      selectConversation,
      deleteConversation,
      sendMessage,
      currentModel,
      currentMode,
      mcpEnabled,
      currentPromptType,
      changeModel,
      changeMode,
      changePrompt,
      isModelChanging,
      isModeChanging,
      isPromptChanging,
      setCurrentModel,
      setCurrentMode,
      setMcpEnabled,
      setCurrentPromptType,
      refreshSystemStatus,
      changeDefaultModel,
      getCurrentDefaultModel
    }}>
      {children}
    </ChatContext.Provider>
  );
};