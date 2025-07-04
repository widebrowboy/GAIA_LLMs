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
  private serverReady = true; // 서버 준비 상태 추적

  constructor() {
    // this 바인딩 보장 - 모든 메서드를 바인딩하여 this 참조 문제 해결
    this.sleep = this.sleep.bind(this);
    this.fetchWithRetry = this.fetchWithRetry.bind(this);
    this.xhrFetch = this.xhrFetch.bind(this);
    this.simpleFetch = this.simpleFetch.bind(this);
    this.getModelsDetailed = this.getModelsDetailed.bind(this);
    this.switchModelSafely = this.switchModelSafely.bind(this);
    this.startModel = this.startModel.bind(this);
    this.stopModel = this.stopModel.bind(this);
    this.startModelMultiple = this.startModelMultiple.bind(this);
    this.stopAllModels = this.stopAllModels.bind(this);
    this.checkHealth = this.checkHealth.bind(this);
    this.changeModel = this.changeModel.bind(this);
    this.safeApiCall = this.safeApiCall.bind(this);
  }

  static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient();
      
      // 인스턴스 검증 강화
      if (typeof ApiClient.instance.xhrFetch !== 'function') {
        console.error('❌ xhrFetch 메서드 바인딩 실패');
        throw new Error('ApiClient 인스턴스 생성 실패: xhrFetch 메서드가 함수가 아닙니다');
      } else {
        console.log('✅ ApiClient 인스턴스 생성 완료');
      }
    }
    return ApiClient.instance;
  }

  // 안전한 정적 메서드 (this 바인딩 문제 완전 해결)
  static async safeXhrFetch(endpoint: string, method: string = 'GET', data?: any): Promise<any> {
    const instance = ApiClient.getInstance();
    const boundMethod = instance.xhrFetch.bind(instance);
    return boundMethod(endpoint, method, data);
  }

  private sleep = async (ms: number): Promise<void> => {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  fetchWithRetry = async <T = any>(
    endpoint: string,
    options: RequestInit = {},
    retries = this.retryCount
  ): Promise<ApiResponse<T>> => {
    const fullUrl = getApiUrl(endpoint);
    console.log(`🌐 API 요청 시작: ${fullUrl}`, { 
      method: options.method || 'GET',
      retries,
      headers: options.headers 
    });

    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      console.warn(`⏰ API 요청 타임아웃 (30초): ${fullUrl}`);
      controller.abort();
    }, 30000); // 30초로 증가 (모델 작업 고려)

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
        console.warn(`⚠️ HTTP 오류: ${response.status} ${response.statusText}`, {
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
        console.warn(`⚠️ JSON 파싱 실패: ${fullUrl}`, parseError, responseText);
        throw new Error(`JSON 파싱 오류: ${parseError}`);
      }

      return { success: true, data };
      
    } catch (error) {
      clearTimeout(timeoutId);
      
      console.warn(`⚠️ API 요청 예외: ${fullUrl}`, {
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

  // XMLHttpRequest 기반 fetch 대체 (fetch 문제 해결용) - 재시도 로직 포함
  xhrFetch = async (endpoint: string, method: string = 'GET', data?: any, retryCount: number = 5): Promise<any> => {
    return new Promise((resolve) => {
      try {
        const url = getApiUrl(endpoint);
        console.log(`🔧 XHR Fetch 사용: ${method} ${url}`, data ? { data } : {});
        
        // XHR 요청 바로 시작 (서버 준비 대기 제거)
        console.log('🔧 XHR 요청 시작...');
        
        const xhr = new XMLHttpRequest();
        xhr.open(method, url, true);
        
        // CORS 헤더 설정
        xhr.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
        xhr.setRequestHeader('Accept', 'application/json');
        xhr.setRequestHeader('Cache-Control', 'no-cache');
        
        // CORS credentials 설정
        xhr.withCredentials = false;
        
        xhr.onreadystatechange = () => {
          if (xhr.readyState === 4) {
            console.log(`📋 XHR 응답: ${xhr.status} ${xhr.statusText}`);
            console.log(`📋 XHR 응답 헤더:`, xhr.getAllResponseHeaders());
            
            if (xhr.status >= 200 && xhr.status < 300) {
              try {
                const responseText = xhr.responseText;
                console.log(`📄 XHR 응답 텍스트 (처음 200자):`, responseText.substring(0, 200));
                
                if (!responseText || !responseText.trim()) {
                  console.warn('⚠️ 빈 응답 텍스트 - 서버 연결 문제일 수 있음');
                  resolve({ success: false, error: '서버에서 빈 응답을 받았습니다. 서버 상태를 확인해주세요.' });
                  return;
                }
                
                const data = JSON.parse(responseText);
                console.log('✅ XHR 성공:', data);
                resolve({ success: true, data });
              } catch (parseError) {
                console.warn('⚠️ XHR JSON 파싱 오류:', parseError);
                console.log('📄 원본 응답:', xhr.responseText);
                resolve({ success: false, error: `JSON 파싱 실패: ${parseError}` });
              }
            } else {
              // HTTP 오류: 0 처리 - 상세 분석 및 자세한 오류 정보 제공
              if (xhr.status === 0) {
                console.warn(`⚠️ XHR HTTP Status 0 - 연결 문제 감지`);
                console.log(`🔍 URL: ${url}`);
                console.log(`🔍 Method: ${method}`);
                console.log(`🔍 Ready State: ${xhr.readyState}`);
                console.log(`🔍 Response Text: ${xhr.responseText || '(empty)'}`);
                console.log(`🔍 Response Headers: ${xhr.getAllResponseHeaders() || '(none)'}`);
                console.log(`🔍 Server Ready Status: ${this.serverReady}`);
                
                // 구체적인 오류 원인 분석 및 해결책 제안
                let errorMessage = 'HTTP Status 0 오류 - ';
                let troubleshootingTips = [];
                
                if (!this.serverReady) {
                  errorMessage += '서버가 완전히 준비되지 않았습니다.';
                  troubleshootingTips.push('서버 시작 완료 대기 중...');
                  troubleshootingTips.push('잠시 후 자동으로 재시도됩니다.');
                } else {
                  errorMessage += '네트워크 연결 또는 CORS 문제입니다.';
                  troubleshootingTips.push('브라우저 새로고침을 시도해보세요.');
                  troubleshootingTips.push('서버가 http://localhost:8000에서 실행 중인지 확인하세요.');
                }
                
                console.log('💡 문제 해결 방법:', troubleshootingTips);
                
                // HTTP Status 0 오류에 대한 자동 재시도 로직
                if (retryCount > 0) {
                  console.warn(`🔄 HTTP Status 0 오류 재시도 (${retryCount}회 남음)`);
                  
                  // 1초 대기 후 재시도 (빠른 재시도) - this 바인딩 보장
                  setTimeout(() => {
                    const boundXhrFetch = this.xhrFetch.bind(this);
                    boundXhrFetch(endpoint, method, data, retryCount - 1)
                      .then((result: any) => resolve(result))
                      .catch((error: any) => resolve({ success: false, error: error.message }));
                  }, 1000);
                  return;
                }
                
                resolve({ 
                  success: false, 
                  error: errorMessage,
                  troubleshooting: troubleshootingTips,
                  serverReady: this.serverReady
                });
              } else {
                console.warn(`⚠️ XHR HTTP 오류: ${xhr.status}`, xhr.responseText);
                resolve({ success: false, error: `HTTP ${xhr.status}: ${xhr.statusText}` });
              }
            }
          }
        };
        
        xhr.onerror = () => {
          console.warn('⚠️ XHR 네트워크 오류');
          console.log(`🔍 오류 발생 URL: ${url}`);
          console.log(`🔍 XHR Status: ${xhr.status}, ReadyState: ${xhr.readyState}`);
          console.log(`🔍 StatusText: ${xhr.statusText}`);
          
          // 네트워크 오류에 대한 재시도 로직
          if (retryCount > 0) {
            console.warn(`🔄 네트워크 오류 재시도 (${retryCount}회 남음)`);
            
            // 2초 대기 후 재시도 - this 바인딩 보장
            setTimeout(() => {
              const boundXhrFetch = this.xhrFetch.bind(this);
              boundXhrFetch(endpoint, method, data, retryCount - 1)
                .then((result: any) => resolve(result))
                .catch((error: any) => resolve({ success: false, error: error.message }));
            }, 2000);
            return;
          }
          
          resolve({ success: false, error: 'Network error - 서버에 연결할 수 없습니다 (서버가 시작 중이거나 네트워크 문제)' });
        };
        
        xhr.ontimeout = () => {
          console.warn('⏰ XHR 타임아웃');
          resolve({ success: false, error: 'XHR 타임아웃 - 서버 응답이 너무 늦습니다' });
        };
        
        xhr.timeout = 20000; // 20초 타임아웃 (더 안정적인 API 호출)
        
        // 요청 전송 - JSON 인코딩 문제 해결
        if (method === 'POST' || method === 'PUT') {
          const payload = data ? JSON.stringify(data, null, 0) : JSON.stringify({});
          console.log(`📤 XHR 요청 데이터:`, payload);
          
          // Content-Length 명시적 설정
          xhr.setRequestHeader('Content-Length', new Blob([payload]).size.toString());
          xhr.send(payload);
        } else {
          xhr.send();
        }
        
      } catch (error) {
        console.warn('⚠️ XHR 설정 오류:', error);
        resolve({ success: false, error: error instanceof Error ? error.message : '알 수 없는 오류' });
      }
    });
  }

  // 모델 자동 시작 확인 및 처리
  checkAndStartModel = async (modelData: any): Promise<any> => {
    try {
      if (!modelData) {
        console.log('🔍 모델 데이터 없음 - 자동 시작 건너뛰기');
        return null;
      }

      const { running = [], current_model_running = false, available = [] } = modelData;
      
      console.log('🔍 모델 자동 시작 확인:', { 
        runningCount: running.length, 
        currentModelRunning: current_model_running,
        availableCount: available.length
      });

      // 실행 중인 모델이 없거나 현재 모델이 실행되지 않은 경우
      if (running.length === 0 || !current_model_running) {
        console.log('⚠️ 실행 중인 모델이 없음 - 자동 기본 모델 시작 시도');
        
        // 기본 모델 선택 (우선순위 순)
        const defaultModels = ['gemma3-12b:latest', 'txgemma-chat:latest', 'Gemma3:27b-it-q4_K_M'];
        let selectedModel = null;
        
        for (const model of defaultModels) {
          if (available.some((m: any) => m.name === model)) {
            selectedModel = model;
            break;
          }
        }
        
        if (!selectedModel && available.length > 0) {
          selectedModel = available[0].name;
        }
        
        if (selectedModel) {
          console.log(`🚀 자동 모델 시작 시도: ${selectedModel}`);
          
          try {
            const startResult = await this.startModel(selectedModel, (progress) => {
              console.log('🔄 자동 모델 시작 진행:', progress);
            });
            
            if (startResult.success) {
              console.log('✅ 자동 모델 시작 성공:', startResult);
              
              // 업데이트된 모델 상태 다시 가져오기
              const updatedResult = await this.xhrFetch('/api/system/models/detailed');
              if (updatedResult.success) {
                console.log('✅ 모델 시작 후 상태 업데이트 완료');
                return updatedResult;
              }
            } else {
              console.warn('⚠️ 자동 모델 시작 실패:', startResult.error);
            }
          } catch (startError) {
            console.warn('⚠️ 자동 모델 시작 중 오류:', startError);
          }
        } else {
          console.warn('⚠️ 시작할 수 있는 모델을 찾을 수 없음');
        }
      } else {
        console.log('✅ 실행 중인 모델이 있음 - 자동 시작 불필요');
      }
      
      return null;
    } catch (error) {
      console.warn('⚠️ 모델 자동 시작 확인 중 오류:', error);
      return null;
    }
  }

  // 간단한 fallback fetch (타입 오류 우회)
  simpleFetch = async (endpoint: string, method: string = 'GET'): Promise<any> => {
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
        console.warn(`⚠️ SimpleFetch HTTP 오류: ${response.status}`, errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
    } catch (error) {
      console.warn('⚠️ SimpleFetch 예외:', error);
      return { success: false, error: error instanceof Error ? error.message : '알 수 없는 오류' };
    }
  }

  // 모델 상세 정보 가져오기 + 자동 모델 시작
  getModelsDetailed = async () => {
    console.log('🎯 getModelsDetailed 호출 (자동 모델 시작 포함)');
    
    // 1차: XMLHttpRequest 시도 (fetch 문제 우회)
    try {
      console.log('🥇 XHR 방식 시도');
      const xhrResult = await this.xhrFetch('/api/system/models/detailed');
      if (xhrResult.success) {
        console.log('✅ XHR 방식 성공!');
        
        // 모델 자동 시작 확인 및 처리
        const autoStartResult = await this.checkAndStartModel(xhrResult.data);
        return autoStartResult || xhrResult;
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
        
        // 모델 자동 시작 확인 및 처리
        const autoStartResult = await this.checkAndStartModel(result.data);
        return autoStartResult || result;
      }
      console.warn('⚠️ fetchWithRetry 실패, simpleFetch로 폴백');
    } catch (error) {
      console.warn('⚠️ fetchWithRetry 예외, simpleFetch로 폴백:', error);
    }
    
    // 3차: 간단한 fetch로 최종 폴백
    console.log('🥉 simpleFetch 최종 시도');
    try {
      const result = await this.simpleFetch('/api/system/models/detailed');
      if (result.success) {
        console.log('✅ simpleFetch 성공!');
        
        // 모델 자동 시작 확인 및 처리
        const autoStartResult = await this.checkAndStartModel(result.data);
        return autoStartResult || result;
      }
      return result;
    } catch (error) {
      console.warn('⚠️ simpleFetch 최종 실패:', error);
      return { success: false, error: '모든 연결 방법 실패' };
    }
  }

  // 안전한 모델 전환 (기존 모델 중지 + 새 모델 시작 + 완료 대기)
  switchModelSafely = async (modelName: string, progressCallback?: (progress: string) => void) => {
    const encodedName = encodeURIComponent(modelName);
    console.log(`🔄 안전한 모델 전환 요청: ${modelName} -> ${encodedName}`);
    
    if (progressCallback) {
      progressCallback('모델 전환 준비 중...');
    }
    
    // XHR 우선 시도 (안전한 모델 전환에 특화된 로직)
    try {
      if (progressCallback) {
        progressCallback('기존 모델 중지 중...');
      }
      
      const xhrResult = await this.xhrFetch(`/api/system/models/switch/${encodedName}`, 'POST', {});
      
      if (xhrResult.success) {
        console.log('✅ XHR 안전한 모델 전환 성공');
        if (progressCallback) {
          progressCallback('모델 전환 완료!');
        }
        return xhrResult;
      }
      console.warn('⚠️ XHR 안전한 모델 전환 실패:', xhrResult.error);
    } catch (error) {
      console.warn('⚠️ XHR 방식 예외, simpleFetch로 폴백:', error);
    }
    
    if (progressCallback) {
      progressCallback('재시도 중...');
    }
    
    console.log('🔄 simpleFetch로 안전한 모델 전환 재시도');
    const result = await this.simpleFetch(`/api/system/models/switch/${encodedName}`, 'POST');
    
    if (progressCallback) {
      progressCallback(result.success ? '모델 전환 완료!' : '전환 실패');
    }
    
    return result;
  }

  // 모델 시작 (진행률 콜백 포함)
  startModel = async (modelName: string, progressCallback?: (progress: string) => void) => {
    const encodedName = encodeURIComponent(modelName);
    console.log(`🚀 모델 시작 요청: ${modelName} -> ${encodedName}`);
    
    if (progressCallback) {
      progressCallback('모델 시작 준비 중...');
    }
    
    // XHR 우선 시도 (모델 시작에 특화된 로직)
    try {
      if (progressCallback) {
        progressCallback('기존 모델 중지 중...');
      }
      
      const xhrResult = await this.xhrFetch(`/api/system/models/${encodedName}/start`, 'POST', {});
      
      if (xhrResult.success) {
        console.log('✅ XHR 모델 시작 성공');
        if (progressCallback) {
          progressCallback('모델 시작 완료!');
        }
        return xhrResult;
      }
      console.warn('⚠️ XHR 모델 시작 실패:', xhrResult.error);
    } catch (error) {
      console.warn('⚠️ XHR 방식 예외, simpleFetch로 폴백:', error);
    }
    
    if (progressCallback) {
      progressCallback('재시도 중...');
    }
    
    console.log('🔄 simpleFetch로 모델 시작 재시도');
    const result = await this.simpleFetch(`/api/system/models/${encodedName}/start`, 'POST');
    
    if (progressCallback) {
      progressCallback(result.success ? '모델 시작 완료!' : '시작 실패');
    }
    
    return result;
  }

  // 모델 중지
  stopModel = async (modelName: string) => {
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

  // 다중 모델 시작 (향후 확장용)
  startModelMultiple = async (modelName: string) => {
    const encodedName = encodeURIComponent(modelName);
    console.log(`🚀 다중 모델 시작 요청: ${modelName} -> ${encodedName}`);
    
    // XHR 우선 시도
    try {
      const xhrResult = await this.xhrFetch(`/api/system/models/${encodedName}/start-multiple`, 'POST', {});
      if (xhrResult.success) {
        console.log('✅ XHR 다중 모델 시작 성공');
        return xhrResult;
      }
      console.warn('⚠️ XHR 다중 모델 시작 실패:', xhrResult.error);
    } catch (error) {
      console.warn('⚠️ XHR 방식 예외, simpleFetch로 폴백:', error);
    }
    
    console.log('🔄 simpleFetch로 다중 모델 시작 재시도');
    return this.simpleFetch(`/api/system/models/${encodedName}/start-multiple`, 'POST');
  }

  // 모든 모델 중지
  stopAllModels = async () => {
    console.log(`🛑 모든 모델 중지 요청`);
    
    // XHR 우선 시도
    try {
      const xhrResult = await this.xhrFetch('/api/system/models/stop-all', 'POST', {});
      if (xhrResult.success) {
        console.log('✅ XHR 모든 모델 중지 성공');
        return xhrResult;
      }
      console.warn('⚠️ XHR 모든 모델 중지 실패:', xhrResult.error);
    } catch (error) {
      console.warn('⚠️ XHR 방식 예외, simpleFetch로 폴백:', error);
    }
    
    console.log('🔄 simpleFetch로 모든 모델 중지 재시도');
    return this.simpleFetch('/api/system/models/stop-all', 'POST');
  }

  // 시스템 상태 확인
  checkHealth = async () => {
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
  // 모델 변경 (안전한 전환 사용)
  changeModel = async (modelName: string, progressCallback?: (progress: string) => void) => {
    console.log(`🔄 모델 변경 요청: ${modelName}`);
    
    if (progressCallback) {
      progressCallback('모델 변경 시작...');
    }
    
    // 안전한 모델 전환 사용
    return this.switchModelSafely(modelName, progressCallback);
  }

  safeApiCall = async (endpoint: string): Promise<any> => {
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
      console.warn('⚠️ 안전한 API 호출 예외:', error);
      return { success: false, error: error instanceof Error ? error.message : '알 수 없는 오류' };
    }
  }
}

// 싱글톤 인스턴스 생성 및 메서드 바인딩 확인
const instance = ApiClient.getInstance();

// 메서드 바인딩 검증
if (typeof instance.xhrFetch !== 'function') {
  console.error('❌ xhrFetch 메서드 바인딩 실패');
} else {
  console.log('✅ ApiClient 인스턴스 생성 완료');
}

export const apiClient = instance;