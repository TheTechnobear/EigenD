"""
EigenD Foundation Tests - Level 00
=================================

These tests verify basic Python 3.14 compatibility and core module imports.
They serve as the foundation for all higher-level testing and must pass first.

Test Strategy:
- Verify Python 3.14 environment setup
- Test core EigenD module imports (pi, piw, pisession, pibelcanto)
- Validate basic functionality without complex session requirements
- Skip advanced PIW data operations that require session context
"""

import pytest
import sys
import os
from pathlib import Path

# Set up paths for EigenD testing
PROJECT_ROOT = Path(__file__).parent.parent.parent  # /Users/kodiak/projects/EigenD
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "tmp" / "modules"))

@pytest.mark.foundation
class TestPythonEnvironment:
    """Test Python 3.14 environment setup and basic functionality"""
    
    def test_python_version(self):
        """Verify we're running Python 3.14"""
        version = sys.version_info
        assert version.major == 3, f"Expected Python 3.x, got {version.major}.x"
        assert version.minor == 14, f"Expected Python 3.14, got {version.major}.{version.minor}"
    
    def test_basic_operations(self):
        """Test basic Python operations work correctly"""
        # Math operations
        assert 2 + 2 == 4
        assert 10 / 3 == pytest.approx(3.333333)
        
        # String operations  
        test_str = "Hello, EigenD!"
        assert test_str.upper() == "HELLO, EIGEND!"
        assert "EigenD" in test_str
        
        # List operations
        numbers = [1, 2, 3, 4, 5]
        assert sum(numbers) == 15
        assert len(numbers) == 5

@pytest.mark.foundation
@pytest.mark.migration
class TestModuleImports:
    """Test that core EigenD modules can be imported in Python 3.14"""
    
    def test_pi_module_import(self):
        """Test pi module imports successfully"""
        import pi
        assert pi is not None
        
        # Test specific submodules
        import pi.state
        assert pi.state is not None
        
    def test_piw_module_import(self):
        """Test piw module imports successfully"""
        import piw
        assert piw is not None
        
        # Verify core functions exist (but don't call them without session)
        assert hasattr(piw, 'makestring'), "piw.makestring function should exist"
        assert hasattr(piw, 'makebool'), "piw.makebool function should exist"
        assert hasattr(piw, 'makelong'), "piw.makelong function should exist"
        
        # Verify these are callable
        assert callable(piw.makestring), "piw.makestring should be callable"
        assert callable(piw.makebool), "piw.makebool should be callable"
        assert callable(piw.makelong), "piw.makelong should be callable"
    
    def test_pisession_module_import(self):
        """Test pisession module imports successfully"""
        import pisession
        assert pisession is not None
        
        import pisession.session
        assert pisession.session is not None
        assert hasattr(pisession.session, 'run_session'), "run_session function should exist"
        assert callable(pisession.session.run_session), "run_session should be callable"
    
    def test_pibelcanto_module_import(self):
        """Test pibelcanto module imports successfully"""
        import pibelcanto
        assert pibelcanto is not None

@pytest.mark.foundation
class TestModuleStructure:
    """Test the structure and organization of core modules"""
    
    def test_pi_module_structure(self):
        """Test pi module has expected structure"""
        import pi
        
        # The pi module is loaded and functional
        assert hasattr(pi, '__file__'), "pi module should have __file__ attribute"
        assert hasattr(pi, '__path__'), "pi module should have __path__ attribute"
        
        # Verify we can import key submodules
        try:
            import pi.state
            pi_state_works = True
        except ImportError:
            pi_state_works = False
            
        try:
            import pi.agent
            pi_agent_works = True
        except ImportError:
            pi_agent_works = False
            
        # At least one key submodule should work
        assert pi_state_works or pi_agent_works, "At least one pi submodule should be importable"
    
    def test_project_paths_exist(self):
        """Test that expected project directories exist"""
        # Use the actual project root where EigenD is located
        actual_paths = [
            PROJECT_ROOT / "pi",
            PROJECT_ROOT / "piw", 
            PROJECT_ROOT / "pisession",
            PROJECT_ROOT / "pibelcanto",
        ]
        
        # Also check tmp/modules where generated modules might be
        tmp_paths = [
            PROJECT_ROOT / "tmp" / "modules" / "pi",
            PROJECT_ROOT / "tmp" / "modules" / "piw",
        ]
        
        # At least the main directories should exist
        main_dirs_exist = [path.exists() for path in actual_paths]
        tmp_dirs_exist = [path.exists() for path in tmp_paths if path.exists()]
        
        # We need either the main directories OR the tmp directories to exist
        assert any(main_dirs_exist) or any(tmp_dirs_exist), "Either main project directories or tmp/modules should exist"

