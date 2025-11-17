"""
Plugin Tests - Level 03
=======================

Test Level: 03_plugins
Purpose: Test EigenD plugin system functionality.

Test Coverage:
- Plugin loading and initialization
- Agent lifecycle management
- Plugin communication and RPC
- Plugin configuration and setup

Dependencies: test_00_foundation.py, test_01_core_piw.py must pass

Note: This file consolidates tests from scattered files in 03_plugins/ subdirectory
"""

import pytest
import sys
import os
import gc
import time

@pytest.mark.plugins
class TestPluginSystemBasics:
    """
    Test basic plugin system functionality.
    """
    
    @pytest.mark.plugins 
    def test_plugin_infrastructure_imports(self):
        """Test that plugin infrastructure modules can be imported."""
        try:
            # Test importing core plugin infrastructure
            import pi.agent
            import pi.atom
            import pi.bundles
            import pi.domain
            import piw
            
            assert hasattr(pi.agent, 'Agent'), "Agent class should be available"
            assert hasattr(pi.atom, 'Atom'), "Atom class should be available" 
            assert hasattr(pi.bundles, 'Output'), "Output bundle should be available"
            assert hasattr(pi.domain, 'Bool'), "Bool domain should be available"
            
            # Test PIW module imports (but don't create objects without session)
            assert hasattr(piw, 'clockdomain_ctl'), "PIW clockdomain_ctl should be available"
            assert hasattr(piw, 'makestring'), "PIW makestring should be available"
            assert hasattr(piw, 'makebool'), "PIW makebool should be available"
            
            print("Plugin infrastructure imports successful")
            
        except ImportError as e:
            pytest.fail(f"Failed to import plugin infrastructure: {e}")
    
    def test_session_infrastructure_available(self):
        """Test that session infrastructure is available for plugins."""
        try:
            import pisession.session
            
            # Test that run_session function exists
            assert hasattr(pisession.session, 'run_session'), "run_session should be available"
            assert callable(pisession.session.run_session), "run_session should be callable"
            
            print("Session infrastructure available")
            
        except ImportError as e:
            pytest.skip(f"Session infrastructure not available: {e}")
    
    @pytest.mark.skip(reason="PIW object creation requires session context")
    def test_plugin_base_functionality(self):
        """Test plugin base functionality without specific plugin."""
        try:
            import pi.agent
            import pi.atom  
            import piw
            
            # Test basic agent creation pattern (without actual plugin)
            # This validates the core agent infrastructure
            
            # Test clock domain creation (required for all plugins)
            domain = piw.clockdomain_ctl()
            domain.set_source(piw.makestring('*', 0))
            
            # Test basic PIW data creation (used by all plugins)
            bool_data = piw.makebool(True, 0)
            string_data = piw.makestring('test', 0)
            
            assert bool_data is not None, "Boolean data creation should work"
            assert string_data is not None, "String data creation should work"
            
            print("Plugin base functionality validated")
            
        except Exception as e:
            pytest.fail(f"Plugin base functionality test failed: {e}")

