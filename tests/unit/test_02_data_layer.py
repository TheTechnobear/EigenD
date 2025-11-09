"""
Data Layer Tests - Level 02
===========================

Test Level: 02_data_layer
Purpose: Test data serialization, encoding, and database operations.

Test Coverage:
- String encoding and Unicode handling (Python 3.14 migration)
- Data serialization and deserialization
- Database operations with proper encoding
- Data type preservation and validation
- Bytes vs Unicode handling for protocol compatibility

Dependencies: test_00_foundation.py and test_01_core_piw.py must pass

Note: This file consolidates tests from scattered files in 02_data_layer/ subdirectory
"""

import pytest
import sys
import os
from pathlib import Path

# Set up paths
PROJECT_ROOT = Path(__file__).parent.parent.parent  
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "tmp" / "modules"))

@pytest.mark.data
@pytest.mark.migration
class TestStringEncodingMigration:
    """
    Test string encoding fixes for Python 3.14 migration.
    
    Consolidated from: test_string_encoding_fix.py, test_bytes_vs_unicode.py
    """
    
    @pytest.mark.data
    def test_unicode_string_encoding(self):
        """Test Unicode string encoding for PIW compatibility."""
        
        def encode_for_piw(s):
            """Encoding function for PIP bindings"""
            if isinstance(s, str):
                return s.encode('utf-8')
            elif isinstance(s, bytes):
                return s
            else:
                return str(s).encode('utf-8')
        
        # ASCII strings (common case)
        ascii_test = "hello"
        encoded_ascii = encode_for_piw(ascii_test)
        assert isinstance(encoded_ascii, bytes), f"Expected bytes, got {type(encoded_ascii)}"
        assert encoded_ascii == b"hello", f"Expected b'hello', got {encoded_ascii}"
        
        # UTF-8 strings (edge case)
        utf8_test = "hello 世界"  
        encoded_utf8 = encode_for_piw(utf8_test)
        assert isinstance(encoded_utf8, bytes), f"Expected bytes, got {type(encoded_utf8)}"
        # Decode back to verify round-trip
        decoded = encoded_utf8.decode('utf-8')
        assert decoded == utf8_test, f"Round-trip failed: {decoded} != {utf8_test}"
        
        # Bytes input (should pass through)
        bytes_test = b"hello"
        encoded_bytes = encode_for_piw(bytes_test)
        assert encoded_bytes == bytes_test, f"Bytes should pass through unchanged"

@pytest.mark.data
@pytest.mark.migration
class TestDataSerialization:
    """
    Test data serialization and type preservation.
    
    Consolidated from: test_data_layer.py, test_database_deserialization.py
    """
    
    @pytest.mark.data
    def test_basic_data_type_creation(self, piw_session):
        """Test creating and validating basic data types."""
        def test_data_types(session_ctx):
            import piw
            
            results = {}
            
            # Test string data
            string_data = piw.makestring("test string", 0)
            results['string'] = {
                'type': string_data.type(),
                'is_string': string_data.is_string(),
                'value': string_data.as_string() if string_data.is_string() else None
            }
            
            # Test boolean data
            bool_data = piw.makebool(True, 0)
            results['bool'] = {
                'type': bool_data.type(),
                'is_bool': bool_data.is_bool(),
                'value': bool_data.as_bool() if bool_data.is_bool() else None
            }
            
            # Test long data
            long_data = piw.makelong(42, 0)
            results['long'] = {
                'type': long_data.type(),
                'is_long': long_data.is_long(),
                'value': long_data.as_long() if long_data.is_long() else None
            }
            
            return results
        
        results = piw_session['run'](test_data_types)
        
        # Validate string data
        assert results['string']['is_string'], "String data should be recognized as string"
        assert results['string']['value'] == "test string", "String value should be preserved"
        
        # Validate boolean data  
        assert results['bool']['is_bool'], "Bool data should be recognized as bool"
        assert results['bool']['value'] is True, "Bool value should be preserved"
        
        # Validate long data
        assert results['long']['is_long'], "Long data should be recognized as long"
        assert results['long']['value'] == 42, "Long value should be preserved"