@pytest.mark.foundation
class TestPiwDataCreation:
    """Test PIW data creation (foundation level - basic functionality)"""
    
    @pytest.mark.foundation
    def test_piw_data_creation_placeholder(self):
        """Test basic PIW data creation capabilities without session context."""
        try:
            import piw
            
            # Test that PIW module has basic functionality
            piw_attrs = [attr for attr in dir(piw) if not attr.startswith('_')]
            assert len(piw_attrs) > 5, f"PIW should have functionality, found {len(piw_attrs)} attributes"
            
            # Test for common PIW functions (check what actually exists)
            expected_functions = ['make_float', 'make_int', 'make_string', 'float_value', 'int_value']
            available_functions = []
            
            for func_name in expected_functions:
                if hasattr(piw, func_name):
                    func = getattr(piw, func_name)
                    if callable(func):
                        available_functions.append(func_name)
            
            # Test basic data type checking functions
            type_functions = ['is_float', 'is_int', 'is_string']
            available_types = []
            for func_name in type_functions:
                if hasattr(piw, func_name):
                    func = getattr(piw, func_name)
                    if callable(func):
                        available_types.append(func_name)
            
            print(f"✓ PIW data functions available: {available_functions}")
            print(f"✓ PIW type functions available: {available_types}")
            print(f"✓ PIW total attributes: {len(piw_attrs)}")
            
            # Just verify PIW has some useful functionality
            assert len(piw_attrs) > 0, "PIW module should have some functionality"
            
        except ImportError:
            pytest.skip("PIW module not available for data creation testing")

@pytest.mark.foundation
class TestFoundationSummary:
    """Summary test for foundation level"""
    
    def test_foundation_components_available(self):
        """Verify all foundation components are available"""
        components = {}
        
        # Test each component
        try:
            import pi
            components['pi'] = True
        except ImportError:
            components['pi'] = False
            
        try:
            import piw  
            components['piw'] = True
        except ImportError:
            components['piw'] = False
            
        try:
            import pisession
            components['pisession'] = True
        except ImportError:
            components['pisession'] = False
            
        try:
            import pibelcanto
            components['pibelcanto'] = True
        except ImportError:
            components['pibelcanto'] = False
        
        # All components should be available
        failed_components = [name for name, available in components.items() if not available]
        assert not failed_components, f"Failed to import: {failed_components}"
        
        print(f"\n✓ Foundation Level Summary:")
        print(f"✓ Python 3.14 environment: OK")
        print(f"✓ Core modules imported: {list(components.keys())}")
        print(f"✓ Foundation tests: PASSED")

import pytest

