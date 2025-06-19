#!/bin/bash

# GAIA-BT WebUI 실행 스크립트
# Next.js + FastAPI 기반 신약개발 AI 웹 인터페이스

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/nextjs-webui"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 배너 출력
print_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                       🧬 GAIA-BT WebUI v2.0 Alpha 🧬                       ║"
    echo "║                     신약개발 연구 AI 어시스턴트 웹 인터페이스                   ║"
    echo "║                                                                              ║"
    echo "║  🌐 Next.js Frontend + FastAPI Backend                                      ║"
    echo "║  🔬 Deep Research MCP 통합                                                  ║"
    echo "║  🎯 전문 프롬프트 시스템                                                      ║"
    echo "║  💬 실시간 채팅 인터페이스                                                    ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 사용법 출력
print_usage() {
    echo -e "${CYAN}사용법:${NC}"
    echo "  $0 [옵션]"
    echo ""
    echo -e "${CYAN}옵션:${NC}"
    echo "  start     - WebUI 서비스 시작 (기본값)"
    echo "  stop      - WebUI 서비스 중지"
    echo "  status    - WebUI 서비스 상태 확인"
    echo "  logs      - 로그 출력"
    echo "  dev       - 개발 모드로 시작"
    echo "  build     - 프로덕션 빌드"
    echo "  help      - 이 도움말 표시"
    echo ""
    echo -e "${CYAN}예시:${NC}"
    echo "  $0 start    # WebUI 시작"
    echo "  $0 dev      # 개발 모드로 시작"
    echo "  $0 stop     # 서비스 중지"
}

# 의존성 확인
check_dependencies() {
    echo -e "${BLUE}🔍 의존성 확인 중...${NC}"
    
    # Node.js 확인
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js가 설치되지 않았습니다.${NC}"
        echo "Node.js 18+ 버전을 설치해 주세요."
        exit 1
    fi
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3가 설치되지 않았습니다.${NC}"
        echo "Python 3.8+ 버전을 설치해 주세요."
        exit 1
    fi
    
    # 프로젝트 디렉토리 확인
    if [ ! -d "$BACKEND_DIR" ] || [ ! -d "$FRONTEND_DIR" ]; then
        echo -e "${RED}❌ 프로젝트 디렉토리를 찾을 수 없습니다.${NC}"
        echo "Backend: $BACKEND_DIR"
        echo "Frontend: $FRONTEND_DIR"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 의존성 확인 완료${NC}"
}

