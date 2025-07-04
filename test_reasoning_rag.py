#!/usr/bin/env python3
"""
Reasoning RAG Pipeline 테스트 스크립트
v3.85 Self-RAG 구현 테스트
"""

import asyncio
import json
import time
import requests
import websockets
from typing import Dict, Any

# API 설정
API_BASE_URL = "http://localhost:8000"
WEBSOCKET_URL = "ws://localhost:8000"

# 테스트 데이터
TEST_QUERIES = [
    {
        "query": "EGFR 억제제의 내성 메커니즘과 차세대 치료제 개발 전략은?",
        "mode": "self_rag",
        "expected_keywords": ["T790M", "돌연변이", "내성", "치료제"]
    },
    {
        "query": "알츠하이머병의 아밀로이드 가설과 최신 치료 접근법을 분석해주세요",
        "mode": "self_rag",
        "expected_keywords": ["아밀로이드", "베타", "플라크", "치료"]
    },
    {
        "query": "면역항암제 PD-1/PD-L1 억제제의 작용 메커니즘과 한계점은?",
        "mode": "self_rag",
        "expected_keywords": ["PD-1", "PD-L1", "면역", "항암제"]
    }
]


class ReasoningRAGTester:
    """Reasoning RAG 테스트 클래스"""
    
    def __init__(self):
        self.api_url = API_BASE_URL
        self.ws_url = WEBSOCKET_URL
        self.test_results = []
    
    def test_api_health(self) -> bool:
        """API 서버 상태 확인"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API 서버 연결 성공")
                return True
            else:
                print(f"❌ API 서버 응답 오류: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API 서버 연결 실패: {e}")
            return False
    
    def test_reasoning_stats(self) -> bool:
        """Reasoning RAG 통계 확인"""
        try:
            response = requests.get(f"{self.api_url}/api/rag/reasoning-stats", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                print("✅ Reasoning RAG 통계 조회 성공")
                print(f"   Pipeline Status: {stats.get('pipeline_status')}")
                print(f"   LLM Model: {stats.get('model_info', {}).get('llm')}")
                print(f"   Embedding Model: {stats.get('model_info', {}).get('embedding')}")
                print(f"   Reranker Device: {stats.get('reranker_info', {}).get('device')}")
                return True
            else:
                print(f"❌ Reasoning 통계 조회 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Reasoning 통계 오류: {e}")
            return False
    
    def test_reasoning_query_api(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """REST API를 통한 Reasoning RAG 테스트"""
        print(f"\n🧠 Testing Reasoning Query: {query_data['query'][:50]}...")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.api_url}/api/rag/reasoning-query",
                json={
                    "query": query_data["query"],
                    "mode": query_data["mode"],
                    "max_iterations": 3,
                    "stream": False
                },
                timeout=60  # 추론은 시간이 오래 걸릴 수 있음
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ Reasoning RAG 쿼리 성공")
                print(f"   Mode: {result.get('mode')}")
                print(f"   Iterations: {result.get('total_iterations')}")
                print(f"   Confidence: {result.get('confidence_score', 0):.2f}")
                print(f"   Elapsed Time: {result.get('elapsed_time', 0):.2f}s")
                print(f"   Final Answer: {result.get('final_answer', '')[:100]}...")
                
                # 키워드 검증
                answer = result.get('final_answer', '').lower()
                found_keywords = [
                    keyword for keyword in query_data['expected_keywords']
                    if keyword.lower() in answer
                ]
                
                print(f"   Found Keywords: {found_keywords}")
                
                return {
                    "success": True,
                    "response_time": elapsed_time,
                    "iterations": result.get('total_iterations'),
                    "confidence": result.get('confidence_score', 0),
                    "keywords_found": len(found_keywords),
                    "total_keywords": len(query_data['expected_keywords']),
                    "result": result
                }
            
            elif response.status_code == 501:
                print(f"⚠️ Mode not implemented: {response.json().get('detail')}")
                return {"success": False, "error": "not_implemented"}
            
            else:
                print(f"❌ API 오류: {response.status_code} - {response.text}")
                return {"success": False, "error": "api_error"}
                
        except Exception as e:
            print(f"❌ Reasoning 쿼리 실패: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_reasoning_websocket(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """WebSocket을 통한 실시간 Reasoning RAG 테스트"""
        print(f"\n🌐 Testing WebSocket Reasoning: {query_data['query'][:50]}...")
        
        session_id = f"test_{int(time.time())}"
        uri = f"{self.ws_url}/ws/reasoning/{session_id}"
        
        messages_received = []
        start_time = time.time()
        
        try:
            async with websockets.connect(uri) as websocket:
                # 연결 확인
                await asyncio.sleep(0.5)
                
                # 쿼리 전송
                query_message = {
                    "type": "reasoning_query",
                    "query": query_data["query"],
                    "mode": query_data["mode"],
                    "max_iterations": 3
                }
                
                await websocket.send(json.dumps(query_message))
                print("   📤 쿼리 전송 완료")
                
                # 응답 수신 (최대 60초)
                timeout_time = time.time() + 60
                
                while time.time() < timeout_time:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(message)
                        messages_received.append(data)
                        
                        msg_type = data.get("type")
                        
                        if msg_type == "reasoning_start":
                            print(f"   🚀 추론 시작: {data.get('mode')}")
                        
                        elif msg_type == "iteration_start":
                            print(f"   🔄 반복 {data.get('iteration', 0) + 1}/{data.get('max_iterations', 3)}")
                        
                        elif msg_type == "query_refined":
                            print(f"   🔍 쿼리 개선: {data.get('refined_query', '')[:50]}...")
                        
                        elif msg_type == "documents_retrieved":
                            print(f"   📚 문서 검색: {data.get('document_count')}개 (점수: {data.get('top_score', 0):.2f})")
                        
                        elif msg_type == "partial_answer":
                            print(f"   💭 부분 답변: {data.get('answer', '')[:50]}...")
                        
                        elif msg_type == "reasoning_complete":
                            elapsed_time = time.time() - start_time
                            print(f"   ✅ 추론 완료!")
                            print(f"   신뢰도: {data.get('confidence_score', 0):.2f}")
                            print(f"   처리 시간: {data.get('elapsed_time', 0):.2f}s")
                            break
                        
                        elif msg_type == "reasoning_error":
                            print(f"   ❌ 추론 오류: {data.get('error')}")
                            break
                    
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        print(f"   ⚠️ 메시지 수신 오류: {e}")
                        break
                
                total_time = time.time() - start_time
                
                # 결과 분석
                reasoning_complete = any(msg.get("type") == "reasoning_complete" for msg in messages_received)
                iteration_count = len([msg for msg in messages_received if msg.get("type") == "iteration_start"])
                
                return {
                    "success": reasoning_complete,
                    "total_time": total_time,
                    "messages_count": len(messages_received),
                    "iterations": iteration_count,
                    "messages": messages_received
                }
        
        except Exception as e:
            print(f"   ❌ WebSocket 연결 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 Reasoning RAG Pipeline 테스트 시작\n")
        
        # 1. API 서버 상태 확인
        if not self.test_api_health():
            print("❌ API 서버 연결 실패. 테스트 중단.")
            return
        
        # 2. Reasoning 통계 확인
        if not self.test_reasoning_stats():
            print("⚠️ Reasoning 통계 확인 실패. 테스트 계속 진행.")
        
        # 3. REST API 테스트
        print("\n" + "="*60)
        print("📡 REST API 테스트")
        print("="*60)
        
        api_results = []
        for i, query_data in enumerate(TEST_QUERIES):
            result = self.test_reasoning_query_api(query_data)
            api_results.append(result)
            
            if i < len(TEST_QUERIES) - 1:
                print("   ⏱️ 다음 테스트까지 5초 대기...")
                time.sleep(5)
        
        # 4. WebSocket 테스트
        print("\n" + "="*60)
        print("🌐 WebSocket 테스트")
        print("="*60)
        
        async def run_websocket_tests():
            ws_results = []
            for i, query_data in enumerate(TEST_QUERIES[:2]):  # WebSocket은 2개만 테스트
                result = await self.test_reasoning_websocket(query_data)
                ws_results.append(result)
                
                if i < 1:  # 마지막이 아니면 대기
                    print("   ⏱️ 다음 테스트까지 5초 대기...")
                    await asyncio.sleep(5)
            
            return ws_results
        
        ws_results = asyncio.run(run_websocket_tests())
        
        # 5. 결과 요약
        self.print_test_summary(api_results, ws_results)
    
    def print_test_summary(self, api_results, ws_results):
        """테스트 결과 요약"""
        print("\n" + "="*60)
        print("📊 테스트 결과 요약")
        print("="*60)
        
        # API 테스트 결과
        api_success = sum(1 for r in api_results if r.get("success"))
        print(f"📡 REST API 테스트: {api_success}/{len(api_results)} 성공")
        
        if api_success > 0:
            avg_time = sum(r.get("response_time", 0) for r in api_results if r.get("success")) / api_success
            avg_confidence = sum(r.get("confidence", 0) for r in api_results if r.get("success")) / api_success
            avg_iterations = sum(r.get("iterations", 0) for r in api_results if r.get("success")) / api_success
            
            print(f"   평균 응답 시간: {avg_time:.2f}초")
            print(f"   평균 신뢰도: {avg_confidence:.2f}")
            print(f"   평균 반복 횟수: {avg_iterations:.1f}")
        
        # WebSocket 테스트 결과
        ws_success = sum(1 for r in ws_results if r.get("success"))
        print(f"🌐 WebSocket 테스트: {ws_success}/{len(ws_results)} 성공")
        
        if ws_success > 0:
            avg_ws_time = sum(r.get("total_time", 0) for r in ws_results if r.get("success")) / ws_success
            avg_messages = sum(r.get("messages_count", 0) for r in ws_results if r.get("success")) / ws_success
            
            print(f"   평균 처리 시간: {avg_ws_time:.2f}초")
            print(f"   평균 메시지 수: {avg_messages:.1f}개")
        
        # 전체 결과
        total_success = api_success + ws_success
        total_tests = len(api_results) + len(ws_results)
        
        print(f"\n🎯 전체 성공률: {total_success}/{total_tests} ({100*total_success/total_tests:.1f}%)")
        
        if total_success == total_tests:
            print("🎉 모든 테스트 통과!")
        elif total_success > total_tests * 0.7:
            print("✅ 대부분의 테스트 통과")
        else:
            print("⚠️ 일부 테스트 실패 - 시스템 점검 필요")


def main():
    """메인 함수"""
    print("🔬 GAIA-BT v3.85 Reasoning RAG Pipeline 테스트")
    print("=" * 60)
    
    tester = ReasoningRAGTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()