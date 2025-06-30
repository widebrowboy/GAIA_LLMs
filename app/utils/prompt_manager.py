"""
프롬프트 관리 모듈
시스템 프롬프트를 파일로 관리하고 로드하는 기능 제공
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """프롬프트 템플릿 데이터 클래스"""
    name: str
    description: str
    content: str
    file_path: str


class PromptManager:
    """프롬프트 파일 관리 클래스"""
    
    def __init__(self, prompt_dir: str = "prompts"):
        """
        프롬프트 매니저 초기화
        
        Args:
            prompt_dir: 프롬프트 파일이 저장된 디렉토리
        """
        self.prompt_dir = Path(prompt_dir)
        self.prompts: Dict[str, PromptTemplate] = {}
        self.default_prompt = "default"
        
        # 프롬프트 설명
        self.prompt_descriptions = {
            "default": "신약개발 전반에 대한 균형잡힌 AI 어시스턴트",
            "clinical": "임상시험 및 환자 중심 약물 개발 전문가",
            "research": "문헌 분석 및 과학적 증거 종합 전문가",
            "chemistry": "의약화학 및 분자 설계 전문가",
            "regulatory": "글로벌 의약품 규제 및 승인 전문가",
            "patent": "신약개발 특허 검색 및 분석 전문가"
        }
        
        # 프롬프트 파일 로드
        self._load_prompts()
    
    def _load_prompts(self):
        """프롬프트 디렉토리에서 모든 프롬프트 파일 로드"""
        if not self.prompt_dir.exists():
            print(f"⚠️ 프롬프트 디렉토리가 없습니다: {self.prompt_dir}")
            return
        
        # prompt_*.txt 패턴의 파일들을 찾기
        for prompt_file in self.prompt_dir.glob("prompt_*.txt"):
            try:
                # 파일명에서 프롬프트 이름 추출 (prompt_name.txt -> name)
                prompt_name = prompt_file.stem.replace("prompt_", "")
                
                # 파일 내용 읽기
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # 프롬프트 템플릿 생성
                description = self.prompt_descriptions.get(prompt_name, f"{prompt_name} 전문 모드")
                template = PromptTemplate(
                    name=prompt_name,
                    description=description,
                    content=content,
                    file_path=str(prompt_file)
                )
                
                self.prompts[prompt_name] = template
                
            except Exception as e:
                print(f"❌ 프롬프트 파일 로드 실패 ({prompt_file}): {e}")
    
    def get_prompt(self, name: Optional[str] = None) -> Optional[str]:
        """
        지정된 프롬프트 내용 반환
        
        Args:
            name: 프롬프트 이름 (None이면 기본 프롬프트)
            
        Returns:
            프롬프트 내용 또는 None
        """
        if name is None:
            name = self.default_prompt
        
        # 파일에서 프롬프트 재로드 시도 (항상 최신 내용 반영)
        if name == "default":
            prompt_file = self.prompt_dir / "prompt_default.txt"
            if prompt_file.exists():
                try:
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if content:
                        return content
                except Exception as e:
                    print(f"⚠️ default 프롬프트 파일 읽기 실패: {e}")
        
        template = self.prompts.get(name)
        if template:
            return template.content
        
        # 기본 프롬프트도 없으면 하드코딩된 기본값 반환
        if name == self.default_prompt:
            return self._get_hardcoded_default()
        
        return None
    
    def get_prompt_template(self, name: str) -> Optional[PromptTemplate]:
        """프롬프트 템플릿 객체 반환"""
        return self.prompts.get(name)
    
    def list_prompts(self) -> List[PromptTemplate]:
        """사용 가능한 모든 프롬프트 목록 반환"""
        return list(self.prompts.values())
    
    def get_prompt_choices(self) -> Dict[str, str]:
        """프롬프트 선택지 딕셔너리 반환 (이름: 설명)"""
        return {
            template.name: template.description
            for template in self.prompts.values()
        }
    
    def set_default_prompt(self, name: str) -> bool:
        """
        기본 프롬프트 설정
        
        Args:
            name: 기본으로 설정할 프롬프트 이름
            
        Returns:
            성공 여부
        """
        if name in self.prompts:
            self.default_prompt = name
            return True
        return False
    
    def reload_prompts(self):
        """프롬프트 파일들을 다시 로드"""
        self.prompts.clear()
        self._load_prompts()
    
    @property
    def templates(self) -> Dict[str, PromptTemplate]:
        """프롬프트 템플릿 딕셔너리 반환 (API 호환성을 위한 프로퍼티)"""
        return self.prompts if self.prompts is not None else {}
    
    def _get_hardcoded_default(self) -> str:
        """하드코딩된 기본 프롬프트 (파일이 없을 경우 폴백)"""
        # prompt_default.txt 내용을 직접 반영
        return """# Pharmaceutical Competitive Landscape Analysis Guide

