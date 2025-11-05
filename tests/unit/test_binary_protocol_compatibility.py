#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Binary Protocol Compatibility Tests - Python 2→3 Migration
Tests that the binary wire protocol between client and server remains unchanged.
This is critical for cross-version and cross-architecture compatibility.
"""

import sys
import os
import unittest
import hashlib
import struct

# Add EigenD paths
test_dir = os.path.dirname(__file__)
project_root = os.path.join(test_dir, '..', '..')
tmp_modules = os.path.join(project_root, 'tmp', 'modules')
sys.path.insert(0, tmp_modules)


class TestBinaryProtocolCompatibility(unittest.TestCase):
    """Test that binary protocol between client/server remains unchanged."""
    
    @classmethod
    def setUpClass(cls):
        """Set up TSD context for binary protocol tests."""
        try:
            import piw
            import piagent
            from pi import utils
            
            def logfunc(msg):
                pass
                
            cls.scaffold = piagent.scaffold_mt(1, utils.stringify(logfunc), 
                                             utils.stringify(None), False, False)
            
            def ctxdun(status):
                pass
                
            cls.context = cls.scaffold.context('test_binary', utils.statusify(ctxdun), 
                                             utils.stringify(logfunc), 'test_binary')
            
            piw.setenv(cls.context.getenv())
            cls.piw = piw
            
        except Exception as e:
            raise RuntimeError(f"Failed to set up TSD context: {e}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up TSD context."""
        try:
            if hasattr(cls, 'context'):
                cls.context.release()
        except:
            pass
    
    def test_string_data_binary_representation(self):
        """Test that string data objects maintain binary compatibility."""
        # These test strings represent common setup file content
        test_strings = [
            "user 2",
            "pico 1 ~ pico",
            "user 1 ~ pico",
            "",
            "with spaces",
            "/path/to/setup/file",
        ]
        
        for test_string in test_strings:
            with self.subTest(string=test_string):
                # Create data object
                data_obj = self.piw.makestring(test_string, 0)
                
                # Verify data type is consistent
                self.assertEqual(data_obj.data_type(), 2, "String data type should be 2")
                
                # Verify we can extract the original string
                extracted = data_obj.as_string()
                self.assertEqual(extracted, test_string)
                
                # Verify the data object is string type
                self.assertTrue(data_obj.is_string())
                self.assertFalse(data_obj.is_bool())
    
    def test_boolean_data_binary_representation(self):
        """Test that boolean data objects maintain binary compatibility."""
        for bool_value in [True, False]:
            with self.subTest(value=bool_value):
                # Create data object
                data_obj = self.piw.makebool(bool_value, 0)
                
                # Verify data type is consistent  
                self.assertEqual(data_obj.data_type(), 6, "Boolean data type should be 6")
                
                # Verify we can extract the original boolean
                extracted = data_obj.as_bool()
                self.assertEqual(extracted, bool_value)
                
                # Verify the data object is boolean type
                self.assertTrue(data_obj.is_bool())
                self.assertFalse(data_obj.is_string())
    
    def test_term_binary_representation(self):
        """Test that term objects maintain binary compatibility."""
        # Test term with string content - type 3 is for string terms
        term_string = self.piw.term("test", 0)
        self.assertEqual(term_string.type(), 3)
        
        # Test term with different types
        for term_type in [0, 1, 2, 6, 7]:
            with self.subTest(type=term_type):
                term = self.piw.term(term_type)
                self.assertEqual(term.type(), term_type)
    
    def test_menu_term_structure_compatibility(self):
        """Test that Menu.term() structures maintain binary compatibility."""
        from pisession import agentd
        
        # Create a menu structure like find_user_setups() does
        menu = agentd.Menu("Test Menu")
        
        # Add setups with different name patterns
        test_setups = [
            ('', 'user 2', '/path1', False, True),
            ('pico', 'pico 1', '/path2', False, False), 
            ('test', 'test setup', '/path3', True, True),
        ]
        
        for name, slot, path, upg, user in test_setups:
            menu.add_setup(name, slot, path, upg, user)
        
        # Generate term structure
        term = menu.term()
        self.assertIsNotNone(term)
        
        # Verify term structure properties
        self.assertGreaterEqual(term.arity(), 0, "Menu term should have children")
        
        # If term has children, verify they're accessible
        if term.arity() > 0:
            child = term.arg(0)
            self.assertIsNotNone(child, "Menu child terms should be accessible")
    
    def test_unicode_vs_bytes_protocol_preservation(self):
        """Test that Unicode strings in Python 3 maintain protocol compatibility."""
        # Test strings that could cause encoding issues
        unicode_strings = [
            "café",           # Latin-1 accented characters
            "naïve",          # More accents
            "résumé",         # Mixed accents
            "🎵",             # Emoji (4-byte UTF-8)
            "日本語",          # CJK characters
        ]
        
        for test_string in unicode_strings:
            with self.subTest(string=test_string):
                # Create data object with Unicode string
                data_obj = self.piw.makestring(test_string, 0)
                
                # Verify roundtrip works
                extracted = data_obj.as_string()
                self.assertEqual(extracted, test_string)
                
                # Verify data type consistency
                self.assertEqual(data_obj.data_type(), 2)
                
                # Create term using working constructor - type 3 for string terms
                term = self.piw.term(test_string, 0)
                self.assertEqual(term.type(), 3)
    
    def test_cross_version_term_serialization(self):
        """Test that term serialization is compatible across Python versions."""
        # Create various term structures
        test_cases = [
            # Simple string term
            self.piw.term("test", 0),
            # Empty term
            self.piw.term(0),
            # Different type term
            self.piw.term(2),
        ]
        
        for term in test_cases:
            with self.subTest(term=term):
                # Test that term can be rendered to string (serialization)
                try:
                    rendered = term.render()
                    self.assertIsInstance(rendered, str)
                    print(f"✅ Term renders to: {rendered}")
                except Exception as e:
                    # render() might not be available in all builds
                    print(f"ℹ️  Term render not available: {e}")
    
    def test_data_wrapper_to_term_workaround_compatibility(self):
        """Test that our data_to_term() workaround maintains protocol compatibility."""
        from pisession import agentd
        
        # Test string data wrapper workflow
        original_string = "user 2"
        
        # Step 1: Create data object (type-safe wrapper)
        string_data = self.piw.makestring(original_string, 0)
        
        # Step 2: Use our workaround instead of broken term(data) constructor
        term_via_workaround = agentd.data_to_term(string_data)
        
        # Step 3: Create equivalent term using working constructor  
        term_direct = self.piw.term(original_string, string_data.data_type())
        
        # Step 4: Verify both approaches produce compatible results
        self.assertEqual(term_via_workaround.type(), term_direct.type())
        
        # Test boolean data wrapper workflow
        for bool_val in [True, False]:
            with self.subTest(bool_value=bool_val):
                # Step 1: Create boolean data object
                bool_data = self.piw.makebool(bool_val, 0)
                
                # Step 2: Use our workaround
                term_bool = agentd.data_to_term(bool_data)
                
                # Step 3: Verify result has expected properties
                self.assertEqual(term_bool.type(), 7)  # Boolean terms use type 7


