"""
Test suite for Python 3 migration threading issues.

These tests specifically target differences between Python 2.7 and Python 3.14
that could affect thread-specific data and context initialization in EigenD.
"""

import pytest
import sys
import threading
import time
from contextlib import contextmanager


class TestPython3ThreadingBehavior:
    """Test Python 3 specific threading behaviors that differ from Python 2.7."""
    
    @pytest.mark.foundation
    def test_python_version_specific_behavior(self):
        """Document the Python version we're testing against."""
        print(f"\nTesting Python {sys.version}")
        print(f"Thread implementation: {type(threading.current_thread())}")
        
        # Python 3 differences from Python 2.7:
        # - Different GIL behavior
        # - Different C API for thread state
        # - Different reference counting in threaded contexts
        assert sys.version_info >= (3, 14), "These tests are for Python 3.14+"
    
    @pytest.mark.foundation  
    def test_threading_local_behavior(self):
        """Test if threading.local behaves differently in Python 3."""
        local_data = threading.local()
        results = {}
        errors = []
        
        def worker(thread_id):
            try:
                # Set thread-local data
                local_data.value = f"thread_{thread_id}"
                time.sleep(0.01)  # Small delay to test persistence
                
                # Verify it persists
                assert hasattr(local_data, 'value'), "Thread local data lost"
                assert local_data.value == f"thread_{thread_id}", "Thread local data corrupted"
                results[thread_id] = "success"
            except Exception as e:
                errors.append(f"Thread {thread_id}: {e}")
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Threading.local errors: {errors}"
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"


class TestPiwContextInitialization:
    """Test PIW-specific context initialization issues."""
    
    @pytest.mark.core
    def test_piw_module_threading_state(self, piw_modules):
        """Test the initial threading state when PIW modules are loaded."""
        piw = piw_modules['piw']
        
        # Test what thread-specific functions are available
        assert hasattr(piw, 'tsd_lock'), "PIW should have tsd_lock function"
        assert hasattr(piw, 'tsd_unlock'), "PIW should have tsd_unlock function"
        
        # Check if there are any context-related functions we can inspect
        piw_attrs = [attr for attr in dir(piw) if 'context' in attr.lower() or 'tsd' in attr.lower()]
        print(f"\nPIW thread/context related attributes: {piw_attrs}")
    
    @pytest.mark.core
    def test_context_before_session(self, piw_modules):
        """Test what happens when we try to access context before proper session setup."""
        piw = piw_modules['piw']
        
        # Try to get current threading state without session
        try:
            # This might give us insight into the current thread context state
            # without actually trying to lock (which causes the assertion failure)
            
            # Check if we can introspect the context without operations
            context_info = {}
            
            # Look for any debugging or introspection functions
            debug_attrs = [attr for attr in dir(piw) if any(word in attr.lower() 
                          for word in ['debug', 'info', 'state', 'current'])]
            context_info['debug_attrs'] = debug_attrs
            
            print(f"\nContext state before session: {context_info}")
            
        except Exception as e:
            # This might give us clues about the state
            print(f"Exception accessing context before session: {e}")
    
    @pytest.mark.core
    def test_session_context_step_by_step(self, piw_session, piw_modules):
        """Test each step of session context setup to find where it fails."""
        piw = piw_modules['piw']
        
        def test_context_stages(session_ctx):
            stages = {}
            
            # Stage 1: Just check if we're in a session
            stages['in_session'] = True
            
            # Stage 2: Check if any context inspection is possible
            try:
                # Try to access thread-specific functions without locking
                stages['tsd_functions_accessible'] = hasattr(piw, 'tsd_lock')
            except Exception as e:
                stages['tsd_access_error'] = str(e)
            
            # Stage 3: Try to get thread ID or similar safe operations
            try:
                import threading
                stages['python_thread_id'] = threading.get_ident()
                stages['python_thread_name'] = threading.current_thread().name
            except Exception as e:
                stages['python_thread_error'] = str(e)
            
            return stages
        
        result = piw_session['run'](test_context_stages)
        print(f"\nSession context stages: {result}")
        
        # Verify we can at least inspect the session state
        assert result['in_session'], "Should be able to detect session context"
        assert 'python_thread_id' in result, "Should be able to get Python thread ID"


