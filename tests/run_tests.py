#!/usr/bin/env python3
"""
EigenD Test Runner - Python 2→3 Migration Validation
Runs all unit and integration tests to validate the migration.
"""

import sys
import os
import argparse
import subprocess
import time
from pathlib import Path

# Ensure we're using Python 3
if sys.version_info.major < 3:
    print("Error: This test runner requires Python 3")
    sys.exit(1)

# Test discovery and execution
def discover_tests(test_dir, pattern="test_*.py"):
    """Discover test files in a directory"""
    test_files = []
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_files.append(os.path.join(root, file))
    return sorted(test_files)

def run_test_file(test_file, timeout=30):
    """Run a single test file with timeout"""
    print(f"\n{'='*60}")
    print(f"Running: {os.path.relpath(test_file)}")
    print(f"{'='*60}")
    
    try:
        # Use gtimeout if available, otherwise rely on Python timeout
        if subprocess.run(['which', 'gtimeout'], capture_output=True).returncode == 0:
            cmd = ['gtimeout', str(timeout), 'python3', test_file]
        else:
            cmd = ['python3', test_file]
            
        result = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.abspath(__file__)) + "/..",
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⏰ Test timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run EigenD migration tests")
    parser.add_argument("--filter", help="Filter tests by name pattern")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per test in seconds")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--system", action="store_true", help="Run only system tests")
    
    args = parser.parse_args()
    
    # Determine test directories
    test_dirs = []
    if args.unit or (not args.integration and not args.system):
        test_dirs.append("tests/unit")
    if args.integration or (not args.unit and not args.system):
        test_dirs.append("tests/integration") 
    if args.system or (not args.unit and not args.integration):
        test_dirs.append("tests/system")
    
    # Discover all tests
    all_tests = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)  # Go up one level to project root
    
    for test_dir in test_dirs:
        full_path = os.path.join(project_root, test_dir)
        if os.path.exists(full_path):
            tests = discover_tests(full_path)
            all_tests.extend(tests)
    
    # Apply filter if specified
    if args.filter:
        all_tests = [t for t in all_tests if args.filter in t]
    
    if not all_tests:
        print("No tests found matching criteria")
        return 1
        
    print(f"Found {len(all_tests)} test files to run")
    
    # Run tests
    passed = 0
    failed = 0
    start_time = time.time()
    
    for test_file in all_tests:
        success = run_test_file(test_file, args.timeout)
        if success:
            passed += 1
        else:
            failed += 1
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests: {len(all_tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Duration: {duration:.2f} seconds")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"💥 {failed} tests FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())