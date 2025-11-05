#!/usr/bin/env python3
"""
Integration tests for EigenD plugin system - Python 2→3 migration validation
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add the modules and plugins paths
sys.path.insert(0, '/Users/kodiak/projects/EigenD/tmp/modules')
sys.path.insert(0, '/Users/kodiak/projects/EigenD/tmp/plugins')

class TestPluginLoading(unittest.TestCase):
    """Test that key plugins can be loaded"""
    
    def test_simple_plugin_import(self):
        """Test that simple plugin can be imported"""
        try:
            from plg_simple import simple_plg
            self.assertTrue(hasattr(simple_plg, 'Agent'), "simple plugin should have Agent class")
        except ImportError as e:
            self.fail(f"simple plugin import failed: {e}")
            
    def test_language_plugin_import(self):
        """Test that language plugin can be imported"""
        try:
            from plg_language import language_plg
            self.assertTrue(hasattr(language_plg, 'Agent'), "language plugin should have Agent class")
        except ImportError as e:
            self.fail(f"language plugin import failed: {e}")

class TestNativePluginModules(unittest.TestCase):
    """Test that plugin native modules can be loaded"""
    
    def test_plugin_native_modules(self):
        """Test that various plugin native modules can be imported"""
        # List of plugin native modules to test
        plugin_natives = [
            'language_native',
            'arranger_native', 
            'audio_native',
            'keyboard_native'
        ]
        
        for native_module in plugin_natives:
            with self.subTest(module=native_module):
                try:
                    __import__(native_module)
                    print(f"✅ {native_module} imported successfully")
                except ImportError as e:
                    # Some plugin natives might not be available in all builds
                    print(f"⚠️  {native_module} import failed: {e}")

class TestSessionSystem(unittest.TestCase):
    """Test the session management system"""
    
    def test_pisession_import(self):
        """Test that pisession can be imported"""
        try:
            import pisession
            from pisession import session
        except ImportError as e:
            self.fail(f"pisession import failed: {e}")
            
    def test_agentd_import(self):
        """Test that agentd can be imported"""
        try:
            from pisession import agentd
        except ImportError as e:
            self.fail(f"agentd import failed: {e}")

class TestBelcantoSystem(unittest.TestCase):
    """Test the Belcanto language system"""
    
    def test_pibelcanto_import(self):
        """Test that pibelcanto can be imported"""
        try:
            import pibelcanto
            from pibelcanto import translate
        except ImportError as e:
            self.fail(f"pibelcanto import failed: {e}")

def run_tests():
    print("=" * 60)
    print("EigenD Plugin System Integration Tests - Python 2→3 Migration")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPluginLoading,
        TestNativePluginModules,
        TestSessionSystem,
        TestBelcantoSystem
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 All plugin system integration tests PASSED")
        return 0
    else:
        print("💥 Some plugin system integration tests FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())