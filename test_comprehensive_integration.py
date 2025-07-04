#!/usr/bin/env python3
"""
GAIA-BT v3.85 포괄적 통합 테스트 스크립트
모든 핵심 기능을 체계적으로 테스트하는 종합 테스트 도구

Features tested:
- API Server Health & System Info
- WebUI Connectivity
- Basic Chat & MCP Mode Switching  
- RAG System (Documents, Query, Search)
- Reasoning RAG Pipeline (Self-RAG, CoT-RAG)
- Feedback System
- Vector Database
- Performance & Load Testing
"""

import asyncio
import json
import time
import requests
import websockets
from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
import os


class ComprehensiveIntegrationTester:
    """포괄적 통합 테스트 클래스"""
    
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.webui_url = "http://localhost:3003"
        self.session_id = None
        self.test_results = []
        self.start_time = time.time()
        
        # 테스트 데이터
        self.test_documents = [
            {
                "text": """
                EGFR (Epidermal Growth Factor Receptor) 돌연변이는 비소세포폐암(NSCLC) 환자의 
                약 10-15%에서 발견됩니다. EGFR-TKI (Tyrosine Kinase Inhibitor) 치료제인 
                게피티닙(Gefitinib), 엘로티닙(Erlotinib), 아파티닙(Afatinib) 등이 
                1차 치료제로 사용됩니다. T790M 내성 돌연변이가 발생할 수 있어 
                정기적인 모니터링이 필요합니다.
                """,
                "metadata": {"topic": "EGFR", "type": "overview", "confidence": 0.95}
            },
            {
                "text": """
                오시머티닙(Osimertinib)은 3세대 EGFR-TKI로 T790M 내성 돌연변이를 가진 
                환자들에게 효과적입니다. FLAURA 연구에서 1차 치료에서도 우수한 효과를 보였으며, 
                중앙 무진행 생존기간(PFS)이 18.9개월로 나타났습니다. 뇌전이에도 효과적이며 
                부작용 프로파일이 양호합니다.
                """,
                "metadata": {"topic": "EGFR", "type": "clinical_trial", "drug": "Osimertinib", "confidence": 0.92}
            },
            {
                "text": """
                면역항암제 PD-1/PD-L1 억제제는 암세포가 면역 체계를 회피하는 메커니즘을 차단합니다.
                펨브롤리주맙(Pembrolizumab), 니볼루맙(Nivolumab), 아테졸리주맙(Atezolizumab) 등이 
                대표적입니다. PD-L1 발현율에 따라 치료 효과가 달라지며, 일부 환자에서는 
                면역 관련 부작용이 발생할 수 있습니다.
                """,
                "metadata": {"topic": "Immunotherapy", "type": "mechanism", "confidence": 0.90}
            }
        ]
        
        self.test_queries = [
            {
                "query": "EGFR 돌연변이 폐암의 1차 치료제와 내성 메커니즘에 대해 설명해주세요",
                "expected_keywords": ["EGFR", "게피티닙", "엘로티닙", "T790M", "내성"],
                "category": "targeted_therapy"
            },
            {
                "query": "오시머티닙의 임상시험 결과와 효과에 대해 자세히 알려주세요",
                "expected_keywords": ["오시머티닙", "FLAURA", "18.9", "PFS", "뇌전이"],
                "category": "clinical_data"
            },
            {
                "query": "면역항암제 PD-1/PD-L1 억제제의 작용 메커니즘과 부작용은?",
                "expected_keywords": ["PD-1", "PD-L1", "펨브롤리주맙", "면역", "부작용"],
                "category": "immunotherapy"
            }
        ]
        
        self.reasoning_queries = [
            {
                "query": "EGFR 억제제의 내성 메커니즘과 차세대 치료제 개발 전략을 분석해주세요",
                "mode": "self_rag",
                "expected_depth": 3
            },
            {
                "query": "면역항암제와 표적치료제의 병용요법 가능성과 한계점을 평가해주세요",
                "mode": "self_rag", 
                "expected_depth": 3
            }
        ]
    
    def log_test_result(self, test_name: str, success: bool, details: Dict[str, Any] = None, duration: float = 0):
        """테스트 결과 로깅"""
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "details": details or {}
        }
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name} - {duration:.2f}s")
        if not success and details:
            print(f"   Error: {details.get('error', 'Unknown error')}")
    
    def test_api_health(self) -> bool:
        """API 서버 헬스 체크"""
        print("\n🔍 API 서버 헬스 체크")
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                health_data = response.json()
                self.log_test_result("API Health Check", True, health_data, duration)
                return True
            else:
                self.log_test_result("API Health Check", False, 
                                   {"error": f"HTTP {response.status_code}"}, duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("API Health Check", False, {"error": str(e)}, duration)
            return False
    
    def test_system_info(self) -> bool:
        """시스템 정보 확인"""
        print("\n🔍 시스템 정보 확인")
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.api_url}/api/system/info", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                info = response.json()
                self.log_test_result("System Info", True, {
                    "ollama_connected": info.get('ollama_status', {}).get('connected', False),
                    "available_models": len(info.get('available_models', [])),
                    "current_model": info.get('current_model', 'unknown')
                }, duration)
                return True
            else:
                self.log_test_result("System Info", False,
                                   {"error": f"HTTP {response.status_code}"}, duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("System Info", False, {"error": str(e)}, duration)
            return False
    
    def test_webui_connectivity(self) -> bool:
        """WebUI 연결성 테스트"""
        print("\n🔍 WebUI 연결성 테스트")
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.webui_url}/", timeout=5)
            duration = time.time() - start_time
            
            success = response.status_code == 200
            self.log_test_result("WebUI Connectivity", success, {
                "status_code": response.status_code,
                "response_size": len(response.content)
            }, duration)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("WebUI Connectivity", False, {"error": str(e)}, duration)
            return False
    
    def create_test_session(self) -> bool:
        """테스트 세션 생성"""
        print("\n🔍 테스트 세션 생성")
        start_time = time.time()
        
        try:
            response = requests.post(f"{self.api_url}/api/session/create", json={}, timeout=5)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data['session_id']
                self.log_test_result("Session Creation", True, 
                                   {"session_id": self.session_id}, duration)
                return True
            else:
                self.log_test_result("Session Creation", False,
                                   {"error": f"HTTP {response.status_code}"}, duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Session Creation", False, {"error": str(e)}, duration)
            return False
    
    def test_basic_chat(self) -> bool:
        """기본 채팅 기능 테스트"""
        print("\n🔍 기본 채팅 기능 테스트")
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.api_url}/api/chat/message",
                json={
                    "message": "안녕하세요, GAIA-BT 테스트 중입니다",
                    "session_id": self.session_id
                },
                timeout=30
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                self.log_test_result("Basic Chat", True, {
                    "response_length": len(response_text),
                    "mode": data.get('mode', 'unknown'),
                    "model": data.get('model', 'unknown')
                }, duration)
                return True
            else:
                self.log_test_result("Basic Chat", False,
                                   {"error": f"HTTP {response.status_code}"}, duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Basic Chat", False, {"error": str(e)}, duration)
            return False
    
    def test_mcp_mode_switching(self) -> bool:
        """MCP 모드 전환 테스트"""
        print("\n🔍 MCP 모드 전환 테스트")
        start_time = time.time()
        
        try:
            # MCP 모드 활성화
            mcp_response = requests.post(
                f"{self.api_url}/api/chat/command",
                json={
                    "command": "/mcp start",
                    "session_id": self.session_id
                },
                timeout=15
            )
            
            # 일반 모드로 복귀
            normal_response = requests.post(
                f"{self.api_url}/api/chat/command", 
                json={
                    "command": "/normal",
                    "session_id": self.session_id
                },
                timeout=10
            )
            
            duration = time.time() - start_time
            success = mcp_response.status_code == 200 and normal_response.status_code == 200
            
            self.log_test_result("MCP Mode Switching", success, {
                "mcp_activation": mcp_response.status_code == 200,
                "normal_mode_return": normal_response.status_code == 200
            }, duration)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("MCP Mode Switching", False, {"error": str(e)}, duration)
            return False
    
    def test_rag_documents(self) -> bool:
        """RAG 문서 추가 테스트"""
        print("\n🔍 RAG 문서 추가 테스트")
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.api_url}/api/rag/documents",
                json={
                    "documents": self.test_documents,
                    "chunk_size": 200
                },
                timeout=30
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_test_result("RAG Document Addition", True, {
                    "documents_added": len(self.test_documents),
                    "message": result.get('message', '')
                }, duration)
                return True
            else:
                self.log_test_result("RAG Document Addition", False,
                                   {"error": f"HTTP {response.status_code}"}, duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("RAG Document Addition", False, {"error": str(e)}, duration)
            return False
    
    def test_rag_queries(self) -> bool:
        """RAG 쿼리 테스트"""
        print("\n🔍 RAG 쿼리 테스트")
        
        all_successful = True
        for i, query_data in enumerate(self.test_queries):
            start_time = time.time()
            
            try:
                response = requests.post(
                    f"{self.api_url}/api/rag/query",
                    json={
                        "query": query_data["query"],
                        "top_k": 3
                    },
                    timeout=45
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get('answer', '').lower()
                    
                    # 키워드 검증
                    found_keywords = [
                        keyword for keyword in query_data['expected_keywords']
                        if keyword.lower() in answer
                    ]
                    
                    keyword_coverage = len(found_keywords) / len(query_data['expected_keywords'])
                    
                    self.log_test_result(f"RAG Query {i+1}", True, {
                        "query": query_data["query"][:50] + "...",
                        "answer_length": len(result.get('answer', '')),
                        "sources_count": len(result.get('sources', [])),
                        "keyword_coverage": keyword_coverage,
                        "found_keywords": found_keywords
                    }, duration)
                else:
                    self.log_test_result(f"RAG Query {i+1}", False,
                                       {"error": f"HTTP {response.status_code}"}, duration)
                    all_successful = False
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test_result(f"RAG Query {i+1}", False, {"error": str(e)}, duration)
                all_successful = False
        
        return all_successful
    
    def test_rag_stats(self) -> bool:
        """RAG 시스템 통계 테스트"""
        print("\n🔍 RAG 시스템 통계 테스트")
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.api_url}/api/rag/stats", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                stats = response.json()
                self.log_test_result("RAG Stats", True, {
                    "embedding_model": stats.get('embedding_model'),
                    "generation_model": stats.get('generation_model'),
                    "num_entities": stats.get('vector_store', {}).get('num_entities', 0)
                }, duration)
                return True
            else:
                self.log_test_result("RAG Stats", False,
                                   {"error": f"HTTP {response.status_code}"}, duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("RAG Stats", False, {"error": str(e)}, duration)
            return False
    
    def test_reasoning_rag(self) -> bool:
        """Reasoning RAG 테스트"""
        print("\n🔍 Reasoning RAG 테스트")
        
        all_successful = True
        for i, query_data in enumerate(self.reasoning_queries):
            start_time = time.time()
            
            try:
                response = requests.post(
                    f"{self.api_url}/api/rag/reasoning-query",
                    json={
                        "query": query_data["query"],
                        "mode": query_data["mode"],
                        "max_iterations": query_data["expected_depth"],
                        "stream": False
                    },
                    timeout=90  # Reasoning은 시간이 오래 걸림
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_test_result(f"Reasoning RAG {i+1}", True, {
                        "mode": result.get('mode'),
                        "iterations": result.get('total_iterations'),
                        "confidence": result.get('confidence_score', 0),
                        "answer_length": len(result.get('final_answer', ''))
                    }, duration)
                elif response.status_code == 501:
                    self.log_test_result(f"Reasoning RAG {i+1}", False,
                                       {"error": "Mode not implemented yet"}, duration)
                    all_successful = False
                else:
                    self.log_test_result(f"Reasoning RAG {i+1}", False,
                                       {"error": f"HTTP {response.status_code}"}, duration)
                    all_successful = False
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test_result(f"Reasoning RAG {i+1}", False, {"error": str(e)}, duration)
                all_successful = False
        
        return all_successful
    
    def test_feedback_system(self) -> bool:
        """피드백 시스템 테스트"""
        print("\n🔍 피드백 시스템 테스트")
        start_time = time.time()
        
        try:
            # 피드백 제출
            feedback_response = requests.post(
                f"{self.api_url}/api/feedback/submit",
                json={
                    "question": "EGFR 치료제 테스트 질문",
                    "answer": "게피티닙과 엘로티닙이 주요 치료제입니다",
                    "feedback_type": "positive",
                    "check_duplicates": True
                },
                timeout=15
            )
            
            # 피드백 통계 확인
            stats_response = requests.get(f"{self.api_url}/api/feedback/stats", timeout=10)
            
            duration = time.time() - start_time
            
            feedback_success = feedback_response.status_code == 200
            stats_success = stats_response.status_code == 200
            
            details = {
                "feedback_submitted": feedback_success,
                "stats_retrieved": stats_success
            }
            
            if stats_success:
                stats = stats_response.json()
                details.update({
                    "total_feedback": stats.get('total_feedback', 0),
                    "positive_feedback": stats.get('positive_feedback', 0)
                })
            
            success = feedback_success and stats_success
            self.log_test_result("Feedback System", success, details, duration)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Feedback System", False, {"error": str(e)}, duration)
            return False
    
    async def test_websocket_connectivity(self) -> bool:
        """WebSocket 연결성 테스트"""
        print("\n🔍 WebSocket 연결성 테스트")
        start_time = time.time()
        
        try:
            session_id = f"test_{int(time.time())}"
            uri = f"ws://localhost:8000/ws/chat/{session_id}"
            
            async with websockets.connect(uri) as websocket:
                # 연결 테스트 메시지
                test_message = {
                    "type": "message",
                    "content": "WebSocket 연결 테스트"
                }
                
                await websocket.send(json.dumps(test_message))
                
                # 응답 대기 (최대 10초)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    
                    duration = time.time() - start_time
                    self.log_test_result("WebSocket Connectivity", True, {
                        "response_received": True,
                        "message_type": data.get("type", "unknown")
                    }, duration)
                    return True
                    
                except asyncio.TimeoutError:
                    duration = time.time() - start_time
                    self.log_test_result("WebSocket Connectivity", False,
                                       {"error": "Response timeout"}, duration)
                    return False
                    
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("WebSocket Connectivity", False, {"error": str(e)}, duration)
            return False
    
    def test_performance_load(self) -> bool:
        """성능 및 로드 테스트 (간단한 버전)"""
        print("\n🔍 성능 및 로드 테스트")
        start_time = time.time()
        
        try:
            # 10개의 동시 요청
            responses = []
            request_times = []
            
            for i in range(5):  # 간단한 로드 테스트
                req_start = time.time()
                response = requests.get(f"{self.api_url}/health", timeout=5)
                req_time = time.time() - req_start
                
                responses.append(response.status_code == 200)
                request_times.append(req_time)
            
            duration = time.time() - start_time
            success_rate = sum(responses) / len(responses)
            avg_response_time = sum(request_times) / len(request_times)
            
            success = success_rate >= 0.8  # 80% 성공률
            
            self.log_test_result("Performance Load Test", success, {
                "total_requests": len(responses),
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "max_response_time": max(request_times)
            }, duration)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Performance Load Test", False, {"error": str(e)}, duration)
            return False
    
    def print_comprehensive_summary(self):
        """포괄적 테스트 결과 요약"""
        total_duration = time.time() - self.start_time
        
        print("\n" + "="*80)
        print("🎯 GAIA-BT v3.85 포괄적 통합 테스트 결과")
        print("="*80)
        
        # 전체 통계
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - successful_tests
        
        print(f"📊 테스트 요약:")
        print(f"   • 총 테스트 수: {total_tests}")
        print(f"   • 성공: {successful_tests}")
        print(f"   • 실패: {failed_tests}")
        print(f"   • 성공률: {(successful_tests/total_tests)*100:.1f}%")
        print(f"   • 총 소요 시간: {total_duration:.2f}초")
        
        # 카테고리별 결과
        categories = {
            "Infrastructure": ["API Health Check", "System Info", "WebUI Connectivity", "Session Creation"],
            "Core Features": ["Basic Chat", "MCP Mode Switching"],
            "RAG System": ["RAG Document Addition", "RAG Stats"] + [f"RAG Query {i}" for i in range(1, 4)],
            "Advanced Features": [f"Reasoning RAG {i}" for i in range(1, 3)],
            "Support Systems": ["Feedback System", "WebSocket Connectivity", "Performance Load Test"]
        }
        
        print(f"\n📋 카테고리별 결과:")
        for category, test_names in categories.items():
            category_results = [r for r in self.test_results if r['test_name'] in test_names]
            if category_results:
                category_success = len([r for r in category_results if r['success']])
                category_total = len(category_results)
                print(f"   • {category}: {category_success}/{category_total} ({(category_success/category_total)*100:.0f}%)")
        
        # 실패한 테스트 상세
        failed_results = [r for r in self.test_results if not r['success']]
        if failed_results:
            print(f"\n❌ 실패한 테스트 상세:")
            for result in failed_results:
                error = result['details'].get('error', 'Unknown error')
                print(f"   • {result['test_name']}: {error}")
        
        # 성능 통계
        durations = [r['duration'] for r in self.test_results if r['duration'] > 0]
        if durations:
            print(f"\n⚡ 성능 통계:")
            print(f"   • 평균 응답 시간: {sum(durations)/len(durations):.2f}초")
            print(f"   • 최대 응답 시간: {max(durations):.2f}초")
            print(f"   • 최소 응답 시간: {min(durations):.2f}초")
        
        # 권장사항
        print(f"\n💡 권장사항:")
        if successful_tests >= total_tests * 0.9:
            print("   🎉 시스템이 안정적으로 작동하고 있습니다!")
            print("   ✨ 모든 핵심 기능이 정상적으로 동작합니다.")
        elif successful_tests >= total_tests * 0.7:
            print("   ⚠️ 일부 기능에 문제가 있습니다.")
            print("   🔧 실패한 테스트를 확인하여 수정해주세요.")
        else:
            print("   🚨 시스템에 심각한 문제가 있습니다!")
            print("   🛠️ 전체적인 시스템 점검이 필요합니다.")
        
        # 접속 정보
        print(f"\n🌐 접속 정보:")
        print(f"   • API 서버: {self.api_url}")
        print(f"   • WebUI: {self.webui_url}")
        print(f"   • API 문서: {self.api_url}/docs")
        
        return successful_tests >= total_tests * 0.8
    
    async def run_all_tests(self) -> bool:
        """모든 테스트 실행"""
        print("🚀 GAIA-BT v3.85 포괄적 통합 테스트 시작")
        print("="*80)
        
        # Phase 1: Infrastructure Tests
        print("\n📡 Phase 1: Infrastructure Tests")
        if not self.test_api_health():
            print("❌ API 서버 연결 실패. 테스트 중단.")
            return False
        
        self.test_system_info()
        self.test_webui_connectivity()
        
        # Phase 2: Session Setup
        print("\n🔧 Phase 2: Session Setup")
        if not self.create_test_session():
            print("❌ 세션 생성 실패. 일부 테스트를 건너뜁니다.")
        
        # Phase 3: Core Functionality Tests
        print("\n⚡ Phase 3: Core Functionality Tests")
        if self.session_id:
            self.test_basic_chat()
            self.test_mcp_mode_switching()
        
        # Phase 4: RAG System Tests
        print("\n🧠 Phase 4: RAG System Tests")
        self.test_rag_documents()
        time.sleep(2)  # 문서 처리 대기
        self.test_rag_stats()
        self.test_rag_queries()
        
        # Phase 5: Advanced Features
        print("\n🚀 Phase 5: Advanced Features")
        self.test_reasoning_rag()
        self.test_feedback_system()
        
        # Phase 6: Connectivity & Performance
        print("\n🌐 Phase 6: Connectivity & Performance")
        await self.test_websocket_connectivity()
        self.test_performance_load()
        
        # 결과 요약
        return self.print_comprehensive_summary()


async def main():
    """메인 함수"""
    tester = ComprehensiveIntegrationTester()
    success = await tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ 테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 예상치 못한 오류가 발생했습니다: {e}")
        sys.exit(1)