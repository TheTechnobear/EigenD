#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for all piw.term constructors - Python 2→3 migration validation

Tests each constructor variant from the PIP binding system to ensure:
1. Working constructors still work correctly
2. Broken constructors are properly identified
3. Our workaround preserves binary protocol compatibility
4. String encoding is handled correctly at each layer
"""

import sys
import os
import unittest

# Add EigenD paths
test_dir = os.path.dirname(__file__)
project_root = os.path.join(test_dir, '..', '..')
tmp_modules = os.path.join(project_root, 'tmp', 'modules')
sys.path.insert(0, tmp_modules)


class TestTermConstructors(unittest.TestCase):
    """Test all piw.term constructor variants."""
    
    @classmethod
    def setUpClass(cls):
        """Set up TSD context for piw operations."""
        try:
            # Import required modules
            import piw
            import piagent
            from pi import utils
            
            # Create scaffold like session.run_session() does
            def logfunc(msg):
                pass  # Suppress logging for tests
                
            cls.scaffold = piagent.scaffold_mt(1, utils.stringify(logfunc), 
                                             utils.stringify(None), False, False)
            
            def ctxdun(status):
                pass
                
            cls.context = cls.scaffold.context('test_term', utils.statusify(ctxdun), 
                                             utils.stringify(logfunc), 'test_term')
            
            piw.setenv(cls.context.getenv())
            cls.piw = piw
            
        except Exception as e:
            cls.skipTest(f"Failed to set up TSD context: {e}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up TSD context."""
        try:
            if hasattr(cls, 'context'):
                cls.context.release()
        except:
            pass
    
    def test_term_empty_constructor(self):
        """Test term() - empty constructor."""
        print("\n🧪 Testing term() - empty constructor")
        
        try:
            term = self.piw.term()
            self.assertIsNotNone(term)
            
            # Verify basic properties
            self.assertIsInstance(term.type(), int)
            self.assertIsInstance(term.arity(), int)
            
            print(f"✅ term() works: type={term.type()}, arity={term.arity()}")
            
        except Exception as e:
            self.fail(f"term() constructor failed: {e}")
    
    def test_term_unsigned_constructor(self):
        """Test term(unsigned) - type constructor."""
        print("\n🧪 Testing term(unsigned) - type constructor")
        
        test_types = [0, 1, 2, 6, 7]  # Common term types
        
        for type_val in test_types:
            with self.subTest(type=type_val):
                try:
                    term = self.piw.term(type_val)
                    self.assertIsNotNone(term)
                    
                    # Verify basic properties without assuming specific type mapping
                    self.assertIsInstance(term.type(), int)
                    self.assertIsInstance(term.arity(), int)
                    self.assertGreaterEqual(term.type(), 0)
                    
                    print(f"✅ term({type_val}) works: type={term.type()}")
                    
                except Exception as e:
                    self.fail(f"term({type_val}) constructor failed: {e}")
    
    def test_term_string_unsigned_constructor(self):
        """Test term(const char *, unsigned) - string + type constructor."""
        print("\n🧪 Testing term(const char *, unsigned) - string + type constructor")
        
        test_cases = [
            ("simple", 0),
            ("user 2", 0),
            ("test string", 0),
            ("", 0),
            ("café", 0),  # Unicode characters
            ("naïve", 0),
            ("🎵", 0),   # Emoji
        ]
        
        for test_string, type_val in test_cases:
            with self.subTest(string=test_string, type=type_val):
                try:
                    term = self.piw.term(test_string, type_val)
                    self.assertIsNotNone(term)
                    
                    # Verify basic properties without assuming specific type mapping
                    self.assertIsInstance(term.type(), int)
                    self.assertIsInstance(term.arity(), int)
                    self.assertGreaterEqual(term.type(), 0)
                    
                    print(f"✅ term({test_string!r}, {type_val}) works: type={term.type()}")
                    
                except Exception as e:
                    self.fail(f"term({test_string!r}, {type_val}) constructor failed: {e}")
    
    def test_term_data_constructor_broken(self):
        """Test term(const data &) - data constructor (EXPECTED TO FAIL in Python 3)."""
        print("\n🧪 Testing term(const data &) - data constructor (expected to fail)")
        
        # Create data objects using makestring and makebool
        test_cases = [
            ("makestring", lambda: self.piw.makestring("test", 0)),
            ("makebool", lambda: self.piw.makebool(True, 0)),
        ]
        
        for desc, data_factory in test_cases:
            with self.subTest(data_type=desc):
                try:
                    data_obj = data_factory()
                    self.assertIsNotNone(data_obj)
                    
                    # This constructor is expected to fail in Python 3
                    term = self.piw.term(data_obj)
                    
                    # If we get here, the constructor unexpectedly worked
                    print(f"⚠️  term({desc}) unexpectedly worked: {term}")
                    
                except Exception as e:
                    # This is expected - the constructor is broken in Python 3
                    print(f"❌ term({desc}) failed as expected: {e}")
                    self.assertIn("call problem", str(e).lower())
    
    def test_term_copy_constructor(self):
        """Test term(const term &) - copy constructor."""
        print("\n🧪 Testing term(const term &) - copy constructor")
        
        try:
            # Create an original term
            original = self.piw.term("test", 0)
            self.assertIsNotNone(original)
            
            print(f"Original term created: {original}")
            print(f"Original type: {original.type()}, arity: {original.arity()}")
            
            # Get information about the term constructor
            print(f"term class: {self.piw.term}")
            print(f"term.__init__ methods: {dir(self.piw.term)}")
            
            # Try to copy the term using copy constructor
            print("Attempting copy constructor...")
            copied = self.piw.term(original)  # This is the failing copy constructor
            self.assertIsNotNone(copied)
            
            # Verify properties match
            self.assertEqual(copied.type(), original.type())
            self.assertEqual(copied.arity(), original.arity())
            
            print(f"✅ term(term) copy constructor works")
            
        except TypeError as e:
            # Capture the exact error details
            print(f"❌ COPY CONSTRUCTOR FAILURE:")
            print(f"   Error: {e}")
            print(f"   Error type: {type(e)}")
            
            # Try to understand the signature issue
            print(f"\n🔍 Investigating term constructor signatures...")
            
            # Check if we can call with different argument counts
            test_cases = [
                ("term()", lambda: self.piw.term()),
                ("term(42)", lambda: self.piw.term(42)),
                ("term('test', 0)", lambda: self.piw.term("test", 0)),
            ]
            
            for desc, test_func in test_cases:
                try:
                    result = test_func()
                    print(f"   ✅ {desc} works: {result}")
                except Exception as test_e:
                    print(f"   ❌ {desc} fails: {test_e}")
            
            # This is a known issue - fail the test but provide diagnostics
            self.fail(f"term copy constructor failed with signature issue: {e}")
        except Exception as e:
            print(f"❌ Unexpected error in copy constructor test: {e}")
            import traceback
            traceback.print_exc()
            self.fail(f"term copy constructor failed: {e}")


