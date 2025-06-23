# SlothGPT Next.js Complete Project

## Project Structure
```
slothgpt-nextjs/
├── package.json
├── next.config.js
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
├── .eslintrc.json
├── public/
│   └── favicon.ico
└── src/
    ├── pages/
    │   ├── _app.tsx
    │   ├── _document.tsx
    │   ├── index.tsx
    │   └── api/
    │       ├── socket.ts
    │       └── chat/
    │           ├── conversations/
    │           │   ├── index.ts
    │           │   └── [id].ts
    │           └── messages.ts
    ├── components/
    │   ├── Sidebar.tsx
    │   ├── ConversationList.tsx
    │   ├── ChatArea.tsx
    │   └── MobileHeader.tsx
    ├── contexts/
    │   └── ChatContext.tsx
    ├── lib/
    │   └── db.ts
    ├── types/
    │   └── index.ts
    └── styles/
        └── globals.css
```

## File: package.json
```json
{
  "name": "slothgpt-nextjs",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3055",
    "build": "next build",
    "start": "next start -p 3055",
    "lint": "next lint"
  },
  "dependencies": {
    "@types/node": "20.14.10",
    "@types/react": "18.3.3",
    "@types/react-dom": "18.3.0",
    "class-transformer": "^0.5.1",
    "class-validator": "^0.14.1",
    "lucide-react": "^0.395.0",
    "next": "14.2.4",
    "react": "18.3.1",
    "react-dom": "18.3.1",
    "socket.io": "^4.7.5",
    "socket.io-client": "^4.7.5",
    "typescript": "5.5.3",
    "uuid": "^9.0.1"
  },
  "devDependencies": {
    "@types/uuid": "^9.0.8",
    "autoprefixer": "^10.4.19",
    "eslint": "8.57.0",
    "eslint-config-next": "14.2.4",
    "postcss": "^8.4.39",
    "tailwindcss": "^3.4.4"
  }
}
```

## File: next.config.js
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
}

module.exports = nextConfig
```

## File: tsconfig.json
```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

