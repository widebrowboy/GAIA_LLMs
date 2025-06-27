'use client';

import React, { useState } from 'react';

export default function DebugPage() {
  const [logs, setLogs] = useState<string[]>([]);
  const [response, setResponse] = useState<string>('');
  const [isRunning, setIsRunning] = useState(false);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = `[${timestamp}] ${message}`;
    setLogs(prev => [...prev, logEntry]);
    console.log(logEntry);
  };

  // SSE 실시간 스트리밍 테스트 - 최소화/안정화 버전
  const testStreaming = async () => {
    if (isRunning) return;
    setIsRunning(true);
    setLogs([]);
    setResponse('');
    let reader: ReadableStreamDefaultReader | null = null;
    try {
      addLog('🚀 스트리밍 테스트 시작');
      const apiUrl = 'http://localhost:8000/api/chat/stream';
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive' },
        body: JSON.stringify({ message: '브라우저 디버그 테스트', session_id: 'browser_debug', complete_response: true, stream: true }),
        cache: 'no-store',
        keepalive: false
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      if (!response.body) throw new Error('응답 본문이 없습니다');
      reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let fullResponse = '';
      let partialLine = '';
      let isDone = false;
      while (!isDone) {
        const { done, value } = await reader.read();
        if (done) break;
        if (!value) continue;
        const chunk = decoder.decode(value, { stream: true });
        const lines = (partialLine + chunk).split('\n');
        partialLine = lines.pop() || '';
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              isDone = true;
              break;
            } else if (data) {
              fullResponse += data;
              setResponse(prev => prev + data);
            }
          }
        }
      }
      // 마지막 partialLine 처리
      if (partialLine && partialLine.startsWith('data: ')) {
        const data = partialLine.slice(6);
        if (data && data !== '[DONE]') {
          fullResponse += data;
          setResponse(prev => prev + data);
        }
      }
    } catch (error) {
      addLog(`❌ 오류: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      if (reader) {
        try { reader.releaseLock(); } catch {}
      }
      setIsRunning(false);
    }
  };



  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">🔧 브라우저 스트리밍 디버그</h1>
      
      <div className="space-y-4">
        <div>
          <button
            onClick={testStreaming}
            disabled={isRunning}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-6 py-2 rounded"
          >
            {isRunning ? '테스트 실행 중...' : '스트리밍 테스트 시작'}
          </button>
        </div>
        
        <div>
          <h3 className="text-lg font-semibold">📋 로그:</h3>
          <div className="bg-gray-100 p-4 rounded h-64 overflow-y-auto font-mono text-sm">
            {logs.map((log, index) => (
              <div key={index} className="mb-1">{log}</div>
            ))}
          </div>
        </div>
        
        <div>
          <h3 className="text-lg font-semibold">💬 받은 응답:</h3>
          <div className="bg-blue-50 p-4 rounded min-h-32 whitespace-pre-wrap">
            {response || '응답이 여기에 표시됩니다...'}
          </div>
        </div>
      </div>
    </div>
  );
}