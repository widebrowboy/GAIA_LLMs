'use client';

import { API_BASE_URL, getDefaultHeaders, DEFAULT_TIMEOUT } from './config';

/**
 * API 클라이언트 - 모든 API 요청의 기본 처리를 담당
 */

// 표준 에러 타입 정의
export interface ApiError {
  status?: number;
  message: string;
  details?: any;
}

// 공통 요청 옵션 타입
export interface RequestOptions {
  timeout?: number;
  signal?: AbortSignal;
  headers?: Record<string, string>;
  cache?: RequestCache;
}

/**
 * 기본 API 요청 함수
 * @param endpoint API 엔드포인트
 * @param method HTTP 메서드
 * @param body 요청 바디 데이터
 * @param options 요청 옵션
 */
export async function apiRequest<T = any>(
  endpoint: string,
  method: string = 'GET',
  body?: any,
  options: RequestOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  // 타임아웃 설정
  const controller = new AbortController();
  const { signal } = controller;
  
  const timeout = options.timeout || DEFAULT_TIMEOUT;
  const timeoutId = setTimeout(() => {
    controller.abort();
  }, timeout);
  
  try {
    const headers = {
      ...getDefaultHeaders(),
      ...(options.headers || {})
    };

    const requestOptions: RequestInit = {
      method,
      headers,
      signal: options.signal || signal,
      cache: options.cache || 'no-store',
    };

    if (body && (method !== 'GET' && method !== 'HEAD')) {
      requestOptions.body = typeof body === 'string' ? body : JSON.stringify(body);
    }

    const response = await fetch(url, requestOptions);

    clearTimeout(timeoutId);
    
    // JSON 응답 처리
    if (response.headers.get('content-type')?.includes('application/json')) {
      const data = await response.json();
      
      if (!response.ok) {
        const error: ApiError = {
          status: response.status,
          message: data.detail || data.message || `API 오류: ${response.statusText}`,
          details: data
        };
        throw error;
      }
      
      return data;
    }
    
    // 텍스트 응답 처리
    if (!response.ok) {
      const textError = await response.text();
      throw {
        status: response.status,
        message: `API 오류: ${response.statusText}`,
        details: textError
      };
    }
    
    // 성공적인 비-JSON 응답
    const result = await response.text();
    return result as unknown as T;
    
  } catch (error: any) {
    clearTimeout(timeoutId);
    
    if (error.name === 'AbortError') {
      throw {
        message: '요청 시간 초과',
        status: 408
      };
    }
    
    // 이미 형식화된 API 에러는 그대로 전달
    if (error.status && error.message) {
      throw error;
    }
    
    // 기타 오류 포맷
    throw {
      message: error.message || '알 수 없는 API 오류',
      details: error
    };
  }
}

/**
 * HTTP GET 요청
 */
export function get<T = any>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  return apiRequest<T>(endpoint, 'GET', undefined, options);
}

/**
 * HTTP POST 요청
 */
export function post<T = any>(endpoint: string, data?: any, options: RequestOptions = {}): Promise<T> {
  return apiRequest<T>(endpoint, 'POST', data, options);
}

/**
 * HTTP PUT 요청
 */
export function put<T = any>(endpoint: string, data?: any, options: RequestOptions = {}): Promise<T> {
  return apiRequest<T>(endpoint, 'PUT', data, options);
}

/**
 * HTTP DELETE 요청
 */
export function del<T = any>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  return apiRequest<T>(endpoint, 'DELETE', undefined, options);
}

/**
 * HTTP PATCH 요청
 */
export function patch<T = any>(endpoint: string, data?: any, options: RequestOptions = {}): Promise<T> {
  return apiRequest<T>(endpoint, 'PATCH', data, options);
}

/**
 * 스트리밍 응답 처리 도우미
 * @param response 스트리밍 응답
 * @param onChunk 청크 데이터 처리 콜백
 */
