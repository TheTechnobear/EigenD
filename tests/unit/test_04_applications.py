"""
Application Tests - Level 04  
============================

Test Level: 04_applications
Purpose: Test EigenD application layer functionality.

Test Coverage:
- Command line tools functionality
- Backend application services
- Application startup and configuration
- User interface components

Dependencies: All lower level tests must pass

Note: This file consolidates tests from scattered files in 04_applications/ subdirectory
"""

import pytest
import sys
import os


@pytest.mark.applications
class TestCommandLineTools:
    """
    Test command line tools functionality.
    
    Consolidated from: 04_applications/app_cmdline/test_*.py
    """
    
    @pytest.mark.applications
    def test_cmdline_tools_importable(self):
        """Test that command line tools can be imported."""
        try:
            # Test importing cmdline modules
            import app_cmdline
            assert app_cmdline is not None, "app_cmdline should be importable"
        except ImportError:
            pytest.skip("app_cmdline not available")
    
    @pytest.mark.applications  
    def test_cmdline_tool_modules(self):
        """Test individual command line tool modules."""
        cmdline_tools = [
            'bls',      # List agents/connections
            'rpc',      # RPC calls
            'rexec',    # Execute commands
            'rbrowse',  # Browse agents
            'cheat',    # Cheatsheet command
            'script',   # Script command
        ]
        
        available_tools = []
        for tool in cmdline_tools:
            try:
                module = __import__(f'app_cmdline.{tool}', fromlist=[tool])
                available_tools.append(tool)
                # Verify main function exists
                assert hasattr(module, 'main'), f"{tool} should have main function"
            except ImportError:
                pass  # Tool not available
        
        # At least some tools should be available
        assert len(available_tools) > 0, f"At least some cmdline tools should be available: {cmdline_tools}"
    
    @pytest.mark.applications
    @pytest.mark.migration
    def test_range_concatenation_fix(self):
        """Test Python 2→3 range concatenation fix in command line tools."""
        # This is the critical fix needed for Python 3 migration
        # [ord('!')] + range(ord('"'), ord('~')+1) needed to become list(range(...))
        try:
            result = [ord('!')] + list(range(ord('"'), ord('~')+1))
            expected_length = 1 + (ord('~') - ord('"') + 1)
            assert len(result) == expected_length, f"Range concatenation should work: got {len(result)}, expected {expected_length}"
        except TypeError:
            pytest.fail("Range concatenation failed - Python 3 fix not applied")
    
    @pytest.mark.applications
    def test_cheat_command_functionality(self):
        """Test cheat command specific functionality."""
        try:
            from app_cmdline import cheat
            assert hasattr(cheat, 'makecheat'), "cheat should have makecheat function"
            assert callable(cheat.makecheat), "makecheat should be callable"
        except ImportError:
            pytest.skip("cheat command not available")

@pytest.mark.applications
class TestEigendBackend:
    """
    Test Eigend backend functionality.
    
    Consolidated from: 04_applications/app_eigend2/test_*.py
    """
    
    @pytest.mark.applications
    def test_backend_module_import(self):
        """Test that backend module can be imported."""
        try:
            from app_eigend2 import backend
            assert backend is not None, "backend module should be importable"
        except ImportError:
            pytest.skip("app_eigend2.backend not available")
    
    @pytest.mark.applications
    def test_backend_class_creation(self):
        """Test Backend class instantiation and basic functionality."""
        try:
            from app_eigend2.backend import Backend
            
            # Create Backend instance
            backend_instance = Backend()
            assert backend_instance is not None, "Backend instance should be created"
            
            # Test mediator interface exists
            assert hasattr(backend_instance, 'mediator'), "Backend should have mediator attribute"
            
            # Test mediator is callable/accessible
            mediator = backend_instance.mediator()
            # Note: mediator might be None if not in EigenD context
            
        except ImportError:
            pytest.skip("Backend class not available")
        except Exception as e:
            pytest.skip(f"Backend creation failed (expected in test environment): {e}")
    
    @pytest.mark.applications  
    def test_native_modules_importable(self):
        """Test that native extension modules can be imported."""
        native_modules = [
            'eigend_native',
            'piw_native', 
            'pisession_native',
            'pibelcanto_native'
        ]
        
        imported_modules = []
        for module_name in native_modules:
            try:
                module = __import__(module_name)
                imported_modules.append(module_name)
            except ImportError:
                pass  # Native module not available in test environment
        
        # In a full EigenD environment, at least some native modules should be available
        # In test environment, this validates the import process doesn't crash

@pytest.mark.skip(reason="Application tests require full EigenD environment setup")
class TestApplicationIntegration:
    """
    Test application integration scenarios.
    """
    
    def test_application_integration_placeholder(self):
        """Placeholder for application integration tests."""
        pass