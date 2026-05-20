# DeerFlow PLC Benchmark Testing Guide

This guide explains how to use the Agents4PLC benchmark to test your DeerFlow multi-agent PLC code generation framework.

## Quick Start

### 1. Clone the Benchmark Repository

```bash
cd /home/kye/Project
git clone https://github.com/Luoji-zju/Agents4PLC_release.git
cd Agents4PLC_release
```

### 2. Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

### 3. Configure the Framework

Edit `config.py` to set your configuration:

```python
# Model configuration
chat_model = "openai"
embedding_model = "text-embedding-ada-002"

# API keys (should be set via environment variables)
# api_key = "sk-your-own-key-here"

# DeerFlow configuration
DEERFLOW_API_URL = "http://localhost:8001"
DEERFLOW_AGENT_ID = "plc-coordinator"

# Benchmark paths
BENCHMARK_DIR = "/home/kye/Project/Agents4PLC_release/benchmark_v2"
RESULT_DIR = "/home/kye/Project/Agents4PLC_release/results"

# Test configuration
TEST_BENCHMARKS = ["medium.jsonl", "hard.jsonl", "high-fidelity.jsonl"]
MAX_TASKS_PER_BENCHMARK = None  # Set to None for all tasks
```

### 4. Run the Benchmark

#### Option 1: Using the Command Line Interface

```bash
# Run with dummy generator (for testing)
python test_framework.py --benchmark medium.jsonl --generator dummy --max-tasks 5

# Run with DeerFlow generator
python test_framework.py --benchmark medium.jsonl --generator deerflow --agent-name plc-coordinator

# Run all benchmarks
python test_framework.py --benchmark medium.jsonl hard.jsonl high-fidelity.jsonl --generator deerflow
```

#### Option 2: Using Python API

```python
from test_framework import BenchmarkTester, DeerFlowPLCGenerator

# Create the generator
generator = DeerFlowPLCGenerator(
    output_dir="results",
    agent_name="plc-coordinator"
)

# Create the tester
tester = BenchmarkTester(
    generator=generator,
    benchmark_dir="benchmark_v2",
    result_dir="results"
)

# Run the benchmark
summary = tester.run_benchmark(["medium.jsonl"], max_tasks=10)

# Access results
print(f"Success rate: {summary.success_rate:.1%}")
print(f"Average execution time: {summary.avg_execution_time:.2f}s")
```

## Benchmark Structure

The benchmark contains three difficulty levels:

| Benchmark | Description | Number of Tasks |
|-----------|-------------|-----------------|
| `medium.jsonl` | Medium difficulty tasks | 70 |
| `hard.jsonl` | Hard difficulty tasks | 3 |
| `high-fidelity.jsonl` | Industrial tasks for efficiency analysis | 21 |

## Task Format

Each benchmark task follows this structure:

```json
{
  "instruction": "Create a PLC function block...",
  "properties_to_be_validated": [
    {
      "property_description": "Ensure X is true...",
      "property": {
        "job_req": "pattern",
        "pattern_id": "pattern-implication",
        "pattern_params": {
          "0": "condition",
          "1": "result"
        }
      }
    }
  ]
}
```

## Evaluation Metrics

The benchmark evaluates:

1. **Compilation Success**: Does the generated code compile without errors?
2. **Verification Success**: Does the code satisfy all formal properties?
3. **Execution Time**: How long does generation and validation take?

## Integration with DeerFlow

To use your DeerFlow multi-agent framework:

1. **Start DeerFlow Services**:
   ```bash
   cd /home/kye/Project/deer-flow/backend
   source .venv/bin/activate
   langgraph dev  # Terminal 1
   uvicorn app.gateway.app:app --port 8001 --reload  # Terminal 2
   ```

2. **Ensure PLC Agent is Configured**:
   - Create a `plc-coordinator` agent
   - Configure the agent to use the PLC tools
   - Set up TwinCAT Validator MCP

3. **Run the Benchmark**:
   ```bash
   python test_framework.py --generator deerflow --agent-name plc-coordinator
   ```

## Results

Results are saved to `results/benchmark_results_<timestamp>.json` with the following structure:

```json
{
  "benchmark_files": ["medium.jsonl"],
  "timestamp": "20240101_120000",
  "results": [
    {
      "task_id": "M1",
      "success": true,
      "st_file_path": "results/task_abc123/output.ST",
      "compilation_success": true,
      "verification_results": {...},
      "execution_time": 15.32
    }
  ]
}
```

## Advanced Usage

### Custom Generator

You can create your own generator by extending the `PLCGenerator` class:

```python
from test_framework import PLCGenerator

class MyCustomGenerator(PLCGenerator):
    def generate(self, instruction: str, properties: List[Dict]) -> str:
        # Your custom generation logic here
        # ...
        return st_file_path
```

### Parallel Execution

For large-scale testing, consider running tasks in parallel:

```python
from concurrent.futures import ThreadPoolExecutor

def run_task(task):
    result = tester.run_single_task(task)
    return result

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(run_task, tasks))
```

## Troubleshooting

### Common Issues

1. **DeerFlowClient import error**:
   - Ensure DeerFlow is installed in your Python environment
   - Add DeerFlow to PYTHONPATH

2. **PLC tools not available**:
   - Ensure TwinCAT Validator MCP is installed and configured
   - Check extensions_config.json

3. **Timeout errors**:
   - Increase timeout in `test_deerflow_plc.py`
   - Check network connectivity to DeerFlow API

### Logs

Check the following for debugging:
- `results/` directory for generated ST files
- `results/benchmark_results_*.json` for test results
- DeerFlow server logs for agent execution details

## Resources

- [Agents4PLC Paper](https://arxiv.org/abs/2407.01234)
- [DeerFlow Documentation](https://github.com/your-org/deer-flow)
- [PLCverif Documentation](https://plcverif.org/)

## Citation

If you use this benchmark in your research, please cite:

```
@article{liu2024agents4plc,
  title={Agents4plc: Automating closed-loop plc code generation and verification in industrial control systems using llm-based agents},
  author={Liu, Zihan and others},
  journal={arXiv preprint arXiv:2407.01234},
  year={2024}
}
```