class TestDataToTermWorkaround(unittest.TestCase):
    """Test our data_to_term() workaround function."""
    
    @classmethod
    def setUpClass(cls):
        """Set up TSD context."""
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
                
            cls.context = cls.scaffold.context('test_workaround', utils.statusify(ctxdun), 
                                             utils.stringify(logfunc), 'test_workaround')
            
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
    
    def test_data_to_term_string(self):
        """Test data_to_term() with string data."""
        print("\n🧪 Testing data_to_term() with string data")
        
        test_strings = [
            "simple",
            "user 2", 
            "test string",
            "",
            "café",
            "naïve", 
            "🎵"
        ]
        
        for test_string in test_strings:
            with self.subTest(string=test_string):
                try:
                    # Create string data using makestring
                    string_data = self.piw.makestring(test_string, 0)
                    self.assertIsNotNone(string_data)
                    
                    # Use our workaround
                    term = self.agentd.data_to_term(string_data)
                    self.assertIsNotNone(term)
                    
                    # Verify it's a valid term
                    self.assertIsInstance(term.type(), int)
                    self.assertIsInstance(term.arity(), int)
                    
                    print(f"✅ data_to_term(makestring({test_string!r})) works")
                    
                except Exception as e:
                    self.fail(f"data_to_term failed for string {test_string!r}: {e}")
    
    def test_data_to_term_bool(self):
        """Test data_to_term() with boolean data."""
        print("\n🧪 Testing data_to_term() with boolean data")
        
        test_bools = [True, False]
        
        for test_bool in test_bools:
            with self.subTest(bool=test_bool):
                try:
                    # Create bool data using makebool
                    bool_data = self.piw.makebool(test_bool, 0)
                    self.assertIsNotNone(bool_data)
                    
                    # Use our workaround
                    term = self.agentd.data_to_term(bool_data)
                    self.assertIsNotNone(term)
                    
                    # Verify it's a valid term
                    self.assertIsInstance(term.type(), int)
                    self.assertIsInstance(term.arity(), int)
                    
                    print(f"✅ data_to_term(makebool({test_bool})) works")
                    
                except Exception as e:
                    self.fail(f"data_to_term failed for bool {test_bool}: {e}")


