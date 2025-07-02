#!/bin/bash

# Milvus 설치 및 실행 스크립트

echo "🚀 Milvus 벡터 데이터베이스 설정 시작..."

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되어 있지 않습니다."
    echo "Docker를 먼저 설치해주세요: https://docs.docker.com/get-docker/"
    exit 1
fi

# Milvus 데이터 디렉토리 생성
MILVUS_DATA_DIR="$HOME/docker/milvus"
mkdir -p "$MILVUS_DATA_DIR/db"
mkdir -p "$MILVUS_DATA_DIR/logs"
mkdir -p "$MILVUS_DATA_DIR/wal"

echo "📁 Milvus 데이터 디렉토리 생성: $MILVUS_DATA_DIR"

# 기존 Milvus 컨테이너 확인 및 제거
if docker ps -a | grep -q milvus-standalone; then
    echo "🔄 기존 Milvus 컨테이너 발견. 제거 중..."
    docker stop milvus-standalone 2>/dev/null || true
    docker rm milvus-standalone 2>/dev/null || true
fi

# Milvus 실행
echo "🐳 Milvus 컨테이너 시작 중..."
docker run -d \
    --name milvus-standalone \
    -p 19530:19530 \
    -p 9091:9091 \
    -v "$MILVUS_DATA_DIR/db:/var/lib/milvus/db" \
    -v "$MILVUS_DATA_DIR/logs:/var/lib/milvus/logs" \
    -v "$MILVUS_DATA_DIR/wal:/var/lib/milvus/wal" \
    milvusdb/milvus:v2.3.3

# 실행 확인
echo "⏳ Milvus 시작 대기 중 (약 10초)..."
sleep 10

# 상태 확인
if docker ps | grep -q milvus-standalone; then
    echo "✅ Milvus가 성공적으로 시작되었습니다!"
    echo ""
    echo "📊 Milvus 정보:"
    echo "   - GRPC 포트: 19530"
    echo "   - Admin 포트: 9091"
    echo "   - 데이터 디렉토리: $MILVUS_DATA_DIR"
    echo ""
    echo "🔍 상태 확인:"
    docker ps | grep milvus-standalone
    echo ""
    echo "📝 로그 확인: docker logs milvus-standalone"
    echo "🛑 중지: docker stop milvus-standalone"
    echo "🗑️  제거: docker rm milvus-standalone"
else
    echo "❌ Milvus 시작 실패!"
    echo "로그 확인: docker logs milvus-standalone"
    exit 1
fi

echo ""
echo "✨ Milvus 설정 완료!"