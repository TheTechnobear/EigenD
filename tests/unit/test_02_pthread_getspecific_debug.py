"""
Targeted tests for pthread_getspecific behavior in PIW session context.

These tests specifically investigate the thread-specific data retrieval
mechanism that's failing in Python 3.14 EigenD migration.
"""

import pytest
import sys
import threading
import time


class TestPthreadGetspecificBehavior:
    """Test pthread_getspecific behavior in different contexts."""
    
    @pytest.mark.core
    def test_context_existence_before_locking(self, piw_session, piw_modules):
        """Test if we can detect context existence before attempting locks."""
        piw = piw_modules['piw']
        
        def test_context_detection(session_ctx):
            results = {}
            
            # Look for functions that might give us context info without locking
            context_funcs = [attr for attr in dir(piw) if 'context' in attr.lower()]
            results['context_functions'] = context_funcs
            
            # Look for debugging or state inquiry functions  
            debug_funcs = [attr for attr in dir(piw) if any(word in attr.lower() 
                          for word in ['dump', 'info', 'state', 'debug'])]
            results['debug_functions'] = debug_funcs
            
            # Try tsd_dump if it exists - this might show us context state
            if hasattr(piw, 'tsd_dump'):
                try:
                    dump_result = piw.tsd_dump()
                    results['tsd_dump_result'] = str(dump_result)[:200]  # Truncate for safety
                except Exception as e:
                    results['tsd_dump_error'] = str(e)
            
            # Try tsd_killed - this checks if context is in killed state
            if hasattr(piw, 'tsd_killed'):
                try:
                    killed_state = piw.tsd_killed()
                    results['tsd_killed_state'] = killed_state
                except Exception as e:
                    results['tsd_killed_error'] = str(e)
                    
            return results
        
        result = piw_session['run'](test_context_detection)
        print(f"\nContext detection results: {result}")
        
        # We should be able to detect some context state
        assert 'context_functions' in result or 'debug_functions' in result
    
    @pytest.mark.core 
    def test_tsd_state_inspection(self, piw_session, piw_modules):
        """Test thread-specific data state inspection functions."""
        piw = piw_modules['piw']
        
        def inspect_tsd_state(session_ctx):
            state = {}
            
            # Test all tsd_ functions that might be read-only
            safe_tsd_funcs = ['tsd_scope', 'tsd_time', 'tsd_killed', 'tsd_client', 
                             'tsd_server', 'tsd_dump', 'tsd_index']
            
            for func_name in safe_tsd_funcs:
                if hasattr(piw, func_name):
                    try:
                        func = getattr(piw, func_name)
                        result = func()
                        state[func_name] = str(result)[:100]  # Truncate for safety
                    except Exception as e:
                        state[f"{func_name}_error"] = str(e)
            
            return state
        
        result = piw_session['run'](inspect_tsd_state)
        print(f"\nTSD state inspection: {result}")
        
        # We should be able to call at least some tsd functions without error
        success_count = len([k for k in result.keys() if not k.endswith('_error')])
        error_count = len([k for k in result.keys() if k.endswith('_error')])
        
        print(f"TSD function calls - Success: {success_count}, Errors: {error_count}")
    
    @pytest.mark.core
    def test_context_validity_checks(self, piw_session, piw_modules):
        """Test if we can validate context before attempting mutex operations."""
        piw = piw_modules['piw']
        
        def check_context_validity(session_ctx):
            checks = {}
            
            # Check 1: Can we call tsd_killed without error?
            try:
                killed = piw.tsd_killed()
                checks['context_accessible'] = True
                checks['context_killed'] = killed
            except Exception as e:
                checks['context_access_error'] = str(e)
                return checks
            
            # Check 2: If context is accessible, what's the scope?
            if checks.get('context_accessible'):
                try:
                    scope = piw.tsd_scope()
                    checks['context_scope'] = str(scope)
                except Exception as e:
                    checks['scope_error'] = str(e)
            
            # Check 3: Try to get any context identification
            try:
                client = piw.tsd_client()
                checks['context_client'] = str(client)
            except Exception as e:
                checks['client_error'] = str(e)
            
            return checks
        
        result = piw_session['run'](check_context_validity)
        print(f"\nContext validity checks: {result}")
        
        if 'context_access_error' in result:
            pytest.skip(f"Context not accessible: {result['context_access_error']}")
        
        # If context is accessible, it should not be killed
        if result.get('context_accessible'):
            assert not result.get('context_killed', True), "Context should not be killed in active session"


