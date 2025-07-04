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
ATTU_PORT=8080
API_URL="http://localhost:${API_PORT}"
WEBUI_URL="http://localhost:${WEBUI_PORT}"
ATTU_URL="http://localhost:${ATTU_PORT}"
API_LOG="/tmp/gaia-bt-api.log"
WEBUI_LOG="/tmp/gaia-bt-webui.log"
ATTU_LOG="/tmp/gaia-bt-attu.log"

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

# 개발 프로세스 식별 함수
identify_gaia_process() {
    local pid=$1
    
    # 🔍 PID 존재 여부 먼저 확인 (v3.87+ 신규)
    if ! ps -p $pid > /dev/null 2>&1; then
        return 1  # 존재하지 않는 PID는 GAIA 프로세스가 아님
    fi
    
    local cmd=$(ps -p $pid -o cmd= 2>/dev/null || echo "")
    
    # GAIA-BT 관련 프로세스 패턴들
    if echo "$cmd" | grep -qE "(gaia|GAIA)" || \
       echo "$cmd" | grep -qE "run_api_server|api_server" || \
       echo "$cmd" | grep -qE "uvicorn.*app\.api_server" || \
       echo "$cmd" | grep -qE "uvicorn.*main:app" || \
       echo "$cmd" | grep -qE "npm.*dev.*gaia_chat" || \
       echo "$cmd" | grep -qE "node.*next.*gaia_chat" || \
       echo "$cmd" | grep -qE "fastapi.*gaia" || \
       echo "$cmd" | grep -qE "python.*workspace/GAIA_LLMs" || \
       echo "$cmd" | grep -qE "attu.*gaia" || \
       echo "$cmd" | grep -qE "docker.*gaia-attu"; then
        return 0
    fi
    
    # 작업 디렉토리로 확인
    local cwd=$(pwdx $pid 2>/dev/null | cut -d' ' -f2- || echo "")
    if echo "$cwd" | grep -qE "GAIA_LLMs|gaia_chat"; then
        return 0
    fi
    
    return 1
}

