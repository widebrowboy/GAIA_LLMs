'use client';

import { useChatStore } from '@/store/chatStore';
import { ModeSelector } from './ModeSelector';
import { PromptSelector } from './PromptSelector';
import { ThemeToggle } from '../ui/ThemeToggle';
import { Badge } from '../ui/Badge';

export function Header() {
  const { currentSessionId, sessions } = useChatStore();
  const currentSession = currentSessionId ? sessions[currentSessionId] : null;

  const getModeLabel = (mode: string) => {
    switch (mode) {
      case 'normal': return '일반 모드';
      case 'mcp': 
      case 'deep_research': return 'Deep Research 모드';
      default: return mode;
    }
  };

  const getPromptLabel = (promptType: string) => {
    switch (promptType) {
      case 'default': return '기본';
      case 'clinical': return '임상시험';
      case 'research': return '연구분석';
      case 'chemistry': return '의약화학';
      case 'regulatory': return '규제';
      default: return promptType;
    }
  };

  return (
    <div className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex items-center justify-between p-4">
        {/* 좌측: 로고 및 상태 */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-research-500 to-biotech-500 rounded-lg flex items-center justify-center">
              <span className="text-sm font-bold text-white">G</span>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-foreground">GAIA-BT</h1>
              <p className="text-xs text-muted-foreground">신약개발 AI 연구 어시스턴트</p>
            </div>
          </div>

          {/* 현재 세션 상태 */}
          {currentSession && (
            <div className="flex items-center space-x-2">
              <Badge variant={currentSession.mode === 'normal' ? 'secondary' : 'default'}>
                {getModeLabel(currentSession.mode)}
              </Badge>
              <Badge variant="outline">
                {getPromptLabel(currentSession.prompt_type)}
              </Badge>
            </div>
          )}
        </div>

        {/* 우측: 컨트롤 */}
        <div className="flex items-center space-x-2">
          {currentSessionId && (
            <>
              <ModeSelector sessionId={currentSessionId} />
              <PromptSelector sessionId={currentSessionId} />
            </>
          )}
          <ThemeToggle />
        </div>
      </div>
    </div>
  );
}