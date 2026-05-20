"""
DeerFlow API Generator - 通过 HTTP API 调用 DeerFlow

这个模块实现了通过 HTTP API 与 DeerFlow 通信的 PLC 生成器，
可以在 DeerFlow 前端（localhost:3000）看到完整的对话过程。
"""

import json
import requests
import sseclient
import uuid
from pathlib import Path
from typing import Optional, Generator, Dict, Any, List

class DeerFlowAPIGenerator:
    """
    通过 HTTP API 调用 DeerFlow 的 PLC 生成器。
    
    使用这个生成器时，对话将在 DeerFlow 前端（localhost:3000）实时显示，
    同时返回生成的 PLC 代码用于测试。
    
    兼容 PLCGenerator 接口，支持测试框架调用。
    """

    def __init__(
        self,
        api_url: str = "http://localhost:8001",
        agent_name: str = "plc-coordinator",
        output_dir: str = "results"
    ):
        """
        初始化生成器。
        
        Args:
            api_url: DeerFlow 后端 API 地址
            agent_name: 使用的 Agent 名称（默认 plc-coordinator）
            output_dir: 输出目录（用于兼容 PLCGenerator 接口）
        """
        self.api_url = api_url.rstrip("/")
        self.agent_name = agent_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        instruction: str,
        properties: List[Dict],
        task_id: Optional[str] = None,
        on_event: Optional[callable] = None
    ) -> str:
        """
        通过 DeerFlow API 生成 PLC 代码。
        
        Args:
            instruction: PLC 功能描述指令
            properties: 需要验证的属性列表
            task_id: 任务 ID（可选）
            on_event: 事件回调函数，用于实时更新
        
        Returns:
            生成的 ST 文件路径
        """
        # 生成唯一的任务 ID
        if task_id is None:
            task_id = str(uuid.uuid4())[:8]
        
        # 创建线程
        thread_id = self._create_thread()
        
        if on_event:
            on_event({
                "type": "status",
                "task_id": task_id,
                "step": "start",
                "message": f"Created thread: {thread_id}",
                "details": {"thread_id": thread_id}
            })
        
        # 构建完整的提示
        properties_str = json.dumps(properties, indent=2, ensure_ascii=False)
        prompt = f"""
        Please generate a PLC function block in Structured Text (ST) based on the following requirements:
        
        {instruction}
        
        The generated code must satisfy the following formal properties:
        {properties_str}
        
        Please output only the ST code without any additional explanations.
        """.strip()
        
        try:
            # 发送消息并获取流式响应
            responses = self._send_message_stream(thread_id, prompt, task_id, on_event)
            
            # 提取最终的 PLC 代码
            plc_code = self._extract_plc_code(responses, task_id, on_event)
            
            # 保存到文件
            task_dir = self.output_dir / f"task_{task_id}"
            task_dir.mkdir(exist_ok=True)
            st_file_path = task_dir / "output.ST"
            
            with open(st_file_path, 'w', encoding='utf-8') as f:
                f.write(plc_code)
            
            return str(st_file_path)
            
        finally:
            # 可选：清理线程
            pass

    def _create_thread(self) -> str:
        """创建一个新的线程。"""
        try:
            response = requests.post(
                f"{self.api_url}/api/threads",
                json={},
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("thread_id", str(uuid.uuid4())[:8])
        except Exception as e:
            print(f"Failed to create thread: {e}")
        
        # 如果创建失败，生成一个临时 ID
        return str(uuid.uuid4())[:8]

    def _send_message_stream(
        self,
        thread_id: str,
        prompt: str,
        task_id: str,
        on_event: Optional[callable] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        发送消息并获取流式响应。
        
        Yields:
            每个 SSE 事件的数据
        """
        url = f"{self.api_url}/api/threads/{thread_id}/runs/stream"
        
        # 构建正确的请求格式
        payload = {
            "assistant_id": self.agent_name,
            "input": {
                "messages": [
                    {
                        "type": "human",
                        "content": prompt
                    }
                ]
            },
            "config": {
                "configurable": {
                    "thread_id": thread_id,
                    "subagent_enabled": True,
                    "max_concurrent_subagents": 3
                }
            },
            "metadata": {
                "task_id": task_id,
                "agent_name": self.agent_name
            },
            "stream_mode": ["values", "messages"]
        }
        
        if on_event:
            on_event({
                "type": "status",
                "task_id": task_id,
                "step": "generating",
                "message": f"Sending request to DeerFlow agent: {self.agent_name}",
                "details": {"thread_id": thread_id}
            })
        
        print(f"DEBUG: Sending request to {url}")
        print(f"DEBUG: Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                url,
                json=payload,
                stream=True,
                headers={"Accept": "text/event-stream"},
                timeout=300
            )
            response.raise_for_status()
            
            print(f"DEBUG: Response status: {response.status_code}")
            
            client = sseclient.SSEClient(response)
            
            for event in client.events():
                if event.event == "error":
                    if on_event:
                        on_event({
                            "type": "status",
                            "task_id": task_id,
                            "step": "error",
                            "message": f"Error: {event.data}"
                        })
                    break
                
                try:
                    data = json.loads(event.data)
                    yield data
                    
                    # 解析事件并触发回调
                    if on_event:
                        self._parse_and_notify(data, task_id, on_event)
                        
                except json.JSONDecodeError as e:
                    print(f"DEBUG: JSON decode error: {e}")
                    continue
                    
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Request failed: {e}")
            if on_event:
                on_event({
                    "type": "status",
                    "task_id": task_id,
                    "step": "error",
                    "message": f"Request failed: {str(e)}"
                })
            raise

    def _parse_and_notify(
        self,
        data: Dict[str, Any],
        task_id: str,
        on_event: callable
    ) -> None:
        """
        解析 SSE 事件数据并触发通知。
        """
        event_type = data.get("type")
        
        if event_type == "values":
            # 状态快照
            values = data.get("data", {}).get("values", {})
            messages = values.get("messages", [])
            
            if messages:
                last_msg = messages[-1]
                msg_type = last_msg.get("type", "")
                
                if msg_type == "ai":
                    content = last_msg.get("content", "")
                    tool_calls = last_msg.get("tool_calls", [])
                    
                    if tool_calls:
                        for tc in tool_calls:
                            on_event({
                                "type": "status",
                                "task_id": task_id,
                                "step": "generating",
                                "message": f"Tool Call: {tc.get('name', '')}",
                                "details": {
                                    "tool_name": tc.get("name"),
                                    "tool_args": tc.get("args", {})
                                }
                            })
                    elif content:
                        on_event({
                            "type": "status",
                            "task_id": task_id,
                            "step": "generating",
                            "message": f"AI Response: {content[:200]}..."
                        })
                
                elif msg_type == "tool":
                    content = last_msg.get("content", "")
                    on_event({
                        "type": "status",
                        "task_id": task_id,
                        "step": "generating",
                        "message": f"Tool Result: {str(content)[:200]}..."
                    })
        
        elif event_type == "end":
            on_event({
                "type": "status",
                "task_id": task_id,
                "step": "generated",
                "message": "Generation completed"
            })

    def _extract_plc_code(
        self,
        responses: Generator[Dict[str, Any], None, None],
        task_id: str,
        on_event: Optional[callable] = None
    ) -> str:
        """
        从响应中提取 PLC 代码。
        
        Args:
            responses: 响应生成器
            task_id: 任务 ID
            on_event: 事件回调
        
        Returns:
            提取的 PLC 代码
        """
        all_messages = []
        
        for data in responses:
            # 响应可能是列表形式
            if isinstance(data, list):
                # 如果是列表，遍历每个元素
                for item in data:
                    self._process_response_item(item, all_messages)
            else:
                self._process_response_item(data, all_messages)
        
        # 从消息中提取 PLC 代码
        plc_code = ""
        for msg in reversed(all_messages):
            content = msg.get("content", "")
            
            # 查找 PLC 代码块
            if "```st" in content or "```ST" in content or "```plc" in content:
                # 提取代码块
                start = content.find("```")
                end = content.find("```", start + 3)
                
                if start != -1 and end != -1:
                    plc_code = content[start + 3:end].strip()
                    # 移除语言标识符
                    plc_code = plc_code.replace("st", "", 1).replace("ST", "", 1).replace("plc", "", 1).strip()
                    break
            elif "FUNCTION_BLOCK" in content or "PROGRAM" in content:
                # 如果没有代码块标记，尝试直接提取
                plc_code = content.strip()
                break
        
        if not plc_code and all_messages:
            # 如果没有找到代码块，返回最后一条消息的内容
            last_msg = all_messages[-1]
            plc_code = last_msg.get("content", "")
        
        if not plc_code:
            # 如果还是没有代码，生成一个简单的占位符
            plc_code = "FUNCTION_BLOCK GeneratedPLC\nEND_FUNCTION_BLOCK"
        
        if on_event:
            on_event({
                "type": "status",
                "task_id": task_id,
                "step": "generated",
                "message": f"PLC code extracted (length: {len(plc_code)})",
                "details": {"code_preview": plc_code[:500]}
            })
        
        return plc_code
    
    def _process_response_item(self, data: Dict[str, Any], all_messages: list):
        """处理单个响应项"""
        if data is None:
            return
        
        if not isinstance(data, dict):
            return
            
        if data.get("type") == "values":
            values = data.get("data", {}).get("values", {})
            messages = values.get("messages", [])
            all_messages.extend(messages)
        elif data.get("type") == "message":
            # 直接消息类型
            all_messages.append(data)


# 测试示例
if __name__ == "__main__":
    generator = DeerFlowAPIGenerator()
    
    def handle_event(event):
        print(f"[{event['task_id']}] {event['step']}: {event['message']}")
    
    test_prompt = """
    请为一个简单的电机控制系统生成 PLC 代码。
    需求：
    - 输入：启动按钮 (Start), 停止按钮 (Stop)
    - 输出：电机运行指示灯 (MotorRun)
    - 逻辑：按下启动按钮电机运行，按下停止按钮电机停止
    """
    
    try:
        code = generator.generate(test_prompt, [], "test-001", handle_event)
        print("\nGenerated PLC Code:")
        print("=" * 50)
        with open(code, 'r') as f:
            print(f.read())
    except Exception as e:
        print(f"Error: {e}")