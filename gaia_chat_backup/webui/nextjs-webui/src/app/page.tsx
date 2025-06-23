'use client';

import { useEffect } from 'react';
import { useChatStore } from '@/store/chatStore';
import { UnifiedChatInterface } from '@/components/chat/UnifiedChatInterface';

export default function Home() {
  const { currentSessionId, createSession } = useChatStore();

  // 세션 초기화
  useEffect(() => {
    const initializeSession = async () => {
      if (!currentSessionId) {
        try {
          await createSession();
        } catch (error) {
          console.error('Failed to create session:', error);
        }
      }
    };

    initializeSession();
  }, [currentSessionId, createSession]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <UnifiedChatInterface 
        variant="gaia"
        features={{
          mcp: true,
          markdown: true,
          promptSelector: true,
          modeToggle: true,
          voiceInput: false,
          fileUpload: false
        }}
      />
    </div>
  );
}