'use client';

/**
 * API 설정 관리 모듈
 * 모든 API 요청에서 일관된 설정을 사용하기 위한 중앙 설정
 */

// API 포트 가져오기
export const getApiPort = (): string => {
  return process.env.NEXT_PUBLIC_API_PORT || '8000';
};

// API 기본 URL
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

// 기본 요청 타임아웃(ms)
export const DEFAULT_TIMEOUT = 10000;

// Default request headers (ensure UTF-8 encoding safety)
export const getDefaultHeaders = (): Record<string, string> => ({
  'Accept': 'application/json, text/plain, */*; charset=utf-8',
  'Content-Type': 'application/json; charset=utf-8',
  'Accept-Charset': 'utf-8'
});

// API 엔드포인트 URL 생성
export const getApiUrl = (endpoint: string): string => {
  return `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
};

// 시스템 기본 설정값
export const DEFAULT_MODEL = 'gemma3-12b:latest';
export const DEFAULT_MODE = 'normal';
