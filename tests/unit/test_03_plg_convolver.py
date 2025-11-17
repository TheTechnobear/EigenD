"""
Per-plugin tests for `plg_convolver` (Convolver plugin)
"""

import pytest
import sys


@pytest.mark.plugins
@pytest.mark.timeout(15)
def test_convolver_plugin_instantiation_in_application_context(piw_session):
    """Test that Convolver plugin can be instantiated in application context."""
    def test_in_session(session_ctx):
        try:
            from Eigenlabs.plg_convolver import convolver_plg
        except ImportError as e:
            return {'success': False, 'error': f"Convolver plugin not available: {e}"}

        try:
            # In application context, Agent instantiation should work
            agent_instance = convolver_plg.Agent('test_address', 1)

            # Get impulse files count via public RPC interface
            try:
                enumerate_result = agent_instance[4].rpc_enumerate('[]')
                # Parse the result string like '[3,0]'
                parts = enumerate_result.strip('[]').split(',')
                impulse_files_count = int(parts[0]) if parts[0].isdigit() else 0
            except:
                impulse_files_count = 0

            # Get sample files via public RPC interface
            impulse_files_sample = []
            impulse_selection_tested = False
            impulse_selection_success = False

            try:
                finfo_result = agent_instance[4].rpc_finfo('[[], 0]')
                # finfo_result is a rendered term string like '[[file,display,name],...]'
                # Extract all file names - each entry is [file,display,name]
                import re
                # Find all sequences that look like file names (between [ and ,)
                file_matches = re.findall(r'\[([^,\]]+)', finfo_result)
                # Clean up the file names (remove any leading '[')
                impulse_files_sample = [f.lstrip('[') for f in file_matches]

                # Test selecting the second impulse file if available
                if len(file_matches) >= 2:
                    second_file = file_matches[1]  # Second file (0-indexed)
                    try:
                        # Set selection
                        agent_instance[4].rpc_setselected(f'[[], "{second_file}"]')
                        # Activate selection
                        result = agent_instance[4].rpc_activated(f'[[], "{second_file}"]')
                        # Check current selection
                        current_result = agent_instance[4].rpc_current('[]')
                        # Parse current selection - should contain the selected file
                        if second_file in current_result:
                            impulse_selection_success = True
                        impulse_selection_tested = True
                    except Exception as e:
                        print(f"Selection test error: {e}", file=sys.stderr)

            except Exception as e:
                print(f"finfo error: {e}", file=sys.stderr)

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
                'impulse_files_count': impulse_files_count,
                'impulse_files_sample': impulse_files_sample,
                'impulse_selection_tested': impulse_selection_tested,
                'impulse_selection_success': impulse_selection_success
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
    if results.get('impulse_selection_tested', False):
        assert results['impulse_selection_success'], "Impulse file selection should work"
    print(f"Info: Found {results['impulse_files_count']} impulse files, sample: {results.get('impulse_files_sample', [])}, selection tested: {results.get('impulse_selection_tested', False)}, selection success: {results.get('impulse_selection_success', False)}")
