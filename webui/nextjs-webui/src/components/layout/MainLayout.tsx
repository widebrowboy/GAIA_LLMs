'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from './Sidebar';
import Header from './Header';
import ChatArea from '../chat/ChatArea';
import MobileNavigation, { MobileTabs } from '../mobile/mobile-navigation';
import { useChatStore } from '@/store/chatStore';
import { useLayoutConfig } from '@/hooks/use-layout-config';
import { useMobile } from '@/hooks/use-mobile';
import { useSwipe } from '@/hooks/use-touch-gestures';
import { ResizeHandle } from '@/components/ui/resize-handle';
import { TouchButton, FloatingActionButton } from '@/components/ui/touch-button';
import { 
  Menu, 
  MessageSquare, 
  Database, 
  Settings, 
  HelpCircle,
  Plus
} from 'lucide-react';

interface MainLayoutProps {
  children?: React.ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  const isMobile = useMobile();
  const [showMobileNav, setShowMobileNav] = useState(false);
  const [currentMobilePage, setCurrentMobilePage] = useState('chat');
  const [mobileTabBadges, setMobileTabBadges] = useState<Record<string, number>>({});
  const mainRef = useRef<HTMLDivElement>(null);
  
  const { currentSessionId, createSession, sessions } = useChatStore();
  
  const {
    config,
    currentBreakpoint,
    isDragging,
    updateConfig,
    handleSidebarResize,
    startDragging,
    stopDragging,
    toggleSidebarCollapse
  } = useLayoutConfig();

  // 스와이프 제스처로 사이드바 제어 (모바일)
  useSwipe(mainRef, {
    onSwipeRight: () => {
      if (isMobile && !showMobileNav) {
        setShowMobileNav(true);
      }
    },
    onSwipeLeft: () => {
      if (isMobile && showMobileNav) {
        setShowMobileNav(false);
      }
    }
  }, {
    minSwipeDistance: 80,
    preventScroll: false
  });

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

  // Determine if sidebar should be shown
  const showSidebar = !config.sidebarCollapsed && (currentBreakpoint.showSidebar || isMobile);
  
  // Layout grid configuration based on mode and breakpoint
  const getLayoutClasses = () => {
    const { gridConfig } = currentBreakpoint;
    const densityPadding = {
      compact: 'p-2',
      normal: gridConfig.padding,
      comfortable: 'p-6'
    };
    
    return {
      container: `${gridConfig.containerWidth} ${densityPadding[config.density]}`,
      gap: gridConfig.gap,
      grid: config.mode === 'spacious' && gridConfig.columns > 1 
        ? `grid grid-cols-${gridConfig.columns}` 
        : 'flex flex-col'
    };
  };

  const layoutClasses = getLayoutClasses();

  // 모바일 네비게이션 핸들러
  const handleMobileNavigation = (page: string) => {
    setCurrentMobilePage(page);
    // 페이지별 로직 처리
    switch (page) {
      case 'chat':
        // 채팅 페이지로 이동
        break;
      case 'history':
        // 히스토리 페이지로 이동
        break;
      case 'settings':
        // 설정 페이지로 이동
        break;
      case 'help':
        // 도움말 페이지로 이동
        break;
    }
  };

  // 모바일 탭 설정
  const mobileTabs = [
    { 
      id: 'chat', 
      label: '채팅', 
      icon: MessageSquare,
      badge: sessions[currentSessionId]?.messages.length > 0 ? 1 : 0
    },
    { 
      id: 'history', 
      label: '기록', 
      icon: Database,
      badge: Object.keys(sessions).length
    },
    { 
      id: 'settings', 
      label: '설정', 
      icon: Settings 
    },
    { 
      id: 'help', 
      label: '도움말', 
      icon: HelpCircle 
    },
  ];

