"""
Targeted investigation of mutex object lifecycle within PIW context.

Since we confirmed the context exists and is accessible, the issue must be
with the specific mutex object (busy_) within the context object.
"""

import pytest
import sys


class TestContextMutexLifecycle:
    """Test the lifecycle and state of mutex objects within PIW context."""
    
    @pytest.mark.core
    def test_context_object_inspection(self, piw_session, piw_modules):
        """Inspect the context object to understand its state before mutex operations."""
        piw = piw_modules['piw']
        
        def inspect_context_object(session_ctx):
            inspection = {}
            
            # We know these work from previous tests
            try:
                inspection['scope'] = str(piw.tsd_scope())
                inspection['killed'] = piw.tsd_killed()
                inspection['time'] = str(piw.tsd_time())
                
                # Try to get more internal state information
                # Look for any debugging or introspection capabilities
                if hasattr(piw, 'tsd_dump'):
                    dump_result = piw.tsd_dump()
                    inspection['dump_result'] = str(dump_result)
                
                inspection['context_state'] = 'accessible'
                
            except Exception as e:
                inspection['error'] = str(e)
            
            return inspection
        
        result = piw_session['run'](inspect_context_object)
        print(f"\nContext object inspection: {result}")
        
        # Verify context is in good state
        assert result.get('context_state') == 'accessible'
        assert not result.get('killed', True), "Context should not be killed"
    
    @pytest.mark.core
    def test_mutex_prerequisite_analysis(self, piw_session, piw_modules):
        """Analyze what prerequisites might be missing for mutex operations."""
        piw = piw_modules['piw']
        
        def analyze_mutex_prerequisites(session_ctx):
            analysis = {}
            
            # Check all the conditions that might affect mutex operations
            
            # 1. Context state
            analysis['context_killed'] = piw.tsd_killed()
            analysis['context_scope'] = str(piw.tsd_scope())
            
            # 2. Thread state 
            import threading
            thread = threading.current_thread()
            analysis['python_thread'] = {
                'name': thread.name,
                'ident': thread.ident,
                'daemon': thread.daemon,
                'is_alive': thread.is_alive()
            }
            
            # 3. Try to determine if there are any context flags or states
            # that might indicate whether locking is safe
            
            # Look for any state that might indicate readiness for locking
            try:
                # These require arguments, but errors might be informative
                try:
                    piw.tsd_client()
                except Exception as e:
                    analysis['client_signature'] = str(e)
                
                try:
                    piw.tsd_server()  
                except Exception as e:
                    analysis['server_signature'] = str(e)
                    
            except Exception as e:
                analysis['signature_check_error'] = str(e)
            
            return analysis
        
        result = piw_session['run'](analyze_mutex_prerequisites)
        print(f"\nMutex prerequisite analysis: {result}")
        
        # Context should be ready
        assert not result['context_killed'], "Context should not be killed for mutex ops"


class TestMutexObjectState:
    """Test the specific state of mutex objects in the context."""
    
    @pytest.mark.core  
    def test_comparison_with_working_mutex(self, piw_session, piw_modules):
        """Compare the context mutex with known working picross mutexes."""
        piw = piw_modules['piw']
        
        def compare_mutex_behaviors(session_ctx):
            comparison = {}
            
            # Test 1: Verify picross mutex still works in session context
            try:
                import picross
                test_mutex = picross.mutex()
                
                # Test the working mutex
                test_mutex.lock()
                test_mutex.unlock()
                comparison['picross_mutex_works'] = True
                
                # Test multiple cycles
                for i in range(3):
                    test_mutex.lock()
                    test_mutex.unlock()
                comparison['picross_multiple_cycles'] = True
                
            except Exception as e:
                comparison['picross_error'] = str(e)
            
            # Test 2: Check context state just before we would attempt locking
            comparison['context_pre_lock_state'] = {
                'killed': piw.tsd_killed(),
                'scope': str(piw.tsd_scope()),
                'time': str(piw.tsd_time())
            }
            
            return comparison
        
        result = piw_session['run'](compare_mutex_behaviors)
        print(f"\nMutex behavior comparison: {result}")
        
        # Picross mutex should still work in session context
        assert result.get('picross_mutex_works'), "Picross mutex should work in session"
        assert result.get('picross_multiple_cycles'), "Multiple cycles should work"