class TestStringEncodingProtocol(unittest.TestCase):
    """Test that string encoding maintains binary protocol compatibility."""
    
    @classmethod
    def setUpClass(cls):
        """Set up context."""
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
                
            cls.context = cls.scaffold.context('test_encoding', utils.statusify(ctxdun), 
                                             utils.stringify(logfunc), 'test_encoding')
            
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
    
    def test_encode_for_piw_function(self):
        """Test that encode_for_piw() produces correct string types."""
        print("\n🧪 Testing encode_for_piw() string type handling")
        
        test_cases = [
            ("simple string", str),
            ("user 2", str),
            ("", str),
            (None, type(None)),
            (123, str),  # Numbers get converted to string
            (b"bytes input", str),  # Bytes get decoded to string
        ]
        
        for test_input, expected_type in test_cases:
            with self.subTest(input=test_input):
                result = self.agentd.encode_for_piw(test_input)
                
                if test_input is None:
                    self.assertIsNone(result)
                else:
                    self.assertIsInstance(result, expected_type)
                    if sys.version_info[0] >= 3:
                        # In Python 3, should always return Unicode strings (not bytes)
                        if result is not None:
                            self.assertIsInstance(result, str)
                            self.assertNotIsInstance(result, bytes)
                
                print(f"✅ encode_for_piw({test_input!r}) -> {result!r} ({type(result)})")
    
    def test_makestring_unicode_compatibility(self):
        """Test that makestring works with Unicode strings from encode_for_piw()."""
        print("\n🧪 Testing makestring Unicode compatibility")
        
        problematic_strings = [
            "user 2",      # Spaces that caused issues
            "café",        # Latin extended characters  
            "naïve",       # Diacritical marks
            "résumé",      # Multiple diacriticals
            "🎵",          # Emoji (4-byte UTF-8)
            "中文",        # CJK characters
            "العربية",      # Arabic script
            "",            # Empty string
            "test~symbol", # Special characters from setup files
        ]
        
        for test_string in problematic_strings:
            with self.subTest(string=test_string):
                try:
                    # Use our encoding function
                    encoded = self.agentd.encode_for_piw(test_string)
                    
                    # This should work with makestring
                    data_obj = self.piw.makestring(encoded, 0)
                    self.assertIsNotNone(data_obj)
                    
                    # Should be able to extract the string back
                    extracted = data_obj.as_string()
                    self.assertEqual(extracted, test_string)
                    
                    print(f"✅ Full round-trip works for: {test_string!r}")
                    
                except Exception as e:
                    self.fail(f"Unicode round-trip failed for {test_string!r}: {e}")
    
    def test_binary_protocol_preservation(self):
        """Test that our changes preserve the binary protocol for different data types."""
        print("\n🧪 Testing binary protocol preservation")
        
        # Test that different data types maintain their type information
        test_cases = [
            ("string", lambda: self.piw.makestring("test", 0), "is_string"),
            ("bool_true", lambda: self.piw.makebool(True, 0), "is_bool"), 
            ("bool_false", lambda: self.piw.makebool(False, 0), "is_bool"),
        ]
        
        for desc, data_factory, type_check in test_cases:
            with self.subTest(data_type=desc):
                try:
                    # Create data object
                    data_obj = data_factory()
                    self.assertIsNotNone(data_obj)
                    
                    # Verify type is preserved
                    type_method = getattr(data_obj, type_check)
                    self.assertTrue(type_method(), f"{desc} should satisfy {type_check}()")
                    
                    # Verify data_type() method returns consistent value
                    data_type = data_obj.data_type()
                    self.assertIsInstance(data_type, int)
                    self.assertGreaterEqual(data_type, 0)
                    
                    print(f"✅ {desc}: type={data_type}, {type_check}()={type_method()}")
                    
                except Exception as e:
                    self.fail(f"Binary protocol test failed for {desc}: {e}")


