'use client';

import { useState } from 'react';
// Message component removed - using MessageArea instead
import { MessageGroup as MessageGroupType, formatTimestamp } from '@/utils/message-utils';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Message as MessageType } from '@/lib/types';
import { 
  Clock, 
  ChevronDown, 
  ChevronUp,
  Users,
  Bot,
  User
} from 'lucide-react';

interface MessageGroupProps {
  group: MessageGroupType;
  onResend?: (message: MessageType) => void;
  onDelete?: (messageId: string) => void;
  onEdit?: (messageId: string, content: string) => void;
  layoutConfig?: {
    mode: 'compact' | 'normal' | 'spacious';
    density: 'compact' | 'normal' | 'comfortable';
    fontSize: 'small' | 'medium' | 'large';
  };
}

export default function MessageGroupComponent({
  group,
  onResend,
  onDelete,
  onEdit,
  layoutConfig = { mode: 'normal', density: 'normal', fontSize: 'medium' }
}: MessageGroupProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  
  const isUser = group.sender === 'user';
  const isSystem = group.sender === 'system';
  const hasMultipleMessages = group.messages.length > 1;
  
  // Get layout classes based on config
  const getLayoutClasses = () => {
    const { mode, density } = layoutConfig;
    
    const spacing = {
      compact: 'mb-2',
      normal: 'mb-4',
      comfortable: 'mb-6'
    };
    
    const groupSpacing = {
      compact: 'space-y-1',
      normal: 'space-y-2',
      comfortable: 'space-y-3'
    };
    
    return {
      groupMargin: spacing[density],
      messageSpacing: groupSpacing[density]
    };
  };

  const classes = getLayoutClasses();

  return (
    <div className={`message-group ${classes.groupMargin}`}>
      {/* Group Timestamp */}
      {group.showTimestamp && (
        <div className="flex items-center justify-center mb-3">
          <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-3 py-1 rounded-full">
            <Clock className="w-3 h-3" />
            <span>{formatTimestamp(group.startTime)}</span>
          </div>
        </div>
      )}

      {/* Group Header (for multiple messages) */}
      {hasMultipleMessages && (
        <div className={`flex items-center ${isUser ? 'justify-end' : 'justify-start'} mb-2`}>
          <Card className="px-3 py-1 bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700">
            <Button
              onClick={() => setIsCollapsed(!isCollapsed)}
              variant="ghost"
              size="sm"
              className="h-6 p-1 text-xs"
            >
              <div className="flex items-center space-x-2">
                <div className="flex items-center space-x-1">
                  {isUser ? (
                    <User className="w-3 h-3" />
                  ) : isSystem ? (
                    <Users className="w-3 h-3" />
                  ) : (
                    <Bot className="w-3 h-3" />
                  )}
                  <span>
                    {isUser ? '사용자' : isSystem ? '시스템' : 'GAIA-BT'}
                  </span>
                </div>
                <Badge variant="outline" className="text-xs px-1">
                  {group.messages.length}개
                </Badge>
                {isCollapsed ? (
                  <ChevronDown className="w-3 h-3" />
                ) : (
                  <ChevronUp className="w-3 h-3" />
                )}
              </div>
            </Button>
          </Card>
        </div>
      )}

      {/* Messages */}
      <div className={`${classes.messageSpacing} ${isCollapsed ? 'hidden' : ''}`}>
        {group.messages.map((message, index) => {
          // Convert to the expected MessageType format
          const messageProps: MessageType = {
            id: message.id,
            role: message.role,
            content: message.content,
            createdAt: message.timestamp,
            metadata: {
              model: message.model,
              sources: message.sources,
              status: message.status
            }
          };

          return (
            <div key={message.id} className="message-item">
              <Message 
                message={messageProps}
                isLoading={message.status === 'sending'}
              />
              
              {/* Additional actions for enhanced UX */}
              <div className="flex items-center justify-end space-x-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                {message.role === 'user' && onEdit && (
                  <Button
                    onClick={() => onEdit(message.id, message.content)}
                    size="sm"
                    variant="ghost"
                    className="h-6 px-2 text-xs"
                  >
                    편집
                  </Button>
                )}
                
                {message.role === 'user' && onResend && (
                  <Button
                    onClick={() => onResend(messageProps)}
                    size="sm"
                    variant="ghost"
                    className="h-6 px-2 text-xs"
                  >
                    재전송
                  </Button>
                )}
                
                {onDelete && (
                  <Button
                    onClick={() => onDelete(message.id)}
                    size="sm"
                    variant="ghost"
                    className="h-6 px-2 text-xs text-red-500 hover:text-red-700"
                  >
                    삭제
                  </Button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Collapsed Preview */}
      {isCollapsed && hasMultipleMessages && (
        <div className={`${isUser ? 'text-right' : 'text-left'} px-4`}>
          <Card className="p-3 bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {group.messages.length}개의 메시지 ({formatTimestamp(group.startTime)} - {formatTimestamp(group.endTime)})
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-500 mt-1 truncate">
              {group.messages[0].content.substring(0, 100)}
              {group.messages[0].content.length > 100 && '...'}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}