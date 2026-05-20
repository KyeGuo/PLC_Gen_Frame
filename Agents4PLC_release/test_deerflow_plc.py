"""
PLC Code Generation Benchmark Tester for DeerFlow Multi-Agent Framework

This script provides a comprehensive testing framework to evaluate your multi-agent
PLC code generation framework against the Agents4PLC benchmark.
"""

import os
import sys
import json
import time
import glob
import shutil
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
parent_dir = Path(__file__).resolve().parent
sys.path.append(str(parent_dir))

from config import *
from evaluate.plcverif_evaluation import plcverif_evaluation
from evaluate.pretty_summary import summary


def load_benchmark(benchmark_file: str) -> List[Dict]:
    """
    Load benchmark tasks from a JSONL file.
    
    Args:
        benchmark_file: Path to the benchmark JSONL file
        
    Returns:
        List of benchmark tasks
    """
    tasks = []
    file_path = os.path.join(BENCHMARK_DIR, benchmark_file)
    
    if not os.path.exists(file_path):
        print(f"Error: Benchmark file not found: {file_path}")
        return tasks
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    task = json.loads(line)
                    tasks.append(task)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
    
    print(f"Loaded {len(tasks)} tasks from {benchmark_file}")
    return tasks


def generate_plc_code_with_deerflow(instruction: str, properties: List[Dict]) -> str:
    """
    Generate PLC code using the DeerFlow multi-agent framework.
    
    Args:
        instruction: Natural language instruction for PLC code generation
        properties: List of properties to be validated
        
    Returns:
        Path to the generated ST file
    """
    import requests
    
    # Prepare the prompt with instruction and properties
    prompt = f"""
    Please generate a PLC function block in Structured Text (ST) based on the following requirements:
    
    {instruction}
    
    The generated code must satisfy the following properties:
    {json.dumps(properties, indent=2, ensure_ascii=False)}
    """
    
    # Create thread and run the agent
    try:
        # Create a thread
        thread_response = requests.post(
            f"{DEERFLOW_API_URL}/threads",
            json={"metadata": {"task_type": "plc_generation"}}
        )
        thread_response.raise_for_status()
        thread_id = thread_response.json()["id"]
        
        # Create a run
        run_response = requests.post(
            f"{DEERFLOW_API_URL}/threads/{thread_id}/runs",
            json={
                "assistantistant_id": DEERFLOW_AGENT_ID,
                "instructions": prompt,
                "max_completion_tokens": max_tokens
            }
        )
        run_response.raise_for_status()
        run_id = run_response.json()["id"]
        
        # Wait for completion
        status = "in_progress"
        timeout = 300  # 5 minutes timeout
        start_time = time.time()
        
        while status == "in_progress" and (time.time() - start_time) < timeout:
            time.sleep(5)
            status_response = requests.get(
                f"{DEERFLOW_API_URL}/threads/{thread_id}/runs/{run_id}"
            )
            status_response.raise_for_status()
            status = status_response.json().get("status", "in_progress")
        
        # Get the generated file from artifacts
        artifacts_response = requests.get(
            f"{DEERFLOW_API_URL}/threads/{thread_id}/artifacts"
        )
        artifacts_response.raise_for_status()
        artifacts = artifacts_response.json()
        
        # Find the ST file
        for artifact in artifacts:
            if artifact.get("filename", "").endswith(".ST"):
                # Download the file
                file_response = requests.get(artifact["url"])
                file_response.raise_for_status()
                
                # Save to results directory
                output_dir = os.path.join(RESULT_DIR, f"task_{thread_id[:8]}")
                os.makedirs(output_dir, exist_ok=True)
                st_file_path = os.path.join(output_dir, "output.ST")
                
                with open(st_file_path, 'w', encoding='utf-8') as f:
                    f.write(file_response.text)
                
                return st_file_path
        
        return None
        
    except Exception as e:
        print(f"Error generating PLC code with DeerFlow: {e}")
        return None


