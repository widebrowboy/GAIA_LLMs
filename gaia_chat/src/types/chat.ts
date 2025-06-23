export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  conversationId: string;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatContextType {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  isLoading: boolean;
  error: string | null;
  currentModel: string;
  currentMode: string;
  mcpEnabled: boolean;
  currentPromptType: string;
  isModelChanging: boolean;
  isModeChanging: boolean;
  isPromptChanging: boolean;
  createConversation: (title?: string) => Promise<Conversation>;
  selectConversation: (id: string) => void;
  sendMessage: (content: string) => Promise<void>;
  refreshConversations: () => Promise<void>;
  toggleMode: () => Promise<void>;
  changeModel: (model: string) => Promise<void>;
  changePromptType: (promptType: string) => Promise<void>;
  setConversations: (conversations: Conversation[]) => void;
  setCurrentConversation: (conversation: Conversation | null) => void;
}