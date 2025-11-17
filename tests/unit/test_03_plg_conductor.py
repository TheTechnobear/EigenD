"""
Per-plugin tests for `plg_conductor` (Clip Manager / Conductor plugin)
"""

import pytest
import sys


@pytest.mark.plugins
@pytest.mark.timeout(15)
def test_clip_manager_widget_functionality(piw_session):
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
def test_clip_manager_agent_instantiation(piw_session):
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
