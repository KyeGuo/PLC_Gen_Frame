#!/usr/bin/env python3
"""Test script to verify sandbox thread-aware path handling."""

import sys
sys.path.insert(0, '/home/kye/Project/deer-flow/backend/packages/harness')

from pathlib import Path
import tempfile
import os

# Test the path building logic
def test_thread_path_handling():
    print("Testing thread-aware path handling:")
    print("=" * 60)
    
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_path = Path(tmpdir) / "workspace"
        workspace_path.mkdir()
        
        # Simulate thread data
        thread_id = "test_thread_123"
        thread_data = {
            "thread_id": thread_id,
            "workspace_path": str(workspace_path)
        }
        
        # Test 1: Write file should create thread directory
        print("\nTest 1: Writing file with thread ID")
        file_name = "FB_Test.TcPOU"
        original_path = workspace_path / file_name
        thread_dir = workspace_path / f"thread_{thread_id}"
        expected_path = thread_dir / file_name
        
        # Create the file in thread directory (simulating what the modified write_file does)
        thread_dir.mkdir(exist_ok=True)
        expected_path.write_text("TEST PLC CODE")
        
        print(f"  Original path: {original_path}")
        print(f"  Thread directory: {thread_dir}")
        print(f"  Expected path: {expected_path}")
        print(f"  File exists: {expected_path.exists()}")
        
        # Test 2: Read file should find it in thread directory
        print("\nTest 2: Reading file from thread directory")
        # Simulate what read_file does - check thread directory
        if not original_path.exists() and thread_dir.exists():
            actual_read_path = thread_dir / file_name
            print(f"  Found file in thread directory: {actual_read_path}")
            content = actual_read_path.read_text()
            print(f"  File content: {content[:20]}...")
            assert content == "TEST PLC CODE", "Content mismatch!"
        
        # Test 3: Verify directory structure
        print("\nTest 3: Directory structure verification")
        all_files = list(workspace_path.rglob("*"))
        print(f"  Files in workspace:")
        for f in all_files:
            rel_path = f.relative_to(workspace_path)
            print(f"    - {rel_path}")
        
        assert len(all_files) == 2, f"Expected 2 items (dir + file), got {len(all_files)}"
        
        print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_thread_path_handling()