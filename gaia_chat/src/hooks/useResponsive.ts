'use client';

import { useState, useEffect } from 'react';

interface ResponsiveState {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  width: number;
  height: number;
}

export const useResponsive = (): ResponsiveState => {
  const [state, setState] = useState<ResponsiveState>({
    isMobile: false,
    isTablet: false,
    isDesktop: true,
    width: 1200,
    height: 800,
  });

  useEffect(() => {
    const updateSize = () => {
      if (typeof window === 'undefined') return;
      
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      setState({
        isMobile: width < 768,
        isTablet: width >= 768 && width < 1024,
        isDesktop: width >= 1024,
        width,
        height,
      });
    };

    // 초기 크기 설정
    updateSize();

    // 클라이언트 사이드에서만 이벤트 리스너 추가
    if (typeof window !== 'undefined') {
      // 리사이즈 이벤트 리스너 추가
      window.addEventListener('resize', updateSize);
      
      // 디바이스 방향 변경 감지 (모바일)
      const handleOrientationChange = () => {
        setTimeout(updateSize, 100);
      };
      window.addEventListener('orientationchange', handleOrientationChange);

      return () => {
        window.removeEventListener('resize', updateSize);
        window.removeEventListener('orientationchange', handleOrientationChange);
      };
    }
  }, []);

  return state;
};

export default useResponsive;