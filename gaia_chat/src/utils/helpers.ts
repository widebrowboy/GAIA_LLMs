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
