export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: Date;
  conversationId: string;
}

export interface Conversation {
  id: string;
  name?: string; // 'title' 대신 'name' 사용 (SimpleChatContext와 일치)
  title: string; // backward compatibility를 위해 유지
  messages: Message[];
  lastMessage?: Message; // 마지막 메시지 (선택적)
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatContextType {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  isLoading: boolean;
  error: string | null;
  sessionId: string;
  currentModel: string;
  currentMode: string;
  mcpEnabled: boolean;
  currentPromptType: string;
  isModelChanging: boolean;
  isModeChanging: boolean;
  isPromptChanging: boolean;
  isStreaming: boolean;
  streamingResponse: string;
  isConnecting: boolean;
  isWaitingForResponse: boolean;
  waitingTimer: number;
  isConnected: boolean;
  reconnectAttempts: number;
  lastHeartbeatTime?: Date | null;
  sendMessage: (content: string) => Promise<void>;
  startNewConversation: () => void;
  selectConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  changeModel: (model: string) => Promise<boolean>;
  changeMode: (mode: string) => Promise<boolean>;
  changePrompt: (promptType: string) => Promise<boolean>;
  resetSession: () => void;
  // ChatArea 컴포넌트에서 사용하는 속성들 (선택적)
  setConversations?: (conversations: Conversation[]) => void;
  setCurrentConversation?: (conversation: Conversation | null) => void;
  // MobileHeader 컴포넌트에서 사용하는 함수들 (선택적)
  toggleMode?: () => Promise<boolean | undefined>;
  createConversation?: (name?: string) => Promise<Conversation>;
}