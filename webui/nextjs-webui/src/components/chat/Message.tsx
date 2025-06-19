'use client';

import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { ReactMarkdown } from 'react-markdown/lib/react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { User, Bot, Search, Beaker } from 'lucide-react';
import { format } from 'date-fns';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  searchResults?: any;
  enhanced?: boolean;
}

interface MessageProps {
  message: ChatMessage;
}

export function Message({ message }: MessageProps) {
  const isUser = message.role === 'user';
  const isEnhanced = message.enhanced || false;

  return (
    <div className={cn(
      'flex gap-3 max-w-4xl',
      isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'
    )}>
      {/* 아바타 */}
      <div className={cn(
        'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
        isUser 
          ? 'bg-research-500 text-white' 
          : isEnhanced 
            ? 'bg-clinical-500 text-white'
            : 'bg-biotech-500 text-white'
      )}>
        {isUser ? (
          <User className="w-4 h-4" />
        ) : isEnhanced ? (
          <Search className="w-4 h-4" />
        ) : (
          <Bot className="w-4 h-4" />
        )}
      </div>

      {/* 메시지 내용 */}
      <div className={cn('flex-1', isUser ? 'text-right' : 'text-left')}>
        <Card className={cn(
          'p-4 shadow-sm',
          isUser 
            ? 'message-user' 
            : isEnhanced 
              ? 'message-enhanced'
              : 'message-assistant'
        )}>
          {/* Enhanced 모드 표시 */}
          {isEnhanced && !isUser && (
            <div className="flex items-center gap-2 mb-3 pb-2 border-b border-clinical-200 dark:border-clinical-800">
              <Badge variant="default" className="bg-clinical-500">
                <Beaker className="w-3 h-3 mr-1" />
                Deep Research
              </Badge>
              <span className="text-xs text-muted-foreground">
                다중 데이터베이스 검색 결과 포함
              </span>
            </div>
          )}

          {/* 메시지 내용 */}
          <div className={cn(
            'prose prose-sm max-w-none',
            'dark:prose-invert',
            'prose-headings:text-foreground',
            'prose-p:text-foreground prose-p:leading-relaxed',
            'prose-strong:text-foreground',
            'prose-code:text-primary prose-code:bg-muted prose-code:px-1 prose-code:py-0.5 prose-code:rounded',
            'prose-pre:bg-muted prose-pre:border',
            isUser && 'text-right'
          )}>
            <ReactMarkdown
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={oneDark}
                      language={match[1]}
                      PreTag="div"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>

          {/* 검색 결과 요약 (Enhanced 모드) */}
          {message.searchResults && !isUser && (
            <div className="mt-4 pt-3 border-t border-clinical-200 dark:border-clinical-800">
              <div className="text-xs text-muted-foreground space-y-1">
                <div className="font-medium">검색 데이터 소스:</div>
                <div className="flex flex-wrap gap-1">
                  {message.searchResults.pubmed && (
                    <Badge variant="outline" className="text-xs">
                      PubMed ({message.searchResults.pubmed.length})
                    </Badge>
                  )}
                  {message.searchResults.chembl && (
                    <Badge variant="outline" className="text-xs">
                      ChEMBL ({message.searchResults.chembl.length})
                    </Badge>
                  )}
                  {message.searchResults.clinical_trials && (
                    <Badge variant="outline" className="text-xs">
                      임상시험 ({message.searchResults.clinical_trials.length})
                    </Badge>
                  )}
                </div>
              </div>
            </div>
          )}
        </Card>

        {/* 타임스탬프 */}
        <div className={cn(
          'text-xs text-muted-foreground mt-1 px-1',
          isUser ? 'text-right' : 'text-left'
        )}>
          {format(new Date(message.timestamp), 'HH:mm')}
        </div>
      </div>
    </div>
  );
}