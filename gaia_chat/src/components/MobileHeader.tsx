'use client';

import React from 'react';
import { Menu, MessageCircle, Settings, X, Brain, Shield } from 'lucide-react';
import { useChatContext } from '@/contexts/ChatContext';
import Image from 'next/image';

interface MobileHeaderProps {
  onMenuToggle: () => void;
  isSidebarOpen: boolean;
}

const MobileHeader: React.FC<MobileHeaderProps> = ({ onMenuToggle, isSidebarOpen }) => {
  const { currentMode, currentPromptType, toggleMode } = useChatContext();

  return (
    <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between md:hidden">
      <div className="flex items-center space-x-3">
        <button
          onClick={onMenuToggle}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          aria-label={isSidebarOpen ? "메뉴 닫기" : "메뉴 열기"}
        >
          {isSidebarOpen ? (
            <X className="w-6 h-6 text-gray-600" />
          ) : (
            <Menu className="w-6 h-6 text-gray-600" />
          )}
        </button>
        
        <div className="flex items-center space-x-2">
          <Image 
            src="/gaia-mark.png" 
            alt="GAIA-GPT" 
            width={20} 
            height={20} 
          />
          <h1 className="text-lg font-bold text-gray-800">GAIA-GPT</h1>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        {/* 현재 모드 표시 */}
        <div className={`px-2 py-1 rounded text-xs font-medium ${
          currentMode === 'deep_research' 
            ? 'bg-green-100 text-green-800' 
            : 'bg-gray-100 text-gray-800'
        }`}>
          {currentMode === 'deep_research' ? '딥리서치' : '기본'}
        </div>

        {/* 프롬프트 타입 표시 */}
        <div className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
          {currentPromptType === 'default' ? '기본' :
           currentPromptType === 'patent' ? '특허' :
           currentPromptType === 'clinical' ? '임상' :
           currentPromptType === 'research' ? '연구' :
           currentPromptType === 'chemistry' ? '화학' :
           currentPromptType === 'regulatory' ? '규제' : currentPromptType}
        </div>

        {/* 모드 전환 버튼 */}
        <button
          onClick={toggleMode}
          className={`p-2 rounded-lg transition-colors ${
            currentMode === 'deep_research'
              ? 'bg-green-100 text-green-600 hover:bg-green-200'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
          title={currentMode === 'deep_research' ? '기본 모드로 전환' : '딥리서치 모드로 전환'}
        >
          {currentMode === 'deep_research' ? <Brain className="w-4 h-4" /> : <Shield className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
};

export default MobileHeader;