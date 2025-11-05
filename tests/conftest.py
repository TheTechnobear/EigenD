"""
EigenD Testing Framework - Shared Fixtures and Configuration
============================================================

This file provides shared pytest fixtures for consistent test environment setup.
No more manual sys.path manipulation in individual test files.
"""

import sys
import os
import pytest
from pathlib import Path

# Project root detection
PROJECT_ROOT = Path(__file__).parent.parent
EIGEND_ROOT = PROJECT_ROOT
TMP_MODULES = PROJECT_ROOT / "tmp" / "modules"

@pytest.fixture(scope="session", autouse=True)
def setup_eigend_environment():
    """
    Automatically set up EigenD environment for all tests.
    This fixture runs once per test session and configures paths.
    """
    # Add EigenD paths to Python path
    paths_to_add = [
        str(EIGEND_ROOT),
        str(TMP_MODULES),
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # Verify critical paths exist
    required_paths = [
        EIGEND_ROOT / "pi",
        EIGEND_ROOT / "piw", 
        EIGEND_ROOT / "pisession",
        EIGEND_ROOT / "pibelcanto",
    ]
    
    missing_paths = [p for p in required_paths if not p.exists()]
    if missing_paths:
        pytest.fail(f"Missing required EigenD paths: {missing_paths}")
    
    # Set up environment variables if needed
    os.environ.setdefault("EIGEND_ROOT", str(EIGEND_ROOT))
    
    yield
    
    # Cleanup after all tests (if needed)
    pass

@pytest.fixture(scope="session")
def eigend_database_path():
    """Path to the test database file."""
    db_path = Path.home() / "Library" / "Eigenlabs" / "2.3.0-community" / "Global" / "current_setup-main"
    if not db_path.exists():
        pytest.skip(f"Test database not found: {db_path}")
    return str(db_path)

@pytest.fixture
def piw_session():
    """
    Provide a PIW session context for tests that need it.
    Automatically handles session setup and cleanup.
    """
    # Return a simple object that can be used to check if session is needed
    # Don't actually start a session unless explicitly requested
    session_data = {
        'available': True,
        'started': False
    }
    
    def session_runner(test_func):
        import pisession.session
        def inner(session_ctx):
            session_data['context'] = session_ctx
            session_data['started'] = True
            return test_func(session_ctx)
        return pisession.session.run_session(inner)
    
    session_data['run'] = session_runner
    return session_data

@pytest.fixture
def piw_modules():
    """Import and return PIW modules for testing."""
    try:
        import piw
        import pi.state
        import pisession.session
        import pibelcanto
        
        return {
            'piw': piw,
            'state': pi.state,
            'session': pisession.session,
            'belcanto': pibelcanto
        }
    except ImportError as e:
        pytest.fail(f"Failed to import required modules: {e}")

@pytest.fixture
def test_database(eigend_database_path, piw_session):
    """
    Provide access to test database within a PIW session.
    """
    def get_database():
        def open_db(session_ctx):
            import pi.state
            return pi.state.open_database(eigend_database_path)
        return piw_session['run'](open_db)
    
    return get_database

@pytest.fixture  
def sample_data_types(piw_session):
    """
    Create sample data objects for testing data type functionality.
    """
    def create_samples():
        def make_samples(session_ctx):
            import piw
            return {
                'string': piw.makestring("test_string", 0),
                'bool_true': piw.makebool(True, 0),
                'bool_false': piw.makebool(False, 0), 
                'long_positive': piw.makelong(42, 0),
                'long_negative': piw.makelong(-123, 0),
                'long_zero': piw.makelong(0, 0),
            }
        return piw_session['run'](make_samples)
    
    return create_samples

# Test data constants
VALID_TYPE_CODES = {
    0x00: 'T_NULL',
    0x01: 'T_ARRAY',
    0x02: 'T_STRING', 
    0x03: 'T_BOOL',
    0x04: 'T_LONG',
    0x05: 'T_FLOAT',
    0x06: 'T_TUPLE',
    0x07: 'T_DICT',
    0x08: 'T_BLOB',
    0x09: 'T_VECTOR'
}

@pytest.fixture
def type_codes():
    """Provide valid type code mapping for tests."""
    return VALID_TYPE_CODES

# Helper functions for test assertions
def assert_piw_data_valid(data, expected_type=None, expected_value=None):
    """
    Helper function for common PIW data assertions.
    
    Args:
        data: PIW data object
        expected_type: Expected type name ('string', 'bool', 'long')
        expected_value: Expected value (if applicable)
    """
    assert data is not None, "Data object should not be None"
    
    type_code = data.type()
    assert type_code in VALID_TYPE_CODES, f"Invalid type code: {type_code}"
    
    if expected_type == 'string':
        assert data.is_string(), f"Data should be string type (code: {type_code})"
        if expected_value is not None:
            assert data.as_string() == expected_value, f"String value mismatch"
    elif expected_type == 'bool':
        assert data.is_bool(), f"Data should be bool type (code: {type_code})"
        if expected_value is not None:
            assert data.as_bool() == expected_value, f"Bool value mismatch"
    elif expected_type == 'long':
        assert data.is_long(), f"Data should be long type (code: {type_code})"
        if expected_value is not None:
            assert data.as_long() == expected_value, f"Long value mismatch"

# Make helper available to all tests
pytest.assert_piw_data_valid = assert_piw_data_valid