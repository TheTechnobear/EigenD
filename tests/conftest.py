"""
EigenD Testing Framework - Shared Fixtures and Configuration
============================================================

This file provides shared pytest fixtures for consistent test environment setup.
No more manual sys.path manipulation in individual test files.
"""

import sys
import os
import pytest
import signal
from pathlib import Path

# Project root detection
PROJECT_ROOT = Path(__file__).parent.parent
EIGEND_ROOT = PROJECT_ROOT
TMP_MODULES = PROJECT_ROOT / "tmp" / "modules"

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--quick-teardown", 
        action="store_true", 
        default=False, 
        help="Enable quick teardown mode - skip slow session cleanup for faster TDD cycles"
    )

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
        str(EIGEND_ROOT / "tmp" / "plugins"),  # Plugin build directory for plugin tests
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
    
    # Set library path for macOS
    import platform
    if platform.system() == "Darwin":
        lib_path = str(EIGEND_ROOT / "tmp" / "bin")
        current_dyld = os.environ.get("DYLD_LIBRARY_PATH", "")
        if lib_path not in current_dyld:
            new_dyld = f"{lib_path}:{current_dyld}" if current_dyld else lib_path
            os.environ["DYLD_LIBRARY_PATH"] = new_dyld
    
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
def piw_session(request):
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
        
        # Check if quick teardown is requested
        quick_teardown = getattr(request.config.option, 'quick_teardown', False)
        
        # Get test-specific timeout (default 30s for integration tests, 5s for quick mode)
        test_timeout = getattr(request.node.get_closest_marker('timeout'), 'args', (None,))[0]
        if test_timeout is None:
            # Check if this is an integration test (longer timeout by default)
            if 'integration' in request.node.keywords:
                test_timeout = 30.0  # 30 seconds for integration tests
            elif quick_teardown:
                test_timeout = 5.0   # 5 seconds for quick mode
            else:
                test_timeout = 15.0  # 15 seconds default
        
        # In quick mode, allow longer timeouts if explicitly requested via marker
        if quick_teardown and test_timeout is None:
            test_timeout = 5.0  # Only cap if no explicit timeout requested
        
        if quick_teardown:
            # For quick mode, use modified session runner with timeout
            def quick_session_runner(session_func):
                import threading
                import time
                
                result = [None]
                test_success = [None]  # Shared variable for test success
                test_result = [None]   # Shared variable for actual test result
                exception = [None]
                
                def target():
                    try:
                        # Wrap the session function to capture success and result before cleanup
                        def wrapped_session_func(session_ctx):
                            try:
                                func_result = session_func(session_ctx)
                                test_success[0] = True  # Signal success before cleanup
                                test_result[0] = func_result  # Store the actual result
                                return func_result
                            except Exception as e:
                                test_success[0] = False  # Signal failure
                                raise e
                        
                        result[0] = pisession.session.run_session(wrapped_session_func)
                    except Exception as e:
                        exception[0] = e
                
                thread = threading.Thread(target=target)
                thread.daemon = True
                thread.start()
                
                # Wait for test completion or timeout
                import time
                start_time = time.time()
                while thread.is_alive() and test_success[0] is None and (time.time() - start_time) < test_timeout:
                    time.sleep(0.1)  # Poll every 100ms
                
                if test_success[0] is True:
                    # Test completed successfully, return the captured result immediately
                    print(f"\nTest completed successfully, skipping cleanup wait...")
                    return test_result[0]
                elif test_success[0] is False:
                    # Test failed
                    print(f"\nTest failed, skipping cleanup wait...")
                    return {'success': False, 'completed_early': True}
                else:
                    # Test didn't complete within timeout
                    print(f"\nWarning: Session teardown timeout ({test_timeout}s) in quick mode, continuing...")
                    return None
                
                if exception[0]:
                    raise exception[0]
                    
                return result[0]
            
            return quick_session_runner(inner)
        else:
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

@pytest.fixture
def eigend_agentd_session(piw_session):
    """
    Provide a PIW session with agentd initialized for plugin testing.
    Attempts to replicate minimal EigenD application context.
    """
    class MockBackend:
        """Mock backend that implements the methods Workspace expects."""
        def load_started(self, label):
            pass
        
        def load_ended(self, errors=[]):
            pass
        
        def load_status(self, message, progress):
            pass
        
        def stop_gc(self):
            pass
        
        def start_gc(self):
            pass
        
        def run_foreground_sync(self, func, *args, **kwds):
            return func(*args, **kwds)
    
    def setup_agentd():
        def init_agentd(session_ctx):
            try:
                import pisession.agentd as agentd
                import pisession.session as session
                import pi.agent
                import piw
                
                # Create mock backend with required methods
                mock_backend = MockBackend()
                
                # Try to create agentd.Agent with mock backend
                ad = agentd.Agent(mock_backend, 1)  # ordinal 1
                
                # Try to load conductor plugin
                # This would normally be done by setup file parsing
                try:
                    import sys
                    sys.path.insert(0, 'tmp/plugins')  # Relative to project root
                    from Eigenlabs.plg_conductor import clip_manager_plg
                    
                    # Create agent in agentd context
                    agent = clip_manager_plg.Agent('test_conductor', 1)
                    
                    return {
                        'agentd': ad,
                        'agent': agent,
                        'session': session_ctx,
                        'success': True
                    }
                except Exception as e:
                    return {
                        'agentd': ad,
                        'error': str(e),
                        'session': session_ctx,
                        'success': False
                    }
                    
            except Exception as e:
                return {
                    'error': f"Failed to initialize agentd: {e}",
                    'success': False
                }
        
        return piw_session['run'](init_agentd)
    
    return setup_agentd# Test data constants
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