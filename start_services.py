#!/usr/bin/env python3
"""
启动 DeerFlow 服务脚本
"""
import subprocess
import time
import os

def main():
    os.chdir('/home/kye/Project/deer-flow/backend')
    
    # 启动 LangGraph 服务器
    print("启动 LangGraph 服务器...")
    langgraph_proc = subprocess.Popen(
        ['uv', 'run', 'langgraph', 'dev', '--no-browser', '--no-reload', '--n-jobs-per-worker', '10'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(5)
    
    # 检查 LangGraph 是否启动成功
    if langgraph_proc.poll() is not None:
        stdout, stderr = langgraph_proc.communicate()
        print(f"LangGraph 启动失败!")
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        return
    
    print("LangGraph 服务器启动成功")
    
    # 启动网关服务
    print("启动网关服务...")
    env = os.environ.copy()
    env['PYTHONPATH'] = '.'
    gateway_proc = subprocess.Popen(
        ['uv', 'run', 'uvicorn', 'app.gateway.app:app', '--host', '0.0.0.0', '--port', '8001'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    time.sleep(3)
    
    # 检查网关是否启动成功
    if gateway_proc.poll() is not None:
        stdout, stderr = gateway_proc.communicate()
        print(f"网关启动失败!")
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        return
    
    print("网关服务启动成功")
    print("所有服务启动完成!")
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("正在停止服务...")
        langgraph_proc.terminate()
        gateway_proc.terminate()

if __name__ == "__main__":
    main()
