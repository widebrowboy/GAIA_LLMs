'use client';

import { useState, useRef } from 'react';
import { motion, AnimatePresence, PanInfo } from 'framer-motion';
import { TouchButton } from '@/components/ui/touch-button';
import { useTouchGestures } from '@/hooks/use-touch-gestures';
import { useMobile } from '@/hooks/use-mobile';
import { 
  Menu, 
  X, 
  Home, 
  MessageSquare, 
  Settings, 
  Database,
  HelpCircle,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface MobileNavigationProps {
  isOpen: boolean;
  onToggle: () => void;
  onNavigate: (page: string) => void;
  currentPage?: string;
}

export default function MobileNavigation({ 
  isOpen, 
  onToggle, 
  onNavigate, 
  currentPage = 'chat' 
}: MobileNavigationProps) {
  const isMobile = useMobile();
  const [dragProgress, setDragProgress] = useState(0);
  const panelRef = useRef<HTMLDivElement>(null);

  // 스와이프 제스처로 네비게이션 제어
  const { gesture } = useTouchGestures(panelRef, {
    minSwipeDistance: 50,
    preventScroll: true
  });

  // 스와이프로 네비게이션 닫기
  if (gesture.direction === 'left' && isOpen) {
    onToggle();
  }

  const navigationItems = [
    { id: 'chat', label: '채팅', icon: MessageSquare },
    { id: 'history', label: '기록', icon: Database },
    { id: 'settings', label: '설정', icon: Settings },
    { id: 'help', label: '도움말', icon: HelpCircle },
  ];

  const handleDrag = (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    if (!isOpen) return;
    
    const { offset } = info;
    const panelWidth = 280; // 네비게이션 패널 너비
    const progress = Math.max(0, Math.min(1, -offset.x / panelWidth));
    setDragProgress(progress);
  };

  const handleDragEnd = (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    const { offset, velocity } = info;
    const threshold = -100; // 드래그 임계값
    
    if (offset.x < threshold || velocity.x < -500) {
      onToggle(); // 네비게이션 닫기
    }
    setDragProgress(0);
  };

  if (!isMobile) return null;

  return (
    <>
      {/* 오버레이 */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="fixed inset-0 bg-black/50 z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onToggle}
          />
        )}
      </AnimatePresence>

      {/* 네비게이션 패널 */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            ref={panelRef}
            className="fixed left-0 top-0 h-full w-70 bg-gray-900 z-50 shadow-2xl"
            initial={{ x: '-100%' }}
            animate={{ 
              x: isOpen ? `${-dragProgress * 100}%` : '-100%'
            }}
            exit={{ x: '-100%' }}
            transition={{ 
              type: "spring", 
              stiffness: 300, 
              damping: 30,
              duration: 0.3
            }}
            drag="x"
            dragConstraints={{ left: -280, right: 0 }}
            dragElastic={0.1}
            onDrag={handleDrag}
            onDragEnd={handleDragEnd}
          >
            {/* 드래그 인디케이터 */}
            <div className="absolute right-0 top-1/2 transform -translate-y-1/2 translate-x-full">
              <div className="bg-gray-700 rounded-r-lg p-2">
                <ChevronLeft className="h-4 w-4 text-gray-300" />
              </div>
            </div>

            {/* 헤더 */}
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-lg flex items-center justify-center">
                  <Database className="h-4 w-4 text-white" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white">GAIA-BT</h2>
                  <p className="text-xs text-gray-300">신약개발 AI</p>
                </div>
              </div>
              
              <TouchButton
                variant="ghost"
                size="sm"
                onClick={onToggle}
                className="text-gray-400 hover:text-white"
              >
                <X className="h-5 w-5" />
              </TouchButton>
            </div>

            {/* 네비게이션 아이템 */}
            <nav className="flex-1 p-4">
              <div className="space-y-2">
                {navigationItems.map((item, index) => {
                  const Icon = item.icon;
                  const isActive = currentPage === item.id;
                  
                  return (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1, duration: 0.3 }}
                    >
                      <TouchButton
                        variant={isActive ? "default" : "ghost"}
                        className={cn(
                          "w-full justify-start h-12 text-left",
                          isActive 
                            ? "bg-blue-600 text-white" 
                            : "text-gray-300 hover:text-white hover:bg-gray-800"
                        )}
                        onClick={() => {
                          onNavigate(item.id);
                          onToggle();
                        }}
                        hapticFeedback={true}
                      >
                        <Icon className="h-5 w-5 mr-3" />
                        {item.label}
                      </TouchButton>
                    </motion.div>
                  );
                })}
              </div>
            </nav>

            {/* 하단 정보 */}
            <div className="p-4 border-t border-gray-700">
              <div className="text-xs text-gray-400 text-center">
                <p>버전 2.0 Alpha</p>
                <p>모바일 최적화</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

// 모바일 탭 네비게이션 컴포넌트
interface MobileTabsProps {
  tabs: Array<{
    id: string;
    label: string;
    icon: React.ComponentType<any>;
    badge?: number;
  }>;
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

export function MobileTabs({ tabs, activeTab, onTabChange }: MobileTabsProps) {
  const isMobile = useMobile();
  
  if (!isMobile) return null;

  return (
    <motion.div 
      className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-700 z-40"
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <div className="flex items-center justify-around px-2 py-1">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          return (
            <TouchButton
              key={tab.id}
              variant="ghost"
              className={cn(
                "flex-1 flex flex-col items-center py-2 px-1 rounded-lg relative",
                isActive 
                  ? "text-blue-400 bg-blue-600/20" 
                  : "text-gray-400"
              )}
              onClick={() => onTabChange(tab.id)}
              hapticFeedback={true}
              touchScale={0.95}
            >
              <div className="relative">
                <Icon className="h-5 w-5" />
                {tab.badge && tab.badge > 0 && (
                  <motion.div
                    className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 500, damping: 15 }}
                  >
                    {tab.badge > 99 ? '99+' : tab.badge}
                  </motion.div>
                )}
              </div>
              <span className="text-xs mt-1 font-medium">{tab.label}</span>
              
              {/* 활성 탭 인디케이터 */}
              {isActive && (
                <motion.div
                  className="absolute bottom-0 left-1/2 w-6 h-0.5 bg-blue-400 rounded-full"
                  layoutId="activeTab"
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  style={{ x: '-50%' }}
                />
              )}
            </TouchButton>
          );
        })}
      </div>

      {/* iOS 홈 인디케이터 공간 */}
      <div className="h-safe-bottom bg-gray-900"></div>
    </motion.div>
  );
}