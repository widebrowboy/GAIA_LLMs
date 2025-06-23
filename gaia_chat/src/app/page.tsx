'use client';

import React, { useState, useEffect } from 'react';
import { Menu } from 'lucide-react';
import Sidebar from "@/components/Sidebar";
import ChatArea from "@/components/ChatArea";
import MobileHeader from "@/components/MobileHeader";
import { useResponsive } from "@/hooks/useResponsive";
import { useSwipe } from "@/hooks/useSwipe";

export default function Home() {
  const { isMobile, isTablet, isDesktop } = useResponsive();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

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

  // 데스크톱에서는 기본적으로 사이드바 열림 (처음 로드 시에만)
  useEffect(() => {
    // localStorage에서 사이드바 상태 복원 (클라이언트 사이드에서만)
    if (typeof window !== 'undefined') {
      const savedSidebarState = localStorage.getItem('gaia-gpt-sidebar-open');
      
      if (savedSidebarState !== null) {
        setIsSidebarOpen(JSON.parse(savedSidebarState));
      } else {
        // 기본값: 데스크톱은 열림, 모바일은 닫힘
        setIsSidebarOpen(isDesktop);
      }
    } else {
      // 서버 사이드에서는 기본값만 설정
      setIsSidebarOpen(isDesktop);
    }
  }, [isDesktop]);

  // 사이드바 상태가 변경될 때 localStorage에 저장 (클라이언트 사이드에서만)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('gaia-gpt-sidebar-open', JSON.stringify(isSidebarOpen));
    }
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
  }, []);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const closeSidebar = () => {
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
          <div className={`
            ${isDesktop ? 'relative' : 'absolute inset-y-0 left-0 z-50'}
            sidebar-transition
          `}>
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

        {/* 사이드바 숨김 상태일 때 토글 버튼 */}
        {!isSidebarOpen && (
          <button
            onClick={toggleSidebar}
            className="fixed top-4 left-4 z-40 p-3 bg-white/90 backdrop-blur-sm rounded-full shadow-lg hover:bg-white hover:shadow-xl transition-all duration-200 border border-gray-200"
            title="사이드바 보이기 (Ctrl+B)"
          >
            <Menu className="w-5 h-5 text-gray-600" />
          </button>
        )}

        {/* 메인 콘텐츠 영역 - 사이드바 상태에 따라 동적 크기 조정 */}
        <div className={`
          ${isSidebarOpen ? 'flex-1' : 'w-full'} 
          flex flex-col transition-all duration-300
        `}>
          <ChatArea 
            onToggleSidebar={toggleSidebar}
            isSidebarOpen={isSidebarOpen}
          />
        </div>
      </div>
    </div>
  );
}