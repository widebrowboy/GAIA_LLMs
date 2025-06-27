'use client';

import { post, streamRequest } from './client';
import { Conversation } from '@/types/chat';

/**
 * 채팅 관련 API 요청 모듈
 */

/**
 * 메시지 전송 요청 인터페이스
 */
export interface SendMessageRequest {
  message: string;
  conversation_id?: string;
  session_id: string;
  history?: Array<{ role: string, content: string }>;
}

/**
 * 메시지 전송 응답 인터페이스
 */
export interface SendMessageResponse {
  response: string;
  conversation_id: string;
}

/**
 * 대화 생성 요청 인터페이스
 */
export interface CreateConversationRequest {
  title?: string;
  session_id: string;
}

/**
 * 대화 생성 응답 인터페이스
 */
export interface CreateConversationResponse {
  conversation_id: string;
  title: string;
  created_at: string;
}

/**
 * 대화 목록 요청 인터페이스
 */
export interface FetchConversationsRequest {
  session_id: string;
  limit?: number;
  offset?: number;
}

/**
 * 메시지 전송 (일반)
 */
export async function sendMessage(
  data: SendMessageRequest
): Promise<SendMessageResponse> {
  return await post<SendMessageResponse>('/api/chat/message', data);
}

/**
 * 메시지 전송 (스트리밍)
 */
export async function sendStreamingMessage(
  data: SendMessageRequest,
  onChunk: (chunk: string) => void,
  signal?: AbortSignal
): Promise<void> {
  return await streamRequest(
    '/api/chat/stream',
    data,
    onChunk,
    { signal }
  );
}

/**
 * 대화 생성
 */
export async function createConversation(
  data: CreateConversationRequest
): Promise<CreateConversationResponse> {
  return await post<CreateConversationResponse>('/api/chat/conversation', data);
}

/**
 * 대화 목록 조회
 */
export async function getConversations(
  data: FetchConversationsRequest
): Promise<Conversation[]> {
  return await post<Conversation[]>('/api/chat/conversations', data);
}

/**
 * 대화 삭제
 */
export async function deleteConversation(
  conversationId: string,
  sessionId: string
): Promise<{ success: boolean }> {
  return await post<{ success: boolean }>(`/api/chat/conversation/${conversationId}/delete`, {
    session_id: sessionId
  });
}

/**
 * 대화 제목 업데이트
 */
export async function updateConversationTitle(
  conversationId: string,
  title: string,
  sessionId: string
): Promise<{ success: boolean }> {
  return await post<{ success: boolean }>(`/api/chat/conversation/${conversationId}/title`, {
    title,
    session_id: sessionId
  });
}

/**
 * 대화 세부 정보 조회
 */
export async function getConversationDetails(
  conversationId: string,
  sessionId: string
): Promise<Conversation> {
  return await post<Conversation>(`/api/chat/conversation/${conversationId}`, {
    session_id: sessionId
  });
}
