'use client';

import { useState, useRef } from 'react';
import { Button } from '@/components/ui/Button';
import { Textarea } from '@/components/ui/Textarea';
import { Send, Loader2 } from 'lucide-react';

interface MessageInputProps {
  onSendMessage: (content: string) => void;
  disabled?: boolean;
  mode?: string;
  promptType?: string;
}

export function MessageInput({ 
  onSendMessage, 
  disabled = false,
  mode = 'normal',
  promptType = 'default'
}: MessageInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (!input.trim() || disabled) return;
    
    onSendMessage(input);
    setInput('');
    
    // 텍스트 영역 높이 리셋
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    
    // 자동 높이 조절
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
  };

  const getPlaceholder = () => {
    if (mode === 'mcp' || mode === 'deep_research') {
      return '신약개발 관련 질문을 입력하세요... (Deep Research 모드 활성화됨)';
    }
    
    switch (promptType) {
      case 'clinical':
        return '임상시험 관련 질문을 입력하세요...';
      case 'research':
        return '연구 분석 관련 질문을 입력하세요...';
      case 'chemistry':
        return '의약화학 관련 질문을 입력하세요...';
      case 'regulatory':
        return '규제 관련 질문을 입력하세요...';
      default:
        return '신약개발 관련 질문을 입력하세요...';
    }
  };

  return (
    <div className="p-4">
      <div className="flex items-end space-x-2">
        <div className="flex-1">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={handleTextareaChange}
            onKeyPress={handleKeyPress}
            placeholder={getPlaceholder()}
            disabled={disabled}
            className="min-h-[60px] max-h-[120px] resize-none"
            rows={1}
          />
        </div>
        <Button
          onClick={handleSubmit}
          disabled={disabled || !input.trim()}
          size="icon"
          className="h-[60px] w-[60px] shrink-0"
        >
          {disabled ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </Button>
      </div>
      
      {/* 힌트 텍스트 */}
      <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
        <span>
          {mode === 'mcp' || mode === 'deep_research' 
            ? '🔬 Deep Research 모드: 다중 데이터베이스 검색 활성화'
            : '일반 모드: 기본 AI 응답'
          }
        </span>
        <span>Enter로 전송, Shift+Enter로 줄바꿈</span>
      </div>
    </div>
  );
}