'use client';

import React, { useState, useEffect } from 'react';
import { Plus, MessageCircle, Settings, Brain, Zap, Shield, X } from 'lucide-react';
import { useChatContext } from '@/contexts/ChatContext';
import { useResponsive } from '@/hooks/useResponsive';
import Image from 'next/image';

const API_BASE_URL = 'http://localhost:8000';

interface SystemStatus {
  status: string;
  model: string;
  mode: string;
  mcp_enabled: boolean;
  debug: boolean;
}

interface SidebarProps {
  onClose?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onClose }) => {
  const { 
    conversations, 
    currentConversation, 
    createConversation, 
    selectConversation, 
    isLoading,
    currentModel,
    currentMode,
    mcpEnabled,
    toggleMode,
    error,
    currentPromptType,
    changePromptType,
    changeModel,
    isModelChanging,
    isModeChanging,
    isPromptChanging
  } = useChatContext();
  
  const { isDesktop } = useResponsive();

  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [showModelDialog, setShowModelDialog] = useState(false);

  // 시스템 상태 확인
  const checkSystemStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (response.ok) {
        const status = await response.json();
        setSystemStatus(status);
      }
    } catch (error) {
      console.error('시스템 상태 확인 실패:', error);
    }
  };

  // 사용 가능한 모델 목록 가져오기
  const fetchAvailableModels = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/system/models`);
      if (response.ok) {
        const models = await response.json();
        setAvailableModels(models.models || []);
      }
    } catch (error) {
      console.error('모델 목록 가져오기 실패:', error);
      // 기본 모델 목록 설정
      setAvailableModels([
        'llama3.1:latest',
        'gemma2:latest', 
        'qwen2.5:latest',
        'mistral:latest',
        'phi3:latest'
      ]);
    }
  };

  // 모델 변경
  const handleModelChange = async (modelName: string) => {
    await changeModel(modelName);
    await checkSystemStatus(); // 상태 업데이트
    setShowModelDialog(false);
  };


  // 프롬프트 모드 변경 (ChatContext 사용)
  const handlePromptChange = async (mode: string) => {
    await changePromptType(mode);
    await checkSystemStatus(); // 상태 업데이트
  };

  // 컴포넌트 마운트 시 상태 확인
  useEffect(() => {
    checkSystemStatus();
    fetchAvailableModels();
    const interval = setInterval(checkSystemStatus, 10000); // 10초마다 상태 확인
    return () => clearInterval(interval);
  }, []);

  const handleNewConversation = async () => {
    try {
      await createConversation();
      // 모바일에서 새 대화 생성 후 사이드바 닫기
      if (onClose) {
        onClose();
      }
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const handleConversationSelect = (conversationId: string) => {
    selectConversation(conversationId);
    // 모바일에서 대화 선택 후 사이드바 닫기
    if (onClose) {
      onClose();
    }
  };

  const formatDate = (date: Date) => {
    const now = new Date();
    const messageDate = new Date(date);
    const diffInHours = (now.getTime() - messageDate.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return messageDate.toLocaleTimeString('ko-KR', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } else {
      return messageDate.toLocaleDateString('ko-KR', { 
        month: 'short', 
        day: 'numeric' 
      });
    }
  };

  return (
    <div className="w-80 sm:w-80 md:w-80 bg-gray-50 border-r border-gray-200 flex flex-col h-full shadow-lg md:shadow-none">
      {/* 헤더 */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-800 flex items-center">
            <Image 
              src="/gaia-mark.png" 
              alt="GAIA-GPT" 
              width={24} 
              height={24} 
              className="mr-2" 
            />
            GAIA-GPT
          </h1>
          <div className="flex items-center space-x-2">
            <div className={`px-2 py-1 rounded text-xs font-medium ${
              currentMode === 'deep_research' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              {currentMode === 'deep_research' ? '딥리서치' : '기본'}
            </div>
            <div className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
              {currentPromptType === 'default' ? '기본' :
               currentPromptType === 'patent' ? '특허' :
               currentPromptType === 'clinical' ? '임상' :
               currentPromptType === 'research' ? '연구' :
               currentPromptType === 'chemistry' ? '화학' :
               currentPromptType === 'regulatory' ? '규제' : currentPromptType}
            </div>
            <div className="flex items-center space-x-1">
              <button
                onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
                className="p-1 rounded hover:bg-gray-100 transition-colors"
                title="고급 설정"
              >
                <Settings className="w-4 h-4 text-gray-600" />
              </button>
              
              {/* 사이드바 닫기 버튼 */}
              {onClose && (
                <button
                  onClick={onClose}
                  className="p-1 rounded hover:bg-gray-100 transition-colors"
                  title={isDesktop ? "사이드바 숨기기 (Ctrl+B)" : "사이드바 닫기"}
                >
                  <X className="w-4 h-4 text-gray-600" />
                </button>
              )}
            </div>
          </div>
        </div>
        
        {/* 새 대화 버튼 + 모드 전환 */}
        <div className="flex space-x-2 mt-3">
          <button
            onClick={handleNewConversation}
            disabled={isLoading}
            className="flex-1 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg flex items-center justify-center space-x-2 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <Plus className="w-4 h-4" />
            <span>새 대화</span>
          </button>
          
          <button
            onClick={toggleMode}
            disabled={isModeChanging}
            className={`px-4 py-2 rounded-lg flex items-center justify-center transition-colors focus:outline-none focus:ring-2 disabled:opacity-50 disabled:cursor-not-allowed ${
              currentMode === 'deep_research'
                ? 'bg-green-500 hover:bg-green-600 disabled:bg-green-300 text-white focus:ring-green-500'
                : 'bg-gray-500 hover:bg-gray-600 disabled:bg-gray-300 text-white focus:ring-gray-500'
            }`}
            title={isModeChanging ? '모드 변경 중...' : currentMode === 'deep_research' ? '기본 모드로 전환' : '딥리서치 모드로 전환'}
          >
            {currentMode === 'deep_research' ? <Brain className="w-4 h-4" /> : <Shield className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* 고급 설정 (토글 가능) */}
      {showAdvancedSettings && (
        <>
          {/* 시스템 상태 */}
          <div className="p-4 bg-gray-50">
            <h3 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
              <Settings className="w-4 h-4 mr-1" />
              시스템 상태
            </h3>
            
            {systemStatus && (
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span>API 연결:</span>
                  <span className={`font-medium ${
                    systemStatus.status === 'healthy' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {systemStatus.status === 'healthy' ? '정상' : '오류'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span>모델:</span>
                  <button
                    onClick={() => setShowModelDialog(true)}
                    disabled={isModelChanging}
                    className="font-medium text-blue-600 truncate max-w-32 hover:text-blue-800 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                    title={isModelChanging ? '모델 변경 중...' : `현재 모델: ${currentModel || 'N/A'} (클릭하여 변경)`}
                  >
                    {isModelChanging ? '변경 중...' : (currentModel || 'N/A')}
                  </button>
                </div>
                <div className="flex justify-between">
                  <span>MCP:</span>
                  <span className={`font-medium ${
                    mcpEnabled ? 'text-green-600' : 'text-gray-600'
                  }`}>
                    {mcpEnabled ? '활성화' : '비활성화'}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* 전문 프롬프트 */}
          <div className="p-4 border-t border-gray-200">
            <h3 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
              <Zap className="w-4 h-4 mr-1" />
              전문 프롬프트
            </h3>
            
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => handlePromptChange('default')}
                disabled={isPromptChanging}
                className={`px-2 py-1 rounded text-xs transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                  currentPromptType === 'default' 
                    ? 'bg-gray-200 text-gray-800 font-medium' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
                title={isPromptChanging ? '프롬프트 변경 중...' : '기본 모드로 변경'}
              >
                {isPromptChanging && currentPromptType === 'default' ? '변경 중...' : '기본모드'}
              </button>
              <button
                onClick={() => handlePromptChange('patent')}
                disabled={isPromptChanging}
                className={`px-2 py-1 rounded text-xs transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                  currentPromptType === 'patent' 
                    ? 'bg-green-200 text-green-800 font-medium' 
                    : 'bg-green-100 text-green-700 hover:bg-green-200'
                }`}
                title={isPromptChanging ? '프롬프트 변경 중...' : '특허 검색 모드로 변경'}
              >
                {isPromptChanging && currentPromptType === 'patent' ? '변경 중...' : '특허검색'}
              </button>
              <button
                onClick={() => handlePromptChange('clinical')}
                disabled={isPromptChanging}
                className={`px-2 py-1 rounded text-xs transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                  currentPromptType === 'clinical' 
                    ? 'bg-blue-200 text-blue-800 font-medium' 
                    : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                }`}
                title={isPromptChanging ? '프롬프트 변경 중...' : '임상시험 모드로 변경'}
              >
                {isPromptChanging && currentPromptType === 'clinical' ? '변경 중...' : '임상시험'}
              </button>
              <button
                onClick={() => handlePromptChange('research')}
                disabled={isPromptChanging}
                className={`px-2 py-1 rounded text-xs transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                  currentPromptType === 'research' 
                    ? 'bg-purple-200 text-purple-800 font-medium' 
                    : 'bg-purple-100 text-purple-700 hover:bg-purple-200'
                }`}
                title={isPromptChanging ? '프롬프트 변경 중...' : '연구분석 모드로 변경'}
              >
                {isPromptChanging && currentPromptType === 'research' ? '변경 중...' : '연구분석'}
              </button>
              <button
                onClick={() => handlePromptChange('chemistry')}
                disabled={isPromptChanging}
                className={`px-2 py-1 rounded text-xs transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                  currentPromptType === 'chemistry' 
                    ? 'bg-orange-200 text-orange-800 font-medium' 
                    : 'bg-orange-100 text-orange-700 hover:bg-orange-200'
                }`}
                title={isPromptChanging ? '프롬프트 변경 중...' : '의약화학 모드로 변경'}
              >
                {isPromptChanging && currentPromptType === 'chemistry' ? '변경 중...' : '의약화학'}
              </button>
              <button
                onClick={() => handlePromptChange('regulatory')}
                disabled={isPromptChanging}
                className={`px-2 py-1 rounded text-xs transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                  currentPromptType === 'regulatory' 
                    ? 'bg-red-200 text-red-800 font-medium' 
                    : 'bg-red-100 text-red-700 hover:bg-red-200'
                }`}
                title={isPromptChanging ? '프롬프트 변경 중...' : '규제승인 모드로 변경'}
              >
                {isPromptChanging && currentPromptType === 'regulatory' ? '변경 중...' : '규제승인'}
              </button>
            </div>
          </div>
        </>
      )}
      
      {/* 대화 목록 */}
      <div className="flex-1 overflow-y-auto border-t border-gray-200">
        <div className="p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">대화 기록</h3>
        </div>
        
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <Image 
              src="/gaia-mark.png" 
              alt="GAIA-GPT" 
              width={48} 
              height={48} 
              className="mx-auto mb-2 opacity-60" 
            />
            <p>아직 대화가 없습니다.</p>
            <p className="text-sm">새 대화를 시작해보세요!</p>
          </div>
        ) : (
          <div className="px-2">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => handleConversationSelect(conversation.id)}
                className={`p-3 rounded-lg cursor-pointer transition-colors mb-1 ${
                  currentConversation?.id === conversation.id
                    ? 'bg-blue-100 border-blue-200 border'
                    : 'hover:bg-gray-100'
                }`}
              >
                <div className="flex justify-between items-start">
                  <h3 className="font-medium text-gray-800 truncate flex-1 mr-2">
                    {conversation.title}
                  </h3>
                  <span className="text-xs text-gray-500 whitespace-nowrap">
                    {formatDate(conversation.updatedAt)}
                  </span>
                </div>
                
                {/* 마지막 메시지 미리보기 */}
                {conversation.messages.length > 0 && (
                  <p className="text-sm text-gray-500 truncate mt-1">
                    {conversation.messages[conversation.messages.length - 1].content}
                  </p>
                )}
                
                {/* 메시지 개수 */}
                {conversation.messages.length > 0 && (
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-xs text-gray-400">
                      {conversation.messages.length}개 메시지
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* 하단 정보 */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <p className="text-xs text-gray-500 text-center">
          GAIA-GPT v2.0 - GAIA-BT 통합
        </p>
      </div>

      {/* 모델 선택 다이얼로그 */}
      {showModelDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-96 overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-800">모델 선택</h3>
              <button
                onClick={() => setShowModelDialog(false)}
                className="p-1 rounded hover:bg-gray-100 transition-colors"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            </div>
            
            <div className="space-y-2 mb-4">
              <p className="text-sm text-gray-600">사용할 AI 모델을 선택하세요:</p>
              {availableModels.length > 0 ? (
                availableModels.map((model) => (
                  <button
                    key={model}
                    onClick={() => handleModelChange(model)}
                    disabled={isModelChanging}
                    className={`w-full text-left p-3 rounded-lg border transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                      currentModel === model
                        ? 'bg-blue-50 border-blue-200 text-blue-800'
                        : 'bg-gray-50 border-gray-200 hover:bg-gray-100 text-gray-700'
                    }`}
                  >
                    <div className="font-medium">{model}</div>
                    {currentModel === model && (
                      <div className="text-xs text-blue-600 mt-1">
                        {isModelChanging ? '변경 중...' : '현재 선택됨'}
                      </div>
                    )}
                  </button>
                ))
              ) : (
                <div className="text-center text-gray-500 py-4">
                  모델을 불러오는 중...
                </div>
              )}
            </div>

            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowModelDialog(false)}
                disabled={isModelChanging}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                취소
              </button>
              <button
                onClick={fetchAvailableModels}
                disabled={isModelChanging}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                새로고침
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;