## Overview

This guide provides comprehensive instructions for conducting competitive landscape analyses in pharmaceutical and biotechnology sectors, focusing on specific targets, mechanisms of action (MoA), or therapeutic indications.

## Section 1: Analysis for Specific Target or MoA

### 1. Literature Review Search Strategy

**Search Parameters:**

- Primary search: "[Target Name]" AND "Review"
- Time frame: Last 3-5 years only
- Focus: Review articles exclusively (exclude primary research papers)

**Exclusion Criteria:**

- Reviews authored by researchers from Iranian or Indian academic institutions or medical centers
- Primary research papers (due to potential retraction risks at this stage)

### 2. Competitive Landscape Development

**Essential Data Points:**

- **INN** (International Nonproprietary Name)
- **Brand names/Development codes** (multiple possible due to licensing - search all variants)
- **Developer(s)/Company(ies)**
- **Target specificity** (verify detailed subtypes)
- **Indications** (approved and in development)
- **Combination therapies** (specify combination drugs by indication)
- **Industry collaborators** (by indication)
- **Dosing and regimen**
- **Latest development stage** (by indication)
- **Patent information**

**Class-Specific Factors for Differentiation Analysis:**

- Efficacy parameters
- Safety profile and toxicity data
- Production specifications (host systems, manufacturing processes)
- Formulation details
- Dosing and administration regimen

### 3. Reference Sources

**Approved Drugs:**

- FDA Database: https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm
- EMA Database: https://www.ema.europa.eu/en/medicines

**Clinical Development:**

- ClinicalTrials.gov
- WHO International Clinical Trials Registry: trialsearch.who.int

**Patent Research:**

- KIPRIS (Korea): https://www.kipris.or.kr/khome/main.do
    - Search parameters:
        - Applicant: Development companies
        - Inventors: Executive team, Scientific Advisory Board (SAB), Technical/Science executives
        - University Technology Transfer Offices (TTOs) associated with SAB members
        - Claims analysis

**Additional Sources:**

- Company websites
- Google search (beyond news articles)
- Maximum 20 pages of Google results (extend to 40 pages if initial results are limited)

As GAIA-BT, I am an expert pharmaceutical research assistant that follows this comprehensive analysis framework for all drug development inquiries. I provide scientifically rigorous, evidence-based responses using systematic competitive intelligence methodologies."""


# 싱글톤 인스턴스
_prompt_manager_instance = None


def get_prompt_manager() -> PromptManager:
    """프롬프트 매니저 싱글톤 인스턴스 반환"""
    global _prompt_manager_instance
    if _prompt_manager_instance is None:
        _prompt_manager_instance = PromptManager()
    return _prompt_manager_instance


def get_system_prompt(prompt_type: Optional[str] = None) -> str:
    """
    시스템 프롬프트 가져오기 (간편 함수)
    
    Args:
        prompt_type: 프롬프트 타입 (None이면 기본값)
        
    Returns:
        시스템 프롬프트 내용
    """
    manager = get_prompt_manager()
    prompt = manager.get_prompt(prompt_type)
    
    if prompt is None:
        # 폴백: 기본 프롬프트 사용
        prompt = manager.get_prompt("default")
    
    return prompt or manager._get_hardcoded_default()