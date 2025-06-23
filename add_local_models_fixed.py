#!/usr/bin/env python3
"""
로컬 GGUF 모델을 Ollama에 추가하는 스크립트 (수정 버전)
"""

import os
import subprocess
import json
import asyncio
import httpx
from pathlib import Path

# 색상 코드
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"

class LocalModelManager:
    def __init__(self):
        self.model_dir = "/home/gaia-bt/workspace/GAIA_LLMs/model"
        self.models = [
            {
                "file": "google.gemma-3-12b-it.Q4_K_M.gguf",
                "name": "gemma3-12b:latest",
                "description": "Gemma 3 12B Instruct (Q4_K_M)"
            },
            {
                "file": "google.txgemma-9b-chat.Q4_K_M.gguf", 
                "name": "txgemma-9b-chat:latest",
                "description": "TxGemma 9B Chat (Q4_K_M)"
            },
            {
                "file": "google.txgemma-9b-predict.Q4_K_M.gguf",
                "name": "txgemma-9b-predict:latest", 
                "description": "TxGemma 9B Predict (Q4_K_M)"
            }
        ]
    
    def check_files_exist(self):
        """모델 파일 존재 여부 확인"""
        print(f"{BLUE}=== 모델 파일 확인 ==={RESET}")
        
        existing_files = []
        missing_files = []
        
        for model in self.models:
            file_path = os.path.join(self.model_dir, model["file"])
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path) / (1024**3)  # GB
                print(f"{GREEN}✓ {model['file']}{RESET} ({file_size:.1f}GB)")
                existing_files.append(model)
            else:
                print(f"{RED}✗ {model['file']}{RESET} (파일 없음)")
                missing_files.append(model)
        
        if missing_files:
            print(f"\n{RED}누락된 파일:{RESET}")
            for model in missing_files:
                print(f"  - {model['file']}")
        
        return existing_files, missing_files
    
    def create_modelfile(self, model_info):
        """Ollama Modelfile 생성"""
        model_path = os.path.join(self.model_dir, model_info["file"])
        
        # 템플릿을 단순화해서 문제 해결
        modelfile_content = f"""FROM {model_path}

# 모델 설정
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096

# 시스템 프롬프트
SYSTEM You are GAIA-BT, an AI assistant specialized in drug development and pharmaceutical research. You provide accurate, evidence-based information about drug discovery, clinical trials, regulatory affairs, and pharmaceutical sciences.
"""
        
        modelfile_path = f"/tmp/Modelfile-{model_info['name'].replace(':', '-')}"
        with open(modelfile_path, 'w') as f:
            f.write(modelfile_content)
        
        return modelfile_path
    
    def add_model_to_ollama(self, model_info):
        """모델을 Ollama에 추가"""
        print(f"\n{YELLOW}모델 추가 중: {model_info['name']}{RESET}")
        
        try:
            # Modelfile 생성
            modelfile_path = self.create_modelfile(model_info)
            print(f"Modelfile 생성: {modelfile_path}")
            
            # ollama create 명령어 실행
            cmd = ["ollama", "create", model_info["name"], "-f", modelfile_path]
            print(f"실행 명령어: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )
            
            if result.returncode == 0:
                print(f"{GREEN}✓ 성공적으로 추가됨{RESET}")
                if result.stdout:
                    print(f"출력: {result.stdout}")
                return True
            else:
                print(f"{RED}✗ 추가 실패{RESET}")
                print(f"오류: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"{RED}✗ 타임아웃 (5분 초과){RESET}")
            return False
        except Exception as e:
            print(f"{RED}✗ 오류: {e}{RESET}")
            return False
        finally:
            # 임시 파일 정리
            if 'modelfile_path' in locals() and os.path.exists(modelfile_path):
                os.remove(modelfile_path)
    
    async def test_model(self, model_name):
        """모델 테스트"""
        print(f"\n{CYAN}--- {model_name} 테스트 ---{RESET}")
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                print(f"{YELLOW}테스트 중... (최대 2분){RESET}")
                start_time = asyncio.get_event_loop().time()
                
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model_name,
                        "prompt": "Hello! Please introduce yourself as GAIA-BT briefly.",
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": 100
                        }
                    }
                )
                
                end_time = asyncio.get_event_loop().time()
                elapsed = end_time - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('response', '')
                    
                    print(f"{GREEN}✓ 성공{RESET} (소요시간: {elapsed:.2f}초)")
                    print(f"응답 길이: {len(response_text)} 문자")
                    print(f"응답: {response_text[:200]}...")
                    
                    return {
                        'success': True,
                        'time': elapsed,
                        'response_length': len(response_text),
                        'response': response_text
                    }
                else:
                    print(f"{RED}✗ HTTP 오류: {response.status_code}{RESET}")
                    return {'success': False, 'error': f"HTTP {response.status_code}"}
                    
        except Exception as e:
            print(f"{RED}✗ 테스트 오류: {e}{RESET}")
            return {'success': False, 'error': str(e)}
    
    async def list_ollama_models(self):
        """Ollama 모델 목록 확인"""
        print(f"\n{BLUE}=== Ollama 모델 목록 ==={RESET}")
        
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(result.stdout)
                
                # API로도 확인
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get("http://localhost:11434/api/tags")
                    data = response.json()
                    models = data.get('models', [])
                    
                    print(f"\n총 {len(models)}개 모델 설치됨:")
                    for model in models:
                        size_gb = model.get('size', 0) / (1024**3)
                        print(f"  - {model['name']} ({size_gb:.1f}GB)")
                
                return models
            else:
                print(f"오류: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"오류: {e}")
            return []

async def main():
    """메인 함수"""
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}로컬 GGUF 모델을 Ollama에 추가{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    manager = LocalModelManager()
    
    # 1. 파일 존재 확인
    existing_files, missing_files = manager.check_files_exist()
    
    if not existing_files:
        print(f"\n{RED}추가할 모델 파일이 없습니다.{RESET}")
        return
    
    # 2. 기존 모델 목록 확인
    await manager.list_ollama_models()
    
    # 3. 모델 추가
    print(f"\n{BLUE}=== 모델 추가 시작 ==={RESET}")
    added_models = []
    
    for model_info in existing_files:
        print(f"\n{CYAN}처리 중: {model_info['description']}{RESET}")
        
        if manager.add_model_to_ollama(model_info):
            added_models.append(model_info)
        else:
            print(f"{RED}스킵: {model_info['name']}{RESET}")
    
    # 4. 업데이트된 모델 목록 확인
    print(f"\n{BLUE}=== 업데이트된 모델 목록 ==={RESET}")
    await manager.list_ollama_models()
    
    # 5. 추가된 모델 테스트
    if added_models:
        print(f"\n{BLUE}=== 모델 테스트 ==={RESET}")
        test_results = {}
        
        for model_info in added_models:
            result = await manager.test_model(model_info['name'])
            test_results[model_info['name']] = result
        
        # 6. 결과 요약
        print(f"\n{BLUE}=== 테스트 결과 요약 ==={RESET}")
        successful_models = []
        failed_models = []
        
        for model_name, result in test_results.items():
            if result['success']:
                successful_models.append((model_name, result['time']))
                print(f"{GREEN}✓ {model_name}{RESET} - {result['time']:.2f}초")
            else:
                failed_models.append(model_name)
                print(f"{RED}✗ {model_name}{RESET} - {result.get('error', 'Unknown error')}")
        
        # 성능 순위
        if successful_models:
            successful_models.sort(key=lambda x: x[1])  # 시간순 정렬
            print(f"\n{CYAN}성능 순위 (빠른 순):{RESET}")
            for i, (model_name, time) in enumerate(successful_models, 1):
                print(f"  {i}. {model_name} ({time:.2f}초)")
        
        # 권장사항
        print(f"\n{BLUE}=== 권장사항 ==={RESET}")
        if successful_models:
            fastest_model = successful_models[0][0]
            print(f"가장 빠른 모델: {GREEN}{fastest_model}{RESET}")
            print(f"설정 변경: export OLLAMA_MODEL={fastest_model}")
            
            # config.py 업데이트 제안
            print(f"\n{YELLOW}config.py 업데이트 제안:{RESET}")
            print(f"OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', '{fastest_model}')")
        
        if failed_models:
            print(f"\n{YELLOW}실패한 모델 해결 방법:{RESET}")
            print("1. 모델 파일 무결성 확인")
            print("2. 충분한 메모리 확보 (16GB+ 권장)")
            print("3. ollama 서비스 재시작")
    
    print(f"\n{GREEN}모델 추가 및 테스트 완료!{RESET}")

if __name__ == "__main__":
    asyncio.run(main())