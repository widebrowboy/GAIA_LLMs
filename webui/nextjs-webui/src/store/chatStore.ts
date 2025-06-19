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
  searchResults?: any;
  enhanced?: boolean;
  error?: string;
}

interface ChatSession {
  id: string;
  mode: 'normal' | 'mcp' | 'deep_research';
  prompt_type: 'default' | 'clinical' | 'research' | 'chemistry' | 'regulatory';
  messages: ChatMessage[];
  created_at: number;
  last_activity: number;
  model?: string;
  settings?: {
    autoSave: boolean;
    notifications: boolean;
    theme: 'dark' | 'light';
  };
}

interface ChatState {
  sessions: Record<string, ChatSession>;
  currentSessionId: string | null;
  isLoading: boolean;
  isTyping: boolean;
  error: string | null;
  messageIdCounter: number;
  systemStatus: {
    apiConnected: boolean;
    mcpServers: Array<{ name: string; status: 'online' | 'offline' | 'error' }>;
    lastHealthCheck: number;
  };
  
  // Actions
  createSession: (config?: { mode?: string; prompt_type?: string }) => Promise<string>;
  deleteSession: (sessionId: string) => void;
  setCurrentSession: (sessionId: string) => void;
  addMessage: (sessionId: string, message: Omit<ChatMessage, 'id' | 'timestamp'>) => string;
  updateMessage: (sessionId: string, messageId: string, updates: Partial<ChatMessage>) => void;
  clearMessages: (sessionId: string) => void;
  sendMessage: (sessionId: string, content: string) => Promise<void>;
  streamMessage: (sessionId: string, content: string) => Promise<void>;
  setMode: (sessionId: string, mode: string) => Promise<void>;
  setPromptType: (sessionId: string, promptType: string) => Promise<void>;
  updateSessionMode: (sessionId: string, mode: string) => void;
  updateSessionPromptType: (sessionId: string, promptType: string) => void;
  updateSystemStatus: (status: Partial<typeof systemStatus>) => void;
  checkSystemHealth: () => Promise<void>;
  exportSession: (sessionId: string) => string;
  importSession: (data: string) => Promise<string>;
  setLoading: (loading: boolean) => void;
  setTyping: (typing: boolean) => void;
  setError: (error: string | null) => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
          mcpServers: [
            { name: 'BiomCP', status: 'offline' },
            { name: 'ChEMBL', status: 'offline' },
            { name: 'DrugBank', status: 'offline' },
            { name: 'OpenTargets', status: 'offline' },
            { name: 'Sequential Thinking', status: 'offline' },
          ],
          lastHealthCheck: 0,
        },

        createSession: async (config = {}) => {
          try {
            // API 서버에 세션 생성 요청
            const response = await fetch(`${API_BASE_URL}/api/session/create`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({}),
            });

            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }

            const sessionData = await response.json();
            const sessionId = sessionData.session_id;
            
            const newSession: ChatSession = {
              id: sessionId,
              mode: config.mode as any || 'normal',
              prompt_type: config.prompt_type as any || 'default',
              messages: [],
              created_at: Date.now(),
              last_activity: Date.now(),
              model: sessionData.model || 'Gemma3:27b-it-q4_K_M',
              settings: {
                autoSave: true,
                notifications: true,
                theme: 'dark',
              },
            };

            set((state) => ({
              sessions: {
                ...state.sessions,
                [sessionId]: newSession,
              },
              currentSessionId: sessionId,
            }));

            return sessionId;
          } catch (error) {
            console.error('Failed to create session:', error);
            // 폴백: 로컬 세션 생성
            const sessionId = `session_${Date.now()}`;
            
            const newSession: ChatSession = {
              id: sessionId,
              mode: config.mode as any || 'normal',
              prompt_type: config.prompt_type as any || 'default',
              messages: [],
              created_at: Date.now(),
              last_activity: Date.now(),
              model: 'Gemma3:27b-it-q4_K_M',
              settings: {
                autoSave: true,
                notifications: true,
                theme: 'dark',
              },
            };

            set((state) => ({
              sessions: {
                ...state.sessions,
                [sessionId]: newSession,
              },
              currentSessionId: sessionId,
            }));

            return sessionId;
          }
        },

      deleteSession: (sessionId: string) => {
        set((state) => {
          const { [sessionId]: deleted, ...remainingSessions } = state.sessions;
          return {
            sessions: remainingSessions,
            currentSessionId: state.currentSessionId === sessionId ? null : state.currentSessionId,
          };
        });
      },

      setCurrentSession: (sessionId: string) => {
        set({ currentSessionId: sessionId });
      },

      addMessage: (sessionId: string, message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
        const state = get();
        const id = `msg_${state.messageIdCounter}_${Date.now()}`;
        const timestamp = Date.now();
        
        set((state) => ({
          messageIdCounter: state.messageIdCounter + 1,
          sessions: {
            ...state.sessions,
            [sessionId]: {
              ...state.sessions[sessionId],
              messages: [
                ...state.sessions[sessionId].messages,
                { ...message, id, timestamp },
              ],
              last_activity: timestamp,
            },
          },
        }));
        
        return id;
      },

      updateMessage: (sessionId: string, messageId: string, updates: Partial<ChatMessage>) => {
        set((state) => ({
          sessions: {
            ...state.sessions,
            [sessionId]: {
              ...state.sessions[sessionId],
              messages: state.sessions[sessionId].messages.map(msg =>
                msg.id === messageId ? { ...msg, ...updates } : msg
              ),
              last_activity: Date.now(),
            },
          },
        }));
      },

      clearMessages: (sessionId: string) => {
        set((state) => ({
          sessions: {
            ...state.sessions,
            [sessionId]: {
              ...state.sessions[sessionId],
              messages: [],
              last_activity: Date.now(),
            },
          },
        }));
      },

      sendMessage: async (sessionId: string, content: string) => {
        const { addMessage, setTyping } = get();
        
        // 사용자 메시지 추가
        addMessage(sessionId, {
          role: 'user',
          content,
        });

        setTyping(true);

        // Mock AI 응답 (실제로는 API 호출)
        setTimeout(() => {
          const session = get().sessions[sessionId];
          const isDeepResearch = session?.mode === 'mcp' || session?.mode === 'deep_research';
          
          let response = '';
          if (isDeepResearch) {
            response = `🔬 Deep Research 분석 결과: "${content}"에 대한 종합적인 과학적 분석을 제공합니다. 

다중 데이터베이스 검색을 통해 다음과 같은 정보를 수집했습니다:
- PubMed 논문 검색 결과
- ChEMBL 화합물 데이터
- 임상시험 정보

과학적 근거를 바탕으로 상세한 답변을 제공합니다.`;
          } else {
            response = `신약개발 AI 어시스턴트입니다. "${content}"에 대한 전문적인 분석을 제공합니다. 

추가적인 상세 정보가 필요하시면 Deep Research 모드를 활성화해주세요.`;
          }

          addMessage(sessionId, {
            role: 'assistant',
            content: response,
            enhanced: isDeepResearch,
            searchResults: isDeepResearch ? {
              pubmed: [{ title: 'Example Research Paper', authors: 'Smith et al.', year: 2024 }],
              chembl: [{ compound: 'Example Compound', activity: 'High' }]
            } : undefined,
          });

          setTyping(false);
        }, 1000 + Math.random() * 2000);
      },

      setMode: async (sessionId: string, mode: string) => {
        set((state) => ({
          sessions: {
            ...state.sessions,
            [sessionId]: {
              ...state.sessions[sessionId],
              mode: mode as any,
            },
          },
        }));
      },

      setPromptType: async (sessionId: string, promptType: string) => {
        set((state) => ({
          sessions: {
            ...state.sessions,
            [sessionId]: {
              ...state.sessions[sessionId],
              prompt_type: promptType as any,
            },
          },
        }));
      },

      updateSessionMode: (sessionId: string, mode: string) => {
        set((state) => ({
          sessions: {
            ...state.sessions,
            [sessionId]: {
              ...state.sessions[sessionId],
              mode: mode as any,
            },
          },
        }));
      },

      updateSessionPromptType: (sessionId: string, promptType: string) => {
        set((state) => ({
          sessions: {
            ...state.sessions,
            [sessionId]: {
              ...state.sessions[sessionId],
              prompt_type: promptType as any,
            },
          },
        }));
      },

      streamMessage: async (sessionId: string, content: string) => {
        const { addMessage, setTyping, updateMessage } = get();
        
        // 사용자 메시지 추가
        addMessage(sessionId, {
          role: 'user',
          content,
        });

        setTyping(true);

        // 스트리밍 응답 생성
        const assistantMessageId = addMessage(sessionId, {
          role: 'assistant',
          content: '',
          streaming: true,
          processing: true,
        });

        try {
          const response = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              message: content,
              session_id: sessionId,
            }),
          });

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const reader = response.body?.getReader();
          const decoder = new TextDecoder();
          let fullResponse = '';

          if (reader) {
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;

              const chunk = decoder.decode(value);
              const lines = chunk.split('\n');

              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  const data = line.slice(6);
                  if (data === '[DONE]') {
                    updateMessage(sessionId, assistantMessageId, {
                      content: fullResponse,
                      streaming: false,
                      processing: false,
                    });
                    setTyping(false);
                    return;
                  }
                  
                  if (data.trim()) {
                    fullResponse += data + ' ';
                    updateMessage(sessionId, assistantMessageId, {
                      content: fullResponse,
                      streaming: true,
                      processing: true,
                    });
                  }
                }
              }
            }
          }
        } catch (error) {
          console.error('Streaming failed:', error);
          updateMessage(sessionId, assistantMessageId, {
            content: `❌ 스트리밍 오류: ${error instanceof Error ? error.message : '알 수 없는 오류'}`,
            streaming: false,
            processing: false,
            error: error instanceof Error ? error.message : 'Unknown error',
          });
          setTyping(false);
        }
      },

      updateSystemStatus: (status) => {
        set((state) => ({
          systemStatus: {
            ...state.systemStatus,
            ...status,
            lastHealthCheck: Date.now(),
          },
        }));
      },

      checkSystemHealth: async () => {
        try {
          const response = await fetch('/api/health');
          const isConnected = response.ok;
          
          const { updateSystemStatus } = get();
          updateSystemStatus({
            apiConnected: isConnected,
            mcpServers: isConnected ? [
              { name: 'BiomCP', status: 'online' },
              { name: 'ChEMBL', status: 'online' },
              { name: 'DrugBank', status: 'online' },
              { name: 'OpenTargets', status: 'online' },
              { name: 'Sequential Thinking', status: 'online' },
            ] : [
              { name: 'BiomCP', status: 'offline' },
              { name: 'ChEMBL', status: 'offline' },
              { name: 'DrugBank', status: 'offline' },
              { name: 'OpenTargets', status: 'offline' },
              { name: 'Sequential Thinking', status: 'offline' },
            ],
          });
        } catch (error) {
          const { updateSystemStatus } = get();
          updateSystemStatus({
            apiConnected: false,
            mcpServers: [
              { name: 'BiomCP', status: 'error' },
              { name: 'ChEMBL', status: 'error' },
              { name: 'DrugBank', status: 'error' },
              { name: 'OpenTargets', status: 'error' },
              { name: 'Sequential Thinking', status: 'error' },
            ],
          });
        }
      },

      exportSession: (sessionId: string) => {
        const session = get().sessions[sessionId];
        if (!session) throw new Error('Session not found');
        
        const exportData = {
          version: '2.0',
          session,
          exportedAt: Date.now(),
        };
        
        return JSON.stringify(exportData, null, 2);
      },

      importSession: async (data: string) => {
        try {
          const parsed = JSON.parse(data);
          const session = parsed.session;
          
          if (!session || !session.id) {
            throw new Error('Invalid session data');
          }

          // 새로운 ID 생성하여 중복 방지
          const newSessionId = `imported_${Date.now()}`;
          const importedSession = {
            ...session,
            id: newSessionId,
            created_at: Date.now(),
            last_activity: Date.now(),
          };

          set((state) => ({
            sessions: {
              ...state.sessions,
              [newSessionId]: importedSession,
            },
            currentSessionId: newSessionId,
          }));

          return newSessionId;
        } catch (error) {
          throw new Error(`Import failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
      },

      setLoading: (loading: boolean) => set({ isLoading: loading }),
      setTyping: (typing: boolean) => set({ isTyping: typing }),
      setError: (error: string | null) => set({ error }),
    }),
    {
      name: 'gaia-bt-chat-store',
      partialize: (state) => ({
        sessions: state.sessions,
        currentSessionId: state.currentSessionId,
        messageIdCounter: state.messageIdCounter,
      }),
    }
  ),
  { name: 'chat-store' }
  )
);