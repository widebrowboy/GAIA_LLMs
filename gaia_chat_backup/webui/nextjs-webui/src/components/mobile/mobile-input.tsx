'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TouchButton } from '@/components/ui/touch-button';
import { useMobile } from '@/hooks/use-mobile';
import { useLongPress } from '@/hooks/use-touch-gestures';
import { 
  Send, 
  Mic, 
  MicOff,
  Paperclip, 
  Smile,
  X,
  Plus,
  Camera,
  Image as ImageIcon,
  FileText
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface MobileInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  placeholder?: string;
  disabled?: boolean;
  maxLength?: number;
  autoFocus?: boolean;
}

export default function MobileInput({
  value,
  onChange,
  onSend,
  placeholder = "메시지를 입력하세요...",
  disabled = false,
  maxLength = 2000,
  autoFocus = false
}: MobileInputProps) {
  const isMobile = useMobile();
  const [isExpanded, setIsExpanded] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [showAttachments, setShowAttachments] = useState(false);
  const [keyboardHeight, setKeyboardHeight] = useState(0);
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // 음성 녹음 길게 누르기
  const voiceRecordProps = useLongPress(() => {
    if (!disabled && 'mediaDevices' in navigator) {
      setIsRecording(true);
      startVoiceRecording();
    }
  }, 200);

  // 키보드 높이 감지 (iOS Safari)
  useEffect(() => {
    if (!isMobile) return;

    const handleResize = () => {
      if (window.visualViewport) {
        const heightDiff = window.innerHeight - window.visualViewport.height;
        setKeyboardHeight(heightDiff);
      }
    };

    const handleViewportChange = () => {
      if (window.visualViewport) {
        setKeyboardHeight(window.innerHeight - window.visualViewport.height);
      }
    };

    window.addEventListener('resize', handleResize);
    window.visualViewport?.addEventListener('resize', handleViewportChange);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.visualViewport?.removeEventListener('resize', handleViewportChange);
    };
  }, [isMobile]);

  // 텍스트 영역 자동 높이 조정
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      const maxHeight = isMobile ? 120 : 160; // 모바일에서 더 작은 최대 높이
      textareaRef.current.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
      
      setIsExpanded(scrollHeight > 44); // 기본 한 줄 높이
    }
  }, [value, isMobile]);

  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // 실제 녹음 로직 구현 (Web Speech API 또는 MediaRecorder 사용)
      console.log('음성 녹음 시작');
      
      // 햅틱 피드백
      if ('vibrate' in navigator) {
        navigator.vibrate([50, 50, 50]);
      }
    } catch (error) {
      console.error('마이크 접근 권한이 필요합니다:', error);
      setIsRecording(false);
    }
  };

  const stopVoiceRecording = () => {
    setIsRecording(false);
    // 녹음 중지 로직
    console.log('음성 녹음 중지');
  };

  const handleSend = () => {
    if (value.trim() && !disabled) {
      onSend();
      // 전송 후 높이 초기화
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
        setIsExpanded(false);
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isMobile) {
      e.preventDefault();
      handleSend();
    }
  };

  const attachmentOptions = [
    { id: 'camera', label: '카메라', icon: Camera, color: 'bg-green-500' },
    { id: 'gallery', label: '갤러리', icon: ImageIcon, color: 'bg-blue-500' },
    { id: 'document', label: '문서', icon: FileText, color: 'bg-purple-500' },
  ];

  if (!isMobile) {
    // 데스크톱에서는 기본 입력 컴포넌트 사용
    return null;
  }

  return (
    <motion.div
      ref={containerRef}
      className="relative"
      style={{
        paddingBottom: keyboardHeight > 0 ? `${keyboardHeight}px` : '0px'
      }}
      layout
    >
      {/* 첨부파일 옵션 */}
      <AnimatePresence>
        {showAttachments && (
          <motion.div
            className="absolute bottom-full left-0 right-0 p-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          >
            <div className="bg-gray-800 rounded-2xl p-4 shadow-xl">
              <div className="flex justify-around">
                {attachmentOptions.map((option) => {
                  const Icon = option.icon;
                  return (
                    <TouchButton
                      key={option.id}
                      variant="ghost"
                      className="flex flex-col items-center space-y-2 p-3"
                      onClick={() => {
                        // 첨부파일 처리 로직
                        console.log(`${option.label} 선택됨`);
                        setShowAttachments(false);
                      }}
                    >
                      <div className={cn("w-12 h-12 rounded-full flex items-center justify-center", option.color)}>
                        <Icon className="h-6 w-6 text-white" />
                      </div>
                      <span className="text-xs text-gray-300">{option.label}</span>
                    </TouchButton>
                  );
                })}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 메인 입력 영역 */}
      <motion.div 
        className={cn(
          "flex items-end space-x-3 p-4 bg-gray-900 border-t border-gray-700",
          isExpanded && "pb-6"
        )}
        layout
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
      >
        {/* 첨부파일 버튼 */}
        <TouchButton
          variant="ghost"
          size="sm"
          className="flex-shrink-0 text-gray-400 hover:text-white"
          onClick={() => setShowAttachments(!showAttachments)}
          disabled={disabled}
        >
          {showAttachments ? <X className="h-5 w-5" /> : <Paperclip className="h-5 w-5" />}
        </TouchButton>

        {/* 텍스트 입력 영역 */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            maxLength={maxLength}
            disabled={disabled}
            autoFocus={autoFocus}
            className={cn(
              "w-full bg-gray-800 border border-gray-600 rounded-2xl",
              "px-4 py-3 pr-12 text-white placeholder-gray-400",
              "resize-none overflow-hidden",
              "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
              "min-h-[44px] max-h-[120px]", // 모바일 최적화 높이
              disabled && "opacity-50 cursor-not-allowed"
            )}
            rows={1}
            style={{
              fontSize: '16px', // iOS에서 줌 방지
              lineHeight: '1.5'
            }}
          />

          {/* 글자 수 카운터 */}
          {value.length > maxLength * 0.8 && (
            <motion.div
              className="absolute bottom-1 right-3 text-xs text-gray-400"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {value.length}/{maxLength}
            </motion.div>
          )}
        </div>

        {/* 음성/전송 버튼 */}
        <div className="flex-shrink-0">
          {value.trim() ? (
            <TouchButton
              className="w-11 h-11 rounded-full bg-blue-600 hover:bg-blue-700 text-white"
              onClick={handleSend}
              disabled={disabled}
              hapticFeedback={true}
            >
              <Send className="h-5 w-5" />
            </TouchButton>
          ) : (
            <TouchButton
              className={cn(
                "w-11 h-11 rounded-full text-white transition-colors",
                isRecording 
                  ? "bg-red-600 hover:bg-red-700" 
                  : "bg-gray-600 hover:bg-gray-500"
              )}
              disabled={disabled}
              hapticFeedback={true}
              onLongPress={() => {
                if (!disabled) {
                  setIsRecording(true);
                  startVoiceRecording();
                }
              }}
              {...voiceRecordProps}
              onTouchEnd={(e) => {
                voiceRecordProps.onTouchEnd(e);
                if (isRecording) {
                  stopVoiceRecording();
                }
              }}
            >
              {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
            </TouchButton>
          )}
        </div>
      </motion.div>

      {/* 음성 녹음 UI */}
      <AnimatePresence>
        {isRecording && (
          <motion.div
            className="absolute inset-0 bg-red-600/20 backdrop-blur-sm rounded-2xl"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="flex items-center justify-center h-full">
              <motion.div
                className="flex items-center space-x-2 text-white"
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
              >
                <div className="w-2 h-2 bg-red-500 rounded-full" />
                <span className="text-sm font-medium">음성 메시지 녹음 중...</span>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* iOS Safe Area 처리 */}
      <div className="h-safe-bottom bg-gray-900" />
    </motion.div>
  );
}