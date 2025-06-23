'use client';

import { Bot } from 'lucide-react';
import { Card } from '@/components/ui/Card';

export function TypingIndicator() {
  return (
    <div className="flex gap-3 max-w-4xl mr-auto animate-fade-in">
      {/* 아바타 */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-biotech-500 text-white">
        <Bot className="w-4 h-4" />
      </div>

      {/* 타이핑 인디케이터 */}
      <div className="flex-1">
        <Card className="message-assistant p-4 shadow-sm">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-muted-foreground">AI가 답변을 준비 중입니다</span>
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-biotech-500 rounded-full typing-indicator"></div>
              <div className="w-2 h-2 bg-biotech-500 rounded-full typing-indicator"></div>
              <div className="w-2 h-2 bg-biotech-500 rounded-full typing-indicator"></div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}