  if (isMobile) {
    // 모바일 레이아웃
    return (
      <motion.div 
        ref={mainRef}
        className="flex h-full w-full relative bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        {/* 모바일 네비게이션 */}
        <MobileNavigation
          isOpen={showMobileNav}
          onToggle={() => setShowMobileNav(!showMobileNav)}
          onNavigate={handleMobileNavigation}
          currentPage={currentMobilePage}
        />

        {/* 모바일 메인 콘텐츠 */}
        <div className="flex-1 flex flex-col">
          {/* 모바일 헤더 - 간소화 */}
          <motion.div 
            className="flex items-center justify-between p-4 bg-gray-900/50 backdrop-blur-sm border-b border-gray-700"
            initial={{ y: -50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.1, duration: 0.3 }}
          >
            <TouchButton
              variant="ghost"
              size="sm"
              onClick={() => setShowMobileNav(true)}
              className="text-white"
            >
              <Menu className="h-6 w-6" />
            </TouchButton>
            
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-lg flex items-center justify-center">
                <Database className="h-3 w-3 text-white" />
              </div>
              <h1 className="text-lg font-bold text-white">GAIA-BT</h1>
            </div>
            
            <TouchButton
              variant="ghost"
              size="sm"
              className="text-white opacity-50"
            >
              <Settings className="h-5 w-5" />
            </TouchButton>
          </motion.div>

          {/* 모바일 채팅 영역 */}
          <motion.div 
            className="flex-1 overflow-hidden"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.4 }}
          >
            {children || (
              <ChatArea 
                layoutConfig={{
                  mode: 'compact', // 모바일에서는 항상 컴팩트 모드
                  density: 'normal',
                  fontSize: 'medium',
                  gridConfig: {
                    columns: 1,
                    gap: 'gap-3',
                    containerWidth: 'max-w-full',
                    padding: 'p-3'
                  }
                }}
              />
            )}
          </motion.div>

          {/* 모바일 탭 네비게이션 */}
          <MobileTabs
            tabs={mobileTabs}
            activeTab={currentMobilePage}
            onTabChange={setCurrentMobilePage}
          />
        </div>

        {/* 플로팅 액션 버튼 */}
        <AnimatePresence>
          {currentMobilePage === 'chat' && (
            <FloatingActionButton
              position="bottom-right"
              offset="5rem" // 탭 네비게이션 위에 위치
              onClick={() => {
                // 새 채팅 시작 로직
                createSession();
              }}
              className="bg-gradient-to-r from-green-500 to-emerald-600"
            >
              <Plus className="h-6 w-6" />
            </FloatingActionButton>
          )}
        </AnimatePresence>
      </motion.div>
    );
  }

  // 데스크톱 레이아웃 (기존 로직 유지)
  return (
    <div className={`flex h-full w-full relative ${config.animations ? 'transition-all duration-300' : ''}`}>
      {/* 데스크톱 사이드바 오버레이 */}
      {showSidebar && isMobile && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30"
          onClick={toggleSidebarCollapse}
        />
      )}
      
      {/* 사이드바 컨테이너 */}
      <div 
        className={`relative flex ${isMobile ? 'fixed inset-y-0 left-0 z-40' : ''}`}
        style={{ 
          width: showSidebar ? `${config.sidebarWidth}px` : '0px',
          transition: config.animations ? 'width 0.3s ease-out' : undefined
        }}
      >
        {/* 사이드바 */}
        {showSidebar && (
          <>
            <Sidebar
              isMobile={false}
              width={config.sidebarWidth}
              onClose={toggleSidebarCollapse}
            />
            
            {/* 리사이즈 핸들 */}
            <ResizeHandle
              onResize={handleSidebarResize}
              onStartDrag={startDragging}
              onEndDrag={stopDragging}
              className="absolute right-0 top-0 z-10"
            />
          </>
        )}
      </div>

      {/* 데스크톱 메인 페이지 영역 */}
      <div 
        className="flex-1 flex flex-col min-w-0"
        style={{
          marginLeft: showSidebar ? `${config.sidebarWidth}px` : '0px',
          transition: config.animations ? 'margin-left 0.3s ease-out' : undefined
        }}
      >
        {/* GAIA-BT 헤더 배너 */}
        <Header
          showSidebar={showSidebar}
          onToggleSidebar={toggleSidebarCollapse}
          layoutMode={config.mode}
          onLayoutModeChange={(mode) => updateConfig({ mode })}
        />

        {/* 메인 콘텐츠 영역 */}
        <main className={`flex-1 overflow-hidden ${layoutClasses.gap}`}>
          <div className={`mx-auto w-full h-full ${layoutClasses.container}`}>
            <div className={`h-full ${layoutClasses.grid} ${layoutClasses.gap}`}>
              {children || (
                <ChatArea 
                  layoutConfig={{
                    mode: config.mode,
                    density: config.density,
                    fontSize: config.fontSize,
                    gridConfig: currentBreakpoint.gridConfig
                  }}
                />
              )}
            </div>
          </div>
        </main>
      </div>
      
      {/* Dragging overlay */}
      {isDragging && (
        <div className="fixed inset-0 z-50" style={{ cursor: 'col-resize' }} />
      )}
    </div>
  );
}