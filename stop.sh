#!/bin/bash
# PLC 代码生成框架停止脚本

echo "======================================="
echo "  停止 PLC 代码生成框架服务"
echo "======================================="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 停止 LangGraph 服务
if [ -f "$SCRIPT_DIR/langgraph.pid" ]; then
    LANGGRAPH_PID=$(cat "$SCRIPT_DIR/langgraph.pid" 2>/dev/null)
    if [ -n "$LANGGRAPH_PID" ]; then
        echo "停止 LangGraph 服务 (PID: $LANGGRAPH_PID)..."
        kill $LANGGRAPH_PID 2>/dev/null || true
    fi
    rm -f "$SCRIPT_DIR/langgraph.pid"
fi

# 停止网关服务
if [ -f "$SCRIPT_DIR/gateway.pid" ]; then
    GATEWAY_PID=$(cat "$SCRIPT_DIR/gateway.pid" 2>/dev/null)
    if [ -n "$GATEWAY_PID" ]; then
        echo "停止网关服务 (PID: $GATEWAY_PID)..."
        kill $GATEWAY_PID 2>/dev/null || true
    fi
    rm -f "$SCRIPT_DIR/gateway.pid"
fi

# 停止前端
if [ -f "$SCRIPT_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$SCRIPT_DIR/frontend.pid" 2>/dev/null)
    if [ -n "$FRONTEND_PID" ]; then
        echo "停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    rm -f "$SCRIPT_DIR/frontend.pid"
fi

# 清理其他可能的进程
pkill -f "make dev" 2>/dev/null || true
pkill -f "make gateway" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true

echo ""
echo "服务已停止"
