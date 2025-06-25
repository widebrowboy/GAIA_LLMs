'use client';

import React, { useState, useEffect } from 'react';
import { Plus, Settings, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { useChatContext } from '@/contexts/SimpleChatContext';
import { getApiUrl } from '@/config/api';

interface SidebarProps {
  onClose?: () => void;
}

const SimpleSidebar: React.FC<SidebarProps> = ({ onClose }) => {
  const { 
    conversations, 
    currentConversation, 
    createConversation, 
    selectConversation, 
    currentModel,
    currentMode,
    mcpEnabled,
    toggleMode,
    changeModel,
    isConnected,
  } = useChatContext();

  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [showModelDialog, setShowModelDialog] = useState(false);
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');

  // API 연결 상태 확인
  const checkApiStatus = async () => {
    try {
      const controller = new AbortController();
      setTimeout(() => controller.abort(), 2000);
      
      const response = await fetch(getApiUrl('/health'), {
        signal: controller.signal
      });
      
      if (response.ok) {
        setApiStatus('connected');
      } else {
        setApiStatus('disconnected');
      }
    } catch {
      setApiStatus('disconnected');
    }
  };

  // 모델 목록 로드
  const loadModels = async () => {
    try {
      const controller = new AbortController();
      setTimeout(() => controller.abort(), 3000);
      
      const response = await fetch(getApiUrl('/api/system/info'), {
        signal: controller.signal
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.available_models && Array.isArray(data.available_models)) {
          setAvailableModels(data.available_models);
        }
      }
    } catch (error) {
      console.warn('모델 목록 로드 실패:', error);
      setAvailableModels([currentModel]);
    }
  };

  // 새 대화 시작
  const handleNewChat = async () => {
    await createConversation?.();
    if (onClose) onClose();
  };

  // 모델 변경
  const handleModelChange = async (model: string) => {
    await changeModel(model);
    setShowModelDialog(false);
  };

  // 초기화
  useEffect(() => {
    checkApiStatus();
    loadModels();
    
    // 30초마다 상태 확인
    const interval = setInterval(checkApiStatus, 30000);
    return () => clearInterval(interval);
  }, [loadModels]);

  // 상태 아이콘 렌더링
  const renderStatusIcon = () => {
    switch (apiStatus) {
      case 'connected':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'disconnected':
        return <XCircle className="w-4 h-4 text-red-400" />;
      default:
        return <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />;
    }
  };

  return (
    <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col h-screen shadow-lg overflow-hidden">
      {/* 헤더 */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-800">GAIA-GPT</h1>
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              currentMode === 'deep_research' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              {currentMode === 'deep_research' ? 'Deep Research' : '기본'}
            </span>
          </div>
        </div>

        {/* 새 대화 버튼 */}
        <div className="flex space-x-2 mt-3">
          <button
            onClick={handleNewChat}
            className="flex-1 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center justify-center space-x-2 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>새 대화</span>
          </button>
          {/* 모드 전환 버튼 - Ollama 모델 연결 상태에 따라 활성화/비활성화 */}
          <button
            className={`flex items-center justify-center px-3 py-1 rounded-md text-xs font-medium transition-colors duration-200 ${!isConnected ? 'opacity-50 cursor-not-allowed ' : ''}${currentMode === 'basic' ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'bg-purple-600 hover:bg-purple-700 text-white'}`}
            onClick={toggleMode}
            disabled={!isConnected}
            title={!isConnected ? 'Ollama 모델과 연결되지 않았습니다. 연결 후 사용 가능합니다.' : '모드 전환'}
          >
            {currentMode === 'deep_research' ? '기본' : 'DR'}
          </button>
        </div>
      </div>

      {/* 시스템 상태 */}
      <div className="p-4 bg-gray-50 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
          <Settings className="w-4 h-4 mr-1" />
          시스템 상태
        </h3>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between items-center">
            <span>API 연결:</span>
            <div className="flex items-center space-x-1">
              {renderStatusIcon()}
              <span className="font-medium">
                {apiStatus === 'connected' ? '연결됨' : 
                 apiStatus === 'disconnected' ? '연결 끊김' : '확인 중...'}
              </span>
            </div>
          </div>
          
          <div className="flex justify-between items-center">
            <span>모델:</span>
            <button
              onClick={() => setShowModelDialog(true)}
              className="font-medium text-blue-600 hover:text-blue-800 transition-colors max-w-32 truncate"
              title={`현재 모델: ${currentModel}`}
            >
              {currentModel}
            </button>
          </div>
          
          <div className="flex justify-between">
            <span>MCP:</span>
            <span className="font-medium text-gray-600">
              {mcpEnabled ? '활성화' : '비활성화'}
            </span>
          </div>
        </div>
      </div>

      {/* 대화 목록 */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-3">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">대화 기록</h3>
        </div>
        
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <p className="text-sm">아직 대화가 없습니다</p>
            <p className="text-xs text-gray-400 mt-1">새 대화를 시작해보세요!</p>
          </div>
        ) : (
          <div className="space-y-1 px-3">
            {conversations.map((conversation) => (
              <button
                key={conversation.id}
                onClick={() => {
                  selectConversation(conversation.id);
                  if (onClose) onClose();
                }}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  currentConversation?.id === conversation.id
                    ? 'bg-blue-100 border border-blue-200'
                    : 'hover:bg-gray-100'
                }`}
              >
                <div className="font-medium text-sm text-gray-800 truncate">
                  {conversation.title || '새 대화'}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {conversation.messages.length}개 메시지
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 하단 정보 */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <p className="text-xs text-gray-500 text-center">
          GAIA-GPT v2.0 - Simple UI
        </p>
      </div>

      {/* 모델 선택 다이얼로그 */}
      {showModelDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">모델 선택</h3>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {availableModels.length === 0 ? (
                <p className="text-gray-500 text-sm">모델 목록을 불러오는 중...</p>
              ) : (
                availableModels.map((model) => (
                  <button
                    key={model}
                    onClick={() => handleModelChange(model)}
                    className={`w-full text-left p-3 rounded-lg border transition-colors ${
                      model === currentModel
                        ? 'bg-blue-50 border-blue-200 text-blue-800'
                        : 'hover:bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="font-medium">{model}</div>
                    {model === currentModel && (
                      <div className="text-xs text-blue-600 mt-1">현재 선택됨</div>
                    )}
                  </button>
                ))
              )}
            </div>
            <div className="flex justify-end space-x-2 mt-4">
              <button
                onClick={() => setShowModelDialog(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SimpleSidebar;