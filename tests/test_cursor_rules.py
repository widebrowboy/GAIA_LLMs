#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
근육 관련 건강기능식품 연구 시스템의 테스트 모듈입니다.

이 모듈은 커서 룰이 제대로 적용되는지 테스트하기 위한 샘플 코드를 포함합니다.
"""

from typing import List, Dict, Optional
import asyncio
from datetime import datetime


class HealthSupplement:
    """건강기능식품 정보를 관리하는 클래스입니다."""

    def __init__(self, name: str, ingredients: List[str], effects: List[str]) -> None:
        """
        건강기능식품 객체를 초기화합니다.

        Args:
            name (str): 건강기능식품의 이름
            ingredients (List[str]): 주요 성분 목록
            effects (List[str]): 주요 효과 목록
        """
        self.name = name
        self.ingredients = ingredients
        self.effects = effects
        self.created_at = datetime.now()

    async def analyze_effects(self) -> Dict[str, List[str]]:
        """
        건강기능식품의 효과를 분석합니다.

        Returns:
            Dict[str, List[str]]: 분석된 효과 정보
        """
        # 실제 구현에서는 Ollama API를 호출하여 분석
        return {
            "primary_effects": self.effects,
            "secondary_effects": [],
            "interactions": []
        }


class ResearchManager:
    """연구 관리 클래스입니다."""

    def __init__(self) -> None:
        """연구 관리자를 초기화합니다."""
        self.supplements: List[HealthSupplement] = []

    async def add_supplement(
        self, name: str, ingredients: List[str], effects: List[str]
    ) -> HealthSupplement:
        """
        새로운 건강기능식품을 추가합니다.

        Args:
            name (str): 건강기능식품의 이름
            ingredients (List[str]): 주요 성분 목록
            effects (List[str]): 주요 효과 목록

        Returns:
            HealthSupplement: 추가된 건강기능식품 객체
        """
        supplement = HealthSupplement(name, ingredients, effects)
        self.supplements.append(supplement)
        return supplement

    async def research_supplement(
        self, supplement: HealthSupplement
    ) -> Dict[str, any]:
        """
        건강기능식품에 대한 연구를 수행합니다.

        Args:
            supplement (HealthSupplement): 연구할 건강기능식품 객체

        Returns:
            Dict[str, any]: 연구 결과
        """
        effects = await supplement.analyze_effects()
        return {
            "name": supplement.name,
            "analysis": effects,
            "timestamp": datetime.now().isoformat()
        }


async def main() -> None:
    """메인 실행 함수입니다."""
    manager = ResearchManager()
    
    # 테스트용 건강기능식품 추가
    supplement = await manager.add_supplement(
        name="프로틴 파우더",
        ingredients=["유청 단백질", "BCAA", "글루타민"],
        effects=["근육 성장", "회복력 향상", "지구력 증가"]
    )
    
    # 연구 수행
    result = await manager.research_supplement(supplement)
    print(f"연구 결과: {result}")


if __name__ == "__main__":
    asyncio.run(main()) 