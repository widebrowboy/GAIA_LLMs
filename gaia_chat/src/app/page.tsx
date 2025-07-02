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
  // 사이드바 열림 상태를 useState로 관리
  const [isSidebarOpen, setIsSidebarOpen] = useState(isDesktop);
  const toggleSidebar = useCallback(() => setIsSidebarOpen((prev) => !prev), []);
  const closeSidebar = useCallback(() => setIsSidebarOpen(false), []);

  // ESC 키로 사이드바 닫기
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isSidebarOpen) {
        closeSidebar();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isSidebarOpen, closeSidebar]);

  return (
    <div className="fixed inset-0 flex flex-col bg-gradient-to-b from-gray-50 to-white">
      {/* 모바일 헤더 - 모바일일 때만 렌더링 */}
      {isMobile && (
        <MobileHeader 
          onMenuToggle={toggleSidebar}
          isSidebarOpen={isSidebarOpen}
        />
      )}
      
      {/* 메인 레이아웃 영역 */}
      <main className="flex flex-1 min-h-0">
        {/* 데스크톱용 사이드바 - 모바일이 아니고 사이드바가 열려있을 때만 표시 */}
        {!isMobile && isSidebarOpen && (
          <aside className="w-1/4 min-w-[240px] max-w-[320px] border-r border-gray-200 bg-white flex-shrink-0">
            <Sidebar onClose={closeSidebar} onToggle={toggleSidebar} isMobileSidebarOpen={false} isSidebarOpen={isSidebarOpen} />
          </aside>
        )}
        
        {/* ChatArea - 전체 크기 차지 */}
        <ChatArea onToggleSidebar={toggleSidebar} isSidebarOpen={isSidebarOpen} />
        
        {/* 모바일용 사이드바 오버레이 - 모바일이고 사이드바가 열려있을 때만 표시 */}
        {isMobile && isSidebarOpen && (
          <>
            {/* 배경 오버레이 - 클릭 시 사이드바 닫기 */}
            <div 
              className="fixed inset-0 z-40 bg-black bg-opacity-50"
              onClick={closeSidebar}
              aria-label="사이드바 닫기"
            />
            {/* 사이드바 */}
            <aside className="fixed inset-y-0 left-0 z-50 w-full max-w-xs h-full bg-white shadow-lg">
              <Sidebar onClose={closeSidebar} onToggle={toggleSidebar} isMobileSidebarOpen={true} isSidebarOpen={isSidebarOpen} />
            </aside>
          </>
        )}
      </main>
    </div>
  );
}