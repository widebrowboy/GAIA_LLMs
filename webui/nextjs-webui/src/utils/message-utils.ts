// Message grouping and formatting utilities

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
  sources?: Array<{ name: string; url?: string }>;
  error?: string;
  model?: string;
}

export interface MessageGroup {
  sender: 'user' | 'assistant' | 'system';
  messages: Message[];
  startTime: Date;
  endTime: Date;
  showTimestamp: boolean;
}

// Group consecutive messages from the same sender within 5 minutes
export function groupMessages(messages: Message[]): MessageGroup[] {
  if (!messages || messages.length === 0) return [];
  
  const TIME_THRESHOLD = 5 * 60 * 1000; // 5 minutes
  const groups: MessageGroup[] = [];
  let currentGroup: MessageGroup | null = null;
  
  messages.forEach((message, index) => {
    const isNewGroup = !currentGroup || 
                      currentGroup.sender !== message.role ||
                      (message.timestamp.getTime() - currentGroup.endTime.getTime()) > TIME_THRESHOLD;
    
    if (isNewGroup) {
      if (currentGroup) {
        groups.push(currentGroup);
      }
      currentGroup = {
        sender: message.role,
        messages: [message],
        startTime: message.timestamp,
        endTime: message.timestamp,
        showTimestamp: shouldShowTimestamp(message.timestamp, groups[groups.length - 1]?.endTime)
      };
    } else {
      currentGroup.messages.push(message);
      currentGroup.endTime = message.timestamp;
    }
  });
  
  if (currentGroup) {
    groups.push(currentGroup);
  }
  
  return groups;
}

// Determine if timestamp should be shown (show if more than 5 minutes gap)
function shouldShowTimestamp(current: Date, previous?: Date): boolean {
  if (!previous) return true;
  return (current.getTime() - previous.getTime()) > 5 * 60 * 1000;
}

// Format timestamp for display
export function formatTimestamp(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (seconds < 60) return '방금 전';
  if (minutes < 60) return `${minutes}분 전`;
  if (hours < 24) return `${hours}시간 전`;
  if (days < 7) return `${days}일 전`;
  
  // Format as date for older messages
  const options: Intl.DateTimeFormatOptions = {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };
  
  if (date.getFullYear() !== now.getFullYear()) {
    options.year = 'numeric';
  }
  
  return new Intl.DateTimeFormat('ko-KR', options).format(date);
}

// Get relative time description for continuous updates
export function getRelativeTime(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const seconds = Math.floor(diff / 1000);
  
  if (seconds < 2) return '지금';
  if (seconds < 60) return `${seconds}초 전`;
  
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}분 전`;
  
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}시간 전`;
  
  const days = Math.floor(hours / 24);
  return `${days}일 전`;
}

// Extract markdown code blocks
export function extractCodeBlocks(content: string): Array<{language: string; code: string; index: number}> {
  const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
  const blocks: Array<{language: string; code: string; index: number}> = [];
  let match;
  
  while ((match = codeBlockRegex.exec(content)) !== null) {
    blocks.push({
      language: match[1] || 'plaintext',
      code: match[2].trim(),
      index: match.index
    });
  }
  
  return blocks;
}

// Parse markdown links
export function parseMarkdownLinks(content: string): Array<{text: string; url: string}> {
  const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
  const links: Array<{text: string; url: string}> = [];
  let match;
  
  while ((match = linkRegex.exec(content)) !== null) {
    links.push({
      text: match[1],
      url: match[2]
    });
  }
  
  return links;
}