## File: tailwind.config.js
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        'jakarta': ['Plus Jakarta Sans', 'sans-serif'],
      },
      colors: {
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
      },
      animation: {
        'typing': 'typing 1.4s infinite',
      },
      keyframes: {
        typing: {
          '0%, 60%, 100%': { transform: 'translateY(0)' },
          '30%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}
```

## File: postcss.config.js
```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

## File: .eslintrc.json
```json
{
  "extends": "next/core-web-vitals"
}
```

## File: src/types/index.ts
```typescript
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  conversationId: string;
  attachments?: string[];
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatState {
  conversations: Conversation[];
  activeConversation: string | null;
  isLoading: boolean;
  error: string | null;
}

export interface CreateMessageDto {
  content: string;
  conversationId: string;
  attachments?: string[];
}

export interface User {
  id: string;
  name: string;
  avatar?: string;
  isOnline: boolean;
}
```

## File: src/lib/db.ts
```typescript
import { Conversation, Message } from '@/types';
import { v4 as uuidv4 } from 'uuid';

// In-memory database (replace with real database in production)
class Database {
  private conversations: Map<string, Conversation>;

  constructor() {
    this.conversations = new Map();
    this.initializeSampleData();
  }

  private initializeSampleData() {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const sampleConversations = [
      { id: 'conv1', title: 'How to be a better person?', createdAt: today },
      { id: 'conv2', title: 'Hacking FBI server with linux', createdAt: today },
      { id: 'conv3', title: 'How to get rich from youtube as an influencer', createdAt: today },
      { id: 'conv4', title: 'Help me with web development tasks from client', createdAt: yesterday },
      { id: 'conv5', title: 'REACT NEXTJS Tutorial', createdAt: yesterday },
    ];

    sampleConversations.forEach(conv => {
      this.conversations.set(conv.id, {
        ...conv,
        messages: [],
        updatedAt: conv.createdAt,
      });
    });
  }

  getConversations(): Conversation[] {
    return Array.from(this.conversations.values()).sort(
      (a, b) => b.updatedAt.getTime() - a.updatedAt.getTime()
    );
  }

  getConversation(id: string): Conversation | null {
    return this.conversations.get(id) || null;
  }

  createConversation(title: string): Conversation {
    const conversation: Conversation = {
      id: uuidv4(),
      title,
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.conversations.set(conversation.id, conversation);
    return conversation;
  }

  async addMessage(conversationId: string, content: string, attachments?: string[]): Promise<Message | null> {
    const conversation = this.conversations.get(conversationId);
    if (!conversation) return null;

    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content,
      timestamp: new Date(),
      conversationId,
      attachments,
    };

    conversation.messages.push(userMessage);
    conversation.updatedAt = new Date();

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: this.generateAIResponse(content),
        timestamp: new Date(),
        conversationId,
      };
      conversation.messages.push(aiMessage);
      conversation.updatedAt = new Date();
    }, 1000);

    return userMessage;
  }

  private generateAIResponse(userMessage: string): string {
    const responses = [
      "That's an interesting question! Let me help you explore that topic...",
      "I understand what you're asking. Here's my perspective on this...",
      "Based on my analysis, I can provide you with the following insights...",
      "Let me break this down for you step by step...",
      "Great question! Here's what I think about that...",
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  }
}

export const db = new Database();
```

## File: src/contexts/ChatContext.tsx
```typescript
import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { io, Socket } from 'socket.io-client';
import { Conversation, Message, ChatState, CreateMessageDto } from '@/types';

interface ChatContextType extends ChatState {
  socket: Socket | null;
  sendMessage: (content: string, attachments?: string[]) => Promise<void>;
  createConversation: (title: string) => Promise<void>;
  selectConversation: (id: string) => void;
  refreshConversations: () => Promise<void>;
}

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

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const [state, setState] = useState<ChatState>({
    conversations: [],
    activeConversation: null,
    isLoading: false,
    error: null,
  });
  const [socket, setSocket] = useState<Socket | null>(null);

  // Initialize socket connection
  useEffect(() => {
    const socketInstance = io(process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:3055', {
      autoConnect: true,
    });

    socketInstance.on('connect', () => {
      console.log('Socket connected');
    });

    socketInstance.on('disconnect', () => {
      console.log('Socket disconnected');
    });

    socketInstance.on('newMessage', (message: Message) => {
      setState(prev => ({
        ...prev,
        conversations: prev.conversations.map(conv => {
          if (conv.id === message.conversationId) {
            return {
              ...conv,
              messages: [...conv.messages, message],
              updatedAt: new Date(),
            };
          }
          return conv;
        }),
      }));
    });

    setSocket(socketInstance);

    return () => {
      socketInstance.disconnect();
    };
  }, []);

  // Load conversations
  const refreshConversations = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const response = await fetch('/api/chat/conversations');
      if (!response.ok) throw new Error('Failed to load conversations');
      
      const conversations = await response.json();
      setState(prev => ({
        ...prev,
        conversations,
        isLoading: false,
        activeConversation: prev.activeConversation || (conversations[0]?.id || null),
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      }));
    }
  }, []);

  // Load conversations on mount
  useEffect(() => {
    refreshConversations();
  }, [refreshConversations]);

  // Join conversation room when active conversation changes
  useEffect(() => {
    if (socket && state.activeConversation) {
      socket.emit('joinConversation', state.activeConversation);
      
      return () => {
        socket.emit('leaveConversation', state.activeConversation);
      };
    }
  }, [socket, state.activeConversation]);

  const sendMessage = async (content: string, attachments?: string[]) => {
    if (!state.activeConversation) return;

    const messageData: CreateMessageDto = {
      content,
      conversationId: state.activeConversation,
      attachments,
    };

    try {
      const response = await fetch('/api/chat/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(messageData),
      });

      if (!response.ok) throw new Error('Failed to send message');

      // Refresh the conversation to get the updated messages
      const conversationResponse = await fetch(`/api/chat/conversations/${state.activeConversation}`);
      if (conversationResponse.ok) {
        const updatedConversation = await conversationResponse.json();
        setState(prev => ({
          ...prev,
          conversations: prev.conversations.map(conv =>
            conv.id === state.activeConversation ? updatedConversation : conv
          ),
        }));
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to send message',
      }));
    }
  };

  const createConversation = async (title: string) => {
    try {
      const response = await fetch('/api/chat/conversations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
      });

      if (!response.ok) throw new Error('Failed to create conversation');

      const newConversation = await response.json();
      setState(prev => ({
        ...prev,
        conversations: [newConversation, ...prev.conversations],
        activeConversation: newConversation.id,
      }));
    } catch (error) {
      console.error('Error creating conversation:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to create conversation',
      }));
    }
  };

  const selectConversation = (id: string) => {
    setState(prev => ({ ...prev, activeConversation: id }));
  };

  const value: ChatContextType = {
    ...state,
    socket,
    sendMessage,
    createConversation,
    selectConversation,
    refreshConversations,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
```

## File: src/styles/globals.css
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  * {
    @apply box-border;
  }

  body {
    @apply font-jakarta text-slate-800 bg-white;
  }
}

@layer components {
  .btn-primary {
    @apply bg-primary-600 text-white hover:bg-primary-700 transition-colors;
  }

  .btn-secondary {
    @apply bg-white border border-slate-300 hover:bg-slate-50 transition-colors;
  }

  .scrollbar-thin {
    scrollbar-width: thin;
    scrollbar-color: #cbd5e1 #f1f5f9;
  }

  .scrollbar-thin::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  .scrollbar-thin::-webkit-scrollbar-track {
    @apply bg-slate-100;
  }

  .scrollbar-thin::-webkit-scrollbar-thumb {
    @apply bg-slate-300 rounded;
  }

  .scrollbar-thin::-webkit-scrollbar-thumb:hover {
    @apply bg-slate-400;
  }
}
```

## File: src/pages/_app.tsx
```typescript
import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import { ChatProvider } from '@/contexts/ChatContext';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ChatProvider>
      <Component {...pageProps} />
    </ChatProvider>
  );
}
```

## File: src/pages/_document.tsx
```typescript
import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <link
          href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
