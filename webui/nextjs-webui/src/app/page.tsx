'use client';

import { useState, useEffect } from 'react';
import { WebChatInterface } from '@/components/chat/WebChatInterface';
import { StartupBanner } from '@/components/chat/StartupBanner';
import { SystemStatus } from '@/components/chat/SystemStatus';
import { useChatStore } from '@/store/chatStore';

export default function HomePage() {
  const [mounted, setMounted] = useState(false);
  const [showBanner, setShowBanner] = useState(true);
  const [systemReady, setSystemReady] = useState(false);
  const { currentSessionId, createSession } = useChatStore();

  useEffect(() => {
    setMounted(true);
    
    // 시스템 초기화
    const initializeSystem = async () => {
      try {
        // API 연결 확인
        const response = await fetch('/api/system/info');
        if (response.ok) {
          setSystemReady(true);
          
          // 기본 세션 생성
          if (!currentSessionId) {
            await createSession({
              mode: 'normal',
              prompt_type: 'default'
            });
          }
          
          // 3초 후 배너 숨김
          setTimeout(() => setShowBanner(false), 3000);
        }
      } catch (error) {
        console.error('System initialization failed:', error);
      }
    };

    initializeSystem();
  }, [currentSessionId, createSession]);

  if (!mounted) {
    return (
      <div className="flex h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900">
        <div className="text-center space-y-6">
          {/* 로딩 애니메이션 */}
          <div className="relative">
            <div className="w-20 h-20 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto"></div>
            <div className="absolute inset-0 w-20 h-20 border-4 border-purple-500/20 border-b-purple-500 rounded-full animate-spin mx-auto" style={{ animationDirection: 'reverse', animationDuration: '3s' }}></div>
          </div>
          
          {/* GAIA-BT 로고 */}
          <div className="space-y-2">
            <div className="flex items-center justify-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">G</span>
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                GAIA-BT
              </h1>
            </div>
            <p className="text-lg text-blue-200">AI-Powered Drug Discovery Platform</p>
            <p className="text-sm text-blue-300/80">시스템 초기화 중...</p>
          </div>
          
          {/* 프로그레스 바 */}
          <div className="w-64 h-1 bg-slate-800 rounded-full mx-auto overflow-hidden">
            <div className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 relative overflow-hidden">
      {/* 동적 배경 그라디언트 */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-950/50 to-purple-950/30"></div>
      
      {/* 애니메이션 배경 요소들 */}
      <div className="absolute inset-0">
        {/* DNA 나선 패턴 */}
        <div className="absolute top-20 left-20 w-96 h-96 opacity-5">
          <svg viewBox="0 0 200 200" className="w-full h-full animate-spin" style={{ animationDuration: '30s' }}>
            <path d="M20,100 Q100,20 180,100 Q100,180 20,100" stroke="url(#dna-gradient)" strokeWidth="2" fill="none" />
            <path d="M20,100 Q100,180 180,100 Q100,20 20,100" stroke="url(#dna-gradient)" strokeWidth="2" fill="none" />
            <defs>
              <linearGradient id="dna-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="100%" stopColor="#8b5cf6" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        
        {/* 분자 구조 패턴 */}
        <div className="absolute bottom-20 right-20 w-80 h-80 opacity-5">
          <svg viewBox="0 0 200 200" className="w-full h-full animate-pulse">
            <circle cx="100" cy="100" r="8" fill="#3b82f6" />
            <circle cx="60" cy="60" r="6" fill="#8b5cf6" />
            <circle cx="140" cy="60" r="6" fill="#06b6d4" />
            <circle cx="60" cy="140" r="6" fill="#10b981" />
            <circle cx="140" cy="140" r="6" fill="#f59e0b" />
            <line x1="100" y1="100" x2="60" y2="60" stroke="#3b82f6" strokeWidth="2" />
            <line x1="100" y1="100" x2="140" y2="60" stroke="#3b82f6" strokeWidth="2" />
            <line x1="100" y1="100" x2="60" y2="140" stroke="#3b82f6" strokeWidth="2" />
            <line x1="100" y1="100" x2="140" y2="140" stroke="#3b82f6" strokeWidth="2" />
          </svg>
        </div>
        
        {/* 떠다니는 파티클들 */}
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-blue-400 rounded-full animate-float opacity-60"></div>
        <div className="absolute top-3/4 left-3/4 w-3 h-3 bg-purple-400 rounded-full animate-float opacity-40" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/3 w-1 h-1 bg-cyan-400 rounded-full animate-float opacity-80" style={{ animationDelay: '4s' }}></div>
        <div className="absolute top-1/3 right-1/4 w-2 h-2 bg-green-400 rounded-full animate-float opacity-50" style={{ animationDelay: '6s' }}></div>
      </div>
      
      {/* 그리드 패턴 오버레이 */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(59,130,246,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(59,130,246,0.03)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
      
      {showBanner && <StartupBanner onClose={() => setShowBanner(false)} />}
      
      <div className="relative z-10 h-screen flex flex-col">
        {/* 시스템 상태 헤더 */}
        <SystemStatus isReady={systemReady} />
        
        {/* 메인 채팅 인터페이스 */}
        <div className="flex-1 flex container mx-auto max-w-7xl px-4">
          <WebChatInterface />
        </div>
      </div>
      
      {/* CSS 애니메이션 */}
      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          33% { transform: translateY(-10px) rotate(120deg); }
          66% { transform: translateY(5px) rotate(240deg); }
        }
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}