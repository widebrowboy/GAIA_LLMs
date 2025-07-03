#!/bin/bash

# GAIA-BT Milvus 서버 관리 스크립트
# Milvus 웹 UI 포함 전체 Milvus 서버 관리

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.milvus.yml"

echo -e "${CYAN}
╔══════════════════════════════════════════════════════════════╗
║                     GAIA-BT Milvus Manager                   ║
║                    Milvus 서버 및 웹 UI 관리                  ║
╚══════════════════════════════════════════════════════════════╝
${NC}"

# 함수: 사용법 표시
show_usage() {
    echo -e "${BLUE}사용법: $0 [COMMAND]${NC}"
    echo ""
    echo -e "${CYAN}Commands:${NC}"
    echo "  start       - Milvus 서버 시작"
    echo "  stop        - Milvus 서버 중지"
    echo "  restart     - Milvus 서버 재시작"
    echo "  status      - Milvus 서버 상태 확인"
    echo "  logs        - Milvus 로그 조회"
    echo "  clean       - 모든 데이터 삭제 (주의!)"
    echo "  webui       - 웹 UI 열기"
    echo "  health      - 헬스 체크"
    echo "  help        - 이 도움말 표시"
    echo ""
    echo -e "${YELLOW}웹 UI 접근:${NC}"
    echo "  - Milvus 웹 UI: http://localhost:9091/webui"
    echo "  - MinIO 콘솔: http://localhost:9001"
    echo ""
}

# 함수: Docker 설치 확인
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker가 설치되지 않았습니다.${NC}"
        echo "Docker를 먼저 설치해주세요: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose가 설치되지 않았습니다.${NC}"
        echo "Docker Compose를 먼저 설치해주세요."
        exit 1
    fi
}

# 함수: Compose 파일 확인
check_compose_file() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Docker Compose 파일을 찾을 수 없습니다: $COMPOSE_FILE${NC}"
        exit 1
    fi
}

# 함수: Milvus 서버 시작
start_milvus() {
    echo -e "${BLUE}🚀 Milvus 서버 시작 중...${NC}"
    
    cd "$PROJECT_ROOT"
    
    # Docker Compose로 서비스 시작
    if docker-compose -f docker-compose.milvus.yml up -d; then
        echo -e "${GREEN}✅ Milvus 서버가 시작되었습니다.${NC}"
        echo ""
        echo -e "${CYAN}서비스 정보:${NC}"
        echo "  - Milvus gRPC: http://localhost:19530"
        echo "  - Milvus 웹 UI: http://localhost:9091/webui"
        echo "  - MinIO 콘솔: http://localhost:9001"
        echo ""
        echo -e "${YELLOW}⏳ 서비스가 완전히 시작될 때까지 1-2분 정도 기다려주세요.${NC}"
        
        # 헬스 체크 실행
        echo ""
        sleep 5
        health_check
    else
        echo -e "${RED}❌ Milvus 서버 시작에 실패했습니다.${NC}"
        exit 1
    fi
}

# 함수: Milvus 서버 중지
stop_milvus() {
    echo -e "${YELLOW}🛑 Milvus 서버 중지 중...${NC}"
    
    cd "$PROJECT_ROOT"
    
    if docker-compose -f docker-compose.milvus.yml down; then
        echo -e "${GREEN}✅ Milvus 서버가 중지되었습니다.${NC}"
    else
        echo -e "${RED}❌ Milvus 서버 중지에 실패했습니다.${NC}"
        exit 1
    fi
}

# 함수: Milvus 서버 재시작
restart_milvus() {
    echo -e "${BLUE}🔄 Milvus 서버 재시작 중...${NC}"
    stop_milvus
    sleep 3
    start_milvus
}

# 함수: 서버 상태 확인
check_status() {
    echo -e "${CYAN}📊 Milvus 서버 상태 확인${NC}"
    echo "=================================================="
    
    cd "$PROJECT_ROOT"
    
    # Docker Compose 상태 확인
    if docker-compose -f docker-compose.milvus.yml ps; then
        echo ""
        echo -e "${CYAN}포트 상태:${NC}"
        
        # 포트 확인
        if netstat -tuln | grep -q ":19530 "; then
            echo -e "${GREEN}✅ Milvus gRPC (19530): 활성${NC}"
        else
            echo -e "${RED}❌ Milvus gRPC (19530): 비활성${NC}"
        fi
        
        if netstat -tuln | grep -q ":9091 "; then
            echo -e "${GREEN}✅ Milvus 웹 UI (9091): 활성${NC}"
        else
            echo -e "${RED}❌ Milvus 웹 UI (9091): 비활성${NC}"
        fi
        
        if netstat -tuln | grep -q ":9001 "; then
            echo -e "${GREEN}✅ MinIO 콘솔 (9001): 활성${NC}"
        else
            echo -e "${RED}❌ MinIO 콘솔 (9001): 비활성${NC}"
        fi
    else
        echo -e "${RED}❌ Milvus 서비스가 실행되지 않고 있습니다.${NC}"
    fi
    
    echo "=================================================="
}

