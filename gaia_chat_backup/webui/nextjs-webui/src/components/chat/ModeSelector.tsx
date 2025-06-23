'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Settings, ChevronDown } from 'lucide-react';
import { useChatStore } from '@/store/chatStore';

interface ModeSelectorProps {
  sessionId: string;
}

export function ModeSelector({ sessionId }: ModeSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { sessions, setMode } = useChatStore();
  
  const currentSession = sessions[sessionId];
  if (!currentSession) return null;

  const modes = [
    { value: 'normal', label: '일반 모드', description: '기본 AI 응답' },
    { value: 'deep_research', label: 'Deep Research', description: 'MCP 통합 검색' },
  ];

  const handleModeChange = async (mode: string) => {
    await setMode(sessionId, mode);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2"
      >
        <Settings className="w-3 h-3" />
        {modes.find(m => m.value === currentSession.mode)?.label || '모드'}
        <ChevronDown className="w-3 h-3" />
      </Button>

      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 top-full mt-1 w-64 bg-background border border-border rounded-md shadow-lg z-20">
            {modes.map((mode) => (
              <button
                key={mode.value}
                className="w-full text-left p-3 hover:bg-muted transition-colors first:rounded-t-md last:rounded-b-md"
                onClick={() => handleModeChange(mode.value)}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium">{mode.label}</span>
                  {currentSession.mode === mode.value && (
                    <Badge variant="default" className="text-xs">현재</Badge>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">{mode.description}</p>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}