# 보호된 프로세스 식별 함수 (v3.87+ 최강화)
is_protected_process() {
    local pid=$1
    
    # 🔍 PID 존재 여부 먼저 확인 (v3.87+ 신규)
    if ! ps -p $pid > /dev/null 2>&1; then
        echo "  ❌ [존재하지않음] PID $pid - 프로세스가 존재하지 않아 건너뜀" >&2
        return 1  # 존재하지 않는 PID는 보호하지 않음
    fi
    
    local comm=$(ps -p $pid -o comm= 2>/dev/null || echo "")
    local cmd=$(ps -p $pid -o cmd= 2>/dev/null || echo "")
    local port_info=$(lsof -p $pid 2>/dev/null | grep LISTEN || echo "")
    local cwd=$(pwdx $pid 2>/dev/null | cut -d' ' -f2- || echo "")
    local parent_pid=$(ps -p $pid -o ppid= 2>/dev/null | tr -d ' ')
    local parent_cmd=$(ps -p $parent_pid -o cmd= 2>/dev/null || echo "")
    
    # 🔥 Claude Code 프로세스 보호 (v3.87+ 최강화)
    if echo "$cmd" | grep -qiE "(claude|anthropic)" || \
       echo "$comm" | grep -qiE "^claude$" || \
       [ "$comm" = "claude" ]; then
        echo "  🤖 [Claude Code] PID $pid - Claude Code CLI 프로세스: $comm" >&2
        return 0
    fi
    
    # 🔥 Claude Code 명시적 PID 보호 (v3.87+ 신규)
    local current_claude_pids=$(ps aux | grep -E "claude" | grep -v grep | awk '{print $2}' 2>/dev/null)
    for claude_pid in $current_claude_pids; do
        if [ "$pid" = "$claude_pid" ]; then
            echo "  🤖 [Claude Code PID] PID $pid - 명시적 Claude Code 프로세스" >&2
            return 0
        fi
    done
    
    # 🔥 Claude Code 실행 위치 기반 보호 (v3.87+ 신규)
    if echo "$cwd" | grep -qE "(claude|anthropic|code)" && \
       echo "$cmd" | grep -qiE "(claude|code|cli)"; then
        echo "  🤖 [Claude Code 위치] PID $pid - Claude Code 작업 디렉토리에서 실행" >&2
        return 0
    fi
    
    # 🔥 현재 스크립트와 관련된 프로세스 보호 (v3.87+ 강화)
    local current_script_pid=$$
    local current_script_name="server_manager.sh"
    
    # 현재 스크립트 프로세스 자체 보호
    if [ "$pid" = "$current_script_pid" ]; then
        echo "  📜 [현재스크립트] PID $pid - 현재 실행 중인 server_manager.sh" >&2
        return 0
    fi
    
    # 현재 스크립트를 실행한 부모 프로세스 보호
    local script_parent_pid=$(ps -p $current_script_pid -o ppid= 2>/dev/null | tr -d ' ')
    if [ "$pid" = "$script_parent_pid" ]; then
        echo "  📜 [스크립트부모] PID $pid - server_manager.sh를 실행한 터미널" >&2
        return 0
    fi
    
    # 🚨 포트 22 (SSH) 사용 프로세스는 절대 보호 - 최우선
    if echo "$port_info" | grep -q ":22 "; then
        echo "  🔐 [SSH 포트] PID $pid - SSH 서버 프로세스 (포트 22 사용)" >&2
        return 0
    fi
    
    # 🔒 SSH 관련 프로세스 (최강화된 패턴)
    if echo "$comm" | grep -qE "^(sshd|ssh-agent|ssh|sftp|scp|ssh-add|ssh-keygen|ssh-copy-id|ssh-askpass|remote-ssh)$"; then
        echo "  🔐 [SSH 프로세스] PID $pid - SSH 관련 프로세스: $comm" >&2
        return 0
    fi
    
    # 💻 IDE 및 에디터 프로세스 (최강화된 보호)
    # Windsurf, VSCode, Cursor 등 메인 IDE 프로세스
    if echo "$comm" | grep -qE "^(windsurf|code|cursor)$" || \
       echo "$comm" | grep -qE "^(windsurf-desktop|code-tunnel|code-server|vscode-server|remote-ssh|ms-vscode)$" || \
       echo "$comm" | grep -qE "^(webstorm|intellij|phpstorm|pycharm|goland|clion|datagrip|rider|rubymine|appcode|mps|gateway)$"; then
        echo "  💻 [IDE 메인] PID $pid - IDE 에디터 프로세스: $comm" >&2
        return 0
    fi
    
    # 🌐 Node.js/Electron 기반 IDE 프로세스 (초정밀 검사)
    if echo "$comm" | grep -qE "^(node|npm|npx|electron)$"; then
        # IDE 관련 키워드 최강화된 검사
        if echo "$cmd" | grep -qE "(windsurf|windsurf-desktop|windsurf.*app)" || \
           echo "$cmd" | grep -qE "(vscode|code.*server|code.*tunnel|ms-vscode)" || \
           echo "$cmd" | grep -qE "(cursor|cursor.*app|cursor.*server)" || \
           echo "$cmd" | grep -qE "(@windsurf|@vscode|@cursor|@codeium)" || \
           echo "$cmd" | grep -qE "(\.vscode|\.windsurf|\.cursor|\.continue)" || \
           echo "$cmd" | grep -qE "(extension|languageserver|lsp-server|extensionHost)" || \
           echo "$cmd" | grep -qE "(remote.*development|development.*server|development.*tunnel)" || \
           echo "$cmd" | grep -qE "(copilot|github.*copilot|claude.*dev|ai.*assistant)"; then
            echo "  🌐 [IDE Node.js] PID $pid - IDE Node.js 프로세스" >&2
            return 0
        fi
        
        # 포트포워딩 및 원격 터널링 프로세스 보호
        if echo "$cmd" | grep -qE "ssh.*-[LR].*[0-9]+|LocalForward|RemoteForward" || \
           echo "$cmd" | grep -qE "(tunnel.*port|port.*tunnel|proxy.*tunnel|remote.*tunnel)" || \
           echo "$cmd" | grep -qE "(port.*forward|forward.*port|ssh.*tunnel)"; then
            echo "  🔗 [포트포워딩] PID $pid - SSH 터널링/포트포워딩 프로세스" >&2
            return 0
        fi
        
        # IDE 작업 디렉토리 검사 (추가 보호)
        if echo "$cwd" | grep -qE "(\.vscode|\.windsurf|\.cursor|\.continue|vscode.*server|remote.*development)"; then
            echo "  📁 [IDE 작업공간] PID $pid - IDE 작업 디렉토리에서 실행" >&2
            return 0
        fi
    fi
    
    # 🔗 원격 개발 환경 프로세스 (최고 보안)
    if echo "$cmd" | grep -qE "(vscode-server|remote-ssh|ssh-tunnel|remote.*tunnel)" || \
       echo "$cmd" | grep -qE "(jetbrains.*remote|intellij.*remote|pycharm.*remote)" || \
       echo "$cmd" | grep -qE "(windsurf.*server|cursor.*server|code.*server)" || \
       echo "$cmd" | grep -qE "(devcontainer|dev.*container|remote.*container)" || \
       echo "$cmd" | grep -qE "(github.*copilot|copilot.*lsp|copilot.*agent)" || \
       echo "$cmd" | grep -qE "(remote.*development|development.*tunnel|tunnel.*development)"; then
        echo "  🔗 [원격개발] PID $pid - 원격 개발 환경 프로세스" >&2
        return 0
    fi
    
    # 🧩 IDE Extension Host 및 Language Server (최강 보호)
    if echo "$cmd" | grep -qE "(extensionHost|extension.*host|host.*extension)" || \
       echo "$cmd" | grep -qE "(@vscode.*extension|@windsurf.*extension|@cursor.*extension)" || \
       echo "$cmd" | grep -qE "(language.*server|lsp.*server|languageserver)" || \
       echo "$cmd" | grep -qE "(typescript.*server|python.*server|rust.*analyzer|pylsp|pyright)" || \
       echo "$cmd" | grep -qE "(copilot.*agent|claude.*agent|ai.*assistant|codeium.*agent)" || \
       echo "$cmd" | grep -qE "(eslint.*server|prettier.*server|formatter.*server)"; then
        echo "  🧩 [언어서버] PID $pid - IDE Extension/Language Server" >&2
        return 0
    fi
    
    # 🔧 개발 도구 및 빌드 시스템 데몬 (v3.87+ 추가 보호)
    if echo "$comm" | grep -qE "^(git|docker|kubectl|helm|terraform|vagrant)$" && \
       echo "$cmd" | grep -qE "(daemon|server|watch|continuous|monitor)"; then
        echo "  🔧 [개발도구] PID $pid - 개발 도구 데몬: $comm" >&2
        return 0
    fi
    
    # 🖥️ 시스템 핵심 프로세스 보호 (절대 보호)
    if echo "$comm" | grep -qE "^(systemd|init|kernel|dbus|NetworkManager|systemd-|gdm|gnome-session|pulseaudio|pipewire|avahi-daemon)$"; then
        echo "  🖥️ [시스템] PID $pid - 시스템 핵심 프로세스: $comm" >&2
        return 0
    fi
    
    # 🖥️ Windsurf/VSCode 통합 터미널 보호 (v3.88+ 신규)
    if echo "$comm" | grep -qE "^(bash|zsh|fish|sh|dash)$"; then
        # 부모나 조상 프로세스가 Windsurf/VSCode 관련인 경우 보호
        local check_ancestor_pid=$parent_pid
        local ancestor_depth=0
        while [ "$check_ancestor_pid" != "1" ] && [ ! -z "$check_ancestor_pid" ] && [ $ancestor_depth -lt 5 ]; do
            local ancestor_cmd=$(ps -p $check_ancestor_pid -o args= 2>/dev/null | head -c 200)
            if echo "$ancestor_cmd" | grep -qE "(windsurf|vscode|code.*server|cursor)" || \
               echo "$ancestor_cmd" | grep -qE "(.windsurf-server|.vscode-server|.cursor-server)"; then
                echo "  🖥️ [IDE 터미널] PID $pid - Windsurf/VSCode 통합 터미널 세션" >&2
                return 0
            fi
            check_ancestor_pid=$(ps -p $check_ancestor_pid -o ppid= 2>/dev/null | tr -d ' ')
            ancestor_depth=$((ancestor_depth + 1))
        done
    fi
    
    # 💬 터미널 및 쉘 세션 보호 (SSH 연결 고려)
    if echo "$comm" | grep -qE "^(bash|zsh|fish|sh|dash|tmux|screen|gnome-terminal|xterm|konsole|alacritty|kitty|tilix)$"; then
        # 부모 프로세스가 SSH 관련인 경우 절대 보호
        if echo "$parent_cmd" | grep -qE "(ssh|sshd|remote|tunnel)"; then
            echo "  💬 [SSH 터미널] PID $pid - SSH 연결을 통한 터미널 세션" >&2
            return 0
        fi
        
        # 로그인 세션이나 시스템 터미널 프로세스는 보호
        if [ "$parent_pid" = "1" ] || echo "$cmd" | grep -qE "(login|session|terminal|shell|tty)"; then
            echo "  💬 [시스템터미널] PID $pid - 시스템 터미널 세션" >&2
            return 0
        fi
        
        # 현재 사용자 세션과 동일한 TTY를 사용하는 쉘 보호 (v3.87+ 강화)
        local current_tty=$(tty 2>/dev/null | sed 's|/dev/||' || echo "")
        local current_ppid=$$
        local current_session_id=$(ps -p $$ -o sid= 2>/dev/null | tr -d ' ')
        
        if [ ! -z "$current_tty" ]; then
            local proc_tty=$(ps -p $pid -o tty= 2>/dev/null | tr -d ' ')
            local proc_session_id=$(ps -p $pid -o sid= 2>/dev/null | tr -d ' ')
            
            # 현재 TTY 또는 세션 ID가 같은 경우 보호
            if [ "$proc_tty" = "$current_tty" ] || [ "$proc_session_id" = "$current_session_id" ]; then
                echo "  💬 [현재터미널] PID $pid - 현재 터미널 세션 (TTY: $current_tty, SID: $current_session_id)" >&2
                return 0
            fi
            
            # 현재 프로세스의 조상 프로세스인 경우 보호 (프로세스 트리 완전 검사)
            local check_pid=$current_ppid
            local ancestry_depth=0
            while [ "$check_pid" != "1" ] && [ ! -z "$check_pid" ] && [ $ancestry_depth -lt 10 ]; do
                if [ "$check_pid" = "$pid" ]; then
                    echo "  💬 [조상터미널] PID $pid - 현재 스크립트의 조상 터미널 프로세스 (depth: $ancestry_depth)" >&2
                    return 0
                fi
                check_pid=$(ps -p $check_pid -o ppid= 2>/dev/null | tr -d ' ')
                ancestry_depth=$((ancestry_depth + 1))
            done
        fi
        
        # 현재 스크립트와 동일한 프로세스 그룹에 속한 경우 보호 (v3.87+ 신규)
        local current_pgid=$(ps -p $$ -o pgid= 2>/dev/null | tr -d ' ')
        local proc_pgid=$(ps -p $pid -o pgid= 2>/dev/null | tr -d ' ')
        
        if [ ! -z "$current_pgid" ] && [ "$current_pgid" = "$proc_pgid" ]; then
            echo "  💬 [동일그룹터미널] PID $pid - 현재 스크립트와 동일한 프로세스 그룹 (PGID: $current_pgid)" >&2
            return 0
        fi
    fi
    
    # 🌍 웹 브라우저 및 개발 프록시 (보조 보호)
    if echo "$comm" | grep -qE "^(chrome|firefox|safari|edge|brave)$" && \
       echo "$cmd" | grep -qE "(remote.*debug|dev.*tools|proxy|tunnel)"; then
        echo "  🌍 [브라우저개발] PID $pid - 브라우저 개발도구/프록시" >&2
        return 0
    fi
    
    return 1
}

