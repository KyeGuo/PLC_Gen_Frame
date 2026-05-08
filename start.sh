#!/bin/bash
# PLC 代码生成框架启动脚本

set -e

echo "======================================="
echo "  PLC 代码生成框架 - 启动脚本"
echo "======================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 检查虚拟环境
if [ ! -d "$SCRIPT_DIR/backend/.venv" ]; then
    echo "错误：未找到虚拟环境，请先运行安装步骤"
    echo "参考 README.md 中的安装说明"
    exit 1
fi

# 检查 PLC 工作空间
PLC_WORKSPACE="$SCRIPT_DIR/../plc-workspace"
if [ ! -d "$PLC_WORKSPACE" ]; then
    echo "创建 PLC 工作空间目录..."
    mkdir -p "$PLC_WORKSPACE"
fi

echo ""
echo "1. 启动 LangGraph 服务器 (端口 2024)..."
cd "$SCRIPT_DIR/backend"
source .venv/bin/activate

# 在后台启动 LangGraph 服务器
echo "LangGraph 服务器启动中..."
make dev > "$SCRIPT_DIR/langgraph.log" 2>&1 &
LANGGRAPH_PID=$!
echo "LangGraph 服务 PID: $LANGGRAPH_PID"
echo "LangGraph 日志: $SCRIPT_DIR/langgraph.log"

# 等待 LangGraph 启动
sleep 3

echo ""
echo "2. 启动网关服务 (端口 8001)..."
# 在后台启动网关服务
echo "网关服务启动中..."
make gateway > "$SCRIPT_DIR/gateway.log" 2>&1 &
GATEWAY_PID=$!
echo "网关服务 PID: $GATEWAY_PID"
echo "网关日志: $SCRIPT_DIR/gateway.log"

# 等待网关启动
sleep 3

echo ""
echo "3. 启动前端服务..."
cd "$SCRIPT_DIR/frontend"

# 在后台启动前端
echo "前端服务启动中..."
npm run dev > "$SCRIPT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "前端服务 PID: $FRONTEND_PID"
echo "前端日志: $SCRIPT_DIR/frontend.log"

# 保存 PID
echo "$LANGGRAPH_PID" > "$SCRIPT_DIR/langgraph.pid"
echo "$GATEWAY_PID" > "$SCRIPT_DIR/gateway.pid"
echo "$FRONTEND_PID" > "$SCRIPT_DIR/frontend.pid"

echo ""
echo "======================================="
echo "  服务启动成功！"
echo "======================================="
echo "  前端地址: http://localhost:3000"
echo "  后端 API: http://localhost:8001"
echo ""
echo "  停止服务命令:"
echo "    ./stop.sh"
echo ""
echo "  查看日志:"
echo "    tail -f langgraph.log"
echo "    tail -f gateway.log"
echo "    tail -f frontend.log"
echo "======================================="

# 捕获退出信号
trap 'echo "正在停止服务..."; kill $LANGGRAPH_PID $GATEWAY_PID $FRONTEND_PID 2>/dev/null; rm -f $SCRIPT_DIR/*.pid; exit' INT TERM

# 保持脚本运行
wait
