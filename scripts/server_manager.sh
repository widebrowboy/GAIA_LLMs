#!/bin/bash

# ============================================================================
# GAIA-BT Server Manager - 포트 충돌 방지 및 서버 관리 스크립트
# ============================================================================

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 로고 출력
print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    GAIA-BT Server Manager                    ║"
    echo "║                  포트 충돌 방지 및 서버 관리                  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 포트 사용 프로세스 확인
check_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null || ps aux | grep -E ":[[:space:]]*$port[[:space:]]|--port[[:space:]]+$port" | grep -v grep | awk '{print $2}' 2>/dev/null)
    
    if [ ! -z "$pids" ]; then
        echo "$pids"
    else
        echo ""
    fi
}

# 포트 사용 프로세스 종료
kill_port_processes() {
    local port=$1
    local service_name=$2
    
    echo -e "${YELLOW}🔍 포트 $port 사용 프로세스 확인 중...${NC}"
    
    local pids=$(check_port $port)
    
    if [ ! -z "$pids" ]; then
        echo -e "${RED}⚠️ 포트 $port가 이미 사용 중입니다 (PID: $pids)${NC}"
        echo -e "${YELLOW}🔪 $service_name 관련 프로세스를 종료합니다...${NC}"
        
        # 먼저 graceful shutdown 시도
        echo "$pids" | xargs -r kill -TERM 2>/dev/null
        sleep 2
        
        # 여전히 실행 중이면 강제 종료
        local remaining_pids=$(check_port $port)
        if [ ! -z "$remaining_pids" ]; then
            echo -e "${RED}💥 강제 종료 중...${NC}"
            echo "$remaining_pids" | xargs -r kill -KILL 2>/dev/null
            sleep 1
        fi
        
        # 최종 확인
        local final_pids=$(check_port $port)
        if [ -z "$final_pids" ]; then
            echo -e "${GREEN}✅ 포트 $port 정리 완료${NC}"
        else
            echo -e "${RED}❌ 포트 $port 정리 실패${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}✅ 포트 $port 사용 가능${NC}"
    fi
    
    return 0
}

# 모든 GAIA-BT 관련 프로세스 종료
stop_all_servers() {
    echo -e "${CYAN}🛑 모든 GAIA-BT 서버 중지 중...${NC}"
    
    # 패턴별로 프로세스 종료
    local patterns=(
        "node.*next"
        "npm.*dev"
        "uvicorn.*gaia"
        "uvicorn.*app"
        "python.*run_api_server"
        "python.*api_server"
        "fastapi"
        "run_webui"
    )
    
    for pattern in "${patterns[@]}"; do
        local pids=$(ps aux | grep -E "$pattern" | grep -v grep | awk '{print $2}')
        if [ ! -z "$pids" ]; then
            echo -e "${YELLOW}🔪 '$pattern' 프로세스 종료 중...${NC}"
            echo "$pids" | xargs -r kill -TERM 2>/dev/null
        fi
    done
    
    sleep 3
    
    # 강제 종료
    for pattern in "${patterns[@]}"; do
        local pids=$(ps aux | grep -E "$pattern" | grep -v grep | awk '{print $2}')
        if [ ! -z "$pids" ]; then
            echo -e "${RED}💥 '$pattern' 강제 종료 중...${NC}"
            echo "$pids" | xargs -r kill -KILL 2>/dev/null
        fi
    done
    
    # 포트별 정리
    kill_port_processes 3001 "Next.js WebUI"
    kill_port_processes 8000 "FastAPI Backend"
    
    echo -e "${GREEN}✅ 모든 서버 중지 완료${NC}"
}