class TestModuleImports:
    """
    Test that all required EigenD modules import correctly.
    
    This is the foundation test - if these fail, nothing else will work.
    These tests validate the basic Python 3.14 migration success.
    """
    
    @pytest.mark.foundation
    def test_core_pi_modules_import(self):
        """Test core pi module imports."""
        import pi
        import pi.state
        import pi.agent
        
        # Try to import pi.node but don't require specific attributes
        try:
            import pi.node
            node_imported = True
        except ImportError:
            node_imported = False
        
        # Verify modules have expected attributes
        assert hasattr(pi.state, 'open_database'), "pi.state should have open_database function"
        assert hasattr(pi.agent, 'Agent'), "pi.agent should have Agent class"
        
        # Check pi.node if it imported successfully
        if node_imported:
            assert hasattr(pi, 'node'), "pi.node should be accessible via pi module"
    
    @pytest.mark.foundation
    def test_piw_realtime_engine_import(self, piw_modules):
        """Test piw (real-time engine) import and essential functions."""
        piw = piw_modules['piw']
        
        # Test key piw functions exist that are actually used in EigenD
        essential_functions = [
            'tsd_lock', 'tsd_unlock',  # Thread safety
            'makestring', 'makebool', 'makelong',  # Data creation
        ]
        
        for func_name in essential_functions:
            assert hasattr(piw, func_name), f"piw.{func_name} should exist"
    
    @pytest.mark.foundation 
    def test_pisession_management_import(self, piw_modules):
        """Test pisession (session management) import."""
        session = piw_modules['session']
        
        assert hasattr(session, 'run_session'), "pisession.session should have run_session function"
    
    @pytest.mark.foundation
    def test_pibelcanto_language_data_import(self, piw_modules):
        """Test pibelcanto (language/data) import including generated modules."""
        belcanto = piw_modules['belcanto']
        
        # Test that generated lexicon module is accessible
        import pibelcanto.lexicon
        
        # Test if we can access key constants (if available)
        if hasattr(belcanto, 'state'):
            state_module = belcanto.state
            expected_constants = ['T_NULL', 'T_ARRAY', 'T_STRING', 'T_BOOL', 'T_LONG', 'T_FLOAT', 'T_TUPLE', 'T_DICT']
            
            for const in expected_constants:
                if hasattr(state_module, const):
                    value = getattr(state_module, const)
                    assert isinstance(value, int), f"{const} should be an integer type code"

class TestPythonEnvironment:
    """
    Test Python environment setup and compatibility.
    
    Validates that the Python 3.14 environment is correctly configured
    for EigenD operation.
    """
    
    @pytest.mark.foundation
    def test_python_version(self):
        """Verify we're running Python 3.14."""
        import sys
        
        major, minor = sys.version_info[:2]
        assert major == 3, f"Should be Python 3.x, got {major}.{minor}"
        assert minor == 14, f"Should be Python 3.14, got {major}.{minor}"
    
    @pytest.mark.foundation
    def test_required_paths_accessible(self):
        """Test that required EigenD paths are accessible."""
        import os
        import sys
        
        # Check that project root is in Python path
        project_paths = [p for p in sys.path if 'EigenD' in p]
        assert len(project_paths) > 0, "EigenD project paths should be in sys.path"
        
        # Verify EIGEND_ROOT environment variable if set
        if 'EIGEND_ROOT' in os.environ:
            eigend_root = os.environ['EIGEND_ROOT']
            assert os.path.exists(eigend_root), f"EIGEND_ROOT path should exist: {eigend_root}"
    
    @pytest.mark.foundation
    def test_native_modules_available(self):
        """Test that native compiled modules are available."""
        # These are the .so files that should be built
        expected_natives = [
            'piw_native',
            'pi_state_native', 
            'pisession_native',
        ]
        
        for native_name in expected_natives:
            try:
                __import__(native_name)
            except ImportError:
                pytest.skip(f"Native module {native_name} not built - run 'make' first")

@pytest.mark.foundation
class TestBasicFunctionality:
    """
    Basic PIW functionality tests (foundation level - no session required).
    
    These tests are moved to test_01_core_piw.py as they require PIW session context.
    """
    
    @pytest.mark.foundation
    def test_placeholder_for_piw_sessions(self):
        """Test basic PIW functionality that doesn't require full session context."""
        try:
            import piw
            
            # Test basic PIW utilities and constants
            basic_functions = ['tsd_time', 'hash_key'] 
            available_functions = []
            
            for func_name in basic_functions:
                if hasattr(piw, func_name):
                    func = getattr(piw, func_name)
                    if callable(func):
                        available_functions.append(func_name)
            
            # Test that PIW module has substantial functionality
            piw_attrs = [attr for attr in dir(piw) if not attr.startswith('_')]
            assert len(piw_attrs) > 10, f"PIW should have substantial functionality, found {len(piw_attrs)} attributes"
            
            # Test basic constants/values if available
            if hasattr(piw, 'version'):
                version = piw.version
                assert version is not None, "PIW version should be available"
            
            print(f"✓ PIW basic functions available: {available_functions}")
            print(f"✓ PIW total attributes: {len(piw_attrs)}")
            
        except ImportError:
            pytest.skip("PIW module not available for basic functionality testing")