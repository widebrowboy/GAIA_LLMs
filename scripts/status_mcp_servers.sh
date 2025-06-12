#!/bin/bash

# MCP 서버 상태 확인 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_DIR="$PROJECT_ROOT/.mcp_pids"

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== MCP 서버 상태 ===${NC}"
echo ""

# 서버 상태 확인 함수
check_server() {
    local name=$1
    local pid_file="$PID_DIR/$name.pid"
    
    echo -n -e "${YELLOW}$name:${NC} "
    
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 실행 중 (PID: $pid)${NC}"
            
            # 프로세스 정보 표시
            ps_info=$(ps -p "$pid" -o %cpu,%mem,etime,cmd --no-headers)
            echo "  └─ CPU/MEM/실행시간: $(echo "$ps_info" | awk '{print $1"% / "$2"% / "$3}')"
            
            # 로그 파일 크기
            log_file="$PID_DIR/$name.log"
            if [ -f "$log_file" ]; then
                log_size=$(du -h "$log_file" | cut -f1)
                echo "  └─ 로그 크기: $log_size"
            fi
        else
            echo -e "${RED}✗ 중지됨 (PID 파일은 존재)${NC}"
            rm -f "$pid_file"
        fi
    else
        echo -e "${RED}✗ 실행되지 않음${NC}"
    fi
}

# 각 서버 상태 확인
check_server "gaia-mcp"
echo ""
check_server "biomcp"
echo ""
check_server "chembl"
echo ""
check_server "sequential-thinking"

echo ""
echo -e "${BLUE}=== 명령어 ===${NC}"
echo "서버 시작: $SCRIPT_DIR/run_mcp_servers.sh"
echo "서버 중지: $SCRIPT_DIR/stop_mcp_servers.sh"
echo "로그 확인: tail -f $PID_DIR/*.log"

# 실행 중인 서버가 있으면 포트 정보 표시
if ls "$PID_DIR"/*.pid 1> /dev/null 2>&1; then
    echo ""
    echo -e "${BLUE}=== 네트워크 포트 ===${NC}"
    # MCP 관련 포트 확인 (8765 등)
    netstat -tlnp 2>/dev/null | grep -E ':(8765|8766|8767)' | grep LISTEN || echo "표준 입출력(stdio) 모드로 실행 중"
fi