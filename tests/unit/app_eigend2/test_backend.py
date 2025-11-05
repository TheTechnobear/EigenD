#!/usr/bin/env python3
"""
Unit tests for app_eigend2.backend module - Python 2→3 migration validation
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add the modules and plugins paths
sys.path.insert(0, '/Users/kodiak/projects/EigenD/tmp/modules')
sys.path.insert(0, '/Users/kodiak/projects/EigenD/tmp/plugins')

class TestBackendModule(unittest.TestCase):
    """Test the backend module imports and basic functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.backend_module = None
        
    def test_backend_import(self):
        """Test that backend module can be imported"""
        print("Testing backend import...")
        try:
            from app_eigend2 import backend
            self.backend_module = backend
            print("✅ Backend imported successfully")
        except ImportError as e:
            self.fail(f"Backend import failed: {e}")
            
    def test_backend_main_function(self):
        """Test that backend main function exists and can be called"""
        print("Testing backend main function...")
        from app_eigend2 import backend
        
        # Check main function exists
        self.assertTrue(hasattr(backend, 'main'), "Backend module should have main function")
        
        # Test calling main function directly (as eigend does)
        try:
            result = backend.main()
            self.assertIsNotNone(result, "main() should return a Backend object")
            print("✅ main() function works correctly")
        except Exception as e:
            self.fail(f"main() function failed: {e}")
            
    def test_backend_class_creation(self):
        """Test Backend class can be instantiated"""
        print("Testing Backend class creation...")
        from app_eigend2.backend import Backend, EigenOpts
        
        # Create mock opts (since we're not running in eigend context)
        mock_opts = EigenOpts()
        
        try:
            # Create backend with minimal initialization
            backend = Backend()
            backend.opts = mock_opts  # Add the missing opts attribute
            self.assertIsInstance(backend, Backend)
            print("✅ Backend class created successfully")
        except Exception as e:
            self.fail(f"Backend creation failed: {e}")
            
    def test_backend_mediator_interface(self):
        """Test that Backend implements the mediator interface"""
        print("Testing Backend mediator interface...")
        from app_eigend2.backend import Backend, EigenOpts
        
        mock_opts = EigenOpts()
        backend = Backend()
        backend.opts = mock_opts
        
        # Test key mediator methods exist
        mediator_methods = ['mediator', 'set_args']
        for method_name in mediator_methods:
            self.assertTrue(hasattr(backend, method_name), 
                          f"Backend should have {method_name} method")
            
        # Test calling mediator() - should return a C++ object
        try:
            result = backend.mediator()
            print(f"✅ mediator() works: {type(result)}")
        except Exception as e:
            self.fail(f"mediator() failed: {e}")

class TestNativeModuleLoading(unittest.TestCase):
    """Test that native modules can be loaded correctly"""
    
    def test_eigend_native_import(self):
        """Test eigend_native module import"""
        print("Testing eigend_native import...")
        try:
            import eigend_native
            # Check it has expected attributes
            expected_attrs = ['c2p', 'p2c']
            for attr in expected_attrs:
                self.assertTrue(hasattr(eigend_native, attr), 
                              f"eigend_native should have {attr}")
            print("✅ eigend_native imported successfully")
        except ImportError as e:
            self.fail(f"eigend_native import failed: {e}")
            
    def test_core_native_modules(self):
        """Test that core native modules can be imported"""
        print("Testing core native modules...")
        core_modules = [
            'piw_native',
            'picross_native', 
            'piagent_native'
        ]
        
        for module_name in core_modules:
            with self.subTest(module=module_name):
                try:
                    __import__(module_name)
                    print(f"✅ {module_name} imported successfully")
                except ImportError as e:
                    self.fail(f"{module_name} import failed: {e}")

class TestPythonVersionCompatibility(unittest.TestCase):
    """Test Python 2→3 compatibility issues"""
    
    def test_python_version(self):
        """Ensure we're running Python 3"""
        self.assertGreaterEqual(sys.version_info.major, 3, 
                               "Tests should run on Python 3")
        print(f"✅ Running on Python {sys.version}")
        
    def test_string_handling(self):
        """Test string/unicode handling works correctly"""
        # Test that string operations work correctly in Python 3
        test_string = "test string"
        self.assertIsInstance(test_string, str)
        
        # Test bytes handling
        test_bytes = b"test bytes"
        self.assertIsInstance(test_bytes, bytes)
        
        # Test encoding/decoding
        encoded = test_string.encode('utf-8')
        decoded = encoded.decode('utf-8')
        self.assertEqual(test_string, decoded)
        print("✅ String handling works correctly")
        
    def test_integer_division(self):
        """Test integer division behavior in Python 3"""
        # Python 3 uses true division by default
        result = 5 / 2
        self.assertEqual(result, 2.5)
        
        # Floor division should work the same
        result = 5 // 2
        self.assertEqual(result, 2)
        print("✅ Integer division behavior correct")

def run_tests():
    print("=" * 60)
    print("EigenD Backend Module Tests - Python 2→3 Migration")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestBackendModule,
        TestNativeModuleLoading, 
        TestPythonVersionCompatibility
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 All tests PASSED")
        return 0
    else:
        print("💥 Some tests FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())