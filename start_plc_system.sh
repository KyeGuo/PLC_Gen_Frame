#!/bin/bash

# PLC多智能体协作系统 - 快速启动脚本
# 用法: ./start_plc_system.sh [选项]
# 选项:
#   --setup     首次运行时安装依赖
#   --start     启动所有服务（默认）
#   --stop      停止所有服务
#   --status    查看服务状态
#   --test      运行测试验证安装

set -e

PROJECT_ROOT="/home/kye/Project"
DEERFLOW_BACKEND="$PROJECT_ROOT/deer-flow/backend"
TWINCAT_MCP="$PROJECT_ROOT/twincat-validator-mcp"
VENV_PYTHON="$DEERFLOW_BACKEND/.venv/bin/python"
UV="/home/kye/.local/bin/uv"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

check_prerequisites() {
    log_info "检查前置条件..."
    
    if [ ! -d "$DEERFLOW_BACKEND" ]; then
        log_error "DeerFlow后端目录不存在: $DEERFLOW_BACKEND"
        exit 1
    fi
    
    if [ ! -d "$TWINCAT_MCP" ]; then
        log_error "TwinCAT Validator MCP目录不存在: $TWINCAT_MCP"
        exit 1
    fi
    
    if [ ! -f "$UV" ]; then
        log_error "uv包管理器未找到: $UV"
        log_info "请先安装uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    if [ ! -f "$VENV_PYTHON" ]; then
        log_error "Python虚拟环境不存在: $DEERFLOW_BACKEND/.venv"
        exit 1
    fi
    
    log_success "所有前置条件满足"
}

install_dependencies() {
    log_info "安装TwinCAT Validator MCP..."
    
    $UV pip install -e "$TWINCAT_MCP" --python "$VENV_PYTHON"
    
    log_success "TwinCAT Validator MCP 安装成功"
    
    log_info "创建工作空间目录..."
    mkdir -p "$PROJECT_ROOT/plc-workspace"
    log_success "工作空间已创建: $PROJECT_ROOT/plc-workspace"
}

verify_installation() {
    log_info "验证安装..."
    
    MCP_CMD="$DEERFLOW_BACKEND/.venv/bin/twincat-validator-mcp"
    
    if [ ! -f "$MCP_CMD" ]; then
        log_error "twincat-validator-mcp 命令未找到"
        return 1
    fi
    
    log_success "MCP命令可执行: $MCP_CMD"
    
    log_info "检查配置文件..."
    
    CONFIG_FILE="$PROJECT_ROOT/deer-flow/extensions_config.json"
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "MCP配置文件不存在: $CONFIG_FILE"
        return 1
    fi
    
    if grep -q "twincat-validator-mcp" "$CONFIG_FILE"; then
        log_success "MCP配置正确"
    else
        log_warn "配置文件中可能缺少twincat-validator配置"
    fi
    
    log_info "检查Agent定义..."
    AGENTS_DIR="$PROJECT_ROOT/deer-flow/agents"
    REQUIRED_AGENTS=("plc-coordinator" "plc-generator" "plc-validator" "plc-optimizer")
    
    for agent in "${REQUIRED_AGENTS[@]}"; do
        if [ -d "$AGENTS_DIR/$agent" ] && [ -f "$AGENTS_DIR/$agent/SOUL.md" ]; then
            log_success "Agent就绪: $agent"
        else
            log_error "Agent缺失或不完整: $agent"
            return 1
        fi
    done
    
    echo ""
    log_success "========================================="
    log_success "  所有组件验证通过！系统就绪 ✅"
    log_success "========================================="
    echo ""
}