# FastAPI 서버 시작
start_api_server() {
    echo -e "${BLUE}🚀 FastAPI 서버 시작 중...${NC}"
    
    # 포트 정리
    kill_port_processes 8000 "FastAPI Backend"
    
    # 작업 디렉토리 확인
    if [ ! -f "/home/gaia-bt/workspace/GAIA_LLMs/run_api_server.py" ]; then
        echo -e "${RED}❌ run_api_server.py 파일을 찾을 수 없습니다${NC}"
        return 1
    fi
    
    cd /home/gaia-bt/workspace/GAIA_LLMs
    
    # Python 환경 확인
    if ! python -c "import uvicorn" 2>/dev/null; then
        echo -e "${YELLOW}⚠️ uvicorn이 설치되지 않았습니다. 설치 중...${NC}"
        pip install uvicorn fastapi
    fi
    
    # API 서버 시작
    echo -e "${CYAN}🔗 API 서버 시작: http://localhost:8000${NC}"
    nohup python -m uvicorn app.api_server.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/gaia-bt-api.log 2>&1 &
    local api_pid=$!
    
    # 시작 확인
    sleep 3
    if kill -0 $api_pid 2>/dev/null; then
        echo -e "${GREEN}✅ FastAPI 서버 시작 완료 (PID: $api_pid)${NC}"
        echo -e "${CYAN}📖 API 문서: http://localhost:8000/docs${NC}"
        return 0
    else
        echo -e "${RED}❌ FastAPI 서버 시작 실패${NC}"
        echo -e "${YELLOW}📄 로그 확인: tail -f /tmp/gaia-bt-api.log${NC}"
        return 1
    fi
}

# Next.js WebUI 서버 시작
start_webui_server() {
    echo -e "${BLUE}🌐 Next.js WebUI 서버 시작 중...${NC}"
    
    # 포트 정리
    kill_port_processes 3001 "Next.js WebUI"
    
    # 작업 디렉토리 확인
    local webui_dir="/home/gaia-bt/workspace/GAIA_LLMs/webui/nextjs-webui"
    if [ ! -d "$webui_dir" ]; then
        echo -e "${RED}❌ WebUI 디렉토리를 찾을 수 없습니다: $webui_dir${NC}"
        return 1
    fi
    
    cd "$webui_dir"
    
    # Node.js 환경 확인
    if [ ! -f "package.json" ]; then
        echo -e "${RED}❌ package.json 파일을 찾을 수 없습니다${NC}"
        return 1
    fi
    
    # 의존성 확인 및 설치
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 의존성 설치 중...${NC}"
        npm install
    fi
    
    # WebUI 서버 시작
    echo -e "${CYAN}🔗 WebUI 서버 시작: http://localhost:3001${NC}"
    nohup npm run dev -- --hostname 0.0.0.0 --port 3001 > /tmp/gaia-bt-webui.log 2>&1 &
    local webui_pid=$!
    
    # 시작 확인
    sleep 5
    if kill -0 $webui_pid 2>/dev/null; then
        echo -e "${GREEN}✅ Next.js WebUI 서버 시작 완료 (PID: $webui_pid)${NC}"
        echo -e "${CYAN}🌐 웹 인터페이스: http://localhost:3001${NC}"
        return 0
    else
        echo -e "${RED}❌ Next.js WebUI 서버 시작 실패${NC}"
        echo -e "${YELLOW}📄 로그 확인: tail -f /tmp/gaia-bt-webui.log${NC}"
        return 1
    fi
}

# 서버 상태 확인
check_server_status() {
    echo -e "${CYAN}📊 서버 상태 확인${NC}"
    echo "=================================================="
    
    # API 서버 상태
    local api_pids=$(check_port 8000)
    if [ ! -z "$api_pids" ]; then
        echo -e "${GREEN}✅ FastAPI 서버: 실행 중 (PID: $api_pids)${NC}"
        echo -e "   🔗 API: http://localhost:8000"
        echo -e "   📖 문서: http://localhost:8000/docs"
        
        # Health check
        if command -v curl >/dev/null 2>&1; then
            local health_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null)
            if [ "$health_status" = "200" ]; then
                echo -e "   💚 Health: 정상"
            else
                echo -e "   💛 Health: 확인 필요 ($health_status)"
            fi
        fi
    else
        echo -e "${RED}❌ FastAPI 서버: 중지됨${NC}"
    fi
    
    echo ""
    
    # WebUI 서버 상태
    local webui_pids=$(check_port 3001)
    if [ ! -z "$webui_pids" ]; then
        echo -e "${GREEN}✅ Next.js WebUI: 실행 중 (PID: $webui_pids)${NC}"
        echo -e "   🌐 WebUI: http://localhost:3001"
        
        # Health check
        if command -v curl >/dev/null 2>&1; then
            local webui_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 2>/dev/null)
            if [ "$webui_status" = "200" ]; then
                echo -e "   💚 Status: 정상"
            else
                echo -e "   💛 Status: 확인 필요 ($webui_status)"
            fi
        fi
    else
        echo -e "${RED}❌ Next.js WebUI: 중지됨${NC}"
    fi
    
    echo "=================================================="
}

