'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Menu } from 'lucide-react';
import Sidebar from "@/components/Sidebar";
import ChatArea from "@/components/ChatArea";
import MobileHeader from "@/components/MobileHeader";
import { useResponsive } from "@/hooks/useResponsive";
import { useSwipe } from "@/hooks/useSwipe";

export default function Home() {
  const { isMobile, isDesktop } = useResponsive();
  // 사이드바 상태 초기화: 기본값은 데스크톱에서는 true, 모바일에서는 false
  // hydration 불일치를 방지하기 위해 초기 상태는 서버/클라이언트 모두 동일하게 설정
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // 스와이프 제스처 설정
  const swipeRef = useSwipe({
    onSwipeLeft: () => {
      if (isSidebarOpen) {
        closeSidebar();
      }
    },
    onSwipeRight: () => {
      if (!isSidebarOpen) {
        setIsSidebarOpen(true);
      }
    },
    threshold: 100
  });

  // localStorage에서 사이드바 상태 복원 (클라이언트 사이드에서만)
  useEffect(() => {
    // 클라이언트 사이드에서만 실행되는 코드
    const saved = localStorage.getItem('gaia-gpt-sidebar-open');
    if (saved !== null) {
      setIsSidebarOpen(JSON.parse(saved));
    } else {
      // localStorage에 값이 없으면 기본값 설정 (데스크톱은 true, 모바일은 false)
      setIsSidebarOpen(isDesktop);
    }
  }, [isDesktop]);

  // 사이드바 상태가 변경될 때 localStorage에 저장 (클라이언트 사이드에서만)
  useEffect(() => {
    // useEffect 자체가 클라이언트 사이드에서만 실행됨
    localStorage.setItem('gaia-gpt-sidebar-open', JSON.stringify(isSidebarOpen));
  }, [isSidebarOpen]);

  const toggleSidebar = useCallback(() => {
    // 모든 환경에서 토글이 가능하도록 수정
    setIsSidebarOpen(!isSidebarOpen);
  }, [isSidebarOpen]);

  // 키보드 단축키 (Ctrl/Cmd + B로 사이드바 토글)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        toggleSidebar();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [toggleSidebar]);

  const closeSidebar = () => {
    // 모든 환경에서 사이드바를 닫을 수 있도록 수정
    setIsSidebarOpen(false);
  };

  return (
    <div ref={swipeRef} className="h-screen flex flex-col bg-gradient-to-b from-gray-50 to-white overflow-hidden">
      {/* 모바일 헤더 */}
      {isMobile && (
        <MobileHeader 
          onMenuToggle={toggleSidebar}
          isSidebarOpen={isSidebarOpen}
        />
      )}
      
      <div className="flex-1 flex relative overflow-hidden">
        {/* 사이드바 */}
        {isSidebarOpen && (
          <div className={`${isDesktop ? 'relative h-full' : 'absolute inset-y-0 left-0 z-50 h-full'} sidebar-transition`}>
            <Sidebar onClose={closeSidebar} />
          </div>
        )}

        {/* 모바일/태블릿 오버레이 */}
        {!isDesktop && isSidebarOpen && (
          <div 
            className="absolute inset-0 bg-black bg-opacity-50 z-40 overlay-enter"
            onClick={closeSidebar}
          />
        )}

        {/* 사이드바 숨김 상태일 때 토글 버튼 - 모바일/태블릿에서만 표시 */}
        {!isSidebarOpen && !isDesktop && (
          <button
            onClick={toggleSidebar}
            className="fixed top-4 left-4 z-40 p-3 bg-white/90 backdrop-blur-sm rounded-full shadow-lg hover:bg-white hover:shadow-xl transition-all duration-200 border border-gray-200"
            title="사이드바 보이기 (Ctrl+B)"
          >
            <Menu className="w-5 h-5 text-gray-600" />
          </button>
        )}

        {/* 메인 콘텐츠 영역 - 사이드바 상태에 따라 동적 크기 조정 */}
        <div className={`${isSidebarOpen ? 'flex-1' : 'w-full'} flex flex-col transition-all duration-300`}>
          <ChatArea 
            onToggleSidebar={toggleSidebar}
            isSidebarOpen={isSidebarOpen}
          />
        </div>
      </div>
    </div>
  );
}