```

## File: src/pages/index.tsx
```typescript
import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Sidebar from '@/components/Sidebar';
import ConversationList from '@/components/ConversationList';
import ChatArea from '@/components/ChatArea';
import MobileHeader from '@/components/MobileHeader';
import { useChatContext } from '@/contexts/ChatContext';

export default function Home() {
  const [isMobile, setIsMobile] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { conversations, activeConversation } = useChatContext();

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const currentConversation = conversations.find(c => c.id === activeConversation);

  return (
    <>
      <Head>
        <title>SlothGPT - Your AI Assistant</title>
        <meta name="description" content="SlothGPT - AI-powered chat assistant" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="flex h-screen overflow-hidden bg-white">
        {!isMobile && <Sidebar />}
        
        <div className={`flex-1 flex ${isMobile ? 'flex-col' : ''}`}>
          {isMobile && (
            <MobileHeader onMenuClick={() => setIsSidebarOpen(true)} />
          )}
          
          <ConversationList
            isOpen={isSidebarOpen}
            onClose={() => setIsSidebarOpen(false)}
            isMobile={isMobile}
          />
          
          <ChatArea conversation={currentConversation} />
        </div>
      </div>
    </>
  );
}
```

## File: src/components/Sidebar.tsx
```typescript
import React from 'react';
import {
  MessageSquare,
  Search,
  Settings,
  HelpCircle,
  Share2,
  LogOut,
} from 'lucide-react';