class TestThreadSpecificDataProbing:
    """Test thread-specific data mechanisms to isolate the pthread issue."""
    
    @pytest.mark.core
    def test_picross_thread_mechanisms(self, piw_modules):
        """Test the picross threading layer directly."""
        try:
            import picross
            
            # Test basic mutex creation (this worked before)
            mutex = picross.mutex()
            
            # Test if there are thread-specific data functions
            tsd_attrs = [attr for attr in dir(picross) if 'tsd' in attr.lower()]
            thread_attrs = [attr for attr in dir(picross) if 'thread' in attr.lower()]
            
            info = {
                'mutex_created': True,
                'tsd_attributes': tsd_attrs,
                'thread_attributes': thread_attrs
            }
            
            print(f"\nPicross threading capabilities: {info}")
            
        except Exception as e:
            pytest.fail(f"Failed to test picross threading: {e}")
    
    @pytest.mark.core
    def test_context_pointer_investigation(self, piw_session, piw_modules):
        """Try to investigate what happens to context pointers."""
        piw = piw_modules['piw']
        
        def investigate_context(session_ctx):
            investigation = {}
            
            try:
                # Try to get some insight into the internal state
                # without calling lock/unlock
                
                # Check if we can access any debug or state information
                piw_internals = [attr for attr in dir(piw) 
                               if not attr.startswith('_') and 
                               callable(getattr(piw, attr))]
                investigation['piw_callable_functions'] = len(piw_internals)
                investigation['sample_functions'] = piw_internals[:10]
                
                # Try to get some basic PIW state
                import threading
                investigation['current_thread'] = threading.current_thread().name
                
                return investigation
                
            except Exception as e:
                investigation['error'] = str(e)
                return investigation
        
        result = piw_session['run'](investigate_context)
        print(f"\nContext investigation: {result}")
        
        assert 'piw_callable_functions' in result, "Should be able to inspect PIW functions"


class TestGradualLockingApproach:
    """Test progressively more complex locking scenarios to find the breaking point."""
    
    @pytest.mark.core
    def test_simple_picross_locking(self, piw_modules):
        """Test if picross mutexes work outside of PIW session context."""
        try:
            import picross
            
            # Test multiple mutexes and complex locking patterns
            mutexes = []
            
            for i in range(3):
                mutex = picross.mutex()
                mutexes.append(mutex)
                
                # Test immediate lock/unlock
                mutex.lock()
                mutex.unlock()
                
                # Test quick succession
                for j in range(3):
                    mutex.lock()
                    mutex.unlock()
            
            print(f"\nSuccessfully tested {len(mutexes)} picross mutexes")
            
        except Exception as e:
            pytest.fail(f"Picross mutex test failed: {e}")
    
    @pytest.mark.core
    def test_threading_with_picross_mutexes(self, piw_modules):
        """Test picross mutexes across multiple Python threads."""
        import picross
        import threading
        import time
        
        shared_mutex = picross.mutex()
        results = {}
        errors = []
        
        def thread_worker(thread_id):
            try:
                for i in range(3):
                    shared_mutex.lock()
                    time.sleep(0.001)  # Hold lock briefly
                    shared_mutex.unlock()
                    
                results[thread_id] = "success"
            except Exception as e:
                errors.append(f"Thread {thread_id}: {e}")
        
        threads = []
        for i in range(3):
            t = threading.Thread(target=thread_worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join(timeout=5)
        
        assert len(errors) == 0, f"Thread mutex errors: {errors}"
        assert len(results) == 3, f"Expected 3 successful threads, got {len(results)}"
        
        print(f"\nSuccessfully tested picross mutex across {len(threads)} threads")


@contextmanager
def session_introspection(piw_session):
    """Context manager to safely introspect session state."""
    try:
        yield piw_session
    except Exception as e:
        print(f"Session introspection error: {e}")
        raise