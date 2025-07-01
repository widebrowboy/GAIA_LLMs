'use client';

import React, { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react';
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

export const SimpleChatProvider = ({ children }: ChatProviderProps) => {
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
  
  // 로딩 상태
  const [isModelChanging] = useState(false);
  const [isModeChanging, setIsModeChanging] = useState(false);
  const [isPromptChanging] = useState(false);
  
  // 진행 상태
  const [waitingTimer, setWaitingTimer] = useState<number>(0);
  const [isWaitingForResponse, setIsWaitingForResponse] = useState<boolean>(false);
  
  // 연결 상태
  const [isConnected, setIsConnected] = useState(true); // 기본적으로 연결된 것으로 간주
  const [reconnectAttempts] = useState(0);
  const [lastHeartbeatTime] = useState<Date | null>(new Date());
  
  // 스트리밍 관련 상태 (SimpleChatContext에서는 사용하지 않지만 타입 호환성을 위해)
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingResponse, setStreamingResponse] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  
  // AbortController 관리 - useRef로 변경하여 re-render 시 안정성 확보
  const abortControllerRef = useRef<AbortController | null>(null);

  // console.log(' SimpleChatProvider 초기화됨:', { API_BASE_URL, sessionId });

  // 대화 선택 함수
  const selectConversation = (id: string) => {
    const conversation = conversations.find(conv => conv.id === id);
    if (conversation) {
      setCurrentConversation(conversation);
    }
  };


  // 대화 생성 함수
  const createConversation = async (name?: string): Promise<Conversation> => {
    const conversationName = name || `새 대화 ${new Date().toLocaleTimeString()}`;
    const newConversation: Conversation = {
      id: 'conv_' + Date.now(),
      name: conversationName,
      title: conversationName, // backward compatibility
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };

    const updatedConversations = [...conversations, newConversation];
    setConversations(updatedConversations);
    setCurrentConversation(newConversation);

    // 로컬 스토리지에 저장
    if (typeof window !== 'undefined') {
      localStorage.setItem('gaia_gpt_conversations', JSON.stringify(updatedConversations));
    }

    return newConversation;
  };

  // 메시지 추가 함수
  const addMessage = (message: Message) => {
    if (!currentConversation) {
      console.warn('현재 대화가 없습니다. 새 대화를 생성합니다.');
      return;
    }

    console.log('📝 메시지 추가 중:', {
      role: message.role,
      content: message.content.substring(0, 50) + '...',
      conversationId: message.conversationId
    });

    const updatedConversation = {
      ...currentConversation,
      messages: [...currentConversation.messages, message],
      updatedAt: new Date()
    };

    const updatedConversations = conversations.map(conv =>
      conv.id === currentConversation.id ? updatedConversation : conv
    );

    setConversations(updatedConversations);
    setCurrentConversation(updatedConversation);

    // 로컬 스토리지에 저장
    if (typeof window !== 'undefined') {
      localStorage.setItem('gaia_gpt_conversations', JSON.stringify(updatedConversations));
    }
    
    console.log(' 메시지 추가 완료, 현재 메시지 수:', updatedConversation.messages.length);
  };

  // 이전 요청 정리 함수
  const cleanupPendingRequests = async () => {
    if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
      try {
        // console.log(' 이전 요청 정리 중...');
        abortControllerRef.current.abort(new DOMException('새로운 요청으로 인한 정리', 'AbortError'));
        abortControllerRef.current = null;
        // 정리 완료까지 짧은 대기
        await new Promise(resolve => setTimeout(resolve, 50));
      } catch (cleanupError) {
        // abort 과정에서 발생하는 에러는 무시
        console.log('요청 정리 중 에러 (정상적인 동작):', cleanupError);
      }
    }
  };

  // 첫 메시지 기반으로 자동 제목 생성 함수
  const generateTitleFromMessage = (message: string): string => {
    // 첫 메시지에서 30자 이내로 적절히 제목 생성
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
      timestamp: new Date(),
      conversationId: conversation.id
    };
    addMessage(userMessage);
    
    // 첫 메시지일 경우 자동 제목 설정
    if (conversation.messages.length === 0) {
      const autoGeneratedTitle = generateTitleFromMessage(message);
      const updatedConversation = {
        ...conversation,
        title: autoGeneratedTitle
      };
      setCurrentConversation(updatedConversation);
      
      // 대화 목록에서도 제목 업데이트
      const updatedConversations = conversations.map(conv => 
        conv.id === conversation.id ? updatedConversation : conv
      );
      setConversations(updatedConversations);
      
      // 로컬 스토리지 업데이트
      if (typeof window !== 'undefined') {
        localStorage.setItem('gaia_gpt_conversations', JSON.stringify(updatedConversations));
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
        mcp_enabled: mcpEnabled // MCP 활성화 상태 추가
      };
      
      console.log('🏗️ 요청 body:', JSON.stringify(requestBody));
      console.log('🎭 현재 모드:', currentMode, 'MCP 활성화:', mcpEnabled);
      
      // 기본 fetch 재시도 (에러 복구 전략 강화)
      let response: Response;
      try {
        console.log('🔄 1차 시도: 기본 fetch 사용');
        response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
          },
          signal: controller.signal,
          body: JSON.stringify(requestBody, (_, value) => {
            if (typeof value === 'string') {
              return value.normalize('NFC');
            }
            return value;
          })
        });
      } catch (fetchError) {
        console.warn('⚠️ 기본 fetch 실패, 단순 재시도 후 에러 처리:', fetchError);
        
        // 간단한 재시도 한 번 더 시도
        try {
          await new Promise(resolve => setTimeout(resolve, 1000)); // 1초 대기
          console.log('🔄 기본 fetch 재시도');
          
          response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            signal: controller.signal,
            body: JSON.stringify(requestBody)
          });
          
          console.log('✅ 재시도 성공:', response.status);
        } catch (retryError) {
          console.error('❌ 재시도도 실패:', retryError);
          
          // 사용자에게 명확한 에러 메시지 표시
          setError('서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.');
          setIsLoading(false);
          setIsStreaming(false);
          setIsConnecting(false);
          
          // 더 이상 진행하지 않고 종료
          return;
        }
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
          throw new Error('스트림 리더를 가져올 수 없습니다');
        }

        let fullResponse = '';
        let buffer = ''; // SSE 이벤트가 청크 경계에서 잘릴 수 있으므로 버퍼 사용
        let streamCompleted = false;

        try {
          while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
              console.log('📖 스트림 리더 완료 (done=true)');
              // 스트림 완료 시에도 버퍼에 남은 데이터 처리
              if (buffer.trim()) {
                console.log('🔍 스트림 완료 후 버퍼 처리:', buffer.trim());
                const lines = buffer.split('\n');
                for (const line of lines) {
                  const trimmedLine = line.trim();
                  if (trimmedLine.startsWith('data: ')) {
                    const data = trimmedLine.slice(6);
                    if (data && data !== '[DONE]' && data.trim()) {
                      // JSON 인코딩된 데이터를 디코딩
                      let decodedData = data;
                      try {
                        decodedData = JSON.parse(data);
                      } catch (e) {
                        // JSON 파싱 실패 시 원본 사용
                      }
                      fullResponse += decodedData;
                      console.log('💬 스트림 완료 후 응답 추가:', decodedData);
                      setStreamingResponse(fullResponse);
                    }
                  }
                }
              }
              break;
            }

            // 바이트를 텍스트로 변환
            const chunk = decoder.decode(value, { stream: true });
            console.log(`📦 청크 수신:`, chunk.substring(0, 100));
            buffer += chunk;
            
            // 줄 단위로 처리
            const lines = buffer.split('\n');
            console.log(`📋 분할된 라인 수: ${lines.length}`);
            
            // 마지막 줄은 불완전할 수 있으므로 버퍼에 보관
            buffer = lines.pop() || '';
            
            for (const line of lines) {
              const trimmedLine = line.trim();
              console.log('🔍 처리 중인 라인:', trimmedLine);
              
              if (trimmedLine.startsWith('data: ')) {
                const data = trimmedLine.slice(6);
                console.log('📤 data 내용:', data);
                
                if (data === '[DONE]') {
                  console.log('🏁 스트리밍 완료 신호 수신 - 루프 종료');
                  streamCompleted = true;
                  break;
                }
                
                if (data && data.trim()) {
                  // JSON 인코딩된 데이터를 디코딩
                  let decodedData = data;
                  try {
                    decodedData = JSON.parse(data);
                  } catch (e) {
                    // JSON 파싱 실패 시 원본 사용
                  }
                  
                  // 데이터를 fullResponse에 추가
                  fullResponse += decodedData;
                  console.log('💬 응답 누적 길이:', fullResponse.length);
                  console.log('📝 현재 응답 미리보기:', fullResponse.substring(fullResponse.length - 50));
                  
                  // 실시간으로 UI 업데이트
                  setStreamingResponse(fullResponse);
                }
              }
            }
            
            // [DONE] 신호를 받았으면 outer loop도 종료
            if (streamCompleted) {
              console.log('✅ [DONE] 신호로 인한 스트리밍 종료');
              break;
            }
          }
          
          console.log('🎯 스트리밍 처리 완료 - 최종 응답 길이:', fullResponse.length);
          console.log('📄 최종 응답 전체:', fullResponse);
        } catch (readerError) {
          console.error('스트림 리더 오류:', readerError);
          throw readerError;
        } finally {
          reader.releaseLock();
        }
        
        // 스트리밍 완료 후 최종 정리
        const finalContent = fullResponse.trim();
        console.log('🔚 스트리밍 최종 정리 시작');
        console.log('📏 최종 컨텐츠 길이:', finalContent.length);
        console.log('🎭 컨트롤러 중단 상태:', controller.signal.aborted);
        
        // After streaming finished, add assistant message with userQuestion field
        if (finalContent && !controller.signal.aborted) {
          const assistantMessage: Message = {
            id: 'assistant_' + Date.now(),
            role: 'assistant',
            content: finalContent,
            timestamp: new Date(),
            conversationId: conversation.id,
            userQuestion: message, // Save the user question for traceability
            isComplete: true, // 완전한 응답임을 표시
            streamCompleted: streamCompleted // 스트림 완료 여부 기록
          };
          addMessage(assistantMessage);
          console.log('✅ 완전한 응답 메시지 저장 완료 - 길이:', finalContent.length);
          console.log('📋 저장된 메시지:', assistantMessage.content.substring(0, 100) + '...');
        } else {
          console.warn('⚠️ 메시지 저장 건너뜀:', {
            hasContent: !!finalContent,
            contentLength: finalContent.length,
            isAborted: controller.signal.aborted
          });
        }
        
        // 스트리밍 완료 후 즉시 상태 해제
        setIsLoading(false);
        setIsStreaming(false);
        setIsConnecting(false);
        setStreamingResponse('');
        console.log('🧹 스트리밍 상태 정리 완료');
      }
    } catch (error) {
      console.error('스트리밍 응답 처리 실패:', error);
      
      // AbortError는 정상적인 취소 상황
      if (error instanceof Error && error.name === 'AbortError') {
        return; // 에러 메시지 추가하지 않고 종료
      }
      
      // 실제 오류인 경우에만 에러 메시지 제공
      if (!controller.signal.aborted) {
        const errorMessage: Message = {
          id: 'assistant_' + Date.now(),
          role: 'assistant',
          content: '죄송합니다. 응답 처리 중 문제가 발생했습니다. 다시 시도해 주세요.',
          timestamp: new Date(),
          conversationId: conversation.id,
          userQuestion: message,
          isComplete: true
        };
        addMessage(errorMessage);
        setError('응답 처리 중 오류가 발생했습니다.');
      }
    } finally {
      // 모든 로딩 상태 강제 해제
      setIsLoading(false);
      setIsStreaming(false);
      setIsConnecting(false);
      setStreamingResponse(''); // 스트리밍 응답 클리어
      
      // 진행 상태도 초기화
      setWaitingTimer(0);
      setIsWaitingForResponse(false);
      
      // 모든 로딩 상태 해제 완료
      console.log('🔄 finally 블록 - 상태 정리 완료');
    }
  };

  const toggleMode = async () => {
    if (isModeChanging) return;

    const newMode = currentMode === 'normal' ? 'deep_research' : 'normal';
    setIsModeChanging(true);

    try {
      console.log(` 모드 변경: ${currentMode} -> ${newMode}`);

      // 로컬 상태 즉시 반영
      setCurrentMode(newMode);
      setMcpEnabled(newMode === 'deep_research');

      // 백엔드에 모드 변경 알림 (에러 처리 개선)
      try {
        console.log('🔄 toggleMode API 호출 시도...');
        const response = await fetch(`${API_BASE_URL}/api/system/mode/${newMode}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sessionId })
        });

        if (response.ok) {
          console.log(' 백엔드 모드 변경 성공');
        } else {
          console.warn('⚠️ 백엔드 모드 변경 실패, 로컬 상태는 유지됩니다');
        }
      } catch (fetchError) {
        console.warn('⚠️ toggleMode API 호출 실패, 재시도 중...', fetchError);
        
        // 간단한 재시도
        try {
          await new Promise(resolve => setTimeout(resolve, 1000)); // 1초 대기
          console.log('🔄 toggleMode 재시도...');
          
          const retryResponse = await fetch(`${API_BASE_URL}/api/system/mode/${newMode}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
          });
          
          if (retryResponse.ok) {
            console.log('✅ 재시도 성공: 백엔드 모드 변경 완료');
          } else {
            console.warn('⚠️ 재시도도 실패, 하지만 로컬 모드는 변경되었습니다');
          }
        } catch (retryError) {
          // API 호출 실패는 무시하고 로컬 상태만 유지
          console.warn('⚠️ 백엔드 통신 실패, 로컬 모드만 변경됨:', retryError);
        }
      }
      
      return true;
    } catch (error) {
      console.error('모드 변경 실패:', error);
      setError('모드 변경에 실패했습니다.');
      return false;
    } finally {
      setIsModeChanging(false);
    }
  };

  // 모델 변경 함수 - 간소화된 버전
  const changeModel = async (model: string): Promise<boolean> => {
    if (isLoading) return false; // 이미 로딩 중이면 무시
    
    try {
      console.log(` 모델 변경: ${currentModel} -> ${model}`);
      
      // 로컬에서 즉시 변경
      setCurrentModel(model);
      
      // 백그라운드에서 API 호출
      try {
        const response = await fetch(`${API_BASE_URL}/api/system/model`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model, session_id: sessionId })
        });
        
        if (response.ok) {
          console.log(' 백엔드 모델 변경 성공');
        } else {
          console.warn('Warning: 백엔드 모델 변경 실패, 로컬 상태 유지');
        }
      } catch (apiError) {
        console.warn('Warning: 백엔드 모델 변경 API 오류:', apiError);
      }
      
      return true;
    } catch (error) {
      console.error('모델 변경 실패:', error);
      setError('모델 변경에 실패했습니다.');
      return false;
    }
  };

  // 모드 변경 함수 - 간소화된 버전
  const changeMode = async (newMode: string): Promise<boolean> => {
    if (isLoading) return false; // 이미 로딩 중이면 무시
    
    setIsModeChanging(true);
    
    try {
      console.log(` 모드 변경: ${currentMode} -> ${newMode}`);
      
      // 로컬에서 즉시 변경
      setCurrentMode(newMode);
      setMcpEnabled(newMode === 'deep_research');
      
      // 백그라운드에서 API 호출 (에러 처리 개선)
      try {
        console.log('🔄 모드 변경 API 호출 시도...');
        const response = await fetch(`${API_BASE_URL}/api/system/mode/${newMode}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sessionId })
        });
        
        if (response.ok) {
          console.log(' 백엔드 모드 변경 성공');
        } else {
          console.warn('⚠️ 백엔드 모드 변경 실패, 로컬 상태는 유지됩니다');
        }
      } catch (fetchError) {
        console.warn('⚠️ 모드 변경 API 호출 실패, 재시도 중...', fetchError);
        
        // 간단한 재시도
        try {
          await new Promise(resolve => setTimeout(resolve, 1000)); // 1초 대기
          console.log('🔄 모드 변경 재시도...');
          
          const retryResponse = await fetch(`${API_BASE_URL}/api/system/mode/${newMode}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
          });
          
          if (retryResponse.ok) {
            console.log('✅ 재시도 성공: 백엔드 모드 변경 완료');
          } else {
            console.warn('⚠️ 재시도도 실패, 하지만 로컬 모드는 변경되었습니다');
          }
        } catch (retryError) {
          // API 호출 실패는 무시하고 로컬 상태만 유지
          console.warn('⚠️ 백엔드 통신 실패, 로컬 모드만 변경됨:', retryError);
          // 사용자에게는 성공으로 표시 (로컬 변경은 성공했으므로)
        }
      }
      
      // 로컬 변경은 성공했으므로 true 반환
      return true;
    } catch (error) {
      console.error('모드 변경 실패:', error);
      setError('모드 변경에 실패했습니다.');
      return false;
    } finally {
      setIsModeChanging(false);
    }
  };

  // 프롬프트 변경 함수 - 간소화된 버전
  const changePrompt = async (promptType: string): Promise<boolean> => {
    setCurrentPromptType(promptType);
    return true;
  };

  // 시스템 시작 시 기본 모델 자동 시작
  const initializeSystem = async () => {
    try {
      console.log(' 시스템 초기화 중...');
      
      // 기본 모델 시작 API 호출
      const response = await fetch(`${API_BASE_URL}/api/system/startup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          console.log(` 시스템 초기화 성공: ${result.message}`);
          if (result.model) {
            setCurrentModel(result.model);
          }
        } else {
          console.warn('시스템 초기화 실패:', result.error);
        }
      }
      
      // 초기화 후 모델 상태도 확인
      await refreshSystemStatus();
    } catch (error) {
      console.warn('시스템 초기화 오류:', error);
    }
  };

  // 시스템 상태 새로고침 함수
  const refreshSystemStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/system/models/detailed`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log(' 시스템 상태 새로고침:', data);
        
        if (data.current_model) {
          setCurrentModel(data.current_model);
        }
        
        // 상태 업데이트를 위한 이벤트 발송
        window.dispatchEvent(new CustomEvent('systemStatusUpdate', { detail: data }));
      }
    } catch (error) {
      console.warn('시스템 상태 새로고침 오류:', error);
    }
  };

  // 로컬 스토리지에서 대화 복원 및 시스템 초기화
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // 시스템 초기화 (모델 시작)
      initializeSystem();
      
      try {
        const savedConversations = localStorage.getItem('gaia_gpt_conversations');
        if (savedConversations) {
          const parsedConversations = JSON.parse(savedConversations);
          setConversations(parsedConversations);
          
          // 저장된 대화는 복원하지만 자동으로 선택하지는 않음
          // 사용자가 명시적으로 대화를 선택하거나 새 대화를 시작할 때까지 환영 페이지 유지
          // if (parsedConversations.length > 0) {
          //   setCurrentConversation(parsedConversations[parsedConversations.length - 1]);
          // }
        }
      } catch (error) {
        console.warn('대화 복원 실패:', error);
      }
    }
  }, []);

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
        try {
          abortControllerRef.current.abort(new DOMException('Component unmount', 'AbortError'));
        } catch {
          // ignore abort errors
        }
        abortControllerRef.current = null;
      }
    };
  }, []);

  
  // startNewConversation 별칭 함수 (기존 코드 호환성)
  const startNewConversation = () => {
    createConversation();
  };

  // deleteConversation 함수 추가
  const deleteConversation = (conversationId: string) => {
    const updatedConversations = conversations.filter(conv => conv.id !== conversationId);
    setConversations(updatedConversations);
    
    if (currentConversation?.id === conversationId) {
      setCurrentConversation(null);
    }
    
    // 로컬 스토리지 업데이트
    if (typeof window !== 'undefined') {
      localStorage.setItem('gaia_gpt_conversations', JSON.stringify(updatedConversations));
    }
  };

  // 세션 리셋 함수 - 스트리밍 상태 완전 초기화
  const resetSession = async () => {
    console.log(' 세션 상태 초기화 중...');
    
    // 진행 중인 요청 정리
    await cleanupPendingRequests();
    
    // 모든 상태 초기화
    setIsStreaming(false);
    setIsConnecting(false);
    setStreamingResponse('');
    setIsLoading(false);
    setError(null);
    setIsWaitingForResponse(false);
    setWaitingTimer(0);
    
    console.log(' 세션 상태 초기화 완료');
  };


  // Context value
  const value: ChatContextType = {
    // 대화 관련
    conversations,
    currentConversation,
    isLoading,
    error,
    sessionId,
    currentModel,
    currentMode,
    mcpEnabled,
    currentPromptType,
    isModelChanging,
    isModeChanging,
    isPromptChanging,
    
    // 스트리밍 관련 (호환성을 위해)
    isStreaming,
    streamingResponse,
    isConnecting,
    
    // 진행 상태
    isWaitingForResponse,
    waitingTimer,
    
    // 연결 상태
    isConnected,
    reconnectAttempts,
    lastHeartbeatTime,
    
    // 함수들
    sendMessage,
    startNewConversation,
    selectConversation,
    deleteConversation,
    changeModel,
    changeMode,
    changePrompt,
    resetSession,
    
    // 추가 함수들 (선택적)
    setConversations,
    setCurrentConversation,
    toggleMode,
    createConversation,
    
    // 상태 설정 함수들 (Sidebar에서 필요)
    setCurrentModel,
    setCurrentMode,
    setMcpEnabled,
    setCurrentPromptType,
    
    // 시스템 상태 새로고침 함수
    refreshSystemStatus: refreshSystemStatus
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};