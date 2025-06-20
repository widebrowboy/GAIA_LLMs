'use client';

import { useState, useEffect, useRef, RefObject } from 'react';

interface TouchPosition {
  x: number;
  y: number;
}

interface SwipeGesture {
  direction: 'left' | 'right' | 'up' | 'down' | null;
  distance: number;
  velocity: number;
  duration: number;
}

interface TouchGestureOptions {
  minSwipeDistance?: number;
  maxSwipeTime?: number;
  preventScroll?: boolean;
  enablePinch?: boolean;
}

export function useTouchGestures(
  elementRef: RefObject<HTMLElement>,
  options: TouchGestureOptions = {}
) {
  const {
    minSwipeDistance = 50,
    maxSwipeTime = 500,
    preventScroll = false,
    enablePinch = false
  } = options;

  const [gesture, setGesture] = useState<SwipeGesture>({
    direction: null,
    distance: 0,
    velocity: 0,
    duration: 0
  });

  const [isScrolling, setIsScrolling] = useState(false);
  const [isPinching, setIsPinching] = useState(false);
  const [pinchScale, setPinchScale] = useState(1);

  const touchStartRef = useRef<TouchPosition | null>(null);
  const touchStartTime = useRef<number>(0);
  const initialPinchDistance = useRef<number>(0);
  const lastPinchScale = useRef<number>(1);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const getDistance = (touch1: Touch, touch2: Touch) => {
      const dx = touch1.clientX - touch2.clientX;
      const dy = touch1.clientY - touch2.clientY;
      return Math.sqrt(dx * dx + dy * dy);
    };

    const handleTouchStart = (e: TouchEvent) => {
      if (preventScroll) {
        e.preventDefault();
      }

      const touch = e.touches[0];
      touchStartRef.current = { x: touch.clientX, y: touch.clientY };
      touchStartTime.current = Date.now();
      setIsScrolling(false);

      // 핀치 제스처 초기화
      if (enablePinch && e.touches.length === 2) {
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        initialPinchDistance.current = getDistance(touch1, touch2);
        setIsPinching(true);
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (!touchStartRef.current) return;

      const touch = e.touches[0];
      const deltaX = Math.abs(touch.clientX - touchStartRef.current.x);
      const deltaY = Math.abs(touch.clientY - touchStartRef.current.y);

      // 스크롤 감지 (세로 움직임이 가로보다 큰 경우)
      if (deltaY > deltaX && deltaY > 10) {
        setIsScrolling(true);
      }

      // 핀치 제스처 처리
      if (enablePinch && e.touches.length === 2 && isPinching) {
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        const currentDistance = getDistance(touch1, touch2);
        
        if (initialPinchDistance.current > 0) {
          const scale = currentDistance / initialPinchDistance.current;
          setPinchScale(lastPinchScale.current * scale);
        }
      }

      if (preventScroll) {
        e.preventDefault();
      }
    };

    const handleTouchEnd = (e: TouchEvent) => {
      if (!touchStartRef.current || isScrolling) {
        touchStartRef.current = null;
        setIsScrolling(false);
        return;
      }

      const touch = e.changedTouches[0];
      const endTime = Date.now();
      const duration = endTime - touchStartTime.current;

      // 핀치 제스처 종료
      if (enablePinch && isPinching) {
        setIsPinching(false);
        lastPinchScale.current = pinchScale;
        return;
      }

      if (duration > maxSwipeTime) {
        touchStartRef.current = null;
        return;
      }

      const deltaX = touch.clientX - touchStartRef.current.x;
      const deltaY = touch.clientY - touchStartRef.current.y;
      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

      if (distance < minSwipeDistance) {
        touchStartRef.current = null;
        return;
      }

      const velocity = distance / duration;
      let direction: SwipeGesture['direction'] = null;

      // 방향 결정
      if (Math.abs(deltaX) > Math.abs(deltaY)) {
        direction = deltaX > 0 ? 'right' : 'left';
      } else {
        direction = deltaY > 0 ? 'down' : 'up';
      }

      setGesture({
        direction,
        distance,
        velocity,
        duration
      });

      touchStartRef.current = null;
    };

    // 이벤트 리스너 등록
    element.addEventListener('touchstart', handleTouchStart, { passive: !preventScroll });
    element.addEventListener('touchmove', handleTouchMove, { passive: !preventScroll });
    element.addEventListener('touchend', handleTouchEnd);

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchmove', handleTouchMove);
      element.removeEventListener('touchend', handleTouchEnd);
    };
  }, [
    elementRef,
    minSwipeDistance,
    maxSwipeTime,
    preventScroll,
    enablePinch,
    isScrolling,
    isPinching,
    pinchScale
  ]);

  const resetGesture = () => {
    setGesture({
      direction: null,
      distance: 0,
      velocity: 0,
      duration: 0
    });
  };

  const resetPinch = () => {
    setPinchScale(1);
    lastPinchScale.current = 1;
  };

  return {
    gesture,
    isScrolling,
    isPinching,
    pinchScale,
    resetGesture,
    resetPinch
  };
}

// 스와이프 전용 훅 (간단한 버전)
export function useSwipe(
  elementRef: RefObject<HTMLElement>,
  callbacks: {
    onSwipeLeft?: () => void;
    onSwipeRight?: () => void;
    onSwipeUp?: () => void;
    onSwipeDown?: () => void;
  },
  options: TouchGestureOptions = {}
) {
  const { gesture, resetGesture } = useTouchGestures(elementRef, options);

  useEffect(() => {
    if (gesture.direction) {
      switch (gesture.direction) {
        case 'left':
          callbacks.onSwipeLeft?.();
          break;
        case 'right':
          callbacks.onSwipeRight?.();
          break;
        case 'up':
          callbacks.onSwipeUp?.();
          break;
        case 'down':
          callbacks.onSwipeDown?.();
          break;
      }
      resetGesture();
    }
  }, [gesture, callbacks, resetGesture]);

  return { gesture };
}

// 길게 누르기 감지 훅
export function useLongPress(
  callback: () => void,
  duration: number = 500
) {
  const [isPressed, setIsPressed] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const start = () => {
    setIsPressed(true);
    timerRef.current = setTimeout(() => {
      callback();
    }, duration);
  };

  const stop = () => {
    setIsPressed(false);
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  };

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  return {
    isPressed,
    onTouchStart: start,
    onTouchEnd: stop,
    onTouchCancel: stop,
    onMouseDown: start,
    onMouseUp: stop,
    onMouseLeave: stop,
  };
}