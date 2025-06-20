'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useChatStore } from '@/store/chatStore';
import { staggerContainerVariants, staggerItemVariants, floatingVariants } from '@/utils/animations';
import { 
  Menu, 
  Settings, 
  RefreshCw, 
  Beaker, 
  Database,
  CheckCircle,
  XCircle,
  Loader2,
  User
} from 'lucide-react';

interface HeaderProps {
  showSidebar: boolean;
  onToggleSidebar: () => void;
  layoutMode?: 'compact' | 'normal' | 'spacious';
  onLayoutModeChange?: (mode: 'compact' | 'normal' | 'spacious') => void;
}

export default function Header({ showSidebar, onToggleSidebar, layoutMode = 'normal', onLayoutModeChange }: HeaderProps) {
  const [currentModel, setCurrentModel] = useState('gemma3');
  const [isModelChanging, setIsModelChanging] = useState(false);
  const [showModelDialog, setShowModelDialog] = useState(false);
  const defaultModels = [
    { id: 'gemma3', name: 'Gemma 3', description: '범용 언어 모델', icon: '💎' },
    { id: 'gemma2:latest', name: 'Gemma 2', description: '빠르고 효율적인 Google 모델', icon: '💎' },
    { id: 'llama3.1:latest', name: 'Llama 3.1', description: '강력한 추론 능력의 Meta 모델', icon: '🦙' },
    { id: 'qwen2.5:latest', name: 'Qwen 2.5', description: '다국어 지원 우수 Alibaba 모델', icon: '🌏' }
  ];
  const [availableModels, setAvailableModels] = useState<Array<{id: string, name: string, description: string, icon: string}>>(defaultModels);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  const [systemInfo, setSystemInfo] = useState<any>(null);

  const { 
    currentSessionId, 
    sessions, 
    updateSessionMode,
    updateSessionPromptType,
    updateSessionModel,
    systemStatus 
  } = useChatStore();
  
  const currentSession = currentSessionId ? sessions[currentSessionId] : null;

  // Ollama 모델 목록 가져오기
  const fetchAvailableModels = async () => {
    setIsLoadingModels(true);
    try {
      const response = await fetch('http://localhost:11434/api/tags', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.models && Array.isArray(data.models)) {
          const ollamaModelList = data.models.map((model: any) => ({
            id: model.name,
            name: model.name.split(':')[0],
            description: `크기: ${model.size ? (model.size / (1024 * 1024 * 1024)).toFixed(1) + 'GB' : '알 수 없음'}`,
            icon: getModelIcon(model.name)
          }));
          
          // 기본 API 모델과 Ollama 모델을 합치기
          const mergedModels = [...defaultModels, ...ollamaModelList];
          setAvailableModels(mergedModels);
        }
      }
    } catch (error) {
      console.error('Ollama 모델 목록 가져오기 실패:', error);
    } finally {
      setIsLoadingModels(false);
    }
  };

  const getModelIcon = (modelName: string) => {
    if (modelName.includes('gemma')) return '💎';
    if (modelName.includes('llama')) return '🦙';
    if (modelName.includes('qwen')) return '🌏';
    if (modelName.includes('mistral')) return '🌪️';
    if (modelName.includes('phi')) return '🔬';
    return '🤖';
  };

  // 초기 모델 목록 로드
  useEffect(() => {
    fetchAvailableModels();
  }, []);

  // 모드 전환 핸들러
  const handleModeToggle = async () => {
    if (!currentSessionId) return;
    
    const newMode = currentSession?.mode === 'deep_research' ? 'normal' : 'deep_research';
    updateSessionMode(currentSessionId, newMode);
  };

  // 모델 변경 핸들러  
  const handleModelChange = async (modelId: string) => {
    if (!currentSessionId) return;
    
    setIsModelChanging(true);
    try {
      // API 모델 변경 요청
      const response = await fetch('/api/gaia-bt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: 'function',
          function_name: 'change_model',
          parameters: { model: modelId }
        }),
      });

      if (response.ok) {
        updateSessionModel(currentSessionId, modelId);
        setCurrentModel(modelId);
      }
    } catch (error) {
      console.error('모델 변경 실패:', error);
    } finally {
      setIsModelChanging(false);
      setShowModelDialog(false);
    }
  };

  // 프롬프트 타입 변경
  const handlePromptChange = (promptType: string) => {
    if (!currentSessionId) return;
    updateSessionPromptType(currentSessionId, promptType);
  };

  return (
    <motion.div 
      className="w-full bg-gradient-to-r from-blue-900 via-purple-900 to-indigo-900 border-b border-gray-700 shadow-lg"
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      {/* 메인 헤더 */}
      <motion.div 
        className="px-6 py-4"
        variants={staggerContainerVariants}
        initial="initial"
        animate="animate"
      >
        <div className="flex items-center justify-between">
          {/* 왼쪽: 로고 및 토글 버튼 */}
          <motion.div 
            className="flex items-center space-x-4"
            variants={staggerItemVariants}
          >
            <Button
              onClick={onToggleSidebar}
              variant="ghost"
              size="sm"
              className="text-white hover:bg-white/10"
            >
              <Menu className="h-4 w-4" />
            </Button>
            
            <div className="flex items-center space-x-3">
              <motion.div 
                className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-lg flex items-center justify-center"
                variants={floatingVariants}
                animate="animate"
                whileHover={{ scale: 1.1, rotate: 5 }}
                whileTap={{ scale: 0.95 }}
              >
                <Beaker className="h-5 w-5 text-white" />
              </motion.div>
              <motion.div
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.3, duration: 0.4 }}
              >
                <h1 className="text-xl font-bold text-white">GAIA-BT</h1>
                <p className="text-xs text-blue-200">신약개발 AI 어시스턴트</p>
              </motion.div>
            </div>
          </motion.div>

          {/* 중앙: 상태 표시 */}
          <motion.div 
            className="flex items-center space-x-4"
            variants={staggerItemVariants}
          >
            {/* 모드 표시 및 전환 */}
            <motion.div 
              className="flex items-center space-x-2"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.3 }}
            >
              <Badge 
                variant={currentSession?.mode === 'deep_research' ? 'default' : 'secondary'}
                className={`${
                  currentSession?.mode === 'deep_research' 
                    ? 'bg-green-600 text-white' 
                    : 'bg-gray-600 text-white'
                }`}
              >
                {currentSession?.mode === 'deep_research' ? (
                  <>
                    <Database className="h-3 w-3 mr-1" />
                    Deep Research
                  </>
                ) : (
                  <>
                    <User className="h-3 w-3 mr-1" />
                    일반 모드
                  </>
                )}
              </Badge>
              
              <Button
                onClick={handleModeToggle}
                size="sm"
                variant="outline"
                className="text-white border-white/20 hover:bg-white/10"
              >
                {currentSession?.mode === 'deep_research' ? '일반 모드' : 'Deep Research'}
              </Button>
            </motion.div>

            {/* 프롬프트 타입 표시 */}
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.5, duration: 0.3 }}
            >
              <Badge variant="outline" className="text-blue-200 border-blue-300">
                {currentSession?.prompt_type === 'clinical' && '🏥 임상시험'}
                {currentSession?.prompt_type === 'research' && '🔬 연구분석'}
                {currentSession?.prompt_type === 'chemistry' && '⚗️ 의약화학'}
                {currentSession?.prompt_type === 'regulatory' && '📋 규제전문'}
                {(!currentSession?.prompt_type || currentSession?.prompt_type === 'default') && '💊 기본모드'}
              </Badge>
            </motion.div>
          </motion.div>

          {/* 오른쪽: 모델 정보 및 설정 */}
          <motion.div 
            className="flex items-center space-x-3"
            variants={staggerItemVariants}
          >
            {/* 레이아웃 모드 전환 */}
            {onLayoutModeChange && (
              <Button
                onClick={() => {
                  const modes: Array<'compact' | 'normal' | 'spacious'> = ['compact', 'normal', 'spacious'];
                  const currentIndex = modes.indexOf(layoutMode);
                  const nextMode = modes[(currentIndex + 1) % modes.length];
                  onLayoutModeChange(nextMode);
                }}
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/10"
                title="레이아웃 모드 변경 (Ctrl+L)"
              >
                {layoutMode === 'compact' && '🔍'}
                {layoutMode === 'normal' && '📐'}
                {layoutMode === 'spacious' && '🖥️'}
              </Button>
            )}
            
            {/* 현재 모델 표시 */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-blue-200">모델:</span>
              <Badge 
                variant="outline" 
                className="text-white border-white/30 cursor-pointer hover:bg-white/10"
                onClick={() => setShowModelDialog(true)}
              >
                {isModelChanging ? (
                  <Loader2 className="h-3 w-3 animate-spin mr-1" />
                ) : (
                  <span>{currentSession?.model || currentModel}</span>
                )}
              </Badge>
            </div>

            {/* 시스템 상태 */}
            <div className="flex items-center space-x-2">
              {systemStatus.apiConnected ? (
                <CheckCircle className="h-4 w-4 text-green-400" />
              ) : (
                <XCircle className="h-4 w-4 text-red-400" />
              )}
              <span className="text-xs text-blue-200">
                {systemStatus.apiConnected ? '연결됨' : '연결 끊김'}
              </span>
            </div>
          </motion.div>
        </div>

        {/* 빠른 명령어 버튼들 */}
        <motion.div 
          className="flex items-center space-x-2 mt-3"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.4 }}
        >
          <div className="flex space-x-2">
            {['clinical', 'research', 'chemistry', 'regulatory', 'default'].map((type) => (
              <Button
                key={type}
                onClick={() => handlePromptChange(type)}
                size="sm"
                variant={currentSession?.prompt_type === type ? 'default' : 'outline'}
                className={`text-xs ${
                  currentSession?.prompt_type === type
                    ? 'bg-blue-600 text-white'
                    : 'text-blue-200 border-blue-400 hover:bg-blue-700/30'
                }`}
              >
                {type === 'clinical' && '🏥 임상시험'}
                {type === 'research' && '🔬 연구분석'}
                {type === 'chemistry' && '⚗️ 의약화학'}
                {type === 'regulatory' && '📋 규제전문'}
                {type === 'default' && '💊 기본모드'}
              </Button>
            ))}
          </div>
          
          <Button
            onClick={fetchAvailableModels}
            size="sm"
            variant="outline"
            className="text-blue-200 border-blue-400 hover:bg-blue-700/30"
            disabled={isLoadingModels}
          >
            {isLoadingModels ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              <RefreshCw className="h-3 w-3" />
            )}
          </Button>
        </motion.div>
      </motion.div>

      {/* 모델 선택 다이얼로그 */}
      <AnimatePresence>
        {showModelDialog && (
          <motion.div 
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowModelDialog(false)}
          >
            <motion.div 
              className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 border border-gray-700"
              initial={{ scale: 0.8, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.8, opacity: 0, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
            <h3 className="text-lg font-semibold text-white mb-4">모델 선택</h3>
            
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {Array.isArray(availableModels) && availableModels.length > 0 ? availableModels.map((model) => (
                <Button
                  key={model.id}
                  onClick={() => handleModelChange(model.id)}
                  variant="outline"
                  className="w-full justify-start text-left p-3 border-gray-600 hover:bg-gray-700"
                  disabled={isModelChanging}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{model.icon}</span>
                    <div>
                      <div className="font-medium text-white">{model.name}</div>
                      <div className="text-xs text-gray-400">{model.description}</div>
                    </div>
                  </div>
                </Button>
              )) : (
                <div className="text-center text-gray-400 py-4">
                  사용 가능한 모델을 로드하는 중...
                </div>
              )}
            </div>
            
            <div className="flex justify-end space-x-2 mt-4">
              <Button
                onClick={() => setShowModelDialog(false)}
                variant="outline"
                size="sm"
                className="border-gray-600 text-gray-300 hover:bg-gray-700"
              >
                취소
              </Button>
            </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}