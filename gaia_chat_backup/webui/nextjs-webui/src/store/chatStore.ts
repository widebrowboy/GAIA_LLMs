import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  mode?: 'normal' | 'deep_research';
  prompt_type?: string;
  sources?: string[];
  processing?: boolean;
  streaming?: boolean;
  error?: string;
}

interface ChatSession {
  id: string;
  mode: 'normal' | 'deep_research';
  prompt_type: 'default' | 'clinical' | 'research' | 'chemistry' | 'regulatory';
  messages: ChatMessage[];
  created_at: number;
  last_activity: number;
  model?: string;
}

interface SystemStatus {
  apiConnected: boolean;
  mcpServers: Array<{ name: string; status: 'running' | 'stopped' | 'error' }>;
  lastHealthCheck: number;
  version: string;
  availableModels: string[];
  availablePrompts: string[];
}

interface ChatState {
  sessions: Record<string, ChatSession>;
  currentSessionId: string | null;
  isLoading: boolean;
  isTyping: boolean;
  error: string | null;
  messageIdCounter: number;
  systemStatus: SystemStatus;
  
  // Core Actions
  createSession: (config?: { mode?: string; prompt_type?: string }) => Promise<string>;
  deleteSession: (sessionId: string) => void;
  setCurrentSession: (sessionId: string) => void;
  addMessage: (sessionId: string, message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  updateMessage: (sessionId: string, messageId: string, updates: Partial<ChatMessage>) => void;
  
  // Message Actions
  sendMessage: (sessionId: string, content: string) => Promise<void>;
  sendStreamingMessage: (sessionId: string, content: string) => Promise<void>;
  executeCommand: (sessionId: string, command: string) => Promise<void>;
  
  // Session Management
  updateSessionMode: (sessionId: string, mode: 'normal' | 'deep_research') => Promise<void>;
  updateSessionPromptType: (sessionId: string, promptType: string) => Promise<void>;
  updateSessionModel: (sessionId: string, model: string) => Promise<void>;
  
  // System Management
  refreshSystemStatus: () => Promise<void>;
  toggleDebugMode: () => Promise<void>;
  checkMCPStatus: () => Promise<void>;
  
  // Utility Actions
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  setTyping: (typing: boolean) => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// API 호출 헬퍼 함수들
const apiCall = async (endpoint: string, options?: RequestInit) => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
};

const webUIApiCall = async (endpoint: string, options?: RequestInit) => {
  const response = await fetch(endpoint, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });
  
