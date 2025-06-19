'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { FileText, ChevronDown } from 'lucide-react';
import { useChatStore } from '@/store/chatStore';

interface PromptSelectorProps {
  sessionId: string;
}

export function PromptSelector({ sessionId }: PromptSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { sessions, setPromptType } = useChatStore();
  
  const currentSession = sessions[sessionId];
  if (!currentSession) return null;

  const prompts = [
    { value: 'default', label: '기본', description: '일반적인 신약개발 질문' },
    { value: 'clinical', label: '임상시험', description: '임상시험 및 환자 중심' },
    { value: 'research', label: '연구분석', description: '문헌 분석 및 증거 종합' },
    { value: 'chemistry', label: '의약화학', description: '분자 설계 및 화학구조' },
    { value: 'regulatory', label: '규제', description: '의약품 규제 및 승인' },
  ];

  const handlePromptChange = async (promptType: string) => {
    await setPromptType(sessionId, promptType);
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
        <FileText className="w-3 h-3" />
        {prompts.find(p => p.value === currentSession.prompt_type)?.label || '프롬프트'}
        <ChevronDown className="w-3 h-3" />
      </Button>

      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 top-full mt-1 w-64 bg-background border border-border rounded-md shadow-lg z-20">
            {prompts.map((prompt) => (
              <button
                key={prompt.value}
                className="w-full text-left p-3 hover:bg-muted transition-colors first:rounded-t-md last:rounded-b-md"
                onClick={() => handlePromptChange(prompt.value)}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium">{prompt.label}</span>
                  {currentSession.prompt_type === prompt.value && (
                    <Badge variant="default" className="text-xs">현재</Badge>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">{prompt.description}</p>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}