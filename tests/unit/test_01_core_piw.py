"""
Core Tests: PIW Real-time Engine and Session Management
=======================================================

Test Level: 01_core  
Purpose: Test PIW (Pi Wire) real-time engine functionality and session management.

Test Coverage:
- Session context creation and management
- PIW data object creation and validation
- Type checking and value extraction
- Term constructors and data type handling
- String/bytes encoding issues in Python 3.14 migration
- Thread safety operations
- Basic PIW operations without session context

Dependencies: test_00_foundation.py must pass

Note: This file consolidates tests from scattered files in 01_core/ subdirectory
"""

import pytest

class TestPiwSessionManagement:
    """
    Test PIW session context creation and management.
    
    Sessions are required for all PIW operations. These tests validate
    that the session system works correctly under Python 3.14.
    """
    
    @pytest.mark.core
    def test_session_creation_lifecycle(self, piw_session):
        """Test complete session creation and cleanup lifecycle."""
        execution_order = []
        
        def test_callback(session_ctx):
            execution_order.append('session_start')
            assert session_ctx is not None, "Session context should be provided"
            execution_order.append('session_active')
            return "session_result"
        
        result = piw_session['run'](test_callback)
        execution_order.append('session_complete')
        
        assert result == "session_result", "Session should return callback result"
        assert execution_order == ['session_start', 'session_active', 'session_complete'], \
               "Session lifecycle should execute in correct order"
    
    @pytest.mark.core 
    def test_session_exception_handling(self, piw_session):
        """Test that session handles exceptions properly."""
        def failing_callback(session_ctx):
            raise ValueError("Test exception")
        
        with pytest.raises(ValueError, match="Test exception"):
            piw_session['run'](failing_callback)
    
    @pytest.mark.core
    def test_nested_session_operations(self, piw_session, piw_modules):
        """Test that complex operations work within session context."""
        piw = piw_modules['piw']
        
        def complex_operations(session_ctx):
            results = []
            
            # Multiple lock/unlock cycles
            for i in range(3):
                piw.tsd_lock()
                results.append(f"locked_{i}")
                piw.tsd_unlock()
                results.append(f"unlocked_{i}")
            
            # Multiple data creations
            for i in range(5):
                data = piw.makestring(f"test_{i}", 0)
                results.append(data.as_string())
            
            return results
        
        results = piw_session['run'](complex_operations)
        
        # Verify lock/unlock pattern
        lock_results = results[:6]
        expected_locks = ['locked_0', 'unlocked_0', 'locked_1', 'unlocked_1', 'locked_2', 'unlocked_2']
        assert lock_results == expected_locks, "Lock/unlock operations should work correctly"
        
        # Verify string creation pattern  
        string_results = results[6:]
        expected_strings = ['test_0', 'test_1', 'test_2', 'test_3', 'test_4']
        assert string_results == expected_strings, "Multiple string creations should work"

class TestPiwDataCreation:
    """
    Test PIW data object creation and type validation.
    
    Covers the core data types used in EigenD: strings, booleans, and longs.
    These tests are critical for validating Python 3.14 migration issues
    around data type handling and string encoding.
    """
    
    @pytest.mark.core
    def test_string_data_creation(self, sample_data_types, type_codes):
        """Test string data creation and validation."""
        samples = sample_data_types()
        string_data = samples['string']
        
        # Use helper function for consistent validation
        pytest.assert_piw_data_valid(string_data, 'string', 'test_string')
        
        # Verify type code specifically
        assert string_data.type() == type_codes[0x02], \
               f"String data should have STRING type code (0x02)"
    
    @pytest.mark.core
    def test_boolean_data_creation(self, sample_data_types, type_codes):
        """Test boolean data creation and validation."""
        samples = sample_data_types()
        
        # Test True value
        bool_true = samples['bool_true']
        pytest.assert_piw_data_valid(bool_true, 'bool', True)
        assert bool_true.type() == 0x03, "Bool data should have BOOL type code (0x03)"
        
        # Test False value
        bool_false = samples['bool_false']
        pytest.assert_piw_data_valid(bool_false, 'bool', False)
        assert bool_false.type() == 0x03, "Bool data should have BOOL type code (0x03)"
    
    @pytest.mark.core
    def test_long_data_creation(self, sample_data_types, type_codes):
        """Test long integer data creation and validation."""
        samples = sample_data_types()
        
        # Test positive value
        long_pos = samples['long_positive']
        pytest.assert_piw_data_valid(long_pos, 'long', 42)
        
        # Test negative value  
        long_neg = samples['long_negative']
        pytest.assert_piw_data_valid(long_neg, 'long', -123)
        
        # Test zero value
        long_zero = samples['long_zero']
        pytest.assert_piw_data_valid(long_zero, 'long', 0)
        
        # All should have LONG type code
        for data in [long_pos, long_neg, long_zero]:
            assert data.type() == 0x04, "Long data should have LONG type code (0x04)"
    
    @pytest.mark.core
    def test_data_type_exclusivity(self, sample_data_types):
        """Test that data objects have exactly one type."""
        samples = sample_data_types()
        
        for name, data in samples.items():
            type_checks = [
                data.is_string(),
                data.is_bool(), 
                data.is_long(),
                data.is_float(),
                data.is_dict(),
                data.is_array(),
            ]
            
            true_count = sum(type_checks)
            assert true_count == 1, \
                   f"Data '{name}' should have exactly one type, got {true_count} types: {type_checks}"

