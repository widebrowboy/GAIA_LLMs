// GAIA-BT WebUI TypeScript 타입 정의

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  sessionId?: string;
  metadata?: MessageMetadata;
}

export interface MessageMetadata {
  mode?: 'normal' | 'deep_research';
  mcpResults?: MCPResults;
  researchProgress?: ResearchProgress;
  promptMode?: string;
}

export interface MCPResults {
  pubmed?: MCPResult[];
  chembl?: MCPResult[];
  clinical?: MCPResult[];
  variants?: MCPResult[];
}

export interface MCPResult {
  id: string;
  title: string;
  summary: string;
  source: string;
  url?: string;
  tags?: string[];
  score?: number;
  date?: string;
}

export interface ResearchProgress {
  steps: ResearchStep[];
  currentStep: number;
  totalSteps: number;
  progress: number;
  status: 'pending' | 'running' | 'completed' | 'error';
}

export interface ResearchStep {
  id: string;
  name: string;
  description: string;
  progress: number;
  status: 'pending' | 'running' | 'completed' | 'error';
  startTime?: string;
  endTime?: string;
}

export interface ChatSession {
  id: string;
  title: string;
  mode: 'normal' | 'deep_research';
  createdAt: string;
  updatedAt: string;
  messageCount: number;
}

export interface SystemStatus {
  status: 'healthy' | 'degraded' | 'error';
  cliAvailable: boolean;
  mcpAvailable: boolean;
  activeSessions: number;
  version?: string;
}

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface ChatRequest {
  content: string;
  sessionId?: string;
  mode?: 'normal' | 'deep_research';
}

export interface ChatResponse {
  response: string;
  sessionId: string;
  mode: string;
  timestamp: string;
}

export interface WebSocketMessage {
  type: 'chat_response' | 'research_progress' | 'mcp_results' | 'error' | 'status';
  content?: string;
  data?: any;
  sessionId?: string;
  timestamp: string;
}

export interface UIConfig {
  theme: 'light' | 'dark' | 'system';
  language: 'ko' | 'en';
  showMCPOutput: boolean;
  autoScroll: boolean;
  soundEnabled: boolean;
}

export interface PromptMode {
  id: string;
  name: string;
  description: string;
  category: 'general' | 'clinical' | 'research' | 'chemistry' | 'regulatory';
  active: boolean;
}

export interface ChartData {
  name: string;
  value: number;
  category?: string;
  date?: string;
}

export interface VisualizationData {
  type: 'line' | 'bar' | 'pie' | 'scatter';
  title: string;
  data: ChartData[];
  xAxis?: string;
  yAxis?: string;
  colors?: string[];
}

// 이벤트 타입
export type ChatEvent = 
  | { type: 'message_sent'; payload: Message }
  | { type: 'message_received'; payload: Message }
  | { type: 'mode_changed'; payload: { mode: 'normal' | 'deep_research' } }
  | { type: 'session_created'; payload: ChatSession }
  | { type: 'session_deleted'; payload: { sessionId: string } }
  | { type: 'error'; payload: { error: string } };

// Hook 반환 타입
export interface UseChatReturn {
  messages: Message[];
  currentSession: ChatSession | null;
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  createSession: () => Promise<string>;
  deleteSession: (sessionId: string) => Promise<void>;
  switchSession: (sessionId: string) => void;
  setMode: (mode: 'normal' | 'deep_research') => void;
}

export interface UseWebSocketReturn {
  isConnected: boolean;
  sendMessage: (message: WebSocketMessage) => void;
  lastMessage: WebSocketMessage | null;
  error: string | null;
}

// 컴포넌트 Props 타입
export interface ChatInterfaceProps {
  sessionId?: string;
  initialMode?: 'normal' | 'deep_research';
  onModeChange?: (mode: 'normal' | 'deep_research') => void;
}

export interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
  onRetry?: (messageId: string) => void;
}

export interface MessageInputProps {
  onSendMessage: (content: string) => void;
  disabled?: boolean;
  placeholder?: string;
  currentMode?: 'normal' | 'deep_research';
}

export interface ResearchPanelProps {
  className?: string;
  progress?: ResearchProgress;
  mcpResults?: MCPResults;
  onClose?: () => void;
}

export interface MCPResultsProps {
  results: MCPResults;
  onResultClick?: (result: MCPResult) => void;
}

export interface ResearchMonitorProps {
  progress: ResearchProgress | null;
  showDetails?: boolean;
}

// 설정 타입
export interface AppConfig {
  api: {
    baseUrl: string;
    timeout: number;
    retryAttempts: number;
  };
  websocket: {
    url: string;
    reconnectInterval: number;
    maxReconnectAttempts: number;
  };
  ui: UIConfig;
  features: {
    mcpEnabled: boolean;
    researchModeEnabled: boolean;
    visualizationEnabled: boolean;
  };
}

// 에러 타입
export interface APIError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
}

export interface ValidationError {
  field: string;
  message: string;
  value?: any;
}

// 유틸리티 타입
export type Nullable<T> = T | null;
export type Optional<T> = T | undefined;
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// 상수
export const MESSAGE_ROLES = {
  USER: 'user',
  ASSISTANT: 'assistant'
} as const;

export const RESEARCH_MODES = {
  NORMAL: 'normal',
  DEEP_RESEARCH: 'deep_research'
} as const;

export const PROMPT_MODES = {
  DEFAULT: 'default',
  CLINICAL: 'clinical',
  RESEARCH: 'research',
  CHEMISTRY: 'chemistry',
  REGULATORY: 'regulatory'
} as const;