# 함수: 로그 조회
show_logs() {
    echo -e "${CYAN}📋 Milvus 로그 조회${NC}"
    
    cd "$PROJECT_ROOT"
    
    echo "어느 서비스의 로그를 확인하시겠습니까?"
    echo "1) Milvus Standalone"
    echo "2) MinIO"
    echo "3) etcd"
    echo "4) 모든 서비스"
    
    read -p "선택 (1-4): " choice
    
    case $choice in
        1)
            docker-compose -f docker-compose.milvus.yml logs -f standalone
            ;;
        2)
            docker-compose -f docker-compose.milvus.yml logs -f minio
            ;;
        3)
            docker-compose -f docker-compose.milvus.yml logs -f etcd
            ;;
        4)
            docker-compose -f docker-compose.milvus.yml logs -f
            ;;
        *)
            echo -e "${RED}잘못된 선택입니다.${NC}"
            ;;
    esac
}

# 함수: 데이터 정리
clean_data() {
    echo -e "${RED}⚠️  경고: 이 작업은 모든 Milvus 데이터를 삭제합니다!${NC}"
    echo -e "${YELLOW}계속하려면 'YES'를 입력하세요:${NC}"
    
    read -p "> " confirm
    
    if [ "$confirm" = "YES" ]; then
        echo -e "${YELLOW}🧹 데이터 정리 중...${NC}"
        
        cd "$PROJECT_ROOT"
        
        # 서비스 중지
        docker-compose -f docker-compose.milvus.yml down
        
        # 볼륨 데이터 삭제
        sudo rm -rf volumes/
        
        # Docker 볼륨 정리
        docker volume prune -f
        
        echo -e "${GREEN}✅ 모든 데이터가 정리되었습니다.${NC}"
    else
        echo -e "${CYAN}작업이 취소되었습니다.${NC}"
    fi
}

# 함수: 웹 UI 열기
open_webui() {
    echo -e "${CYAN}🌐 Milvus 웹 UI 열기${NC}"
    
    # 서비스 상태 확인
    if ! netstat -tuln | grep -q ":9091 "; then
        echo -e "${RED}❌ Milvus 웹 UI가 실행되지 않고 있습니다.${NC}"
        echo "먼저 Milvus 서버를 시작해주세요: $0 start"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 웹 브라우저에서 Milvus 웹 UI를 엽니다...${NC}"
    
    # OS별 브라우저 열기
    if command -v xdg-open > /dev/null; then
        xdg-open "http://localhost:9091/webui"
    elif command -v open > /dev/null; then
        open "http://localhost:9091/webui"
    else
        echo "브라우저에서 다음 URL에 접속하세요: http://localhost:9091/webui"
    fi
    
    echo ""
    echo -e "${CYAN}추가 웹 UI:${NC}"
    echo "  - MinIO 콘솔: http://localhost:9001"
    echo "    (사용자: minioadmin, 비밀번호: minioadmin)"
}

# 함수: 헬스 체크
health_check() {
    echo -e "${CYAN}🏥 Milvus 헬스 체크${NC}"
    
    # Milvus API 헬스 체크
    if curl -s -f "http://localhost:9091/api/v1/health" > /dev/null; then
        echo -e "${GREEN}✅ Milvus API: 정상${NC}"
    else
        echo -e "${RED}❌ Milvus API: 비정상${NC}"
    fi
    
    # MinIO 헬스 체크
    if curl -s -f "http://localhost:9000/minio/health/live" > /dev/null; then
        echo -e "${GREEN}✅ MinIO: 정상${NC}"
    else
        echo -e "${RED}❌ MinIO: 비정상${NC}"
    fi
    
    # Python에서 연결 테스트
    echo -e "${CYAN}🐍 Python 연결 테스트:${NC}"
    python3 -c "
try:
    from pymilvus import connections
    connections.connect('default', host='localhost', port='19530')
    print('✅ PyMilvus 연결: 성공')
    connections.disconnect('default')
except Exception as e:
    print(f'❌ PyMilvus 연결: 실패 - {e}')
"
}

# 메인 로직
check_docker
check_compose_file

case "${1:-help}" in
    start)
        start_milvus
        ;;
    stop)
        stop_milvus
        ;;
    restart)
        restart_milvus
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs
        ;;
    clean)
        clean_data
        ;;
    webui)
        open_webui
        ;;
    health)
        health_check
        ;;
    help|*)
        show_usage
        ;;
esac