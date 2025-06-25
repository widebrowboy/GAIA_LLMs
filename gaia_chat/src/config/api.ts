'use client';

/**
 * API 설정 관리 모듈
 * 모든 컴포넌트에서 일관된 API URL을 사용하기 위한 중앙 설정
 */

// 환경에 따른 API URL 동적 설정
/**
 * API_BASE_URL: 환경변수 및 실행 환경에 따라 동적으로 API 서버 주소를 결정
 * 우선순위: NEXT_PUBLIC_API_URL > (localhost && NEXT_PUBLIC_API_PORT) > 기본값(8000)
 * 프론트엔드 포트도 환경변수로 관리할 수 있도록 구조화 (NEXT_PUBLIC_WEBUI_PORT)
 */
const getApiPort = () => {
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    // 개발 환경: window.location.port 우선 사용
    return process.env.NEXT_PUBLIC_API_PORT || '8000';
  }
  // 배포 환경: 환경변수 우선
  return process.env.NEXT_PUBLIC_API_PORT || '8000';
};

export const API_BASE_URL = (() => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    return `http://localhost:${getApiPort()}`;
  }
  // 배포 환경 기본값
  return `http://localhost:8000`;
})();

// API 관련 유틸리티 함수
export const getApiUrl = (endpoint: string): string => {
  return `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
};

// API 상태 체크 함수
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch(getApiUrl('/health'), {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      cache: 'no-store'
    });
    return response.ok;
  } catch (error) {
    console.error('API 상태 체크 실패:', error);
    return false;
  }
};