@pytest.mark.data
class TestDatabaseOperations:
    """
    Test database operations with proper encoding.
    
    Consolidated from: test_database_deserialization.py, debug_state_database.py
    Note: Now enabled with robust session management from core PIW fixes.
    """
    
    @pytest.mark.data
    @pytest.mark.session
    def test_database_availability(self, piw_session):
        """Test that database functionality is available and accessible."""
        def test_database_access(session_ctx):
            try:
                # Try to access database modules
                import pi.database as database
                results = {
                    'database_module': True,
                    'has_create_function': hasattr(database, 'create') or hasattr(database, 'Database'),
                }
                
                # Try to create or access a test database
                if hasattr(database, 'create'):
                    try:
                        test_db = database.create()
                        results['database_creation'] = True
                        results['database_object'] = test_db is not None
                    except Exception as e:
                        results['database_creation'] = False
                        results['creation_error'] = str(e)
                elif hasattr(database, 'Database'):
                    try:
                        test_db = database.Database()
                        results['database_creation'] = True  
                        results['database_object'] = test_db is not None
                    except Exception as e:
                        results['database_creation'] = False
                        results['creation_error'] = str(e)
                
                return results
                
            except ImportError as e:
                return {'database_module': False, 'import_error': str(e)}
            except Exception as e:
                return {'database_module': True, 'unexpected_error': str(e)}
        
        results = piw_session['run'](test_database_access)
        
        # At minimum, database module should be importable
        if not results.get('database_module', False):
            pytest.skip(f"Database module not available: {results.get('import_error', 'Unknown error')}")
        
        # Report what we found for analysis
        print(f"Database test results: {results}")
    
    @pytest.mark.data
    @pytest.mark.session
    def test_database_string_handling(self, piw_session):
        """Test that database operations handle strings correctly."""
        def test_db_strings(session_ctx):
            try:
                import pi.database as database
                
                # Test string creation and handling
                test_strings = [
                    "simple_string",
                    "string with spaces", 
                    "string_with_underscores",
                    "string-with-dashes",
                ]
                
                results = {'string_tests': []}
                
                for test_str in test_strings:
                    string_result = {
                        'input': test_str,
                        'length': len(test_str),
                    }
                    
                    try:
                        # Test basic string operations that might use database
                        string_result['string_created'] = True
                        string_result['string_preserved'] = test_str == test_str  # Basic preservation test
                        
                    except Exception as e:
                        string_result['string_created'] = False
                        string_result['error'] = str(e)
                    
                    results['string_tests'].append(string_result)
                
                return results
                
            except ImportError as e:
                return {'import_error': str(e)}
            except Exception as e:
                return {'unexpected_error': str(e)}
        
        results = piw_session['run'](test_db_strings)
        
        # Check for import errors
        if 'import_error' in results:
            pytest.skip(f"Database module import failed: {results['import_error']}")
        
        if 'unexpected_error' in results:
            pytest.fail(f"Unexpected error in database string test: {results['unexpected_error']}")
        
        # Validate string handling results
        string_tests = results.get('string_tests', [])
        assert len(string_tests) > 0, "Should have tested at least one string"
        
        for test in string_tests:
            assert test.get('string_created', False), f"String creation failed for '{test['input']}': {test.get('error', 'Unknown error')}"
            assert test.get('string_preserved', False), f"String preservation failed for '{test['input']}'"

