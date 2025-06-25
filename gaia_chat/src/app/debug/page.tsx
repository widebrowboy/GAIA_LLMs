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

  const testStreaming = async () => {
    if (isRunning) return;
    
    setIsRunning(true);
    setLogs([]);
    setResponse('');
    
    try {
      addLog('🚀 브라우저 스트리밍 테스트 시작');
      
      const apiUrl = 'http://localhost:8000/api/chat/stream';
      addLog(`🌐 API URL: ${apiUrl}`);
      
      addLog('📡 fetch() 호출 중...');
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: '브라우저 디버그 테스트',
          session_id: 'browser_debug'
        })
      });
      
      addLog(`📋 응답 수신: ${response.status} ${response.statusText}`);
      addLog(`📋 Content-Type: ${response.headers.get('content-type')}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      if (!response.body) {
        throw new Error('응답 본문이 없습니다');
      }
      
      addLog('✅ ReadableStream 확인됨');
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      let fullResponse = '';
      let chunkCount = 0;
      
      addLog('🔄 스트리밍 읽기 시작');
      
      while (true) {
        addLog(`📖 reader.read() 호출 중... (청크 ${chunkCount + 1})`);
        
        const { done, value } = await reader.read();
        
        addLog(`📋 Read 결과: done=${done}, valueExists=${!!value}, valueLength=${value ? value.length : 0}`);
        
        if (done) {
          addLog('🏁 스트리밍 완료 (연결 종료)');
          break;
        }
        
        if (!value) {
          addLog('⚠️ value가 없음, 다음 청크 대기');
          continue;
        }
        
        chunkCount++;
        const chunk = decoder.decode(value, { stream: true });
        
        addLog(`📥 청크 ${chunkCount} 수신: "${chunk.substring(0, 30)}..."`);
        
        // SSE 파싱
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.trim() && line.startsWith('data: ')) {
            const data = line.slice(6);
            
            if (data === '[DONE]') {
              addLog('🏁 스트리밍 종료 신호 수신');
              reader.releaseLock();
              addLog(`✅ 최종 응답 길이: ${fullResponse.length}자`);
              setIsRunning(false);
              return;
            } else {
              fullResponse += data;
              setResponse(fullResponse);
              addLog(`📝 응답 업데이트: +${data.length}자 (총 ${fullResponse.length}자)`);
            }
          }
        }
      }
      
      reader.releaseLock();
      addLog(`✅ 스트리밍 완료 - 총 ${fullResponse.length}자 수신`);
      
    } catch (error) {
      addLog(`❌ 오류: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
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