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
      
      // 타임아웃 설정 (600초로 증가 - 딥리서치 및 긴 응답용)
      const timeoutId = setTimeout(() => {
        if (!controller.signal.aborted) {
          console.warn('Warning: API 요청 타임아웃 발생 (600초 초과)');
          console.warn(`경과 시간: ${(Date.now() - startTime) / 1000}초`);
          controller.abort(new DOMException('Request timeout', 'AbortError'));
        }
      }, 600000); // 10분으로 연장
      
      console.log('🔄 스트리밍 요청 준비:', {
        url: `${API_BASE_URL}/api/chat/stream`,
        message: message.substring(0, 50),
        sessionId
      });

      const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
          'Referrer-Policy': 'same-origin'
        },
        signal: controller.signal,
        body: JSON.stringify({
          message: message,
          session_id: sessionId,
          complete_response: true, // 전체 응답 수신을 명시적으로 요청
          stream: true // 스트림 명시적으로 활성화
        }, (_, value) => {
          // 문자열 값에 대해 UTF-8 인코딩 문제 방지
          if (typeof value === 'string') {
            return value.normalize('NFC');
          }
          return value;
        })
      });
      
      console.log('📡 스트리밍 응답 수신:', {
        status: response.status,
        ok: response.ok,
        headers: Object.fromEntries(response.headers.entries())
      });
      
      clearTimeout(timeoutId);
      
      // 연결 완료
      setIsConnecting(false);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ 스트리밍 응답 오류:', {
          status: response.status,
          statusText: response.statusText,
          errorText: errorText.substring(0, 200)
        });
        throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
      }

      if (response.ok) {
        // 스트리밍 응답 처리 개선
        const reader = response.body?.getReader();
        const decoder = new TextDecoder('utf-8', { fatal: false });
        
        if (!reader) {
          throw new Error('스트림 리더를 가져올 수 없습니다');
        }

        console.log('📖 스트림 리더 시작 - 응답 읽기 시작');
        let fullResponse = '';
        let isCompleted = false;
        let lastUpdateTime = Date.now();
        const responseChunks: string[] = [];
        let chunkCount = 0;

        while (true) {
          const { done, value } = await reader.read();
          chunkCount++;
          
          if (chunkCount <= 5 || chunkCount % 10 === 0) {
            console.log(`📦 청크 ${chunkCount} 수신:`, { done, valueLength: value?.length });
          }
          
          if (done) {
            isCompleted = true;
            console.log(`✅ 스트림 완료 - 총 ${chunkCount}개 청크 처리`);
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6).trim();
              if (data && data !== '' && data !== '[DONE]') {
                try {
                  const jsonData = JSON.parse(data);
                  const content = jsonData.content || jsonData.response || jsonData.text || data;
                  
                  // 오류 메시지 감지 및 처리
                  if (content.includes('[연결 오류]') || content.includes('[모델 시작 오류]')) {
                    console.error('Ollama 연결/모델 오류 감지:', content);
                    setError(`Ollama 연결 문제가 발생했습니다: ${content}`);
                    setIsStreaming(false);
                    setIsConnecting(false);
                    return;
                  }
                  
                  fullResponse += content;
                  responseChunks.push(content);
                  
                  // 응답 품질 향상을 위한 적응적 업데이트
                  const currentTime = Date.now();
                  if (currentTime - lastUpdateTime > 50 || content.includes('\n') || 
                      /[.!?]\s*$/.test(content) || responseChunks.length % 5 === 0) {
                    setStreamingResponse(fullResponse);
                    lastUpdateTime = currentTime;
                  }
                } catch {
                  // JSON이 아닌 일반 텍스트인 경우
                  const content = data;
                  
                  // 오류 메시지 감지 및 처리 (일반 텍스트)
                  if (content.includes('[연결 오류]') || content.includes('[모델 시작 오류]')) {
                    console.error('Ollama 연결/모델 오류 감지:', content);
                    setError(`Ollama 연결 문제가 발생했습니다: ${content}`);
                    setIsStreaming(false);
                    setIsConnecting(false);
                    return;
                  }
                  
                  fullResponse += content;
                  responseChunks.push(content);
                  setStreamingResponse(fullResponse);
                }
              }
            } else if (line.trim() !== '') {
              // 'data:' 접두사가 없는 유효한 라인도 처리
              const content = line.trim();
              
              // 오류 메시지 감지 및 처리 (일반 라인)
              if (content.includes('[연결 오류]') || content.includes('[모델 시작 오류]')) {
                console.error('Ollama 연결/모델 오류 감지:', content);
                setError(`Ollama 연결 문제가 발생했습니다: ${content}`);
                setIsStreaming(false);
                setIsConnecting(false);
                return;
              }
              
              fullResponse += content;
              responseChunks.push(content);
              setStreamingResponse(fullResponse);
            }
          }
        }
        
        // 마지막 부분 라인 처리 - 완전성 보장
        const partialLine = decoder.decode();
        if (partialLine && partialLine.trim()) {
          let finalContent = '';
          if (partialLine.startsWith('data: ')) {
            const data = partialLine.slice(6).trim();
            if (data && data !== '' && data !== '[DONE]') {
              try {
                const jsonData = JSON.parse(data);
                finalContent = jsonData.content || jsonData.response || jsonData.text || data;
              } catch {
                finalContent = data;
              }
            }
          } else if (partialLine.trim() !== '') {
            finalContent = partialLine.trim();
          }
          
          if (finalContent) {
            fullResponse += finalContent;
            responseChunks.push(finalContent);
            setStreamingResponse(fullResponse);
          }
        }
        
        // 최종 응답 완전성 검증
        const finalResponseLength = fullResponse.length;
        const chunksTotal = responseChunks.join('').length;
        console.log(` 응답 완전성 검증: 최종응답=${finalResponseLength}자, 청크총합=${chunksTotal}자`);
        
        if (finalResponseLength !== chunksTotal && responseChunks.length > 0) {
          // 불일치 시 청크 기반으로 재구성
          fullResponse = responseChunks.join('');
          setStreamingResponse(fullResponse);
          console.log(' 응답 재구성 완료');
        }
        
        console.log(` 스트리밍 응답 완료 (${fullResponse.length}자, ${responseChunks.length}개 청크)`);
        
        // 스트리밍 완료 후 최종 마크다운 검증 및 정리
        let finalContent = fullResponse.trim();
        if (finalContent) {
          // 마크다운 구조 개선을 위한 후처리
          finalContent = finalContent
            .replace(/\n{3,}/g, '\n\n') // 과도한 줄바꿈 정리
            .replace(/([.!?])([A-Za-z가-힣])/g, '$1 $2') // 문장 간 공백 확보
            .replace(/#{1,6}\s*([^\n]+)/g, (match, title) => {
              // 마크다운 헤더 정리
              const level = match.indexOf(' ');
              return '#'.repeat(Math.min(level, 6)) + ' ' + title.trim();
            });
          
          console.log(' 마크다운 후처리 완료');
        }
        
        // After streaming finished, add assistant message with userQuestion field
        if (finalContent && !controller.signal.aborted) {
          const assistantMessage: Message = {
            id: 'assistant_' + Date.now(),
            role: 'assistant',
            content: finalContent,
            timestamp: new Date(),
            conversationId: conversation.id,
            userQuestion: message, // Save the user question for traceability
            isComplete: true // 완전한 응답임을 표시
          };
          addMessage(assistantMessage);
          console.log(' 완전한 응답 메시지 저장 완료');
          
          // 스트리밍 완료 후 즉시 상태 해제
          setIsLoading(false);
          setIsStreaming(false);
          setIsConnecting(false);
          setStreamingResponse('');
          console.log(' 스트리밍 완료 - 상태 즉시 해제');
        }
      }
    } catch (error) {
      console.error('스트리밍 응답 처리 실패:', error);
      
      // AbortError는 정상적인 취소 상황
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('🛑 요청이 취소되었습니다 (컴포넌트 재마운트 또는 새 요청)');
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
      
      console.log('✅ 모든 로딩 상태 해제 완료');
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

      // 백엔드에 모드 변경 알림
      const response = await fetch(`${API_BASE_URL}/api/system/mode/${newMode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });

      if (response.ok) {
        console.log(' 백엔드 모드 변경 성공');
      } else {
        console.warn('Warning: 백엔드 모드 변경 실패, 로컬 상태 유지');
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
      
      // 백그라운드에서 API 호출
      try {
        const response = await fetch(`${API_BASE_URL}/api/system/mode/${newMode}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sessionId })
        });
        
        if (response.ok) {
          console.log(' 백엔드 모드 변경 성공');
        } else {
          console.warn('Warning: 백엔드 모드 변경 실패, 로컬 상태 유지');
        }
      } catch (error) {
        console.error('모드 변경 실패:', error);
        setError('모드 변경에 실패했습니다.');
        return false;
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