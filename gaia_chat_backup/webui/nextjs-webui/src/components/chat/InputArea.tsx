'use client';

import { useRef, useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { TouchButton } from '@/components/ui/touch-button';
import MobileInput from '../mobile/mobile-input';
import { useMobile } from '@/hooks/use-mobile';
import { 
  Send, 
  Loader2,
  Command,
  HelpCircle,
  Paperclip,
  Smile,
  Mic,
  Square,
  ArrowUp,
  MoreHorizontal,
  FileText,
  Image as ImageIcon,
  Code,
  Zap
} from 'lucide-react';

interface InputAreaProps {
  input: string;
  setInput: (value: string) => void;
  onSendMessage: () => void;
  isProcessing: boolean;
  layoutConfig?: {
    mode: 'compact' | 'normal' | 'spacious';
    density: 'compact' | 'normal' | 'comfortable';
    fontSize: 'small' | 'medium' | 'large';
  };
}

export default function InputArea({ 
  input, 
  setInput, 
  onSendMessage, 
  isProcessing, 
  layoutConfig = { mode: 'normal', density: 'normal', fontSize: 'medium' }
}: InputAreaProps) {
  
  const isMobile = useMobile();
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [showFileAttach, setShowFileAttach] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [showMarkdownPreview, setShowMarkdownPreview] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(-1);

  // 자동 높이 조절
  const adjustTextareaHeight = () => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      const scrollHeight = inputRef.current.scrollHeight;
      const maxHeight = layoutConfig.mode === 'compact' ? 120 : 200;
      inputRef.current.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
    }
  };

  // 입력 포커스
  useEffect(() => {
    if (inputRef.current && !isProcessing) {
      inputRef.current.focus();
    }
  }, [isProcessing]);

  // 입력 변경 시 높이 조절
  useEffect(() => {
    adjustTextareaHeight();
  }, [input]);

  // 자동완성 명령어 검색
  useEffect(() => {
    if (input.startsWith('/')) {
      const commands = [
        '/help - 도움말 표시',
        '/mcp start - Deep Research 모드 시작',
        '/normal - 일반 모드로 전환',
        '/prompt clinical - 임상시험 전문 모드',
        '/prompt research - 연구분석 전문 모드',
        '/prompt chemistry - 의약화학 전문 모드',
        '/prompt regulatory - 규제전문 모드',
        '/model - AI 모델 변경',
        '/status - 시스템 상태 확인',
        '/debug - 디버그 모드 토글',
        '/mcpshow - MCP 출력 표시 토글'
      ];
      
      const query = input.slice(1).toLowerCase();
      const filtered = commands.filter(cmd => 
        cmd.toLowerCase().includes(query)
      );
      setSuggestions(filtered);
    } else {
      setSuggestions([]);
    }
    setActiveSuggestionIndex(-1);
  }, [input]);

  // 키보드 핸들링
  const handleKeyDown = (e: React.KeyboardEvent) => {
    // 자동완성 네비게이션
    if (suggestions.length > 0) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setActiveSuggestionIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        return;
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        setActiveSuggestionIndex(prev => prev > 0 ? prev - 1 : prev);
        return;
      }
      if (e.key === 'Tab' || e.key === 'Enter') {
        if (activeSuggestionIndex >= 0) {
          e.preventDefault();
          const suggestion = suggestions[activeSuggestionIndex];
          const command = suggestion.split(' - ')[0];
          setInput(command + ' ');
          setSuggestions([]);
          setActiveSuggestionIndex(-1);
          return;
        }
      }
      if (e.key === 'Escape') {
        setSuggestions([]);
        setActiveSuggestionIndex(-1);
        return;
      }
    }

    // 메시지 전송
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isProcessing && input.trim()) {
        onSendMessage();
      }
    }

    // Ctrl+Enter로 줄바꿈
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      setInput(prev => prev + '\n');
    }
  };

  // 자동완성 선택
  const handleSuggestionClick = (suggestion: string) => {
    const command = suggestion.split(' - ')[0];
    setInput(command + ' ');
    setSuggestions([]);
    setActiveSuggestionIndex(-1);
    inputRef.current?.focus();
  };

  // 파일 첨부 핸들링
  const handleFileAttach = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      // 파일 첨부 로직 (향후 구현)
      console.log('Files selected:', files);
    }
  };

  // 음성 입력 토글
  const toggleVoiceInput = () => {
    if (isRecording) {
      setIsRecording(false);
      // 음성 녹음 중지 로직
    } else {
      setIsRecording(true);
      // 음성 녹음 시작 로직
    }
  };

  // 글자 수 계산
  const characterCount = input.length;
  const maxCharacters = 2000;
  const isOverLimit = characterCount > maxCharacters;

  // 텍스트 영역 자동 높이 조정
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    
    // 자동 높이 조정
    const textarea = e.target;
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 120); // 최대 높이 제한
    textarea.style.height = `${newHeight}px`;
  };

  // 카드 크기에 따른 스타일 조정
  const getInputAreaClasses = () => {
    switch (layoutConfig.mode) {
      case 'spacious':
        return 'p-6 m-6';
      case 'compact':
        return 'p-4 m-4';
      default:
        return 'p-5 m-5';
    }
  };

  const getTextAreaClasses = () => {
    switch (layoutConfig.fontSize) {
      case 'large':
        return 'text-base';
      case 'small':
        return 'text-xs';
      default:
        return 'text-sm';
    }
  };

  const inputAreaClasses = getInputAreaClasses();
  const textAreaClasses = getTextAreaClasses();

  // 빠른 명령어 버튼들
  const quickCommands = [
    { cmd: '/help', desc: '도움말', icon: HelpCircle },
    { cmd: '/mcp start', desc: 'Deep Research', icon: Command },
    { cmd: '/normal', desc: '일반 모드', icon: Command },
    { cmd: '/status', desc: '상태 확인', icon: Command }
  ];

  const handleQuickCommand = (command: string) => {
    setInput(command);
    // 자동으로 전송하지 않고 사용자가 확인 후 전송하도록 함
    setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.focus();
        inputRef.current.setSelectionRange(command.length, command.length);
      }
    }, 0);
  };

  // 모바일에서는 전용 모바일 입력 컴포넌트 사용
  if (isMobile) {
    return (
      <MobileInput
        value={input}
        onChange={setInput}
        onSend={onSendMessage}
        disabled={isProcessing}
        placeholder="메시지를 입력하세요..."
        maxLength={2000}
        autoFocus={false}
      />
    );
  }

  // 데스크톱 레이아웃
  return (
    <div className="flex-shrink-0 relative">
      {/* 자동완성 팝업 */}
      {suggestions.length > 0 && (
        <div className="absolute bottom-full left-0 right-0 mb-2 z-50">
          <Card className="border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 shadow-lg max-h-48 overflow-y-auto">
            {suggestions.map((suggestion, index) => (
              <div
                key={index}
                className={`px-3 py-2 cursor-pointer transition-colors ${
                  index === activeSuggestionIndex
                    ? 'bg-blue-100 dark:bg-blue-900'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
                onClick={() => handleSuggestionClick(suggestion)}
              >
                <div className="flex items-center space-x-2">
                  <Code className="w-3 h-3 text-blue-500" />
                  <span className="text-sm font-mono">{suggestion.split(' - ')[0]}</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {suggestion.split(' - ')[1]}
                  </span>
                </div>
              </div>
            ))}
          </Card>
        </div>
      )}

      <Card className={`${inputAreaClasses} bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-lg`}>
        
        {/* 빠른 명령어 버튼들 */}
        <div className="flex flex-wrap gap-2 mb-4">
          {quickCommands.map((cmd) => (
            <Button
              key={cmd.cmd}
              onClick={() => handleQuickCommand(cmd.cmd)}
              variant="outline"
              size="sm"
              className="text-xs"
              disabled={isProcessing}
            >
              <cmd.icon className="h-3 w-3 mr-1" />
              {cmd.desc}
            </Button>
          ))}
        </div>

        {/* 메인 입력 영역 */}
        <div className="space-y-3">
          
          {/* 상단 도구 모음 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {/* 파일 첨부 */}
              <div className="relative">
                <input
                  type="file"
                  id="file-upload"
                  className="hidden"
                  onChange={handleFileAttach}
                  multiple
                  accept=".txt,.doc,.docx,.pdf,.png,.jpg,.jpeg"
                />
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                  onClick={() => document.getElementById('file-upload')?.click()}
                  disabled={isProcessing}
                  title="파일 첨부"
                >
                  <Paperclip className="h-4 w-4" />
                </Button>
              </div>

              {/* 이모지 피커 */}
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                disabled={isProcessing}
                title="이모지"
              >
                <Smile className="h-4 w-4" />
              </Button>

              {/* 음성 입력 */}
              <Button
                variant="ghost"
                size="sm"
                className={`h-8 w-8 p-0 ${isRecording ? 'text-red-500' : ''}`}
                onClick={toggleVoiceInput}
                disabled={isProcessing}
                title={isRecording ? '음성 입력 중지' : '음성 입력 시작'}
              >
                {isRecording ? <Square className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
              </Button>
            </div>

            <div className="flex items-center space-x-2">
              {/* 마크다운 미리보기 */}
              <Button
                variant="ghost"
                size="sm"
                className="h-8 px-2 text-xs"
                onClick={() => setShowMarkdownPreview(!showMarkdownPreview)}
                disabled={isProcessing}
              >
                <FileText className="h-3 w-3 mr-1" />
                {showMarkdownPreview ? '편집' : '미리보기'}
              </Button>
            </div>
          </div>
          
          {/* 텍스트 입력 영역 */}
          <div className="relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder={
                isProcessing 
                  ? "AI가 응답하는 중입니다..." 
                  : "메시지를 입력하세요... (Enter: 전송, Shift+Enter: 줄바꿈)"
              }
              className={`
                w-full ${textAreaClasses} 
                bg-gray-50 dark:bg-gray-900 
                border border-gray-200 dark:border-gray-600 
                rounded-lg px-4 py-3 
                text-gray-900 dark:text-white 
                placeholder-gray-500 dark:placeholder-gray-400 
                resize-none 
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                transition-all duration-200
                ${isOverLimit ? 'border-red-500 focus:ring-red-500' : ''}
              `}
              style={{ 
                minHeight: layoutConfig.mode === 'compact' ? '48px' : '60px',
                maxHeight: layoutConfig.mode === 'compact' ? '120px' : '200px'
              }}
              disabled={isProcessing}
            />
            
            {/* 전송 버튼 (텍스트 영역 내부) */}
            <div className="absolute bottom-2 right-2">
              <Button
                onClick={onSendMessage}
                size="sm"
                className="h-8 w-8 p-0 rounded-full"
                disabled={isProcessing || !input.trim() || isOverLimit}
                variant={input.trim() && !isOverLimit ? "default" : "ghost"}
              >
                {isProcessing ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <ArrowUp className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
          
          {/* 하단 정보 및 힌트 */}
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center space-x-4 text-gray-500 dark:text-gray-400">
              <span>💡 /help로 명령어 확인</span>
              {input.startsWith('/') && (
                <Badge variant="outline" className="text-xs px-2 py-0">
                  명령어 모드
                </Badge>
              )}
              {isRecording && (
                <Badge variant="destructive" className="text-xs px-2 py-0 animate-pulse">
                  🎤 녹음 중
                </Badge>
              )}
            </div>
            
            <div className={`text-right ${isOverLimit ? 'text-red-500' : 'text-gray-500 dark:text-gray-400'}`}>
              <span>{characterCount}/{maxCharacters}</span>
              {characterCount > 1800 && (
                <span className="ml-2 text-yellow-500">⚠️</span>
              )}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}