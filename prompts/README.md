# GAIA-BT Prompt Template System

## 디렉토리 구조

```
prompts/
├── README.md                    # 이 파일 - 시스템 설명서
├── base/                        # 기본 프롬프트 템플릿
│   ├── common_guidelines.md     # 모든 모델 공통 지침
│   ├── markdown_format.md       # 마크다운 포맷 규칙
│   └── citation_rules.md        # 인용 규칙 (APA 스타일)
├── models/                      # 모델별 특화 프롬프트
│   ├── gemma3/                  # Gemma3 모델군
│   ├── txgemma-chat/           # TxGemma Chat 모델
│   ├── txgemma-predict/        # TxGemma Predict 모델
│   └── general/                # 일반 모델용
├── modes/                       # 모드별 프롬프트
│   ├── normal/                 # 일반 모드
│   └── deep_research/          # 딥리서치 모드
├── specializations/            # 전문 영역별 프롬프트
│   ├── clinical/               # 임상시험 전문
│   ├── chemistry/              # 의약화학 전문
│   ├── regulatory/             # 규제 전문
│   ├── research/               # 연구 분석 전문
│   └── patent/                 # 특허 전문
├── combinations/               # 조합된 프롬프트 파일들
│   ├── gemma3_normal_default.txt
│   ├── gemma3_deep_clinical.txt
│   ├── txgemma-chat_deep_research.txt
│   └── [model]_[mode]_[spec].txt
└── legacy/                     # 기존 프롬프트 파일들 (호환성)
    ├── prompt_default.txt
    ├── prompt_clinical.txt
    └── ...
```

## 명명 규칙

### 조합 파일 이름 패턴
`{model}_{mode}_{specialization}.txt`

- **model**: `gemma3`, `txgemma-chat`, `txgemma-predict`, `general`
- **mode**: `normal`, `deep`, `research`
- **specialization**: `default`, `clinical`, `chemistry`, `regulatory`, `research`, `patent`

### 예시
- `gemma3_normal_default.txt` - Gemma3 모델, 일반 모드, 기본 프롬프트
- `txgemma-chat_deep_clinical.txt` - TxGemma Chat 모델, 딥리서치 모드, 임상시험 전문
- `general_normal_chemistry.txt` - 일반 모델, 일반 모드, 의약화학 전문

## 사용법

### 1. 프롬프트 로딩 시스템
```python
def load_prompt(model: str, mode: str, specialization: str = "default") -> str:
    # 조합 파일 우선 검색
    combo_file = f"combinations/{model}_{mode}_{specialization}.txt"
    if exists(combo_file):
        return load_file(combo_file)
    
    # 동적 조합 생성
    return combine_prompts(model, mode, specialization)
```

### 2. 동적 조합 생성
기본 프롬프트 + 모델별 + 모드별 + 전문 영역별 프롬프트를 자동 조합

### 3. 관리자 인터페이스
- 웹 기반 프롬프트 편집기 (향후 구현)
- 파일 기반 직접 편집
- 버전 관리 시스템 연동

## 프롬프트 조합 우선순위

1. **combinations/** 디렉토리의 완성된 조합 파일
2. **동적 조합**: base + models + modes + specializations
3. **legacy/** 디렉토리의 기존 파일 (하위 호환성)

## 확장 가이드

### 새로운 모델 추가
1. `models/{new_model}/` 디렉토리 생성
2. 모델별 특화 지침 작성
3. 조합 파일 생성 또는 동적 조합 활용

### 새로운 전문 영역 추가
1. `specializations/{new_spec}/` 디렉토리 생성
2. 전문 영역별 프롬프트 작성
3. 기존 모델/모드와의 조합 테스트

### 새로운 모드 추가
1. `modes/{new_mode}/` 디렉토리 생성
2. 모드별 동작 지침 작성
3. 전체 조합 매트릭스 업데이트

## 품질 관리

### 1. 일관성 검사
- 모든 조합에서 공통 지침 준수
- 인용 스타일 통일성
- 마크다운 포맷 일관성

### 2. 성능 테스트
- 모델별 응답 품질 측정
- 조합별 효과성 평가
- A/B 테스트 결과 반영

### 3. 버전 관리
- Git을 통한 변경 이력 추적
- 프롬프트 효과성 측정 결과 문서화
- 롤백 시스템 구축

## 마이그레이션 가이드

기존 `prompt_*.txt` 파일들은 `legacy/` 디렉토리로 이동하되, 하위 호환성을 위해 유지됩니다.

새로운 시스템으로 완전 전환 후 단계적으로 제거할 예정입니다.