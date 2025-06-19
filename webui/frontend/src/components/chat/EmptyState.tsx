'use client';

export function EmptyState() {
  return (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="text-center space-y-4 max-w-md">
        <div className="w-20 h-20 mx-auto bg-gradient-to-br from-research-500 via-biotech-500 to-clinical-500 rounded-full flex items-center justify-center">
          <span className="text-3xl text-white">🧬</span>
        </div>
        <div>
          <h2 className="text-2xl font-bold text-foreground mb-2">
            GAIA-BT에 오신 것을 환영합니다
          </h2>
          <p className="text-muted-foreground">
            신약개발 AI 연구 어시스턴트가 도움을 드릴 준비가 되었습니다.
            새로운 채팅을 시작해보세요.
          </p>
        </div>
      </div>
    </div>
  );
}