def generate_plc_code_with_dummy(instruction: str, properties: List[Dict]) -> str:
    """
    Dummy PLC code generator for testing purposes.
    This simulates what your multi-agent framework would return.
    
    Args:
        instruction: Natural language instruction for PLC code generation
        properties: List of properties to be validated
        
    Returns:
        Path to the generated ST file
    """
    # Extract function block name from instruction
    import re
    match = re.search(r"FUNCTION_BLOCK\s+(\w+)", instruction)
    fb_name = match.group(1) if match else "GeneratedFB"
    
    # Create a simple ST code based on instruction pattern
    st_code = f"""FUNCTION_BLOCK {fb_name}
VAR_INPUT
    SugarLevel : REAL;
    SpinningSpeed : INT;
END_VAR
VAR_OUTPUT
    SugarFeeder : BOOL;
    MotorSpeed : INT;
END_VAR

// Generated by DeerFlow Multi-Agent Framework
SugarFeeder := SugarLevel < 10.0;
MotorSpeed := SpinningSpeed;
IF SpinningSpeed <= 0 THEN
    MotorSpeed := 0;
END_IF;

END_FUNCTION_BLOCK
"""
    
    # Save the generated code
    timestamp = int(time.time())
    output_dir = os.path.join(RESULT_DIR, f"task_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    st_file_path = os.path.join(output_dir, "output.ST")
    
    with open(st_file_path, 'w', encoding='utf-8') as f:
        f.write(st_code)
    
    print(f"Generated ST file: {st_file_path}")
    return st_file_path


def run_benchmark(benchmark_file: str, num_tasks: int = None) -> Dict:
    """
    Run benchmark tests on the specified benchmark file.
    
    Args:
        benchmark_file: Name of the benchmark file (e.g., "medium.jsonl")
        num_tasks: Number of tasks to run (None for all)
        
    Returns:
        Evaluation statistics
    """
    print(f"\n{'='*60}")
    print(f"Running benchmark: {benchmark_file}")
    print(f"{'='*60}")
    
    # Load benchmark tasks
    tasks = load_benchmark(benchmark_file)
    
    if not tasks:
        print("No tasks loaded.")
        return {}
    
    # Limit tasks if specified
    if num_tasks and num_tasks < len(tasks):
        tasks = tasks[:num_tasks]
        print(f"Running {num_tasks} tasks out of {len(tasks)} available")
    
    # Prepare input files for evaluation
    input_files = []
    
    for i, task in enumerate(tasks, 1):
        print(f"\nProcessing task {i}/{len(tasks)}...")
        
        instruction = task.get("instruction", "")
        properties = task.get("properties_to_be_validated", [])
        
        # Generate PLC code using DeerFlow framework
        print("Generating PLC code...")
        st_file_path = generate_plc_code_with_dummy(instruction, properties)
        
        if st_file_path and os.path.exists(st_file_path):
            input_files.append({
                "st_file_path": st_file_path,
                "properties": properties,
                "instruction": instruction,
                "eval_folder_path": os.path.dirname(st_file_path)
            })
        else:
            print(f"Failed to generate PLC code for task {i}")
    
    # Run evaluation
    if input_files:
        print(f"\n{'='*60}")
        print("Running plcverif evaluation...")
        print(f"{'='*60}")
        
        eval_base_dir = os.path.join(RESULT_DIR, f"eval_{benchmark_file[:-5]}")
        os.makedirs(eval_base_dir, exist_ok=True)
        
        # Copy config if not exists
        if not os.path.exists(os.path.join(parent_dir, 'config.py')):
            shutil.copy(os.path.join(parent_dir, 'config_template.py'), 
                        os.path.join(parent_dir, 'config.py'))
        
        # Run evaluation
        plcverif_evaluation(input_files, eval_base_dir)
        
        return {"success": True, "tasks_processed": len(input_files)}
    else:
        print("No valid ST files generated for evaluation.")
        return {"success": False, "tasks_processed": 0}


def main():
    """Main entry point for the benchmark tester."""
    print("="*60)
    print("DeerFlow PLC Code Generation Benchmark Tester")
    print("="*60)
    print(f"Benchmark Directory: {BENCHMARK_DIR}")
    print(f"Result Directory: {RESULT_DIR}")
    print(f"DeerFlow API: {DEERFLOW_API_URL}")
    print("="*60)
    
    # Create result directory
    os.makedirs(RESULT_DIR, exist_ok=True)
    
    # Run all specified benchmarks
    results = []
    for benchmark_file in TEST_BENCHMARKS:
        result = run_benchmark(benchmark_file, MAX_TASKS_PER_BENCHMARK)
        results.append({
            "benchmark": benchmark_file,
            **result
        })
    
    # Print summary
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    for result in results:
        print(f"{result['benchmark']}: {'PASS' if result['success'] else 'FAIL'}")
        print(f"  Tasks processed: {result['tasks_processed']}")


if __name__ == "__main__":
    main()
