'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Conversation, Message, ChatContextType } from '@/types/chat';
import { getApiUrl } from '@/config/api';

const NewChatContext = createContext<ChatContextType | undefined>(undefined);

export const useNewChatContext = () => {
  const context = useContext(NewChatContext);
  if (!context) {
    throw new Error('useNewChatContext must be used within a NewChatProvider');
  }
  return context;
};

interface NewChatProviderProps {
  children: ReactNode;
}

export const NewChatProvider = ({ children }: NewChatProviderProps) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState('webui_session');
  
  // 시스템 상태 (고정값)
  const currentModel = 'gemma3-12b:latest';
  const currentMode = 'normal';
  const mcpEnabled = false;
  const currentPromptType = 'default';
  
  // 스트리밍 상태
  const [streamingResponse, setStreamingResponse] = useState<string>('');
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [isConnecting, setIsConnecting] = useState<boolean>(false);
  
  console.log('🆕 NewChatProvider 초기화됨:', { sessionId });
  console.log('🔄 현재 상태:', { conversations: conversations.length, currentConversation: currentConversation?.id, isStreaming, streamingResponse: streamingResponse.substring(0, 50) });
  
  // 간단한 메시지 전송 함수
  const sendMessage = async (content: string): Promise<void> => {
    if (!content.trim()) return;

    console.log('📤 메시지 전송 시작:', content.substring(0, 50));
    setIsLoading(true);
    setError(null);
    setIsConnecting(true);
    setIsStreaming(false);
    setStreamingResponse('');
    
    // 사용자 메시지를 즉시 추가
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: content,
      timestamp: new Date(),
      conversationId: currentConversation?.id || '',
    };

    // 현재 대화가 없으면 새로 생성
    if (!currentConversation) {
      const newConversation: Conversation = {
        id: Date.now().toString(),
        title: content.slice(0, 50) + (content.length > 50 ? '...' : ''),
        messages: [userMessage],
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      setCurrentConversation(newConversation);
      setConversations(prev => [newConversation, ...prev]);
    } else {
      // 기존 대화에 사용자 메시지 추가
      const updatedConversation = {
        ...currentConversation,
        messages: [...currentConversation.messages, userMessage],
        updatedAt: new Date(),
      };
      setCurrentConversation(updatedConversation);
      setConversations(prev => 
        prev.map(conv => conv.id === updatedConversation.id ? updatedConversation : conv)
      );
    }

    try {
      const apiUrl = getApiUrl('/api/chat/stream');
      console.log('🌐 API 요청 시작...', { url: apiUrl, sessionId, messageLength: content.length });
      
      // Fetch API를 사용한 스트리밍 방식으로 변경 (타임아웃 및 취소 지원)
      let fullResponse = '';
      
      // AbortController로 요청 취소 지원
      const abortController = new AbortController();
      const timeoutId = setTimeout(() => {
        abortController.abort();
      }, 120000); // 2분 타임아웃
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          session_id: sessionId,
        }),
        signal: abortController.signal
      });

      console.log('📡 Fetch 응답 수신:', response.status, response.statusText);
      console.log('📋 응답 헤더:', {
        contentType: response.headers.get('content-type'),
        cacheControl: response.headers.get('cache-control'),
        connection: response.headers.get('connection'),
        transferEncoding: response.headers.get('transfer-encoding')
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ HTTP 오류 응답:', errorText);
        throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
      }

      if (!response.body) {
        console.error('❌ 응답 본문 없음');
        throw new Error('응답 본문이 없습니다');
      }

      console.log('✅ ReadableStream 확인됨:', response.body);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      try {
        let buffer = '';
        let chunkCounter = 0;
        
        console.log('🚀 ReadableStream 읽기 시작');
        
        while (true) {
          console.log(`📖 reader.read() 호출 중... (청크 ${chunkCounter + 1})`);
          
          const readResult = await reader.read();
          const { done, value } = readResult;
          
          console.log(`📋 Read 결과:`, {
            done,
            valueExists: !!value,
            valueLength: value ? value.length : 0,
            chunkNumber: chunkCounter + 1
          });
          
          if (done) {
            console.log('🏁 스트리밍 완료 (연결 종료)');
            setIsStreaming(false);
            break;
          }
          
          if (!value) {
            console.warn('⚠️ value가 없음, 다음 청크 대기');
            continue;
          }
          
          chunkCounter++;
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;
          console.log(`📥 청크 ${chunkCounter} 수신:`, {
            rawLength: value.length,
            decodedLength: chunk.length,
            preview: chunk.substring(0, 100),
            bufferLength: buffer.length
          });
          
          // 버퍼에서 완전한 라인들 처리
          const lines = buffer.split('\n');
          
          // 마지막 라인은 불완전할 수 있으므로 버퍼에 남김
          buffer = lines.pop() || '';
          
          for (const line of lines) {
            if (line.trim() && line.startsWith('data: ')) {
              const data = line.slice(6); // trim() 제거 - 공백도 중요함
              
              if (data === '[DONE]') {
                console.log('🏁 스트리밍 종료 신호 수신');
                setIsStreaming(false);
                return;
              } else if (data !== undefined) { // 빈 문자열도 허용
                // 첫 번째 데이터를 받으면 연결 완료, 스트리밍 시작
                if (!isStreaming && isConnecting) {
                  setIsConnecting(false);
                  setIsStreaming(true);
                  console.log('🚀 스트리밍 시작 - 첫 데이터 수신');
                }
                
                fullResponse += data;
                setStreamingResponse(fullResponse);
                console.log('📝 스트리밍 업데이트:', { 
                  responseLength: fullResponse.length, 
                  lastChunk: `"${data}"`, // 공백 등을 명시적으로 표시
                  fullPreview: fullResponse.substring(0, 50)
                });
              }
            }
          }
        }
        
        // 남은 버퍼 처리
        if (buffer.trim()) {
          const lines = buffer.split('\n');
          for (const line of lines) {
            if (line.trim() && line.startsWith('data: ')) {
              const data = line.slice(6); // trim() 제거
              if (data !== '[DONE]') {
                fullResponse += data;
                setStreamingResponse(fullResponse);
                console.log('📝 버퍼 처리:', { responseLength: fullResponse.length, data: `"${data}"` });
              }
            }
          }
        }
        
      } finally {
        reader.releaseLock();
      }
      
      // 스트리밍 완료 후 처리
      console.log('✅ 스트리밍 완료, 최종 응답 길이:', fullResponse.length);
      console.log('📄 최종 응답 내용:', fullResponse.substring(0, 100) + '...');
      setIsStreaming(false);
      setIsConnecting(false);
      
      // AI 응답을 대화에 추가
      if (fullResponse.trim()) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: fullResponse.trim(),
          timestamp: new Date(),
          conversationId: currentConversation?.id || '',
        };
        
        console.log('💬 AI 메시지 생성:', { id: assistantMessage.id, contentLength: assistantMessage.content.length });
        
        const updatedConversation = currentConversation ? {
          ...currentConversation,
          messages: [...currentConversation.messages, assistantMessage],
          lastMessage: assistantMessage,
          updatedAt: new Date(),
        } : {
          id: Date.now().toString(),
          title: content.slice(0, 50) + (content.length > 50 ? '...' : ''),
          messages: [userMessage, assistantMessage],
          lastMessage: assistantMessage,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        console.log('📝 대화 업데이트:', { conversationId: updatedConversation.id, messageCount: updatedConversation.messages.length });
        
        setCurrentConversation(updatedConversation);
        setConversations(prev => 
          prev.map(conv => conv.id === updatedConversation.id ? updatedConversation : conv)
        );
        
        console.log('✅ 대화 상태 업데이트 완료');
      } else {
        console.warn('⚠️ 빈 응답으로 인해 메시지가 추가되지 않음');
      }
      
      setStreamingResponse('');
      console.log('🏁 sendMessage 함수 완료');
      
    } catch (error: unknown) {
      console.error('❌ 스트리밍 오류:', error);
      
      // 타임아웃 정리
      clearTimeout(timeoutId);
      
      // 에러 타입별 처리
      let errorMessage = '알 수 없는 오류';
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorMessage = '요청이 타임아웃되었습니다. 잠시 후 다시 시도해주세요.';
        } else if (error.message.includes('NetworkError') || error.message.includes('fetch')) {
          errorMessage = '네트워크 연결에 문제가 있습니다. 인터넷 연결을 확인해주세요.';
        } else if (error.message.includes('500')) {
          errorMessage = '서버에 일시적인 문제가 있습니다. 잠시 후 다시 시도해주세요.';
        } else {
          errorMessage = error.message;
        }
      }
      
      setError(errorMessage);
      setIsStreaming(false);
      setIsConnecting(false);
      setStreamingResponse('');
    } finally {
      setIsLoading(false);
      setIsConnecting(false);
    }
  };

  // 새 대화 시작
  const startNewConversation = () => {
    console.log('🆕 새 대화 시작');
    
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
    setStreamingResponse('');
    
    console.log('✅ 새 대화 생성됨:', newConversation.id);
  };

  // 대화 선택
  const selectConversation = (conversationId: string) => {
    if (!conversationId) {
      setCurrentConversation(null);
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

  // 세션 초기화 (스트리밍 상태 리셋)
  const resetSession = () => {
    console.log('🔄 세션 상태 초기화');
    setIsStreaming(false);
    setIsConnecting(false);
    setStreamingResponse('');
    setIsLoading(false);
    setError(null);
  };

  // 더미 함수들 (호환성을 위해)
  const changeModel = async (model: string): Promise<boolean> => {
    console.log('NewChatContext: changeModel 호출됨:', model);
    return true;
  };
  
  const changeMode = async (mode: string): Promise<boolean> => {
    console.log('NewChatContext: changeMode 호출됨:', mode);
    return true;
  };
  
  const changePrompt = async (promptType: string): Promise<boolean> => {
    console.log('NewChatContext: changePrompt 호출됨:', promptType);
    return true;
  };

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
    isModelChanging: false,
    isModeChanging: false,
    isPromptChanging: false,
    
    // 스트리밍 상태
    isStreaming,
    streamingResponse,
    isConnecting,
    
    // 액션
    sendMessage,
    startNewConversation,
    selectConversation,
    deleteConversation,
    changeModel,
    changeMode,
    changePrompt,
    resetSession,
    
    // 대기 상태
    isWaitingForResponse: false,
    waitingTimer: 0,
    
    // 연결 상태
    isConnected: true,
    reconnectAttempts: 0,
  };

  return (
    <NewChatContext.Provider value={value}>
      {children}
    </NewChatContext.Provider>
  );
};