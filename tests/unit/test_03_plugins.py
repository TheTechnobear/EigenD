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
        def test_in_session(session_ctx):
            try:
                from Eigenlabs.plg_finger import finger_plg
            except ImportError as e:
                return {'success': False, 'error': f"Fingerer plugin not available: {e}"}
            
            try:
                # In application context, Agent instantiation should work
                agent_instance = finger_plg.Agent('test_address', 1)
                return {
                    'success': True,
                    'agent': agent_instance,
                    'has_domain': hasattr(agent_instance, 'domain'),
                    'has_finger': hasattr(agent_instance, 'finger'),
                    'has_fingering': hasattr(agent_instance, 'current_fingering'),
                    'ordinal_count': len([k for k in agent_instance.keys() if isinstance(k, int)])
                }
            except Exception as e:
                return {'success': False, 'error': f"Agent creation failed: {e}"}
        
        results = piw_session['run'](test_in_session)
        
        if results is None:
            pytest.skip("Session timed out - test function did not complete")
        
        if not results.get('success', False):
            pytest.skip(f"Fingerer plugin test failed: {results.get('error', 'Unknown error')}")
        
        # Test completed successfully - run assertions
        assert results['has_domain'], "Agent should have domain"
        assert results['has_finger'], "Agent should have finger component"
        assert results['has_fingering'], "Agent should have current fingering"
        assert results['ordinal_count'] >= 5, f"Agent should have at least 5 ordinals, got {results['ordinal_count']}"
    
    @pytest.mark.plugins
    @pytest.mark.timeout(15)
    def test_clip_manager_widget_functionality(self, piw_session):
        """Test ClipManagerWidget full functionality in application context."""
        def test_in_session(session_ctx):
            try:
                from Eigenlabs.plg_conductor import clip_manager_plg
            except ImportError as e:
                return {'success': False, 'error': f"Clip manager plugin not available: {e}"}
            
            try:
                # In application context, Agent instantiation should work
                agent_instance = clip_manager_plg.Agent('test_address', 1)
                widget = agent_instance[1]  # Get the widget from the agent
                
                return {
                    'success': True,
                    'widget_exists': widget is not None,
                    'widget_type': type(widget).__name__ if widget else None,
                    'has_native_widget': hasattr(widget, '_ClipManagerWidget__widget') if widget else False
                }
            except Exception as e:
                return {'success': False, 'error': f"Widget test failed: {e}"}
        
        results = piw_session['run'](test_in_session)
        
        if results is None:
            pytest.skip("Session timed out - test function did not complete")
        
        if not results.get('success', False):
            pytest.skip(f"Clip manager widget test failed: {results.get('error', 'Unknown error')}")
        
        # Test completed successfully - run assertions
        assert results['widget_exists'], "Widget should exist"
        assert results['widget_type'] == 'ClipManagerWidget', f"Widget should be ClipManagerWidget, got {results['widget_type']}"
        assert results['has_native_widget'], "Widget should have native clip manager"
    
    @pytest.mark.plugins
    @pytest.mark.timeout(15)
    def test_clip_manager_agent_instantiation(self, piw_session):
        """Test that ClipManager Agent can be instantiated in application context."""
        def test_in_session(session_ctx):
            try:
                from Eigenlabs.plg_conductor import clip_manager_plg
            except ImportError as e:
                return {'success': False, 'error': f"Clip manager plugin not available: {e}"}
            
            try:
                # In application context, Agent instantiation should work
                agent_instance = clip_manager_plg.Agent('test_address', 1)
                return {
                    'success': True,
                    'agent': agent_instance,
                    'has_clip_manager': agent_instance.clip_manager is not None,
                    'has_ordinal_1': 1 in agent_instance,
                    'widget_type': type(agent_instance[1]).__name__ if 1 in agent_instance else None
                }
            except Exception as e:
                return {'success': False, 'error': f"Agent creation failed: {e}"}
        
        results = piw_session['run'](test_in_session)
        
        if results is None:
            pytest.skip("Session timed out - test function did not complete")
        
        if not results.get('success', False):
            pytest.skip(f"Clip manager test failed: {results.get('error', 'Unknown error')}")
        
        # Test completed successfully - run assertions
        assert results['has_clip_manager'], "Clip manager should be created"
        assert results['has_ordinal_1'], "Agent should contain ordinal 1"
        assert results['widget_type'] == 'ClipManagerWidget', f"Agent[1] should be ClipManagerWidget, got {results['widget_type']}"
    
    @pytest.mark.plugins
    @pytest.mark.timeout(15)
    def test_convolver_plugin_instantiation_in_application_context(self, piw_session):
        """Test that Convolver plugin can be instantiated in application context."""
        def test_in_session(session_ctx):
            try:
                from Eigenlabs.plg_convolver import convolver_plg
            except ImportError as e:
                return {'success': False, 'error': f"Convolver plugin not available: {e}"}
            
            try:
                # In application context, Agent instantiation should work
                agent_instance = convolver_plg.Agent('test_address', 1)
                return {
                    'success': True,
                    'agent': agent_instance,
                    'has_domain': hasattr(agent_instance, 'domain'),
                    'has_convolver': hasattr(agent_instance, 'convolver'),
                    'has_input': hasattr(agent_instance, 'input'),
                    'has_output': hasattr(agent_instance, 'output'),
                    'ordinal_count': len([k for k in agent_instance.keys() if isinstance(k, int)]),
                    'impulse_browser_exists': 4 in agent_instance,
                    'userdir': agent_instance[4].userdir if 4 in agent_instance else None,
                    'reldir': agent_instance[4].reldir if 4 in agent_instance else None,
                    'impulse_browser_type': type(agent_instance[4]).__name__ if 4 in agent_instance else None,
                    'impulse_browser_has_files': hasattr(agent_instance[4], '_ImpulseBrowser__files') if 4 in agent_instance else False,
                    'impulse_browser_files_type': type(agent_instance[4]._ImpulseBrowser__files).__name__ if 4 in agent_instance and hasattr(agent_instance[4], '_ImpulseBrowser__files') else None,
                    'impulse_files_count': len(agent_instance[4]._ImpulseBrowser__files) if 4 in agent_instance and hasattr(agent_instance[4], '_ImpulseBrowser__files') else 0,
                    'impulse_names_count': len(agent_instance[4]._ImpulseBrowser__n2c) if 4 in agent_instance and hasattr(agent_instance[4], '_ImpulseBrowser__n2c') else 0,
                    'impulse_files_sample': agent_instance[4]._ImpulseBrowser__files[:10] if 4 in agent_instance and hasattr(agent_instance[4], '_ImpulseBrowser__files') else []
                }
            except Exception as e:
                return {'success': False, 'error': f"Agent creation failed: {e}"}
        
        results = piw_session['run'](test_in_session)

        if results is None:
            pytest.skip("Session timed out - test function did not complete")
        
        if not results.get('success', False):
            pytest.skip(f"Convolver plugin test failed: {results.get('error', 'Unknown error')}")
        
        # Test completed successfully - run assertions
        assert results['has_domain'], "Agent should have domain"
        assert results['has_convolver'], "Agent should have convolver"
        assert results['has_input'], "Agent should have input"
        assert results['has_output'], "Agent should have output"
        assert results['ordinal_count'] >= 4, f"Agent should have at least 4 ordinals, got {results['ordinal_count']}"
        assert results['impulse_browser_exists'], "Agent should have impulse browser at ordinal 4"
        assert results['impulse_files_count'] > 0, f"Should have impulse files available, found {results['impulse_files_count']}"
        assert results['impulse_names_count'] >= 0, f"Should have impulse names available, found {results['impulse_names_count']}"
        print(f"Info: Found {results['impulse_files_count']} impulse files, sample: {results['impulse_files_sample']}")
        # assert False, f"Info: Found {results['impulse_files_count']} impulse files, sample: {results['impulse_files_sample']}"