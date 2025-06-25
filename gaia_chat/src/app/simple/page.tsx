'use client';

import React, { useState } from 'react';

export default function SimplePage() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = 'http://localhost:8000';

  const handleSendMessage = async () => {
    if (!message.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);
    setResponse('');

    try {
      console.log('📡 API 호출:', `${API_BASE_URL}/api/chat/message`);
      
      const res = await fetch(`${API_BASE_URL}/api/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: 'simple-session-' + Date.now()
        })
      });

      console.log('📡 응답 상태:', res.status);

      if (res.ok) {
        const data = await res.json();
        setResponse(data.response || '응답이 없습니다.');
        console.log('✅ API 호출 성공');
      } else {
        throw new Error(`API 오류: ${res.status} ${res.statusText}`);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      console.error('❌ API 호출 실패:', errorMsg);
      setError(`API 호출 실패: ${errorMsg}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            🧬 GAIA-BT 간단 테스트
          </h1>
          <p className="text-gray-600">
            신약개발 AI 어시스턴트 - 직접 API 호출 테스트
          </p>
          <div className="mt-4 text-sm text-gray-500">
            <p><strong>API URL:</strong> {API_BASE_URL}</p>
            <p><strong>엔드포인트:</strong> /api/chat/message</p>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          {/* Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              메시지를 입력하세요:
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="예: 아스피린의 작용 메커니즘은?"
                className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !message.trim()}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? '전송 중...' : '전송'}
              </button>
            </div>
          </div>

          {/* Quick Test Buttons */}
          <div className="mb-6">
            <p className="text-sm text-gray-600 mb-2">빠른 테스트:</p>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setMessage('아스피린의 작용 메커니즘을 설명해주세요')}
                className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
              >
                💊 아스피린 메커니즘
              </button>
              <button
                onClick={() => setMessage('임상시험 1상과 2상의 차이점은?')}
                className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
              >
                🏥 임상시험 차이
              </button>
              <button
                onClick={() => setMessage('신약개발 과정을 간단히 설명해주세요')}
                className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
              >
                🔬 신약개발 과정
              </button>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <h3 className="font-medium text-red-800 mb-2">❌ 오류 발생</h3>
              <p className="text-red-700 text-sm">{error}</p>
              <div className="mt-2 text-xs text-red-600">
                <p><strong>해결 방법:</strong></p>
                <ul className="list-disc list-inside mt-1">
                  <li>API 서버가 실행 중인지 확인: <code>curl {API_BASE_URL}/health</code></li>
                  <li>브라우저에서 직접 테스트: <a href={`${API_BASE_URL}/docs`} target="_blank" className="underline">{API_BASE_URL}/docs</a></li>
                  <li>서버 재시작: <code>./scripts/server_manager.sh restart</code></li>
                </ul>
              </div>
            </div>
          )}

          {/* Response Display */}
          {response && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <h3 className="font-medium text-green-800 mb-2">✅ 응답</h3>
              <div className="text-green-700 whitespace-pre-wrap">{response}</div>
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                <span className="text-blue-700">AI가 응답을 생성하고 있습니다...</span>
              </div>
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="font-medium text-yellow-800 mb-2">📝 사용 방법</h3>
          <ul className="text-yellow-700 text-sm space-y-1">
            <li>1. 위의 입력창에 신약개발 관련 질문을 입력하세요</li>
            <li>2. 전송 버튼을 클릭하거나 Enter 키를 누르세요</li>
            <li>3. API 서버가 정상 작동하면 AI 응답이 표시됩니다</li>
            <li>4. 오류가 발생하면 상세한 해결 방법이 표시됩니다</li>
          </ul>
        </div>
      </div>
    </div>
  );
}