  if (!response.ok) {
    throw new Error(`WebUI API Error: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
};

export const useChatStore = create<ChatState>()(
  devtools(
    persist(
      (set, get) => ({
        sessions: {},
        currentSessionId: null,
        isLoading: false,
        isTyping: false,
        error: null,
        messageIdCounter: 0,
        systemStatus: {
          apiConnected: false,
          mcpServers: [],
          lastHealthCheck: 0,
          version: '2.0.0',
          availableModels: [],
          availablePrompts: []
        },

        // Core Actions
        createSession: async (config = {}) => {
          set({ isLoading: true });
          
          try {
            // FastAPI로 세션 생성
            const sessionData = await apiCall('/api/session/create', {
              method: 'POST',
              body: JSON.stringify({
                mode: config.mode || 'normal',
                prompt_type: config.prompt_type || 'default'
              })
            });
            
            const sessionId = sessionData.session_id;
            const newSession: ChatSession = {
              id: sessionId,
              mode: config.mode === 'deep_research' ? 'deep_research' : 'normal',
              prompt_type: (config.prompt_type as any) || 'default',
              messages: [],
              created_at: Date.now(),
              last_activity: Date.now(),
              model: sessionData.model
            };

            set(state => ({
              sessions: { ...state.sessions, [sessionId]: newSession },
              currentSessionId: sessionId,
              isLoading: false
            }));

            return sessionId;
          } catch (error) {
            // 폴백: 로컬 세션 생성
            const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            const newSession: ChatSession = {
              id: sessionId,
              mode: config.mode === 'deep_research' ? 'deep_research' : 'normal',
              prompt_type: (config.prompt_type as any) || 'default',
              messages: [],
              created_at: Date.now(),
              last_activity: Date.now()
            };

            set(state => ({
              sessions: { ...state.sessions, [sessionId]: newSession },
              currentSessionId: sessionId,
              isLoading: false,
              error: `세션 생성 중 API 오류 발생. 로컬 세션으로 생성됨: ${error}`
            }));

            return sessionId;
          }
        },

        deleteSession: (sessionId: string) => {
          set(state => {
            const newSessions = { ...state.sessions };
            delete newSessions[sessionId];
            
            const remainingSessions = Object.keys(newSessions);
            const newCurrentSessionId = state.currentSessionId === sessionId 
              ? (remainingSessions.length > 0 ? remainingSessions[0] : null)
              : state.currentSessionId;

            // API로 세션 삭제 요청 (비동기)
            apiCall(`/api/session/${sessionId}`, { method: 'DELETE' }).catch(console.error);

            return {
              sessions: newSessions,
              currentSessionId: newCurrentSessionId
            };
          });
        },

        setCurrentSession: (sessionId: string) => {
          set({ currentSessionId: sessionId });
        },

        addMessage: (sessionId: string, message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
          set(state => {
            const session = state.sessions[sessionId];
            if (!session) return state;

            const messageId = `msg_${state.messageIdCounter}_${Date.now()}`;
            const newMessage: ChatMessage = {
              ...message,
              id: messageId,
              timestamp: Date.now()
            };

            return {
              sessions: {
                ...state.sessions,
                [sessionId]: {
                  ...session,
                  messages: [...session.messages, newMessage],
                  last_activity: Date.now()
                }
              },
              messageIdCounter: state.messageIdCounter + 1
            };
          });
        },

        updateMessage: (sessionId: string, messageId: string, updates: Partial<ChatMessage>) => {
          set(state => {
            const session = state.sessions[sessionId];
            if (!session) return state;

            const messageIndex = session.messages.findIndex(m => m.id === messageId);
            if (messageIndex === -1) return state;

            const updatedMessages = [...session.messages];
            updatedMessages[messageIndex] = { ...updatedMessages[messageIndex], ...updates };

            return {
              sessions: {
                ...state.sessions,
                [sessionId]: {
                  ...session,
                  messages: updatedMessages,
                  last_activity: Date.now()
                }
              }
            };
          });
        },

        // Message Actions
        sendMessage: async (sessionId: string, content: string) => {
          const { addMessage } = get();
          
          // 사용자 메시지 추가
          addMessage(sessionId, {
            role: 'user',
            content,
            timestamp: Date.now()
          });

          set({ isTyping: true });

          try {
            // WebUI API 통해 메시지 전송
            const response = await webUIApiCall('/api/chat', {
              method: 'POST',
              body: JSON.stringify({
                message: content,
                sessionId: sessionId
              })
            });

            if (response.success) {
              // AI 응답 추가
              addMessage(sessionId, {
                role: 'assistant',
                content: response.response,
                mode: response.mode,
                sources: response.mcpSources,
                timestamp: Date.now()
              });
            } else {
              throw new Error(response.error || 'Unknown error');
            }
          } catch (error) {
            // 에러 메시지 추가
            addMessage(sessionId, {
              role: 'assistant',
              content: `죄송합니다. 메시지 처리 중 오류가 발생했습니다: ${error}`,
              error: error instanceof Error ? error.message : 'Unknown error',
              timestamp: Date.now()
            });
            
            set({ error: error instanceof Error ? error.message : 'Unknown error' });
          } finally {
            set({ isTyping: false });
          }
        },

        sendStreamingMessage: async (sessionId: string, content: string) => {
          const { addMessage, updateMessage } = get();
          
          // 사용자 메시지 추가
          addMessage(sessionId, {
            role: 'user',
            content,
            timestamp: Date.now()
          });

          // AI 응답 메시지 생성 (빈 내용으로 시작)
          const assistantMessageId = `msg_${get().messageIdCounter}_${Date.now()}`;
          addMessage(sessionId, {
            role: 'assistant',
            content: '',
            streaming: true,
            timestamp: Date.now()
          });

          set({ isTyping: true, messageIdCounter: get().messageIdCounter + 1 });

          try {
            // WebUI PUT 엔드포인트를 통한 스트리밍 시뮬레이션
            const response = await fetch('/api/chat', {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                message: content,
                sessionId: sessionId
              })
            });

            if (response.ok) {
              const fullResponse = await response.text();
              
              // 스트리밍 시뮬레이션
              const words = fullResponse.split(' ');
              let currentContent = '';
              
              for (let i = 0; i < words.length; i++) {
                currentContent += (i > 0 ? ' ' : '') + words[i];
                
                updateMessage(sessionId, assistantMessageId, {
                  content: currentContent,
                  streaming: i < words.length - 1
                });
                
                // 80ms 간격으로 단어별 표시
                if (i < words.length - 1) {
                  await new Promise(resolve => setTimeout(resolve, 80));
                }
              }
              
              // 스트리밍 완료
              updateMessage(sessionId, assistantMessageId, {
                streaming: false
              });
            } else {
              throw new Error(`HTTP ${response.status}`);
            }
          } catch (error) {
            updateMessage(sessionId, assistantMessageId, {
              content: `죄송합니다. 스트리밍 메시지 처리 중 오류가 발생했습니다: ${error}`,
              error: error instanceof Error ? error.message : 'Unknown error',
              streaming: false
            });
            
            set({ error: error instanceof Error ? error.message : 'Unknown error' });
          } finally {
            set({ isTyping: false });
          }
        },

        executeCommand: async (sessionId: string, command: string) => {
          set({ isLoading: true });
          
          try {
            const response = await apiCall('/api/chat/command', {
              method: 'POST',
              body: JSON.stringify({
                command,
                session_id: sessionId
              })
            });

            // 명령어 결과를 메시지로 추가
            get().addMessage(sessionId, {
              role: 'assistant',
              content: response.response || response.message || '명령어가 실행되었습니다.',
              timestamp: Date.now()
            });
          } catch (error) {
            get().addMessage(sessionId, {
              role: 'assistant',
              content: `명령어 실행 실패: ${error}`,
              error: error instanceof Error ? error.message : 'Unknown error',
              timestamp: Date.now()
            });
          } finally {
            set({ isLoading: false });
          }
        },

        // Session Management
        updateSessionMode: async (sessionId: string, mode: 'normal' | 'deep_research') => {
          try {
            await apiCall(`/api/system/mode/${mode}`, {
              method: 'POST',
              body: JSON.stringify({ session_id: sessionId })
            });

            set(state => ({
              sessions: {
                ...state.sessions,
                [sessionId]: {
                  ...state.sessions[sessionId],
                  mode,
                  last_activity: Date.now()
                }
              }
            }));
          } catch (error) {
            // 로컬 상태만 업데이트 (폴백)
            set(state => ({
              sessions: {
                ...state.sessions,
                [sessionId]: {
                  ...state.sessions[sessionId],
                  mode,
                  last_activity: Date.now()
                }
              },
              error: `모드 변경 중 오류 발생: ${error}`
            }));
          }
        },

        updateSessionPromptType: async (sessionId: string, promptType: string) => {
          try {
            await apiCall('/api/system/prompt', {
              method: 'POST',
              body: JSON.stringify({
                prompt_type: promptType,
                session_id: sessionId
              })
            });

            set(state => ({
              sessions: {
                ...state.sessions,
                [sessionId]: {
                  ...state.sessions[sessionId],
                  prompt_type: promptType as any,
                  last_activity: Date.now()
                }
              }
            }));
          } catch (error) {
            // 로컬 상태만 업데이트 (폴백)
            set(state => ({
              sessions: {
                ...state.sessions,
                [sessionId]: {
                  ...state.sessions[sessionId],
                  prompt_type: promptType as any,
                  last_activity: Date.now()
                }
              },
              error: `프롬프트 타입 변경 중 오류 발생: ${error}`
            }));
          }
        },

        updateSessionModel: async (sessionId: string, model: string) => {
          try {
            await apiCall('/api/system/model', {
              method: 'POST',
              body: JSON.stringify({
                model_name: model,
                session_id: sessionId
              })
            });

            set(state => ({
              sessions: {
                ...state.sessions,
                [sessionId]: {
                  ...state.sessions[sessionId],
                  model,
                  last_activity: Date.now()
                }
              }
            }));
          } catch (error) {
            set({ error: `모델 변경 중 오류 발생: ${error}` });
          }
        },

        // System Management
        refreshSystemStatus: async () => {
          try {
            const systemInfo = await apiCall('/api/system/info');
            const mcpStatus = await apiCall('/api/mcp/status');

            set(state => ({
              systemStatus: {
                ...state.systemStatus,
                apiConnected: true,
                lastHealthCheck: Date.now(),
                version: systemInfo.version,
                availableModels: systemInfo.available_models || [],
                availablePrompts: systemInfo.available_prompts || [],
                mcpServers: mcpStatus.servers || []
              },
              error: null
            }));
          } catch (error) {
            set(state => ({
              systemStatus: {
                ...state.systemStatus,
                apiConnected: false,
                lastHealthCheck: Date.now()
              },
              error: `시스템 상태 확인 실패: ${error}`
            }));
          }
        },

        toggleDebugMode: async () => {
          try {
            await apiCall('/api/system/debug', { method: 'POST' });
          } catch (error) {
            set({ error: `디버그 모드 토글 실패: ${error}` });
          }
        },

        checkMCPStatus: async () => {
          try {
            const mcpStatus = await apiCall('/api/mcp/status');
            set(state => ({
              systemStatus: {
                ...state.systemStatus,
                mcpServers: mcpStatus.servers || []
              }
            }));
          } catch (error) {
            console.error('MCP 상태 확인 실패:', error);
          }
        },

        // Utility Actions
        clearError: () => set({ error: null }),
        setLoading: (loading: boolean) => set({ isLoading: loading }),
        setTyping: (typing: boolean) => set({ isTyping: typing })
      }),
      {
        name: 'gaia-bt-chat-store',
        partialize: (state) => ({ 
          sessions: state.sessions, 
          currentSessionId: state.currentSessionId,
          messageIdCounter: state.messageIdCounter
        })
      }
    ),
    { name: 'gaia-bt-chat-store' }
  )
);