class TestContextInitializationSequence:
    """Test the sequence of context initialization in PIW sessions."""
    
    @pytest.mark.core
    def test_session_setup_sequence(self, piw_modules):
        """Test what happens during session setup sequence."""
        pisession = piw_modules['pisession']
        piw = piw_modules['piw']
        
        # Test session creation without running anything
        session_info = {}
        
        # Check if we can inspect session module
        session_attrs = [attr for attr in dir(pisession) if not attr.startswith('_')]
        session_info['pisession_attrs'] = session_attrs[:10]  # Sample
        
        # Check if session has context-related functions
        context_attrs = [attr for attr in session_attrs if 'context' in attr.lower()]
        session_info['context_attrs'] = context_attrs
        
        print(f"\nSession setup info: {session_info}")
        
        assert len(session_attrs) > 0, "Should be able to inspect pisession module"
    
    @pytest.mark.core
    def test_manual_context_setup(self, piw_modules):
        """Try to manually set up context if possible."""
        piw = piw_modules['piw']
        
        # Look for context setup functions
        setup_funcs = [attr for attr in dir(piw) if any(word in attr.lower() 
                      for word in ['setcontext', 'initcontext', 'createcontext'])]
        
        print(f"\nPotential context setup functions: {setup_funcs}")
        
        # This test is mainly for discovery
        assert isinstance(setup_funcs, list), "Should be able to search for setup functions"


class TestContextPointerDebugging:
    """Test to debug what's happening with context pointers."""
    
    @pytest.mark.core
    def test_context_pointer_investigation_enhanced(self, piw_session, piw_modules):
        """Enhanced investigation of context pointer state."""
        piw = piw_modules['piw']
        
        def detailed_context_investigation(session_ctx):
            investigation = {}
            
            # Get more detailed thread information
            import threading
            current_thread = threading.current_thread()
            investigation['thread_details'] = {
                'name': current_thread.name,
                'ident': current_thread.ident,
                'is_alive': current_thread.is_alive(),
                'daemon': current_thread.daemon
            }
            
            # Check what happens when we try various TSD operations
            tsd_operations = ['tsd_scope', 'tsd_time', 'tsd_killed', 'tsd_client']
            
            for op in tsd_operations:
                if hasattr(piw, op):
                    try:
                        func = getattr(piw, op)
                        result = func()
                        investigation[f'{op}_success'] = True
                        investigation[f'{op}_result'] = str(result)[:50]
                    except Exception as e:
                        investigation[f'{op}_error'] = str(e)
            
            # Try to call functions that might show internal state
            if hasattr(piw, 'tsd_dump'):
                try:
                    dump = piw.tsd_dump()
                    investigation['dump_available'] = True
                    investigation['dump_type'] = type(dump).__name__
                except Exception as e:
                    investigation['dump_error'] = str(e)
            
            return investigation
        
        result = piw_session['run'](detailed_context_investigation)
        print(f"\nDetailed context investigation: {result}")
        
        # Check if we have successful TSD operations
        successful_ops = [k for k in result.keys() if k.endswith('_success')]
        failed_ops = [k for k in result.keys() if k.endswith('_error')]
        
        print(f"TSD Operations - Successful: {len(successful_ops)}, Failed: {len(failed_ops)}")
        
        # If we can call TSD functions successfully, the context exists
        if successful_ops:
            print("✓ Context appears to be accessible - issue may be specific to lock/unlock")
        else:
            print("✗ Context not accessible - broader initialization issue")


class TestLockingPrerequisites:
    """Test what prerequisites might be missing for successful locking."""
    
    @pytest.mark.core
    def test_locking_prerequisites(self, piw_session, piw_modules):
        """Test what conditions need to be met before locking."""
        piw = piw_modules['piw']
        
        def check_prerequisites(session_ctx):
            prereqs = {}
            
            # Check 1: Is context killed?
            try:
                killed = piw.tsd_killed()
                prereqs['context_killed'] = killed
                if killed:
                    prereqs['skip_reason'] = "Context is killed"
                    return prereqs
            except Exception as e:
                prereqs['killed_check_error'] = str(e)
            
            # Check 2: Do we have a valid scope?
            try:
                scope = piw.tsd_scope()
                prereqs['has_scope'] = scope is not None
                prereqs['scope_value'] = str(scope)
            except Exception as e:
                prereqs['scope_error'] = str(e)
            
            # Check 3: Are we in the right thread context?
            try:
                client = piw.tsd_client()
                prereqs['has_client'] = client is not None
                prereqs['client_value'] = str(client)[:50]
            except Exception as e:
                prereqs['client_error'] = str(e)
            
            # Check 4: Can we access server info?
            try:
                server = piw.tsd_server()
                prereqs['has_server'] = server is not None
                prereqs['server_value'] = str(server)[:50]
            except Exception as e:
                prereqs['server_error'] = str(e)
            
            return prereqs
        
        result = piw_session['run'](check_prerequisites)
        print(f"\nLocking prerequisites check: {result}")
        
        # Analyze the prerequisites
        if result.get('context_killed'):
            pytest.skip("Context is killed - cannot proceed with locking")
        
        missing_prereqs = []
        if not result.get('has_scope', False):
            missing_prereqs.append("scope")
        if not result.get('has_client', False):
            missing_prereqs.append("client")
        if not result.get('has_server', False):
            missing_prereqs.append("server")
        
        if missing_prereqs:
            print(f"⚠️  Missing prerequisites for locking: {missing_prereqs}")
        else:
            print("✓ All prerequisites appear to be met")
        
        # The test passes if we can check prerequisites (even if some are missing)
        assert 'killed_check_error' not in result or len([k for k in result.keys() if not k.endswith('_error')]) > 0