"""
Real-time Agent Event Client for DeerFlow

This module captures real-time events from DeerFlow agents and broadcasts them
via WebSocket for visualization in the frontend dashboard.
"""

import asyncio
import json
import queue
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Generator, Optional

import requests

try:
    from deerflow.client import DeerFlowClient, StreamEvent
    HAS_DEERFLOW_CLIENT = True
except ImportError:
    HAS_DEERFLOW_CLIENT = False
    StreamEvent = None


@dataclass
class AgentEvent:
    """Represents a single event from the agent."""
    event_type: str  # "text", "tool_call", "tool_result", "error", "status"
    task_id: str
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


class DeerFlowRealtimeClient:
    """
    A client that connects to DeerFlow and captures real-time agent events
    for visualization purposes.
    """

    def __init__(
        self,
        backend_url: str = "http://localhost:2026",
        api_base_url: str = "http://localhost:2026/api",
    ):
        self.backend_url = backend_url
        self.api_base_url = api_base_url
        self._client = None
        self._websocket = None
        self._message_queue = queue.Queue()
        self._event_loop = None
        self._thread = None

    def _ensure_client(self):
        """Initialize the DeerFlow client if not already done."""
        if self._client is None and HAS_DEERFLOW_CLIENT:
            self._client = DeerFlowClient(
                subagent_enabled=True,
                thinking_enabled=True,
            )
        return self._client

    def generate_with_events(
        self,
        prompt: str,
        task_id: str,
        thread_id: str = None,
        agent_name: str = None,
        on_event: Callable[[AgentEvent], None] = None,
    ) -> Generator[AgentEvent, None, str]:
        """
        Generate PLC code while yielding real-time events.

        Args:
            prompt: The prompt to send to the agent
            task_id: Unique task identifier for tracking
            thread_id: Optional thread ID for conversation continuity
            agent_name: Optional agent name to use
            on_event: Optional callback for each event

        Yields:
            AgentEvent objects representing the agent's thought process
        """
        client = self._ensure_client()
        if thread_id is None:
            thread_id = str(uuid.uuid4())[:8]

        # Send initial status event
        yield AgentEvent(
            event_type="status",
            task_id=task_id,
            content="Starting agent conversation...",
            metadata={"thread_id": thread_id}
        )

        try:
            # Get streaming response
            if client is not None:
                # Use DeerFlowClient's stream method
                for event in client.stream(prompt, thread_id=thread_id):
                    agent_event = self._convert_stream_event(event, task_id)
                    if agent_event:
                        if on_event:
                            on_event(agent_event)
                        yield agent_event
            else:
                # Fallback: use direct API calls
                yield from self._stream_via_api(prompt, task_id, thread_id, on_event)

        except Exception as e:
            yield AgentEvent(
                event_type="error",
                task_id=task_id,
                content=f"Error during generation: {str(e)}",
                metadata={"error_type": type(e).__name__}
            )

    def _convert_stream_event(self, event, task_id: str) -> Optional[AgentEvent]:
        """Convert DeerFlow stream event to AgentEvent."""
        if event is None:
            return None

        event_type = getattr(event, 'type', None)
        data = getattr(event, 'data', {})

        if event_type == "values":
            # Full state snapshot - could contain final result
            messages = data.get("messages", [])
            if messages:
                last_msg = messages[-1]
                return AgentEvent(
                    event_type="status",
                    task_id=task_id,
                    content="Processing response...",
                    metadata={"message_count": len(messages)}
                )

        elif event_type == "messages-tuple":
            msg_type = data.get("type", "")
            content = data.get("content", "")

            if msg_type == "ai":
                # Check for tool calls
                tool_calls = data.get("tool_calls", [])
                if tool_calls:
                    for tc in tool_calls:
                        return AgentEvent(
                            event_type="tool_call",
                            task_id=task_id,
                            content=f"Calling tool: {tc.get('name')}",
                            metadata={
                                "tool_name": tc.get("name"),
                                "tool_args": tc.get("args", {}),
                                "tool_call_id": tc.get("id")
                            }
                        )
                elif content:
                    return AgentEvent(
                        event_type="text",
                        task_id=task_id,
                        content=content[:500],  # Truncate for display
                        metadata={"full_content_length": len(content)}
                    )

            elif msg_type == "tool":
                return AgentEvent(
                    event_type="tool_result",
                    task_id=task_id,
                    content=str(content)[:500],
                    metadata={
                        "tool_name": data.get("name"),
                        "tool_call_id": data.get("tool_call_id")
                    }
                )

        elif event_type == "end":
            return AgentEvent(
                event_type="status",
                task_id=task_id,
                content="Generation completed",
                metadata={}
            )

        return None

    def _stream_via_api(
        self,
        prompt: str,
        task_id: str,
        thread_id: str,
        on_event: Callable[[AgentEvent], None] = None,
    ) -> Generator[AgentEvent, None, None]:
        """Fallback: stream events via direct API calls."""
        yield AgentEvent(
            event_type="status",
            task_id=task_id,
            content="Using API fallback method...",
            metadata={"thread_id": thread_id}
        )

        # Create thread
        try:
            response = requests.post(
                f"{self.api_base_url}/threads",
                json={},
                timeout=10
            )
            if response.status_code == 200:
                thread_data = response.json()
                thread_id = thread_data.get("thread_id", thread_id)
        except Exception:
            pass

        yield AgentEvent(
            event_type="status",
            task_id=task_id,
            content="Sending message to agent...",
            metadata={"thread_id": thread_id}
        )

        # In a real implementation, we would stream the SSE response here
        # For now, yield a placeholder
        yield AgentEvent(
            event_type="text",
            task_id=task_id,
            content=f"[Would send to agent]: {prompt[:200]}...",
            metadata={}
        )


