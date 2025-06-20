'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { useLongPress } from '@/hooks/use-touch-gestures';
import { Button } from './Button';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  children?: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

interface TouchButtonProps extends ButtonProps {
  onLongPress?: () => void;
  longPressDuration?: number;
  hapticFeedback?: boolean;
  touchScale?: number;
  rippleEffect?: boolean;
  className?: string;
  children?: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

export const TouchButton = React.forwardRef<HTMLButtonElement, TouchButtonProps>(
  ({ 
    className, 
    onLongPress,
    longPressDuration = 500,
    hapticFeedback = true,
    touchScale = 0.95,
    rippleEffect = true,
    children, 
    onClick,
    disabled,
    ...props 
  }, ref) => {
    const [isActive, setIsActive] = React.useState(false);
    const [ripples, setRipples] = React.useState<Array<{ id: string; x: number; y: number }>>([]);
    
    const longPressProps = useLongPress(() => {
      if (onLongPress && !disabled) {
        // 햅틱 피드백
        if (hapticFeedback && 'vibrate' in navigator) {
          navigator.vibrate(50);
        }
        onLongPress();
      }
    }, longPressDuration);

    const handleTouchStart = (e: React.TouchEvent<HTMLButtonElement>) => {
      setIsActive(true);
      
      if (rippleEffect && !disabled) {
        const rect = e.currentTarget.getBoundingClientRect();
        const touch = e.touches[0];
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;
        
        const newRipple = {
          id: Date.now().toString(),
          x,
          y
        };
        
        setRipples(prev => [...prev, newRipple]);
        
        // 리플 효과 제거
        setTimeout(() => {
          setRipples(prev => prev.filter(ripple => ripple.id !== newRipple.id));
        }, 600);
      }
      
      longPressProps.onTouchStart(e);
    };

    const handleTouchEnd = (e: React.TouchEvent<HTMLButtonElement>) => {
      setIsActive(false);
      longPressProps.onTouchEnd(e);
    };

    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
      if (!disabled) {
        // 경량 햅틱 피드백
        if (hapticFeedback && 'vibrate' in navigator) {
          navigator.vibrate(25);
        }
        onClick?.(e);
      }
    };

    return (
      <motion.div
        className="relative inline-block"
        whileTap={{ scale: disabled ? 1 : touchScale }}
        transition={{ type: "spring", stiffness: 400, damping: 17 }}
      >
        <Button
          ref={ref}
          className={cn(
            // 기본 터치 최적화 스타일
            "relative overflow-hidden",
            "min-h-[44px] min-w-[44px]", // Apple HIG 권장 최소 터치 타겟 크기
            "touch-manipulation", // iOS 더블탭 줌 방지
            "select-none", // 텍스트 선택 방지
            // 활성 상태 스타일
            isActive && !disabled && "brightness-90",
            // 길게 누르기 상태 스타일
            longPressProps.isPressed && !disabled && "ring-2 ring-blue-500 ring-opacity-50",
            className
          )}
          disabled={disabled}
          onClick={handleClick}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
          onTouchCancel={longPressProps.onTouchCancel}
          {...props}
        >
          {children}
          
          {/* 리플 효과 */}
          {rippleEffect && (
            <div className="absolute inset-0 overflow-hidden rounded-inherit pointer-events-none">
              {ripples.map((ripple) => (
                <motion.div
                  key={ripple.id}
                  className="absolute bg-white/30 rounded-full"
                  style={{
                    left: ripple.x,
                    top: ripple.y,
                  }}
                  initial={{
                    width: 0,
                    height: 0,
                    x: '-50%',
                    y: '-50%',
                    opacity: 1,
                  }}
                  animate={{
                    width: 200,
                    height: 200,
                    opacity: 0,
                  }}
                  transition={{
                    duration: 0.6,
                    ease: "easeOut",
                  }}
                />
              ))}
            </div>
          )}
        </Button>
      </motion.div>
    );
  }
);

TouchButton.displayName = 'TouchButton';

// 플로팅 액션 버튼 (FAB) 컴포넌트
interface FABProps extends TouchButtonProps {
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  offset?: string;
  className?: string;
  children?: React.ReactNode;
}

export const FloatingActionButton = React.forwardRef<HTMLButtonElement, FABProps>(
  ({ position = 'bottom-right', offset = '1rem', className, ...props }, ref) => {
    const positionClasses = {
      'bottom-right': 'bottom-4 right-4',
      'bottom-left': 'bottom-4 left-4', 
      'top-right': 'top-4 right-4',
      'top-left': 'top-4 left-4',
    };

    return (
      <motion.div
        className={cn(
          "fixed z-50",
          positionClasses[position]
        )}
        style={{ 
          bottom: position.includes('bottom') ? offset : undefined,
          top: position.includes('top') ? offset : undefined,
          right: position.includes('right') ? offset : undefined,
          left: position.includes('left') ? offset : undefined,
        }}
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0, opacity: 0 }}
        transition={{ type: "spring", stiffness: 260, damping: 20 }}
      >
        <TouchButton
          ref={ref}
          className={cn(
            "w-14 h-14 rounded-full shadow-lg",
            "bg-gradient-to-r from-blue-600 to-purple-600",
            "text-white hover:shadow-xl",
            "transition-shadow duration-200",
            className
          )}
          touchScale={0.9}
          {...props}
        />
      </motion.div>
    );
  }
);

FloatingActionButton.displayName = 'FloatingActionButton';