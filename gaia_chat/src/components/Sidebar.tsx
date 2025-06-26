'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Image from 'next/image';
import { Plus, MessageCircle, Trash2, X, Brain, Shield, Zap, ChevronDown, ChevronUp, Monitor } from 'lucide-react';
import { useChatContext } from '@/contexts/SimpleChatContext';
import { formatDate } from '../utils/helpers';
import { useResponsive } from '@/hooks/useResponsive';
import { getApiUrl } from '@/config/api';


interface SidebarProps {
  onClose?: () => void;
  isMobileSidebarOpen?: boolean;
  onToggle?: () => void;
}


const Sidebar: React.FC<SidebarProps> = ({ onClose, onToggle }) => {
  console.log('💡 Sidebar 컴포넌트 렌더링 시작');
  
  const { 
    conversations, 
    currentConversation, 
    startNewConversation,
    selectConversation, 
    deleteConversation,
    isLoading,
    currentModel,
    currentMode,
    mcpEnabled,
    changeMode,
    currentPromptType,
    changePrompt,
    changeModel,
    isModelChanging,
    isModeChanging,
    isPromptChanging
  } = useChatContext();
  
  const { isDesktop } = useResponsive();

  const [showSystemStatus, setShowSystemStatus] = useState(true);
  const [showExpertPrompts, setShowExpertPrompts] = useState(false);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  const [showModelDialog, setShowModelDialog] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const [serverConnected] = useState(true);

  // 시스템 상태 확인
  const checkSystemStatus = useCallback(async () => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);
    
    try {
      const response = await fetch(getApiUrl('/health'), {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal
      });
      
      if (response.ok) {
        await response.json();
        // 상태 업데이트 로직 제거 (현재는 컨텍스트에서 관리)
      } else {
        // 에러 상태 처리 (현재는 컨텍스트에서 관리)
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') return;
      // 오프라인 상태 처리 (현재는 컨텍스트에서 관리)
    } finally {
      clearTimeout(timeoutId);
    }
  }, [currentModel, currentMode, mcpEnabled]);

  // 사용 가능한 모델 목록 가져오기
  const fetchAvailableModels = useCallback(async () => {
    setIsLoadingModels(true);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);
    
    try {
      const response = await fetch(getApiUrl('/api/system/models'), {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal
      });
      
      if (response.ok) {
        const models = await response.json();
        setAvailableModels(models.models || []);
      } else {
        const fallbackModels = [
          'gemma3-12b:latest',
          'txgemma-chat:latest', 
          'txgemma-predict:latest',
          'Gemma3:27b-it-q4_K_M'
        ];
        setAvailableModels(fallbackModels);
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') return;
      const fallbackModels = [
        'gemma3-12b:latest',
        'txgemma-chat:latest',
        'txgemma-predict:latest',
        'Gemma3:27b-it-q4_K_M'
      ];
      setAvailableModels(fallbackModels);
    } finally {
      clearTimeout(timeoutId);
      setIsLoadingModels(false);
    }
  }, []);

  const handleOpenModelDialog = async () => {
    setShowModelDialog(true);
    await fetchAvailableModels();
  };

  const handleModelChange = async (modelName: string) => {
    if (!serverConnected) {
      alert('서버에 연결되지 않았습니다. 연결을 확인해주세요.');
      return;
    }
    
    try {
      await changeModel(modelName);
      await checkSystemStatus();
      setShowModelDialog(false);
    } catch (error) {
      console.error('Failed to change model:', error);
      alert('모델 변경 중 오류가 발생했습니다.');
    }
  };

  const handlePromptChange = async (mode: string) => {
    if (!serverConnected) {
      alert('서버에 연결되지 않았습니다. 연결을 확인해주세요.');
      return;
    }
    
    try {
      await changePrompt(mode);
      await checkSystemStatus();
    } catch (error) {
      console.error('Failed to change prompt type:', error);
      alert('프롬프트 변경 중 오류가 발생했습니다.');
    }
  };

  // 컴포넌트 마운트 시 상태 확인
  useEffect(() => {
    let mounted = true;
    
    const doInitialLoad = async () => {
      if (mounted) {
        await checkSystemStatus();
      }
    };
    
    doInitialLoad();
    
    return () => {
      mounted = false;
    };
  }, [checkSystemStatus]);

  // 모델 다이얼로그 열릴 때 모델 목록 새로고침
  useEffect(() => {
    if (showModelDialog) {
      fetchAvailableModels();
    }
  }, [showModelDialog, fetchAvailableModels]);

  const handleNewConversation = async () => {
    if (!serverConnected) {
      alert('서버에 연결되지 않았습니다. 연결을 확인해주세요.');
      return;
    }
    
    try {
      startNewConversation();
      if (onClose) {
        onClose();
      }
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const handleModeToggle = async () => {
    if (!serverConnected) {
      alert('서버에 연결되지 않았습니다. 연결을 확인해주세요.');
      return;
    }
    
    try {
      const newMode = currentMode === 'deep_research' ? 'normal' : 'deep_research';
      await changeMode(newMode);
    } catch (error) {
      console.error('Failed to toggle mode:', error);
      alert('모드 전환 중 오류가 발생했습니다.');
    }
  };

  const handleConversationSelect = (conversationId: string) => {
    selectConversation(conversationId);
    if (onClose) {
      onClose();
    }
  };

  const handleDeleteConversation = (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDeleteConfirmId(conversationId);
  };

  const confirmDelete = async () => {
    if (deleteConfirmId) {
      try {
        deleteConversation(deleteConfirmId);
      } catch (error) {
        console.error('대화 삭제 중 오류 발생:', error);
      } finally {
        setDeleteConfirmId(null);
      }
    }
  };

  const cancelDelete = () => {
    setDeleteConfirmId(null);
  };

  return (
    <div className="sidebar-container w-72 sm:w-80 md:w-80 bg-gray-50 border-r border-gray-200 shadow-lg md:shadow-none overflow-hidden flex flex-col h-[100vh] max-h-screen">
      {/* 모바일에서 사이드바 닫기 버튼 */}
      {!isDesktop && (
        <button 
          onClick={onToggle} 
          className="absolute top-3 right-3 w-9 h-9 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center text-gray-600 hover:bg-gray-100 z-10 shadow-sm border border-gray-200 transition-all duration-200"
          aria-label="사이드바 닫기"
        >
          <X className="w-5 h-5" />
        </button>
      )}

      {/* 헤더 */}
      <div className="p-3 sm:p-4 border-b border-gray-200 bg-white sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <h1 
            className="text-xl font-bold text-gray-800 flex items-center cursor-pointer hover:text-blue-600 transition-colors duration-200"
            onClick={() => {
              // 환영 페이지로 이동(현재 대화 선택 해제)
              selectConversation('');
              
              // 사이드바 열림 상태로 설정 (로컬스토리지에도 저장)
              if (typeof window !== 'undefined') {
                localStorage.setItem('gaia-gpt-sidebar-open', JSON.stringify(true));
                // 부모 컴포넌트에서 onToggle 호출 시 사이드바가 열릴 수 있도록 설정
                if (onToggle) onToggle();
              }
            }}
            title="홈으로 이동 - 환영 페이지로 돌아가기"
          >
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
              {currentPromptType === 'default' ? '일반' :
               currentPromptType === 'patent' ? '특허' :
               currentPromptType === 'clinical' ? '임상' :
               currentPromptType === 'research' ? '연구' :
               currentPromptType === 'chemistry' ? '화학' :
               currentPromptType === 'regulatory' ? '규제' : currentPromptType}
            </div>
            {onClose && !isDesktop && (
              <button
                onClick={onClose}
                className="p-1 rounded hover:bg-gray-100 transition-colors"
                title="사이드바 닫기"
              >
                <X className="w-4 h-4 text-gray-600" />
              </button>
            )}
          </div>
        </div>
        
        {/* 새 대화 버튼 + 모드 전환 */}
        <div className="flex space-x-2 mt-3">
          <button
            onClick={handleNewConversation}
            disabled={isLoading || !serverConnected}
            className="flex-1 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg flex items-center justify-center space-x-2 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            title={!serverConnected ? '서버 연결 필요' : '새 대화 시작'}
          >
            <Plus className="w-4 h-4" />
            <span>새 대화</span>
          </button>
          
          <button
            onClick={handleModeToggle}
            disabled={isModeChanging || !serverConnected}
            className={`px-4 py-2 rounded-lg flex items-center justify-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
              currentMode === 'deep_research'
                ? 'bg-green-500 hover:bg-green-600 disabled:bg-green-300 text-white focus:ring-green-500'
                : 'bg-gray-500 hover:bg-gray-600 disabled:bg-gray-300 text-white focus:ring-gray-500'
            }`}
            title={!serverConnected ? '서버 연결 필요' : isModeChanging ? '모드 변경 중...' : currentMode === 'deep_research' ? '기본 모드로 전환' : '딥리서치 모드로 전환'}
          >
            {currentMode === 'deep_research' ? <Brain className="w-4 h-4" /> : <Shield className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* 시스템 상태 */}
      <div className="p-4 bg-gray-50 border-t border-gray-200">
        <button
          onClick={() => setShowSystemStatus(!showSystemStatus)}
          className="w-full text-sm font-semibold text-gray-700 mb-2 flex items-center justify-between hover:text-gray-900 transition-colors"
        >
          <div className="flex items-center">
            <Monitor className="w-4 h-4 mr-1" />
            시스템 상태
          </div>
          {showSystemStatus ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        
        {showSystemStatus && (
          <div className="space-y-2 text-xs">
            <div className="flex justify-between items-center">
              <span>서버 연결:</span>
              <div className="flex items-center space-x-1">
                <div className={`w-2 h-2 rounded-full ${
                  serverConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                }`}></div>
                <span className={`font-medium ${
                  serverConnected ? 'text-green-600' : 'text-red-600'
                }`}>
                  {serverConnected ? '연결됨' : '연결 끊김'}
                </span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span>모델:</span>
              <button
                onClick={handleOpenModelDialog}
                disabled={isModelChanging || !serverConnected}
                className="font-medium text-blue-600 truncate max-w-32 hover:text-blue-800 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                title={!serverConnected ? '서버 연결 필요' : isModelChanging ? '모델 변경 중...' : `현재 모델: ${currentModel || 'N/A'} (클릭하여 변경)`}
              >
                {isModelChanging ? '변경 중...' : (currentModel || 'N/A')}
              </button>
            </div>
            <div className="flex justify-between">
              <span>MCP:</span>
              <span className={`font-medium ${
                currentMode === 'deep_research' ? 'text-green-600' : 'text-gray-600'
              }`}>
                {currentMode === 'deep_research' ? '활성화' : '비활성화'}
              </span>
            </div>
            <div className="flex justify-between">
              <span>모드:</span>
              <span className={`font-medium ${
                currentMode === 'deep_research' ? 'text-green-600' : 'text-blue-600'
              }`}>
                {currentMode === 'deep_research' ? 'Deep Research' : '일반'}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* 전문 프롬프트 */}
      <div className="p-4 bg-gray-50 border-t border-gray-200">
        <button
          onClick={() => setShowExpertPrompts(!showExpertPrompts)}
          className="w-full text-sm font-semibold text-gray-700 mb-2 flex items-center justify-between hover:text-gray-900 transition-colors"
        >
          <div className="flex items-center">
            <Zap className="w-4 h-4 mr-1" />
            전문 프롬프트
          </div>
          {showExpertPrompts ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        
        {showExpertPrompts && (
          <div className="grid grid-cols-2 gap-2">
            {[
              { key: 'default', label: '일반모드' },
              { key: 'patent', label: '특허검색' },
              { key: 'clinical', label: '임상시험' },
              { key: 'research', label: '연구분석' },
              { key: 'chemistry', label: '의약화학' },
              { key: 'regulatory', label: '규제승인' }
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => handlePromptChange(key)}
                disabled={isPromptChanging || !serverConnected}
                className={`px-2 py-1 rounded text-xs transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                  currentPromptType === key 
                    ? 'bg-blue-200 text-blue-800 font-medium' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
                title={!serverConnected ? '서버 연결 필요' : isPromptChanging ? '프롬프트 변경 중...' : `${label} 모드로 변경`}
              >
                {isPromptChanging && currentPromptType === key ? '변경 중...' : label}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 대화 목록 */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden border-t border-gray-200 thin-scrollbar max-h-[calc(100vh-16rem)]">
        <div className="p-3 bg-white border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-700 mb-1 flex items-center">
            <MessageCircle className="w-4 h-4 mr-1" />
            대화 기록
            <span className="ml-2 text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
              {conversations.length}
            </span>
          </h3>
        </div>
        
        {conversations.length === 0 ? (
          <div className="flex-1 flex items-center justify-center p-4">
            <div className="text-center text-gray-500">
              <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-sm font-medium mb-1">아직 대화가 없습니다</p>
              <p className="text-xs text-gray-400">새 대화를 시작해보세요!</p>
            </div>
          </div>
        ) : (
          <div className="p-3 space-y-2">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => handleConversationSelect(conversation.id)}
                className={`group p-3 rounded-lg cursor-pointer transition-all duration-200 border ${
                  currentConversation?.id === conversation.id
                    ? 'bg-blue-50 border-blue-200 shadow-sm'
                    : 'bg-white border-gray-100 hover:bg-gray-50 hover:border-gray-200 hover:shadow-sm'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-gray-800 truncate flex-1 mr-2 text-sm">
                    {conversation.title || '새 대화'}
                  </h4>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-500 whitespace-nowrap">
                      {formatDate(conversation.updatedAt)}
                    </span>
                    {currentConversation?.id !== conversation.id && (
                      <button
                        onClick={(e) => handleDeleteConversation(conversation.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-100 transition-all duration-200"
                        title="대화 삭제"
                      >
                        <Trash2 className="w-3 h-3 text-red-500" />
                      </button>
                    )}
                  </div>
                </div>
                
                {conversation.messages && conversation.messages.length > 0 && (
                  <p className="text-xs text-gray-500 mb-2 overflow-hidden" style={{
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical'
                  }}>
                    {conversation.messages[conversation.messages.length - 1].content}
                  </p>
                )}
                
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-400">
                    {conversation.messages?.length || 0}개 메시지
                  </span>
                  {currentConversation?.id === conversation.id && (
                    <span className="text-xs text-blue-600 font-medium">활성</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* 하단 정보 */}
      <div className="p-4 border-t border-gray-200 bg-white flex-shrink-0">
        <p className="text-xs text-gray-500 text-center">
          GAIA-GPT v2.0 - GAIA-BT 통합
        </p>
      </div>

      {/* 모델 선택 다이얼로그 */}
      {showModelDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-96 overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h1 className="text-2xl font-bold text-gray-800">GAIA-GPT</h1>
              <button
                onClick={() => setShowModelDialog(false)}
                className="p-1 rounded hover:bg-gray-100 transition-colors"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            </div>
            
            <div className="space-y-2 mb-4">
              <p className="text-sm text-gray-600">사용할 AI 모델을 선택하세요:</p>
              <div className="text-xs text-gray-500 mb-2">
                사용 가능한 모델: {availableModels.length}개 {isLoadingModels && '(로딩 중...)'}
              </div>
              {isLoadingModels ? (
                <div className="text-center text-gray-500 py-4">
                  <div className="animate-spin inline-block w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full mb-2"></div>
                  <div className="mb-2">모델 목록을 불러오는 중...</div>
                  <div className="text-xs">잠시만 기다려주세요</div>
                </div>
              ) : availableModels.length > 0 ? (
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
                  <div className="mb-2">모델을 불러오는 중...</div>
                  <div className="text-xs">잠시만 기다려주세요</div>
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

      {/* 삭제 확인 다이얼로그 */}
      {deleteConfirmId && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mr-3">
                <Trash2 className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-800">대화 삭제</h3>
                <p className="text-sm text-gray-600">이 대화를 삭제하시겠습니까?</p>
              </div>
            </div>
            
            <div className="bg-gray-50 rounded p-3 mb-4">
              <p className="text-xs text-gray-600">
                삭제된 대화는 복구할 수 없습니다. 대화 내용과 모든 메시지가 영구적으로 삭제됩니다.
              </p>
            </div>

            <div className="flex justify-end space-x-2">
              <button
                onClick={cancelDelete}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                취소
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
              >
                삭제
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;