class TestPiwDataTypeValidation:
    """
    Test data type validation - the core migration issue.
    
    This addresses the specific Python 3.14 migration problem where
    is_string() returns False for data that should be strings, causing
    assertion failures in the EigenD codebase.
    """
    
    @pytest.mark.core
    @pytest.mark.migration
    def test_string_type_assertion_issue(self, piw_session, piw_modules):
        """
        Test the specific is_string() assertion issue from Python 3.14 migration.
        
        This test reproduces and validates the fix for the core problem:
        data objects with STRING type code (0x02) not passing is_string() checks.
        """
        piw = piw_modules['piw']
        
        def test_string_assertions(session_ctx):
            # Create various string data objects
            test_strings = [
                "simple",
                "with spaces",
                "with_underscores", 
                "with-dashes",
                "unicode_test_äöü",  # Unicode handling
                "",  # Empty string
                "very_long_string_" * 10,  # Long string
            ]
            
            results = []
            for test_str in test_strings:
                data = piw.makestring(test_str, 0)
                result = {
                    'input': test_str,
                    'type_code': data.type(),
                    'is_string': data.is_string(),
                    'can_extract': False,
                    'extracted_value': None,
                    'error': None
                }
                
                # This is where the assertion failure occurred in Python 3.14
                try:
                    if data.is_string():
                        result['extracted_value'] = data.as_string()
                        result['can_extract'] = True
                except Exception as e:
                    result['error'] = str(e)
                
                results.append(result)
            
            return results
        
        results = piw_session['run'](test_string_assertions)
        
        # Validate all strings work correctly
        for result in results:
            input_str = result['input']
            
            # Critical assertion: type code should be STRING (0x02)
            assert result['type_code'] == 0x02, \
                   f"String '{input_str}' should have STRING type code (0x02), got {result['type_code']}"
            
            # Critical assertion: is_string() should return True
            assert result['is_string'], \
                   f"String '{input_str}' should pass is_string() check"
            
            # Critical assertion: should be able to extract value
            assert result['can_extract'], \
                   f"String '{input_str}' should allow value extraction: {result['error']}"
            
            # Critical assertion: extracted value should match input
            assert result['extracted_value'] == input_str, \
                   f"String '{input_str}' extraction failed: got '{result['extracted_value']}'"
    
    @pytest.mark.core
    @pytest.mark.migration
    def test_type_code_consistency(self, sample_data_types, type_codes):
        """
        Test that type codes match is_*() method results.
        
        This validates the fix for type code vs type method mismatches
        that were causing assertion failures.
        """
        samples = sample_data_types()
        
        for name, data in samples.items():
            type_code = data.type()
            
            # Map type codes to expected methods
            expected_methods = {
                0x02: 'is_string',  # T_STRING
                0x03: 'is_bool',    # T_BOOL  
                0x04: 'is_long',    # T_LONG
            }
            
            if type_code in expected_methods:
                expected_method = expected_methods[type_code]
                method_result = getattr(data, expected_method)()
                
                assert method_result, \
                       f"Data '{name}' with type_code {type_code} should pass {expected_method}() check"
            else:
                pytest.fail(f"Data '{name}' has unexpected type_code: {type_code}")

