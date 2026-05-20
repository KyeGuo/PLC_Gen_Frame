"""
HTTP Server for PLC Benchmark Test Dashboard

This server provides:
1. Static file serving for the frontend dashboard
2. API endpoint to start benchmark tests with configurable parameters
3. Integration with DeerFlow for real-time agent conversation visualization
4. API endpoints for test tasks to integrate with DeerFlow frontend
"""

import os
import json
import threading
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_framework import BenchmarkTester, DummyPLCGenerator, DeerFlowPLCGenerator
from deerflow_api_generator import DeerFlowAPIGenerator
from websocket_server import run_server_in_background, update_test_status, send_task_update, send_task_result, send_summary

# Import test tasks API
from api.test_tasks import router as test_tasks_router

app = Flask(__name__, static_folder='frontend')
CORS(app, origins=["http://localhost:3000"])

# Register test tasks API
app.register_blueprint(test_tasks_router)

# Global tester instance
tester = None
test_thread = None
dashboard_server = None

# Default benchmark files and their task counts
ALL_BENCHMARKS = {
    "medium.jsonl": 70,
    "hard.jsonl": 3,
    "high-fidelity.jsonl": 21
}


@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')


@app.route('/api/benchmarks', methods=['GET'])
def get_benchmarks():
    """Get available benchmark files and their task counts."""
    return jsonify({
        "benchmarks": [
            {"name": name, "task_count": count}
            for name, count in ALL_BENCHMARKS.items()
        ],
        "total_tasks": sum(ALL_BENCHMARKS.values())
    })


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current server configuration."""
    return jsonify({
        "backend_url": "http://localhost:2026",
        "api_base_url": "http://localhost:2026/api",
        "websocket_port": 8765,
        "available_benchmarks": ALL_BENCHMARKS
    })


@app.route('/start-test', methods=['POST'])
def start_test():
    """Start a benchmark test."""
    global tester, test_thread, dashboard_server

    data = request.get_json() or {}

    # Get benchmark files to run - default is ALL benchmarks
    run_all = data.get('run_all', False)
    if run_all:
        benchmark_files = list(ALL_BENCHMARKS.keys())
    else:
        benchmark_files = data.get('benchmark', ['medium.jsonl'])

    max_tasks = data.get('max_tasks', None)  # None means run all
    generator_type = data.get('generator', 'deerflow')  # Default to deerflow
    agent_name = data.get('agent_name', None)
    enable_streaming = data.get('enable_streaming', True)

    print(f"\n{'='*60}")
    print("Starting Benchmark Test")
    print(f"{'='*60}")
    print(f"Received data: {data}")
    print(f"Benchmark files: {benchmark_files}")
    print(f"Max tasks: {'All' if max_tasks is None else max_tasks}")
    print(f"Generator: {generator_type}")
    print(f"Agent name: {agent_name}")
    print(f"Streaming enabled: {enable_streaming}")

    # Create generator
    if generator_type == 'deerflow':
        try:
            generator = DeerFlowPLCGenerator(
                output_dir='results',
                agent_name=agent_name
            )
            print("Using DeerFlow PLC Generator (embedded client)")
        except Exception as e:
            print(f"Failed to initialize DeerFlow generator: {e}")
            print("Falling back to Dummy generator")
            generator = DummyPLCGenerator(output_dir='results')
    elif generator_type == 'deerflow-api':
        try:
            generator = DeerFlowAPIGenerator(
                api_url="http://localhost:8001",
                agent_name=agent_name or "plc-coordinator"
            )
            print(f"Using DeerFlow API Generator (HTTP) with agent: {generator.agent_name}")
            print("Note: Conversation will be visible in DeerFlow frontend at localhost:3000")
        except Exception as e:
            print(f"Failed to initialize DeerFlow API generator: {e}")
            print("Falling back to Dummy generator")
            generator = DummyPLCGenerator(output_dir='results')
    else:
        generator = DummyPLCGenerator(output_dir='results')
        print("Using Dummy PLC Generator")

    # Start WebSocket server for real-time updates if not already running
    if dashboard_server is None:
        try:
            dashboard_server = run_server_in_background()
            print("WebSocket server started on ws://0.0.0.0:8765")
        except Exception as e:
            print(f"Warning: Could not start WebSocket server: {e}")

    # Create tester with websocket enabled
    tester = BenchmarkTester(
        generator=generator,
        benchmark_dir='benchmark_v2',
        result_dir='results',
        enable_websocket=True
    )

    # Run test in a separate thread
    def run_test():
        tester.run_benchmark(benchmark_files, max_tasks)

    test_thread = threading.Thread(target=run_test)
    test_thread.start()

    return jsonify({
        'status': 'started',
        'benchmark': benchmark_files,
        'max_tasks': max_tasks,
        'generator': generator_type,
        'total_available_tasks': sum(
            ALL_BENCHMARKS.get(f, 0) for f in benchmark_files
        )
    })


@app.route('/status', methods=['GET'])
def get_status():
    """Get current test status."""
    is_running = test_thread is not None and test_thread.is_alive()

    status = {
        'is_running': is_running,
        'benchmarks': ALL_BENCHMARKS
    }

    if tester and hasattr(tester, '_update_status'):
        # Try to get more detailed status from tester
        pass

    return jsonify(status)


@app.route('/stop-test', methods=['POST'])
def stop_test():
    """Stop the currently running test."""
    global test_thread
    if test_thread and test_thread.is_alive():
        # Note: Thread cannot be forcefully stopped in Python
        # The test will complete naturally
        return jsonify({
            'status': 'requested',
            'message': 'Stop requested. Test will complete naturally.'
        })
    return jsonify({
        'status': 'not_running',
        'message': 'No test is currently running'
    })


if __name__ == '__main__':
    # Create frontend directory if it doesn't exist
    os.makedirs('frontend', exist_ok=True)

    # Run the server
    print("\n" + "="*60)
    print("PLC Benchmark Test Dashboard Server")
    print("="*60)
    print("Dashboard available at: http://localhost:5000")
    print("WebSocket server for real-time updates: ws://localhost:8765")
    print("\nAvailable benchmarks:")
    for name, count in ALL_BENCHMARKS.items():
        print(f"  - {name}: {count} tasks")
    print(f"  - Total: {sum(ALL_BENCHMARKS.values())} tasks")
    print("\nAPI Endpoints:")
    print("  GET  /               - Dashboard UI")
    print("  GET  /api/benchmarks - List available benchmarks")
    print("  POST /start-test     - Start a benchmark test")
    print("  GET  /status         - Get test status")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