@pytest.mark.plugins
class TestPluginModuleStructure:
    """
    Test plugin module structure and availability.
    """
    
    def test_plugin_directories_exist(self):
        """Test that plugin directories are available."""
        import os
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent
        
        # Check for some key plugin directories
        plugin_dirs = [
            'plg_simple',
            'plg_audio', 
            'plg_midi',
            'plg_language'
        ]
        
        found_plugins = []
        for plugin_dir in plugin_dirs:
            plugin_path = project_root / plugin_dir
            if plugin_path.exists() and plugin_path.is_dir():
                found_plugins.append(plugin_dir)
                
        assert len(found_plugins) > 0, f"Should find at least some plugin directories"
        print(f"Found plugin directories: {found_plugins}")
    
    def test_plugin_module_imports(self):
        """Test basic plugin module imports (without instantiation)."""
        try:
            # Test that we can at least import plugin package directories
            plugin_packages = ['plg_simple', 'plg_audio', 'plg_midi']
            
            importable_plugins = []
            for pkg in plugin_packages:
                try:
                    __import__(pkg)
                    importable_plugins.append(pkg)
                except ImportError as e:
                    # Expected for some plugins that need build artifacts
                    pass
                    
            # We should be able to import at least the package directories
            assert len(importable_plugins) > 0, "Should be able to import some plugin packages"
            print(f"Successfully imported plugin packages: {importable_plugins}")
            
        except Exception as e:
            pytest.fail(f"Plugin module import test failed: {e}")
    
    @pytest.mark.skip(reason="Agent creation requires session context and version modules")
    def test_mock_plugin_agent_creation(self):
        """Test creating a mock plugin agent to validate the pattern."""
        try:
            import pi.agent
            import pi.atom
            import piw
            
            # Create a minimal mock agent following the plugin pattern
            class MockAgent(pi.agent.Agent):
                def __init__(self, address, ordinal):
                    # Mock version for testing
                    mock_version = type('MockVersion', (), {'version': '1.0.0'})()
                    
                    super().__init__(signature=mock_version, names='mock_plugin', ordinal=ordinal)
                    
                    # Add basic plugin structure
                    self.domain = piw.clockdomain_ctl()
                    self.domain.set_source(piw.makestring('*', 0))
                    
                    # Add basic atoms (typical plugin pattern)
                    self[2] = pi.atom.Atom(names='outputs')
                    self[3] = pi.atom.Atom(names='control')
            
            # Test agent creation
            agent = MockAgent('test_mock', 1)
            
            assert agent is not None, "Mock agent should be created"
            assert hasattr(agent, 'domain'), "Agent should have domain"
            assert 2 in agent, "Agent should have outputs atom"
            assert 3 in agent, "Agent should have control atom"
            
            print("Mock plugin agent creation successful")
            
        except Exception as e:
            pytest.fail(f"Mock plugin agent creation failed: {e}")
    
    def test_plugin_class_patterns(self):
        """Test that plugin classes follow expected patterns without instantiation."""
        import os
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent
        
        # Look for plugin files that we can analyze
        plugin_files = []
        for plugin_dir in ['plg_simple', 'plg_audio', 'plg_midi']:
            plugin_path = project_root / plugin_dir
            if plugin_path.exists():
                for py_file in plugin_path.glob('*_plg.py'):
                    plugin_files.append(py_file)
        
        assert len(plugin_files) > 0, "Should find some plugin files to analyze"
        
        # Analyze plugin file structure
        agent_patterns = []
        for plugin_file in plugin_files[:3]:  # Just check first few
            try:
                content = plugin_file.read_text()
                if 'class Agent(' in content and 'agent.Agent' in content:
                    agent_patterns.append(plugin_file.name)
            except:
                pass
                
        assert len(agent_patterns) > 0, "Should find plugin files with Agent classes"
        print(f"Found plugin Agent patterns in: {agent_patterns}")
    
    @pytest.mark.plugins
    @pytest.mark.timeout(15)
    def test_fingerer_plugin_instantiation(self, piw_session):
        """Test that Fingerer plugin can be instantiated in application context."""
        pytest.skip("Plugin-specific tests moved to separate per-plugin test files")
    
    @pytest.mark.plugins
    @pytest.mark.timeout(15)
    def test_clip_manager_widget_functionality(self, piw_session):
        """Test ClipManagerWidget full functionality in application context."""
        pytest.skip("Plugin-specific tests moved to separate per-plugin test files")
    
    @pytest.mark.plugins
    @pytest.mark.timeout(15)
    def test_clip_manager_agent_instantiation(self, piw_session):
        """Test that ClipManager Agent can be instantiated in application context."""
        pytest.skip("Plugin-specific tests moved to separate per-plugin test files")
    
    @pytest.mark.plugins
    @pytest.mark.timeout(15)
    def test_convolver_plugin_instantiation_in_application_context(self, piw_session):
        """Test that Convolver plugin can be instantiated in application context."""
        pytest.skip("Plugin-specific tests moved to separate per-plugin test files")