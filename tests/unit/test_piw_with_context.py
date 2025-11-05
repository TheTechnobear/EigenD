#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test piw functionality with proper TSD context setup.
This test reproduces the term_copy issue but with minimal setup.
"""

import unittest
import sys
import os

# Add EigenD paths
test_dir = os.path.dirname(__file__)
project_root = os.path.join(test_dir, '..', '..')
tmp_modules = os.path.join(project_root, 'tmp', 'modules')
sys.path.insert(0, tmp_modules)


class TestPiwWithContext(unittest.TestCase):
    """Test piw functionality with proper context setup."""
    
    @classmethod
    def setUpClass(cls):
        """Set up a proper TSD context for piw operations."""
        try:
            # Import required modules
            import piw
            import piagent
            from pi import utils
            
            # Create scaffold like session.run_session() does
            def logfunc(msg):
                print(f"LOG: {msg}")
                
            # Create scaffold with single thread, logging, no clock callbacks, no realtime
            cls.scaffold = piagent.scaffold_mt(1, utils.stringify(logfunc), 
                                             utils.stringify(None), False, False)
            
            # Create context from scaffold
            def ctxdun(status):
                pass  # Context cleanup callback
                
            cls.context = cls.scaffold.context('test', utils.statusify(ctxdun), 
                                             utils.stringify(logfunc), 'test_context')
            
            # Set environment and TSD context
            piw.setenv(cls.context.getenv())
            
            cls.piw = piw
            print("✅ TSD context set up successfully using piagent.scaffold_mt")
            
        except Exception as e:
            print(f"❌ Failed to set up TSD context: {e}")
            raise
    
    @classmethod
    def tearDownClass(cls):
        """Clean up TSD context."""
        try:
            if hasattr(cls, 'context'):
                cls.context.release()
                print("✅ TSD context released")
        except Exception as e:
            print(f"⚠️  Failed to release TSD context: {e}")
    
    def test_basic_makestring(self):
        """Test makestring with proper context."""
        # Test with simple string
        result = self.piw.makestring("test", 0)
        self.assertIsNotNone(result)
        print(f"✅ makestring('test') = {result}")
        
        # Test with problematic string
        result2 = self.piw.makestring("user 2", 0)
        self.assertIsNotNone(result2)
        print(f"✅ makestring('user 2') = {result2}")
    
    def test_term_creation(self):
        """Test creating terms from strings."""
        # Create string data
        string_data = self.piw.makestring("test term", 0)
        
        # Create term from string (if term function exists)
        if hasattr(self.piw, 'term'):
            term = self.piw.term(string_data)
            self.assertIsNotNone(term)
            print(f"✅ term created from string data")
        else:
            print("ℹ️  piw.term function not available")
    
    def test_problematic_strings(self):
        """Test the specific strings that cause issues in setup files."""
        problematic_strings = [
            "user 2",
            "pico 1 ~ pico",
            "user 1 ~ pico", 
            "",
            "with spaces",
            "test~symbol"
        ]
        
        for test_string in problematic_strings:
            with self.subTest(string=test_string):
                try:
                    # Test raw string
                    result1 = self.piw.makestring(test_string, 0)
                    self.assertIsNotNone(result1)
                    
                    # Test encoded string
                    encoded = test_string.encode('utf-8')
                    result2 = self.piw.makestring(encoded, 0)
                    self.assertIsNotNone(result2)
                    
                    print(f"✅ Both raw and encoded work for: '{test_string}'")
                    
                except Exception as e:
                    self.fail(f"Failed for string '{test_string}': {e}")


class TestAgentdWithContext(unittest.TestCase):
    """Test pisession.agentd with proper context."""
    
    @classmethod 
    def setUpClass(cls):
        """Set up context and import agentd."""
        try:
            # Import and set up context like the previous test
            import piw
            import piagent
            from pi import utils
            
            # Create scaffold like session.run_session() does
            def logfunc(msg):
                print(f"LOG: {msg}")
                
            cls.scaffold = piagent.scaffold_mt(1, utils.stringify(logfunc), 
                                             utils.stringify(None), False, False)
            
            def ctxdun(status):
                pass
                
            cls.context = cls.scaffold.context('agentd_test', utils.statusify(ctxdun), 
                                             utils.stringify(logfunc), 'agentd_test')
            
            piw.setenv(cls.context.getenv())
            
            # Now import agentd 
            import pisession.agentd as agentd
            cls.agentd = agentd
            cls.piw = piw
            
            print("✅ agentd context set up successfully")
            
        except Exception as e:
            print(f"❌ Failed to set up agentd context: {e}")
            raise
    
    @classmethod
    def tearDownClass(cls):
        """Clean up context."""
        try:
            if hasattr(cls, 'context'):
                cls.context.release()
        except:
            pass
    
    def test_menu_creation(self):
        """Test creating Menu objects."""
        menu = self.agentd.Menu("Test Menu")
        self.assertIsNotNone(menu)
        print("✅ Menu created successfully")
    
    def test_menu_term_empty(self):
        """Test creating term from empty menu."""
        menu = self.agentd.Menu("Test Menu")
        term = menu.term()
        self.assertIsNotNone(term)
        print("✅ Empty menu term created successfully")
    
    def test_menu_with_setup(self):
        """Test the specific failing case - menu with setup."""
        menu = self.agentd.Menu("Test Menu")
        
        # Add the problematic setup that causes the term_copy issue
        menu.add_setup('', 'user 2', '/test/path', False, True)
        
        try:
            # This should work now with proper context
            term = menu.term()
            self.assertIsNotNone(term)
            print("✅ Menu with setup term created successfully")
            
            # Test accessing the term structure (this is where the crash happened)
            if term.arity() > 0:
                child = term.arg(0)
                self.assertIsNotNone(child)
                print("✅ Term child access successful")
                
                # This is the operation that was crashing - term copy
                if hasattr(self.piw, 'term_t'):
                    copied_term = self.piw.term_t(child)
                    self.assertIsNotNone(copied_term)
                    print("✅ Term copy successful!")
                else:
                    print("ℹ️  piw.term_t not available")
            
        except Exception as e:
            self.fail(f"Menu with setup failed: {e}")


if __name__ == '__main__':
    print("🧪 Testing piw with proper TSD context...")
    unittest.main(verbosity=2)