#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for piw term creation with Python 3.14
Tests the fundamental term creation operations that are failing.
"""

import unittest
import sys
import os

# Add EigenD paths
test_dir = os.path.dirname(__file__)
project_root = os.path.join(test_dir, '..', '..')
sys.path.insert(0, os.path.join(project_root, 'tmp', 'stage', 'lib', 'python'))
sys.path.insert(0, project_root)


class TestPiwTermCreation(unittest.TestCase):
    """Test basic piw term creation functionality with Python 3."""
    
    def setUp(self):
        """Import piw module for testing."""
        try:
            import piw
            self.piw = piw
        except ImportError as e:
            self.skipTest(f"Could not import piw: {e}")
    
    def test_simple_term_creation(self):
        """Test creating a simple term."""
        term = self.piw.term("test", 0)
        self.assertIsNotNone(term)
        self.assertEqual(term.type(), 0)
    
    def test_makestring_with_unicode(self):
        """Test makestring with Python 3 Unicode strings."""
        test_string = "user 2"
        
        # This should work in both Python 2 and 3
        result = self.piw.makestring(test_string, 0)
        self.assertIsNotNone(result)
        
        # Create a term from the string
        term = self.piw.term(result)
        self.assertIsNotNone(term)
    
    def test_makestring_with_bytes(self):
        """Test makestring with encoded bytes."""
        test_string = "user 2"
        encoded_string = test_string.encode('utf-8')
        
        result = self.piw.makestring(encoded_string, 0)
        self.assertIsNotNone(result)
        
        # Create a term from the string
        term = self.piw.term(result)
        self.assertIsNotNone(term)
    
    def test_problematic_filenames(self):
        """Test with the actual filenames that are causing issues."""
        problematic_names = [
            "user 2",
            "pico 1 ~ pico", 
            "user 1 ~ pico",
            "",  # empty string
        ]
        
        for name in problematic_names:
            with self.subTest(filename=name):
                # Test both raw and encoded
                try:
                    # Raw string
                    result1 = self.piw.makestring(name, 0)
                    term1 = self.piw.term(result1)
                    
                    # Encoded string  
                    encoded = name.encode('utf-8') if hasattr(name, 'encode') else name
                    result2 = self.piw.makestring(encoded, 0)
                    term2 = self.piw.term(result2)
                    
                except Exception as e:
                    self.fail(f"Failed to create term for '{name}': {e}")
    
    def test_term_with_children(self):
        """Test creating terms with child arguments (like the Menu structure)."""
        # Create parent term
        parent = self.piw.term("parent", 0)
        
        # Create child term
        child_string = self.piw.makestring("child", 0)
        child = self.piw.term(child_string)
        
        # Add child to parent
        parent.add_arg(-1, child)
        
        # Verify structure
        self.assertEqual(parent.arity(), 1)
        retrieved_child = parent.arg(0)
        self.assertIsNotNone(retrieved_child)
    
    def test_term_copy_operation(self):
        """Test the specific term copy operation that's failing."""
        # Create a term structure similar to what find_all_setups creates
        main_term = self.piw.term("test", 0)
        
        # Add a child term
        child_string = self.piw.makestring("test child", 0)
        child_term = self.piw.term(child_string)
        main_term.add_arg(-1, child_term)
        
        # This is the operation that fails - accessing and copying child terms
        if main_term.arity() > 0:
            # This is what EigenTreeItem::itemOpennessChanged does
            retrieved_child = main_term.arg(0)
            
            # Test copying the term (this is where the crash happens)
            try:
                # This should not crash
                copied_term = self.piw.term_t(retrieved_child)
                self.assertIsNotNone(copied_term)
            except Exception as e:
                self.fail(f"Term copy failed: {e}")


class TestMenuTermCreation(unittest.TestCase):
    """Test the Menu class term creation specifically."""
    
    def setUp(self):
        """Import required modules."""
        try:
            import pisession.agentd as agentd
            self.agentd = agentd
        except ImportError as e:
            self.skipTest(f"Could not import agentd: {e}")
    
    def test_empty_menu_term(self):
        """Test creating a term from an empty menu."""
        menu = self.agentd.Menu("Test Menu")
        term = menu.term()
        self.assertIsNotNone(term)
    
    def test_menu_with_setup(self):
        """Test menu with a single setup (the failing case)."""
        menu = self.agentd.Menu("Test Menu")
        
        # Add the problematic setup
        menu.add_setup('', 'user 2', '/test/path', False, True)
        
        # This should not fail
        try:
            term = menu.term()
            self.assertIsNotNone(term)
        except Exception as e:
            self.fail(f"Menu term creation failed: {e}")
    
    def test_menu_with_multiple_setups(self):
        """Test menu with multiple setups."""
        menu = self.agentd.Menu("Test Menu")
        
        # Add various setups that might be problematic
        test_setups = [
            ('', 'user 2', '/path1', False, True),
            ('pico', 'pico 1', '/path2', False, False),
            ('', 'test setup', '/path3', True, True),
        ]
        
        for name, slot, path, upg, user in test_setups:
            menu.add_setup(name, slot, path, upg, user)
        
        try:
            term = menu.term()
            self.assertIsNotNone(term)
            
            # Test accessing the term structure
            if term.arity() > 0:
                child = term.arg(0)
                self.assertIsNotNone(child)
                
        except Exception as e:
            self.fail(f"Multi-setup menu term creation failed: {e}")


class TestEncodingHelpers(unittest.TestCase):
    """Test the encoding helper functions."""
    
    def setUp(self):
        """Import agentd for encoding functions."""
        try:
            import pisession.agentd as agentd
            self.agentd = agentd
        except ImportError as e:
            self.skipTest(f"Could not import agentd: {e}")
    
    def test_encode_for_piw(self):
        """Test the encode_for_piw helper function."""
        # Test various string types
        test_cases = [
            "simple string",
            "user 2", 
            "with spaces",
            "",
            None,
        ]
        
        for test_str in test_cases:
            with self.subTest(string=test_str):
                result = self.agentd.encode_for_piw(test_str)
                
                if test_str is None:
                    self.assertIsNone(result)
                else:
                    self.assertIsNotNone(result)
                    # Should be bytes in Python 3
                    if hasattr(test_str, 'encode'):
                        self.assertIsInstance(result, bytes)


if __name__ == '__main__':
    unittest.main(verbosity=2)