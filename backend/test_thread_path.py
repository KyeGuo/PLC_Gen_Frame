#!/usr/bin/env python3
"""Test script to verify thread-aware path building."""

import sys
sys.path.insert(0, '/home/kye/Project/deer-flow/backend/packages/harness')

from pathlib import Path
from deerflow.tools.plc_tools import _build_thread_aware_path

# Test cases
test_cases = [
    # (input_path, thread_id, expected_contains)
    ("/mnt/user-data/workspace/FB_Test.TcPOU", "abc123", "thread_abc123"),
    ("/mnt/user-data/workspace/FB_Test.TcPOU", None, "/mnt/user-data/workspace/FB_Test.TcPOU"),
    ("/mnt/user-data/workspace/thread_existing/FB_Test.TcPOU", "abc123", "/mnt/user-data/workspace/thread_existing/FB_Test.TcPOU"),
    ("/mnt/user-data/outputs/GVL_Test.TcGVL", "def456", "thread_def456"),
]

print("Testing _build_thread_aware_path function:")
print("=" * 60)

for input_path, thread_id, expected in test_cases:
    result = _build_thread_aware_path(input_path, thread_id)
    passed = expected in result if thread_id else result == expected
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status}")
    print(f"  Input:    {input_path}")
    print(f"  Thread:   {thread_id}")
    print(f"  Output:   {result}")
    print(f"  Expected: {expected}")

print("\n" + "=" * 60)
print("Test completed!")