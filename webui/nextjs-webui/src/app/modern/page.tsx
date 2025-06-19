'use client';

import { useState, useEffect } from 'react';
import { ModernChatInterface } from '@/components/chat/ModernChatInterface';
import { SystemStatus } from '@/components/chat/SystemStatus';
import { useChatStore } from '@/store/chatStore';

export default function ModernChatPage() {
  const [mounted, setMounted] = useState(false);
  const [systemReady, setSystemReady] = useState(false);
  const { currentSessionId, createSession } = useChatStore();

  useEffect(() => {
    setMounted(true);
    
    // 시스템 초기화
    const initializeSystem = async () => {
      try {
        // API 연결 확인
        const response = await fetch('/api/health');
        if (response.ok) {
          setSystemReady(true);
          
          // 기본 세션 생성
          if (!currentSessionId) {
            await createSession({
              mode: 'normal',
              prompt_type: 'default'
            });
          }
        }
      } catch (error) {
        console.error('System initialization failed:', error);
        // API 연결 실패 시에도 기본 세션 생성
        if (!currentSessionId) {
          await createSession({
            mode: 'normal',
            prompt_type: 'default'
          });
        }
        setSystemReady(true); // UI는 작동하도록 설정
      }
    };

    initializeSystem();
  }, [currentSessionId, createSession]);

  if (!mounted) {
    return (
      <div className="flex h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-blue-950 to-purple-950">
        <div className="text-center space-y-8">
          {/* 로딩 애니메이션 */}
          <div className="relative">
            <div className="w-24 h-24 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto"></div>
            <div className="absolute inset-0 w-24 h-24 border-4 border-purple-500/20 border-b-purple-500 rounded-full animate-spin mx-auto" style={{ animationDirection: 'reverse', animationDuration: '3s' }}></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">G</span>
              </div>
            </div>
          </div>
          
          {/* GAIA-BT 로고 */}
          <div className="space-y-4">
            <div className="flex items-center justify-center space-x-3">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                GAIA-BT
              </h1>
              <div className="px-3 py-1 bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-full border border-purple-400/30">
                <span className="text-sm font-medium text-purple-300">v2.0 Alpha</span>
              </div>
            </div>
            <p className="text-xl text-blue-200 font-medium">Drug Development AI Assistant</p>
            <p className="text-sm text-blue-300/80">Modern WebUI 초기화 중...</p>
          </div>
          
          {/* 기능 미리보기 */}
          <div className="grid grid-cols-3 gap-4 max-w-md mx-auto text-xs">
            <div className="p-3 bg-blue-500/10 rounded-lg border border-blue-400/20">
              <div className="text-blue-400 mb-1">🔬</div>
              <div className="text-blue-200">Deep Research</div>
            </div>
            <div className="p-3 bg-purple-500/10 rounded-lg border border-purple-400/20">
              <div className="text-purple-400 mb-1">🧬</div>
              <div className="text-purple-200">Multi-Database</div>
            </div>
            <div className="p-3 bg-cyan-500/10 rounded-lg border border-cyan-400/20">
              <div className="text-cyan-400 mb-1">⚡</div>
              <div className="text-cyan-200">Real-time</div>
            </div>
          </div>
          
          {/* 프로그레스 바 */}
          <div className="w-80 h-2 bg-slate-800 rounded-full mx-auto overflow-hidden">
            <div className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-cyan-500 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      {/* 동적 배경 그라디언트 */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-blue-950/30 to-purple-950/20"></div>
      
      {/* 애니메이션 배경 요소들 */}
      <div className="absolute inset-0 overflow-hidden">
        {/* DNA 나선 패턴 */}
        <div className="absolute top-20 left-20 w-96 h-96 opacity-3">
          <svg viewBox="0 0 200 200" className="w-full h-full animate-spin" style={{ animationDuration: '60s' }}>
            <path d="M20,100 Q100,20 180,100 Q100,180 20,100" stroke="url(#dna-gradient)" strokeWidth="1" fill="none" />
            <path d="M20,100 Q100,180 180,100 Q100,20 20,100" stroke="url(#dna-gradient)" strokeWidth="1" fill="none" />
            <defs>
              <linearGradient id="dna-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="50%" stopColor="#8b5cf6" />
                <stop offset="100%" stopColor="#06b6d4" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        
        {/* 분자 구조 패턴 */}
        <div className="absolute bottom-20 right-20 w-80 h-80 opacity-3">
          <svg viewBox="0 0 200 200" className="w-full h-full animate-pulse" style={{ animationDuration: '4s' }}>
            <circle cx="100" cy="100" r="6" fill="#3b82f6" />
            <circle cx="60" cy="60" r="4" fill="#8b5cf6" />
            <circle cx="140" cy="60" r="4" fill="#06b6d4" />
            <circle cx="60" cy="140" r="4" fill="#10b981" />
            <circle cx="140" cy="140" r="4" fill="#f59e0b" />
            <line x1="100" y1="100" x2="60" y2="60" stroke="#3b82f6" strokeWidth="1" opacity="0.5" />
            <line x1="100" y1="100" x2="140" y2="60" stroke="#3b82f6" strokeWidth="1" opacity="0.5" />
            <line x1="100" y1="100" x2="60" y2="140" stroke="#3b82f6" strokeWidth="1" opacity="0.5" />
            <line x1="100" y1="100" x2="140" y2="140" stroke="#3b82f6" strokeWidth="1" opacity="0.5" />
          </svg>
        </div>
        
        {/* 떠다니는 파티클들 */}
        <div className="absolute top-1/4 left-1/4 w-1 h-1 bg-blue-400 rounded-full animate-float opacity-40"></div>
        <div className="absolute top-3/4 left-3/4 w-2 h-2 bg-purple-400 rounded-full animate-float opacity-30" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/3 w-1 h-1 bg-cyan-400 rounded-full animate-float opacity-50" style={{ animationDelay: '4s' }}></div>
        <div className="absolute top-1/3 right-1/4 w-1 h-1 bg-green-400 rounded-full animate-float opacity-40" style={{ animationDelay: '6s' }}></div>
        <div className="absolute top-2/3 left-1/5 w-1 h-1 bg-yellow-400 rounded-full animate-float opacity-30" style={{ animationDelay: '8s' }}></div>
      </div>
      
      {/* 그리드 패턴 오버레이 */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(59,130,246,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(59,130,246,0.02)_1px,transparent_1px)] bg-[size:100px_100px]"></div>
      
      <div className="relative z-10 h-screen flex flex-col">
        {/* 메인 채팅 인터페이스 */}
        <div className="flex-1 flex container mx-auto py-6">
          <ModernChatInterface />
        </div>
      </div>
      
      {/* CSS 애니메이션 */}
      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.4; }
          25% { transform: translateY(-20px) rotate(90deg); opacity: 0.8; }
          50% { transform: translateY(-10px) rotate(180deg); opacity: 0.6; }
          75% { transform: translateY(-30px) rotate(270deg); opacity: 0.7; }
        }
        .animate-float {
          animation: float 8s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}