# 로그 확인
show_logs() {
    local service=$1
    
    case $service in
        "api"|"backend")
            echo -e "${CYAN}📄 FastAPI 서버 로그:${NC}"
            if [ -f "/tmp/gaia-bt-api.log" ]; then
                tail -f /tmp/gaia-bt-api.log
            else
                echo -e "${YELLOW}⚠️ API 서버 로그 파일이 없습니다${NC}"
            fi
            ;;
        "webui"|"frontend")
            echo -e "${CYAN}📄 Next.js WebUI 로그:${NC}"
            if [ -f "/tmp/gaia-bt-webui.log" ]; then
                tail -f /tmp/gaia-bt-webui.log
            else
                echo -e "${YELLOW}⚠️ WebUI 로그 파일이 없습니다${NC}"
            fi
            ;;
        *)
            echo -e "${YELLOW}📄 모든 로그:${NC}"
            echo -e "${BLUE}=== API 서버 로그 ===${NC}"
            [ -f "/tmp/gaia-bt-api.log" ] && tail -20 /tmp/gaia-bt-api.log || echo "로그 없음"
            echo -e "${BLUE}=== WebUI 로그 ===${NC}"
            [ -f "/tmp/gaia-bt-webui.log" ] && tail -20 /tmp/gaia-bt-webui.log || echo "로그 없음"
            ;;
    esac
}

# 도움말
show_help() {
    echo -e "${CYAN}GAIA-BT Server Manager 사용법:${NC}"
    echo ""
    echo -e "${GREEN}기본 명령어:${NC}"
    echo "  start          - 모든 서버 시작 (API + WebUI)"
    echo "  stop           - 모든 서버 중지"
    echo "  restart        - 모든 서버 재시작"
    echo "  status         - 서버 상태 확인"
    echo ""
    echo -e "${GREEN}개별 서버 제어:${NC}"
    echo "  start-api      - FastAPI 서버만 시작"
    echo "  start-webui    - Next.js WebUI 서버만 시작"
    echo "  stop-api       - FastAPI 서버만 중지"
    echo "  stop-webui     - Next.js WebUI 서버만 중지"
    echo ""
    echo -e "${GREEN}포트 관리:${NC}"
    echo "  kill-port 3001 - 특정 포트 사용 프로세스 종료"
    echo "  clean-ports    - 모든 관련 포트 정리"
    echo ""
    echo -e "${GREEN}로그 및 디버깅:${NC}"
    echo "  logs           - 모든 로그 확인"
    echo "  logs-api       - API 서버 로그 확인"
    echo "  logs-webui     - WebUI 로그 확인"
    echo ""
    echo -e "${GREEN}접속 정보:${NC}"
    echo "  📱 WebUI: http://localhost:3001"
    echo "  🔗 API: http://localhost:8000"
    echo "  📖 API 문서: http://localhost:8000/docs"
}

# 메인 함수
main() {
    print_banner
    
    case "${1:-start}" in
        "start")
            stop_all_servers
            start_api_server && start_webui_server
            sleep 2
            check_server_status
            ;;
        "stop")
            stop_all_servers
            ;;
        "restart")
            stop_all_servers
            sleep 2
            start_api_server && start_webui_server
            sleep 2
            check_server_status
            ;;
        "status")
            check_server_status
            ;;
        "start-api")
            kill_port_processes 8000 "FastAPI Backend"
            start_api_server
            ;;
        "start-webui")
            kill_port_processes 3001 "Next.js WebUI"
            start_webui_server
            ;;
        "stop-api")
            kill_port_processes 8000 "FastAPI Backend"
            ;;
        "stop-webui")
            kill_port_processes 3001 "Next.js WebUI"
            ;;
        "kill-port")
            if [ -z "$2" ]; then
                echo -e "${RED}❌ 포트 번호를 지정해주세요: $0 kill-port 3001${NC}"
                exit 1
            fi
            kill_port_processes "$2" "Port $2"
            ;;
        "clean-ports")
            kill_port_processes 3001 "Next.js WebUI"
            kill_port_processes 8000 "FastAPI Backend"
            ;;
        "logs")
            show_logs "all"
            ;;
        "logs-api")
            show_logs "api"
            ;;
        "logs-webui")
            show_logs "webui"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}❌ 알 수 없는 명령어: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 스크립트 실행
main "$@"