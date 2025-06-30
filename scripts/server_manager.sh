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

# 서버 정보
API_PORT=8000
WEBUI_PORT=3003
API_URL="http://localhost:${API_PORT}"
WEBUI_URL="http://localhost:${WEBUI_PORT}"
API_LOG="/tmp/gaia-bt-api.log"
WEBUI_LOG="/tmp/gaia-bt-webui.log"

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

# 포트 대기 함수
wait_for_port_free() {
    local port=$1
    local max_wait=10
    local wait_count=0
    
    while [ $wait_count -lt $max_wait ]; do
        if [ -z "$(check_port $port)" ]; then
            return 0
        fi
        echo -e "${YELLOW}⏳ 포트 $port 해제 대기 중... ($wait_count/$max_wait)${NC}"
        sleep 1
        wait_count=$((wait_count + 1))
    done
    
    return 1
}

# 서버 준비 대기 함수
wait_for_servers() {
    local max_wait=30
    local api_ready=false
    local webui_ready=false
    local wait_count=0
    
    echo -e "${YELLOW}⏳ 서버 준비 대기 중...${NC}"
    
    while [ $wait_count -lt $max_wait ]; do
        # API 서버 확인
        if ! $api_ready && curl -s $API_URL/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ API 서버($API_PORT) 준비 완료${NC}"
            api_ready=true
        fi
        
        # WebUI 서버 확인
        if ! $webui_ready && curl -s $WEBUI_URL > /dev/null 2>&1; then
            echo -e "${GREEN}✅ WebUI 서버($WEBUI_PORT) 준비 완료${NC}"
            webui_ready=true
        fi
        
        # 둘 다 준비되면 종료
        if $api_ready && $webui_ready; then
            return 0
        fi
        
        sleep 1
        wait_count=$((wait_count + 1))
        
        # 10초마다 상태 표시
        if [ $((wait_count % 10)) -eq 0 ]; then
            echo -e "${YELLOW}⏳ 서버 준비 대기 중... ($wait_count/$max_wait)${NC}"
        fi
    done
    
    # 타임아웃
    echo -e "${YELLOW}⚠️ 일부 서버가 준비되지 않았습니다. 브라우저는 오픈되지만 완전히 동작하지 않을 수 있습니다.${NC}"
    return 1
}

# 브라우저 열기 함수
open_browser() {
    local url=${1:-$WEBUI_URL}
    local wait=${2:-false}
    
    # 지정된 경우 서버 준비 대기
    if $wait; then
        wait_for_servers
    fi
    
    echo -e "${CYAN}🌐 브라우저에서 WebUI 열기: $url${NC}"
    
    # 다양한 브라우저 지원
    if command -v xdg-open > /dev/null; then
        xdg-open $url > /dev/null 2>&1 &
    elif command -v gnome-open > /dev/null; then
        gnome-open $url > /dev/null 2>&1 &
    elif command -v open > /dev/null; then
        open $url > /dev/null 2>&1 &
    else
        echo -e "${YELLOW}⚠️ 자동으로 브라우저를 열 수 없습니다. 수동으로 접속하세요: $url${NC}"
    fi
}

