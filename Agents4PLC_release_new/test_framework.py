"""
PLC Code Generation Benchmark Testing Framework

This module provides a complete testing infrastructure to evaluate
multi-agent PLC code generation frameworks against the Agents4PLC benchmark.
"""

import os
import sys
import json
import time
import uuid
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field

# Add parent directory to path
parent_dir = Path(__file__).resolve().parent
sys.path.append(str(parent_dir))


@dataclass
class BenchmarkTask:
    """Represents a single benchmark task."""
    task_id: str
    instruction: str
    properties: List[Dict]
    difficulty: str = "medium"
    
    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "task_id": self.task_id,
            "instruction": self.instruction,
            "properties_to_be_validated": self.properties,
            "difficulty": self.difficulty
        }


@dataclass
class TestResult:
    """Represents the result of a single test."""
    task_id: str
    success: bool
    st_file_path: Optional[str] = None
    compilation_success: Optional[bool] = None
    verification_results: Optional[Dict] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "task_id": self.task_id,
            "success": self.success,
            "st_file_path": self.st_file_path,
            "compilation_success": self.compilation_success,
            "verification_results": self.verification_results,
            "error_message": self.error_message,
            "execution_time": self.execution_time
        }


@dataclass
class BenchmarkSummary:
    """Summary results for a benchmark run."""
    benchmark_name: str
    total_tasks: int
    completed_tasks: int
    success_rate: float
    compilation_success_rate: float
    verification_success_rate: float
    avg_execution_time: float
    results: List[TestResult] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "benchmark_name": self.benchmark_name,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "success_rate": self.success_rate,
            "compilation_success_rate": self.compilation_success_rate,
            "verification_success_rate": self.verification_success_rate,
            "avg_execution_time": self.avg_execution_time,
            "results": [r.to_dict() for r in self.results]
        }


class BenchmarkLoader:
    """Load and manage benchmark tasks."""
    
    def __init__(self, benchmark_dir: str = "benchmark_v2"):
        self.benchmark_dir = Path(benchmark_dir)
        self.tasks: List[BenchmarkTask] = []
    
    def _parse_json_objects(self, content: str) -> List[str]:
        """
        Parse multiple JSON objects from a string by counting brace depth.
        
        Args:
            content: The content containing multiple JSON objects
            
        Returns:
            List of individual JSON object strings
        """
        json_objects = []
        current = ''
        depth = 0
        
        for char in content:
            if char == '{':
                depth += 1
                current += char
            elif char == '}':
                depth -= 1
                current += char
                if depth == 0:
                    current = current.strip()
                    if current:
                        json_objects.append(current)
                    current = ''
            else:
                if depth > 0:
                    current += char
        
        return json_objects
    
    def load_benchmark(self, filename: str) -> List[BenchmarkTask]:
        """
        Load benchmark tasks from a JSONL file.
        
        The file contains multiple JSON objects concatenated together.
        
        Args:
            filename: Name of the benchmark file (e.g., "medium.jsonl")
            
        Returns:
            List of BenchmarkTask objects
        """
        file_path = self.benchmark_dir / filename
        
        if not file_path.exists():
            print(f"Error: Benchmark file not found: {file_path}")
            return []
        
        tasks = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse JSON objects by brace depth
        json_objects = self._parse_json_objects(content)
        
        for i, json_str in enumerate(json_objects, 1):
            try:
                data = json.loads(json_str)
                task_id = data.get("id", data.get("task_id", f"{filename[:-5]}_{i}"))
                tasks.append(BenchmarkTask(
                    task_id=task_id,
                    instruction=data.get("instruction", ""),
                    properties=data.get("properties_to_be_validated", []),
                    difficulty=data.get("difficulty", filename[:-5])
                ))
            except json.JSONDecodeError as e:
                print(f"Error parsing task {i}: {e}")
        
        print(f"Loaded {len(tasks)} tasks from {filename}")
        self.tasks.extend(tasks)
        return tasks
    
    def load_all_benchmarks(self, patterns: List[str] = None) -> List[BenchmarkTask]:
        """
        Load all benchmark files matching the given patterns.
        
        Args:
            patterns: List of file patterns to match (e.g., ["medium.jsonl", "hard.jsonl"])
            
        Returns:
            List of all loaded BenchmarkTask objects
        """
        if patterns is None:
            patterns = ["medium.jsonl", "hard.jsonl", "high-fidelity.jsonl"]
        
        all_tasks = []
        for pattern in patterns:
            tasks = self.load_benchmark(pattern)
            all_tasks.extend(tasks)
        
        return all_tasks