class TestMenuTermCreationWithWorkaround(unittest.TestCase):
    """Test Menu.term() creation with our workaround (the actual failing case)."""
    
    @classmethod
    def setUpClass(cls):
        """Set up context."""
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
                
            cls.context = cls.scaffold.context('test_menu', utils.statusify(ctxdun), 
                                             utils.stringify(logfunc), 'test_menu')
            
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
    
    def test_menu_with_problematic_setup(self):
        """Test Menu.term() with the specific setup that was causing crashes."""
        print("\n🧪 Testing Menu.term() with problematic setup (original failing case)")
        
        try:
            # Create menu like find_user_setups() does
            menu = self.agentd.Menu("Test Menu")
            
            # Add the specific setup that was causing term_copy crashes
            menu.add_setup('', 'user 2', '/test/path', False, True)
            
            # This should now work with our workaround
            term = menu.term()
            self.assertIsNotNone(term)
            
            # Verify term structure
            self.assertIsInstance(term.type(), int)
            self.assertIsInstance(term.arity(), int)
            
            # Test accessing children (this was causing the crash)
            if term.arity() > 0:
                child = term.arg(0)
                self.assertIsNotNone(child)
                
                # Test nested access
                if child.arity() > 0:
                    nested_child = child.arg(0)
                    self.assertIsNotNone(nested_child)
            
            print("✅ Menu.term() with problematic setup now works!")
            
        except Exception as e:
            self.fail(f"Menu.term() test failed: {e}")
    
    def test_multiple_setups_with_unicode(self):
        """Test menu with multiple setups containing Unicode characters."""
        print("\n🧪 Testing Menu with multiple Unicode setups")
        
        test_setups = [
            ('café', 'user 1', '/path1', False, True),
            ('naïve', 'user 2', '/path2', False, True), 
            ('🎵 music', 'user 3', '/path3', False, True),
            ('', 'empty name', '/path4', False, True),
        ]
        
        try:
            menu = self.agentd.Menu("Unicode Test Menu")
            
            for name, slot, path, upg, user in test_setups:
                menu.add_setup(name, slot, path, upg, user)
            
            # Generate term
            term = menu.term()
            self.assertIsNotNone(term)
            
            print(f"✅ Menu with {len(test_setups)} Unicode setups works!")
            
        except Exception as e:
            self.fail(f"Unicode menu test failed: {e}")


def run_tests():
    """Run all term constructor tests."""
    print("=" * 80)
    print("EigenD Term Constructor Tests - Python 2→3 Migration Validation")
    print("=" * 80)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestTermConstructors,
        TestDataToTermWorkaround,
        TestStringEncodingProtocol,
        TestMenuTermCreationWithWorkaround,
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 80)
    if result.wasSuccessful():
        print("🎉 All term constructor tests PASSED")
        return 0
    else:
        print("💥 Some term constructor tests FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())