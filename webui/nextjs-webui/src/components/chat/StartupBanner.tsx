'use client';

import { useState, useEffect } from 'react';
import { X, Beaker, Target, Heart, Sparkles, Zap, Globe, Activity, Users, ArrowRight, Play, Cpu, Database, Brain } from 'lucide-react';
import { Card } from '@/components/ui/Card';

interface StartupBannerProps {
  onClose: () => void;
}

export function StartupBanner({ onClose }: StartupBannerProps) {
  const [currentModel, setCurrentModel] = useState('gemma3:latest');
  const [currentPrompt, setCurrentPrompt] = useState('default (신약개발 전문 AI 어시스턴트)');
  const [isVisible, setIsVisible] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const initSteps = [
    "AI 모델 로딩 중...",
    "MCP 서버 연결 중...",
    "데이터베이스 초기화 중...",
    "시스템 준비 완료!"
  ];

  useEffect(() => {
    // API에서 현재 설정 가져오기
    const fetchSettings = async () => {
      try {
        // GAIA-BT API를 통해 시스템 정보 가져오기
        const response = await fetch('/api/gaia-bt', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            type: 'status'
          })
        });
        
        const data = await response.json();
        
        if (data.success && data.status) {
          setCurrentModel(data.status.model || 'gemma3:latest');
          const promptType = data.status.prompt_type || 'default';
          const promptDesc = data.status.prompt_description || '신약개발 전문 AI 어시스턴트';
          setCurrentPrompt(`${promptType} (${promptDesc})`);
        } else {
          // 기본값 설정
          setCurrentModel('gemma3:latest');
          setCurrentPrompt('default (신약개발 전문 AI 어시스턴트)');
        }
      } catch (error) {
        console.error('Failed to fetch settings:', error);
        // 에러 시 기본값 설정
        setCurrentModel('gemma3:latest');
        setCurrentPrompt('default (신약개발 전문 AI 어시스턴트)');
      }
    };

    fetchSettings();
    setIsVisible(true);

    // 초기화 단계 애니메이션
    const interval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < initSteps.length - 1) {
          return prev + 1;
        }
        clearInterval(interval);
        return prev;
      });
    }, 800);

    return () => clearInterval(interval);
  }, []);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 300);
  };

  return (
    <div className={`fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4 transition-opacity duration-500 ${isVisible ? 'opacity-100' : 'opacity-0'}`}>
      <Card className={`w-full max-w-6xl bg-slate-900/95 backdrop-blur-xl border border-blue-500/20 shadow-2xl transform transition-all duration-500 ${isVisible ? 'scale-100' : 'scale-95'} relative overflow-hidden`}>
        {/* 헤더 라인 */}
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-cyan-500"></div>
        
        {/* 닫기 버튼 */}
        <button
          onClick={handleClose}
          className="absolute top-6 right-6 w-12 h-12 bg-white/5 hover:bg-white/10 border border-white/20 rounded-full flex items-center justify-center transition-all duration-300 backdrop-blur-sm group z-20"
        >
          <X className="w-5 h-5 text-white group-hover:rotate-90 transition-transform duration-300" />
        </button>

        <div className="relative p-8 space-y-8 text-white">
          {/* 헤더 섹션 */}
          <div className="text-center space-y-6">
            {/* 로고 및 브랜딩 */}
            <div className="flex items-center justify-center gap-6">
              <div className="relative group">
                {/* GAIA-BT 로고 */}
                <div className="w-24 h-24 bg-gradient-to-br from-blue-500 via-purple-500 to-cyan-500 rounded-2xl flex items-center justify-center relative overflow-hidden shadow-2xl">

                  <div className="relative z-10 text-white">
                    <svg viewBox="0 0 40 40" className="w-12 h-12">
                      {/* DNA 구조 로고 */}
                      <path d="M8,20 Q20,8 32,20 Q20,32 8,20" stroke="currentColor" strokeWidth="2" fill="none" />
                      <path d="M8,20 Q20,32 32,20 Q20,8 8,20" stroke="currentColor" strokeWidth="2" fill="none" />
                      <circle cx="20" cy="20" r="3" fill="currentColor" />
                      <circle cx="12" cy="14" r="1.5" fill="currentColor" />
                      <circle cx="28" cy="14" r="1.5" fill="currentColor" />
                      <circle cx="12" cy="26" r="1.5" fill="currentColor" />
                      <circle cx="28" cy="26" r="1.5" fill="currentColor" />
                    </svg>
                  </div>
                  
                  {/* 상태 인디케이터 */}
                  <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center animate-pulse shadow-lg">
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  </div>
                </div>
              </div>
              
              {/* 브랜드 텍스트 */}
              <div className="text-left space-y-2">
                <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-300 via-purple-300 to-cyan-300 bg-clip-text text-transparent tracking-tight">
                  GAIA-BT
                </h1>
                <p className="text-xl text-blue-200/80 font-light">AI-Powered Drug Discovery Platform</p>
                <p className="text-lg text-blue-300/60">신약개발 연구 AI 어시스턴트 v2.0 Alpha</p>
              </div>
            </div>

            {/* 핵심 기능 태그 */}
            <div className="flex items-center justify-center gap-4 flex-wrap">
              <div className="flex items-center gap-2 bg-blue-500/20 px-4 py-2 rounded-full border border-blue-500/30">
                <Brain className="w-4 h-4 text-blue-300" />
                <span className="text-sm text-blue-200">AI 기반 분석</span>
              </div>
              <div className="flex items-center gap-2 bg-purple-500/20 px-4 py-2 rounded-full border border-purple-500/30">
                <Database className="w-4 h-4 text-purple-300" />
                <span className="text-sm text-purple-200">다중 데이터베이스</span>
              </div>
              <div className="flex items-center gap-2 bg-cyan-500/20 px-4 py-2 rounded-full border border-cyan-500/30">
                <Zap className="w-4 h-4 text-cyan-300" />
                <span className="text-sm text-cyan-200">실시간 검색</span>
              </div>
            </div>
          </div>

          {/* 시스템 초기화 진행 상태 */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/50">
            <h3 className="text-lg font-semibold mb-4 text-center text-slate-200">시스템 초기화</h3>
            <div className="space-y-3">
              {initSteps.map((step, index) => (
                <div key={index} className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-500 ${
                  index <= currentStep 
                    ? 'bg-blue-500/20 border border-blue-500/30' 
                    : 'bg-slate-700/30 border border-slate-600/30'
                }`}>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center transition-all duration-500 ${
                    index < currentStep 
                      ? 'bg-green-500' 
                      : index === currentStep 
                        ? 'bg-blue-500 animate-pulse' 
                        : 'bg-slate-600'
                  }`}>
                    {index < currentStep ? (
                      <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : index === currentStep ? (
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    ) : (
                      <div className="w-2 h-2 bg-slate-400 rounded-full"></div>
                    )}
                  </div>
                  <span className={`text-sm transition-colors duration-500 ${
                    index <= currentStep ? 'text-white' : 'text-slate-400'
                  }`}>
                    {step}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* 현재 시스템 설정 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 rounded-xl p-5 border border-blue-400/30 backdrop-blur-sm">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center shadow-lg">
                  <Cpu className="w-5 h-5 text-white" />
                </div>
                <div>
                  <span className="font-semibold text-blue-200">AI 모델</span>
                  <p className="text-xs text-blue-300/80">Language Model</p>
                </div>
              </div>
              <p className="text-white font-mono text-sm mb-1">{currentModel}</p>
              <p className="text-blue-300/80 text-xs">최신 신약개발 전문 모델</p>
            </div>
            
            <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 rounded-xl p-5 border border-purple-400/30 backdrop-blur-sm">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center shadow-lg">
                  <Target className="w-5 h-5 text-white" />
                </div>
                <div>
                  <span className="font-semibold text-purple-200">프롬프트 모드</span>
                  <p className="text-xs text-purple-300/80">Expert Mode</p>
                </div>
              </div>
              <p className="text-white text-sm mb-1">Default (균형잡힌 전문가)</p>
              <p className="text-purple-300/80 text-xs">신약개발 전문 AI 어시스턴트</p>
            </div>
          </div>

          {/* 핵심 기능 카드 */}
          <div>
            <h3 className="text-2xl font-bold text-center mb-8 bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">
              🚀 핵심 기능
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="group bg-gradient-to-br from-blue-500/15 to-cyan-500/15 rounded-xl p-5 border border-blue-400/30 hover:border-blue-300/60 transition-all duration-300 cursor-pointer hover:scale-105">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg">
                    <Beaker className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h4 className="font-bold text-blue-200">웹 인터페이스</h4>
                    <p className="text-xs text-blue-300/80">Next.js + React</p>
                  </div>
                </div>
                <p className="text-sm text-blue-200/90 leading-relaxed">
                  실시간 스트리밍 채팅, 마크다운 렌더링, 명령어 지원
                </p>
              </div>

              <div className="group bg-gradient-to-br from-purple-500/15 to-pink-500/15 rounded-xl p-5 border border-purple-400/30 hover:border-purple-300/60 transition-all duration-300 cursor-pointer hover:scale-105">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg">
                    <Target className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h4 className="font-bold text-purple-200">Deep Research</h4>
                    <p className="text-xs text-purple-300/80">MCP 통합</p>
                  </div>
                </div>
                <p className="text-sm text-purple-200/90 leading-relaxed">
                  PubMed, ChEMBL, ClinicalTrials 다중 데이터베이스 동시 검색
                </p>
              </div>

              <div className="group bg-gradient-to-br from-emerald-500/15 to-green-500/15 rounded-xl p-5 border border-emerald-400/30 hover:border-emerald-300/60 transition-all duration-300 cursor-pointer hover:scale-105">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-emerald-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg">
                    <Brain className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h4 className="font-bold text-emerald-200">전문 모드</h4>
                    <p className="text-xs text-emerald-300/80">Expert System</p>
                  </div>
                </div>
                <p className="text-sm text-emerald-200/90 leading-relaxed">
                  임상시험, 연구분석, 의약화학, 규제 전문가 모드
                </p>
              </div>

              <div className="group bg-gradient-to-br from-orange-500/15 to-red-500/15 rounded-xl p-5 border border-orange-400/30 hover:border-orange-300/60 transition-all duration-300 cursor-pointer hover:scale-105">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg">
                    <Users className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h4 className="font-bold text-orange-200">실시간 분석</h4>
                    <p className="text-xs text-orange-300/80">AI-Powered</p>
                  </div>
                </div>
                <p className="text-sm text-orange-200/90 leading-relaxed">
                  실시간 데이터 분석 및 신약개발 인사이트 제공
                </p>
              </div>
            </div>
          </div>

          {/* 빠른 시작 가이드 */}
          <div className="bg-gradient-to-r from-slate-800/50 to-blue-900/30 rounded-2xl p-6 border border-slate-700/50 backdrop-blur-sm">
            <h3 className="text-xl font-bold mb-6 text-center text-slate-200 flex items-center justify-center gap-2">
              <Play className="w-5 h-5 text-blue-400" />
              빠른 시작 가이드
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center space-y-3">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center mx-auto shadow-lg">
                  <span className="text-white font-bold text-lg">1</span>
                </div>
                <h4 className="font-bold text-blue-200">기본 사용</h4>
                <ul className="text-sm text-slate-300 space-y-1 text-left">
                  <li className="flex items-center gap-2">
                    <ArrowRight className="w-3 h-3 text-blue-400" />
                    신약개발 질문 직접 입력
                  </li>
                  <li className="flex items-center gap-2">
                    <ArrowRight className="w-3 h-3 text-blue-400" />
                    실시간 스트리밍 응답
                  </li>
                  <li className="flex items-center gap-2">
                    <ArrowRight className="w-3 h-3 text-blue-400" />
                    마크다운 렌더링 지원
                  </li>
                </ul>
              </div>
              
              <div className="text-center space-y-3">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full flex items-center justify-center mx-auto shadow-lg">
                  <span className="text-white font-bold text-lg">2</span>
                </div>
                <h4 className="font-bold text-purple-200">Deep Research</h4>
                <ul className="text-sm text-slate-300 space-y-1 text-left">
                  <li className="flex items-center gap-2">
                    <ArrowRight className="w-3 h-3 text-purple-400" />
                    <code className="bg-purple-500/20 px-2 py-0.5 rounded text-purple-300">/mcp start</code> 명령어
                  </li>
                  <li className="flex items-center gap-2">
                    <ArrowRight className="w-3 h-3 text-purple-400" />
                    다중 DB 검색 결과
                  </li>
                  <li className="flex items-center gap-2">
                    <ArrowRight className="w-3 h-3 text-purple-400" />
                    과학적 근거 제공
                  </li>
                </ul>
              </div>
              
              <div className="text-center space-y-3">
                <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-full flex items-center justify-center mx-auto shadow-lg">
                  <span className="text-white font-bold text-lg">3</span>
                </div>
                <h4 className="font-bold text-emerald-200">전문 모드</h4>
                <ul className="text-sm text-slate-300 space-y-1 text-left">
                  <li className="flex items-center gap-2">
                    <ArrowRight className="w-3 h-3 text-emerald-400" />
                    <code className="bg-emerald-500/20 px-2 py-0.5 rounded text-emerald-300">/prompt clinical</code>
                  </li>
                  <li className="flex items-center gap-2">
                    <ArrowRight className="w-3 h-3 text-emerald-400" />
                    임상시험 전문가 모드
                  </li>
                  <li className="flex items-center gap-2">
                    <ArrowRight className="w-3 h-3 text-emerald-400" />
                    연구분석 전문가 모드
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* 시작 버튼 및 시스템 상태 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full shadow-sm"></div>
                <span className="text-green-300 font-medium">Backend API 연결됨</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full shadow-sm"></div>
                <span className="text-blue-300 font-medium">WebUI 준비 완료</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-amber-500 rounded-full shadow-sm"></div>
                <span className="text-amber-300 font-medium">MCP 서버 대기</span>
              </div>
            </div>
            
            <button
              onClick={handleClose}
              className="group bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-8 py-3 rounded-xl font-bold transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center gap-2"
            >
              <span>시작하기</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
}