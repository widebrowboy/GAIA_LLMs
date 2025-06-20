'use client';

import { useState, useEffect } from 'react';
import { 
  Settings, 
  Brain, 

  Monitor, 
  Cpu, 
  Database, 
  Zap,
  ChevronRight,
  RefreshCw,
  Server,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { cn, getModelDisplayName, getModeDisplayName, getPromptDisplayName } from '@/lib/utils';
import { ChatSettings, GaiaBTSystemInfo, MCPServer } from '@/lib/types';

interface SidebarProps {
  settings: ChatSettings;
  onSettingsChange: (settings: ChatSettings) => void;
  className?: string;
}

export function Sidebar({ settings, onSettingsChange, className }: SidebarProps) {
  const [systemInfo, setSystemInfo] = useState<GaiaBTSystemInfo | null>(null);
  const [mcpServers, setMcpServers] = useState<MCPServer[]>([]);
  const [loading, setLoading] = useState(true);
  const [collapsed, setCollapsed] = useState(false);

  // 시스템 정보 로드
  const loadSystemInfo = async () => {
    try {
      const response = await fetch('/api/system/info');
      if (response.ok) {
        const data = await response.json();
        setSystemInfo(data);
      }
    } catch (error) {
      console.error('Failed to load system info:', error);
    }
  };

  // MCP 서버 상태 로드
  const loadMCPStatus = async () => {
    try {
      const response = await fetch('/api/mcp/status');
      if (response.ok) {
        const data = await response.json();
        setMcpServers(data.servers || []);
      }
    } catch (error) {
      console.error('Failed to load MCP status:', error);
    }
  };

  const refreshAll = async () => {
    setLoading(true);
    await Promise.all([loadSystemInfo(), loadMCPStatus()]);
    setLoading(false);
  };

  useEffect(() => {
    refreshAll();
    
    // 30초마다 자동 새로고침
    const interval = setInterval(refreshAll, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: MCPServer['status']) => {
    switch (status) {
      case 'running':
        return <CheckCircle className="h-3 w-3 text-green-500" />;
      case 'stopped':
        return <XCircle className="h-3 w-3 text-red-500" />;
      case 'error':
        return <AlertCircle className="h-3 w-3 text-yellow-500" />;
      default:
        return <Server className="h-3 w-3 text-gray-400" />;
    }
  };

  return (
    <div className={cn(
      'flex flex-col h-full bg-white border-r border-gray-200 transition-all duration-300',
      collapsed ? 'w-16' : 'w-80',
      className
    )}>
      {/* 헤더 */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {!collapsed && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="font-semibold text-sm text-gray-900">GAIA-BT</h2>
              <p className="text-xs text-gray-500">Drug Discovery AI</p>
            </div>
          </div>
        )}
        
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setCollapsed(!collapsed)}
          className="p-1"
        >
          <ChevronRight className={cn(
            'h-4 w-4 transition-transform',
            collapsed ? 'rotate-0' : 'rotate-180'
          )} />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* 시스템 상태 */}
        <div>
          <div className="flex items-center justify-between mb-3">
            {!collapsed && (
              <h3 className="font-medium text-sm text-gray-900 flex items-center">
                <Monitor className="h-4 w-4 mr-2 text-blue-600" />
                시스템 상태
              </h3>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={refreshAll}
              disabled={loading}
              className="p-1"
            >
              <RefreshCw className={cn('h-3 w-3', loading && 'animate-spin')} />
            </Button>
          </div>

          {!collapsed && systemInfo && (
            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                <span className="text-gray-600">버전</span>
                <span className="font-medium">{systemInfo.version}</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                <span className="text-gray-600">현재 모델</span>
                <span className="font-medium text-blue-600">
                  {getModelDisplayName(systemInfo.model)}
                </span>
              </div>
              <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                <span className="text-gray-600">MCP 상태</span>
                <span className={cn(
                  'px-2 py-0.5 rounded-full text-xs font-medium',
                  systemInfo.mcp_enabled
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-700'
                )}>
                  {systemInfo.mcp_enabled ? '활성' : '비활성'}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* AI 모델 설정 */}
        <div>
          {!collapsed && (
            <h3 className="font-medium text-sm text-gray-900 mb-3 flex items-center">
              <Brain className="h-4 w-4 mr-2 text-purple-600" />
              AI 모델 설정
            </h3>
          )}

          <div className="space-y-2">
            {/* 모델 선택 */}
            {!collapsed && systemInfo?.available_models && (
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  모델
                </label>
                <select
                  value={settings.model.model}
                  onChange={(e) => onSettingsChange({
                    ...settings,
                    model: { ...settings.model, model: e.target.value }
                  })}
                  className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  {systemInfo.available_models.map((model) => (
                    <option key={model} value={model}>
                      {getModelDisplayName(model)}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* 모드 선택 */}
            {!collapsed && (
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  작동 모드
                </label>
                <div className="grid grid-cols-2 gap-1">
                  <button
                    onClick={() => onSettingsChange({
                      ...settings,
                      mode: 'normal',
                      enableMCP: false
                    })}
                    className={cn(
                      'p-2 text-xs rounded border transition-colors',
                      settings.mode === 'normal'
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300 text-gray-600'
                    )}
                  >
                    <Zap className="h-3 w-3 mx-auto mb-1" />
                    일반
                  </button>
                  <button
                    onClick={() => onSettingsChange({
                      ...settings,
                      mode: 'deep_research',
                      enableMCP: true
                    })}
                    className={cn(
                      'p-2 text-xs rounded border transition-colors',
                      settings.mode === 'deep_research'
                        ? 'border-purple-500 bg-purple-50 text-purple-700'
                        : 'border-gray-200 hover:border-gray-300 text-gray-600'
                    )}
                  >
                    <Brain className="h-3 w-3 mx-auto mb-1" />
                    딥 리서치
                  </button>
                </div>
              </div>
            )}

            {/* 프롬프트 타입 */}
            {!collapsed && systemInfo?.available_prompts && (
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  전문 분야
                </label>
                <select
                  value={settings.promptType}
                  onChange={(e) => onSettingsChange({
                    ...settings,
                    promptType: e.target.value
                  })}
                  className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  {systemInfo.available_prompts.map((promptType) => (
                    <option key={promptType} value={promptType}>
                      {getPromptDisplayName(promptType)}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* 온도 조절 */}
            {!collapsed && (
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  창의성 (Temperature): {settings.model.temperature}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.model.temperature}
                  onChange={(e) => onSettingsChange({
                    ...settings,
                    model: { ...settings.model, temperature: parseFloat(e.target.value) }
                  })}
                  className="w-full"
                />
              </div>
            )}
          </div>
        </div>

        {/* MCP 서버 상태 */}
        {settings.mode === 'deep_research' && (
          <div>
            {!collapsed && (
              <h3 className="font-medium text-sm text-gray-900 mb-3 flex items-center">
                <Database className="h-4 w-4 mr-2 text-green-600" />
                MCP 서버
              </h3>
            )}

            <div className="space-y-1">
              {mcpServers.length === 0 ? (
                !collapsed && (
                  <p className="text-xs text-gray-500 text-center py-2">
                    MCP 서버 없음
                  </p>
                )
              ) : (
                mcpServers.map((server, index) => (
                  <div
                    key={index}
                    className="flex items-center space-x-2 p-2 rounded hover:bg-gray-50"
                  >
                    {getStatusIcon(server.status)}
                    {!collapsed && (
                      <div className="flex-1 min-w-0">
                        <div className="text-xs font-medium text-gray-900 truncate">
                          {server.name}
                        </div>
                        {server.tools && (
                          <div className="text-xs text-gray-500">
                            {server.tools.length}개 도구
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* 현재 설정 요약 */}
        {!collapsed && (
          <div className="pt-4 border-t border-gray-200">
            <h3 className="font-medium text-sm text-gray-900 mb-3 flex items-center">
              <Settings className="h-4 w-4 mr-2 text-gray-600" />
              현재 설정
            </h3>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-600">모드</span>
                <span className={cn(
                  'px-2 py-0.5 rounded-full font-medium',
                  settings.mode === 'deep_research'
                    ? 'bg-purple-100 text-purple-700'
                    : 'bg-blue-100 text-blue-700'
                )}>
                  {getModeDisplayName(settings.mode)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">분야</span>
                <span className="font-medium">
                  {getPromptDisplayName(settings.promptType)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">창의성</span>
                <span className="font-medium">{settings.model.temperature}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}