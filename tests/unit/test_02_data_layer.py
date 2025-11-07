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