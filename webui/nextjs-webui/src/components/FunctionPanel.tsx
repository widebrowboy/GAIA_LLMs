'use client';

import React, { useState } from 'react';
import { 
  Zap, 
  Search, 
  FlaskConical, 
  FileText, 
  Heart, 
  BookOpen, 
  PlaneTakeoff,
  Settings,
  Activity,
  Loader2
} from 'lucide-react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

interface FunctionResult {
  function: string;
  result: string;
  timestamp: string;
  mock?: boolean;
}

const FUNCTIONS = [
  {
    id: 'get_system_status',
    name: 'System Status',
    description: 'GAIA-BT 시스템 상태 및 설정 확인',
    icon: Activity,
    params: [],
    category: 'system'
  },
  {
    id: 'switch_mode',
    name: 'Switch Mode',
    description: 'Normal/Deep Research 모드 전환',
    icon: Settings,
    params: [
      { name: 'mode', type: 'select', options: ['normal', 'deep_research'], default: 'deep_research' }
    ],
    category: 'system'
  },
  {
    id: 'change_prompt_mode',
    name: 'Change Prompt Mode',
    description: '전문 프롬프트 모드 변경',
    icon: FileText,
    params: [
      { 
        name: 'mode', 
        type: 'select', 
        options: ['default', 'clinical', 'research', 'chemistry', 'regulatory'], 
        default: 'clinical' 
      }
    ],
    category: 'system'
  },
  {
    id: 'deep_research_search',
    name: 'Deep Research Search',
    description: 'MCP 통합 심층 연구 검색',
    icon: Search,
    params: [
      { name: 'query', type: 'text', placeholder: 'BRCA1 inhibitor breast cancer', required: true }
    ],
    category: 'research'
  },
  {
    id: 'molecular_analysis',
    name: 'Molecular Analysis',
    description: '분자 구조 및 약물 상호작용 분석',
    icon: FlaskConical,
    params: [
      { name: 'compound', type: 'text', placeholder: 'aspirin', required: true }
    ],
    category: 'chemistry'
  },
  {
    id: 'clinical_trial_search',
    name: 'Clinical Trial Search',
    description: '특정 적응증의 임상시험 검색',
    icon: Heart,
    params: [
      { name: 'indication', type: 'text', placeholder: 'breast cancer', required: true },
      { name: 'phase', type: 'select', options: ['1', '2', '3', '4'], optional: true }
    ],
    category: 'clinical'
  },
  {
    id: 'literature_search',
    name: 'Literature Search',
    description: '신약개발 주제의 과학 문헌 검색',
    icon: BookOpen,
    params: [
      { name: 'topic', type: 'text', placeholder: 'drug development', required: true },
      { name: 'years', type: 'number', placeholder: '5', default: 5 }
    ],
    category: 'research'
  },
  {
    id: 'generate_research_plan',
    name: 'Generate Research Plan',
    description: 'AI 기반 연구 계획 수립',
    icon: PlaneTakeoff,
    params: [
      { name: 'objective', type: 'text', placeholder: 'novel cancer drug development', required: true },
      { name: 'budget', type: 'text', placeholder: '$5M', optional: true },
      { name: 'timeline', type: 'text', placeholder: '24 months', optional: true }
    ],
    category: 'planning'
  }
];

const CATEGORIES = {
  system: { label: '⚙️ System Control', color: 'bg-gray-500' },
  research: { label: '🔬 Research', color: 'bg-blue-500' },
  chemistry: { label: '⚗️ Chemistry', color: 'bg-green-500' },
  clinical: { label: '🏥 Clinical', color: 'bg-red-500' },
  planning: { label: '📋 Planning', color: 'bg-purple-500' }
};

