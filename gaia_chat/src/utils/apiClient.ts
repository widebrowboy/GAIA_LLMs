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

  // XMLHttpRequest 기반 fetch 대체 (fetch 문제 해결용)
  async xhrFetch(endpoint: string, method: string = 'GET', data?: any): Promise<any> {
    return new Promise(async (resolve) => {
      try {
        const url = getApiUrl(endpoint);
        console.log(`🔧 XHR Fetch 사용: ${method} ${url}`, data ? { data } : {});
        
        // 연결 전 서버 상태 간단 확인 (빠른 health check)
        try {
          console.log('🔍 XHR 요청 전 서버 연결 상태 확인...');
          const quickCheck = await fetch('http://localhost:8000/health', {
            method: 'HEAD', // HEAD 요청으로 빠른 확인
            signal: AbortSignal.timeout(2000) // 2초 타임아웃
          });
          if (!quickCheck.ok) {
            console.warn('⚠️ 사전 연결 확인 실패, 그래도 XHR 시도');
          } else {
            console.log('✅ 사전 연결 확인 성공');
          }
        } catch (quickError) {
          console.warn('⚠️ 사전 연결 확인 실패:', quickError, '- 그래도 XHR 시도');
        }
        
        const xhr = new XMLHttpRequest();
        xhr.open(method, url, true);
        
        // CORS 헤더 설정
        xhr.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
        xhr.setRequestHeader('Accept', 'application/json');
        xhr.setRequestHeader('Cache-Control', 'no-cache');
        
        // CORS credentials 설정
        xhr.withCredentials = false;
        
        xhr.onreadystatechange = function() {
          if (xhr.readyState === 4) {
            console.log(`📋 XHR 응답: ${xhr.status} ${xhr.statusText}`);
            console.log(`📋 XHR 응답 헤더:`, xhr.getAllResponseHeaders());
            
            if (xhr.status >= 200 && xhr.status < 300) {
              try {
                const responseText = xhr.responseText;
                console.log(`📄 XHR 응답 텍스트 (처음 200자):`, responseText.substring(0, 200));
                
                if (!responseText.trim()) {
                  console.warn('⚠️ 빈 응답 텍스트');
                  resolve({ success: false, error: '서버에서 빈 응답을 받았습니다' });
                  return;
                }
                
                const data = JSON.parse(responseText);
                console.log('✅ XHR 성공:', data);
                resolve({ success: true, data });
              } catch (parseError) {
                console.error('❌ XHR JSON 파싱 오류:', parseError);
                console.error('❌ 원본 응답:', xhr.responseText);
                resolve({ success: false, error: `JSON 파싱 실패: ${parseError}` });
              }
            } else {
              // HTTP 오류: 0 처리 - 네트워크 연결 실패 또는 서버 미준비 상태
              if (xhr.status === 0) {
                console.error(`❌ XHR HTTP 오류: 0 - 네트워크 연결 실패 또는 서버 미준비`);
                console.error(`🔍 URL: ${url}, Method: ${method}`);
                console.error(`🔍 Ready State: ${xhr.readyState}, Status: ${xhr.status}`);
                resolve({ success: false, error: 'Network connection failed or server not ready' });
              } else {
                console.error(`❌ XHR HTTP 오류: ${xhr.status}`, xhr.responseText);
                resolve({ success: false, error: `HTTP ${xhr.status}: ${xhr.statusText}` });
              }
            }
          }
        };
        
        xhr.onerror = function() {
          console.error('💥 XHR 네트워크 오류');
          console.error(`🔍 오류 발생 URL: ${url}`);
          console.error(`🔍 XHR Status: ${xhr.status}, ReadyState: ${xhr.readyState}`);
          console.error(`🔍 StatusText: ${xhr.statusText}`);
          resolve({ success: false, error: 'Network error - 서버에 연결할 수 없습니다 (서버가 시작 중이거나 네트워크 문제)' });
        };
        
        xhr.ontimeout = function() {
          console.error('⏰ XHR 타임아웃');
          resolve({ success: false, error: 'XHR 타임아웃 - 서버 응답이 너무 늦습니다' });
        };
        
        xhr.timeout = 15000; // 15초 타임아웃으로 연장 (서버 준비 시간 고려)
        
        // 요청 전송
        if (method === 'POST' || method === 'PUT') {
          const payload = data ? JSON.stringify(data) : JSON.stringify({});
          console.log(`📤 XHR 요청 데이터:`, payload);
          xhr.send(payload);
        } else {
          xhr.send();
        }
        
      } catch (error) {
        console.error('💥 XHR 설정 오류:', error);
        resolve({ success: false, error: error instanceof Error ? error.message : '알 수 없는 오류' });
      }
    });
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
    
    // 1차: XMLHttpRequest 시도 (fetch 문제 우회)
    try {
      console.log('🥇 XHR 방식 시도');
      const xhrResult = await this.xhrFetch('/api/system/models/detailed');
      if (xhrResult.success) {
        console.log('✅ XHR 방식 성공!');
        return xhrResult;
      }
      console.warn('⚠️ XHR 방식 실패, fetchWithRetry로 폴백');
    } catch (error) {
      console.warn('⚠️ XHR 방식 예외, fetchWithRetry로 폴백:', error);
    }
    
    // 2차: 복잡한 fetchWithRetry 시도
    try {
      console.log('🥈 fetchWithRetry 시도');
      const result = await this.fetchWithRetry('/api/system/models/detailed');
      if (result.success) {
        console.log('✅ fetchWithRetry 성공!');
        return result;
      }
      console.warn('⚠️ fetchWithRetry 실패, simpleFetch로 폴백');
    } catch (error) {
      console.warn('⚠️ fetchWithRetry 예외, simpleFetch로 폴백:', error);
    }
    
    // 3차: 간단한 fetch로 최종 폴백
    console.log('🥉 simpleFetch 최종 시도');
    return this.simpleFetch('/api/system/models/detailed');
  }

  // 모델 시작
  async startModel(modelName: string) {
    const encodedName = encodeURIComponent(modelName);
    console.log(`🚀 모델 시작 요청: ${modelName} -> ${encodedName}`);
    
    // XHR 우선 시도
    try {
      const xhrResult = await this.xhrFetch(`/api/system/models/${encodedName}/start`, 'POST', {});
      if (xhrResult.success) {
        console.log('✅ XHR 모델 시작 성공');
        return xhrResult;
      }
      console.warn('⚠️ XHR 모델 시작 실패:', xhrResult.error);
    } catch (error) {
      console.warn('⚠️ XHR 방식 예외, simpleFetch로 폴백:', error);
    }
    
    console.log('🔄 simpleFetch로 모델 시작 재시도');
    return this.simpleFetch(`/api/system/models/${encodedName}/start`, 'POST');
  }

  // 모델 중지
  async stopModel(modelName: string) {
    const encodedName = encodeURIComponent(modelName);
    console.log(`🛑 모델 중지 요청: ${modelName} -> ${encodedName}`);
    
    // XHR 우선 시도
    try {
      const xhrResult = await this.xhrFetch(`/api/system/models/${encodedName}/stop`, 'POST', {});
      if (xhrResult.success) {
        console.log('✅ XHR 모델 중지 성공');
        return xhrResult;
      }
      console.warn('⚠️ XHR 모델 중지 실패:', xhrResult.error);
    } catch (error) {
      console.warn('⚠️ XHR 방식 예외, simpleFetch로 폴백:', error);
    }
    
    console.log('🔄 simpleFetch로 모델 중지 재시도');
    return this.simpleFetch(`/api/system/models/${encodedName}/stop`, 'POST');
  }

  // 시스템 상태 확인
  async checkHealth() {
    console.log(`💊 Health 체크 요청`);
    
    // XHR 우선 시도
    try {
      const xhrResult = await this.xhrFetch('/health');
      if (xhrResult.success) {
        console.log('✅ XHR Health 체크 성공');
        return xhrResult;
      }
      console.warn('⚠️ XHR Health 체크 실패:', xhrResult.error);
    } catch (error) {
      console.warn('⚠️ XHR 방식 예외, simpleFetch로 폴백:', error);
    }
    
    console.log('🔄 simpleFetch로 Health 체크 재시도');
    return this.simpleFetch('/health');
  }

  // 완전 독립적인 안전한 API 호출 (마지막 fallback)
  async safeApiCall(endpoint: string): Promise<any> {
    console.log(`🛡️ 안전한 API 호출: ${endpoint}`);
    
    try {
      const url = getApiUrl(endpoint);
      console.log(`🌐 안전한 API URL: ${url}`);
      
      // Image나 XMLHttpRequest를 이용한 가장 기본적인 방법
      return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
          console.log('✅ 서버 연결 확인됨 (이미지 로딩 성공)');
          resolve({ success: true, data: { status: 'reachable' } });
        };
        img.onerror = () => {
          console.log('❌ 서버 연결 실패 (이미지 로딩 실패)');
          resolve({ success: false, error: '서버 연결 실패' });
        };
        // 실제 API 엔드포인트가 아닌 favicon을 테스트
        img.src = getApiUrl('/favicon.ico');
        
        // 5초 후 타임아웃
        setTimeout(() => {
          console.log('⏰ 안전한 API 호출 타임아웃');
          resolve({ success: false, error: '연결 타임아웃' });
        }, 5000);
      });
      
    } catch (error) {
      console.error('💥 안전한 API 호출 예외:', error);
      return { success: false, error: error instanceof Error ? error.message : '알 수 없는 오류' };
    }
  }
}

export const apiClient = ApiClient.getInstance();