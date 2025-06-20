'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { useChatStore } from '@/store/chatStore';
import { staggerContainerVariants, staggerItemVariants, cardVariants } from '@/utils/animations';
import { 
  X,
  Settings,
  Database,
  CheckCircle,
  XCircle,
  Loader2,
  Info,
  HelpCircle,
  Settings2,
  CircleSlash,
  Bug,
  RefreshCw
} from 'lucide-react';

interface MCPServer {
  name: string;
  status: 'running' | 'stopped' | 'error';
  port: number;
  description: string;
  responseTime?: number;
}

interface SidebarProps {
  isMobile: boolean;
  width: number;
  onClose: () => void;
}

export default function Sidebar({ isMobile, width, onClose }: SidebarProps) {
  const [showMcpStatus, setShowMcpStatus] = useState(false);
  const [showPromptSelector, setShowPromptSelector] = useState(false);
  const [debugMode, setDebugMode] = useState(false);
  const [mcpOutputVisible, setMcpOutputVisible] = useState(false);
  const defaultMcpServers: MCPServer[] = [
    { name: 'BiomCP', status: 'stopped', port: 8080, description: '논문 및 바이오 데이터 검색' },
    { name: 'ChEMBL', status: 'stopped', port: 8081, description: '화학 구조 및 약물 정보' },
    { name: 'DrugBank', status: 'stopped', port: 8082, description: '약물 데이터베이스' },
    { name: 'OpenTargets', status: 'stopped', port: 8083, description: '타겟-질병 연관성' },
    { name: 'Sequential Thinking', status: 'stopped', port: 8084, description: '단계별 추론 AI' },
    { name: 'Playwright', status: 'stopped', port: 8085, description: '웹 자동화 및 데이터 수집' }
  ];
  const [mcpServers, setMcpServers] = useState<MCPServer[]>(defaultMcpServers);

  const { 
    currentSessionId, 
    sessions, 
    systemStatus,
    updateSessionPromptType,
    checkSystemHealth 
  } = useChatStore();
  
  const currentSession = currentSessionId ? sessions[currentSessionId] : null;

  // MCP 서버 상태 업데이트
  useEffect(() => {
    const updateMcpStatus = () => {
      setMcpServers(prev => {
        if (!Array.isArray(prev)) return defaultMcpServers;
        return prev.map(server => ({
          ...server,
          status: systemStatus.apiConnected ? 'running' : 'stopped',
          responseTime: systemStatus.apiConnected ? Math.floor(Math.random() * 50) + 20 : undefined
        }));
      });
    };

    updateMcpStatus();
  }, [systemStatus.apiConnected]);

  // 시스템 헬스 체크
  const handleHealthCheck = async () => {
    await checkSystemHealth();
  };

  // 프롬프트 변경
  const handlePromptChange = (promptType: string) => {
    if (!currentSessionId) return;
    updateSessionPromptType(currentSessionId, promptType);
    setShowPromptSelector(false);
  };

  // MCP 명령어 실행
  const handleMcpCommand = async (command: string) => {
    if (!currentSessionId) return;
    
    try {
      const response = await fetch('/api/gaia-bt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: 'function',
          function_name: 'mcp_command',
          parameters: { command }
        }),
      });
      
      if (response.ok) {
        await handleHealthCheck();
      }
    } catch (error) {
      console.error('MCP 명령어 실행 실패:', error);
    }
  };

  return (
    <motion.div 
      className={`${sidebarWidth} bg-gray-800 border-r border-gray-700 flex flex-col h-full ${
        isMobile ? 'fixed left-0 top-0 z-40 shadow-2xl' : 'relative'
      }`}
      initial={{ x: isMobile ? -100 : 0, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: isMobile ? -100 : 0, opacity: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      {/* 사이드바 헤더 */}
      <motion.div 
        className="p-4 border-b border-gray-700"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.3 }}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">시스템 제어</h2>
          {isMobile && (
            <Button
              onClick={onClose}
              variant="ghost"
              size="sm"
              className="text-gray-400 hover:text-white"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </motion.div>

      {/* 스크롤 가능한 콘텐츠 영역 */}
      <motion.div 
        className="flex-1 overflow-y-auto p-4 space-y-4"
        variants={staggerContainerVariants}
        initial="initial"
        animate="animate"
      >
        
        {/* 시스템 상태 카드 */}
        <motion.div variants={staggerItemVariants}>
          <Card className="p-4 bg-gray-700 border-gray-600 hover:bg-gray-600/50 transition-colors duration-200">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-white flex items-center">
              <Settings className="h-4 w-4 mr-2" />
              시스템 상태
            </h3>
            <Button
              onClick={handleHealthCheck}
              variant="outline"
              size="sm"
              className="border-gray-500 text-gray-300 hover:bg-gray-600"
            >
              <RefreshCw className="h-3 w-3" />
            </Button>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">API 연결</span>
              <div className="flex items-center space-x-1">
                {systemStatus.apiConnected ? (
                  <>
                    <CheckCircle className="h-3 w-3 text-green-400" />
                    <span className="text-xs text-green-400">연결됨</span>
                  </>
                ) : (
                  <>
                    <XCircle className="h-3 w-3 text-red-400" />
                    <span className="text-xs text-red-400">연결 끊김</span>
                  </>
                )}
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">세션 ID</span>
              <span className="text-xs text-blue-400 font-mono">
                {currentSessionId ? currentSessionId.slice(-8) : 'N/A'}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">메시지 수</span>
              <span className="text-xs text-gray-400">
                {currentSession?.messages.length || 0}
              </span>
            </div>
          </div>
          </Card>
        </motion.div>

        {/* MCP 서버 상태 */}
        <motion.div variants={staggerItemVariants}>
          <Card className="p-4 bg-gray-700 border-gray-600 hover:bg-gray-600/50 transition-colors duration-200">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-white flex items-center">
              <Database className="h-4 w-4 mr-2" />
              MCP 서버
            </h3>
            <Button
              onClick={() => setShowMcpStatus(!showMcpStatus)}
              variant="outline"
              size="sm"
              className="border-gray-500 text-gray-300 hover:bg-gray-600"
            >
              {showMcpStatus ? '숨기기' : '자세히'}
            </Button>
          </div>

          <div className="space-y-2">
            {Array.isArray(mcpServers) && mcpServers.length > 0 ? mcpServers.slice(0, showMcpStatus ? mcpServers.length : 3).map((server) => (
              <div key={server.name} className="flex items-center justify-between p-2 rounded bg-gray-800">
                <div className="flex items-center space-x-2">
                  {server.status === 'running' ? (
                    <CheckCircle className="h-3 w-3 text-green-400" />
                  ) : server.status === 'error' ? (
                    <XCircle className="h-3 w-3 text-red-400" />
                  ) : (
                    <CircleSlash className="h-3 w-3 text-gray-400" />
                  )}
                  <div>
                    <div className="text-xs font-medium text-white">{server.name}</div>
                    {showMcpStatus && (
                      <div className="text-xs text-gray-400">{server.description}</div>
                    )}
                  </div>
                </div>
                
                {showMcpStatus && server.responseTime && (
                  <span className="text-xs text-gray-400">{server.responseTime}ms</span>
                )}
              </div>
            )) : (
              <div className="text-center text-gray-400 py-2">
                MCP 서버 정보를 로드하는 중...
              </div>
            )}
          </div>

          {showMcpStatus && (
            <div className="mt-3 space-y-2">
              <Button
                onClick={() => handleMcpCommand('start')}
                variant="outline"
                size="sm"
                className="w-full border-green-600 text-green-400 hover:bg-green-600/20"
              >
                MCP 서버 시작
              </Button>
              <Button
                onClick={() => handleMcpCommand('stop')}
                variant="outline"
                size="sm"
                className="w-full border-red-600 text-red-400 hover:bg-red-600/20"
              >
                MCP 서버 중지
              </Button>
            </div>
          )}
          </Card>
        </motion.div>

        {/* 프롬프트 선택 */}
        <motion.div variants={staggerItemVariants}>
          <Card className="p-4 bg-gray-700 border-gray-600 hover:bg-gray-600/50 transition-colors duration-200">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-white flex items-center">
              <Settings2 className="h-4 w-4 mr-2" />
              전문 모드
            </h3>
            <Badge variant="outline" className="text-blue-300 border-blue-400">
              {currentSession?.prompt_type === 'clinical' && '임상시험'}
              {currentSession?.prompt_type === 'research' && '연구분석'}
              {currentSession?.prompt_type === 'chemistry' && '의약화학'}
              {currentSession?.prompt_type === 'regulatory' && '규제전문'}
              {(!currentSession?.prompt_type || currentSession?.prompt_type === 'default') && '기본모드'}
            </Badge>
          </div>

          <div className="space-y-2">
            {[
              { id: 'default', name: '💊 기본모드', desc: '일반적인 신약개발 상담' },
              { id: 'clinical', name: '🏥 임상시험', desc: '임상시험 설계 및 분석' },
              { id: 'research', name: '🔬 연구분석', desc: '문헌 검토 및 데이터 분석' },
              { id: 'chemistry', name: '⚗️ 의약화학', desc: '분자 설계 및 화학 구조' },
              { id: 'regulatory', name: '📋 규제전문', desc: '글로벌 의약품 규제' }
            ].map((prompt) => (
              <Button
                key={prompt.id}
                onClick={() => handlePromptChange(prompt.id)}
                variant={currentSession?.prompt_type === prompt.id ? 'default' : 'outline'}
                size="sm"
                className={`w-full text-left justify-start ${
                  currentSession?.prompt_type === prompt.id
                    ? 'bg-blue-600 text-white'
                    : 'border-gray-500 text-gray-300 hover:bg-gray-600'
                }`}
              >
                <div>
                  <div className="text-xs font-medium">{prompt.name}</div>
                  <div className="text-xs opacity-75">{prompt.desc}</div>
                </div>
              </Button>
            ))}
          </div>
          </Card>
        </motion.div>

        {/* 빠른 명령어 */}
        <motion.div variants={staggerItemVariants}>
          <Card className="p-4 bg-gray-700 border-gray-600 hover:bg-gray-600/50 transition-colors duration-200">
          <h3 className="font-medium text-white mb-3 flex items-center">
            <HelpCircle className="h-4 w-4 mr-2" />
            빠른 명령어
          </h3>
          
          <div className="grid grid-cols-1 gap-2">
            {[
              { cmd: '/help', desc: '도움말 표시' },
              { cmd: '/status', desc: '시스템 상태 확인' },
              { cmd: '/clear', desc: '대화 초기화' },
              { cmd: '/mcp start', desc: 'Deep Research 시작' },
              { cmd: '/normal', desc: '일반 모드로 전환' }
            ].map((item) => (
              <div key={item.cmd} className="text-xs p-2 rounded bg-gray-800">
                <div className="font-mono text-blue-400">{item.cmd}</div>
                <div className="text-gray-400">{item.desc}</div>
              </div>
            ))}
          </div>
          </Card>
        </motion.div>

        {/* 개발자 옵션 */}
        <motion.div variants={staggerItemVariants}>
          <Card className="p-4 bg-gray-700 border-gray-600 hover:bg-gray-600/50 transition-colors duration-200">
          <h3 className="font-medium text-white mb-3 flex items-center">
            <Bug className="h-4 w-4 mr-2" />
            개발자 옵션
          </h3>
          
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">디버그 모드</span>
              <Button
                onClick={() => setDebugMode(!debugMode)}
                variant="outline"
                size="sm"
                className={`${
                  debugMode 
                    ? 'border-green-600 text-green-400 bg-green-600/20' 
                    : 'border-gray-500 text-gray-300'
                }`}
              >
                {debugMode ? 'ON' : 'OFF'}
              </Button>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">MCP 출력 표시</span>
              <Button
                onClick={() => setMcpOutputVisible(!mcpOutputVisible)}
                variant="outline"
                size="sm"
                className={`${
                  mcpOutputVisible 
                    ? 'border-blue-600 text-blue-400 bg-blue-600/20' 
                    : 'border-gray-500 text-gray-300'
                }`}
              >
                {mcpOutputVisible ? 'SHOW' : 'HIDE'}
              </Button>
            </div>
          </div>
          
          <div className="mt-3 p-2 rounded bg-gray-800">
            <div className="text-xs text-gray-400">
              마지막 헬스 체크: {new Date(systemStatus.lastHealthCheck).toLocaleTimeString()}
            </div>
          </div>
          </Card>
        </motion.div>

      </motion.div>
    </motion.div>
  );
}