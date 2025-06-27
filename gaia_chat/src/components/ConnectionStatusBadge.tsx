'use client';

import React, { useState, useEffect, useRef } from 'react';

interface ConnectionStatus {
  server_healthy: boolean;
  model_ready: boolean;
  ollama_models: string[];
  current_model: string | null;
  mode: string;
  mcp_enabled: boolean;
  connected_sessions: number;
  test_result: {
    success: boolean;
    error?: string;
    response_length: number;
  };
  error?: string;
}

interface ConnectionStatusBadgeProps {
  onConnectionChange?: (connected: boolean) => void;
}

export default function ConnectionStatusBadge({ onConnectionChange }: ConnectionStatusBadgeProps) {
  const [isConnected, setIsConnected] = useState(true); // 초기값을 true로 설정
  const [status, setStatus] = useState<ConnectionStatus | null>(null);
  const [isReconnecting, setIsReconnecting] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const maxReconnectAttempts = 10;
  const reconnectDelay = 3000; // 3초
  const [hasReceivedStatus, setHasReceivedStatus] = useState(false);

  const connect = () => {
    // 기존 연결이 있으면 먼저 정리
    if (wsRef.current) {
      try {
        if (wsRef.current.readyState === WebSocket.OPEN || 
            wsRef.current.readyState === WebSocket.CONNECTING) {
          wsRef.current.close();
        }
      } catch (err) {
        console.log('이전 WebSocket 연결 정리 중 오류:', err);
      }
      wsRef.current = null;
    }

    const sessionId = `status_${Date.now()}`;
    const wsUrl = `ws://localhost:8000/ws/status/${sessionId}`;
    
    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('Status WebSocket 연결 성공');
        setIsReconnecting(false);
        setReconnectAttempts(0);
        // WebSocket 연결 성공 시 초기 연결 상태는 true로 유지
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'status_update') {
            setStatus(data);
            setHasReceivedStatus(true);
            
            // model_ready 상태를 기준으로 연결 상태 설정
            const modelReady = data.model_ready && data.server_healthy;
            
            console.log('Status 업데이트:', {
              server_healthy: data.server_healthy,
              model_ready: data.model_ready,
              test_success: data.test_result?.success,
              final_connected: modelReady
            });
            
            setIsConnected(modelReady);
            onConnectionChange?.(modelReady);
          }
        } catch (error) {
          console.error('Status message parsing error:', error);
        }
      };

      ws.onclose = () => {
        console.log('Status WebSocket 연결 해제');
        setIsConnected(false);
        setStatus(null);
        onConnectionChange?.(false);
        
        // 자동 재연결 로직
        if (reconnectAttempts < maxReconnectAttempts && !isReconnecting) {
          setIsReconnecting(true);
          setReconnectAttempts(prev => prev + 1);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`재연결 시도 ${reconnectAttempts + 1}/${maxReconnectAttempts}`);
            connect();
          }, reconnectDelay);
        }
      };

      ws.onerror = (_event) => {
        // WebSocket 에러는 보안상의 이유로 상세 정보를 제공하지 않음
        // 대신 일반적인 메시지와 연결 상태만 기록
        console.error('Status WebSocket 연결 오류 발생. 서버가 실행 중인지 확인하세요.');
        setIsConnected(false);
        setStatus(null);
        onConnectionChange?.(false);
        
        // 자동 재연결 로직 추가 (onclose와 유사하게)
        if (reconnectAttempts < maxReconnectAttempts && !isReconnecting) {
          setIsReconnecting(true);
          setReconnectAttempts(prev => prev + 1);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`WebSocket 오류 후 재연결 시도 ${reconnectAttempts + 1}/${maxReconnectAttempts}`);
            connect();
          }, reconnectDelay);
        }
      };

    } catch (error) {
      console.error('WebSocket 연결 실패:', error);
      setIsConnected(false);
      onConnectionChange?.(false);
    }
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
    setIsReconnecting(false);
    setStatus(null);
    setReconnectAttempts(0);
  };

  const manualReconnect = () => {
    disconnect();
    setReconnectAttempts(0);
    setTimeout(connect, 500);
  };

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect]);

  const getStatusColor = () => {
    if (isReconnecting) return 'bg-yellow-500';
    if (!isConnected) return 'bg-red-500';
    if (!status?.server_healthy) return 'bg-red-500';
    if (!status?.model_ready) return 'bg-orange-500';
    return 'bg-green-500';
  };

  const getStatusText = () => {
    if (isReconnecting) return `재연결 중... (${reconnectAttempts}/${maxReconnectAttempts})`;
    if (!hasReceivedStatus) return '상태 확인 중...';
    if (!status?.server_healthy) return '서버 오류';
    if (!status?.model_ready) {
      const error = status?.test_result?.error;
      if (error?.includes('timeout')) return 'AI 모델 응답 지연';
      if (error?.includes('Empty')) return 'AI 모델 응답 없음';
      return 'AI 모델 준비 중';
    }
    return '연결됨';
  };

  const getModelInfo = () => {
    if (!status?.current_model) return '';
    return status.current_model;
  };

  const getModeInfo = () => {
    if (!status) return '';
    const mode = status.mode === 'mcp' ? 'Deep Research' : '일반 모드';
    return mode;
  };

  return (
    <div className="flex items-center space-x-2 text-sm">
      {/* 연결 상태 표시 */}
      <div className="flex items-center space-x-2">
        <div className={`w-2 h-2 rounded-full ${getStatusColor()} ${isConnected ? 'animate-pulse' : ''}`}></div>
        <span className="text-gray-600 dark:text-gray-300">{getStatusText()}</span>
      </div>

      {/* 모델 정보 */}
      {isConnected && status?.current_model && (
        <div className="flex items-center space-x-1 text-xs text-gray-500 dark:text-gray-400">
          <span>•</span>
          <span>{getModelInfo()}</span>
        </div>
      )}

      {/* 모드 정보 */}
      {isConnected && status && (
        <div className="flex items-center space-x-1 text-xs text-gray-500 dark:text-gray-400">
          <span>•</span>
          <span>{getModeInfo()}</span>
        </div>
      )}

      {/* 수동 재연결 버튼 */}
      {!isConnected && !isReconnecting && (
        <button
          onClick={manualReconnect}
          className="text-xs px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          재연결
        </button>
      )}

      {/* 상세 정보 (개발 모드) */}
      {process.env.NODE_ENV === 'development' && status && (
        <div className="text-xs text-gray-400 ml-2">
          Sessions: {status.connected_sessions}
        </div>
      )}
    </div>
  );
}