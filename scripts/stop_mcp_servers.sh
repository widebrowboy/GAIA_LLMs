#!/bin/bash

# MCP 서버 중지 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_DIR="$PROJECT_ROOT/.mcp_pids"

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "MCP 서버들을 중지합니다..."

# 서버 중지 함수
stop_server() {
    local name=$1
    local pid_file="$PID_DIR/$name.pid"
    
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}$name 서버 중지 중... (PID: $pid)${NC}"
            kill "$pid"
            
            # 프로세스 종료 대기 (최대 5초)
            count=0
            while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 5 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # 강제 종료 필요시
            if ps -p "$pid" > /dev/null 2>&1; then
                echo -e "${RED}강제 종료 중...${NC}"
                kill -9 "$pid"
            fi
            
            echo -e "${GREEN}✓ $name 서버가 중지되었습니다${NC}"
        else
            echo -e "${YELLOW}$name 서버가 실행되고 있지 않습니다${NC}"
        fi
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}$name 서버 PID 파일이 없습니다${NC}"
    fi
}

# 모든 서버 중지
stop_server "gaia-mcp"
stop_server "biomcp"
stop_server "chembl"
stop_server "sequential-thinking"

# 로그 파일 정리 옵션
read -p "로그 파일을 삭제하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f "$PID_DIR"/*.log
    echo -e "${GREEN}로그 파일이 삭제되었습니다${NC}"
fi

echo ""
echo "모든 MCP 서버가 중지되었습니다."