#!/bin/bash
# Gemma3:27b-it-q4_K_M 성능 최적화 스크립트

echo "🔧 Gemma3:27b-it-q4_K_M 성능 최적화 시작..."

# 1. 시스템 메모리 정리
echo "1. 시스템 메모리 정리 중..."
echo "비밀번호가 필요합니다:"
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
echo "✅ 시스템 캐시 정리 완료"

# 2. GPU 메모리 정리
echo "2. GPU 메모리 정리 중..."
if command -v nvidia-smi &> /dev/null; then
    sudo nvidia-smi --gpu-reset
    echo "✅ GPU 메모리 정리 완료"
else
    echo "⚠️  nvidia-smi를 찾을 수 없습니다"
fi

# 3. Ollama 최적화 설정
echo "3. Ollama 환경변수 설정 중..."
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_QUEUE=2
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_KEEP_ALIVE=600  # 10분 동안 모델 메모리 유지

# 환경변수를 bashrc에 추가
echo "export OLLAMA_NUM_PARALLEL=1" >> ~/.bashrc
echo "export OLLAMA_MAX_QUEUE=2" >> ~/.bashrc
echo "export OLLAMA_FLASH_ATTENTION=1" >> ~/.bashrc
echo "export OLLAMA_KEEP_ALIVE=600" >> ~/.bashrc

echo "✅ 환경변수 설정 완료"

# 4. Ollama 서비스 재시작
echo "4. Ollama 서비스 재시작 중..."
sudo systemctl restart ollama
sleep 5
echo "✅ Ollama 재시작 완료"

# 5. 모델 사전 로드
echo "5. Gemma3 모델 사전 로드 중... (최대 3분 소요)"
timeout 180 ollama run Gemma3:27b-it-q4_K_M "Hello" || echo "타임아웃 발생"

# 6. 스왑 파일 확장 (선택사항)
echo "6. 스왑 파일 크기 확인..."
SWAP_SIZE=$(free -h | awk '/^Swap:/ {print $2}')
echo "현재 스왑 크기: $SWAP_SIZE"

if [[ "$SWAP_SIZE" == "0B" ]] || [[ -z "$SWAP_SIZE" ]]; then
    echo "⚠️  스왑 파일이 없습니다. 16GB 스왑 파일 생성을 권장합니다:"
    echo "sudo fallocate -l 16G /swapfile"
    echo "sudo chmod 600 /swapfile"
    echo "sudo mkswap /swapfile"
    echo "sudo swapon /swapfile"
    echo "echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab"
fi

echo ""
echo "🎉 최적화 완료!"
echo ""
echo "📊 적용된 설정:"
echo "  - OLLAMA_NUM_PARALLEL=1 (동시 요청 제한)"
echo "  - OLLAMA_MAX_QUEUE=2 (대기열 크기 감소)"
echo "  - OLLAMA_FLASH_ATTENTION=1 (Flash Attention 활성화)"
echo "  - OLLAMA_KEEP_ALIVE=600 (모델 10분간 메모리 유지)"
echo ""
echo "🚀 이제 Gemma3 모델이 더 빠르게 작동할 것입니다!"
echo ""
echo "💡 추가 권장사항:"
echo "  - 시스템 재시작 시 모델 사전 로드: ollama run Gemma3:27b-it-q4_K_M"
echo "  - 메모리 부족 시 txgemma-chat:latest 사용 고려"