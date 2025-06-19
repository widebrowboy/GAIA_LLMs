export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  searchResults?: any;
  enhanced?: boolean;
}