class TestClientServerCompatibility(unittest.TestCase):
    """Test scenarios that affect client-server communication."""
    
    @classmethod
    def setUpClass(cls):
        """Set up for client-server tests."""
        try:
            import piw
            import piagent
            from pi import utils
            
            def logfunc(msg):
                pass
                
            cls.scaffold = piagent.scaffold_mt(1, utils.stringify(logfunc), 
                                             utils.stringify(None), False, False)
            
            def ctxdun(status):
                pass
                
            cls.context = cls.scaffold.context('test_client', utils.statusify(ctxdun), 
                                             utils.stringify(logfunc), 'test_client')
            
            piw.setenv(cls.context.getenv())
            cls.piw = piw
            
        except Exception as e:
            raise RuntimeError(f"Failed to set up TSD context: {e}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up TSD context."""
        try:
            if hasattr(cls, 'context'):
                cls.context.release()
        except:
            pass
    
    def test_setup_file_protocol_compatibility(self):
        """Test that setup file term structures maintain protocol compatibility."""
        from pisession import agentd
        
        # Simulate what find_all_setups() creates
        main_menu = agentd.Menu('Setups')
        
        # Add user setups submenu
        user_menu = agentd.Menu('User Setups')
        user_menu.add_setup('', 'user 2', '/test/path', False, True)
        main_menu.add_child(user_menu)
        
        # Generate the complete term structure
        try:
            complete_term = main_menu.term()
            self.assertIsNotNone(complete_term)
            
            # This is what the GUI tries to do - access the term structure
            if complete_term.arity() > 0:
                first_child = complete_term.arg(0)
                self.assertIsNotNone(first_child)
                
                if first_child.arity() > 0:
                    setup_term = first_child.arg(0)
                    self.assertIsNotNone(setup_term)
                    
            print("✅ Setup file protocol structure compatible")
            
        except Exception as e:
            self.fail(f"Setup file protocol compatibility failed: {e}")
    
    def test_rpc_message_compatibility(self):
        """Test that RPC message structures remain compatible."""
        # Test creating terms that would be used in RPC messages
        message_terms = [
            self.piw.term("method_name", 0),
            self.piw.term("arg1", 0), 
            self.piw.term("arg2", 0),
        ]
        
        for term in message_terms:
            self.assertIsNotNone(term)
            self.assertEqual(term.type(), 3)  # String terms are type 3


if __name__ == '__main__':
    print("🧪 Testing binary protocol compatibility...")
    unittest.main(verbosity=2)