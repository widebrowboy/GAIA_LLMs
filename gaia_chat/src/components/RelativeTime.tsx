'use client';

import React, { useState, useEffect } from 'react';
import { formatRelativeTime } from '@/utils/helpers';

interface RelativeTimeProps {
  date: Date | string;
  className?: string;
  updateInterval?: number; // 밀리초 단위, 기본값 60초
}

const RelativeTime: React.FC<RelativeTimeProps> = ({ 
  date, 
  className = '', 
  updateInterval = 60000 
}) => {
  const [relativeTime, setRelativeTime] = useState<string>('');

  useEffect(() => {
    // 초기 시간 설정
    const updateTime = () => {
      setRelativeTime(formatRelativeTime(date));
    };

    updateTime();

    // 주기적 업데이트
    const interval = setInterval(updateTime, updateInterval);

    return () => clearInterval(interval);
  }, [date, updateInterval]);

  return <span className={className}>{relativeTime}</span>;
};

export default RelativeTime;