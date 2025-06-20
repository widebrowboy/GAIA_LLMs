'use client';

import { motion } from 'framer-motion';
import { loadingDotsVariants, typingVariants, progressVariants } from '@/utils/animations';

interface LoadingDotsProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  className?: string;
}

export function LoadingDots({ 
  size = 'md', 
  color = 'currentColor',
  className = '' 
}: LoadingDotsProps) {
  const sizeClasses = {
    sm: 'w-1 h-1',
    md: 'w-2 h-2',
    lg: 'w-3 h-3'
  };

  const dotClass = `${sizeClasses[size]} rounded-full`;

  return (
    <div className={`flex items-center space-x-1 ${className}`}>
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className={dotClass}
          style={{ backgroundColor: color }}
          variants={loadingDotsVariants}
          initial="initial"
          animate="animate"
          transition={{
            delay: i * 0.2,
            duration: 0.6,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      ))}
    </div>
  );
}

interface TypingIndicatorProps {
  text?: string;
  className?: string;
}

export function TypingIndicator({ 
  text = "AI가 입력 중입니다",
  className = '' 
}: TypingIndicatorProps) {
  return (
    <motion.div
      className={`flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400 ${className}`}
      variants={typingVariants}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <LoadingDots size="sm" color="rgb(107 114 128)" />
      <span>{text}</span>
    </motion.div>
  );
}

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: string;
  className?: string;
}

export function Spinner({ 
  size = 'md', 
  color = 'currentColor',
  className = '' 
}: SpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  return (
    <motion.div
      className={`${sizeClasses[size]} ${className}`}
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: "linear"
      }}
    >
      <svg
        className="w-full h-full"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke={color}
          strokeWidth="2"
          strokeOpacity="0.3"
        />
        <path
          d="M22 12c0-5.523-4.477-10-10-10"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    </motion.div>
  );
}

interface ProgressBarProps {
  progress: number; // 0-100
  height?: number;
  color?: string;
  backgroundColor?: string;
  className?: string;
  animated?: boolean;
}

export function ProgressBar({
  progress,
  height = 4,
  color = 'rgb(59 130 246)', // blue-500
  backgroundColor = 'rgb(229 231 235)', // gray-200
  className = '',
  animated = true
}: ProgressBarProps) {
  return (
    <div
      className={`w-full rounded-full overflow-hidden ${className}`}
      style={{ 
        height: `${height}px`,
        backgroundColor: backgroundColor
      }}
    >
      <motion.div
        className="h-full rounded-full"
        style={{ backgroundColor: color }}
        initial={animated ? { width: 0 } : { width: `${progress}%` }}
        animate={{ width: `${progress}%` }}
        transition={animated ? {
          duration: 0.5,
          ease: "easeOut"
        } : { duration: 0 }}
      />
    </div>
  );
}

interface PulseProps {
  children: React.ReactNode;
  intensity?: 'light' | 'medium' | 'strong';
  color?: string;
  className?: string;
}

export function Pulse({ 
  children, 
  intensity = 'medium',
  color = 'rgb(59 130 246)',
  className = '' 
}: PulseProps) {
  const intensityValues = {
    light: [1, 1.02, 1],
    medium: [1, 1.05, 1],
    strong: [1, 1.1, 1]
  };

  return (
    <motion.div
      className={className}
      animate={{
        scale: intensityValues[intensity],
        boxShadow: [
          `0 0 0 0 ${color}40`,
          `0 0 0 10px ${color}00`,
          `0 0 0 0 ${color}00`
        ]
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    >
      {children}
    </motion.div>
  );
}

interface WaveLoaderProps {
  bars?: number;
  height?: number;
  color?: string;
  className?: string;
}

export function WaveLoader({ 
  bars = 5, 
  height = 20,
  color = 'currentColor',
  className = '' 
}: WaveLoaderProps) {
  return (
    <div className={`flex items-center space-x-1 ${className}`}>
      {Array.from({ length: bars }, (_, i) => (
        <motion.div
          key={i}
          className="w-1 rounded-full"
          style={{ 
            backgroundColor: color,
            height: `${height}px`
          }}
          animate={{
            scaleY: [1, 2, 1],
            opacity: [0.5, 1, 0.5]
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: i * 0.1,
            ease: "easeInOut"
          }}
        />
      ))}
    </div>
  );
}

interface RippleProps {
  size?: number;
  color?: string;
  className?: string;
}

export function Ripple({ 
  size = 40, 
  color = 'rgb(59 130 246)',
  className = '' 
}: RippleProps) {
  return (
    <div 
      className={`relative flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
    >
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="absolute rounded-full border-2"
          style={{ 
            borderColor: color,
            width: size,
            height: size
          }}
          animate={{
            scale: [0, 1],
            opacity: [1, 0]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: i * 0.6,
            ease: "easeOut"
          }}
        />
      ))}
    </div>
  );
}

// AI 특화 로딩 인디케이터
export function AIThinkingIndicator({ className = '' }: { className?: string }) {
  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      <div className="flex items-center space-x-1">
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      <span className="text-sm text-gray-500 dark:text-gray-400">
        GAIA-BT가 분석 중입니다...
      </span>
    </div>
  );
}

// 검색 로딩 인디케이터
export function SearchLoadingIndicator({ 
  searchTerms = [], 
  className = '' 
}: { 
  searchTerms?: string[]; 
  className?: string; 
}) {
  return (
    <motion.div
      className={`flex items-center space-x-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg ${className}`}
      variants={typingVariants}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <Spinner size="sm" color="rgb(59 130 246)" />
      <div className="flex-1">
        <div className="text-sm font-medium text-blue-700 dark:text-blue-300">
          정보를 검색하고 있습니다...
        </div>
        {searchTerms.length > 0 && (
          <div className="text-xs text-blue-500 dark:text-blue-400 mt-1">
            검색 중: {searchTerms.join(', ')}
          </div>
        )}
      </div>
    </motion.div>
  );
}