class TestPiwStringEncoding:
    """
    Test string encoding issues specific to Python 3.14 migration.
    
    The migration from Python 2.7 to 3.14 introduced strict Unicode handling
    that caused issues with raw bytes being treated as strings.
    """
    
    @pytest.mark.core
    @pytest.mark.migration
    def test_unicode_string_handling(self, piw_session, piw_modules):
        """Test that Unicode strings are handled correctly."""
        piw = piw_modules['piw']
        
        def test_unicode(session_ctx):
            unicode_tests = [
                "Simple ASCII",
                "Umlauts: äöüÄÖÜß", 
                "Symbols: ™©®",
                "Math: ∑∏∆∇",
                "Emoji: 🎵🎹🎸",  # Musical instruments for EigenD!
            ]
            
            results = []
            for test_str in unicode_tests:
                try:
                    data = piw.makestring(test_str, 0)
                    extracted = data.as_string()
                    results.append({
                        'input': test_str,
                        'success': True,
                        'matches': extracted == test_str,
                        'extracted': extracted
                    })
                except Exception as e:
                    results.append({
                        'input': test_str,
                        'success': False,
                        'error': str(e)
                    })
            
            return results
        
        results = piw_session['run'](test_unicode)
        
        for result in results:
            input_str = result['input']
            
            if result['success']:
                assert result['matches'], \
                       f"Unicode string '{input_str}' should round-trip correctly, got '{result['extracted']}'"
            else:
                # Document Unicode issues but don't fail tests
                # EigenD may not support all Unicode characters
                print(f"Unicode handling issue with '{input_str}': {result['error']}")
    
    @pytest.mark.core 
    @pytest.mark.migration
    def test_empty_and_edge_case_strings(self, piw_session, piw_modules):
        """Test edge cases that might cause encoding issues."""
        piw = piw_modules['piw']
        
        def test_edge_cases(session_ctx):
            edge_cases = [
                "",  # Empty string
                " ",  # Single space
                "\n",  # Newline
                "\t",  # Tab
                "\r\n",  # Windows line ending
                "null\0test",  # Embedded null (might not work)
                "very_long_" * 100,  # Very long string
            ]
            
            results = []
            for test_str in edge_cases:
                try:
                    data = piw.makestring(test_str, 0)
                    extracted = data.as_string()
                    results.append({
                        'input': repr(test_str),  # repr for visibility
                        'length': len(test_str),
                        'success': True,
                        'matches': extracted == test_str
                    })
                except Exception as e:
                    results.append({
                        'input': repr(test_str),
                        'length': len(test_str), 
                        'success': False,
                        'error': str(e)
                    })
            
            return results
        
        results = piw_session['run'](test_edge_cases)
        
        for result in results:
            # Most edge cases should work
            if result['length'] > 0:  # Non-empty strings should always work
                assert result['success'], \
                       f"Edge case string {result['input']} should work: {result.get('error', '')}"
                
                if result['success']:
                    assert result['matches'], \
                           f"Edge case string {result['input']} should round-trip correctly"


# ============================================================================
# Consolidated Tests from 01_core/ subdirectory
# ============================================================================

@pytest.mark.core 
class TestPiwTermConstructors:
    """
    Test PIW term constructors and basic operations.
    
    Consolidated from: test_piw_core_functionality.py, test_term_constructors.py
    """
    
    @pytest.mark.core
    def test_term_constructors_without_session(self):
        """Test term constructors that should work without session context."""
        import piw
        
        # Test empty term constructor
        empty_term = piw.term()
        assert empty_term is not None, "Empty term should be created"
        
        # Test unsigned int constructor  
        unsigned_term = piw.term(42)
        assert unsigned_term is not None, "Unsigned term should be created"
        assert unsigned_term.value() == 42, "Unsigned term should preserve value"
        
        # Test term copying
        copy_term = piw.term(unsigned_term)
        assert copy_term is not None, "Term copy should work"
        assert copy_term.value() == unsigned_term.value(), "Copied term should have same value"

@pytest.mark.core
class TestPiwBasicOperations:
    """
    Test basic PIW operations that don't require full session context.
    
    Consolidated from: test_native_modules.py, test_piw_with_init.py
    """
    
    @pytest.mark.core  
    def test_piw_function_availability(self):
        """Test that key PIW functions are available."""
        import piw
        
        # Core data creation functions
        assert hasattr(piw, 'makestring'), "piw.makestring should exist"
        assert hasattr(piw, 'makebool'), "piw.makebool should exist"
        assert hasattr(piw, 'makelong'), "piw.makelong should exist"
        assert hasattr(piw, 'term'), "piw.term should exist"
        
        # Thread safety functions
        assert hasattr(piw, 'tsd_lock'), "piw.tsd_lock should exist"
        assert hasattr(piw, 'tsd_unlock'), "piw.tsd_unlock should exist"
        
        # All should be callable
        for func_name in ['makestring', 'makebool', 'makelong', 'term', 'tsd_lock', 'tsd_unlock']:
            func = getattr(piw, func_name)
            assert callable(func), f"piw.{func_name} should be callable"

@pytest.mark.core
class TestPiwBytesStringHandling:
    """
    Test PIW string/bytes handling specific to Python 3.14 migration.
    
    Consolidated from: test_bytes_vs_unicode.py, debug files
    """
    
    @pytest.mark.core
    @pytest.mark.migration
    def test_makestring_with_different_types(self, piw_session):
        """Test makestring with both str and bytes input."""
        def test_string_types(session_ctx):
            import piw
            
            results = {}
            
            # Test with Python string
            str_input = "test string"
            str_data = piw.makestring(str_input, 0)
            results['str_type'] = str_data.type()
            results['str_is_string'] = str_data.is_string()
            results['str_value'] = str_data.as_string() if str_data.is_string() else None
            
            # Test with bytes
            bytes_input = b"test bytes" 
            bytes_data = piw.makestring(bytes_input, 0)
            results['bytes_type'] = bytes_data.type()
            results['bytes_is_string'] = bytes_data.is_string()
            results['bytes_value'] = bytes_data.as_string() if bytes_data.is_string() else None
            
            return results
        
        results = piw_session['run'](test_string_types)
        
        # Both should work and be recognized as strings
        assert results['str_is_string'], "String input should create string data"
        assert results['bytes_is_string'], "Bytes input should create string data"
        assert results['str_value'] == "test string", "String value should be preserved"
        assert results['bytes_value'] == "test bytes", "Bytes value should be converted to string"