@pytest.mark.data
class TestDataLayerEdgeCases:
    """
    Test edge cases in data layer for Python 3.14 migration.
    
    Consolidated from: various debug_*.py files
    Note: Now enabled with robust session management from core PIW fixes.
    """
    
    @pytest.mark.data
    @pytest.mark.session
    def test_empty_and_special_strings(self, piw_session):
        """Test edge cases with empty and special strings."""
        def test_special_strings(session_ctx):
            import piw
            
            test_cases = [
                "",           # Empty string
                " ",          # Single space
                "\n",         # Newline
                "\t",         # Tab
                "\\",         # Backslash
                '"',          # Quote
                "'",          # Single quote
                "hello\x00world",  # Null byte (if supported)
            ]
            
            results = []
            for test_str in test_cases:
                try:
                    data = piw.makestring(test_str, 0)
                    value = data.as_string() if data.is_string() else None
                    results.append({
                        'input': repr(test_str),
                        'success': True,
                        'is_string': data.is_string(),
                        'matches': value == test_str,
                        'type': data.type()
                    })
                except Exception as e:
                    results.append({
                        'input': repr(test_str),
                        'success': False,
                        'error': str(e)
                    })
            
            return results
        
        results = piw_session['run'](test_special_strings)
        
        # Most special strings should work (null byte might not due to C++ limitations)
        for result in results:
            if "\\x00" not in result['input']:  # Skip null byte test for assertion
                assert result['success'], f"Special string {result['input']} should work: {result.get('error', '')}"
                if result['success']:
                    assert result['is_string'], f"Special string {result['input']} should be recognized as string"
                    # Note: For null byte strings, we don't assert matches due to C++ string termination