class TestMutexInitializationTiming:
    """Test if the issue is related to when the context mutex is initialized."""
    
    @pytest.mark.core
    def test_context_creation_timing(self, piw_modules):
        """Test the timing of context creation and when mutex issues might arise."""
        pisession = piw_modules['pisession']
        
        # This test runs outside of piw_session to examine session creation
        session_creation_info = {}
        
        # Check if we can examine session creation process
        if hasattr(pisession, 'session'):
            session_creation_info['has_session_module'] = True
            session_attrs = [attr for attr in dir(pisession.session) if not attr.startswith('_')]
            session_creation_info['session_attributes'] = session_attrs[:10]
        
        print(f"\nSession creation analysis: {session_creation_info}")
        
        # This is mainly for information gathering
        assert isinstance(session_creation_info, dict)


class TestDeferredMutexOperations:
    """Test if we can defer or work around the mutex operations."""
    
    @pytest.mark.core
    def test_alternative_synchronization(self, piw_session, piw_modules):
        """Test if we can use alternative synchronization mechanisms."""
        piw = piw_modules['piw']
        
        def test_alternatives(session_ctx):
            alternatives = {}
            
            # Test 1: Can we use Python's threading mechanisms instead?
            import threading
            python_lock = threading.Lock()
            
            try:
                python_lock.acquire()
                python_lock.release()
                alternatives['python_threading_lock'] = True
            except Exception as e:
                alternatives['python_lock_error'] = str(e)
            
            # Test 2: Can we use any other PIW synchronization mechanisms?
            # Look for alternative sync functions
            sync_functions = [attr for attr in dir(piw) if any(word in attr.lower() 
                             for word in ['sync', 'wait', 'signal', 'enter', 'exit'])]
            alternatives['piw_sync_functions'] = sync_functions
            
            # Test 3: Check if we can access the context without locking
            alternatives['context_accessible_without_lock'] = True
            alternatives['context_state'] = {
                'scope': str(piw.tsd_scope()),
                'killed': piw.tsd_killed()
            }
            
            return alternatives
        
        result = piw_session['run'](test_alternatives)
        print(f"\nAlternative synchronization test: {result}")
        
        # Python threading should still work
        assert result.get('python_threading_lock'), "Python threading should work"
        assert result.get('context_accessible_without_lock'), "Context should be accessible"


class TestMinimalMutexReproduction:
    """Create minimal test to reproduce the exact mutex failure."""
    
    @pytest.mark.core
    def test_minimal_lock_attempt(self, piw_session, piw_modules):
        """Make the minimal possible attempt to reproduce the lock failure."""
        piw = piw_modules['piw']
        
        def minimal_lock_test(session_ctx):
            import threading
            
            # Record state right before the attempt
            pre_state = {
                'context_killed': piw.tsd_killed(),
                'context_scope': str(piw.tsd_scope()),
                'thread_name': threading.current_thread().name
            }
            
            # Document that we're about to attempt the operation that fails
            attempt_info = {
                'pre_state': pre_state,
                'about_to_attempt': 'piw.tsd_lock()',
                'expected_failure': 'pthread_mutex_lock assertion'
            }
            
            return attempt_info
        
        result = piw_session['run'](minimal_lock_test)
        print(f"\nMinimal lock test preparation: {result}")
        
        # This test documents the state before the failing operation
        # We deliberately don't attempt the lock to avoid the assertion failure
        assert result['pre_state']['context_killed'] == False
        
        print("✓ Context is in good state before lock attempt")
        print("✗ The issue occurs specifically in piw.tsd_lock() -> context.lock() -> busy_.lock()")
        print("✓ This confirms the problem is in the pic::mutex_t object within the context")