export default function FunctionPanel() {
  const [selectedFunction, setSelectedFunction] = useState<string | null>(null);
  const [parameters, setParameters] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<FunctionResult | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const executeFunction = async () => {
    if (!selectedFunction || isLoading) return;

    const func = FUNCTIONS.find(f => f.id === selectedFunction);
    if (!func) return;

    // Validate required parameters
    const missingParams = func.params
      .filter(p => p.required && !parameters[p.name])
      .map(p => p.name);

    if (missingParams.length > 0) {
      alert(`다음 필수 매개변수를 입력해주세요: ${missingParams.join(', ')}`);
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      const response = await axios.post('/api/gaia-bt', {
        type: 'function',
        function_name: selectedFunction,
        parameters: parameters
      });

      setResult({
        function: func.name,
        result: response.data.result,
        timestamp: response.data.timestamp,
        mock: response.data.mock
      });
    } catch (error) {
      console.error('Function execution error:', error);
      setResult({
        function: func.name,
        result: '⚠️ 함수 실행 중 오류가 발생했습니다.',
        timestamp: new Date().toISOString()
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleParameterChange = (paramName: string, value: any) => {
    setParameters(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  const getFilteredFunctions = () => {
    if (selectedCategory === 'all') return FUNCTIONS;
    return FUNCTIONS.filter(func => func.category === selectedCategory);
  };

  const selectedFunc = FUNCTIONS.find(f => f.id === selectedFunction);

  return (
    <div className=\"flex flex-col h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50\">
      {/* Header */}
      <div className=\"bg-white border-b border-gray-200 p-4 shadow-sm\">
        <div className=\"flex items-center space-x-3\">
          <div className=\"w-10 h-10 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center\">
            <Zap className=\"w-6 h-6 text-white\" />
          </div>
          <div>
            <h1 className=\"text-xl font-bold text-gray-900\">🧬 GAIA-BT Functions</h1>
            <p className=\"text-sm text-gray-600\">신약개발 전문 도구 모음</p>
          </div>
        </div>

        {/* Category Filter */}
        <div className=\"mt-4 flex flex-wrap gap-2\">
          <button
            onClick={() => setSelectedCategory('all')}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              selectedCategory === 'all'
                ? 'bg-gray-800 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            🎯 All Functions
          </button>
          {Object.entries(CATEGORIES).map(([key, category]) => (
            <button
              key={key}
              onClick={() => setSelectedCategory(key)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                selectedCategory === key
                  ? `${category.color} text-white`
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {category.label}
            </button>
          ))}
        </div>
      </div>

      <div className=\"flex-1 flex overflow-hidden\">
        {/* Function List */}
        <div className=\"w-1/3 border-r border-gray-200 bg-white overflow-y-auto\">
          <div className=\"p-4\">
            <h2 className=\"text-lg font-semibold text-gray-900 mb-4\">Available Functions</h2>
            <div className=\"space-y-2\">
              {getFilteredFunctions().map((func) => {
                const Icon = func.icon;
                const category = CATEGORIES[func.category as keyof typeof CATEGORIES];
                
                return (
                  <button
                    key={func.id}
                    onClick={() => {
                      setSelectedFunction(func.id);
                      setParameters({});
                      setResult(null);
                    }}
                    className={`w-full text-left p-3 rounded-lg border transition-colors ${
                      selectedFunction === func.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className=\"flex items-start space-x-3\">
                      <div className={`w-8 h-8 ${category.color} rounded-lg flex items-center justify-center flex-shrink-0`}>
                        <Icon className=\"w-4 h-4 text-white\" />
                      </div>
                      <div className=\"flex-1 min-w-0\">
                        <div className=\"font-medium text-gray-900 text-sm\">{func.name}</div>
                        <div className=\"text-xs text-gray-600 mt-1\">{func.description}</div>
                        <div className=\"text-xs text-gray-500 mt-1\">{category.label}</div>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Function Details & Execution */}
        <div className=\"flex-1 flex flex-col overflow-hidden\">
          {selectedFunc ? (
            <>
              {/* Function Info */}
              <div className=\"bg-white border-b border-gray-200 p-4\">
                <div className=\"flex items-center space-x-3 mb-4\">
                  <div className={`w-10 h-10 ${CATEGORIES[selectedFunc.category as keyof typeof CATEGORIES].color} rounded-lg flex items-center justify-center`}>
                    <selectedFunc.icon className=\"w-6 h-6 text-white\" />
                  </div>
                  <div>
                    <h3 className=\"text-lg font-semibold text-gray-900\">{selectedFunc.name}</h3>
                    <p className=\"text-sm text-gray-600\">{selectedFunc.description}</p>
                  </div>
                </div>

                {/* Parameters */}
                {selectedFunc.params.length > 0 && (
                  <div className=\"space-y-3\">
                    <h4 className=\"font-medium text-gray-900\">Parameters</h4>
                    {selectedFunc.params.map((param) => (
                      <div key={param.name}>
                        <label className=\"block text-sm font-medium text-gray-700 mb-1\">
                          {param.name}
                          {param.required && <span className=\"text-red-500 ml-1\">*</span>}
                          {param.optional && <span className=\"text-gray-400 ml-1\">(optional)</span>}
                        </label>
                        
                        {param.type === 'select' ? (
                          <select
                            value={parameters[param.name] || param.default || ''}
                            onChange={(e) => handleParameterChange(param.name, e.target.value)}
                            className=\"w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent\"
                          >
                            {!param.required && <option value=\"\">선택하세요</option>}
                            {param.options?.map(option => (
                              <option key={option} value={option}>{option}</option>
                            ))}
                          </select>
                        ) : param.type === 'number' ? (
                          <input
                            type=\"number\"
                            value={parameters[param.name] || param.default || ''}
                            onChange={(e) => handleParameterChange(param.name, parseInt(e.target.value) || '')}
                            placeholder={param.placeholder}
                            className=\"w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent\"
                          />
                        ) : (
                          <input
                            type=\"text\"
                            value={parameters[param.name] || param.default || ''}
                            onChange={(e) => handleParameterChange(param.name, e.target.value)}
                            placeholder={param.placeholder}
                            className=\"w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent\"
                          />
                        )}
                      </div>
                    ))}
                  </div>
                )}

                <button
                  onClick={executeFunction}
                  disabled={isLoading}
                  className={`mt-4 w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                    isLoading
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-blue-500 hover:bg-blue-600 text-white'
                  }`}
                >
                  {isLoading ? (
                    <div className=\"flex items-center justify-center space-x-2\">
                      <Loader2 className=\"w-4 h-4 animate-spin\" />
                      <span>Executing...</span>
                    </div>
                  ) : (
                    <div className=\"flex items-center justify-center space-x-2\">
                      <Zap className=\"w-4 h-4\" />
                      <span>Execute Function</span>
                    </div>
                  )}
                </button>
              </div>

              {/* Results */}
              <div className=\"flex-1 overflow-y-auto p-4\">
                {result ? (
                  <div className=\"bg-white rounded-lg border border-gray-200 p-4\">
                    <div className=\"flex items-center justify-between mb-3\">
                      <h4 className=\"font-medium text-gray-900\">
                        ⚡ {result.function} Result
                      </h4>
                      <div className=\"flex items-center space-x-2\">
                        {result.mock && (
                          <span className=\"px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full\">
                            Mock Mode
                          </span>
                        )}
                        <span className=\"text-xs text-gray-500\">
                          {new Date(result.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                    
                    <div className=\"prose prose-sm max-w-none text-gray-900\">
                      <ReactMarkdown
                        components={{
                          pre: ({ children }) => (
                            <pre className=\"bg-gray-100 p-3 rounded overflow-x-auto text-sm\">
                              {children}
                            </pre>
                          ),
                          code: ({ children }) => (
                            <code className=\"bg-gray-100 px-1 py-0.5 rounded text-sm\">
                              {children}
                            </code>
                          ),
                          h1: ({ children }) => (
                            <h1 className=\"text-xl font-bold text-gray-900 mb-3\">{children}</h1>
                          ),
                          h2: ({ children }) => (
                            <h2 className=\"text-lg font-semibold text-gray-900 mb-2\">{children}</h2>
                          ),
                          h3: ({ children }) => (
                            <h3 className=\"text-md font-medium text-gray-900 mb-2\">{children}</h3>
                          ),
                        }}
                      >
                        {result.result}
                      </ReactMarkdown>
                    </div>
                  </div>
                ) : (
                  <div className=\"text-center py-12\">
                    <Zap className=\"w-12 h-12 text-gray-400 mx-auto mb-4\" />
                    <h3 className=\"text-lg font-medium text-gray-900 mb-2\">
                      Ready to Execute
                    </h3>
                    <p className=\"text-gray-600\">
                      매개변수를 입력하고 \"Execute Function\" 버튼을 클릭하세요.
                    </p>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className=\"flex-1 flex items-center justify-center\">
              <div className=\"text-center\">
                <Zap className=\"w-16 h-16 text-gray-400 mx-auto mb-4\" />
                <h3 className=\"text-lg font-medium text-gray-900 mb-2\">
                  Select a Function
                </h3>
                <p className=\"text-gray-600 max-w-md\">
                  왼쪽에서 실행할 GAIA-BT 함수를 선택하세요. 
                  각 함수는 신약개발의 다양한 측면을 지원합니다.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}