export async function handleStreamingResponse(
  response: Response,
  onChunk: (chunk: string) => void
): Promise<void> {
  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('스트리밍 응답을 처리할 수 없습니다');
  }

  const decoder = new TextDecoder('utf-8');
  let done = false;
  let buffer = '';
  let lastChunk = '';
  // 누적 텍스트 - 줄바꿈 또는 문장 경계가 확인될 때만 onChunk 호출
  let accumulated = '';

  try {
    while (!done) {
      const { value, done: doneReading } = await reader.read();
      done = doneReading;

      if (done) break;
      
      if (value) {
        // UTF-8 디코딩을 명시적으로 설정
        const chunk = decoder.decode(value, { stream: true });
        
        // SSE 형식 처리 (data: 프리픽스 제거)
        const lines = (buffer + chunk).split('\n');
        buffer = lines.pop() || ''; // 마지막 줄은 불완전할 수 있으므로 버퍼에 보관
        
        for (const line of lines) {
          const trimmedLine = line.trim();
          if (trimmedLine === '') continue; // 빈 줄 건너뛰기
          
          if (line.startsWith('data: ')) {
            // SSE 형식: 'data: ' 접두사 제거 후 콜백 호출
            const content = line.substring(6); // 'data: ' 길이가 6
            if (content === '[DONE]') {
              // 특별 종료 신호는 처리하지 않음
              console.log('SSE [DONE] 신호 수신');
              continue;
            }
            // 실제 내용을 처리 – 토큰을 누적하고 경계 조건이 만족될 때만 전달
            accumulated += content;
            lastChunk = content;
            // 헤딩·문단 등 마크다운 경계(\n) 또는 문장 종결부호(., ?, !) 뒤 공백/줄바꿈이 있을 때 렌더링
            if (/\n$/.test(content) || /[.!?]\s*$/.test(content)) {
              onChunk(accumulated);
            }
          } else if (trimmedLine.startsWith('{') && trimmedLine.endsWith('}')) {
            // JSON 객체 형식: 딥리서치 모드에서 자주 사용됨
            try {
              const jsonObj = JSON.parse(trimmedLine);
              
              // 딥리서치 모드의 JSON 응답에서 콘텐츠 추출 우선순위 개선
              // 1. content 필드 (주로 딥리서치 모드에서 사용)
              // 2. response 필드 (일부 응답에서 사용)
              // 3. text 필드 (일반 텍스트)
              // 4. 전체 JSON 객체 문자열 (마지막 수단)
              const content = jsonObj.content || jsonObj.response || jsonObj.text || JSON.stringify(jsonObj);
              
              if (content && typeof content === 'string') {
                accumulated += content;
                lastChunk = content;
                
                // 마크다운 헤더(#, ##), 코드 블록(```), 목록 항목(-,*,1.) 등 마크다운 구조 요소를 경계로 인식
                if (/\n$/.test(content) || /[.!?]\s*$/.test(content) || 
                    /^#+\s|^[-*]\s|^\d+\.\s|^```/.test(content)) {
                  onChunk(accumulated);
                }
              }
              
              // 메타데이터가 있는 경우 로깅 (디버깅 목적)
              if (jsonObj.metadata) {
                console.log('스트리밍 응답 메타데이터:', jsonObj.metadata);
              }
            } catch (_error) {
              // JSON 파싱 실패 시 원본 텍스트 전달
              console.warn('JSON 파싱 실패, 원본 텍스트 누적 전달:', _error);
              accumulated += trimmedLine;
              lastChunk = trimmedLine;
              if (/\n$/.test(trimmedLine) || /[.!?]\s*$/.test(trimmedLine)) {
                onChunk(accumulated);
              }
            }
          } else {
            // 일반 텍스트 형식 - 마크다운 누락 방지를 위해 누적 처리
            accumulated += trimmedLine;
            lastChunk = trimmedLine;
            
            // 마크다운 구조 요소를 포함한 경계 조건 확인
            if (/\n$/.test(trimmedLine) || /[.!?]\s*$/.test(trimmedLine) || 
                /^#+\s|^[-*]\s|^\d+\.\s|^```/.test(trimmedLine)) {
              onChunk(accumulated);
            }
          }
        }
      }
    }
    
    // 마지막 버퍼 처리 - 잘린 응답의 마지막 부분을 처리
    if (buffer.trim() !== '') {
      const trimmedBuffer = buffer.trim();
      
      if (buffer.startsWith('data: ')) {
        const content = buffer.substring(6);
        if (content !== '[DONE]') {
          lastChunk = content;
          onChunk(content);
        }
      } else if (trimmedBuffer.startsWith('{') && trimmedBuffer.endsWith('}')) {
        // JSON 객체 처리 - 마지막 버퍼에 있는 JSON도 동일한 우선순위와 경계 조건으로 처리
        try {
          const jsonObj = JSON.parse(trimmedBuffer);
          const content = jsonObj.content || jsonObj.response || jsonObj.text || JSON.stringify(jsonObj);
          if (content && typeof content === 'string') {
            accumulated += content;
            lastChunk = content;
            // 마지막 버퍼의 경우 누적된 내용 전송 (경계 조건 체크 없이)
            onChunk(accumulated);
          }
        } catch (_error) {
          // JSON 파싱 실패 시 원본 텍스트 누적 전달
          accumulated += trimmedBuffer;
          lastChunk = trimmedBuffer;
          onChunk(accumulated);
        }
      } else {
        // 일반 텍스트
        accumulated += trimmedBuffer;
        lastChunk = trimmedBuffer;
        if (/\n$/.test(trimmedBuffer) || /[.!?]\s*$/.test(trimmedBuffer)) {
          onChunk(accumulated);
        }
      }
    }
    
    // 루프 종료 후 남은 누적 텍스트가 있으면 한 번 더 전달
    if (accumulated.trim().length > 0) {
      onChunk(accumulated);
    }
    // 최종 종료 신호 처리
    console.log('스트리밍 처리 완료, 최종 청크 길이:', lastChunk.length);
  } catch (error) {
    console.error('스트리밍 처리 중 오류:', error);
    throw error;
  }
}

