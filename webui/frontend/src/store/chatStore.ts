import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  searchResults?: any;
  enhanced?: boolean;
}

interface ChatSession {
  id: string;
  mode: 'normal' | 'mcp' | 'deep_research';
  prompt_type: 'default' | 'clinical' | 'research' | 'chemistry' | 'regulatory';
  messages: ChatMessage[];
  created_at: number;
  last_activity: number;
}

interface ChatState {
  sessions: Record<string, ChatSession>;
  currentSessionId: string | null;
  isLoading: boolean;
  isTyping: boolean;
  error: string | null;
  
  // Actions
  createSession: (config?: { mode?: string; prompt_type?: string }) => Promise<string>;
  deleteSession: (sessionId: string) => void;
  setCurrentSession: (sessionId: string) => void;
  addMessage: (sessionId: string, message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  sendMessage: (sessionId: string, content: string) => Promise<void>;
  setMode: (sessionId: string, mode: string) => Promise<void>;
  setPromptType: (sessionId: string, promptType: string) => Promise<void>;
  setLoading: (loading: boolean) => void;
  setTyping: (typing: boolean) => void;
  setError: (error: string | null) => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const useChatStore = create<ChatState>()(
  devtools(
    (set, get) => ({
      sessions: {},
      currentSessionId: null,
      isLoading: false,
      isTyping: false,
      error: null,

      createSession: async (config = {}) => {
        const sessionId = `session_${Date.now()}`;
        
        const newSession: ChatSession = {
          id: sessionId,
          mode: config.mode as any || 'normal',
          prompt_type: config.prompt_type as any || 'default',
          messages: [],
          created_at: Date.now(),
          last_activity: Date.now(),
        };

        set((state) => ({
          sessions: {
            ...state.sessions,
            [sessionId]: newSession,
          },
          currentSessionId: sessionId,
        }));

        return sessionId;
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
        const id = Date.now().toString();
        const timestamp = Date.now();
        
        set((state) => ({
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

      setLoading: (loading: boolean) => set({ isLoading: loading }),
      setTyping: (typing: boolean) => set({ isTyping: typing }),
      setError: (error: string | null) => set({ error }),
    }),
    { name: 'chat-store' }
  )
);