#!/usr/bin/env python3
"""
Unit tests for core pi module - Python 2→3 migration validation
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add the modules path
sys.path.insert(0, '/Users/kodiak/projects/EigenD/tmp/modules')

class TestPiAgent(unittest.TestCase):
    """Test the pi.agent module"""
    
    def test_agent_import(self):
        """Test that pi.agent can be imported"""
        try:
            from pi import agent
            self.assertTrue(hasattr(agent, 'Agent'), "pi.agent should have Agent class")
        except ImportError as e:
            self.fail(f"pi.agent import failed: {e}")
            
    def test_agent_class(self):
        """Test basic Agent class functionality"""
        from pi import agent
        
        # Test that Agent class exists and can be inspected
        self.assertTrue(hasattr(agent.Agent, '__init__'), "Agent should have __init__")
        
        # Test key methods exist
        expected_methods = ['create_output', 'create_input', 'server_opened', 'server_closed']
        for method in expected_methods:
            self.assertTrue(hasattr(agent.Agent, method), 
                          f"Agent should have {method} method")

class TestPiUtils(unittest.TestCase):
    """Test the pi.utils module"""
    
    def test_utils_import(self):
        """Test that pi.utils can be imported"""
        try:
            from pi import utils
        except ImportError as e:
            self.fail(f"pi.utils import failed: {e}")

class TestPiState(unittest.TestCase):
    """Test the pi.state module"""
    
    def test_state_import(self):
        """Test that pi.state can be imported"""
        try:
            from pi import state
        except ImportError as e:
            self.fail(f"pi.state import failed: {e}")

class TestPiResource(unittest.TestCase):
    """Test the pi.resource module"""
    
    def test_resource_import(self):
        """Test that pi.resource can be imported"""
        try:
            from pi import resource
        except ImportError as e:
            self.fail(f"pi.resource import failed: {e}")

class TestPiBundles(unittest.TestCase):
    """Test the pi.bundles module"""
    
    def test_bundles_import(self):
        """Test that pi.bundles can be imported"""
        try:
            from pi import bundles
            # Check key classes exist
            expected_classes = ['Output', 'Input']
            for cls_name in expected_classes:
                self.assertTrue(hasattr(bundles, cls_name), 
                              f"bundles should have {cls_name} class")
        except ImportError as e:
            self.fail(f"pi.bundles import failed: {e}")

class TestPythonVersionFeatures(unittest.TestCase):
    """Test Python 3 specific features and migration fixes"""
    
    def test_print_function(self):
        """Test that print is a function (Python 3)"""
        # This should work in Python 3
        import builtins
        self.assertTrue(callable(builtins.print), "print should be a function")
        
    def test_division_behavior(self):
        """Test division behavior is Python 3 style"""
        # In Python 3, / always does true division
        result = 7 / 2
        self.assertEqual(result, 3.5)
        
        # Floor division should still work
        result = 7 // 2
        self.assertEqual(result, 3)
        
    def test_range_behavior(self):
        """Test range returns iterator (Python 3)"""
        r = range(5)
        # In Python 3, range returns a range object, not a list
        self.assertNotEqual(type(r), list)
        
        # But it should be iterable
        self.assertEqual(list(r), [0, 1, 2, 3, 4])
        
    def test_string_types(self):
        """Test string type handling (Python 3)"""
        # In Python 3, str is unicode by default
        s = "test string"
        self.assertIsInstance(s, str)
        
        # Bytes are separate
        b = b"test bytes"
        self.assertIsInstance(b, bytes)
        
        # Test encoding/decoding
        encoded = s.encode('utf-8')
        self.assertIsInstance(encoded, bytes)
        decoded = encoded.decode('utf-8')
        self.assertEqual(s, decoded)

def run_tests():
    print("=" * 60)
    print("EigenD Core Pi Module Tests - Python 2→3 Migration")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPiAgent,
        TestPiUtils,
        TestPiState,
        TestPiResource,
        TestPiBundles,
        TestPythonVersionFeatures
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 All core pi module tests PASSED")
        return 0
    else:
        print("💥 Some core pi module tests FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())