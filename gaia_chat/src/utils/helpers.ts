/**
 * 날짜 형식화 유틸리티 함수
 * 24시간 이내의 날짜는 시간:분 형식으로 표시
 * 24시간 이상 지난 날짜는 월 일 형식으로 표시
 */
export const formatDate = (date: Date): string => {
  const now = new Date();
  const messageDate = new Date(date);
  const diffInHours = (now.getTime() - messageDate.getTime()) / (1000 * 60 * 60);
  
  if (diffInHours < 24) {
    return messageDate.toLocaleTimeString('ko-KR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  } else {
    return messageDate.toLocaleDateString('ko-KR', { 
      month: 'short', 
      day: 'numeric' 
    });
  }
};

/**
 * 상대적 시간 표시 함수
 * 현재 시간을 기준으로 몇 분 전, 몇 시간 전, 몇 일 전 등으로 표시
 */
export const formatRelativeTime = (date: Date | string): string => {
  const now = new Date();
  const messageDate = new Date(date);
  const diffInMs = now.getTime() - messageDate.getTime();
  
  // 음수인 경우 (미래 시간) 처리
  if (diffInMs < 0) {
    return '방금 전';
  }
  
  const diffInSeconds = Math.floor(diffInMs / 1000);
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  const diffInHours = Math.floor(diffInMinutes / 60);
  const diffInDays = Math.floor(diffInHours / 24);
  const diffInWeeks = Math.floor(diffInDays / 7);
  const diffInMonths = Math.floor(diffInDays / 30);
  const diffInYears = Math.floor(diffInDays / 365);
  
  if (diffInSeconds < 60) {
    return '방금 전';
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}분 전`;
  } else if (diffInHours < 24) {
    return `${diffInHours}시간 전`;
  } else if (diffInDays < 7) {
    return `${diffInDays}일 전`;
  } else if (diffInWeeks < 4) {
    return `${diffInWeeks}주 전`;
  } else if (diffInMonths < 12) {
    return `${diffInMonths}개월 전`;
  } else {
    return `${diffInYears}년 전`;
  }
};

/**
 * 절대 시간 표시 함수 (연구 기록용)
 * 연구 시작 날짜와 시간을 "2024년 1월 15일 14:30" 형식으로 표시
 */
export const formatAbsoluteDateTime = (date: Date | string): string => {
  const targetDate = new Date(date);
  const now = new Date();
  
  const year = targetDate.getFullYear();
  const month = targetDate.getMonth() + 1;
  const day = targetDate.getDate();
  const hours = targetDate.getHours();
  const minutes = targetDate.getMinutes();
  
  // 오늘인지 확인
  const isToday = targetDate.toDateString() === now.toDateString();
  
  // 이번 년도인지 확인
  const isThisYear = targetDate.getFullYear() === now.getFullYear();
  
  if (isToday) {
    // 오늘이면 시간만 표시
    return `오늘 ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
  } else if (isThisYear) {
    // 올해면 년도 생략
    return `${month}월 ${day}일 ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
  } else {
    // 다른 년도면 년도 포함
    return `${year}년 ${month}월 ${day}일 ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
  }
};

/**
 * 문자열이 비어있는지 확인
 */
export const isEmpty = (str: string | null | undefined): boolean => {
  return !str || str.trim().length === 0;
};

/**
 * 문자열 길이를 제한하여 반환
 */
export const truncateString = (str: string, maxLength: number): string => {
  if (!str) return '';
  return str.length > maxLength ? `${str.substring(0, maxLength)}...` : str;
};
