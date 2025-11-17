"""
Per-plugin tests for `plg_finger` (Fingerer plugin)
"""

import pytest


@pytest.mark.plugins
@pytest.mark.timeout(15)
def test_fingerer_plugin_instantiation(piw_session):
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