class PLCGenerator:
    """Base class for PLC code generators."""
    
    def generate(self, instruction: str, properties: List[Dict]) -> str:
        """
        Generate PLC code from instruction and properties.
        
        Args:
            instruction: Natural language instruction
            properties: List of properties to validate
            
        Returns:
            Path to generated ST file
        """
        raise NotImplementedError("Subclasses must implement generate()")


class DummyPLCGenerator(PLCGenerator):
    """Dummy generator for testing purposes."""
    
    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, instruction: str, properties: List[Dict]) -> str:
        """Generate PLC code using a simple template."""
        import re
        
        # Extract function block name from instruction
        match = re.search(r"FUNCTION_BLOCK\s+(\w+)", instruction)
        fb_name = match.group(1) if match else "GeneratedFB"
        
        # Extract inputs and outputs from instruction
        inputs = []
        outputs = []
        
        input_match = re.search(r"VAR_INPUT(.*?)END_VAR", instruction, re.DOTALL)
        if input_match:
            for line in input_match.group(1).strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('(*'):
                    parts = line.split(':')
                    if len(parts) >= 2:
                        var_name = parts[0].strip()
                        var_type = parts[1].split(';')[0].strip()
                        inputs.append((var_name, var_type))
        
        output_match = re.search(r"VAR_OUTPUT(.*?)END_VAR", instruction, re.DOTALL)
        if output_match:
            for line in output_match.group(1).strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('(*'):
                    parts = line.split(':')
                    if len(parts) >= 2:
                        var_name = parts[0].strip()
                        var_type = parts[1].split(';')[0].strip()
                        outputs.append((var_name, var_type))
        
        # Generate ST code
        st_code = f"FUNCTION_BLOCK {fb_name}\n"
        
        if inputs:
            st_code += "VAR_INPUT\n"
            for var_name, var_type in inputs:
                st_code += f"    {var_name} : {var_type};\n"
            st_code += "END_VAR\n"
        
        if outputs:
            st_code += "VAR_OUTPUT\n"
            for var_name, var_type in outputs:
                st_code += f"    {var_name} : {var_type};\n"
            st_code += "END_VAR\n"
        
        # Add simple logic based on properties
        st_code += "\n// Generated by DummyPLCGenerator\n"
        
        for prop in properties:
            prop_desc = prop.get("property_description", "")
            if "sugar level" in prop_desc.lower() and "below" in prop_desc.lower():
                st_code += "SugarFeeder := SugarLevel < 10.0;\n"
            elif "motor speed" in prop_desc.lower() and "positive" in prop_desc.lower():
                st_code += "MotorSpeed := SpinningSpeed;\nIF SpinningSpeed <= 0 THEN\n    MotorSpeed := 0;\nEND_IF;\n"
        
        st_code += "\nEND_FUNCTION_BLOCK\n"
        
        # Save to file
        timestamp = int(time.time())
        task_dir = self.output_dir / f"task_{timestamp}"
        task_dir.mkdir(exist_ok=True)
        st_file_path = task_dir / "output.ST"
        
        with open(st_file_path, 'w', encoding='utf-8') as f:
            f.write(st_code)
        
        return str(st_file_path)


