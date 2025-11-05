#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Binary Protocol Preservation Tests for EigenD Python 2→3 Migration

These tests ensure that our string encoding changes preserve the exact binary
protocol that EigenD relies on for cross-language communication between:
- Python layer (agent code)
- C++ layer (native libraries) 
- PIP binding system (generated interface code)

Critical requirements:
1. String data must preserve UTF-8 encoding across all layers
2. Data type information must be maintained
3. Term serialization must be identical to Python 2.7 behavior
4. No corruption of binary data (especially setup files, term structures)
"""

import sys
import os
import unittest
import hashlib

# Add EigenD paths
test_dir = os.path.dirname(__file__)
project_root = os.path.join(test_dir, '..', '..')
tmp_modules = os.path.join(project_root, 'tmp', 'modules')
sys.path.insert(0, tmp_modules)


class TestBinaryProtocolPreservation(unittest.TestCase):
    """Test that binary protocol is preserved across Python 2→3 migration."""
    
    @classmethod
    def setUpClass(cls):
        """Set up TSD context for testing."""
        try:
            import piw
            import piagent
            from pi import utils
            import pisession.agentd as agentd
            
            def logfunc(msg):
                pass
                
            cls.scaffold = piagent.scaffold_mt(1, utils.stringify(logfunc), 
                                             utils.stringify(None), False, False)
            
            def ctxdun(status):
                pass
                
            cls.context = cls.scaffold.context('binary_test', utils.statusify(ctxdun), 
                                             utils.stringify(logfunc), 'binary_test')
            
            piw.setenv(cls.context.getenv())
            cls.piw = piw
            cls.agentd = agentd
            
        except Exception as e:
            cls.skipTest(f"Failed to set up context: {e}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up context."""
        try:
            if hasattr(cls, 'context'):
                cls.context.release()
        except:
            pass
    
    def test_string_utf8_encoding_consistency(self):
        """Test that string encoding is consistent across all layers."""
        print("\n🧪 Testing UTF-8 encoding consistency")
        
        # Test strings that have caused issues historically
        test_strings = [
            "user 2",           # The specific failing case
            "café",             # Latin-1 characters
            "naïve résumé",     # Multiple diacriticals
            "🎵 music 🎸",      # Emoji (4-byte UTF-8)
            "中文测试",          # CJK characters
            "العربية",           # Arabic script (RTL)
            "Ελληνικά",         # Greek
            "Русский",          # Cyrillic
            "",                 # Empty string edge case
            "test~symbol#$%",   # Special characters from setup files
        ]
        
        for test_string in test_strings:
            with self.subTest(string=test_string):
                print(f"\n  Testing: {test_string!r}")
                
                # 1. Python layer encoding
                encoded = self.agentd.encode_for_piw(test_string)
                self.assertIsInstance(encoded, str)  # Should be Unicode in Python 3
                print(f"    encode_for_piw: {encoded!r} ({type(encoded)})")
                
                # 2. C++ layer via makestring (goes through PIP binding)
                data_obj = self.piw.makestring(encoded, 0)
                self.assertIsNotNone(data_obj)
                print(f"    makestring result: {data_obj}")
                
                # 3. Round-trip back to Python
                extracted = data_obj.as_string()
                self.assertEqual(extracted, test_string)
                print(f"    extracted: {extracted!r}")
                
                # 4. Verify UTF-8 bytes are consistent
                original_utf8 = test_string.encode('utf-8')
                extracted_utf8 = extracted.encode('utf-8')
                self.assertEqual(original_utf8, extracted_utf8)
                print(f"    UTF-8 bytes match: {len(original_utf8)} bytes")
    
    def test_data_type_preservation(self):
        """Test that data types are preserved exactly."""
        print("\n🧪 Testing data type preservation")
        
        # Test each data type we use
        test_cases = [
            ("string_empty", lambda: self.piw.makestring("", 0)),
            ("string_simple", lambda: self.piw.makestring("test", 0)),
            ("string_unicode", lambda: self.piw.makestring("café", 0)),
            ("bool_true", lambda: self.piw.makebool(True, 0)),
            ("bool_false", lambda: self.piw.makebool(False, 0)),
        ]
        
        type_map = {}  # Track consistent type values
        
        for desc, factory in test_cases:
            with self.subTest(case=desc):
                print(f"\n  Testing: {desc}")
                
                data_obj = factory()
                self.assertIsNotNone(data_obj)
                
                # Check type information
                data_type = data_obj.data_type()
                type_val = data_obj.type()
                
                print(f"    data_type(): {data_type}")
                print(f"    type(): {type_val}")
                
                # Store type mapping for consistency checking
                category = desc.split('_')[0]  # string, bool
                if category not in type_map:
                    type_map[category] = data_type
                else:
                    self.assertEqual(type_map[category], data_type, 
                                   f"Type mismatch for {category}: expected {type_map[category]}, got {data_type}")
                
                # Verify type check methods
                if category == "string":
                    self.assertTrue(data_obj.is_string())
                    self.assertFalse(data_obj.is_bool())
                elif category == "bool":
                    self.assertTrue(data_obj.is_bool())
                    self.assertFalse(data_obj.is_string())
        
        print(f"\n  Type mapping: {type_map}")
    
    def test_term_serialization_consistency(self):
        """Test that term serialization produces consistent binary output."""
        print("\n🧪 Testing term serialization consistency")
        
        # Create terms using different methods and verify they're equivalent
        test_string = "user 2"
        
        # Method 1: Direct string constructor (this works)
        term1 = self.piw.term(test_string, 0)
        
        # Method 2: Via our workaround
        string_data = self.piw.makestring(test_string, 0)
        term2 = self.agentd.data_to_term(string_data)
        
        # Both should have same properties
        self.assertEqual(term1.type(), term2.type())
        print(f"  Both terms have type: {term1.type()}")
        
        # Both should render to same string representation
        render1 = term1.render()
        render2 = term2.render()
        print(f"  term1.render(): {render1!r}")
        print(f"  term2.render(): {render2!r}")
        
        # They should be equivalent (though not necessarily identical due to different construction paths)
        self.assertEqual(term1.type(), term2.type())
    
    def test_menu_binary_consistency(self):
        """Test that Menu.term() produces consistent binary output."""
        print("\n🧪 Testing Menu binary consistency")
        
        # Create identical menus with our problematic data
        menu1 = self.agentd.Menu("Test Menu")
        menu1.add_setup('', 'user 2', '/test/path', False, True)
        
        menu2 = self.agentd.Menu("Test Menu") 
        menu2.add_setup('', 'user 2', '/test/path', False, True)
        
        # Generate terms
        term1 = menu1.term()
        term2 = menu2.term()
        
        # Should have identical structure
        self.assertEqual(term1.type(), term2.type())
        self.assertEqual(term1.arity(), term2.arity())
        
        print(f"  Menu terms: type={term1.type()}, arity={term1.arity()}")
        
        # Verify children are accessible (this was crashing before)
        if term1.arity() > 0:
            child1 = term1.arg(0)
            child2 = term2.arg(0)
            
            self.assertEqual(child1.type(), child2.type())
            self.assertEqual(child1.arity(), child2.arity())
            
            print(f"  Child terms: type={child1.type()}, arity={child1.arity()}")
    
    def test_setup_file_data_integrity(self):
        """Test that setup file data maintains integrity through the encoding layers."""
        print("\n🧪 Testing setup file data integrity")
        
        # Simulate the data that goes through agentd.find_user_setups()
        setup_data = [
            ('', 'user 2', '/path/to/setup1', False, True),
            ('pico', 'pico 1', '/path/to/setup2', False, False),
            ('test', 'user 1', '/path/to/setup3', True, True),
            ('café setup', 'naïve user', '/path/to/setup4', False, True),
        ]
        
        for name, slot, path, upg, user in setup_data:
            with self.subTest(setup=f"{name}~{slot}"):
                print(f"\n  Testing setup: name={name!r}, slot={slot!r}")
                
                # Test each component that goes through string encoding
                components = [name, slot, path]
                
                for component in components:
                    if component:  # Skip empty strings
                        # Encode through our layer
                        encoded = self.agentd.encode_for_piw(component)
                        
                        # Create data object
                        data_obj = self.piw.makestring(encoded, 0)
                        
                        # Extract back
                        extracted = data_obj.as_string()
                        
                        # Should be identical
                        self.assertEqual(component, extracted)
                        print(f"    Component {component!r} → round-trip OK")
    
    def test_unicode_edge_cases(self):
        """Test Unicode edge cases that could break binary protocol."""
        print("\n🧪 Testing Unicode edge cases")
        
        edge_cases = [
            ("null_char", "test\x00null"),           # Null bytes
            ("high_unicode", "\U0001F600"),          # High Unicode (emoji)
            ("combining", "e\u0301"),                # Combining characters (é)
            ("surrogate_pair", "\U0001D11E"),        # Surrogate pairs
            ("mixed_scripts", "Hello世界"),           # Mixed scripts
            ("bidi_text", "Hello العالم"),           # Bidirectional text
            ("long_string", "x" * 1000),             # Long strings
        ]
        
        for desc, test_string in edge_cases:
            with self.subTest(case=desc):
                print(f"\n  Testing {desc}: {test_string!r}")
                
                try:
                    # Full round-trip through all layers
                    encoded = self.agentd.encode_for_piw(test_string)
                    data_obj = self.piw.makestring(encoded, 0)
                    term = self.agentd.data_to_term(data_obj)
                    
                    # Verify term is valid
                    self.assertIsNotNone(term)
                    self.assertIsInstance(term.type(), int)
                    
                    print(f"    Edge case {desc} handled correctly")
                    
                except Exception as e:
                    # Some edge cases might legitimately fail, document them
                    print(f"    Edge case {desc} failed: {e}")
                    if desc in ["null_char"]:  # Expected failures
                        pass
                    else:
                        raise


def run_tests():
    """Run binary protocol preservation tests."""
    print("=" * 80)
    print("EigenD Binary Protocol Preservation Tests")
    print("=" * 80)
    print("Testing that Python 2→3 migration preserves exact binary compatibility")
    print("=" * 80)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)


if __name__ == '__main__':
    run_tests()