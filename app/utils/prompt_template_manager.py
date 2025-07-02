#!/usr/bin/env python3
"""
GAIA-BT 프롬프트 템플릿 관리 시스템

모든 모델, 모드, 전문 영역 조합에 대한 프롬프트를 동적으로 생성하고 관리합니다.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import json

logger = logging.getLogger(__name__)

class PromptTemplateManager:
    """프롬프트 템플릿 관리자"""
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        프롬프트 템플릿 관리자 초기화
        
        Args:
            prompts_dir: 프롬프트 디렉토리 경로 (기본값: 프로젝트 루트/prompts)
        """
        if prompts_dir is None:
            # 프로젝트 루트에서 prompts 디렉토리 찾기
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent
            prompts_dir = project_root / "prompts"
        
        self.prompts_dir = Path(prompts_dir)
        self.base_dir = self.prompts_dir / "base"
        self.models_dir = self.prompts_dir / "models"
        self.modes_dir = self.prompts_dir / "modes"
        self.specializations_dir = self.prompts_dir / "specializations"
        self.combinations_dir = self.prompts_dir / "combinations"
        self.legacy_dir = self.prompts_dir / "legacy"
        
        # 사용 가능한 옵션들
        self.available_models = ["gemma3", "txgemma-chat", "txgemma-predict", "general"]
        self.available_modes = ["normal", "deep_research"]
        self.available_specializations = ["default", "clinical", "chemistry", "regulatory", "research", "patent"]
        
        logger.info(f"PromptTemplateManager 초기화: {self.prompts_dir}")
        
    def get_prompt(self, model: str, mode: str, specialization: str = "default") -> str:
        """
        지정된 조합에 대한 프롬프트를 반환합니다.
        
        Args:
            model: 모델명 (gemma3, txgemma-chat, txgemma-predict, general)
            mode: 모드 (normal, deep_research)
            specialization: 전문 영역 (default, clinical, chemistry, regulatory, research, patent)
            
        Returns:
            str: 조합된 프롬프트 내용
        """
        try:
            # 1. 조합 파일 우선 검색
            combo_prompt = self._load_combination_prompt(model, mode, specialization)
            if combo_prompt:
                logger.info(f"조합 파일 로드: {model}_{mode}_{specialization}")
                return combo_prompt
            
            # 2. 동적 조합 생성
            dynamic_prompt = self._create_dynamic_prompt(model, mode, specialization)
            if dynamic_prompt:
                logger.info(f"동적 조합 생성: {model}_{mode}_{specialization}")
                return dynamic_prompt
            
            # 3. 레거시 파일 폴백
            legacy_prompt = self._load_legacy_prompt(specialization)
            if legacy_prompt:
                logger.info(f"레거시 파일 사용: prompt_{specialization}.txt")
                return legacy_prompt
            
            # 4. 기본 프롬프트 반환
            logger.warning(f"프롬프트를 찾을 수 없어 기본 프롬프트 사용: {model}_{mode}_{specialization}")
            return self._get_default_prompt()
            
        except Exception as e:
            logger.error(f"프롬프트 로드 실패: {e}")
            return self._get_default_prompt()
    
    def _load_combination_prompt(self, model: str, mode: str, specialization: str) -> Optional[str]:
        """조합 파일에서 프롬프트 로드"""
        combo_file = self.combinations_dir / f"{model}_{mode}_{specialization}.txt"
        
        if combo_file.exists():
            try:
                with open(combo_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"조합 파일 읽기 실패 {combo_file}: {e}")
        
        return None
    
    def _create_dynamic_prompt(self, model: str, mode: str, specialization: str) -> Optional[str]:
        """동적으로 프롬프트 조합 생성"""
        try:
            # 기본 구성 요소들 로드
            components = {}
            
            # 1. 공통 가이드라인
            components['common'] = self._load_file(self.base_dir / "common_guidelines.md")
            components['markdown'] = self._load_file(self.base_dir / "markdown_format.md")
            components['citation'] = self._load_file(self.base_dir / "citation_rules.md")
            
            # 2. 모델별 최적화
            model_file = self.models_dir / model / "optimization.md"
            components['model'] = self._load_file(model_file)
            
            # 3. 모드별 지침
            mode_file = self.modes_dir / mode / "core_instructions.md"
            components['mode'] = self._load_file(mode_file)
            
            # 4. 전문 영역별 지침
            if specialization != "default":
                spec_file = self.specializations_dir / specialization / "core_expertise.md"
                components['specialization'] = self._load_file(spec_file)
            
            # 5. 조합하여 완전한 프롬프트 생성
            return self._combine_components(components, model, mode, specialization)
            
        except Exception as e:
            logger.error(f"동적 프롬프트 생성 실패: {e}")
            return None
    
    def _load_legacy_prompt(self, specialization: str) -> Optional[str]:
        """레거시 프롬프트 파일 로드"""
        legacy_file = self.legacy_dir / f"prompt_{specialization}.txt"
        
        if legacy_file.exists():
            try:
                with open(legacy_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"레거시 파일 읽기 실패 {legacy_file}: {e}")
        
        return None
    
    def _load_file(self, file_path: Path) -> str:
        """파일 내용 로드"""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"파일 읽기 실패 {file_path}: {e}")
        
        return ""
    
    def _combine_components(self, components: Dict[str, str], model: str, mode: str, specialization: str) -> str:
        """프롬프트 구성 요소들을 조합"""
        prompt_parts = []
        
        # 헤더
        prompt_parts.append(f"# GAIA-BT {model.upper()} - {mode.title()} Mode - {specialization.title()} Specialization")
        prompt_parts.append("")
        
        # 공통 가이드라인
        if components.get('common'):
            prompt_parts.append("## 기본 가이드라인")
            prompt_parts.append(components['common'])
            prompt_parts.append("")
        
        # 모드별 지침
        if components.get('mode'):
            prompt_parts.append("## 모드별 지침")
            prompt_parts.append(components['mode'])
            prompt_parts.append("")
        
        # 모델별 최적화
        if components.get('model'):
            prompt_parts.append("## 모델 최적화")
            prompt_parts.append(components['model'])
            prompt_parts.append("")
        
        # 전문 영역별 지침
        if components.get('specialization'):
            prompt_parts.append("## 전문 영역 지침")
            prompt_parts.append(components['specialization'])
            prompt_parts.append("")
        
        # 마크다운 포맷 가이드
        if components.get('markdown'):
            prompt_parts.append("## 마크다운 포맷 규칙")
            prompt_parts.append(components['markdown'])
            prompt_parts.append("")
        
        # 인용 규칙
        if components.get('citation'):
            prompt_parts.append("## 인용 및 참고문헌 규칙")
            prompt_parts.append(components['citation'])
            prompt_parts.append("")
        
        return "\n".join(prompt_parts)
    
    def _get_default_prompt(self) -> str:
        """기본 프롬프트 반환"""
        return """# GAIA-BT 기본 프롬프트

당신은 GAIA-BT (Drug Discovery AI Assistant) 신약개발 전문 AI 연구 어시스턴트입니다.

## 기본 원칙
- 정확하고 신뢰할 수 있는 정보 제공
- 구조화된 응답으로 가독성 확보  
- 실무에 도움이 되는 실용적 조언
- 전문 용어는 영문 유지, 설명은 한국어 사용

## 응답 구조
1. 개요 및 핵심 포인트
2. 상세 분석
3. 실무적 고려사항
4. 참고 리소스 안내

정확한 정보 제공을 위해 최신 데이터베이스 확인을 권장합니다.
"""
    
    def save_combination_prompt(self, model: str, mode: str, specialization: str, content: str) -> bool:
        """조합 프롬프트를 파일로 저장"""
        try:
            combo_file = self.combinations_dir / f"{model}_{mode}_{specialization}.txt"
            combo_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(combo_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"조합 프롬프트 저장 완료: {combo_file}")
            return True
            
        except Exception as e:
            logger.error(f"조합 프롬프트 저장 실패: {e}")
            return False
    
    def get_available_combinations(self) -> List[Tuple[str, str, str]]:
        """사용 가능한 모든 조합 반환"""
        combinations = []
        
        for model in self.available_models:
            for mode in self.available_modes:
                for spec in self.available_specializations:
                    combinations.append((model, mode, spec))
        
        return combinations
    
    def validate_combination(self, model: str, mode: str, specialization: str) -> bool:
        """조합의 유효성 검사"""
        return (
            model in self.available_models and
            mode in self.available_modes and
            specialization in self.available_specializations
        )
    
    def get_prompt_info(self, model: str, mode: str, specialization: str) -> Dict[str, any]:
        """프롬프트 조합 정보 반환"""
        combo_file = self.combinations_dir / f"{model}_{mode}_{specialization}.txt"
        
        return {
            "combination": f"{model}_{mode}_{specialization}",
            "model": model,
            "mode": mode,
            "specialization": specialization,
            "has_combination_file": combo_file.exists(),
            "combination_file_path": str(combo_file),
            "can_generate_dynamic": self._can_generate_dynamic(model, mode, specialization),
            "has_legacy_fallback": self._has_legacy_fallback(specialization)
        }
    
    def _can_generate_dynamic(self, model: str, mode: str, specialization: str) -> bool:
        """동적 생성 가능 여부 확인"""
        # 기본 파일들 확인
        base_files = [
            self.base_dir / "common_guidelines.md",
            self.base_dir / "markdown_format.md",
            self.base_dir / "citation_rules.md"
        ]
        
        model_file = self.models_dir / model / "optimization.md"
        mode_file = self.modes_dir / mode / "core_instructions.md"
        
        required_files = base_files + [model_file, mode_file]
        
        # 전문 영역이 default가 아니면 전문 파일도 필요
        if specialization != "default":
            spec_file = self.specializations_dir / specialization / "core_expertise.md"
            required_files.append(spec_file)
        
        return all(f.exists() for f in required_files)
    
    def _has_legacy_fallback(self, specialization: str) -> bool:
        """레거시 폴백 가능 여부 확인"""
        legacy_file = self.legacy_dir / f"prompt_{specialization}.txt"
        return legacy_file.exists()
    
    def create_all_combinations(self) -> Dict[str, bool]:
        """모든 가능한 조합의 파일을 생성"""
        results = {}
        
        for model, mode, spec in self.get_available_combinations():
            # 이미 조합 파일이 있으면 건너뛰기
            combo_file = self.combinations_dir / f"{model}_{mode}_{spec}.txt"
            if combo_file.exists():
                results[f"{model}_{mode}_{spec}"] = True
                continue
            
            # 동적 생성 시도
            prompt = self._create_dynamic_prompt(model, mode, spec)
            if prompt:
                success = self.save_combination_prompt(model, mode, spec, prompt)
                results[f"{model}_{mode}_{spec}"] = success
            else:
                results[f"{model}_{mode}_{spec}"] = False
        
        return results
    
    def reload_all_prompts(self) -> bool:
        """모든 프롬프트 파일을 다시 로드 (실시간 반영)"""
        try:
            logger.info("프롬프트 파일 실시간 리로드 시작...")
            
            # 기존 캐시 초기화
            self._prompt_cache = {}
            
            # 조합 파일들의 수정 시간 체크 (필요시 추가)
            reloaded_count = 0
            
            # 조합 파일 디렉토리가 존재하면 확인
            if self.combinations_dir.exists():
                for combo_file in self.combinations_dir.glob("*.txt"):
                    reloaded_count += 1
                    
            logger.info(f"프롬프트 파일 리로드 완료: {reloaded_count}개 파일 확인")
            return True
            
        except Exception as e:
            logger.error(f"프롬프트 리로드 실패: {e}")
            return False
    
    def invalidate_cache(self):
        """프롬프트 캐시 무효화"""
        if hasattr(self, '_prompt_cache'):
            self._prompt_cache.clear()
            logger.info("프롬프트 캐시 무효화 완료")
    
    def reload_specific_prompt(self, model: str, mode: str, specialization: str) -> bool:
        """특정 프롬프트 조합만 리로드"""
        try:
            combo_key = f"{model}_{mode}_{specialization}"
            
            # 캐시에서 해당 조합 제거
            if hasattr(self, '_prompt_cache'):
                self._prompt_cache.pop(combo_key, None)
            
            # 조합 파일이 존재하는지 확인
            combo_file = self.combinations_dir / f"{combo_key}.txt"
            if combo_file.exists():
                logger.info(f"프롬프트 조합 리로드: {combo_key}")
                return True
            else:
                logger.warning(f"프롬프트 조합 파일이 없습니다: {combo_file}")
                return False
                
        except Exception as e:
            logger.error(f"특정 프롬프트 리로드 실패 ({model}_{mode}_{specialization}): {e}")
            return False