# 보호된 포트 확인 함수
is_protected_port() {
    local port=$1
    
    # SSH 포트 (22) 절대 보호
    if [ "$port" = "22" ]; then
        return 0
    fi
    
    # 시스템 중요 포트들 (1-1023 중 중요한 것들)
    if echo "$port" | grep -qE "^(21|23|25|53|80|110|143|443|993|995)$"; then
        return 0
    fi
    
    # IDE/개발 도구 관련 포트들 (일반적으로 사용되는 포트들)
    # 이 포트들은 특별히 확인 후 처리
    if echo "$port" | grep -qE "^(3000|3001|4000|5000|5173|8080|9000)$"; then
        # 이 포트들은 보호하지 않지만 더 신중하게 처리
        return 1
    fi
    
    return 1
}

# 포트 사용 프로세스 확인 및 안전한 처리
check_port_safely() {
    local port=$1
    local service_name=$2
    
    # 보호된 포트 확인
    if is_protected_port $port; then
        echo -e "${RED}🚨 포트 $port는 시스템 중요 포트입니다. 정리하지 않습니다.${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}🔍 포트 $port 사용 프로세스 확인 중...${NC}"
    
    local pids=$(check_port $port)
    
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}⚠️ 포트 $port가 이미 사용 중입니다 (PID: $pids)${NC}"
        
        local protected_pids=""
        local gaia_pids=""
        local other_pids=""
        
        # 각 프로세스를 분류
        for pid in $pids; do
            # 🔍 PID 존재 여부 먼저 확인 (v3.87+ 신규)
            if ! ps -p $pid > /dev/null 2>&1; then
                continue  # 존재하지 않는 PID는 건너뛰기
            fi
            
            if is_protected_process $pid; then
                protected_pids="$protected_pids $pid"
            elif identify_gaia_process $pid; then
                gaia_pids="$gaia_pids $pid"
            else
                other_pids="$other_pids $pid"
            fi
        done
        
        # 보호된 프로세스가 있는 경우 (v3.87 상세 분류 강화)
        if [ ! -z "$protected_pids" ]; then
            echo -e "${RED}🚨 중요 시스템/개발 프로세스가 포트 $port를 사용 중입니다.${NC}"
            echo -e "${RED}🔒 안전상 이 프로세스들은 종료하지 않습니다:${NC}"
            echo -e "${YELLOW}📋 보호된 프로세스 상세 분류:${NC}"
            
            for pid in $protected_pids; do
                # 🔍 PID 존재 여부 재확인 (v3.87+ 신규)
                if ! ps -p $pid > /dev/null 2>&1; then
                    continue  # 존재하지 않는 PID는 건너뛰기
                fi
                
                local proc_name=$(ps -p $pid -o comm= 2>/dev/null || echo "unknown")
                local proc_cmd=$(ps -p $pid -o cmd= 2>/dev/null | cut -c1-100 || echo "unknown")
                local proc_type="일반"
                local proc_icon="🔒"
                local proc_risk="높음"
                
                # 프로세스 유형별 상세 분류 (v3.87 강화)
                if echo "$proc_cmd" | grep -qE "(ssh|sshd)"; then
                    proc_type="SSH 원격접속"
                    proc_icon="🔐"
                    proc_risk="매우높음"
                elif echo "$proc_cmd" | grep -qE "(windsurf|vscode|cursor|code.*server)"; then
                    proc_type="IDE 편집기"
                    proc_icon="💻"
                    proc_risk="높음"
                elif echo "$proc_cmd" | grep -qE "(tunnel|remote|port.*forward|LocalForward|RemoteForward)"; then
                    proc_type="포트포워딩/터널링"
                    proc_icon="🔗"
                    proc_risk="높음"
                elif echo "$proc_cmd" | grep -qE "(extension|languageserver|lsp)"; then
                    proc_type="IDE 확장/언어서버"
                    proc_icon="🧩"
                    proc_risk="중간"
                elif echo "$proc_cmd" | grep -qE "(copilot|claude|ai.*assistant)"; then
                    proc_type="AI 개발도구"
                    proc_icon="🤖"
                    proc_risk="중간"
                elif echo "$proc_cmd" | grep -qE "(systemd|init|dbus|NetworkManager)"; then
                    proc_type="시스템 핵심서비스"
                    proc_icon="🖥️"
                    proc_risk="매우높음"
                elif echo "$proc_cmd" | grep -qE "(bash|zsh|fish|terminal)"; then
                    proc_type="터미널/쉘 세션"
                    proc_icon="💬"
                    proc_risk="높음"
                elif echo "$proc_cmd" | grep -qE "(docker|git|kubectl)"; then
                    proc_type="개발도구 데몬"
                    proc_icon="🔧"
                    proc_risk="중간"
                fi
                
                echo -e "${YELLOW}   $proc_icon PID $pid [위험도: $proc_risk] $proc_type${NC}"
                echo -e "${YELLOW}      프로세스: $proc_name${NC}"
                echo -e "${YELLOW}      명령어: $proc_cmd${NC}"
                echo ""
            done
            
            echo -e "${CYAN}💡 해결 방법 (우선순위별):${NC}"
            echo -e "${CYAN}   1. 🔄 다른 포트 사용: GAIA-BT 설정에서 포트 변경${NC}"
            echo -e "${CYAN}   2. 🔍 연결 상태 확인: SSH/IDE 연결이 활성 상태인지 확인${NC}"
            echo -e "${CYAN}   3. 🛡️ 수동 검사: ps -fp $protected_pids${NC}"
            echo -e "${CYAN}   4. 🌐 포트포워딩: Windsurf/VSCode Remote 설정 확인${NC}"
            echo -e "${CYAN}   5. ⚠️ 주의사항: 이 프로세스들을 강제 종료하면 연결이 끊어집니다!${NC}"
            echo ""
            echo -e "${RED}🚫 GAIA-BT는 현재 이 포트를 사용할 수 없습니다.${NC}"
            return 1
        fi
        
        # GAIA-BT 관련 프로세스 종료
        if [ ! -z "$gaia_pids" ]; then
            echo -e "${YELLOW}🔄 GAIA-BT 개발 프로세스만 안전하게 재시작합니다...${NC}"
            for pid in $gaia_pids; do
                local proc_cmd=$(ps -p $pid -o cmd= 2>/dev/null | cut -c1-60 || echo "unknown")
                echo -e "${YELLOW}   - PID $pid: $proc_cmd${NC}"
            done
            
            echo -e "${YELLOW}🔪 GAIA-BT 프로세스 종료 중... (PID: $gaia_pids)${NC}"
            echo "$gaia_pids" | xargs -r kill -TERM 2>/dev/null
            sleep 3
            
            # 여전히 실행 중이면 강제 종료
            local remaining_pids=""
            for pid in $gaia_pids; do
                if kill -0 $pid 2>/dev/null; then
                    remaining_pids="$remaining_pids $pid"
                fi
            done
            
            if [ ! -z "$remaining_pids" ]; then
                echo -e "${RED}💥 GAIA-BT 프로세스 강제 종료 중... (PID: $remaining_pids)${NC}"
                echo "$remaining_pids" | xargs -r kill -KILL 2>/dev/null
                sleep 1
            fi
        fi
        
        # 다른 프로세스에 대한 경고
        if [ ! -z "$other_pids" ]; then
            echo -e "${YELLOW}⚠️ 포트 $port를 사용하는 다른 프로세스가 있습니다:${NC}"
            for pid in $other_pids; do
                local proc_cmd=$(ps -p $pid -o cmd= 2>/dev/null | cut -c1-60 || echo "unknown")
                echo -e "${YELLOW}   - PID $pid: $proc_cmd${NC}"
            done
            echo -e "${YELLOW}💡 이 프로세스들은 자동으로 종료되지 않습니다.${NC}"
        fi
        
        # 최종 확인
        local final_pids=$(check_port $port)
        if [ -z "$final_pids" ]; then
            echo -e "${GREEN}✅ 포트 $port 정리 완료${NC}"
        else
            echo -e "${YELLOW}⚠️ 포트 $port에 여전히 프로세스가 실행 중입니다${NC}"
            for pid in $final_pids; do
                if ! is_protected_process $pid; then
                    local proc_cmd=$(ps -p $pid -o cmd= 2>/dev/null | cut -c1-60 || echo "unknown")
                    echo -e "${YELLOW}   - PID $pid: $proc_cmd${NC}"
                fi
            done
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

