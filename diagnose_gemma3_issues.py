#!/usr/bin/env python3
"""
Gemma3:27b-it-q4_K_M 모델 문제 진단 스크립트
"""

import asyncio
import httpx
import json
import time
import psutil
import subprocess
from datetime import datetime

# 색상 코드
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"

class Gemma3Diagnostics:
    def __init__(self):
        self.model_name = "Gemma3:27b-it-q4_K_M"
        
    def check_system_resources(self):
        """시스템 리소스 확인"""
        print(f"{BLUE}=== 시스템 리소스 분석 ==={RESET}")
        
        # CPU 정보
        cpu_count = psutil.cpu_count()
        cpu_usage = psutil.cpu_percent(interval=1)
        print(f"CPU 코어: {cpu_count}개")
        print(f"CPU 사용률: {cpu_usage:.1f}%")
        
        # 메모리 정보
        memory = psutil.virtual_memory()
        memory_total = memory.total / (1024**3)  # GB
        memory_used = memory.used / (1024**3)   # GB
        memory_available = memory.available / (1024**3)  # GB
        
        print(f"총 메모리: {memory_total:.1f}GB")
        print(f"사용 중: {memory_used:.1f}GB ({memory.percent:.1f}%)")
        print(f"사용 가능: {memory_available:.1f}GB")
        
        # GPU 정보 (nvidia-smi 사용)
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total,memory.used,memory.free', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                gpu_info = result.stdout.strip().split('\n')[0].split(', ')
                gpu_total = int(gpu_info[0]) / 1024  # GB
                gpu_used = int(gpu_info[1]) / 1024   # GB
                gpu_free = int(gpu_info[2]) / 1024   # GB
                
                print(f"GPU 메모리 (총): {gpu_total:.1f}GB")
                print(f"GPU 메모리 (사용): {gpu_used:.1f}GB")
                print(f"GPU 메모리 (여유): {gpu_free:.1f}GB")
                
                # 27B 모델에 필요한 최소 메모리 (16-20GB)
                min_required = 16
                if gpu_free < min_required:
                    print(f"{RED}⚠️  GPU 메모리 부족! 최소 {min_required}GB 필요, 현재 {gpu_free:.1f}GB 여유{RESET}")
                    return False
                else:
                    print(f"{GREEN}✓ GPU 메모리 충분{RESET}")
            else:
                print(f"{YELLOW}GPU 정보를 가져올 수 없습니다{RESET}")
        except FileNotFoundError:
            print(f"{YELLOW}nvidia-smi를 찾을 수 없습니다{RESET}")
        
        # 메모리 권장사항
        min_ram_required = 32  # 27B 모델 권장 RAM
        if memory_total < min_ram_required:
            print(f"{RED}⚠️  RAM 부족! 권장 {min_ram_required}GB, 현재 {memory_total:.1f}GB{RESET}")
            return False
        elif memory_available < 16:
            print(f"{YELLOW}⚠️  사용 가능한 RAM이 적습니다. {memory_available:.1f}GB{RESET}")
            return False
        else:
            print(f"{GREEN}✓ RAM 충분{RESET}")
            
        return True
    
    async def test_model_loading_time(self):
        """모델 로딩 시간 측정"""
        print(f"\n{BLUE}=== 모델 로딩 시간 분석 ==={RESET}")
        
        try:
            # 1. 현재 로드된 모델 확인
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("http://localhost:11434/api/ps")
                loaded_models = response.json().get('models', [])
                
                model_loaded = any(model['name'] == self.model_name for model in loaded_models)
                print(f"모델 로드 상태: {'로드됨' if model_loaded else '언로드됨'}")
                
                if model_loaded:
                    for model in loaded_models:
                        if model['name'] == self.model_name:
                            print(f"메모리 사용량: {model.get('size', 'unknown')}")
                            print(f"로드 시간: {model.get('modified', 'unknown')}")
            
            # 2. 콜드 스타트 테스트 (모델이 언로드된 상태에서)
            if not model_loaded:
                print(f"{YELLOW}콜드 스타트 테스트 중... (최대 5분){RESET}")
                start_time = time.time()
                
                async with httpx.AsyncClient(timeout=300.0) as client:
                    response = await client.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": self.model_name,
                            "prompt": "Hello",
                            "stream": False,
                            "options": {"num_predict": 1}
                        }
                    )
                    
                    end_time = time.time()
                    loading_time = end_time - start_time
                    
                    if response.status_code == 200:
                        print(f"{GREEN}✓ 모델 로딩 성공{RESET}")
                        print(f"로딩 시간: {loading_time:.2f}초")
                        
                        if loading_time > 120:  # 2분 이상
                            print(f"{RED}⚠️  로딩 시간이 너무 깁니다 ({loading_time:.2f}초){RESET}")
                            return False
                        elif loading_time > 60:  # 1분 이상
                            print(f"{YELLOW}⚠️  로딩 시간이 깁니다 ({loading_time:.2f}초){RESET}")
                        
                        return True
                    else:
                        print(f"{RED}✗ 모델 로딩 실패: {response.status_code}{RESET}")
                        return False
            
            # 3. 웜 스타트 테스트 (모델이 이미 로드된 상태)
            print(f"{YELLOW}웜 스타트 테스트 중...{RESET}")
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": "Hello",
                        "stream": False,
                        "options": {"num_predict": 10}
                    }
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    print(f"{GREEN}✓ 웜 스타트 성공{RESET}")
                    print(f"응답 시간: {response_time:.2f}초")
                    
                    if response_time > 30:
                        print(f"{RED}⚠️  응답 시간이 너무 깁니다 ({response_time:.2f}초){RESET}")
                        return False
                    elif response_time > 15:
                        print(f"{YELLOW}⚠️  응답 시간이 깁니다 ({response_time:.2f}초){RESET}")
                    
                    return True
                else:
                    print(f"{RED}✗ 웜 스타트 실패: {response.status_code}{RESET}")
                    return False
                    
        except Exception as e:
            print(f"{RED}✗ 테스트 오류: {e}{RESET}")
            return False
    
    async def test_concurrent_requests(self):
        """동시 요청 처리 테스트"""
        print(f"\n{BLUE}=== 동시 요청 처리 테스트 ==={RESET}")
        
        async def single_request(request_id):
            try:
                start_time = time.time()
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": self.model_name,
                            "prompt": f"Request {request_id}: What is AI?",
                            "stream": False,
                            "options": {"num_predict": 20}
                        }
                    )
                    
                    end_time = time.time()
                    return {
                        'id': request_id,
                        'success': response.status_code == 200,
                        'time': end_time - start_time,
                        'response_length': len(response.json().get('response', '')) if response.status_code == 200 else 0
                    }
            except Exception as e:
                return {
                    'id': request_id,
                    'success': False,
                    'time': 0,
                    'error': str(e)
                }
        
        # 3개의 동시 요청
        tasks = [single_request(i) for i in range(1, 4)]
        results = await asyncio.gather(*tasks)
        
        successful = sum(1 for r in results if r['success'])
        avg_time = sum(r['time'] for r in results if r['success']) / max(successful, 1)
        
        print(f"성공한 요청: {successful}/3")
        print(f"평균 응답 시간: {avg_time:.2f}초")
        
        for result in results:
            status = "✓" if result['success'] else "✗"
            print(f"  요청 {result['id']}: {status} ({result['time']:.2f}초)")
        
        return successful >= 2  # 최소 2개 요청 성공
    
    def check_ollama_configuration(self):
        """Ollama 설정 확인"""
        print(f"\n{BLUE}=== Ollama 설정 분석 ==={RESET}")
        
        # Ollama 프로세스 확인
        ollama_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                if 'ollama' in proc.info['name'].lower():
                    memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
                    ollama_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'memory_mb': memory_mb
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if ollama_processes:
            print(f"Ollama 프로세스: {len(ollama_processes)}개")
            for proc in ollama_processes:
                print(f"  PID {proc['pid']}: {proc['name']} (메모리: {proc['memory_mb']:.1f}MB)")
        else:
            print(f"{RED}✗ Ollama 프로세스를 찾을 수 없습니다{RESET}")
            return False
        
        # 환경 변수 확인
        import os
        ollama_host = os.getenv('OLLAMA_HOST', 'localhost:11434')
        ollama_num_parallel = os.getenv('OLLAMA_NUM_PARALLEL', '1')
        ollama_max_queue = os.getenv('OLLAMA_MAX_QUEUE', '512')
        
        print(f"OLLAMA_HOST: {ollama_host}")
        print(f"OLLAMA_NUM_PARALLEL: {ollama_num_parallel}")
        print(f"OLLAMA_MAX_QUEUE: {ollama_max_queue}")
        
        return True
    
    def generate_recommendations(self, resource_ok, loading_ok, concurrent_ok, config_ok):
        """해결 방안 제안"""
        print(f"\n{BLUE}=== 문제 진단 및 해결 방안 ==={RESET}")
        
        # 문제점 분석
        issues = []
        if not resource_ok:
            issues.append("시스템 리소스 부족")
        if not loading_ok:
            issues.append("모델 로딩/응답 시간 과다")
        if not concurrent_ok:
            issues.append("동시 요청 처리 불안정")
        if not config_ok:
            issues.append("Ollama 설정 문제")
        
        if not issues:
            print(f"{GREEN}✓ 특별한 문제가 발견되지 않았습니다{RESET}")
            print("하지만 다음 최적화 방안을 고려해보세요:")
        else:
            print(f"{RED}발견된 문제:{RESET}")
            for issue in issues:
                print(f"  - {issue}")
        
        print(f"\n{CYAN}=== 해결 방안 ==={RESET}")
        
        # 1. 시스템 리소스 최적화
        print(f"{YELLOW}1. 시스템 리소스 최적화{RESET}")
        print("   - GPU 메모리 정리: sudo nvidia-smi --gpu-reset")
        print("   - 시스템 메모리 정리: sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'")
        print("   - 다른 GPU 사용 프로세스 종료")
        print("   - 스왑 파일 크기 확장 (16GB 이상 권장)")
        
        # 2. Ollama 설정 최적화
        print(f"\n{YELLOW}2. Ollama 설정 최적화{RESET}")
        print("   - 환경변수 설정:")
        print("     export OLLAMA_NUM_PARALLEL=1  # 동시 요청 제한")
        print("     export OLLAMA_MAX_QUEUE=2     # 대기열 크기 감소")
        print("     export OLLAMA_FLASH_ATTENTION=1  # Flash Attention 활성화")
        print("   - Ollama 재시작: sudo systemctl restart ollama")
        
        # 3. 모델별 대안
        print(f"\n{YELLOW}3. 모델 사용 전략{RESET}")
        print("   - 일반 작업: txgemma-chat:latest (16GB) 사용")
        print("   - 고품질 작업: Gemma3:27b-it-q4_K_M 사용")
        print("   - 모델 사전 로드: ollama run Gemma3:27b-it-q4_K_M")
        print("   - 더 작은 모델 고려: gemma:7b-instruct-q4_K_M")
        
        # 4. 애플리케이션 최적화
        print(f"\n{YELLOW}4. 애플리케이션 최적화{RESET}")
        print("   - 타임아웃 증가: 300초 이상")
        print("   - 청크 크기 조정: num_predict=500")
        print("   - 온도 설정 최적화: temperature=0.3")
        print("   - 동시 요청 제한: max_concurrent=1")
        
        # 5. 하드웨어 업그레이드
        print(f"\n{YELLOW}5. 하드웨어 고려사항{RESET}")
        print("   - 최소 권장: 32GB RAM + 24GB VRAM")
        print("   - 이상적: 64GB RAM + 48GB VRAM")
        print("   - SSD 스토리지 권장 (모델 로딩 속도)")

