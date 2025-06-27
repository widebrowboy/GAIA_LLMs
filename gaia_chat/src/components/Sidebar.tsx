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

  const [showSystemStatus, setShowSystemStatus] = useState(false);
  const [showExpertPrompts, setShowExpertPrompts] = useState(false);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  const [showModelDialog, setShowModelDialog] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const [serverConnected] = useState(true);
  const [ollamaRunning, setOllamaRunning] = useState(false);

  // 실제 Ollama 모델 상태 확인
  const checkSystemStatus = useCallback(async () => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);
    
    try {
      // Ollama API에서 직접 실행 중인 모델 확인
      const response = await fetch('http://localhost:11434/api/ps', {
        method: 'GET',
        signal: controller.signal
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.models && data.models.length > 0) {
          const runningModel = data.models[0].name;
          setCurrentModel(runningModel);
          setOllamaRunning(true);
          return true;
        } else {
          setOllamaRunning(false);
        }
      } else {
        setOllamaRunning(false);
      }
      
      // Fallback: 기본 모델 상태 유지
      return true;
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') return true;
      console.warn('Ollama 상태 확인 실패:', error);
      setOllamaRunning(false);
      return true;
    } finally {
      clearTimeout(timeoutId);
    }
  }, []);

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
    <div className={
      `flex flex-col h-full bg-white` +
      (isDesktop ? ' border-r shadow-lg' : ' fixed inset-y-0 left-0 w-full max-w-xs z-50')
    }>
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
      <div className="p-3 sm:p-4 border-b border-emerald-200 bg-gradient-to-r from-emerald-50 to-blue-50 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <h1 
            className="text-xl font-bold bg-gradient-to-r from-emerald-700 to-blue-700 bg-clip-text text-transparent flex items-center cursor-pointer hover:from-emerald-600 hover:to-blue-600 transition-all duration-200"
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
            <span className="mr-2 text-2xl">🧬</span>
            GAIA-BT
          </h1>
          <div className="flex items-center space-x-2">
            <div className={`px-3 py-1 rounded-full text-xs font-medium flex items-center space-x-1 ${
              currentMode === 'deep_research' 
                ? 'bg-gradient-to-r from-emerald-100 to-green-100 text-emerald-800 border border-emerald-200' 
                : 'bg-gradient-to-r from-gray-100 to-slate-100 text-gray-700 border border-gray-200'
            }`}>
              <span>{currentMode === 'deep_research' ? '🧬' : '💬'}</span>
              <span>{currentMode === 'deep_research' ? '딥리서치' : '기본'}</span>
            </div>
            <div className="px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 border border-blue-200 flex items-center space-x-1">
              <span>⚙️</span>
              <span>{currentPromptType === 'default' ? '일반' :
               currentPromptType === 'patent' ? '특허' :
               currentPromptType === 'clinical' ? '임상' :
               currentPromptType === 'research' ? '연구' :
               currentPromptType === 'chemistry' ? '화학' :
               currentPromptType === 'regulatory' ? '규제' : currentPromptType}</span>
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
        <div className="flex space-x-2 mt-4">
          <button
            onClick={handleNewConversation}
            disabled={isLoading || !serverConnected}
            className="flex-1 bg-gradient-to-r from-emerald-500 to-blue-600 hover:from-emerald-600 hover:to-blue-700 disabled:from-gray-300 disabled:to-gray-400 text-white px-4 py-3 rounded-2xl flex items-center justify-center space-x-2 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-lg disabled:shadow-none font-medium"
            title={!serverConnected ? '서버 연결 필요' : '새 대화 시작'}
          >
            <span className="text-lg">✨</span>
            <span>새 연구</span>
          </button>
          
          <button
            onClick={handleModeToggle}
            disabled={isModeChanging || !serverConnected}
            className={`px-4 py-3 rounded-2xl flex items-center justify-center transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg disabled:shadow-none font-medium ${
              currentMode === 'deep_research'
                ? 'bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white focus:ring-emerald-500'
                : 'bg-gradient-to-r from-gray-500 to-slate-600 hover:from-gray-600 hover:to-slate-700 text-white focus:ring-gray-500'
            }`}
            title={!serverConnected ? '서버 연결 필요' : isModeChanging ? '모드 변경 중...' : currentMode === 'deep_research' ? '기본 모드로 전환' : '딥리서치 모드로 전환'}
          >
            {currentMode === 'deep_research' ? <span className="text-lg">🧠</span> : <span className="text-lg">💬</span>}
          </button>
        </div>
      </div>

      {/* 시스템 상태 */}
      <div className="p-4 bg-gradient-to-r from-emerald-50/50 to-blue-50/50 border-t border-emerald-200">
        <button
          onClick={() => setShowSystemStatus(!showSystemStatus)}
          className="w-full text-sm font-semibold text-emerald-700 mb-3 flex items-center justify-between hover:text-emerald-800 transition-colors bg-white/50 p-2 rounded-xl border border-emerald-200/50"
        >
          <div className="flex items-center space-x-2">
            <span className="text-base">📊</span>
            <span>시스템 상태</span>
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
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  ollamaRunning ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
                }`}></div>
                <button
                  onClick={handleOpenModelDialog}
                  disabled={isModelChanging || !serverConnected}
                  className={`font-medium truncate max-w-28 disabled:cursor-not-allowed transition-colors ${
                    ollamaRunning 
                      ? 'text-green-600 hover:text-green-800' 
                      : 'text-gray-600 hover:text-gray-800'
                  } disabled:text-gray-400`}
                  title={!serverConnected ? '서버 연결 필요' : isModelChanging ? '모델 변경 중...' : `현재 모델: ${currentModel || 'N/A'} ${ollamaRunning ? '(실행 중)' : '(중지됨)'} (클릭하여 변경)`}
                >
                  {isModelChanging ? '변경 중...' : (currentModel || 'N/A')}
                </button>
              </div>
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
      <div className="p-4 bg-gradient-to-r from-purple-50/50 to-pink-50/50 border-t border-purple-200">
        <button
          onClick={() => setShowExpertPrompts(!showExpertPrompts)}
          className="w-full text-sm font-semibold text-purple-700 mb-3 flex items-center justify-between hover:text-purple-800 transition-colors bg-white/50 p-2 rounded-xl border border-purple-200/50"
        >
          <div className="flex items-center space-x-2">
            <span className="text-base">⚖️</span>
            <span>전문 프롬프트</span>
          </div>
          {showExpertPrompts ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        
        {showExpertPrompts && (
          <div className="grid grid-cols-2 gap-2">
            {[
              { key: 'default', label: '일반모드', icon: '💬', colors: 'from-gray-50 to-slate-100 border-gray-200 text-gray-700' },
              { key: 'patent', label: '특허검색', icon: '📋', colors: 'from-blue-50 to-blue-100 border-blue-200 text-blue-700' },
              { key: 'clinical', label: '임상시험', icon: '🏥', colors: 'from-green-50 to-emerald-100 border-green-200 text-green-700' },
              { key: 'research', label: '연구분석', icon: '📊', colors: 'from-purple-50 to-purple-100 border-purple-200 text-purple-700' },
              { key: 'chemistry', label: '의약화학', icon: '⚗️', colors: 'from-orange-50 to-orange-100 border-orange-200 text-orange-700' },
              { key: 'regulatory', label: '규제승인', icon: '⚖️', colors: 'from-red-50 to-red-100 border-red-200 text-red-700' }
            ].map(({ key, label, icon, colors }) => (
              <button
                key={key}
                onClick={() => handlePromptChange(key)}
                disabled={isPromptChanging || !serverConnected}
                className={`px-3 py-2 rounded-xl text-xs font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed border flex flex-col items-center space-y-1 hover:shadow-md ${
                  currentPromptType === key 
                    ? `bg-gradient-to-br ${colors} shadow-md scale-105` 
                    : `bg-gradient-to-br from-white to-gray-50 border-gray-200 text-gray-600 hover:${colors.split(' ')[0]} hover:${colors.split(' ')[1]}`
                }`}
                title={!serverConnected ? '서버 연결 필요' : isPromptChanging ? '프롬프트 변경 중...' : `${label} 모드로 변경`}
              >
                <span className="text-sm">{icon}</span>
                <span className="text-center leading-tight">
                  {isPromptChanging && currentPromptType === key ? '변경 중...' : label}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 대화 목록 */}
      <div className="flex-1 overflow-y-auto border-t border-emerald-200 thin-scrollbar bg-gradient-to-b from-white to-emerald-50/30">
        <div className="p-4 bg-gradient-to-r from-emerald-50 to-blue-50 border-b border-emerald-200/50">
          <h3 className="text-sm font-bold text-emerald-700 mb-1 flex items-center">
            <span className="text-base mr-2">📜</span>
            연구 기록
            <span className="ml-2 text-xs font-medium text-emerald-600 bg-gradient-to-r from-emerald-100 to-green-100 px-3 py-1 rounded-full border border-emerald-200">
              {conversations.length}
            </span>
          </h3>
        </div>
        
        {conversations.length === 0 ? (
          <div className="flex-1 flex items-center justify-center p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-emerald-100 to-blue-100 rounded-3xl flex items-center justify-center mx-auto mb-4 border-2 border-emerald-200/50">
                <span className="text-2xl">🧬</span>
              </div>
              <p className="text-sm font-semibold text-emerald-700 mb-2">아직 연구가 없습니다</p>
              <p className="text-xs text-emerald-600">새 연구를 시작해보세요!</p>
            </div>
          </div>
        ) : (
          <div className="p-3 space-y-3">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => handleConversationSelect(conversation.id)}
                className={`group p-4 rounded-2xl cursor-pointer transition-all duration-300 border-2 ${
                  currentConversation?.id === conversation.id
                    ? 'bg-gradient-to-br from-emerald-50 to-blue-50 border-emerald-300/70 shadow-lg scale-[1.02]'
                    : 'bg-gradient-to-br from-white to-gray-50/50 border-gray-200/50 hover:from-emerald-50/50 hover:to-blue-50/50 hover:border-emerald-300/50 hover:shadow-md hover:scale-[1.01]'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center space-x-2 flex-1 mr-2">
                    <span className="text-sm flex-shrink-0">🧬</span>
                    <h4 className={`font-semibold truncate flex-1 text-sm ${
                      currentConversation?.id === conversation.id
                        ? 'bg-gradient-to-r from-emerald-700 to-blue-700 bg-clip-text text-transparent'
                        : 'text-gray-800'
                    }`}>
                      {conversation.title || '새 연구'}
                    </h4>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`text-xs whitespace-nowrap font-medium ${
                      currentConversation?.id === conversation.id
                        ? 'text-emerald-600'
                        : 'text-gray-500'
                    }`}>
                      {formatDate(conversation.updatedAt)}
                    </span>
                    {currentConversation?.id !== conversation.id && (
                      <button
                        onClick={(e) => handleDeleteConversation(conversation.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-1.5 rounded-xl hover:bg-red-100 transition-all duration-300 hover:scale-110"
                        title="대화 삭제"
                      >
                        <Trash2 className="w-3 h-3 text-red-500" />
                      </button>
                    )}
                  </div>
                </div>
                
                {conversation.messages && conversation.messages.length > 0 && (
                  <div className={`text-xs mb-3 overflow-hidden p-2 rounded-xl border ${
                    currentConversation?.id === conversation.id
                      ? 'bg-white/60 border-emerald-200/50 text-emerald-700'
                      : 'bg-gray-50/80 border-gray-200/50 text-gray-600'
                  }`} style={{
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical'
                  }}>
                    {conversation.messages[conversation.messages.length - 1].content}
                  </div>
                )}
                
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-1">
                    <span className="text-xs">💬</span>
                    <span className={`text-xs font-medium ${
                      currentConversation?.id === conversation.id
                        ? 'text-emerald-600'
                        : 'text-gray-500'
                    }`}>
                      {conversation.messages?.length || 0}개 메시지
                    </span>
                  </div>
                  {currentConversation?.id === conversation.id && (
                    <div className="flex items-center space-x-1">
                      <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                      <span className="text-xs text-emerald-600 font-bold">진행 중</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* 하단 정보 */}
      <div className="p-4 border-t border-emerald-200 bg-gradient-to-r from-emerald-50 to-blue-50 flex-shrink-0">
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-1">
            <span className="text-sm">🧬</span>
            <p className="text-xs font-bold bg-gradient-to-r from-emerald-700 to-blue-700 bg-clip-text text-transparent">
              GAIA-BT v3.5
            </p>
          </div>
          <p className="text-xs text-emerald-600 font-medium">
            신약개발 AI 연구 어시스턴트
          </p>
        </div>
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