# 포트 사용 프로세스 확인 및 안전한 처리
check_port_safely() {
    local port=$1
    local service_name=$2
    
    echo -e "${YELLOW}🔍 포트 $port 사용 프로세스 확인 중...${NC}"
    
    local pids=$(check_port $port)
    
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}⚠️ 포트 $port가 이미 사용 중입니다 (PID: $pids)${NC}"
        
        # SSH 관련 프로세스인지 확인
        local ssh_processes=$(echo "$pids" | xargs -I {} ps -p {} -o comm= 2>/dev/null | grep -E "sshd|ssh-agent|ssh|sftp|scp" || true)
        
        if [ ! -z "$ssh_processes" ]; then
            echo -e "${RED}🚨 SSH 관련 프로세스가 포트 $port를 사용 중입니다. 보안상 종료하지 않습니다.${NC}"
            echo -e "${YELLOW}💡 해결 방법: 다른 포트를 사용하거나 수동으로 확인하세요.${NC}"
            return 1
        fi
        
        # GAIA-BT 관련 프로세스만 안전하게 종료
        local gaia_processes=$(echo "$pids" | xargs -I {} ps -p {} -o cmd= 2>/dev/null | grep -E "gaia|api_server|webui|uvicorn.*app|node.*next" || true)
        
        if [ ! -z "$gaia_processes" ]; then
            echo -e "${YELLOW}🔄 $service_name 관련 프로세스만 안전하게 재시작합니다...${NC}"
            
            # GAIA-BT 관련 프로세스의 PID만 추출
            local gaia_pids=$(echo "$pids" | xargs -I {} bash -c 'ps -p {} -o cmd= 2>/dev/null | grep -E "gaia|api_server|webui|uvicorn.*app|node.*next" >/dev/null && echo {}' || true)
            
            if [ ! -z "$gaia_pids" ]; then
                echo -e "${YELLOW}🔪 GAIA-BT 프로세스 종료 중... (PID: $gaia_pids)${NC}"
                echo "$gaia_pids" | xargs -r kill -TERM 2>/dev/null
                sleep 3
                
                # 여전히 실행 중이면 강제 종료
                local remaining_gaia_pids=$(echo "$gaia_pids" | xargs -I {} bash -c 'kill -0 {} 2>/dev/null && echo {}' || true)
                if [ ! -z "$remaining_gaia_pids" ]; then
                    echo -e "${RED}💥 GAIA-BT 프로세스 강제 종료 중...${NC}"
                    echo "$remaining_gaia_pids" | xargs -r kill -KILL 2>/dev/null
                    sleep 1
                fi
            fi
        else
            echo -e "${YELLOW}⚠️ 포트 $port를 사용하는 프로세스가 GAIA-BT와 관련이 없습니다.${NC}"
            echo -e "${YELLOW}💡 서버 재시작을 계속 진행하지만, 포트 충돌이 발생할 수 있습니다.${NC}"
        fi
        
        # 최종 확인
        local final_pids=$(check_port $port)
        if [ -z "$final_pids" ]; then
            echo -e "${GREEN}✅ 포트 $port 정리 완료${NC}"
        else
            echo -e "${YELLOW}⚠️ 포트 $port에 여전히 다른 프로세스가 실행 중입니다${NC}"
            echo -e "${YELLOW}💡 해당 프로세스: $(echo "$final_pids" | xargs -I {} ps -p {} -o cmd= 2>/dev/null | head -1)${NC}"
        fi
    else
        echo -e "${GREEN}✅ 포트 $port 사용 가능${NC}"
    fi
    
    return 0
}

