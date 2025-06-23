'use client';

import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { useChatStore } from '@/store/chatStore';
import { Search, FileText, Beaker, Users } from 'lucide-react';

export function ResearchPanel() {
  const { currentSessionId, sessions } = useChatStore();
  const currentSession = currentSessionId ? sessions[currentSessionId] : null;

  if (!currentSession) return null;

  // 최근 메시지에서 검색 결과 추출
  const enhancedMessages = currentSession.messages.filter(msg => 
    msg.role === 'assistant' && msg.searchResults
  );

  const latestSearchResults = enhancedMessages.length > 0 
    ? enhancedMessages[enhancedMessages.length - 1].searchResults 
    : null;

  return (
    <div className="h-full flex flex-col bg-muted/30">
      {/* 헤더 */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <Search className="w-4 h-4 text-research-500" />
          <h2 className="font-semibold">연구 패널</h2>
          {currentSession.mode === 'deep_research' && (
            <Badge variant="default" className="text-xs">활성</Badge>
          )}
        </div>
      </div>

      {/* 내용 */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-4">
        {/* 세션 정보 */}
        <Card className="p-4">
          <h3 className="font-medium mb-3">세션 정보</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">모드:</span>
              <Badge variant={currentSession.mode === 'normal' ? 'secondary' : 'default'}>
                {currentSession.mode === 'normal' ? '일반' : 'Deep Research'}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">프롬프트:</span>
              <span>{currentSession.prompt_type}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">메시지:</span>
              <span>{currentSession.messages.length}개</span>
            </div>
          </div>
        </Card>

        {/* 검색 결과 요약 */}
        {latestSearchResults && (
          <Card className="p-4">
            <h3 className="font-medium mb-3 flex items-center gap-2">
              <Beaker className="w-4 h-4 text-clinical-500" />
              검색 결과 요약
            </h3>
            <div className="space-y-3">
              {/* PubMed 결과 */}
              {latestSearchResults.pubmed && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="w-3 h-3 text-research-500" />
                    <span className="text-sm font-medium">PubMed</span>
                    <Badge variant="outline" className="text-xs">
                      {latestSearchResults.pubmed.length}개
                    </Badge>
                  </div>
                  {latestSearchResults.pubmed.slice(0, 3).map((paper: any, idx: number) => (
                    <div key={idx} className="text-xs bg-muted/50 rounded p-2 mb-1">
                      <div className="font-medium">{paper.title}</div>
                      <div className="text-muted-foreground">{paper.authors} ({paper.year})</div>
                    </div>
                  ))}
                </div>
              )}

              {/* ChEMBL 결과 */}
              {latestSearchResults.chembl && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Beaker className="w-3 h-3 text-biotech-500" />
                    <span className="text-sm font-medium">ChEMBL</span>
                    <Badge variant="outline" className="text-xs">
                      {latestSearchResults.chembl.length}개
                    </Badge>
                  </div>
                  {latestSearchResults.chembl.slice(0, 3).map((compound: any, idx: number) => (
                    <div key={idx} className="text-xs bg-muted/50 rounded p-2 mb-1">
                      <div className="font-medium">{compound.compound}</div>
                      <div className="text-muted-foreground">활성: {compound.activity}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>
        )}

        {/* 추천 액션 */}
        <Card className="p-4">
          <h3 className="font-medium mb-3">추천 액션</h3>
          <div className="space-y-2 text-sm">
            <button className="w-full text-left p-2 rounded hover:bg-muted transition-colors">
              <div className="font-medium">Deep Research 모드 활성화</div>
              <div className="text-muted-foreground text-xs">더 상세한 과학적 분석</div>
            </button>
            <button className="w-full text-left p-2 rounded hover:bg-muted transition-colors">
              <div className="font-medium">전문 프롬프트 변경</div>
              <div className="text-muted-foreground text-xs">특정 분야에 특화된 질문</div>
            </button>
            <button className="w-full text-left p-2 rounded hover:bg-muted transition-colors">
              <div className="font-medium">연구 결과 내보내기</div>
              <div className="text-muted-foreground text-xs">PDF 또는 Word 형태로 저장</div>
            </button>
          </div>
        </Card>
      </div>
    </div>
  );
}