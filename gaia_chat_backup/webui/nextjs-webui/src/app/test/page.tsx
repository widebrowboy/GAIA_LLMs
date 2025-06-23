'use client';

import { useState } from 'react';

export default function TestPage() {
  const [mode, setMode] = useState<'normal' | 'deep_research'>('normal');
  const [promptType, setPromptType] = useState<'default' | 'clinical' | 'research' | 'chemistry' | 'regulatory'>('default');

  const getModeColor = (currentMode: string) => {
    return currentMode === 'deep_research' 
      ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white' 
      : 'bg-gradient-to-r from-green-500 to-teal-500 text-white';
  };

  const getPromptColor = (type: string) => {
    switch (type) {
      case 'clinical': return 'bg-gradient-to-r from-purple-400 to-pink-400';
      case 'research': return 'bg-gradient-to-r from-blue-400 to-cyan-400';
      case 'chemistry': return 'bg-gradient-to-r from-green-400 to-emerald-400';
      case 'regulatory': return 'bg-gradient-to-r from-red-400 to-orange-400';
      default: return 'bg-gradient-to-r from-gray-400 to-slate-400';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-8">
      {/* 헤더 */}
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="flex items-center space-x-4 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-full flex items-center justify-center">
              <span className="text-2xl text-white">🧬</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">GAIA-BT WebUI Test</h1>
              <p className="text-gray-600">신약개발 AI 연구 어시스턴트 테스트 페이지</p>
            </div>
          </div>
          
          {/* 상태 표시 */}
          <div className="flex space-x-4">
            <div className={`px-4 py-2 rounded-lg ${getModeColor(mode)}`}>
              {mode === 'normal' ? '일반 모드' : 'Deep Research 모드'}
            </div>
            <div className={`px-4 py-2 rounded-lg text-white ${getPromptColor(promptType)}`}>
              {promptType === 'default' ? '기본' :
               promptType === 'clinical' ? '임상시험' :
               promptType === 'research' ? '연구분석' :
               promptType === 'chemistry' ? '의약화학' : '규제'}
            </div>
          </div>
        </div>

        {/* 컨트롤 패널 */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-lg font-semibold mb-4">🎛️ 컨트롤 패널</h2>
          
          {/* 모드 선택 */}
          <div className="mb-6">
            <h3 className="font-medium mb-2">모드 선택</h3>
            <div className="flex space-x-2">
              <button
                onClick={() => setMode('normal')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  mode === 'normal' 
                    ? 'bg-green-500 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                일반 모드
              </button>
              <button
                onClick={() => setMode('deep_research')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  mode === 'deep_research' 
                    ? 'bg-purple-500 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                🔬 Deep Research 모드
              </button>
            </div>
          </div>

          {/* 프롬프트 타입 선택 */}
          <div className="mb-6">
            <h3 className="font-medium mb-2">프롬프트 타입</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
              {[
                { value: 'default', label: '기본', icon: '⚙️' },
                { value: 'clinical', label: '임상시험', icon: '🏥' },
                { value: 'research', label: '연구분석', icon: '📊' },
                { value: 'chemistry', label: '의약화학', icon: '⚗️' },
                { value: 'regulatory', label: '규제', icon: '📋' },
              ].map((type) => (
                <button
                  key={type.value}
                  onClick={() => setPromptType(type.value as any)}
                  className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                    promptType === type.value
                      ? `${getPromptColor(type.value)} text-white`
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {type.icon} {type.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Mock 채팅 인터페이스 */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-semibold mb-4">💬 채팅 미리보기</h2>
          
          <div className="space-y-4">
            {/* 사용자 메시지 */}
            <div className="flex justify-end">
              <div className="bg-blue-500 text-white px-4 py-2 rounded-lg max-w-xs">
                아스피린의 작용 메커니즘을 설명해주세요
              </div>
            </div>

            {/* AI 응답 */}
            <div className="flex justify-start">
              <div className={`px-4 py-3 rounded-lg max-w-md ${
                mode === 'deep_research' 
                  ? 'bg-gradient-to-r from-purple-100 to-blue-100 border-l-4 border-purple-500' 
                  : 'bg-gray-100'
              }`}>
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-lg">🤖</span>
                  <span className="font-medium">GAIA-BT</span>
                  {mode === 'deep_research' && (
                    <span className="bg-purple-500 text-white text-xs px-2 py-1 rounded">
                      🔬 Deep Research
                    </span>
                  )}
                </div>
                
                <p className="text-sm text-gray-700">
                  {mode === 'deep_research' 
                    ? `🔍 다중 데이터베이스 검색 결과를 바탕으로 답변드립니다...\n\n아스피린(아세틸살리실산)은 COX-1과 COX-2 효소를 비가역적으로 억제하여 프로스타글란딘 합성을 차단합니다. 최근 연구에 따르면...`
                    : `아스피린은 cyclooxygenase(COX) 효소를 억제하여 염증과 통증을 감소시킵니다.`
                  }
                </p>

                {mode === 'deep_research' && (
                  <div className="mt-3 pt-2 border-t border-purple-200">
                    <div className="text-xs text-gray-600">
                      <strong>검색 소스:</strong> PubMed(15), ChEMBL(8), ClinicalTrials(3)
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 입력 영역 */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex space-x-2">
              <input
                type="text"
                placeholder={
                  mode === 'deep_research' 
                    ? "신약개발 질문을 입력하세요... (Deep Research 모드 활성화됨)"
                    : "신약개발 질문을 입력하세요..."
                }
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                전송
              </button>
            </div>
            <div className="text-xs text-gray-500 mt-2">
              {mode === 'deep_research' 
                ? "🔬 Deep Research 모드: 다중 데이터베이스 검색이 활성화됩니다"
                : "일반 모드: 기본 AI 응답을 제공합니다"
              }
            </div>
          </div>
        </div>

        {/* API 테스트 */}
        <div className="bg-white rounded-lg shadow-lg p-6 mt-8">
          <h2 className="text-lg font-semibold mb-4">🔗 API 연결 테스트</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <h3 className="font-medium text-green-800 mb-2">✅ Backend API</h3>
              <p className="text-sm text-green-700">http://localhost:8000 - 정상 연결</p>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h3 className="font-medium text-blue-800 mb-2">✅ Frontend</h3>
              <p className="text-sm text-blue-700">http://localhost:3000 - 정상 작동</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}