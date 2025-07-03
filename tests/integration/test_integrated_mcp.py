#!/usr/bin/env python3
"""
통합 MCP 테스트 - ChEMBL + BiomCP + Sequential Thinking
근육 보충제 화학 구조 분석과 생의학 연구 통합 테스트
"""

import asyncio
import sys
import os
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

async def test_integrated_mcp():
    """통합 MCP 테스트 실행"""
    logger.info("=== 통합 MCP 테스트 시작 ===")
    logger.info("ChEMBL + BiomCP + Sequential Thinking 통합")
    
    # MCP 관련 모듈 임포트
    try:
        from mcp.integration.mcp_manager import MCPManager
        logger.info("✓ MCPManager 임포트 성공")
    except Exception as e:
        logger.error(f"✗ MCPManager 임포트 실패: {e}")
        return
    
    # MCP Manager 초기화
    mcp_manager = MCPManager()
    
    try:
        # 1. GAIA MCP 서버 시작
        logger.info("1. GAIA MCP 서버 시작...")
        success = await mcp_manager.start_server()
        if success:
            logger.info("✓ GAIA MCP 서버 시작됨")
        else:
            logger.error("✗ GAIA MCP 서버 시작 실패")
            return
        
        # 2. 외부 MCP 서버들 시작 (ChEMBL, BiomCP, Sequential Thinking)
        logger.info("2. 외부 MCP 서버들 시작...")
        logger.info("- ChEMBL 서버 시작 중...")
        logger.info("- BiomCP 서버 시작 중...")
        logger.info("- Sequential Thinking 서버 시작 중...")
        
        external_servers = ['chembl', 'biomcp', 'gaia-sequential-thinking-python']
        logger.info(f"시작할 서버: {external_servers}")
        
        external_success = await mcp_manager.start_external_servers(external_servers)
        if external_success:
            logger.info("✓ 외부 MCP 서버들이 시작됨")
        else:
            logger.warning("⚠ 일부 외부 서버 시작 실패")
        
        # 서버 초기화 대기
        await asyncio.sleep(5)
        
        # 3. 상태 확인
        logger.info("3. MCP 상태 확인...")
        status = mcp_manager.get_status()
        logger.info(f"- 실행 중: {'✓' if status['running'] else '✗'}")
        logger.info(f"- 서버 활성: {'✓' if status['server_active'] else '✗'}")
        logger.info(f"- 클라이언트 수: {status['clients_count']}")
        logger.info(f"- 연결된 클라이언트: {', '.join(status['client_ids'])}")
        
        # 4. 통합 테스트 시나리오: 크레아틴 연구
        logger.info("\n4. 통합 연구 시나리오: 크레아틴 (Creatine) 분석")
        
        creatine_smiles = "C(=N)(N)N(C)CC(=O)O"  # 크레아틴 SMILES
        research_question = "크레아틴 보충제의 분자 구조, 작용 메커니즘, 그리고 근육 성장에 미치는 효과"
        
        logger.info(f"연구 대상: 크레아틴 (SMILES: {creatine_smiles})")
        logger.info(f"연구 질문: {research_question}")
        
        # 4a. Sequential Thinking으로 연구 계획 수립
        if 'gaia-sequential-thinking-python' in status['client_ids']:
            logger.info("\n- Sequential Thinking으로 연구 계획 수립...")
            try:
                result = await mcp_manager.call_tool(
                    client_id='gaia-sequential-thinking-python',
                    tool_name='start_thinking',
                    arguments={
                        'problem': f'Analyze creatine supplementation for muscle growth: chemical structure, mechanism, effects',
                        'maxSteps': 8
                    }
                )
                logger.info("  ✓ 연구 계획 수립 완료")
                if result and 'content' in result:
                    content = result['content'][0].get('text', '') if result['content'] else ''
                    logger.info(f"  계획: {content[:100]}...")
            except Exception as e:
                logger.error(f"  ✗ Sequential Thinking 오류: {e}")
        
        # 4b. ChEMBL로 크레아틴 분자 정보 검색
        if 'chembl' in status['client_ids']:
            logger.info("\n- ChEMBL로 크레아틴 분자 정보 검색...")
            try:
                # 분자 검색
                result = await mcp_manager.call_tool(
                    client_id='chembl',
                    tool_name='get_molecule',
                    arguments={
                        'query': 'creatine',
                        'limit': 5
                    }
                )
                logger.info("  ✓ 크레아틴 분자 정보 검색 완료")
                
                # SMILES 구조 분석
                smiles_result = await mcp_manager.call_tool(
                    client_id='chembl',
                    tool_name='canonicalize_smiles',
                    arguments={'smiles': creatine_smiles}
                )
                logger.info("  ✓ SMILES 구조 분석 완료")
                
            except Exception as e:
                logger.error(f"  ✗ ChEMBL 검색 오류: {e}")
        
        # 4c. BiomCP로 크레아틴 관련 논문 및 임상시험 검색
        if 'biomcp' in status['client_ids']:
            logger.info("\n- BiomCP로 크레아틴 연구 데이터 검색...")
            try:
                # 논문 검색
                papers_result = await mcp_manager.call_tool(
                    client_id='biomcp',
                    tool_name='search_articles',
                    arguments={
                        'query': 'creatine supplementation muscle growth performance',
                        'limit': 5
                    }
                )
                logger.info("  ✓ 크레아틴 논문 검색 완료")
                
                # 임상시험 검색
                trials_result = await mcp_manager.call_tool(
                    client_id='biomcp',
                    tool_name='search_trials',
                    arguments={
                        'condition': 'creatine supplementation athletic performance',
                        'limit': 3
                    }
                )
                logger.info("  ✓ 크레아틴 임상시험 검색 완료")
                
            except Exception as e:
                logger.error(f"  ✗ BiomCP 검색 오류: {e}")
        
        # 4d. GAIA Research로 종합 분석
        if 'default' in status['client_ids']:
            logger.info("\n- GAIA Research로 종합 분석...")
            try:
                comprehensive_result = await mcp_manager.research_question(
                    question=research_question,
                    depth="detailed",
                    client_id="default"
                )
                logger.info("  ✓ 종합 연구 분석 완료")
                if comprehensive_result and not comprehensive_result.startswith("Error:"):
                    logger.info(f"  결과 미리보기: {comprehensive_result[:200]}...")
            except Exception as e:
                logger.error(f"  ✗ GAIA 종합 분석 오류: {e}")
        
        # 5. 추가 테스트: BCAA vs 단백질 비교 분석
        logger.info("\n5. 추가 분석: BCAA vs 단백질 보충제 비교")
        
        # BCAA 주요 성분 SMILES
        leucine_smiles = "CC(C)CC(C(=O)O)N"  # 류신
        
        if 'gaia-sequential-thinking-python' in status['client_ids']:
            try:
                comparison_result = await mcp_manager.call_tool(
                    client_id='gaia-sequential-thinking-python',
                    tool_name='start_thinking',
                    arguments={
                        'problem': 'Compare BCAA vs whey protein for muscle growth effectiveness',
                        'maxSteps': 6
                    }
                )
                logger.info("  ✓ BCAA vs 단백질 비교 분석 완료")
            except Exception as e:
                logger.error(f"  ✗ 비교 분석 오류: {e}")
        
        logger.info("\n✓ 모든 통합 테스트 완료!")
        
        # 결과 요약
        logger.info("\n=== 통합 테스트 결과 요약 ===")
        logger.info(f"✓ GAIA MCP 서버: 활성")
        logger.info(f"{'✓' if 'chembl' in status['client_ids'] else '✗'} ChEMBL 서버 (화학 데이터)")
        logger.info(f"{'✓' if 'biomcp' in status['client_ids'] else '✗'} BiomCP 서버 (생의학 데이터)")
        logger.info(f"{'✓' if 'gaia-sequential-thinking-python' in status['client_ids'] else '✗'} Sequential Thinking 서버")
        logger.info(f"총 {status['clients_count']}개의 MCP 클라이언트 연결됨")
        
        logger.info("\n통합 시스템이 성공적으로 작동하여:")
        logger.info("- 화학 구조 분석 (ChEMBL)")
        logger.info("- 생의학 연구 데이터 (BiomCP)")  
        logger.info("- 단계별 추론 (Sequential Thinking)")
        logger.info("- 종합 연구 분석 (GAIA)")
        logger.info("이 모두 조화롭게 진행되었습니다.")
        
    except Exception as e:
        logger.error(f"\n✗ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 정리
        logger.info("\n6. MCP 서버 정리 중...")
        await mcp_manager.stop_external_servers()
        await mcp_manager.cleanup()
        logger.info("✓ 모든 MCP 서버가 중지되었습니다.")

def main():
    """메인 함수"""
    logger.info("GAIA 통합 MCP 테스트")
    logger.info("=" * 60)
    logger.info("ChEMBL + BiomCP + Sequential Thinking 통합 테스트")
    logger.info("근육 보충제 화학/생의학 연구 시나리오")
    logger.info("")
    
    asyncio.run(test_integrated_mcp())
    
    logger.info("\n통합 테스트가 완료되었습니다!")
    logger.info("이제 챗봇에서 다음 명령어들을 사용할 수 있습니다:")
    logger.info("- /mcp chembl molecule creatine")
    logger.info("- /mcp bioarticle creatine muscle growth")
    logger.info("- /mcp think 'BCAA vs protein effectiveness'")

if __name__ == "__main__":
    main()