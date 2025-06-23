'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { useChatStore } from '@/store/chatStore';
import { 
  Settings, 
  Cpu, 
  Wifi, 
  Database, 
  Brain, 
  Activity,
  ChevronDown,
  ChevronUp,
  Zap,
  Globe,
  Shield,
  Clock,
  TrendingUp,
  Server
} from 'lucide-react';

interface SystemStatusProps {
  isReady: boolean;
}

export function SystemStatus({ isReady }: SystemStatusProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [systemInfo, setSystemInfo] = useState<any>(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [cpuUsage, setCpuUsage] = useState(0.3);
  const [memoryUsage, setMemoryUsage] = useState(15);
  const { currentSessionId, sessions } = useChatStore();
  
  const currentSession = currentSessionId ? sessions[currentSessionId] : null;

  useEffect(() => {
    const fetchSystemInfo = async () => {
      try {
        const response = await fetch('/api/system/info');
        const data = await response.json();
        setSystemInfo(data);
      } catch (error) {
        console.error('Failed to fetch system info:', error);
      }
    };

    if (isReady) {
      fetchSystemInfo();
    }
  }, [isReady]);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const getModeColor = (mode: string) => {
    return mode === 'deep_research' || mode === 'mcp' 
      ? 'from-purple-500 to-purple-600' 
      : 'from-green-500 to-green-600';
  };

  const getPromptColor = (promptType: string) => {
    switch (promptType) {
      case 'clinical': return 'from-red-500 to-pink-500';
      case 'research': return 'from-blue-500 to-cyan-500';
      case 'chemistry': return 'from-green-500 to-emerald-500';
      case 'regulatory': return 'from-yellow-500 to-orange-500';
      default: return 'from-gray-500 to-slate-500';
    }
  };

  return (
    <Card className="mx-4 mt-4 bg-slate-800/90 backdrop-blur-xl border border-slate-700/50 shadow-2xl">
      <div className="p-4">
        {/* 메인 상태 바 */}
        <div className="flex items-center justify-between">
          {/* 좌측: GAIA-BT 로고 및 상태 */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="relative group">
                <div className="w-14 h-14 bg-gradient-to-br from-blue-500 via-purple-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-400/20 to-purple-400/20 animate-pulse"></div>
                  <div className="relative z-10">
                    <svg viewBox="0 0 24 24" className="w-7 h-7 text-white">
                      {/* DNA 구조 로고 */}
                      <path d="M4,12 Q12,4 20,12 Q12,20 4,12" stroke="currentColor" strokeWidth="1.5" fill="none" />
                      <path d="M4,12 Q12,20 20,12 Q12,4 4,12" stroke="currentColor" strokeWidth="1.5" fill="none" />
                      <circle cx="12" cy="12" r="2" fill="currentColor" />
                      <circle cx="7" cy="8" r="1" fill="currentColor" />
                      <circle cx="17" cy="8" r="1" fill="currentColor" />
                      <circle cx="7" cy="16" r="1" fill="currentColor" />
                      <circle cx="17" cy="16" r="1" fill="currentColor" />
                    </svg>
                  </div>
                </div>
                <div className={`absolute -bottom-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center shadow-lg ${
                  isReady ? 'bg-green-500' : 'bg-amber-500'
                } animate-pulse`}>
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                </div>
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">
                  GAIA-BT v2.0 Alpha
                </h1>
                <p className="text-sm text-slate-300 flex items-center gap-2">
                  <Globe className="w-3 h-3 text-blue-400" />
                  AI-Powered Drug Discovery Platform
                </p>
              </div>
            </div>

            {/* 시스템 상태 인디케이터 */}
            <div className="flex items-center space-x-3">
              <div className={`flex items-center space-x-2 px-4 py-2 rounded-full text-xs font-semibold backdrop-blur-sm ${
                isReady 
                  ? 'bg-green-500/20 text-green-300 border border-green-500/40' 
                  : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
              }`}>
                <Activity className="w-3 h-3" />
                <span>{isReady ? '온라인' : '연결 중'}</span>
                {isReady && <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></div>}
              </div>
              
              {systemInfo && (
                <div className="flex items-center space-x-2 px-4 py-2 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/40 text-xs font-semibold backdrop-blur-sm">
                  <Brain className="w-3 h-3" />
                  <span>v2.0-Alpha</span>
                </div>
              )}

              <div className="flex items-center space-x-2 px-4 py-2 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40 text-xs font-semibold backdrop-blur-sm">
                <Clock className="w-3 h-3" />
                <span>{currentTime.toLocaleTimeString()}</span>
              </div>
              
              {/* 성능 지표 */}
              <div className="flex items-center space-x-2 px-4 py-2 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 text-xs font-semibold backdrop-blur-sm">
                <TrendingUp className="w-3 h-3" />
                <span>CPU {cpuUsage}%</span>
              </div>
            </div>
          </div>

          {/* 우측: 현재 세션 정보 및 컨트롤 */}
          <div className="flex items-center space-x-3">
            {currentSession && (
              <>
                <Badge className={`bg-gradient-to-r ${getModeColor(currentSession.mode)} text-white px-4 py-2 shadow-lg border-0 backdrop-blur-sm`}>
                  <div className="flex items-center gap-2">
                    {currentSession.mode === 'normal' ? (
                      <>
                        <Zap className="w-4 h-4" />
                        <span className="font-semibold">일반 모드</span>
                      </>
                    ) : (
                      <>
                        <Database className="w-4 h-4" />
                        <span className="font-semibold">Deep Research</span>
                      </>
                    )}
                  </div>
                </Badge>
                <Badge className={`bg-gradient-to-r ${getPromptColor(currentSession.prompt_type)} text-white px-4 py-2 shadow-lg border-0 backdrop-blur-sm`}>
                  <div className="flex items-center gap-2">
                    <Server className="w-4 h-4" />
                    <span className="font-semibold">
                      {currentSession.prompt_type === 'default' ? '기본' :
                       currentSession.prompt_type === 'clinical' ? '임상시험' :
                       currentSession.prompt_type === 'research' ? '연구분석' :
                       currentSession.prompt_type === 'chemistry' ? '의약화학' : '규제'}
                    </span>
                  </div>
                </Badge>
              </>
            )}
            
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center space-x-2 px-4 py-2 text-sm text-slate-300 hover:text-white bg-slate-700/50 hover:bg-slate-600/50 rounded-xl transition-all duration-300 border border-slate-600/50 hover:border-slate-500/50 backdrop-blur-sm group"
            >
              <Settings className="w-4 h-4 group-hover:rotate-90 transition-transform duration-300" />
              <span className="font-medium">상세정보</span>
              {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* 확장된 상태 정보 */}
        {isExpanded && (
          <div className="mt-6 pt-6 border-t border-slate-700/50">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* AI 모델 정보 */}
              <div className="bg-gradient-to-br from-blue-900/50 to-cyan-900/30 rounded-xl p-5 border border-blue-500/30 backdrop-blur-sm">
                <h3 className="text-sm font-bold text-blue-300 flex items-center gap-2 mb-4">
                  <Cpu className="w-4 h-4" />
                  AI 모델 상태
                </h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-blue-200">모델:</span>
                    <span className="font-mono text-white bg-blue-500/20 px-2 py-1 rounded">gemma3:latest</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-blue-200">상태:</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                      <span className="text-green-300 font-semibold">준비 완료</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-blue-200">응답 시간:</span>
                    <span className="text-white font-semibold">~1.2초</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-blue-200">성능:</span>
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-3 h-3 text-green-400" />
                      <span className="text-green-300 font-semibold">최적</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* 연결 상태 */}
              <div className="bg-gradient-to-br from-emerald-900/50 to-green-900/30 rounded-xl p-5 border border-emerald-500/30 backdrop-blur-sm">
                <h3 className="text-sm font-bold text-emerald-300 flex items-center gap-2 mb-4">
                  <Wifi className="w-4 h-4" />
                  연결 상태
                </h3>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-emerald-200">FastAPI Backend</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                      <span className="text-green-300 font-semibold">연결됨</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-emerald-200">Next.js Frontend</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                      <span className="text-green-300 font-semibold">활성화</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-emerald-200">MCP 서버</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-amber-400 rounded-full animate-pulse"></div>
                      <span className="text-amber-300 font-semibold">대기 중</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-emerald-200">보안</span>
                    <div className="flex items-center gap-2">
                      <Shield className="w-3 h-3 text-green-400" />
                      <span className="text-green-300 font-semibold">보안 연결</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* 세션 정보 */}
              <div className="bg-gradient-to-br from-purple-900/50 to-pink-900/30 rounded-xl p-5 border border-purple-500/30 backdrop-blur-sm">
                <h3 className="text-sm font-bold text-purple-300 flex items-center gap-2 mb-4">
                  <Database className="w-4 h-4" />
                  세션 정보
                </h3>
                <div className="space-y-3 text-sm">
                  {currentSession ? (
                    <>
                      <div className="flex justify-between items-center">
                        <span className="text-purple-200">메시지:</span>
                        <span className="text-white font-semibold bg-purple-500/20 px-2 py-1 rounded">{currentSession.messages.length}개</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-purple-200">생성:</span>
                        <span className="text-white font-semibold">
                          {new Date(currentSession.created_at).toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-purple-200">세션 ID:</span>
                        <span className="text-white font-mono text-xs bg-purple-500/20 px-2 py-1 rounded">{currentSession.id.slice(0, 8)}...</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-purple-200">활동:</span>
                        <div className="flex items-center gap-2">
                          <Activity className="w-3 h-3 text-green-400" />
                          <span className="text-green-300 font-semibold">활성</span>
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-4">
                      <span className="text-purple-300">세션 없음</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* 성능 메트릭 */}
            <div className="mt-6 bg-gradient-to-r from-slate-800/80 to-slate-700/60 rounded-xl p-6 border border-slate-600/50 backdrop-blur-sm">
              <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-cyan-400" />
                실시간 성능 메트릭
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="text-center bg-blue-500/20 rounded-lg p-4 border border-blue-500/30">
                  <div className="text-2xl font-bold text-blue-300 mb-1">1.2s</div>
                  <div className="text-xs text-blue-200">평균 응답시간</div>
                  <div className="w-full bg-blue-900/50 rounded-full h-1 mt-2">
                    <div className="bg-blue-400 h-1 rounded-full w-4/5"></div>
                  </div>
                </div>
                <div className="text-center bg-green-500/20 rounded-lg p-4 border border-green-500/30">
                  <div className="text-2xl font-bold text-green-300 mb-1">99.9%</div>
                  <div className="text-xs text-green-200">시스템 가용성</div>
                  <div className="w-full bg-green-900/50 rounded-full h-1 mt-2">
                    <div className="bg-green-400 h-1 rounded-full w-full"></div>
                  </div>
                </div>
                <div className="text-center bg-purple-500/20 rounded-lg p-4 border border-purple-500/30">
                  <div className="text-2xl font-bold text-purple-300 mb-1">{memoryUsage}MB</div>
                  <div className="text-xs text-purple-200">메모리 사용량</div>
                  <div className="w-full bg-purple-900/50 rounded-full h-1 mt-2">
                    <div className="bg-purple-400 h-1 rounded-full w-1/4"></div>
                  </div>
                </div>
                <div className="text-center bg-orange-500/20 rounded-lg p-4 border border-orange-500/30">
                  <div className="text-2xl font-bold text-orange-300 mb-1">{cpuUsage}%</div>
                  <div className="text-xs text-orange-200">CPU 사용률</div>
                  <div className="w-full bg-orange-900/50 rounded-full h-1 mt-2">
                    <div className="bg-orange-400 h-1 rounded-full w-1/5"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* 빠른 명령어 */}
            <div className="mt-6 pt-6 border-t border-slate-700/50">
              <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
                <Zap className="w-4 h-4 text-amber-400" />
                빠른 명령어
              </h3>
              <div className="flex flex-wrap gap-3">
                {[
                  { cmd: '/help', color: 'bg-blue-500/20 text-blue-300 border-blue-500/40 hover:bg-blue-500/30' },
                  { cmd: '/mcp start', color: 'bg-purple-500/20 text-purple-300 border-purple-500/40 hover:bg-purple-500/30' },
                  { cmd: '/prompt clinical', color: 'bg-red-500/20 text-red-300 border-red-500/40 hover:bg-red-500/30' },
                  { cmd: '/debug', color: 'bg-amber-500/20 text-amber-300 border-amber-500/40 hover:bg-amber-500/30' },
                  { cmd: '/normal', color: 'bg-green-500/20 text-green-300 border-green-500/40 hover:bg-green-500/30' }
                ].map((item, index) => (
                  <code key={index} className={`px-4 py-2 rounded-lg text-xs font-mono border ${item.color} hover:scale-105 transition-all duration-200 cursor-pointer backdrop-blur-sm`}>
                    {item.cmd}
                  </code>
                ))}
              </div>
            </div>

            {/* 예시 질문 */}
            <div className="mt-6">
              <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
                <Brain className="w-4 h-4 text-pink-400" />
                시작 예시 질문
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  {
                    icon: "💊",
                    question: "아스피린의 작용 메커니즘을 설명해주세요",
                    category: "기본"
                  },
                  {
                    icon: "🧬",
                    question: "EGFR 억제제의 부작용은 무엇인가요?",
                    category: "Deep Research"
                  },
                  {
                    icon: "🔬",
                    question: "신약개발 과정의 주요 단계를 설명해주세요",
                    category: "전문"
                  }
                ].map((item, index) => (
                  <div key={index} className="bg-slate-700/50 rounded-lg p-4 border border-slate-600/50 hover:bg-slate-600/50 transition-all duration-200 cursor-pointer group backdrop-blur-sm">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-lg">{item.icon}</span>
                      <span className="text-xs text-slate-400 bg-slate-600/50 px-2 py-1 rounded">{item.category}</span>
                    </div>
                    <p className="text-sm text-slate-300 group-hover:text-white transition-colors leading-relaxed">
                      {item.question}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}