# 연결 상태 확인 및 보고 함수 (v3.87+ 신규)
check_connection_status() {
    local context=${1:-"일반"}
    
    echo -e "${YELLOW}🔍 $context 연결 상태 확인 중...${NC}"
    
    # SSH 연결 확인
    local ssh_connections=$(ps aux | grep sshd | grep -v "sshd:" | grep -v grep | wc -l)
    local ssh_status=""
    if [ "$ssh_connections" -gt 0 ]; then
        ssh_status="${GREEN}  🔐 SSH 연결: $ssh_connections 개 (활성)${NC}"
    else
        ssh_status="${YELLOW}  🔐 SSH 연결: 없음${NC}"
    fi
    
    # IDE 프로세스 확인  
    local ide_processes=$(ps aux | grep -E "(windsurf|code|cursor)" | grep -v grep | wc -l)
    local ide_status=""
    if [ "$ide_processes" -gt 0 ]; then
        ide_status="${GREEN}  💻 IDE 프로세스: $ide_processes 개 (활성)${NC}"
    else
        ide_status="${YELLOW}  💻 IDE 프로세스: 없음${NC}"
    fi
    
    # Claude Code 프로세스 확인 (v3.87+ 강화)
    local claude_processes=$(ps aux | grep -E "claude" | grep -v grep | wc -l)
    local claude_pids=$(ps aux | grep -E "claude" | grep -v grep | awk '{print $2}' 2>/dev/null | tr '\n' ' ')
    local claude_status=""
    if [ "$claude_processes" -gt 0 ]; then
        claude_status="${GREEN}  🤖 Claude Code: $claude_processes 개 (활성, PID: $claude_pids)${NC}"
    else
        claude_status="${YELLOW}  🤖 Claude Code: 없음${NC}"
    fi
    
    # 포트포워딩 확인
    local tunnel_processes=$(ps aux | grep -E "(tunnel|LocalForward|RemoteForward)" | grep -v grep | wc -l)
    local tunnel_status=""
    if [ "$tunnel_processes" -gt 0 ]; then
        tunnel_status="${GREEN}  🔗 터널링: $tunnel_processes 개 (활성)${NC}"
    else
        tunnel_status="${YELLOW}  🔗 터널링: 없음${NC}"
    fi
    
    # 현재 터미널 세션 확인
    local current_tty=$(tty 2>/dev/null | sed 's|/dev/||' || echo "unknown")
    local current_session_id=$(ps -p $$ -o sid= 2>/dev/null | tr -d ' ')
    local terminal_status="${GREEN}  💬 현재 터미널: $current_tty (SID: $current_session_id)${NC}"
    
    echo -e "$ssh_status"
    echo -e "$ide_status" 
    echo -e "$claude_status"
    echo -e "$tunnel_status"
    echo -e "$terminal_status"
    echo ""
    
    # 위험도 평가
    local critical_connections=$((ssh_connections + ide_processes + claude_processes))
    if [ "$critical_connections" -gt 0 ]; then
        echo -e "${CYAN}🛡️ 중요 연결 감지: $critical_connections 개 프로세스가 보호됩니다${NC}"
        return 0
    else
        echo -e "${GREEN}✅ 보호 대상 연결 없음: 안전한 재시작 가능${NC}"
        return 1
    fi
}