async def main():
    """메인 진단 함수"""
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Gemma3:27b-it-q4_K_M 모델 문제 진단{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    diagnostics = Gemma3Diagnostics()
    
    # 진단 단계별 실행
    print(f"{CYAN}1단계: 시스템 리소스 확인{RESET}")
    resource_ok = diagnostics.check_system_resources()
    
    print(f"\n{CYAN}2단계: Ollama 설정 확인{RESET}")
    config_ok = diagnostics.check_ollama_configuration()
    
    print(f"\n{CYAN}3단계: 모델 로딩 테스트{RESET}")
    loading_ok = await diagnostics.test_model_loading_time()
    
    print(f"\n{CYAN}4단계: 동시 요청 테스트{RESET}")
    concurrent_ok = await diagnostics.test_concurrent_requests()
    
    # 최종 권장사항
    diagnostics.generate_recommendations(resource_ok, loading_ok, concurrent_ok, config_ok)
    
    print(f"\n{BLUE}=== 빠른 해결 명령어 ==={RESET}")
    print("# GPU 메모리 정리")
    print("sudo nvidia-smi --gpu-reset")
    print()
    print("# Ollama 최적화 설정")
    print("export OLLAMA_NUM_PARALLEL=1")
    print("export OLLAMA_MAX_QUEUE=2")
    print("sudo systemctl restart ollama")
    print()
    print("# 모델 사전 로드")
    print("ollama run Gemma3:27b-it-q4_K_M")

if __name__ == "__main__":
    asyncio.run(main())