# 글로벌 인스턴스
_prompt_manager = None

def get_prompt_manager() -> PromptTemplateManager:
    """프롬프트 관리자 인스턴스 반환 (싱글톤 패턴)"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptTemplateManager()
    return _prompt_manager

def reload_prompt_manager() -> PromptTemplateManager:
    """프롬프트 관리자를 완전히 다시 생성 (실시간 리로드)"""
    global _prompt_manager
    _prompt_manager = None  # 기존 인스턴스 제거
    _prompt_manager = PromptTemplateManager()  # 새 인스턴스 생성
    logger.info("프롬프트 관리자 완전 리로드 완료")
    return _prompt_manager


# CLI 테스트 함수
def main():
    """CLI 테스트"""
    manager = get_prompt_manager()
    
    print("=== GAIA-BT 프롬프트 템플릿 관리자 ===")
    print(f"프롬프트 디렉토리: {manager.prompts_dir}")
    
    # 사용 가능한 조합 출력
    print("\\n사용 가능한 조합:")
    combinations = manager.get_available_combinations()
    for i, (model, mode, spec) in enumerate(combinations[:10]):  # 처음 10개만 출력
        print(f"{i+1}. {model} + {mode} + {spec}")
    
    if len(combinations) > 10:
        print(f"... 총 {len(combinations)}개 조합")
    
    # 샘플 프롬프트 테스트
    print("\\n=== 샘플 프롬프트 테스트 ===")
    sample_prompt = manager.get_prompt("gemma3", "normal", "default")
    print(f"프롬프트 길이: {len(sample_prompt)}자")
    print(f"프롬프트 미리보기:\\n{sample_prompt[:200]}...")


if __name__ == "__main__":
    main()