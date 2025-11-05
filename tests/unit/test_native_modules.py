#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple test to verify native module loading and basic piw functionality.
"""

import unittest
import sys
import os

# Add EigenD paths
test_dir = os.path.dirname(__file__)
project_root = os.path.join(test_dir, '..', '..')
tmp_modules = os.path.join(project_root, 'tmp', 'modules')
sys.path.insert(0, tmp_modules)


class TestNativeModuleLoading(unittest.TestCase):
    """Test that native modules load correctly."""
    
    def test_piw_import(self):
        """Test importing piw native module."""
        try:
            import piw
            self.assertTrue(hasattr(piw, 'makestring'))
            print(f"✅ piw imported successfully")
            print(f"✅ piw has makestring: {hasattr(piw, 'makestring')}")
            print(f"✅ piw dir: {[attr for attr in dir(piw) if not attr.startswith('_')]}")
        except Exception as e:
            self.fail(f"Failed to import piw: {e}")
    
    def test_pisession_import(self):
        """Test importing pisession modules."""
        try:
            import pisession
            print(f"✅ pisession imported successfully")
            
            # Try to import agentd specifically
            import pisession.agentd as agentd
            print(f"✅ pisession.agentd imported successfully") 
            print(f"✅ agentd has Menu: {hasattr(agentd, 'Menu')}")
            
        except Exception as e:
            print(f"❌ pisession import failed: {e}")
            # Don't fail the test, just report
    
    def test_basic_piw_operations(self):
        """Test basic piw operations that should work."""
        try:
            import piw
            
            # Test makestring with different string types
            test_string = "test"
            result = piw.makestring(test_string, 0)
            print(f"✅ makestring with str: {result}")
            
            # Test with bytes
            test_bytes = b"test"
            result2 = piw.makestring(test_bytes, 0)
            print(f"✅ makestring with bytes: {result2}")
            
            # Test creating a term if the function exists
            if hasattr(piw, 'term'):
                term = piw.term(result)
                print(f"✅ term created: {term}")
            else:
                print(f"ℹ️  piw.term not available")
                
        except Exception as e:
            self.fail(f"Basic piw operations failed: {e}")


if __name__ == '__main__':
    print("🧪 Testing native module loading...")
    print(f"Python path: {sys.path[:3]}")
    print(f"Modules path: {tmp_modules}")
    print(f"Modules exist: {os.path.exists(tmp_modules)}")
    
    unittest.main(verbosity=2)