'use client';

import React from 'react';
import { Clock, Database } from 'lucide-react';

interface WaitingTimerProps {
  seconds: number;
  isWaiting: boolean;
  isDeepResearchMode?: boolean;
}

const WaitingTimer: React.FC<WaitingTimerProps> = ({ seconds, isWaiting, isDeepResearchMode = false }) => {
  // Deep Research 모드에서만 타이머 표시
  if (!isWaiting || !isDeepResearchMode) return null;

  // 시간 형식 변환 함수
  const formatTime = (totalSeconds: number) => {
    const minutes = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // 진행률 계산 (30분 = 1800초)
  const progressPercentage = Math.min((seconds / 1800) * 100, 100);

  // 시간대별 상태 메시지
  const getStatusMessage = (seconds: number) => {
    if (seconds < 60) {
      return "초기 분석 중...";
    } else if (seconds < 300) { // 5분 미만
      return "데이터베이스 검색 중...";
    } else if (seconds < 600) { // 10분 미만
      return "심층 분석 수행 중...";
    } else if (seconds < 1200) { // 20분 미만
      return "복잡한 연관성 분석 중...";
    } else if (seconds < 1800) { // 30분 미만
      return "최종 결과 정리 중...";
    } else {
      return "매우 복잡한 질문 처리 중...";
    }
  };

  // 시간대별 색상
  const getProgressColor = (seconds: number) => {
    if (seconds < 300) return "bg-green-500"; // 5분 미만 - 녹색
    if (seconds < 900) return "bg-blue-500";  // 15분 미만 - 파란색
    if (seconds < 1500) return "bg-yellow-500"; // 25분 미만 - 노란색
    return "bg-red-500"; // 25분 이상 - 빨간색
  };

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-3 mb-2 shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1">
            <Database className="w-4 h-4 text-blue-600 animate-pulse" />
            <span className="text-sm font-medium text-blue-800">Deep Research 진행 중</span>
          </div>
          <div className="flex items-center space-x-1">
            <Clock className="w-3 h-3 text-blue-600" />
            <span className="text-sm text-blue-700 font-mono">{formatTime(seconds)}</span>
          </div>
        </div>
        <div className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded-full">
          최대 30분
        </div>
      </div>
      
      {/* 진행률 바 */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-2 overflow-hidden">
        <div 
          className={`h-full ${getProgressColor(seconds)} transition-all duration-1000 ease-out`}
          style={{ width: `${progressPercentage}%` }}
        />
      </div>
      
      {/* 상태 메시지 */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-blue-700">{getStatusMessage(seconds)}</span>
        <span className="text-blue-600">
          {seconds >= 1800 ? '30분 초과' : `${Math.round((1800 - seconds) / 60)}분 남음`}
        </span>
      </div>
      
      {/* 30분 경과 시 추가 안내 */}
      {seconds >= 1800 && (
        <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
          <div className="flex items-center space-x-1">
            <span className="font-medium">⚠️ 처리 시간 초과</span>
          </div>
          <div className="mt-1">
            매우 복잡한 질문이거나 서버 부하가 높습니다. 잠시 후 다시 질문해보시거나, 질문을 단순화해보세요.
          </div>
        </div>
      )}
    </div>
  );
};

export default WaitingTimer;