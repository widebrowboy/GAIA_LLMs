'use client';

import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { useChatStore } from '@/store/chatStore';
import { 
  Beaker, 
  Database, 
  User, 
  Lightbulb,
  MessageSquare 
} from 'lucide-react';
import { 
  pageVariants, 
  cardVariants, 
  staggerContainerVariants, 
  staggerItemVariants, 
  floatingVariants 
} from '@/utils/animations';

interface WelcomeSectionProps {
  onSuggestedQuestion: (question: string) => void;
  layoutConfig?: {
    mode: 'compact' | 'normal' | 'spacious';
    density: 'compact' | 'normal' | 'comfortable';
    fontSize: 'small' | 'medium' | 'large';
    gridConfig: {
      columns: number;
      gap: string;
      containerWidth: string;
      padding: string;
    };
  };
  isProcessing: boolean;
}

export default function WelcomeSection({ 
  onSuggestedQuestion, 
  layoutConfig, 
  isProcessing 
}: WelcomeSectionProps) {
  
  const { currentSessionId, sessions } = useChatStore();
  const currentSession = currentSessionId ? sessions[currentSessionId] : null;

  const suggestedQuestions = [
    {
      category: "신약개발 기초",
      icon: "💊",
      questions: [
        "신약개발 과정의 주요 단계를 설명해주세요",
        "타겟 발굴에서 약물 설계까지의 과정은?",
        "전임상 시험에서 확인하는 항목들은 무엇인가요?"
      ]
    },
    {
      category: "임상시험",
      icon: "🏥",
      questions: [
        "임상 1상, 2상, 3상의 차이점을 설명해주세요",
        "임상시험 설계 시 고려해야 할 주요 요소는?",
        "바이오마커의 역할과 중요성을 설명해주세요"
      ]
    },
    {
      category: "의약화학",
      icon: "⚗️",
      questions: [
        "lead compound 최적화 과정을 설명해주세요",
        "약물의 ADMET 특성이란 무엇인가요?",
        "Structure-Activity Relationship(SAR) 분석 방법은?"
      ]
    },
    {
      category: "규제 및 승인",
      icon: "📋",
      questions: [
        "FDA 신약 승인 과정을 단계별로 설명해주세요",
        "IND와 NDA의 차이점은 무엇인가요?",
        "글로벌 규제 기관들의 승인 요구사항 차이점은?"
      ]
    }
  ];

  // 카드 크기에 따른 스타일 조정
  const getCardSizeClasses = () => {
    const cardSize = layoutConfig?.density || 'normal';
    switch (cardSize) {
      case 'compact':
        return { 
          card: 'p-4 min-h-[100px]', 
          grid: 'grid-cols-1 md:grid-cols-2',
          icon: 'text-lg',
          spacing: 'space-y-4'
        };
      case 'comfortable':
        return { 
          card: 'p-8 min-h-[160px]', 
          grid: 'grid-cols-1 lg:grid-cols-2 xl:grid-cols-2',
          icon: 'text-3xl',
          spacing: 'space-y-8'
        };
      default: // normal
        return { 
          card: 'p-5 min-h-[110px]', 
          grid: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-2',
          icon: 'text-xl',
          spacing: 'space-y-5'
        };
    }
  };

  const getTextSizeClasses = () => {
    const textSize = layoutConfig?.fontSize || 'medium';
    switch (textSize) {
      case 'large':
        return { title: 'text-2xl', subtitle: 'text-base', button: 'text-base' };
      case 'small':
        return { title: 'text-lg', subtitle: 'text-sm', button: 'text-xs' };
      default: // medium
        return { title: 'text-xl', subtitle: 'text-sm', button: 'text-sm' };
    }
  };

  const cardSizeClasses = getCardSizeClasses();
  const textSizes = getTextSizeClasses();

  return (
    <motion.div 
      className="flex-1 flex items-center justify-center min-h-0"
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <div className={`w-full ${layoutConfig?.gridConfig?.containerWidth || 'max-w-4xl'} ${layoutConfig?.gridConfig?.padding || 'p-4'}`}>
        
        {/* 환영 메시지 */}
        <motion.div 
          className="text-center mb-8"
          variants={staggerContainerVariants}
          initial="initial"
          animate="animate"
        >
          <motion.div 
            className="flex items-center justify-center mb-4"
            variants={staggerItemVariants}
          >
            <motion.div 
              className="w-16 h-16 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-2xl flex items-center justify-center shadow-lg"
              variants={floatingVariants}
              animate="animate"
              whileHover={{ scale: 1.1, rotate: 5 }}
              whileTap={{ scale: 0.95 }}
            >
              <Beaker className="h-8 w-8 text-white" />
            </motion.div>
          </motion.div>
          
          <motion.h1 
            className={`${textSizes.title} font-bold text-white mb-2`}
            variants={staggerItemVariants}
          >
            GAIA-BT에 오신 것을 환영합니다!
          </motion.h1>
          
          <motion.p 
            className={`${textSizes.subtitle} text-blue-200 mb-4`}
            variants={staggerItemVariants}
          >
            신약개발 전문 AI 어시스턴트입니다. 무엇을 도와드릴까요?
          </motion.p>

          {/* 현재 모드 표시 */}
          <motion.div 
            className="flex items-center justify-center space-x-4 mb-6"
            variants={staggerItemVariants}
          >
            <Badge 
              variant={currentSession?.mode === 'deep_research' ? 'default' : 'secondary'}
              className={`${
                currentSession?.mode === 'deep_research' 
                  ? 'bg-green-600 text-white' 
                  : 'bg-gray-600 text-white'
              } px-3 py-1`}
            >
              {currentSession?.mode === 'deep_research' ? (
                <>
                  <Database className="h-3 w-3 mr-1" />
                  Deep Research 모드
                </>
              ) : (
                <>
                  <User className="h-3 w-3 mr-1" />
                  일반 모드
                </>
              )}
            </Badge>
            
            <Badge variant="outline" className="text-blue-200 border-blue-300 px-3 py-1">
              {currentSession?.prompt_type === 'clinical' && '🏥 임상시험 전문'}
              {currentSession?.prompt_type === 'research' && '🔬 연구분석 전문'}
              {currentSession?.prompt_type === 'chemistry' && '⚗️ 의약화학 전문'}
              {currentSession?.prompt_type === 'regulatory' && '📋 규제전문'}
              {(!currentSession?.prompt_type || currentSession?.prompt_type === 'default') && '💊 기본모드'}
            </Badge>
          </motion.div>
        </motion.div>

        {/* 추천 질문 섹션 */}
        <motion.div 
          className={`grid ${cardSizeClasses.grid} ${layoutConfig?.gridConfig?.gap || 'gap-4'}`}
          variants={staggerContainerVariants}
          initial="initial"
          animate="animate"
        >
          {Array.isArray(suggestedQuestions) && suggestedQuestions.length > 0 ? suggestedQuestions.map((category, categoryIndex) => (
            <motion.div
              key={category.category}
              variants={staggerItemVariants}
              whileHover={{ y: -5 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
            >
              <Card 
                className={`${cardSizeClasses.card} bg-white/10 backdrop-blur-sm border-white/20 hover:bg-white/15 transition-all duration-300 h-full`}
              >
                <div className="h-full flex flex-col">
                  <div className="flex items-center mb-3">
                    <span className={`${cardSizeClasses.icon} mr-2`}>{category.icon}</span>
                    <h3 className={`${textSizes.button} font-semibold text-white`}>
                      {category.category}
                    </h3>
                  </div>
                  
                  <div className="flex-1 space-y-2">
                    {Array.isArray(category.questions) && category.questions.length > 0 ? category.questions.map((question, questionIndex) => (
                      <motion.div
                        key={`suggestion-${categoryIndex}-${questionIndex}-${question.slice(0, 10)}`}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.8 + (categoryIndex * 0.2) + (questionIndex * 0.1) }}
                        whileHover={{ x: 5 }}
                      >
                        <Button
                          onClick={() => onSuggestedQuestion(question)}
                          variant="ghost"
                          size="sm"
                          disabled={isProcessing}
                          className={`w-full text-left justify-start ${textSizes.button} text-blue-100 hover:text-white hover:bg-white/10 p-2 h-auto whitespace-normal leading-relaxed`}
                          animated={true}
                        >
                          <div className="flex items-start">
                            <MessageSquare className="h-3 w-3 mr-2 mt-0.5 flex-shrink-0" />
                            <span className="text-left">{question}</span>
                          </div>
                        </Button>
                      </motion.div>
                    )) : (
                      <div className="text-center text-blue-300 py-2">
                        질문을 로드하는 중...
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            </motion.div>
          )) : (
            <div className="col-span-full text-center text-blue-300 py-8">
              추천 질문을 로드하는 중...
            </div>
          )}
        </motion.div>

        {/* 안내 메시지 */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center space-x-2 text-blue-300 bg-blue-900/30 px-4 py-2 rounded-lg border border-blue-700/50">
            <Lightbulb className="h-4 w-4" />
            <span className={`${textSizes.button}`}>
              {currentSession?.mode === 'deep_research' 
                ? "Deep Research 모드: 다중 데이터베이스 검색을 통한 상세한 분석을 제공합니다"
                : "일반 모드: 기본 AI 답변을 제공합니다. Deep Research 모드를 활성화하면 더 상세한 분석을 받을 수 있습니다"
              }
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}