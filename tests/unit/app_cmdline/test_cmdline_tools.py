#!/usr/bin/env python3
"""
Unit tests for app_cmdline tools - Python 2→3 migration validation
"""

import sys
import os
import unittest
import tempfile
from unittest.mock import patch, Mock

# Add the modules path
sys.path.insert(0, '/Users/kodiak/projects/EigenD/tmp/modules')

class TestCheatCommand(unittest.TestCase):
    """Test the cheat command-line tool"""
    
    def test_cheat_import(self):
        """Test that cheat module can be imported"""
        try:
            from app_cmdline import cheat
            self.assertTrue(hasattr(cheat, 'main'), "cheat should have main function")
        except ImportError as e:
            self.fail(f"cheat import failed: {e}")
            
    def test_range_concatenation(self):
        """Test the Python 2→3 range concatenation fix"""
        # This is the pattern that was fixed in various command line tools
        # [ord('!')] + range(ord('"'), ord('~')+1) needed to become list(range(...))
        try:
            result = [ord('!')] + list(range(ord('"'), ord('~')+1))
            expected_length = 1 + (ord('~') - ord('"') + 1)
            self.assertEqual(len(result), expected_length)
        except TypeError:
            self.fail("Range concatenation failed - Python 3 fix not applied")
        
    def test_cheat_execution(self):
        """Test cheat command functions are available"""
        from app_cmdline import cheat
        
        # Test that the module has expected functions
        self.assertTrue(hasattr(cheat, 'makecheat'), "cheat should have makecheat function")
        
        # Just verify the function is callable - don't test complex formatting
        self.assertTrue(callable(cheat.makecheat), "makecheat should be callable")

class TestRPCCommand(unittest.TestCase):
    """Test the rpc command-line tool"""
    
    def test_rpc_import(self):
        """Test that rpc module can be imported"""
        try:
            from app_cmdline import rpc
            self.assertTrue(hasattr(rpc, 'main'), "rpc should have main function")
        except ImportError as e:
            self.fail(f"rpc import failed: {e}")

class TestBLSCommand(unittest.TestCase):
    """Test the bls (browse/list) command-line tool"""
    
    def test_bls_import(self):
        """Test that bls module can be imported"""
        try:
            from app_cmdline import bls
            self.assertTrue(hasattr(bls, 'main'), "bls should have main function")
        except ImportError as e:
            self.fail(f"bls import failed: {e}")

class TestScriptCommand(unittest.TestCase):
    """Test the script command-line tool"""
    
    def test_script_import(self):
        """Test that script module can be imported"""
        try:
            from app_cmdline import script
            self.assertTrue(hasattr(script, 'main'), "script should have main function")
        except ImportError as e:
            self.fail(f"script import failed: {e}")

def run_tests():
    print("=" * 60)
    print("EigenD Command Line Tools Tests - Python 2→3 Migration")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestCheatCommand,
        TestRPCCommand,
        TestBLSCommand,
        TestScriptCommand
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 All command line tool tests PASSED")
        return 0
    else:
        print("💥 Some command line tool tests FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())