/**
 * 스트리밍 요청 - 서버 전송 이벤트(SSE)나 청크 응답 처리
 */
export async function streamRequest(
  endpoint: string,
  body: any,
  onChunk: (chunk: string) => void,
  options: RequestOptions = {}
): Promise<void> {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  // 딥리서치 모드에서는 응답 타임아웃 늘리기 (모델 로딩 및 처리 시간 고려)
  
  
  // 딥리서치 모드와 일반 모드에 따라 요청 옵션 최적화
  const isDeepResearchMode = body?.mode === 'deep_research';
  
  const requestOptions: RequestInit = {
    method: 'POST',
    headers: {
      ...getDefaultHeaders(),
      'Content-Type': 'application/json; charset=utf-8',
      // 딥리서치 모드에서는 더 명확한 Accept 헤더 설정
      'Accept': isDeepResearchMode 
        ? 'text/event-stream, application/json, text/markdown, text/plain; charset=utf-8'
        : 'text/event-stream, application/json, text/plain; charset=utf-8',
      // 마크다운 응답 크기가 클 수 있으므로 압축 지원
      'Accept-Encoding': 'gzip, deflate, br',
      ...(options.headers || {})
    },
    signal: options.signal,
    // 딥리서치 모드에서 필요한 추가 파라미터 설정
    body: typeof body === 'string' ? body : JSON.stringify({
      ...body,
      // 딥리서치 모드에서 최적화된 파라미터 전달
      ...(isDeepResearchMode && {
        stream: true,
        raw: true,  // 원본 출력 유지
        format: 'json',  // JSON 형식으로 응답 요청
      })
    })
  };
  
  console.log(`스트리밍 요청 시작: ${endpoint}`);
  const response = await fetch(url, requestOptions);
  
  if (!response.ok) {
    let errorText = '';
    try {
      const errorData = await response.json();
      errorText = errorData.detail || errorData.message || response.statusText;
    } catch {
      errorText = await response.text() || response.statusText;
    }
    
    throw {
      status: response.status,
      message: `API 스트리밍 오류: ${errorText}`
    };
  }
  
  // Content-Type 확인 및 로깅
  const contentType = response.headers.get('Content-Type') || 'unknown';
  console.log(`스트리밍 응답 Content-Type: ${contentType}`);
  
  await handleStreamingResponse(response, onChunk);
  console.log('스트리밍 요청 완료됨');
}