# 포트 확인
check_ports() {
    echo -e "${BLUE}🔍 포트 사용 확인 중...${NC}"
    
    if ss -tulpn | grep -q ":3000 "; then
        echo -e "${YELLOW}⚠️  포트 3000이 이미 사용 중입니다.${NC}"
        read -p "계속하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    if ss -tulpn | grep -q ":8000 "; then
        echo -e "${YELLOW}⚠️  포트 8000이 이미 사용 중입니다.${NC}"
        read -p "계속하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 백엔드 시작
start_backend() {
    echo -e "${BLUE}🚀 FastAPI 백엔드 시작 중...${NC}"
    cd "$BACKEND_DIR"
    
    # Python 의존성 설치 확인
    if [ ! -f "requirements.txt" ]; then
        echo -e "${RED}❌ requirements.txt를 찾을 수 없습니다.${NC}"
        exit 1
    fi
    
    # 백엔드 시작
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    # 백엔드 시작 대기
    echo -e "${YELLOW}⏳ 백엔드 시작 대기 중...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ FastAPI 백엔드가 포트 8000에서 시작되었습니다.${NC}"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ 백엔드 시작 실패${NC}"
            kill $BACKEND_PID 2>/dev/null || true
            exit 1
        fi
    done
}

# 프론트엔드 시작
start_frontend() {
    echo -e "${BLUE}🚀 Next.js 프론트엔드 시작 중...${NC}"
    cd "$FRONTEND_DIR"
    
    # Node.js 의존성 설치 확인
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 의존성 설치 중...${NC}"
        npm install
    fi
    
    # 프론트엔드 시작
    if [ "$1" = "dev" ]; then
        npm run dev &
    else
        npm run build && npm start &
    fi
    FRONTEND_PID=$!
    
    echo -e "${GREEN}✅ Next.js 프론트엔드가 포트 3000에서 시작되었습니다.${NC}"
}

# 서비스 시작
start_services() {
    check_dependencies
    check_ports
    
    start_backend
    start_frontend "$1"
    
    echo ""
    echo -e "${GREEN}🎉 GAIA-BT WebUI가 성공적으로 시작되었습니다!${NC}"
    echo ""
    echo -e "${CYAN}📱 웹 인터페이스:${NC} http://localhost:3000"
    echo -e "${CYAN}🔗 API 문서:${NC} http://localhost:8000/docs"
    echo -e "${CYAN}⚡ API 엔드포인트:${NC} http://localhost:8000/api"
    echo ""
    echo -e "${YELLOW}💡 사용 팁:${NC}"
    echo "  • 웹 브라우저에서 http://localhost:3000 접속"
    echo "  • '/mcp start' 명령어로 Deep Research 모드 활성화"
    echo "  • '/help' 명령어로 전체 기능 확인"
    echo "  • Ctrl+C로 서비스 중지"
    echo ""
    
    # PID 저장
    echo "$BACKEND_PID" > /tmp/gaia-bt-backend.pid
    echo "$FRONTEND_PID" > /tmp/gaia-bt-frontend.pid
    
    # 신호 처리
    trap 'stop_services; exit 0' SIGINT SIGTERM
    
    # 서비스 상태 모니터링
    while true; do
        if ! kill -0 $BACKEND_PID 2>/dev/null || ! kill -0 $FRONTEND_PID 2>/dev/null; then
            echo -e "${RED}❌ 서비스가 중지되었습니다.${NC}"
            stop_services
            exit 1
        fi
        sleep 5
    done
}

# 서비스 중지
stop_services() {
    echo -e "${YELLOW}🛑 GAIA-BT WebUI 서비스 중지 중...${NC}"
    
    # PID 파일에서 읽기
    if [ -f /tmp/gaia-bt-backend.pid ]; then
        BACKEND_PID=$(cat /tmp/gaia-bt-backend.pid)
        kill $BACKEND_PID 2>/dev/null || true
        rm -f /tmp/gaia-bt-backend.pid
    fi
    
    if [ -f /tmp/gaia-bt-frontend.pid ]; then
        FRONTEND_PID=$(cat /tmp/gaia-bt-frontend.pid)
        kill $FRONTEND_PID 2>/dev/null || true
        rm -f /tmp/gaia-bt-frontend.pid
    fi
    
    # 추가로 포트 기반 프로세스 종료
    pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
    pkill -f "next.*dev" 2>/dev/null || true
    
    echo -e "${GREEN}✅ 서비스가 중지되었습니다.${NC}"
}

# 서비스 상태 확인
check_status() {
    echo -e "${BLUE}📊 GAIA-BT WebUI 서비스 상태${NC}"
    echo ""
    
    # 백엔드 상태
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ FastAPI 백엔드: 정상 동작 (포트 8000)${NC}"
        API_INFO=$(curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "API 정보 확인 불가")
        echo "   $API_INFO"
    else
        echo -e "${RED}❌ FastAPI 백엔드: 중지됨 (포트 8000)${NC}"
    fi
    
    # 프론트엔드 상태
    if curl -s -o /dev/null http://localhost:3000; then
        echo -e "${GREEN}✅ Next.js 프론트엔드: 정상 동작 (포트 3000)${NC}"
    else
        echo -e "${RED}❌ Next.js 프론트엔드: 중지됨 (포트 3000)${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}🔗 접속 URL:${NC}"
    echo "  • 웹 인터페이스: http://localhost:3000"
    echo "  • API 문서: http://localhost:8000/docs"
}

# 로그 출력
show_logs() {
    echo -e "${BLUE}📋 실시간 로그 출력 (Ctrl+C로 종료)${NC}"
    echo ""
    
    # 백엔드 로그와 프론트엔드 로그를 함께 출력
    tail -f /tmp/gaia-bt-*.log 2>/dev/null || echo "로그 파일을 찾을 수 없습니다."
}

# 빌드
build_production() {
    echo -e "${BLUE}🏗️  프로덕션 빌드 시작...${NC}"
    
    cd "$FRONTEND_DIR"
    npm install
    npm run build
    
    echo -e "${GREEN}✅ 빌드 완료${NC}"
}

# 메인 로직
main() {
    print_banner
    
    case "${1:-start}" in
        start)
            start_services "production"
            ;;
        dev)
            start_services "dev"
            ;;
        stop)
            stop_services
            ;;
        status)
            check_status
            ;;
        logs)
            show_logs
            ;;
        build)
            build_production
            ;;
        help|--help|-h)
            print_usage
            ;;
        *)
            echo -e "${RED}❌ 알 수 없는 옵션: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
}

# 스크립트 실행
main "$@"