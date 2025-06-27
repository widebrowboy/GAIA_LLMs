'use client';

import { getApiUrl } from '@/config/api';

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

/**
 * API 클라이언트 미들웨어
 * - 자동 재시도
 * - 에러 처리
 * - 타임아웃 관리
 */
export class ApiClient {
  private static instance: ApiClient;
  private retryCount = 3;
  private retryDelay = 1000; // 1초

  static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient();
    }
    return ApiClient.instance;
  }

  private async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async fetchWithRetry<T = any>(
    endpoint: string,
    options: RequestInit = {},
    retries = this.retryCount
  ): Promise<ApiResponse<T>> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30초 타임아웃

    try {
      const response = await fetch(getApiUrl(endpoint), {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        if (retries > 0 && response.status >= 500) {
          console.warn(`API 요청 실패 (${response.status}), 재시도 중... (남은 횟수: ${retries})`);
          await this.sleep(this.retryDelay);
          return this.fetchWithRetry(endpoint, options, retries - 1);
        }
        
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return { success: true, data };
      
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof Error && error.name === 'AbortError') {
        if (retries > 0) {
          console.warn(`API 요청 타임아웃, 재시도 중... (남은 횟수: ${retries})`);
          await this.sleep(this.retryDelay);
          return this.fetchWithRetry(endpoint, options, retries - 1);
        }
        return { success: false, error: '요청 시간 초과' };
      }
      
      console.error('API 요청 오류:', error);
      return { success: false, error: error instanceof Error ? error.message : '알 수 없는 오류' };
    }
  }

  // 모델 상세 정보 가져오기
  async getModelsDetailed() {
    return this.fetchWithRetry('/api/system/models/detailed');
  }

  // 모델 시작
  async startModel(modelName: string) {
    const encodedName = encodeURIComponent(modelName);
    return this.fetchWithRetry(`/api/system/models/${encodedName}/start`, {
      method: 'POST',
    });
  }

  // 모델 중지
  async stopModel(modelName: string) {
    const encodedName = encodeURIComponent(modelName);
    return this.fetchWithRetry(`/api/system/models/${encodedName}/stop`, {
      method: 'POST',
    });
  }

  // 시스템 상태 확인
  async checkHealth() {
    return this.fetchWithRetry('/health');
  }
}

export const apiClient = ApiClient.getInstance();