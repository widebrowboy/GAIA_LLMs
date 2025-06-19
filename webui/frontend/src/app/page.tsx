'use client';

import { useState, useEffect } from 'react';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { Sidebar } from '@/components/chat/Sidebar';
import { Header } from '@/components/chat/Header';
import { ResearchPanel } from '@/components/research/ResearchPanel';
import { useChatStore } from '@/store/chatStore';
import { useTheme } from 'next-themes';

export default function HomePage() {
  const [mounted, setMounted] = useState(false);
  const { currentSessionId, createSession } = useChatStore();
  const { theme } = useTheme();

  useEffect(() => {
    setMounted(true);
    
    // 기본 세션 생성
    if (!currentSessionId) {
      createSession({
        mode: 'normal',
        prompt_type: 'default'
      });
    }
  }, [currentSessionId, createSession]);

  if (!mounted) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-research-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-background">
      {/* 사이드바 */}
      <div className="w-80 border-r border-border">
        <Sidebar />
      </div>

      {/* 메인 콘텐츠 */}
      <div className="flex-1 flex flex-col">
        {/* 헤더 */}
        <Header />

        {/* 채팅 및 연구 패널 */}
        <div className="flex-1 flex">
          {/* 채팅 인터페이스 */}
          <div className="flex-1">
            <ChatInterface />
          </div>

          {/* 연구 패널 (선택적 표시) */}
          {currentSessionId && (
            <div className="w-96 border-l border-border">
              <ResearchPanel />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}