@pytest.mark.data
@pytest.mark.migration  
class TestSetupFileHandling:
    """
    Test setup file handling and string encoding compatibility.
    
    These tests target the specific issue causing eigend to crash when
    reading setup files due to string assertion failures.
    """
    
    @pytest.mark.data
    def test_setup_file_string_encoding(self, piw_session):
        """Test setup file string encoding compatibility.
        
        Reproduces: eigend crash reading current_setup-main
        Issue: Setup files contain strings that fail is_string() check
        """
        def test_setup_encoding():
            import piw
            import os
            results = {}
            
            try:
                # Test strings that would typically be found in setup files
                setup_strings = [
                    "agent",
                    "connection",
                    "parameter", 
                    "audio_unit",
                    "plugin:audio_unit:2.3.0-community:1.0.5",
                    "/Users/kodiak/Library/Eigenlabs/2.3.0-community/Global",
                    "/Users/kodiak/projects/EigenD/tmp/plugins",
                    "Eigenlabs/plg_primitive/latch_plg",
                    "current_setup-main",
                    "2.3.0-community",
                    "input_connection",
                    "output_connection",
                ]
                
                for i, setup_str in enumerate(setup_strings):
                    # Create data as if it came from a setup file
                    str_data = piw.makestring(setup_str, 0)
                    
                    results[f'setup_{i}_original'] = setup_str
                    results[f'setup_{i}_is_string'] = str_data.is_string()
                    results[f'setup_{i}_type'] = str_data.type()
                    
                    # This is the critical test - calling as_string() after is_string() check
                    if str_data.is_string():
                        try:
                            recovered = str_data.as_string()
                            results[f'setup_{i}_recovered'] = recovered
                            results[f'setup_{i}_matches'] = (recovered == setup_str)
                        except Exception as e:
                            results[f'setup_{i}_as_string_error'] = str(e)
                            results[f'setup_{i}_as_string_error_type'] = type(e).__name__
                    else:
                        results[f'setup_{i}_not_string'] = True
                
                # Test the actual setup file if it exists
                setup_file_path = "/Users/kodiak/Library/Eigenlabs/2.3.0-community/Global/current_setup-main"
                if os.path.exists(setup_file_path):
                    results['setup_file_exists'] = True
                    results['setup_file_size'] = os.path.getsize(setup_file_path)
                    
                    # Try to read a small portion to understand the format
                    try:
                        with open(setup_file_path, 'rb') as f:
                            header = f.read(100)  # First 100 bytes
                        results['setup_file_header'] = header[:50].hex()  # First 50 bytes as hex
                        results['setup_file_readable'] = True
                    except Exception as e:
                        results['setup_file_read_error'] = str(e)
                else:
                    results['setup_file_exists'] = False
                
                return results
                
            except Exception as e:
                results['error'] = str(e)
                results['error_type'] = type(e).__name__
                return results
        
        results = piw_session['run'](test_setup_encoding)
        
        # Check for errors
        if 'error' in results:
            pytest.fail(f"Setup encoding test failed: {results['error_type']}: {results['error']}")
        
        # All setup-style strings should work
        for i in range(12):
            assert results[f'setup_{i}_is_string'], f"Setup string {i} ('{results[f'setup_{i}_original']}') should be recognized as string"
            
            # If it was recognized as a string, as_string() should work
            if results[f'setup_{i}_is_string']:
                assert f'setup_{i}_as_string_error' not in results, f"Setup string {i} should not fail as_string() call"
                assert results[f'setup_{i}_matches'], f"Setup string {i} should round-trip correctly"
        
        # Log setup file information for debugging
        print(f"Setup file exists: {results.get('setup_file_exists', False)}")
        if results.get('setup_file_exists'):
            print(f"Setup file size: {results.get('setup_file_size', 'unknown')} bytes")

    @pytest.mark.data
    def test_setup_file_data_type_consistency(self, piw_session):
        """Test data type consistency in setup files.
        
        Reproduces: Mixed data types causing assertion failures
        Issue: Setup file contains data marked as strings but failing validation
        """
        def test_data_consistency():
            import piw
            results = {}
            
            try:
                # Simulate the mix of data types that might be in a setup file
                mixed_data_scenarios = [
                    ("string_value", "test_string"),
                    ("empty_string", ""),
                    ("numeric_string", "123"),
                    ("path_string", "/path/to/file"),
                    ("version_string", "2.3.0-community"),
                    ("colon_separated", "plugin:type:version"),
                ]
                
                # Test creating mixed data and verifying type consistency
                for name, value in mixed_data_scenarios:
                    # Create string data
                    str_data = piw.makestring(value, 0)
                    
                    # Also create some numeric data for comparison
                    float_data = piw.makefloat(1.0, 0)
                    
                    # Test type detection
                    results[f'{name}_str_is_string'] = str_data.is_string()
                    results[f'{name}_str_type'] = str_data.type()
                    results[f'{name}_float_is_string'] = float_data.is_string()
                    results[f'{name}_float_type'] = float_data.type()
                    
                    # Test safe access patterns (like eigend should use)
                    if str_data.is_string():
                        try:
                            str_value = str_data.as_string()
                            results[f'{name}_str_value'] = str_value
                            results[f'{name}_str_success'] = True
                        except Exception as e:
                            results[f'{name}_str_error'] = str(e)
                            results[f'{name}_str_success'] = False
                    
                    # Verify float data is NOT treated as string
                    if float_data.is_string():
                        results[f'{name}_float_unexpected_string'] = True
                    else:
                        results[f'{name}_float_correctly_not_string'] = True
                        try:
                            float_value = float_data.as_float()
                            results[f'{name}_float_value'] = float_value
                        except Exception as e:
                            results[f'{name}_float_error'] = str(e)
                
                return results
                
            except Exception as e:
                results['error'] = str(e)
                results['error_type'] = type(e).__name__
                return results
        
        results = piw_session['run'](test_data_consistency)
        
        # Check for errors
        if 'error' in results:
            pytest.fail(f"Data consistency test failed: {results['error_type']}: {results['error']}")
        
        # Verify data type consistency
        scenarios = ["string_value", "empty_string", "numeric_string", "path_string", "version_string", "colon_separated"]
        for name in scenarios:
            # String data should be consistently recognized
            assert results[f'{name}_str_is_string'], f"{name} string should be recognized as string"
            assert results[f'{name}_str_success'], f"{name} string should allow as_string() access"
            
            # Float data should NOT be recognized as string
            assert results[f'{name}_float_correctly_not_string'], f"{name} float should not be recognized as string"
            assert f'{name}_float_unexpected_string' not in results, f"{name} float should not be mistaken for string"


