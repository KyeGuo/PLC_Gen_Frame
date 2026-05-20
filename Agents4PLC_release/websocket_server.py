"""
WebSocket Server for Real-time Test Progress Streaming

This module provides a WebSocket server that broadcasts test progress
to connected clients in real-time.
"""

import asyncio
import json
import queue
import threading
from websockets.server import serve
from websockets.exceptions import ConnectionClosed
from typing import Dict, List, Any

# Store connected clients
connected_clients: List = []
test_status = {
    "is_running": False,
    "current_task": None,
    "progress": 0,
    "total_tasks": 0,
    "results": []
}

# Message queue for thread-safe communication
message_queue = queue.Queue()
_event_loop = None


async def broadcast(message: dict):
    """Broadcast a message to all connected clients."""
    global connected_clients
    if connected_clients:
        await asyncio.gather(
            *[client.send(json.dumps(message)) for client in connected_clients],
            return_exceptions=True
        )


async def process_queue():
    """Process messages from the queue."""
    global message_queue
    while True:
        try:
            message = message_queue.get_nowait()
            await broadcast(message)
        except queue.Empty:
            pass
        await asyncio.sleep(0.01)


async def handle_client(websocket):
    """Handle a new WebSocket client connection."""
    global connected_clients
    connected_clients.append(websocket)
    print(f"New client connected. Total: {len(connected_clients)}")
    
    # Send current status to new client
    await websocket.send(json.dumps({
        "type": "status",
        "data": test_status
    }))
    
    try:
        async for message in websocket:
            # Handle incoming messages from client
            try:
                data = json.loads(message)
                if data.get("type") == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                pass
    except ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)
        print(f"Client disconnected. Total: {len(connected_clients)}")


async def start_server(host: str = "0.0.0.0", port: int = 8765):
    """Start the WebSocket server."""
    global _event_loop
    _event_loop = asyncio.get_running_loop()
    
    # Start queue processor
    asyncio.create_task(process_queue())
    
    async with serve(handle_client, host, port):
        print(f"WebSocket server started on ws://{host}:{port}")
        await asyncio.Future()  # Run forever


def update_test_status(key: str, value: Any):
    """Update the test status and broadcast to clients."""
    global test_status
    test_status[key] = value
    message_queue.put({
        "type": "status",
        "data": test_status
    })


def send_task_update(task_id: str, step: str, message: str, details: dict = None):
    """Send a task update to all connected clients."""
    message_queue.put({
        "type": "task_update",
        "data": {
            "task_id": task_id,
            "step": step,
            "message": message,
            "details": details or {}
        }
    })


def send_task_result(task_result: dict):
    """Send a completed task result to all connected clients."""
    message_queue.put({
        "type": "task_result",
        "data": task_result
    })


def send_summary(summary: dict):
    """Send the final summary to all connected clients."""
    message_queue.put({
        "type": "summary",
        "data": summary
    })


def run_server_in_background():
    """Run the WebSocket server in a background thread."""
    def run():
        asyncio.run(start_server())
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    # Run the server directly for testing
    asyncio.run(start_server())