const Sidebar: React.FC = () => {
  const menuItems = [
    { icon: MessageSquare, active: true },
    { icon: Search },
    { icon: Share2 },
    { icon: Settings },
    { icon: HelpCircle },
    { icon: LogOut },
  ];

  return (
    <aside className="w-20 h-screen bg-white border-r border-slate-200 flex flex-col items-center py-6">
      <div className="flex-1 flex flex-col items-center gap-8">
        <div className="mb-2">
          <div className="w-8 h-8 bg-primary-600 rounded-xl flex items-center justify-center text-white font-extrabold text-sm shadow-[0_0_0_3px_rgba(255,255,255,0.32)]">
            SL
          </div>
        </div>
        
        <nav className="flex flex-col gap-4">
          {menuItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <button
                key={index}
                className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
                  item.active
                    ? 'bg-slate-50 text-primary-600'
                    : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'
                }`}
              >
                <Icon size={24} />
              </button>
            );
          })}
        </nav>
      </div>
      
      <div className="flex flex-col gap-4 items-center">
        <button className="w-12 h-12 rounded-full flex items-center justify-center text-slate-500 hover:bg-slate-50 hover:text-slate-800 transition-all">
          <Settings size={24} />
        </button>
        <div className="w-12 h-12 rounded-full overflow-hidden">
          <img
            src="https://api.dicebear.com/7.x/avatars/svg?seed=user"
            alt="User"
            className="w-full h-full object-cover"
          />
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
```

## File: src/components/ConversationList.tsx
```typescript
import React, { useState } from 'react';
import {
  Crown,
  Cpu,
  ShoppingCart,
  Lightbulb,
  ChevronDown,
  Plus,
  Sparkles,
  X,
} from 'lucide-react';
import { useChatContext } from '@/contexts/ChatContext';

interface ConversationListProps {
  isOpen: boolean;
  onClose: () => void;
  isMobile: boolean;
}

const ConversationList: React.FC<ConversationListProps> = ({
  isOpen,
  onClose,
  isMobile,
}) => {
  const { conversations, activeConversation, selectConversation, createConversation } = useChatContext();
  const [expandedSections, setExpandedSections] = useState({
    today: true,
    previous: true,
  });

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const todayConversations = conversations.filter(
    conv => new Date(conv.updatedAt) >= today
  );
  const previousConversations = conversations.filter(
    conv => new Date(conv.updatedAt) < today
  );

  const menuItems = [
    { icon: Cpu, label: 'Explore GPTs' },
    { icon: ShoppingCart, label: 'GPT Store' },
    { icon: Lightbulb, label: 'Custom Instructions' },
  ];

  const handleNewChat = async () => {
    await createConversation('New Chat');
    if (isMobile) onClose();
  };

  const handleSelectConversation = (id: string) => {
    selectConversation(id);
    if (isMobile) onClose();
  };

  return (
    <div
      className={`${
        isMobile
          ? `fixed inset-0 z-20 transform transition-transform duration-300 ${
              isOpen ? 'translate-x-0' : '-translate-x-full'
            }`
          : 'w-[360px]'
      } h-full bg-slate-50 border-r border-slate-200 flex flex-col`}
    >
      <header className="p-5 border-b border-slate-300 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <Crown size={32} className="text-primary-600" />
          <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">
            slothGPT
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleNewChat}
            className="w-10 h-10 border border-slate-300 bg-white rounded-full flex items-center justify-center text-slate-600 hover:bg-slate-50 transition-colors"
          >
            <Plus size={24} />
          </button>
          {isMobile && (
            <button
              onClick={onClose}
              className="w-10 h-10 rounded-full flex items-center justify-center text-slate-600 hover:bg-slate-200 transition-colors"
            >
              <X size={24} />
            </button>
          )}
        </div>
      </header>

      <nav className="py-4 border-b border-slate-300">
        {menuItems.map((item, index) => {
          const Icon = item.icon;
          return (
            <button
              key={index}
              className="w-full px-6 py-5 flex items-center gap-3 hover:bg-slate-200 transition-colors"
            >
              <Icon size={24} className="text-slate-800" />
              <span className="text-lg font-bold text-slate-800 tracking-tight">
                {item.label}
              </span>
            </button>
          );
        })}
      </nav>

      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {todayConversations.length > 0 && (
          <div className="border-b border-slate-300">
            <button
              onClick={() =>
                setExpandedSections({
                  ...expandedSections,
                  today: !expandedSections.today,
                })
              }
              className="w-full px-6 py-3.5 flex items-center justify-between hover:bg-slate-100 transition-colors"
            >
              <span className="text-lg font-bold text-slate-800 tracking-tight">
                Today
              </span>
              <div className="flex items-center gap-3">
                <span className="text-base font-medium text-slate-600 tracking-tight">
                  {todayConversations.length} Total
                </span>
                <ChevronDown
                  size={24}
                  className={`text-slate-600 transition-transform ${
                    expandedSections.today ? 'rotate-180' : ''
                  }`}
                />
              </div>
            </button>
            {expandedSections.today && (
              <div className="pb-2">
                {todayConversations.map(conv => (
                  <button
                    key={conv.id}
                    onClick={() => handleSelectConversation(conv.id)}
                    className={`w-full px-6 py-3 text-left text-base font-medium tracking-tight transition-colors ${
                      activeConversation === conv.id
                        ? 'bg-primary-50 text-slate-800 border-l-2 border-primary-600'
                        : 'text-slate-800 hover:bg-slate-200'
                    }`}
                  >
                    {conv.title}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {previousConversations.length > 0 && (
          <div className="border-b border-slate-300">
            <button
              onClick={() =>
                setExpandedSections({
                  ...expandedSections,
                  previous: !expandedSections.previous,
                })
              }
              className="w-full px-6 py-3.5 flex items-center justify-between hover:bg-slate-100 transition-colors"
            >
              <span className="text-lg font-bold text-slate-800 tracking-tight">
                Previous 7 Days
              </span>
              <div className="flex items-center gap-3">
                <span className="text-base font-medium text-slate-600 tracking-tight">
                  {previousConversations.length}
                </span>
                <ChevronDown
                  size={24}
                  className={`text-slate-600 transition-transform ${
                    expandedSections.previous ? 'rotate-180' : ''
                  }`}
                />
              </div>
            </button>
            {expandedSections.previous && (
              <div className="pb-2">
                {previousConversations.map(conv => (
                  <button
                    key={conv.id}
                    onClick={() => handleSelectConversation(conv.id)}
                    className={`w-full px-6 py-3 text-left text-base font-medium tracking-tight transition-colors ${
                      activeConversation === conv.id
                        ? 'bg-primary-50 text-slate-800 border-l-2 border-primary-600'
                        : 'text-slate-800 hover:bg-slate-200'
                    }`}
                  >
                    {conv.title}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="p-5 flex items-center gap-4">
        <div className="w-12 h-12 bg-primary-50 rounded-full flex items-center justify-center text-primary-600">
          <Sparkles size={24} />
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-800 tracking-tight">
            Upgrade Plan
          </h3>
          <p className="text-sm text-slate-600">Get GPT-8 and more</p>
        </div>
      </div>
    </div>
  );
};

export default ConversationList;
```

## File: src/components/ChatArea.tsx
```typescript
import React, { useState, useRef, useEffect } from 'react';
import {
  User,
  ChevronDown,
  Paperclip,
  Send,
  Copy,
  RefreshCw,
  ThumbsDown,
  Volume2,
  Wand2,
  ChevronLeft,
  ChevronRight,
  Cpu,
  Plus,
  Settings,
  Share2,
  HelpCircle,
  Mic,
} from 'lucide-react';
import { Conversation, Message } from '@/types';
import { useChatContext } from '@/contexts/ChatContext';

interface ChatAreaProps {
  conversation?: Conversation;
}

const ChatArea: React.FC<ChatAreaProps> = ({ conversation }) => {
  const { sendMessage, socket } = useChatContext();
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages]);

  useEffect(() => {
    if (socket && conversation) {
      socket.on('userTyping', ({ isTyping: typing }) => {
        setIsTyping(typing);
      });

      return () => {
        socket.off('userTyping');
      };
    }
  }, [socket, conversation]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && conversation) {
      await sendMessage(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  };

  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(date));
  };

  if (!conversation) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl text-slate-500">Select a conversation to start chatting</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      <header className="h-20 border-b border-slate-300 flex items-center justify-between px-8">
        <div className="flex items-center gap-8">
          <button className="flex items-center gap-2 text-slate-600 hover:text-slate-800 transition-colors">
            <User size={24} />
            <span className="text-lg font-bold tracking-tight">sloth GPT 7.0</span>
            <ChevronDown size={24} />
          </button>
        </div>
        
        <div className="flex items-center gap-2">
          <button className="w-10 h-10 bg-primary-50 rounded-full flex items-center justify-center text-primary-600 hover:bg-primary-100 transition-colors">
            <Plus size={20} />
          </button>
          <button className="w-10 h-10 border border-slate-300 rounded-full flex items-center justify-center text-slate-600 hover:bg-slate-50 transition-colors">
            <Settings size={20} />
          </button>
          <div className="w-px h-6 bg-slate-300 mx-2" />
          <button className="w-10 h-10 border border-slate-300 rounded-full flex items-center justify-center text-slate-600 hover:bg-slate-50 transition-colors">
            <Share2 size={20} />
          </button>
          <button className="w-10 h-10 border border-slate-300 rounded-full flex items-center justify-center text-slate-600 hover:bg-slate-50 transition-colors">
            <HelpCircle size={20} />
          </button>
          <div className="relative w-10 h-10 ml-2">
            <img
              src="https://api.dicebear.com/7.x/avatars/svg?seed=user"
              alt="User"
              className="w-full h-full rounded-full object-cover"
            />
            <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-500 border-2 border-white rounded-full"></span>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-8 scrollbar-thin">
        {conversation.messages.map((msg, index) => (
          <div key={msg.id} className="flex gap-3 mb-8">
            <div className="flex-shrink-0">
              {msg.role === 'user' ? (
                <img
                  src="https://api.dicebear.com/7.x/avatars/svg?seed=user"
                  alt="User"
                  className="w-12 h-12 rounded-full"
                />
              ) : (
                <div className="w-12 h-12 bg-primary-50 rounded-full flex items-center justify-center text-primary-600">
                  <Cpu size={28} />
                </div>
              )}
            </div>
            <div className="flex-1 max-w-[748px]">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-base font-bold text-slate-800 tracking-tight">
                  {msg.role === 'user' ? 'You' : 'slothGPT'}
                </span>
                <span className="text-sm font-medium text-slate-400 tracking-tight">
                  {formatTime(msg.timestamp)}
                </span>
              </div>
              <div className="bg-slate-50 rounded-3xl px-6 py-3">
                <p className="text-base text-slate-600 leading-relaxed">{msg.content}</p>
              </div>
              {msg.role === 'assistant' && index === conversation.messages.length - 1 && (
                <div className="flex gap-4 mt-3">
                  <button className="text-slate-500 hover:text-slate-800 transition-colors">
                    <Volume2 size={24} />
                  </button>
                  <button className="text-slate-500 hover:text-slate-800 transition-colors">
                    <Copy size={24} />
                  </button>
                  <button className="text-slate-500 hover:text-slate-800 transition-colors">
                    <RefreshCw size={24} />
                  </button>
                  <button className="text-slate-500 hover:text-slate-800 transition-colors">
                    <ThumbsDown size={24} />
                  </button>
                  <button className="text-slate-500 hover:text-slate-800 transition-colors">
                    <Wand2 size={24} />
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex gap-3 mb-8">
            <div className="w-12 h-12 bg-primary-50 rounded-full flex items-center justify-center text-primary-600">
              <Cpu size={28} />
            </div>
            <div className="flex items-center">
              <div className="bg-slate-50 rounded-2xl px-4 py-2">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-typing"></span>
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-typing animation-delay-200"></span>
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-typing animation-delay-400"></span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-8">
        <div className="flex items-end gap-3 p-3 bg-white border border-slate-300 rounded-full mb-2">
          <button type="button" className="p-2 text-slate-500 hover:text-slate-800 transition-colors">
            <Paperclip size={24} />
          </button>
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            placeholder="Message slothGPT..."
            className="flex-1 px-3 py-2 bg-transparent outline-none resize-none text-base font-medium text-slate-800 placeholder-slate-500 tracking-tight max-h-[120px]"
            rows={1}
          />
          <div className="flex gap-1">
            <button type="button" className="p-2 text-slate-500 hover:text-slate-800 transition-colors">
              <Mic size={24} />
            </button>
            <button
              type="submit"
              disabled={!message.trim()}
              className={`p-2 rounded-full transition-all ${
                message.trim()
                  ? 'bg-primary-600 text-white hover:bg-primary-700'
                  : 'bg-slate-200 text-slate-400 cursor-not-allowed'
              }`}
            >
              <Send size={24} />
            </button>
          </div>
        </div>
        <p className="text-center text-sm font-medium text-slate-400 tracking-tight">
          slothGPT can make mistakes. Check our Terms & Conditions.
        </p>
      </form>
    </div>
  );
};

export default ChatArea;
```

## File: src/components/MobileHeader.tsx
```typescript
import React from 'react';
import { Menu, Plus } from 'lucide-react';
import { useChatContext } from '@/contexts/ChatContext';

interface MobileHeaderProps {
  onMenuClick: () => void;
}

const MobileHeader: React.FC<MobileHeaderProps> = ({ onMenuClick }) => {
  const { createConversation } = useChatContext();

  const handleNewChat = async () => {
    await createConversation('New Chat');
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 md:hidden">
      <button
        onClick={onMenuClick}
        className="w-10 h-10 flex items-center justify-center text-slate-600 hover:bg-slate-50 rounded-lg transition-colors"
      >
        <Menu size={24} />
      </button>
      
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 bg-primary-600 rounded-xl flex items-center justify-center text-white font-extrabold text-sm">
          SL
        </div>
      </div>
      
      <button
        onClick={handleNewChat}
        className="w-10 h-10 flex items-center justify-center text-slate-600 hover:bg-slate-50 rounded-lg transition-colors"
      >
        <Plus size={24} />
      </button>
    </header>
  );
};

export default MobileHeader;
```

## File: src/pages/api/socket.ts
```typescript
import { Server } from 'socket.io';
import type { NextApiRequest, NextApiResponse } from 'next';
import type { Server as HTTPServer } from 'http';
import type { Socket as NetSocket } from 'net';

interface SocketServer extends HTTPServer {
  io?: Server;
}

interface SocketWithIO extends NetSocket {
  server: SocketServer;
}

interface NextApiResponseWithSocket extends NextApiResponse {
  socket: SocketWithIO;
}

const SocketHandler = (_: NextApiRequest, res: NextApiResponseWithSocket) => {
  if (res.socket.server.io) {
    console.log('Socket is already running');
  } else {
    console.log('Socket is initializing');
    const io = new Server(res.socket.server, {
      path: '/api/socket',
      cors: {
        origin: '*',
        methods: ['GET', 'POST'],
      },
    });

    res.socket.server.io = io;

    io.on('connection', (socket) => {
      console.log(`Client connected: ${socket.id}`);

      socket.on('joinConversation', (conversationId: string) => {
        socket.join(conversationId);
        console.log(`Client ${socket.id} joined conversation ${conversationId}`);
      });

      socket.on('leaveConversation', (conversationId: string) => {
        socket.leave(conversationId);
        console.log(`Client ${socket.id} left conversation ${conversationId}`);
      });

      socket.on('typing', (data: { conversationId: string; isTyping: boolean }) => {
        socket.to(data.conversationId).emit('userTyping', {
          userId: socket.id,
          isTyping: data.isTyping,
        });
      });

      socket.on('disconnect', () => {
        console.log(`Client disconnected: ${socket.id}`);
      });
    });
  }
  res.end();
};

export default SocketHandler;
```

## File: src/pages/api/chat/conversations/index.ts
```typescript
import type { NextApiRequest, NextApiResponse } from 'next';
import { db } from '@/lib/db';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    const conversations = db.getConversations();
    res.status(200).json(conversations);
  } else if (req.method === 'POST') {
    const { title } = req.body;
    if (!title) {
      return res.status(400).json({ error: 'Title is required' });
    }
    const conversation = db.createConversation(title);
    res.status(201).json(conversation);
  } else {
    res.setHeader('Allow', ['GET', 'POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
```

## File: src/pages/api/chat/conversations/[id].ts
```typescript
import type { NextApiRequest, NextApiResponse } from 'next';
import { db } from '@/lib/db';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const { id } = req.query;

  if (req.method === 'GET') {
    const conversation = db.getConversation(id as string);
    if (!conversation) {
      return res.status(404).json({ error: 'Conversation not found' });
    }
    res.status(200).json(conversation);
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
```

## File: src/pages/api/chat/messages.ts
```typescript
import type { NextApiRequest, NextApiResponse } from 'next';
import { db } from '@/lib/db';
import type { Server } from 'socket.io';

interface ExtendedNextApiResponse extends NextApiResponse {
  socket: any;
}

export default async function handler(req: NextApiRequest, res: ExtendedNextApiResponse) {
  if (req.method === 'POST') {
    const { content, conversationId, attachments } = req.body;

    if (!content || !conversationId) {
      return res.status(400).json({ error: 'Content and conversationId are required' });
    }

    const message = await db.addMessage(conversationId, content, attachments);
    if (!message) {
      return res.status(404).json({ error: 'Conversation not found' });
    }

    // Emit to WebSocket if available
    const io = res.socket.server.io as Server;
    if (io) {
      io.to(conversationId).emit('newMessage', message);
      
      // Emit AI response after delay
      setTimeout(() => {
        const conversation = db.getConversation(conversationId);
        if (conversation && conversation.messages.length > 0) {
          const aiResponse = conversation.messages[conversation.messages.length - 1];
          io.to(conversationId).emit('newMessage', aiResponse);
        }
      }, 1500);
    }

    res.status(201).json(message);
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
```

## Installation & Run Commands

```bash
# Create project directory
mkdir slothgpt-nextjs
cd slothgpt-nextjs

# Initialize project with package.json above
npm init -y

# Install dependencies
npm install

# Create all files according to the structure above

# Run development server
npm run dev

# Build for production
npm run build
npm start
```

## Environment Variables (.env.local)
```
NEXT_PUBLIC_SOCKET_URL=http://localhost:3055
```

Project will run on http://localhost:3055