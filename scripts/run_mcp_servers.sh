#!/bin/bash

# MCP 서버 동시 실행 스크립트
# 이 스크립트는 GAIA, BiomCP, Sequential Thinking 서버를 동시에 실행합니다.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "GAIA MCP 서버들을 시작합니다..."

# PID 파일 경로
PID_DIR="$PROJECT_ROOT/.mcp_pids"
mkdir -p "$PID_DIR"

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 서버 시작 함수
start_server() {
    local name=$1
    local cmd=$2
    local pid_file="$PID_DIR/$name.pid"
    
    echo -e "${YELLOW}$name 서버 시작 중...${NC}"
    
    # 기존 프로세스 확인
    if [ -f "$pid_file" ]; then
        old_pid=$(cat "$pid_file")
        if ps -p "$old_pid" > /dev/null 2>&1; then
            echo -e "${RED}$name 서버가 이미 실행 중입니다 (PID: $old_pid)${NC}"
            return 1
        fi
    fi
    
    # 서버 시작
    eval "$cmd" &
    local pid=$!
    echo $pid > "$pid_file"
    
    # 서버 시작 확인
    sleep 2
    if ps -p "$pid" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $name 서버가 성공적으로 시작되었습니다 (PID: $pid)${NC}"
        return 0
    else
        echo -e "${RED}✗ $name 서버 시작에 실패했습니다${NC}"
        rm -f "$pid_file"
        return 1
    fi
}

# 1. GAIA MCP 서버 시작
cd "$PROJECT_ROOT"
start_server "gaia-mcp" "python -m mcp.run_server --transport stdio > $PID_DIR/gaia-mcp.log 2>&1"

# 2. BiomCP 서버 시작
export PYTHONPATH="$PROJECT_ROOT/mcp/biomcp/src:$PYTHONPATH"
start_server "biomcp" "biomcp run --mode stdio > $PID_DIR/biomcp.log 2>&1"

# 3. ChEMBL 서버 시작
export PYTHONPATH="$PROJECT_ROOT/mcp/chembl:$PYTHONPATH"
start_server "chembl" "python $PROJECT_ROOT/mcp/chembl/chembl_server.py --transport stdio > $PID_DIR/chembl.log 2>&1"

# 4. Sequential Thinking Python 서버 시작
export PYTHONPATH="$PROJECT_ROOT/mcp/python-sequential-thinking/src:$PYTHONPATH"
start_server "sequential-thinking" "sequential-thinking run > $PID_DIR/sequential-thinking.log 2>&1"

# 5. PubMed MCP 서버 시작
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
start_server "pubmed-mcp" "python $PROJECT_ROOT/mcp/pubmed/pubmed_mcp.py > $PID_DIR/pubmed-mcp.log 2>&1"

# 6. ClinicalTrials MCP 서버 시작
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
start_server "clinicaltrials-mcp" "python $PROJECT_ROOT/mcp/clinicaltrials/clinicaltrials_mcp.py > $PID_DIR/clinicaltrials-mcp.log 2>&1"

echo ""
echo "모든 MCP 서버가 시작되었습니다."
echo "서버 중지: $SCRIPT_DIR/stop_mcp_servers.sh"
echo "서버 상태 확인: $SCRIPT_DIR/status_mcp_servers.sh"
echo "로그 확인: tail -f $PID_DIR/*.log"