# 기존 함수명 호환성을 위한 별칭
kill_port_processes() {
    check_port_safely "$@"
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
    kill_port_processes 3003 "Next.js WebUI"
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
    
    # 포트 사용 가능 대기
    if ! wait_for_port_free 8000; then
        echo -e "${RED}❌ 포트 8000이 계속 사용 중입니다${NC}"
        return 1
    fi
    
    # API 서버 시작 (Deep Research용 30분 타임아웃)
    echo -e "${CYAN}🔗 API 서버 시작: http://localhost:8000${NC}"
    nohup python -m uvicorn app.api_server.main:app --reload --host 0.0.0.0 --port 8000 --timeout-keep-alive 1800 --timeout-graceful-shutdown 60 > /tmp/gaia-bt-api.log 2>&1 &
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
    kill_port_processes 3003 "Next.js WebUI"
    
    # 작업 디렉토리 확인
    local webui_dir="/home/gaia-bt/workspace/GAIA_LLMs/gaia_chat"
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
    
    # 포트 사용 가능 대기
    if ! wait_for_port_free 3003; then
        echo -e "${RED}❌ 포트 3003이 계속 사용 중입니다${NC}"
        return 1
    fi
    
    # WebUI 서버 시작
    echo -e "${CYAN}🔗 WebUI 서버 시작: http://localhost:3003${NC}"
    nohup npm run dev -- --hostname 0.0.0.0 --port 3003 > /tmp/gaia-bt-webui.log 2>&1 &
    local webui_pid=$!
    
    # 시작 확인 (더 긴 대기 시간)
    local wait_count=0
    while [ $wait_count -lt 10 ]; do
        if kill -0 $webui_pid 2>/dev/null; then
            # 포트 열림 확인
            if [ ! -z "$(check_port 3003)" ]; then
                echo -e "${GREEN}✅ Next.js WebUI 서버 시작 완료 (PID: $webui_pid)${NC}"
                echo -e "${CYAN}🌐 웹 인터페이스: http://localhost:3003${NC}"
                return 0
            fi
        fi
        echo -e "${YELLOW}⏳ WebUI 서버 시작 대기 중... ($wait_count/10)${NC}"
        sleep 1
        wait_count=$((wait_count + 1))
    done
    
    echo -e "${RED}❌ Next.js WebUI 서버 시작 실패${NC}"
    echo -e "${YELLOW}📄 로그 확인: tail -f /tmp/gaia-bt-webui.log${NC}"
    return 1
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
    local webui_pids=$(check_port 3003)
    if [ ! -z "$webui_pids" ]; then
        echo -e "${GREEN}✅ Next.js WebUI: 실행 중 (PID: $webui_pids)${NC}"
        echo -e "   🌐 WebUI: http://localhost:3003"
        
        # Health check
        if command -v curl >/dev/null 2>&1; then
            local webui_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3003 2>/dev/null)
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
    echo "  start-all      - 모든 서버 시작 후 브라우저 자동 실행"
    echo "  stop           - 모든 서버 중지"
    echo "  restart        - 모든 서버 재시작"
    echo "  restart-all    - 모든 서버 재시작 후 브라우저 자동 실행"
    echo "  status         - 서버 상태 확인"
    echo "  open           - WebUI를 브라우저에서 열기"
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
    echo "  📱 WebUI: $WEBUI_URL"
    echo "  🔗 API: $API_URL"
    echo "  📖 API 문서: $API_URL/docs"
}

# 메인 함수
main() {
    print_banner
    
    case "${1:-start}" in
        "start")
            stop_all_servers
            # 포트 완전 해제 확인
            sleep 2
            if start_api_server && start_webui_server; then
                sleep 2
                check_server_status
            else
                echo -e "${RED}❌ 서버 시작 실패${NC}"
                exit 1
            fi
            ;;
        "start-all")
            stop_all_servers
            # 포트 완전 해제 확인
            sleep 2
            if start_api_server && start_webui_server; then
                sleep 2
                check_server_status
                # 브라우저 자동 실행
                open_browser $WEBUI_URL true
            else
                echo -e "${RED}❌ 서버 시작 실패${NC}"
                exit 1
            fi
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
        "restart-all")
            stop_all_servers
            sleep 2
            start_api_server && start_webui_server
            sleep 2
            check_server_status
            # 브라우저 자동 실행
            open_browser $WEBUI_URL true
            ;;
        "open")
            open_browser $WEBUI_URL false
            ;;
        "status")
            check_server_status
            ;;
        "start-api")
            kill_port_processes 8000 "FastAPI Backend"
            start_api_server
            ;;
        "start-webui")
            kill_port_processes 3003 "Next.js WebUI"
            start_webui_server
            ;;
        "stop-api")
            kill_port_processes 8000 "FastAPI Backend"
            ;;
        "stop-webui")
            kill_port_processes 3003 "Next.js WebUI"
            ;;
        "kill-port")
            if [ -z "$2" ]; then
                echo -e "${RED}❌ 포트 번호를 지정해주세요: $0 kill-port 3001${NC}"
                exit 1
            fi
            kill_port_processes "$2" "Port $2"
            ;;
        "clean-ports")
            kill_port_processes 3003 "Next.js WebUI"
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