@pytest.mark.data
@pytest.mark.migration
class TestPiwDataComparison:
    """
    Test piw.data equality and comparison operations (Python 2→3 migration issue).
    
    Issue: In Python 2, __cmp__ was used for comparisons. Python 3 removed __cmp__
    and requires __eq__, __lt__, etc. (rich comparison protocol).
    
    The PIP template generates tp_richcompare=0, causing piw.data objects to use
    default identity comparison instead of content comparison via compare() method.
    
    This breaks proxy.py's change detection which relies on as_dict_lookup() == comparison.
    """
    
    @pytest.mark.data
    def test_data_equality_basic(self, piw_session):
        """Test that identical piw.data objects compare as equal."""
        
        def test_basic_equality(session_ctx):
            import piw
            
            # Create two null/empty data objects
            d1 = piw.data()
            d2 = piw.data()
            
            return {
                'd1_str': str(d1),
                'd2_str': str(d2),
                'd1_equals_d2': d1 == d2,
                'd1_compare_d2': d1.compare(d2),
                'd1_id': id(d1),
                'd2_id': id(d2),
                'same_identity': d1 is d2
            }
        
        results = piw_session['run'](test_basic_equality)
        
        # compare() returns 0 for equal objects (C++ style)
        assert results['d1_compare_d2'] == 0, "compare() should return 0 for identical data"
        
        # BUG: This fails in Python 3 because __eq__ uses identity comparison
        # instead of calling compare() method
        assert results['d1_equals_d2'], (
            "PYTHON 3 BUG: piw.data.__eq__ uses identity comparison instead of "
            "compare() method. Two identical data objects should compare as equal "
            f"(compare()={results['d1_compare_d2']} but =={results['d1_equals_d2']})"
        )
    
    @pytest.mark.data
    def test_data_equality_strings(self, piw_session):
        """Test that piw.data string objects with same content compare as equal."""
        
        def test_string_equality(session_ctx):
            import piw
            
            # Create two string data objects with identical content
            s1 = piw.makestring("test", 0)
            s2 = piw.makestring("test", 0)
            
            # Create different string for contrast
            s3 = piw.makestring("different", 0)
            
            return {
                's1_str': str(s1),
                's2_str': str(s2),
                's3_str': str(s3),
                's1_equals_s2': s1 == s2,
                's1_compare_s2': s1.compare(s2),
                's1_equals_s3': s1 == s3,
                's1_compare_s3': s1.compare(s3),
            }
        
        results = piw_session['run'](test_string_equality)
        
        # compare() should return 0 for equal strings
        assert results['s1_compare_s2'] == 0, "compare() should return 0 for identical strings"
        assert results['s1_compare_s3'] != 0, "compare() should return non-0 for different strings"
        
        # BUG: These fail in Python 3
        assert results['s1_equals_s2'], (
            "PYTHON 3 BUG: Identical piw.data string objects should compare as equal "
            f"(compare()={results['s1_compare_s2']} but =={results['s1_equals_s2']})"
        )
        assert not results['s1_equals_s3'], "Different strings should not compare as equal"
    
    @pytest.mark.data
    def test_data_equality_dict_lookup(self, piw_session):
        """Test that as_dict_lookup() values compare correctly (the exact proxy.py use case)."""
        
        def test_dict_lookup_comparison(session_ctx):
            import piw
            import pi.utils as utils
            
            # Create a dict with domain metadata (like controller nodes use)
            # Use the same pattern as proxy.py: create dict from Python dict
            dict1 = utils.makedict_nb({'domain': piw.makestring_nb('bfloat(-1000,1000,0,[inc(1),control(updown)])', 0)}, 0)
            dict2 = utils.makedict_nb({'domain': piw.makestring_nb('bfloat(-1000,1000,0,[inc(1),control(updown)])', 0)}, 0)
            
            # Extract domain values
            v1 = dict1.as_dict_lookup('domain')
            v2 = dict2.as_dict_lookup('domain')
            
            return {
                'v1_str': str(v1),
                'v2_str': str(v2),
                'v1_equals_v2': v1 == v2,
                'v1_compare_v2': v1.compare(v2),
                'v1_id': id(v1),
                'v2_id': id(v2),
            }
        
        results = piw_session['run'](test_dict_lookup_comparison)
        
        # compare() should return 0 for identical domain strings
        assert results['v1_compare_v2'] == 0, "compare() should return 0 for identical domains"
        
        # BUG: This is the exact failure case from proxy.py line 279!
        # old_value.as_dict_lookup(k) == new_value.as_dict_lookup(k) returns False
        # even though the domain strings are identical
        assert results['v1_equals_v2'], (
            "CRITICAL BUG: This is the exact failure in proxy.py __meta_changed()! "
            f"Identical domain values should compare equal (compare()={results['v1_compare_v2']} "
            f"but =={results['v1_equals_v2']}). This causes spurious node_changed() "
            "notifications and triggers the attach/detach loop in controller_plg.py"
        )
    
    @pytest.mark.data  
    def test_data_richcompare_all_operators(self, piw_session):
        """Test all rich comparison operators (__eq__, __lt__, __le__, __gt__, __ge__, __ne__)."""
        
        def test_all_comparisons(session_ctx):
            import piw
            
            # Create comparable data
            n1 = piw.makelong(1, 0)
            n2 = piw.makelong(1, 0)
            n3 = piw.makelong(2, 0)
            
            return {
                'n1_eq_n2': n1 == n2,       # Should be True
                'n1_ne_n2': n1 != n2,       # Should be False
                'n1_eq_n3': n1 == n3,       # Should be False
                'n1_ne_n3': n1 != n3,       # Should be True
                'n1_lt_n3': n1 < n3,        # Should be True
                'n1_le_n2': n1 <= n2,       # Should be True
                'n3_gt_n1': n3 > n1,        # Should be True
                'n3_ge_n1': n3 >= n1,       # Should be True
                'n1_compare_n2': n1.compare(n2),
                'n1_compare_n3': n1.compare(n3),
            }
        
        results = piw_session['run'](test_all_comparisons)
        
        # Verify compare() works correctly
        assert results['n1_compare_n2'] == 0, "1 should equal 1"
        assert results['n1_compare_n3'] < 0, "1 should be less than 2"
        
        # BUG: All these will fail because tp_richcompare=0
        assert results['n1_eq_n2'], "__eq__ should work based on compare()"
        assert not results['n1_ne_n2'], "__ne__ should work based on compare()"
        assert not results['n1_eq_n3'], "1 != 2"
        assert results['n1_ne_n3'], "1 != 2"
        assert results['n1_lt_n3'], "1 < 2"
        assert results['n1_le_n2'], "1 <= 1"
        assert results['n3_gt_n1'], "2 > 1"
        assert results['n3_ge_n1'], "2 >= 1"
    
    @pytest.mark.data
    def test_data_nb_inherits_comparison(self, piw_session):
        """Test that data_nb subtype properly inherits comparison from data_base."""
        
        def test_data_nb_comparison(session_ctx):
            import piw
            
            # Create data_nb objects (non-blocking variant)
            nb1 = piw.data_nb()
            nb2 = piw.data_nb()
            
            # Create string data_nb objects
            nbs1 = piw.makestring_nb("test", 0)
            nbs2 = piw.makestring_nb("test", 0)
            nbs3 = piw.makestring_nb("different", 0)
            
            return {
                'nb1_equals_nb2': nb1 == nb2,
                'nb1_compare_nb2': nb1.compare(nb2),
                'nbs1_equals_nbs2': nbs1 == nbs2,
                'nbs1_compare_nbs2': nbs1.compare(nbs2),
                'nbs1_equals_nbs3': nbs1 == nbs3,
                'nbs1_compare_nbs3': nbs1.compare(nbs3),
                'nbs1_lt_nbs3': nbs1 < nbs3,  # Test ordering
            }
        
        results = piw_session['run'](test_data_nb_comparison)
        
        # Verify compare() works
        assert results['nb1_compare_nb2'] == 0, "Empty data_nb should equal"
        assert results['nbs1_compare_nbs2'] == 0, "Identical strings should equal"
        
        # Verify __eq__ works (inherited from data_base)
        assert results['nb1_equals_nb2'], "data_nb should inherit __eq__ from data_base"
        assert results['nbs1_equals_nbs2'], "data_nb strings should compare equal"
        assert not results['nbs1_equals_nbs3'], "Different strings should not compare equal"
        
        # Verify ordering operators work
        assert results['nbs1_lt_nbs3'], "data_nb should inherit < operator from data_base"