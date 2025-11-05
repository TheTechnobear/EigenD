#!/usr/bin/env python3
"""
Unit test for app_cmdline/cheat.py - Python 2→3 range concatenation fix

Tests the specific issue where range() needed to be converted to list()
for concatenation with lists in Python 3.

Prerequisites: None (standalone test)
Expected: Cheatsheet runs without TypeError
"""

import sys
import os
import subprocess
import tempfile

def test_cheatsheet_execution():
    """Test that cheatsheet command executes without range concatenation errors"""
    print("Testing cheatsheet execution...")
    
    try:
        # Test the fixed cheatsheet command
        result = subprocess.run([
            '/Users/kodiak/projects/EigenD/tmp/bin/cheatsheet'
        ], capture_output=True, text=True, timeout=10)
        
        # Check exit code
        if result.returncode == 0:
            print("✅ Cheatsheet executed successfully")
            print(f"   Output length: {len(result.stdout)} characters")
            return True
        else:
            print(f"❌ Cheatsheet failed with exit code: {result.returncode}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Cheatsheet timed out")
        return False
    except FileNotFoundError:
        print("❌ Cheatsheet binary not found - build required")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_range_concatenation_fix():
    """Test the specific range concatenation that was fixed"""
    print("Testing range concatenation fix...")
    
    try:
        # This is the pattern that was fixed in cheat.py
        # [ord('!')] + range(ord('"'), ord('~')+1)
        result = [ord('!')] + list(range(ord('"'), ord('~')+1))
        expected_length = 1 + (ord('~') - ord('"') + 1)
        
        if len(result) == expected_length:
            print(f"✅ Range concatenation works: {len(result)} items")
            return True
        else:
            print(f"❌ Range concatenation failed: got {len(result)}, expected {expected_length}")
            return False
            
    except TypeError as e:
        print(f"❌ Range concatenation TypeError: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error in range concatenation: {e}")
        return False

def main():
    """Run all cheatsheet tests"""
    print("=" * 60)
    print("EigenD Cheatsheet Test - Python 2→3 Migration")
    print("=" * 60)
    
    tests = [
        test_range_concatenation_fix,
        test_cheatsheet_execution,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All cheatsheet tests PASSED")
        return 0
    else:
        print("💥 Some cheatsheet tests FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())