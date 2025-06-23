'use client';

import { Plus, MessageSquare, Settings, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { useChatStore } from '@/store/chatStore';

export function Sidebar() {
  const { 
    sessions, 
    currentSessionId, 
    createSession, 
    setCurrentSession, 
    deleteSession 
  } = useChatStore();

  const handleNewChat = async () => {
    try {
      await createSession({
        mode: 'normal',
        prompt_type: 'default'
      });
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const getModeLabel = (mode: string) => {
    switch (mode) {
      case 'normal': return '일반';
      case 'mcp': 
      case 'deep_research': return 'Deep';
      default: return mode;
    }
  };

  return (
    <div className="flex flex-col h-full bg-muted/50">
      {/* 헤더 */}
      <div className="p-4 border-b border-border">
        <Button 
          onClick={handleNewChat}
          className="w-full"
          size="lg"
        >
          <Plus className="w-4 h-4 mr-2" />
          새 채팅
        </Button>
      </div>

      {/* 채팅 목록 */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-2">
        {Object.values(sessions).length === 0 ? (
          <div className="text-center text-muted-foreground py-8">
            <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">채팅 기록이 없습니다</p>
          </div>
        ) : (
          Object.values(sessions)
            .sort((a, b) => b.last_activity - a.last_activity)
            .map((session) => (
              <Card
                key={session.id}
                className={`p-3 cursor-pointer transition-colors hover:bg-accent group ${
                  currentSessionId === session.id ? 'ring-2 ring-primary' : ''
                }`}
                onClick={() => setCurrentSession(session.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge 
                        variant={session.mode === 'normal' ? 'secondary' : 'default'}
                        className="text-xs"
                      >
                        {getModeLabel(session.mode)}
                      </Badge>
                    </div>
                    
                    <div className="text-sm font-medium text-foreground mb-1 truncate">
                      {session.messages.length > 0 
                        ? session.messages[0].content.slice(0, 30) + '...'
                        : '새 채팅'
                      }
                    </div>
                    
                    <div className="text-xs text-muted-foreground">
                      메시지 {session.messages.length}개
                    </div>
                  </div>
                  
                  <Button
                    variant="ghost"
                    size="icon"
                    className="opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteSession(session.id);
                    }}
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              </Card>
            ))
        )}
      </div>

      {/* 푸터 */}
      <div className="p-4 border-t border-border">
        <Button variant="ghost" size="sm" className="w-full justify-start">
          <Settings className="w-4 h-4 mr-2" />
          설정
        </Button>
      </div>
    </div>
  );
}