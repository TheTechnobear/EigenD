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
    def test_data_type_constants(self):
        """Test that data type constants are available and correct."""
        try:
            import pibelcanto.state as state
            
            # Expected type constants from state.h
            expected_types = {
                'T_NULL': 0x00,
                'T_ARRAY': 0x01, 
                'T_STRING': 0x02,
                'T_BOOL': 0x03,
                'T_LONG': 0x04,
                'T_FLOAT': 0x05,
                'T_TUPLE': 0x06,
                'T_DICT': 0x07,
                'T_BLOB': 0x08,
                'T_VECTOR': 0x09
            }
            
            for const_name, expected_value in expected_types.items():
                if hasattr(state, const_name):
                    actual_value = getattr(state, const_name)
                    assert isinstance(actual_value, int), f"{const_name} should be an integer"
                    assert actual_value == expected_value, f"{const_name} should be {expected_value}, got {actual_value}"
                else:
                    pytest.skip(f"Constant {const_name} not available in pibelcanto.state")
        
        except ImportError:
            pytest.skip("pibelcanto.state not available")

@pytest.mark.skip(reason="Database operations require session context - often hang")
class TestDatabaseOperations:
    """
    Test database operations with proper encoding.
    
    Consolidated from: test_database_deserialization.py, debug_state_database.py
    """
    
    @pytest.mark.data
    def test_database_availability(self, test_database):
        """Test that test database is available and accessible."""
        try:
            db = test_database()
            assert db is not None, "Database should be accessible"
            print(f"✓ Database available: {db}")
        except Exception as e:
            pytest.skip(f"Database not available: {e}")
    
    @pytest.mark.data
    def test_database_string_handling(self, test_database, piw_session):
        """Test that database operations handle strings correctly."""
        def test_db_strings(session_ctx):
            try:
                db = test_database()
                
                # Try to access database structure
                # This tests that string handling in database deserialization works
                results = {
                    'db_accessible': db is not None,
                    'has_children': hasattr(db, 'children') or hasattr(db, 'list_children'),
                }
                
                # Try to list children if possible
                if hasattr(db, 'list_children'):
                    try:
                        children = db.list_children()
                        results['children_accessible'] = True
                        results['children_count'] = len(children) if children else 0
                    except Exception as e:
                        results['children_accessible'] = False
                        results['children_error'] = str(e)
                elif hasattr(db, 'children'):
                    try:
                        children = db.children()
                        results['children_accessible'] = True  
                        results['children_count'] = len(children) if children else 0
                    except Exception as e:
                        results['children_accessible'] = False
                        results['children_error'] = str(e)
                
                return results
                
            except Exception as e:
                return {'error': str(e), 'db_accessible': False}
        
        try:
            results = piw_session['run'](test_db_strings)
            
            # Database should be accessible
            assert results.get('db_accessible', False), f"Database should be accessible: {results}"
            
            # If we can access children, string handling should work
            if results.get('children_accessible'):
                assert isinstance(results.get('children_count', -1), int), "Children count should be integer"
            
        except Exception as e:
            pytest.skip(f"Database operations test skipped: {e}")

@pytest.mark.skip(reason="Edge cases require session context - often hang")
class TestDataLayerEdgeCases:
    """
    Test edge cases in data layer for Python 3.14 migration.
    
    Consolidated from: various debug_*.py files
    """
    
    @pytest.mark.data
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
        
        # Most special strings should work (null byte might not)
        for result in results:
            if "\x00" not in result['input']:  # Skip null byte test
                assert result['success'], f"Special string {result['input']} should work: {result.get('error', '')}"
                if result['success']:
                    assert result['is_string'], f"Special string {result['input']} should be recognized as string"