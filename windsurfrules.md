# GAIA-BT v2.0 Alpha 신약개발 연구 시스템 - 개발 가이드 & 규칙

## 📋 프로젝트 개요
GAIA-BT v2.0 Alpha는 Ollama LLM과 MCP(Model Context Protocol)를 활용한 신약개발 전문 AI 연구 어시스턴트 시스템입니다.

## 🎯 현재 구현 상태 (2024년 기준)
- **전체 완성도**: 92-97% 완료 (Alpha 버전)
- **핵심 기능**: 모든 주요 기능 구현 완료
- **신규 기능**: 
  - Playwright MCP 웹 자동화 추가
  - 이중 모드 시스템 (일반/Deep Research 모드)
  - MCP 출력 제어 옵션 추가
  - 파일 기반 프롬프트 관리 시스템
- **상태**: 알파 테스트 단계 (Alpha Testing)
- **사용 가능**: 즉시 사용 가능한 상태

## 🔧 개발 시 필수 준수 규칙

### Rule 1: 코드 구조 및 아키텍처
```
MUST FOLLOW: 
- 모든 import는 `from app.xxx import yyy` 형태로 사용
- 클래스명은 DrugDevelopmentChatbot, OllamaClient 등 기존 명명 규칙 준수
- 비동기 프로그래밍: async/await 패턴 필수 사용
- 에러 처리: 모든 외부 API 호출에 try-catch 블록 필수
```

### Rule 2: MCP 통합 개발 규칙
```
MUST FOLLOW:
- 새로운 MCP 서버 추가 시 mcp/integration/mcp_manager.py에 등록
- Mock 응답 시스템 유지: 외부 API 없이도 동작해야 함
- Deep Search 통합: 키워드 기반 자동 라우팅 구현
- 모든 MCP 호출은 에러 처리와 폴백 로직 포함
```

### Rule 3: 설정 및 환경 관리
```
MUST FOLLOW:
- 모든 설정은 app/utils/config.py 통해 관리
- 환경변수 우선순위: .env > 기본값
- API 키 등 민감정보는 절대 하드코딩 금지
- mcp.json 설정 변경 시 반드시 문서 업데이트
```

### Rule 4: 사용자 경험 (UX) 규칙
```
MUST FOLLOW:
- Rich 라이브러리 사용하여 시각적 피드백 제공
- 모든 에러 메시지는 사용자가 이해할 수 있는 한국어로
- 긴 작업 시 진행상황 표시 필수
- 디버그 모드 지원: --debug 플래그로 상세 정보 출력
```

### Rule 5: 신약개발 도메인 특화 규칙
```
MUST FOLLOW:
- 모든 AI 응답은 신약개발 관점에서 해석 및 설명
- 의학/생물학 용어 사용 시 한국어 설명 병기
- 논문, 임상시험 정보 포함하여 근거 기반 답변 제공
- 화학구조, 타겟-약물 상호작용 정보 우선 활용
```

### Rule 6: 프롬프트 관리 규칙 (신규)
```
MUST FOLLOW:
- 모든 시스템 프롬프트는 prompts/ 폴더에 파일로 관리
- 프롬프트 파일명은 prompt_<타입>.txt 형식 준수
- 프롬프트 변경은 /prompt 명령어를 통해서만 수행
- 목적별 전문 프롬프트 활용 (clinical, research, chemistry, regulatory)
- prompt_manager.py를 통한 중앙집중식 프롬프트 관리
```

### Rule 7: 이중 모드 시스템 규칙 (신규 v2.0 Alpha)
```
MUST FOLLOW:
- 일반 모드: 기본 AI 답변만 제공, MCP 비활성화
- Deep Research 모드: MCP 통합 검색 활성화, 다중 데이터베이스 검색
- 모드 전환은 /mcp (Deep Research) 및 /normal 명령어로만 수행
- MCP 출력 표시는 show_mcp_output 설정으로 제어
- 각 모드별 전용 배너 및 UI 제공
```

### Rule 8: MCP 출력 제어 규칙 (신규 v2.0 Alpha)
```
MUST FOLLOW:
- MCP 검색 과정 출력은 config.show_mcp_output 설정으로 제어
- /mcpshow 명령어로 실시간 토글 가능
- 기본값은 False (출력 숨김) - 사용자 경험 개선
- 디버그 모드와 별도로 동작 (독립적 제어)
- Deep Research 모드에서만 적용됨
```

### Rule 9: WebUI 개발 규칙 (신규 v2.0 Alpha)
```
MUST FOLLOW:
- Open WebUI 기반 개발 (Svelte + Python 플러그인 시스템)
- 기존 CLI 시스템과 Function Calling으로 직접 통합
- 모든 WebUI 컴포넌트는 webui/ 디렉토리에 구성
- CLI 기능과 1:1 호환성 유지 (Pipelines Framework 활용)
- 신약개발 특화 플러그인 개발 필수
- Ollama 네이티브 지원 및 즉시 사용 가능한 UI
```

### Rule 10: 메모리 및 단축키 활용 규칙 (신규)
```
MUST FOLLOW:
- 주요 정보 및 규칙은 windsufrules.md(본 파일)에 항상 기록
- 개발 중 즉시 참고 및 업데이트 가능해야 함
- CLAUDE.md와 내용 동기화 유지
```

---

> **항상 `windsurfrules.md` 파일을 참고하여 개발 및 연구 규칙을 준수하세요.**
> 
> 본 파일은 CLAUDE.md와 동일한 내용을 유지하며, 모든 개발자는 변경 시 반드시 동기화할 것!
