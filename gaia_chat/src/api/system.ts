'use client';

import { get, post } from './client';

/**
 * 시스템 관련 API 요청 모듈
 */

/**
 * 시스템 정보 응답 인터페이스
 */
export interface SystemInfoResponse {
  version: string;
  available_models: string[];
  current_model: string;
  current_mode: string;
  mcp_enabled: boolean;
  current_prompt_type: string;
}

/**
 * 모드 변경 요청 인터페이스
 */
export interface ChangeModeRequest {
  session_id: string;
}

/**
 * 모델 변경 요청 인터페이스
 */
export interface ChangeModelRequest {
  model: string;
  session_id: string;
}

/**
 * 프롬프트 변경 요청 인터페이스
 */
export interface ChangePromptRequest {
  prompt_type: string;
  session_id: string;
}

/**
 * 시스템 정보 조회
 */
export async function getSystemInfo(): Promise<SystemInfoResponse> {
  return await get<SystemInfoResponse>('/api/system/info');
}

/**
 * 시스템 상태 확인 (헬스 체크)
 */
export async function checkSystemHealth(timeout = 3000): Promise<boolean> {
  try {
    await get<{ status: string }>('/health', { timeout });
    return true;
  } catch (error) {
    console.error('API 상태 체크 실패:', error);
    return false;
  }
}

/**
 * 모드 변경
 */
export async function changeMode(
  mode: string,
  sessionId: string
): Promise<{ success: boolean }> {
  return await post<{ success: boolean }>(`/api/system/mode/${mode}`, {
    session_id: sessionId
  });
}

/**
 * 모델 변경
 */
export async function changeModel(
  model: string,
  sessionId: string
): Promise<{ success: boolean }> {
  return await post<{ success: boolean }>('/api/system/model', {
    model,
    session_id: sessionId
  });
}

/**
 * 프롬프트 타입 변경
 */
export async function changePrompt(
  promptType: string,
  sessionId: string
): Promise<{ success: boolean }> {
  return await post<{ success: boolean }>('/api/system/prompt', {
    prompt_type: promptType,
    session_id: sessionId
  });
}

/**
 * MCP 출력 표시 설정 변경
 */
export async function toggleMcpOutput(
  showMcpOutput: boolean,
  sessionId: string
): Promise<{ success: boolean }> {
  return await post<{ success: boolean }>('/api/system/mcp_output', {
    show_mcp_output: showMcpOutput,
    session_id: sessionId
  });
}
