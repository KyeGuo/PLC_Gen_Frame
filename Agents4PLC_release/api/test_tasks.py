"""API endpoints for PLC benchmark test tasks."""

import json
import os
import re
from flask import Blueprint, jsonify, request

router = Blueprint('test_tasks', __name__)

# 测试数据目录
BENCHMARK_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "benchmark_v2")


@router.route('/api/test-benchmarks', methods=['GET'])
def get_benchmarks():
    """Get list of available benchmark files."""
    try:
        benchmarks = []
        for filename in os.listdir(BENCHMARK_DIR):
            if filename.endswith(".jsonl"):
                file_path = os.path.join(BENCHMARK_DIR, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 使用 JSON decoder 来正确计算任务数
                decoder = json.JSONDecoder()
                count = 0
                idx = 0
                while idx < len(content):
                    remaining = content[idx:]
                    if not remaining.strip():
                        break
                    try:
                        _, end = decoder.raw_decode(remaining.strip())
                        count += 1
                        idx += end
                    except json.JSONDecodeError:
                        idx += 1
                        continue
                
                benchmarks.append({
                    "name": filename,
                    "task_count": count
                })
        
        return jsonify({"benchmarks": benchmarks})
    
    except Exception as e:
        return jsonify({"error": f"Error loading benchmarks: {str(e)}"}), 500


@router.route('/api/test-tasks', methods=['GET'])
def get_test_tasks():
    """Get list of test tasks from the benchmark."""
    try:
        benchmark = request.args.get('benchmark', 'medium.jsonl')
        limit = int(request.args.get('limit', 100))
        
        file_path = os.path.join(BENCHMARK_DIR, benchmark)
        
        if not os.path.exists(file_path):
            return jsonify({"error": f"Benchmark file '{benchmark}' not found"}), 404
        
        tasks = []
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式匹配每个 JSON 对象
        # 匹配以 { 开头，} 结尾的完整 JSON 对象
        json_pattern = r'\{[^{}]*\}'
        
        # 对于跨行的 JSON，需要更复杂的处理
        # 我们需要找到匹配的 { 和 } 对
        
        # 简单方法：使用 json.JSONDecoder 来解析
        decoder = json.JSONDecoder()
        idx = 0
        while idx < len(content):
            content = content[idx:]
            if not content.strip():
                break
            try:
                obj, end = decoder.raw_decode(content.strip())
                tasks.append({
                    "id": obj.get("id", ""),
                    "instruction": obj.get("instruction", ""),
                    "properties_to_be_validated": obj.get("properties_to_be_validated", [])
                })
                idx = end
            except json.JSONDecodeError:
                # 如果解析失败，跳过一个字符继续
                idx = 1
                continue
        
        return jsonify({"tasks": tasks[:limit], "total": len(tasks)})
    
    except Exception as e:
        return jsonify({"error": f"Error loading test tasks: {str(e)}"}), 500


@router.route('/api/test-tasks/<task_id>', methods=['GET'])
def get_test_task(task_id):
    """Get a specific test task by ID."""
    try:
        benchmark = request.args.get('benchmark', 'medium.jsonl')
        file_path = os.path.join(BENCHMARK_DIR, benchmark)
        
        if not os.path.exists(file_path):
            return jsonify({"error": f"Benchmark file '{benchmark}' not found"}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        decoder = json.JSONDecoder()
        idx = 0
        while idx < len(content):
            content = content[idx:]
            if not content.strip():
                break
            try:
                obj, end = decoder.raw_decode(content.strip())
                if obj.get("id") == task_id:
                    return jsonify({
                        "id": obj.get("id", ""),
                        "instruction": obj.get("instruction", ""),
                        "properties_to_be_validated": obj.get("properties_to_be_validated", [])
                    })
                idx = end
            except json.JSONDecodeError:
                idx = 1
                continue
        
        return jsonify({"error": f"Task '{task_id}' not found"}), 404
    
    except Exception as e:
        return jsonify({"error": f"Error loading test task: {str(e)}"}), 500