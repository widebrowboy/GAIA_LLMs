export interface Message {
  id: string;
  content: string;
  /**
   * Role of the message sender: 'user', 'assistant', or 'system'
   */
  role: 'user' | 'assistant' | 'system';
  /**
   * Timestamp of the message (ISO string or Date)
   */
  timestamp: Date;
  /**
   * Conversation ID this message belongs to
   */
  conversationId: string;
  /**
   * (Optional) The original user question for assistant responses.
   * Only set for messages where role === 'assistant'.
   */
  userQuestion?: string;
  /**
   * (Optional) Indicates if the message is a complete response (streaming finished)
   */
  isComplete?: boolean;
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
  // Sidebar 컴포넌트에서 사용하는 상태 설정 함수들 (선택적)
  setCurrentModel?: (model: string) => void;
  setCurrentMode?: (mode: string) => void;
  setMcpEnabled?: (enabled: boolean) => void;
  setCurrentPromptType?: (promptType: string) => void;
}