# 안전한 서버 중지 함수 (SSH/IDE/Claude Code 연결 보호 최강화)
stop_all_servers() {
    echo -e "${CYAN}🛑 모든 GAIA-BT 서버 안전 중지 중... (SSH/IDE/Claude Code 보호)${NC}"
    
    # Claude Code 프로세스 사전 확인 및 보호 (v3.87+ 신규)
    local claude_pids=$(ps aux | grep -E "claude" | grep -v grep | awk '{print $2}' 2>/dev/null)
    if [ ! -z "$claude_pids" ]; then
        echo -e "${GREEN}🤖 Claude Code 프로세스 감지 및 보호: PID $claude_pids${NC}"
        for claude_pid in $claude_pids; do
            local claude_cmd=$(ps -p $claude_pid -o cmd= 2>/dev/null | cut -c1-80 || echo "unknown")
            echo -e "${GREEN}   🛡️ 보호됨 - PID $claude_pid: $claude_cmd${NC}"
        done
        echo ""
    fi
    
    # 현재 연결 상태 사전 확인
    check_connection_status "중지 전"
    
    # 모든 실행 중인 프로세스를 스캔하여 GAIA-BT 관련 프로세스만 식별
    local all_pids=$(ps -eo pid --no-headers)
    local gaia_pids=""
    local protected_pids=""
    
    echo -e "${YELLOW}🔍 GAIA-BT 관련 프로세스 식별 중...${NC}"
    
    for pid in $all_pids; do
        # 🔍 PID 존재 여부 먼저 확인 (v3.87+ 신규)
        if ! ps -p $pid > /dev/null 2>&1; then
            continue  # 존재하지 않는 PID는 건너뛰기
        fi
        
        if identify_gaia_process $pid; then
            # GAIA-BT 프로세스 중에서도 보호 대상 확인
            if is_protected_process $pid >/dev/null 2>&1; then
                protected_pids="$protected_pids $pid"
                local proc_cmd=$(ps -p $pid -o cmd= 2>/dev/null | cut -c1-80 || echo "unknown")
                echo -e "${RED}   🛡️ 보호됨 - PID $pid: $proc_cmd${NC}"
            else
                local proc_cmd=$(ps -p $pid -o cmd= 2>/dev/null | cut -c1-80 || echo "unknown")
                echo -e "${YELLOW}   ✂️ 중지예정 - PID $pid: $proc_cmd${NC}"
                gaia_pids="$gaia_pids $pid"
            fi
        fi
    done
    
    # 보호된 프로세스가 있는 경우 경고
    if [ ! -z "$protected_pids" ]; then
        echo ""
        echo -e "${CYAN}🛡️ 다음 GAIA-BT 프로세스는 안전상 중지하지 않습니다:${NC}"
        for pid in $protected_pids; do
            local proc_cmd=$(ps -p $pid -o cmd= 2>/dev/null | cut -c1-120 || echo "unknown")
            echo -e "${CYAN}   🔒 PID $pid: $proc_cmd${NC}"
        done
        echo ""
    fi
    
    if [ ! -z "$gaia_pids" ]; then
        echo -e "${YELLOW}🔪 안전한 GAIA-BT 프로세스 정상 종료 중... (PID: $gaia_pids)${NC}"
        for pid in $gaia_pids; do
            # 마지막 순간 보호 검사
            if ! is_protected_process $pid >/dev/null 2>&1; then
                kill -TERM $pid 2>/dev/null || true
            else
                echo -e "${RED}  🚫 마지막 순간 보호 - PID $pid 건너뜀${NC}"
            fi
        done
        
        sleep 3
        
        # 여전히 실행 중인 안전한 프로세스만 강제 종료
        local remaining_pids=""
        for pid in $gaia_pids; do
            if kill -0 $pid 2>/dev/null && ! is_protected_process $pid >/dev/null 2>&1; then
                remaining_pids="$remaining_pids $pid"
            fi
        done
        
        if [ ! -z "$remaining_pids" ]; then
            echo -e "${RED}💥 남은 안전한 GAIA-BT 프로세스 강제 종료 중... (PID: $remaining_pids)${NC}"
            for pid in $remaining_pids; do
                # 최종 안전 검사
                if ! is_protected_process $pid >/dev/null 2>&1; then
                    kill -KILL $pid 2>/dev/null || true
                fi
            done
            sleep 1
        fi
    else
        echo -e "${GREEN}✅ 중지할 GAIA-BT 프로세스가 없습니다${NC}"
    fi
    
    # Docker 컨테이너 정리 (더 안전하게)
    if command -v docker >/dev/null 2>&1; then
        local attu_container=$(docker ps -q --filter "name=gaia-attu" 2>/dev/null)
        if [ ! -z "$attu_container" ]; then
            echo -e "${YELLOW}🐳 GAIA-BT Attu 컨테이너 안전 중지 중...${NC}"
            docker stop gaia-attu >/dev/null 2>&1
            docker rm gaia-attu >/dev/null 2>&1
        fi
    fi
    
    # 포트별 안전한 정리 (보호 프로세스 최우선 확인)
    echo -e "${YELLOW}🔧 포트별 안전한 정리 시작...${NC}"
    check_port_safely 3003 "Next.js WebUI"
    check_port_safely 8000 "FastAPI Backend"  
    check_port_safely 8080 "Attu WebUI"
    
    echo ""
    echo -e "${GREEN}✅ 모든 GAIA-BT 서버 안전 중지 완료 (보호 프로세스 유지)${NC}"
    
    # 최종 보호 상태 확인
    echo -e "${CYAN}🔍 중지 후 상태 확인:${NC}"
    check_connection_status "중지 후"
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
    
    # 시작 확인 및 health check 대기
    sleep 3
    if kill -0 $api_pid 2>/dev/null; then
        echo -e "${GREEN}✅ FastAPI 서버 시작 완료 (PID: $api_pid)${NC}"
        echo -e "${CYAN}📖 API 문서: http://localhost:8000/docs${NC}"
        
        # Health check 대기 - 실제 API 준비 완료까지 대기
        echo -e "${YELLOW}⏳ API 서버 완전 준비 대기 중...${NC}"
        for i in {1..20}; do
            if curl -s -f http://localhost:8000/health >/dev/null 2>&1; then
                echo -e "${GREEN}✅ API 서버 완전 준비 완료 ($i초)${NC}"
                return 0
            fi
            echo -ne "${YELLOW}⏳ API 준비 대기... ($i/20)\r${NC}"
            sleep 1
        done
        
        echo -e "${YELLOW}⚠️ API health check 타임아웃 - 서버는 시작되었지만 완전 준비되지 않을 수 있음${NC}"
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

# Attu 웹 UI 서버 시작 (Milvus 관리 인터페이스)
start_attu_server() {
    echo -e "${BLUE}🎨 Attu Milvus 관리 UI 시작 중...${NC}"
    
    # Docker 확인
    if ! command -v docker >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker가 설치되지 않았습니다${NC}"
        return 1
    fi
    
    # 포트 정리
    kill_port_processes 8080 "Attu WebUI"
    
    # 기존 Attu 컨테이너 확인 및 정리
    local existing_container=$(docker ps -aq --filter "name=gaia-attu" 2>/dev/null)
    if [ ! -z "$existing_container" ]; then
        echo -e "${YELLOW}🔄 기존 Attu 컨테이너 정리 중...${NC}"
        docker stop gaia-attu >/dev/null 2>&1
        docker rm gaia-attu >/dev/null 2>&1
    fi
    
    # 포트 사용 가능 대기
    if ! wait_for_port_free 8080; then
        echo -e "${RED}❌ 포트 8080이 계속 사용 중입니다${NC}"
        return 1
    fi
    
    # Milvus 서버 연결 확인
    echo -e "${YELLOW}🔍 Milvus 서버 연결 확인 중...${NC}"
    local milvus_health=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9091/api/v1/health 2>/dev/null)
    if [ "$milvus_health" != "200" ]; then
        echo -e "${YELLOW}⚠️ Milvus 서버가 실행되지 않았거나 응답하지 않습니다${NC}"
        echo -e "${YELLOW}💡 Attu는 실행되지만 Milvus에 연결할 수 없을 수 있습니다${NC}"
    fi
    
    # Docker 네트워크 확인 (host 모드로 실행)
    echo -e "${CYAN}🔗 Attu 서버 시작: http://localhost:8080${NC}"
    docker run -d \
        --name gaia-attu \
        --network host \
        -e MILVUS_URL=localhost:19530 \
        -e ATTU_LOG_LEVEL=info \
        --restart unless-stopped \
        zilliz/attu:v2.4.8 > "$ATTU_LOG" 2>&1
    
    local attu_exit_code=$?
    
    # 시작 확인
    if [ $attu_exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ Attu 웹 UI 시작 완료${NC}"
        echo -e "${CYAN}🎨 Milvus 관리 인터페이스: http://localhost:8080${NC}"
        
        # 준비 상태 확인 (최대 30초 대기)
        echo -e "${YELLOW}⏳ Attu 웹 UI 준비 대기 중...${NC}"
        for i in {1..30}; do
            if curl -s -f http://localhost:8080 >/dev/null 2>&1; then
                echo -e "${GREEN}✅ Attu 웹 UI 준비 완료 ($i초)${NC}"
                return 0
            fi
            echo -ne "${YELLOW}⏳ Attu 준비 대기... ($i/30)\r${NC}"
            sleep 1
        done
        
        echo -e "${YELLOW}⚠️ Attu 응답 대기 시간 초과 - 컨테이너는 시작되었지만 완전 준비되지 않을 수 있음${NC}"
        return 0
    else
        echo -e "${RED}❌ Attu 웹 UI 시작 실패${NC}"
        echo -e "${YELLOW}📄 로그 확인: tail -f $ATTU_LOG${NC}"
        return 1
    fi
}

# 벡터 데이터베이스 상태 확인
check_vector_database() {
    echo -e "${PURPLE}🗃️ 벡터 데이터베이스 상태 확인${NC}"
    
    # Milvus Lite 데이터베이스 파일 확인
    local milvus_db_file="/home/gaia-bt/workspace/GAIA_LLMs/milvus_lite.db"
    if [ -f "$milvus_db_file" ]; then
        local db_size=$(du -h "$milvus_db_file" | cut -f1)
        echo -e "   📊 Milvus Lite DB: 존재 (크기: $db_size)"
    else
        echo -e "   📊 Milvus Lite DB: 없음 (초기화 필요)"
    fi
    
    # 피드백 데이터베이스 파일 확인
    local feedback_db_file="/home/gaia-bt/workspace/GAIA_LLMs/feedback_milvus.db"
    if [ -f "$feedback_db_file" ]; then
        local feedback_db_size=$(du -h "$feedback_db_file" | cut -f1)
        echo -e "   💬 피드백 DB: 존재 (크기: $feedback_db_size)"
    else
        echo -e "   💬 피드백 DB: 없음 (초기화 필요)"
    fi
    
    # RAG API 엔드포인트 확인
    if command -v curl >/dev/null 2>&1; then
        local rag_stats_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/rag/stats 2>/dev/null)
        if [ "$rag_stats_status" = "200" ]; then
            echo -e "   🔍 RAG API: 정상 동작"
            
            # RAG 통계 정보 가져오기
            local rag_stats=$(curl -s http://localhost:8000/api/rag/stats 2>/dev/null)
            if [ ! -z "$rag_stats" ]; then
                echo -e "   📈 RAG 통계: $rag_stats"
            fi
        else
            echo -e "   🔍 RAG API: 확인 필요 ($rag_stats_status)"
        fi
        
        # 피드백 API 엔드포인트 확인
        local feedback_stats_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/feedback/stats 2>/dev/null)
        if [ "$feedback_stats_status" = "200" ]; then
            echo -e "   💭 피드백 API: 정상 동작"
        else
            echo -e "   💭 피드백 API: 확인 필요 ($feedback_stats_status)"
        fi
    fi
    
    # Milvus 서버 상태 확인
    echo ""
    echo -e "${PURPLE}🗄️ Milvus 서버 상태 확인${NC}"
    
    # Docker 컨테이너 확인
    if command -v docker >/dev/null 2>&1; then
        local milvus_container=$(docker ps --filter "name=milvus-standalone" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null | grep milvus-standalone || echo "")
        if [ ! -z "$milvus_container" ]; then
            echo -e "   🐳 Milvus 컨테이너: 실행 중"
            
            # Milvus API 확인
            local milvus_health=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9091/api/v1/health 2>/dev/null)
            if [ "$milvus_health" = "200" ]; then
                echo -e "   ✅ Milvus API: 정상 동작 (포트 9091)"
            else
                echo -e "   ❌ Milvus API: 확인 필요 ($milvus_health)"
            fi
        else
            echo -e "   ❌ Milvus 컨테이너: 중지됨"
        fi
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
        echo -e "   📖 API 문서: http://localhost:8000/docs"
        echo -e "   🔬 Swagger UI: http://localhost:8000/docs"
        
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
        echo -e "   💻 웹 인터페이스: http://localhost:3003"
        
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
    
    echo ""
    
    # Attu 웹 UI 상태
    local attu_pids=$(check_port 8080)
    if [ ! -z "$attu_pids" ]; then
        echo -e "${GREEN}✅ Attu 웹 UI: 실행 중 (PID: $attu_pids)${NC}"
        echo -e "   🎨 Milvus 관리 UI: http://localhost:8080"
        
        # Health check
        if command -v curl >/dev/null 2>&1; then
            local attu_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 2>/dev/null)
            if [ "$attu_status" = "200" ]; then
                echo -e "   💚 Status: 정상"
            else
                echo -e "   💛 Status: 확인 필요 ($attu_status)"
            fi
        fi
    else
        echo -e "${RED}❌ Attu 웹 UI: 중지됨${NC}"
    fi
    
    echo ""
    
    # 벡터 데이터베이스 상태 확인
    check_vector_database
    
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
    echo "  start-attu     - Attu Milvus 관리 UI만 시작"
    echo "  stop-api       - FastAPI 서버만 중지"
    echo "  stop-webui     - Next.js WebUI 서버만 중지"
    echo "  stop-attu      - Attu Milvus 관리 UI만 중지"
    echo ""
    echo -e "${GREEN}포트 관리:${NC}"
    echo "  kill-port 3001 - 특정 포트 사용 프로세스 종료"
    echo "  clean-ports    - 모든 관련 포트 정리"
    echo ""
    echo -e "${GREEN}보안 및 보호:${NC}"
    echo "  🔒 SSH(포트 22) 및 시스템 중요 포트 자동 보호"
    echo "  🛡️ Windsurf/VSCode/Cursor 등 IDE 연결 보호"
    echo "  🚫 원격 개발 환경 및 터널링 프로세스 보호"
    echo "  ⚠️ GAIA-BT 관련 프로세스만 선별적 재시작"
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
    echo "  🎨 Milvus 관리: $ATTU_URL"
}