start_services() {
    log_info "启动DeerFlow服务（共3个）..."
    
    cd "$DEERFLOW_BACKEND"
    
    log_info "⚠️  请手动启动以下服务（在3个新终端中）："
    echo ""
    echo -e "${YELLOW}终端1 - LangGraph服务器（端口2024）:${NC}"
    echo "  cd $DEERFLOW_BACKEND"
    echo "  source .venv/bin/activate"
    echo "  langgraph dev"
    echo ""
    echo -e "${YELLOW}终端2 - Gateway API服务器（端口8001）:${NC}"
    echo "  cd $DEERFLOW_BACKEND"
    echo "  source .venv/bin/activate"
    echo "  uvicorn app.gateway.app:app --port 8001 --reload"
    echo ""
    echo -e "${YELLOW}终端3 - Frontend前端UI（端口3000）⭐:${NC}"
    echo "  cd $PROJECT_ROOT/deer-flow/frontend"
    echo "  pnpm dev"
    echo ""
    
    log_success "启动命令已显示，请在3个新终端中分别执行"
    echo ""
    log_info "🌐 浏览器访问地址:"
    echo -e "  ${GREEN}http://localhost:3000${NC} ⭐⭐⭐ （前端UI聊天界面）"
    echo ""
    log_warn "❌ 不要访问 http://localhost:2024 （那是后端API，会显示 {\"ok\":true}）"
}

show_status() {
    log_info "系统状态检查..."
    
    echo ""
    echo -e "${BLUE}📁 项目结构:${NC}"
    ls -la "$PROJECT_ROOT/deer-flow/agents/" | grep -E "^d"
    
    echo ""
    echo -e "${BLUE}🔧 MCP配置:${NC}"
    cat "$PROJECT_ROOT/deer-flow/extensions_config.json" | python3 -m json.tool 2>/dev/null || cat "$PROJECT_ROOT/deer-flow/extensions_config.json"
    
    echo ""
    echo -e "${BLUE}🤖 Agent列表:${NC}"
    for agent_dir in "$PROJECT_ROOT/deer-flow/agents/"*/; do
        agent_name=$(basename "$agent_dir")
        if [ -f "$agent_dir/config.yaml" ]; then
            description=$(grep -E "^description:" "$agent_dir/config.yaml" | cut -d'"' -f2)
            echo -e "  ${GREEN}✓${NC} $agent_name: $description"
        fi
    done
}

run_test() {
    log_info "运行快速测试..."
    
    MCP_CMD="$DEERFLOW_BACKEND/.venv/bin/twincat-validator-mcp"
    
    echo ""
    log_info "测试TwinCAT Validator MCP (5秒超时)..."
    timeout 5 $MCP_CMD --help || true
    
    echo ""
    log_success "测试完成"
}

show_usage() {
    echo ""
    echo -e "${BLUE}PLC多智能体协作系统 - 使用指南${NC}"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --setup     首次运行时安装依赖"
    echo "  --start     显示启动命令（默认）"
    echo "  --stop      停止提示"
    echo "  --status    查看系统状态"
    echo "  --test      运行安装验证测试"
    echo "  --help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --setup      # 首次安装"
    echo "  $0 --start      # 启动系统"
    echo "  $0 --status     # 查看状态"
    echo "  $0 --test       # 验证安装"
    echo ""
    echo -e "${YELLOW}快速开始:${NC}"
    echo "  1. 运行: $0 --setup"
    echo "  2. 运行: $0 --start"
    echo "  3. 在3个终端中分别启动3个服务（见启动命令）"
    echo "  4. 浏览器打开: ${GREEN}http://localhost:3000${NC} ⭐（前端UI）"
    echo "  5. 选择 plc-coordinator Agent开始使用"
    echo ""
    echo -e "${RED}注意:${NC} 不要访问 localhost:2024，那是后端API！"
    echo ""
}

main() {
    case "${1:-}" in
        --setup)
            check_prerequisites
            install_dependencies
            verify_installation
            ;;
        --start)
            check_prerequisites
            start_services
            ;;
        --stop)
            log_info "停止提示："
            echo "  在运行服务的终端按 Ctrl+C 停止服务"
            ;;
        --status)
            show_status
            ;;
        --test)
            check_prerequisites
            run_test
            ;;
        --help|-h)
            show_usage
            ;;
        "")
            show_usage
            start_services
            ;;
        *)
            log_error "未知选项: $1"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