class RealtimeDashboardServer:
    """
    Server that runs the benchmark and broadcasts real-time agent events
    to connected dashboard clients.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self._connected_clients = []
        self._message_queue = queue.Queue()
        self._running = False
        self._server_thread = None

    async def _process_queue(self):
        """Process messages from the queue and broadcast to clients."""
        import websockets
        while self._running:
            try:
                message = self._message_queue.get_nowait()
                if self._connected_clients:
                    await asyncio.gather(
                        *[client.send(json.dumps(message)) for client in self._connected_clients],
                        return_exceptions=True
                    )
            except queue.Empty:
                pass
            await asyncio.sleep(0.01)

    async def _handle_client(self, websocket):
        """Handle a new WebSocket client connection."""
        import websockets
        self._connected_clients.append(websocket)
        print(f"Dashboard client connected. Total: {len(self._connected_clients)}")

        try:
            # Send welcome message with current status
            await websocket.send(json.dumps({
                "type": "welcome",
                "data": {
                    "message": "Connected to PLC Benchmark Dashboard",
                    "server": f"ws://{self.host}:{self.port}"
                }
            }))

            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get("type") == "ping":
                        await websocket.send(json.dumps({"type": "pong"}))
                except json.JSONDecodeError:
                    pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self._connected_clients.remove(websocket)
            print(f"Dashboard client disconnected. Total: {len(self._connected_clients)}")

    async def _start_server(self):
        """Start the WebSocket server."""
        import websockets
        self._running = True

        # Start queue processor
        asyncio.create_task(self._process_queue())

        async with websockets.serve(self._handle_client, self.host, self.port):
            print(f"Realtime dashboard server started on ws://{self.host}:{self.port}")
            await asyncio.Future()

    def broadcast_event(self, event: AgentEvent):
        """Broadcast an agent event to all connected dashboard clients."""
        self._message_queue.put({
            "type": "agent_event",
            "data": {
                "event_type": event.event_type,
                "task_id": event.task_id,
                "content": event.content,
                "timestamp": event.timestamp,
                "metadata": event.metadata
            }
        })

    def broadcast_status(self, status: dict):
        """Broadcast a status update to all connected clients."""
        self._message_queue.put({
            "type": "status",
            "data": status
        })

    def broadcast_task_result(self, result: dict):
        """Broadcast a task result to all connected clients."""
        self._message_queue.put({
            "type": "task_result",
            "data": result
        })

    def broadcast_summary(self, summary: dict):
        """Broadcast a summary to all connected clients."""
        self._message_queue.put({
            "type": "summary",
            "data": summary
        })

    def start(self):
        """Start the server in a background thread."""
        def run():
            asyncio.run(self._start_server())

        self._server_thread = threading.Thread(target=run, daemon=True)
        self._server_thread.start()
        print(f"Dashboard server starting on ws://{self.host}:{self.port}")
        return self

    def stop(self):
        """Stop the server."""
        self._running = False
        if self._server_thread:
            self._server_thread.join(timeout=1)