# 메인 함수
main() {
    print_banner
    
    case "${1:-start}" in
        "start")
            check_connection_status "시작 전"
            stop_all_servers
            # 포트 완전 해제 확인
            sleep 2
            if start_api_server && start_webui_server && start_attu_server; then
                sleep 2
                check_server_status
                echo ""
                check_connection_status "시작 후"
            else
                echo -e "${RED}❌ 서버 시작 실패${NC}"
                check_connection_status "시작 실패 후"
                exit 1
            fi
            ;;
        "start-all")
            check_connection_status "시작 전"
            stop_all_servers
            # 포트 완전 해제 확인
            sleep 2
            if start_api_server && start_webui_server && start_attu_server; then
                sleep 2
                check_server_status
                echo ""
                check_connection_status "시작 후"
                # 브라우저 자동 실행
                open_browser $WEBUI_URL true
            else
                echo -e "${RED}❌ 서버 시작 실패${NC}"
                check_connection_status "시작 실패 후"
                exit 1
            fi
            ;;
        "stop")
            check_connection_status "중지 명령 전"
            stop_all_servers
            ;;
        "restart")
            check_connection_status "재시작 전"
            stop_all_servers
            sleep 2
            start_api_server && start_webui_server && start_attu_server
            sleep 2
            check_server_status
            echo ""
            check_connection_status "재시작 후"
            ;;
        "restart-all")
            check_connection_status "재시작 전"
            stop_all_servers
            sleep 2
            start_api_server && start_webui_server && start_attu_server
            sleep 2
            check_server_status
            echo ""
            check_connection_status "재시작 후"
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
        "start-attu")
            kill_port_processes 8080 "Attu WebUI"
            start_attu_server
            ;;
        "stop-api")
            kill_port_processes 8000 "FastAPI Backend"
            ;;
        "stop-webui")
            kill_port_processes 3003 "Next.js WebUI"
            ;;
        "stop-attu")
            kill_port_processes 8080 "Attu WebUI"
            docker stop gaia-attu >/dev/null 2>&1
            docker rm gaia-attu >/dev/null 2>&1
            ;;
        "kill-port")
            if [ -z "$2" ]; then
                echo -e "${RED}❌ 포트 번호를 지정해주세요: $0 kill-port 3001${NC}"
                exit 1
            fi
            # 보호된 포트 확인
            if is_protected_port "$2"; then
                echo -e "${RED}🚨 포트 $2는 시스템 중요 포트입니다. 안전상 정리하지 않습니다.${NC}"
                echo -e "${YELLOW}💡 보호된 포트 목록:${NC}"
                echo -e "${YELLOW}   - SSH: 22 (원격 접속)${NC}"
                echo -e "${YELLOW}   - 웹 서비스: 80, 443 (HTTP/HTTPS)${NC}"
                echo -e "${YELLOW}   - 메일: 25, 110, 143, 993, 995${NC}"
                echo -e "${YELLOW}   - 기타: 21 (FTP), 23 (Telnet), 53 (DNS)${NC}"
                echo -e "${CYAN}💡 대신 다른 포트를 사용하거나 수동으로 확인하세요.${NC}"
                exit 1
            fi
            check_port_safely "$2" "Port $2"
            ;;
        "clean-ports")
            kill_port_processes 3003 "Next.js WebUI"
            kill_port_processes 8000 "FastAPI Backend"
            kill_port_processes 8080 "Attu WebUI"
            docker stop gaia-attu >/dev/null 2>&1
            docker rm gaia-attu >/dev/null 2>&1
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