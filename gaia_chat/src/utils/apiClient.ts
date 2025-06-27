'use client';

import { getApiUrl } from '@/config/api';

// Next.js 환경에서 fetch API 타입 확실하게 지정
declare global {
  const fetch: typeof globalThis.fetch;
}

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
    const fullUrl = getApiUrl(endpoint);
    console.log(`🌐 API 요청 시작: ${fullUrl}`, { 
      method: options.method || 'GET',
      retries,
      headers: options.headers 
    });

    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      console.warn(`⏰ API 요청 타임아웃 (10초): ${fullUrl}`);
      controller.abort();
    }, 10000); // 10초로 단축

    try {
      const fetchOptions: RequestInit = {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          ...options.headers,
        },
      };

      console.log(`📡 fetch 호출 중: ${fullUrl}`, fetchOptions);
      
      // @ts-ignore - fetch API 타입 오류 완전 우회
      const response = await fetch(fullUrl, fetchOptions);
      
      console.log(`📥 응답 받음: ${fullUrl}`, {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        headers: Object.fromEntries(response.headers.entries())
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Unknown error');
        console.error(`❌ HTTP 오류: ${response.status} ${response.statusText}`, {
          url: fullUrl,
          errorText,
          retries
        });
        
        if (retries > 0 && response.status >= 500) {
          console.warn(`🔄 재시도 중... (남은 횟수: ${retries})`);
          await this.sleep(this.retryDelay);
          return this.fetchWithRetry(endpoint, options, retries - 1);
        }
        
        throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
      }

      const responseText = await response.text();
      console.log(`📄 원본 응답 텍스트: ${fullUrl}`, responseText.substring(0, 200) + '...');
      
      let data;
      try {
        data = JSON.parse(responseText);
        console.log(`✅ JSON 파싱 성공: ${fullUrl}`, data);
      } catch (parseError) {
        console.error(`❌ JSON 파싱 실패: ${fullUrl}`, parseError, responseText);
        throw new Error(`JSON 파싱 오류: ${parseError}`);
      }

      return { success: true, data };
      
    } catch (error) {
      clearTimeout(timeoutId);
      
      console.error(`💥 API 요청 예외: ${fullUrl}`, {
        error,
        name: error instanceof Error ? error.name : 'Unknown',
        message: error instanceof Error ? error.message : error,
        retries
      });
      
      if (error instanceof Error && error.name === 'AbortError') {
        if (retries > 0) {
          console.warn(`🔄 타임아웃 재시도 중... (남은 횟수: ${retries})`);
          await this.sleep(this.retryDelay);
          return this.fetchWithRetry(endpoint, options, retries - 1);
        }
        return { success: false, error: '요청 시간 초과' };
      }
      
      return { 
        success: false, 
        error: error instanceof Error ? error.message : '알 수 없는 오류'
      };
    }
  }

  // 간단한 fallback fetch (타입 오류 우회)
  async simpleFetch(endpoint: string, method: string = 'GET'): Promise<any> {
    try {
      const url = getApiUrl(endpoint);
      console.log(`🔧 SimpleFetch 사용: ${method} ${url}`);
      
      // @ts-ignore - 타입 체크 우회
      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        // POST일 때만 body 추가 (필요한 경우)
        ...(method === 'POST' ? { body: JSON.stringify({}) } : {})
      });
      
      console.log(`📋 SimpleFetch 응답: ${response.status} ${response.statusText}`);
      
      if (response.ok) {
        const data = await response.json();
        return { success: true, data };
      } else {
        const errorText = await response.text().catch(() => 'Unknown error');
        console.error(`❌ SimpleFetch HTTP 오류: ${response.status}`, errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
    } catch (error) {
      console.error('💥 SimpleFetch 예외:', error);
      return { success: false, error: error instanceof Error ? error.message : '알 수 없는 오류' };
    }
  }

  // 모델 상세 정보 가져오기
  async getModelsDetailed() {
    console.log('🎯 getModelsDetailed 호출');
    
    // 먼저 복잡한 fetchWithRetry 시도
    try {
      const result = await this.fetchWithRetry('/api/system/models/detailed');
      if (result.success) {
        return result;
      }
      console.warn('⚠️ fetchWithRetry 실패, simpleFetch로 폴백');
    } catch (error) {
      console.warn('⚠️ fetchWithRetry 예외, simpleFetch로 폴백:', error);
    }
    
    // 실패 시 간단한 fetch로 폴백
    return this.simpleFetch('/api/system/models/detailed');
  }

  // 모델 시작
  async startModel(modelName: string) {
    const encodedName = encodeURIComponent(modelName);
    console.log(`🚀 모델 시작 요청: ${modelName} -> ${encodedName}`);
    return this.simpleFetch(`/api/system/models/${encodedName}/start`, 'POST');
  }

  // 모델 중지
  async stopModel(modelName: string) {
    const encodedName = encodeURIComponent(modelName);
    console.log(`🛑 모델 중지 요청: ${modelName} -> ${encodedName}`);
    return this.simpleFetch(`/api/system/models/${encodedName}/stop`, 'POST');
  }

  // 시스템 상태 확인
  async checkHealth() {
    console.log(`💊 Health 체크 요청`);
    return this.simpleFetch('/health');
  }
}

export const apiClient = ApiClient.getInstance();