class DeerFlowPLCGenerator(PLCGenerator):
    """PLC Generator using DeerFlow embedded client."""
    
    def __init__(self, output_dir: str = "results", agent_name: str = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.agent_name = agent_name
        self._client = None
    
    def _get_client(self):
        """Get or create the DeerFlow client."""
        if self._client is None:
            try:
                from deerflow.client import DeerFlowClient
                self._client = DeerFlowClient(
                    agent_name=self.agent_name,
                    subagent_enabled=True
                )
            except ImportError as e:
                raise RuntimeError(f"Failed to import DeerFlowClient: {e}")
        
        return self._client
    
    def generate(self, instruction: str, properties: List[Dict]) -> str:
        """Generate PLC code using DeerFlow multi-agent framework."""
        client = self._get_client()
        
        # Prepare the prompt
        prompt = f"""
        Please generate a PLC function block in Structured Text (ST) based on the following requirements:
        
        {instruction}
        
        The generated code must satisfy the following formal properties:
        {json.dumps(properties, indent=2, ensure_ascii=False)}
        
        Please output only the ST code without any additional explanations.
        """
        
        # Generate a unique thread ID
        thread_id = str(uuid.uuid4())[:8]
        
        try:
            # Call the DeerFlow client
            response = client.chat(prompt, thread_id=thread_id)
            
            # Extract ST code from response
            st_code = self._extract_st_code(response)
            
            # Save to file
            task_dir = self.output_dir / f"task_{thread_id}"
            task_dir.mkdir(exist_ok=True)
            st_file_path = task_dir / "output.ST"
            
            with open(st_file_path, 'w', encoding='utf-8') as f:
                f.write(st_code)
            
            return str(st_file_path)
            
        except Exception as e:
            print(f"Error generating PLC code: {e}")
            raise
    
    def _extract_st_code(self, response: str) -> str:
        """Extract ST code from agent response."""
        # Try to find code blocks
        import re
        
        # Look for ```st ... ``` or ```ST ... ``` blocks
        match = re.search(r"```(?:st|ST)?\s*(.*?)\s*```", response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Look for FUNCTION_BLOCK ... END_FUNCTION_BLOCK
        match = re.search(r"(FUNCTION_BLOCK.*?END_FUNCTION_BLOCK)", response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Return the whole response if no code block found
        return response.strip()


class BenchmarkTester:
    """Main benchmark testing class."""
    
    def __init__(
        self,
        generator: PLCGenerator,
        benchmark_dir: str = "benchmark_v2",
        result_dir: str = "results",
        enable_websocket: bool = False
    ):
        self.generator = generator
        self.loader = BenchmarkLoader(benchmark_dir)
        self.result_dir = Path(result_dir)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.enable_websocket = enable_websocket
        
        # Initialize websocket server if enabled
        if self.enable_websocket:
            try:
                from websocket_server import run_server_in_background, update_test_status, send_task_update, send_task_result, send_summary
                self._websocket_thread = run_server_in_background()
                self._update_status = update_test_status
                self._send_task_update = send_task_update
                self._send_task_result = send_task_result
                self._send_summary = send_summary
                print("WebSocket server started for real-time updates")
            except ImportError:
                print("Warning: websocket_server module not found, real-time updates disabled")
                self.enable_websocket = False
    
    def _log_update(self, task_id: str, step: str, message: str, details: dict = None):
        """Log update to console and optionally send via websocket."""
        print(f"[{task_id}] {step}: {message}")
        if self.enable_websocket:
            self._send_task_update(task_id, step, message, details)
    
    def run_single_task(self, task: BenchmarkTask) -> TestResult:
        """
        Run a single benchmark task.
        
        Args:
            task: The benchmark task to run
            
        Returns:
            TestResult object with the results
        """
        start_time = time.time()
        
        try:
            # Generate PLC code
            self._log_update(task.task_id, "start", f"Starting task {task.task_id}")
            self._log_update(task.task_id, "generating", "Generating PLC code...")
            
            st_file_path = self.generator.generate(task.instruction, task.properties)
            
            if not st_file_path or not os.path.exists(st_file_path):
                self._log_update(task.task_id, "error", "Failed to generate ST file")
                return TestResult(
                    task_id=task.task_id,
                    success=False,
                    error_message="Failed to generate ST file",
                    execution_time=time.time() - start_time
                )
            
            # Read generated code for logging
            with open(st_file_path, 'r', encoding='utf-8') as f:
                generated_code = f.read()
            
            self._log_update(task.task_id, "generated", f"PLC code generated successfully", {
                "file_path": st_file_path,
                "code_preview": generated_code[:200] + "..." if len(generated_code) > 200 else generated_code
            })
            
            # Validate the generated code
            self._log_update(task.task_id, "validating", "Validating generated code...")
            validation_result = self._validate_st_code(st_file_path, task.properties)
            
            execution_time = time.time() - start_time
            
            result = TestResult(
                task_id=task.task_id,
                success=validation_result.get("overall_success", False),
                st_file_path=st_file_path,
                compilation_success=validation_result.get("compilation_success"),
                verification_results=validation_result.get("verification_results"),
                execution_time=execution_time
            )
            
            status = "passed" if result.success else "failed"
            self._log_update(task.task_id, "completed", f"Task completed: {status}", {
                "compilation_success": result.compilation_success,
                "verification_results": str(result.verification_results)[:500]
            })
            
            # Send task result via websocket
            if self.enable_websocket:
                self._send_task_result(result.to_dict())
            
            return result
            
        except Exception as e:
            self._log_update(task.task_id, "error", str(e))
            return TestResult(
                task_id=task.task_id,
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    def _validate_st_code(self, st_file_path: str, properties: List[Dict]) -> Dict:
        """
        Validate generated ST code using plcverif.
        
        Args:
            st_file_path: Path to the ST file
            properties: List of properties to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            from evaluate.plcverif_evaluation import single_file_plcverif_evaluation
            
            eval_folder_path = os.path.join(self.result_dir, f"eval_{os.path.basename(st_file_path)[:-3]}")
            os.makedirs(eval_folder_path, exist_ok=True)
            
            result = single_file_plcverif_evaluation(st_file_path, eval_folder_path, properties)
            
            return {
                "overall_success": result is True,
                "compilation_success": result is not False,
                "verification_results": result
            }
            
        except ImportError:
            # If plcverif evaluation is not available, just check file exists
            return {
                "overall_success": os.path.exists(st_file_path),
                "compilation_success": True,
                "verification_results": "plcverif not available"
            }
        except Exception as e:
            return {
                "overall_success": False,
                "compilation_success": False,
                "verification_results": f"Validation error: {e}"
            }
    
    def run_benchmark(self, benchmark_files: List[str], max_tasks: int = None) -> BenchmarkSummary:
        """
        Run benchmark tests.
        
        Args:
            benchmark_files: List of benchmark filenames to run
            max_tasks: Maximum number of tasks to run (None for all)
            
        Returns:
            BenchmarkSummary with aggregated results
        """
        print(f"\n{'='*60}")
        print("Running Benchmark Tests")
        print(f"{'='*60}")
        
        # Load tasks
        all_tasks = self.loader.load_all_benchmarks(benchmark_files)
        
        if not all_tasks:
            print("No tasks loaded.")
            return BenchmarkSummary(
                benchmark_name=", ".join(benchmark_files),
                total_tasks=0,
                completed_tasks=0,
                success_rate=0.0,
                compilation_success_rate=0.0,
                verification_success_rate=0.0,
                avg_execution_time=0.0
            )
        
        # Limit tasks if specified
        total_tasks_count = len(all_tasks)
        if max_tasks and max_tasks < total_tasks_count:
            all_tasks = all_tasks[:max_tasks]
            total_tasks_count = max_tasks
            print(f"Running {max_tasks} tasks out of {len(all_tasks)} available")
        
        # Update status - test started
        if self.enable_websocket:
            self._update_status("is_running", True)
            self._update_status("total_tasks", total_tasks_count)
            self._update_status("progress", 0)
            self._update_status("results", [])
        
        # Run all tasks
        results = []
        total_time = 0.0
        compilation_success_count = 0
        verification_success_count = 0
        
        for i, task in enumerate(all_tasks, 1):
            # Update current task
            if self.enable_websocket:
                self._update_status("current_task", task.task_id)
                self._update_status("progress", int((i / total_tasks_count) * 100))
            
            print(f"\nTask {i}/{total_tasks_count}: {task.task_id}")
            print(f"Difficulty: {task.difficulty}")
            
            result = self.run_single_task(task)
            results.append(result)
            
            total_time += result.execution_time
            
            if result.compilation_success:
                compilation_success_count += 1
            if result.success:
                verification_success_count += 1
            
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"Status: {status}")
            if result.error_message:
                print(f"Error: {result.error_message}")
        
        # Calculate statistics
        total_tasks = total_tasks_count
        completed_tasks = len([r for r in results if r.st_file_path])
        success_rate = verification_success_count / total_tasks if total_tasks > 0 else 0.0
        compilation_success_rate = compilation_success_count / total_tasks if total_tasks > 0 else 0.0
        verification_success_rate = verification_success_count / compilation_success_count if compilation_success_count > 0 else 0.0
        avg_execution_time = total_time / total_tasks if total_tasks > 0 else 0.0
        
        # Save results
        self._save_results(results, benchmark_files)
        
        # Print summary
        self._print_summary(
            benchmark_files,
            total_tasks,
            completed_tasks,
            success_rate,
            compilation_success_rate,
            verification_success_rate,
            avg_execution_time
        )
        
        # Update status - test completed
        summary_data = {
            "benchmark_name": ", ".join(benchmark_files),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "success_rate": success_rate,
            "compilation_success_rate": compilation_success_rate,
            "verification_success_rate": verification_success_rate,
            "avg_execution_time": avg_execution_time
        }
        
        if self.enable_websocket:
            self._update_status("is_running", False)
            self._update_status("current_task", None)
            self._update_status("progress", 100)
            self._update_status("results", [r.to_dict() for r in results])
            self._send_summary(summary_data)
        
        return BenchmarkSummary(
            benchmark_name=", ".join(benchmark_files),
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            success_rate=success_rate,
            compilation_success_rate=compilation_success_rate,
            verification_success_rate=verification_success_rate,
            avg_execution_time=avg_execution_time,
            results=results
        )
    
    def _save_results(self, results: List[TestResult], benchmark_files: List[str]):
        """Save results to JSON file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        result_file = self.result_dir / f"benchmark_results_{timestamp}.json"
        
        summary = {
            "benchmark_files": benchmark_files,
            "timestamp": timestamp,
            "results": [r.to_dict() for r in results]
        }
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {result_file}")
    
    def _print_summary(self, benchmark_files, total_tasks, completed_tasks,
                       success_rate, compilation_success_rate,
                       verification_success_rate, avg_execution_time):
        """Print the benchmark summary."""
        print("\n" + "="*60)
        print("BENCHMARK SUMMARY")
        print("="*60)
        print(f"Benchmark files: {', '.join(benchmark_files)}")
        print(f"Total tasks: {total_tasks}")
        print(f"Completed tasks: {completed_tasks}")
        print(f"Success rate: {success_rate:.1%}")
        print(f"Compilation success rate: {compilation_success_rate:.1%}")
        print(f"Verification success rate: {verification_success_rate:.1%}")
        print(f"Average execution time: {avg_execution_time:.2f} seconds")
        print("="*60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="PLC Code Generation Benchmark Tester")
    parser.add_argument(
        "--benchmark",
        nargs='+',
        default=["medium.jsonl"],
        help="Benchmark files to run (medium.jsonl, hard.jsonl, high-fidelity.jsonl)"
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=None,
        help="Maximum number of tasks to run"
    )
    parser.add_argument(
        "--generator",
        choices=["dummy", "deerflow"],
        default="dummy",
        help="PLC generator to use"
    )
    parser.add_argument(
        "--agent-name",
        type=str,
        default=None,
        help="Name of the DeerFlow agent to use (only for deerflow generator)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Output directory for results"
    )
    parser.add_argument(
        "--websocket",
        action="store_true",
        default=False,
        help="Enable WebSocket server for real-time progress updates"
    )
    
    args = parser.parse_args()
    
    # Create generator
    if args.generator == "deerflow":
        generator = DeerFlowPLCGenerator(
            output_dir=args.output_dir,
            agent_name=args.agent_name
        )
    else:
        generator = DummyPLCGenerator(output_dir=args.output_dir)
    
    # Create tester and run
    tester = BenchmarkTester(
        generator=generator,
        benchmark_dir="benchmark_v2",
        result_dir=args.output_dir,
        enable_websocket=args.websocket
    )
    
    tester.run_benchmark(args.benchmark, args.max_tasks)


if __name__ == "__main__":
    main()
