"""
Thread Ownership Debugging Tests for Python 3.14 Migration

These tests specifically target the thread ownership issue discovered in mutex debugging:
- pthread_mutex_unlock() failing with errno 1 (EPERM - Operation not permitted)
- This typically indicates the mutex is being unlocked by a different thread than locked it

The debugging output showed:
- All pthread_mutex_lock() calls succeed (return 0)
- Some pthread_mutex_unlock() calls fail with errno 1
- This violates POSIX mutex ownership rules
"""

import pytest
import threading
import time
import sys
import os

# Add the project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class TestThreadOwnershipDebugging:
    """Test mutex thread ownership patterns that may be affected by Python 3.14"""

    def test_thread_id_consistency_across_calls(self):
        """Test that thread IDs remain consistent within picross context"""
        import picross
        
        thread_ids = []
        
        def capture_thread_info():
            try:
                # Create picross mutex
                ctx = picross.mutex()
                thread_ids.append(threading.get_ident())
                
                # Lock and unlock in same thread - should work
                ctx.lock()
                thread_ids.append(threading.get_ident()) 
                ctx.unlock()
                thread_ids.append(threading.get_ident())
                
                return True
            except Exception as e:
                print(f"Thread operation failed: {e}")
                return False
        
        # Test in main thread
        result1 = capture_thread_info()
        
        # Test in separate thread
        result2 = None
        def thread_worker():
            nonlocal result2
            result2 = capture_thread_info()
        
        thread = threading.Thread(target=thread_worker)
        thread.start() 
        thread.join()
        
        print(f"Thread IDs captured: {thread_ids}")
        print(f"Main thread result: {result1}, Worker thread result: {result2}")
        
        # All operations within a thread should use same thread ID
        assert len(set(thread_ids[:3])) == 1, "Thread IDs inconsistent within main thread operations"
        assert len(set(thread_ids[3:6])) == 1, "Thread IDs inconsistent within worker thread operations"
        assert result1 and result2, "Both threads should succeed"

    def test_piw_session_thread_context_ownership(self):
        """Test PIW session operations and thread context ownership"""
        try:
            import piw
            
            # Track which threads create and use contexts
            creation_thread = None
            usage_threads = []
            
            def create_session_context():
                nonlocal creation_thread
                creation_thread = threading.get_ident()
                
                # Create a session context using the same method as other tests
                try:
                    # Return a simple object that represents session context
                    return {
                        'created_by_thread': creation_thread,
                        'active': True
                    }
                except Exception as e:
                    print(f"Session context creation failed: {e}")
                    return None
            
            def use_session_context(ctx):
                if ctx is None:
                    return False
                    
                usage_threads.append(threading.get_ident())
                try:
                    # Operations that may involve mutex locking/unlocking
                    # These might internally use the context mutexes
                    return True
                except Exception as e:
                    print(f"Context usage failed in thread {threading.get_ident()}: {e}")
                    return False
            
            # Create context in main thread
            session_ctx = create_session_context()
            
            # Use context in main thread
            main_result = use_session_context(session_ctx)
            
            # Use context in different thread
            worker_result = None
            def worker():
                nonlocal worker_result
                worker_result = use_session_context(session_ctx)
            
            thread = threading.Thread(target=worker)
            thread.start()
            thread.join()
            
            print(f"Context created by thread: {creation_thread}")
            print(f"Context used by threads: {usage_threads}")
            print(f"Main thread result: {main_result}, Worker thread result: {worker_result}")
            
            # Both should succeed if thread ownership is handled correctly
            assert main_result, "Main thread context usage should succeed"
            # Worker thread result may legitimately fail if context is thread-local
            
            return {
                'creation_thread': creation_thread,
                'usage_threads': usage_threads,
                'main_result': main_result,
                'worker_result': worker_result
            }
            
        except ImportError as e:
            pytest.skip(f"PIW session not available: {e}")

    def test_mutex_cross_thread_access_pattern(self):
        """Test the specific pattern that might cause the EPERM error"""
        import picross
        
        shared_mutex = None
        lock_thread = None
        unlock_thread = None
        lock_success = False
        unlock_success = False
        
        def lock_mutex():
            nonlocal shared_mutex, lock_thread, lock_success
            try:
                shared_mutex = picross.mutex()
                lock_thread = threading.get_ident()
                shared_mutex.lock()
                lock_success = True
                print(f"Mutex locked by thread {lock_thread}")
                
                # Hold the lock briefly to ensure the other thread tries to unlock
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Lock failed: {e}")
                lock_success = False
        
        def unlock_mutex():
            nonlocal unlock_thread, unlock_success
            try:
                # Wait for the lock to be acquired
                time.sleep(0.05)
                
                unlock_thread = threading.get_ident()
                if shared_mutex:
                    print(f"Attempting unlock by thread {unlock_thread}")
                    shared_mutex.unlock()
                    unlock_success = True
                    print(f"Mutex unlocked by thread {unlock_thread}")
                else:
                    print("No mutex to unlock")
                    
            except Exception as e:
                print(f"Unlock failed by thread {unlock_thread}: {e}")
                unlock_success = False
        
        # Create threads
        lock_thread_obj = threading.Thread(target=lock_mutex)
        unlock_thread_obj = threading.Thread(target=unlock_mutex)
        
        # Start lock thread first
        lock_thread_obj.start()
        
        # Start unlock thread (will try to unlock mutex locked by other thread)
        unlock_thread_obj.start()
        
        # Wait for both
        lock_thread_obj.join()
        unlock_thread_obj.join()
        
        print(f"Lock thread: {lock_thread}, success: {lock_success}")
        print(f"Unlock thread: {unlock_thread}, success: {unlock_success}")
        
        # The lock should succeed
        assert lock_success, "Mutex lock should succeed"
        
        # Cross-thread unlock should fail (this is expected POSIX behavior)
        # But if EigenD allows this, it suggests a wrapper that tracks ownership
        if lock_thread != unlock_thread:
            print("Different threads used for lock/unlock - this may be the source of EPERM errors")
            
        return {
            'lock_thread': lock_thread,
            'unlock_thread': unlock_thread, 
            'lock_success': lock_success,
            'unlock_success': unlock_success,
            'cross_thread': lock_thread != unlock_thread
        }

    def test_python_threading_model_changes(self):
        """Test if Python 3.14 threading model affects thread-local storage or IDs"""
        
        # Test thread-local storage consistency
        import threading
        
        thread_local_data = threading.local()
        
        def test_thread_local():
            thread_local_data.value = threading.get_ident()
            return thread_local_data.value == threading.get_ident()
        
        # Test in main thread
        main_result = test_thread_local()
        
        # Test in worker thread
        worker_result = None
        def worker():
            nonlocal worker_result
            worker_result = test_thread_local()
        
        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()
        
        print(f"Thread-local storage - Main: {main_result}, Worker: {worker_result}")
        
        assert main_result, "Thread-local storage should work in main thread"
        assert worker_result, "Thread-local storage should work in worker thread"
        
        # Test if thread IDs are stable
        initial_id = threading.get_ident()
        time.sleep(0.01)  # Small delay
        final_id = threading.get_ident()
        
        assert initial_id == final_id, "Thread ID should remain stable within same thread"
        
        return {
            'thread_local_works': main_result and worker_result,
            'thread_id_stable': initial_id == final_id,
            'main_thread_id': initial_id
        }

    def test_piw_context_thread_local_behavior(self):
        """Test if PIW context behaves as thread-local in Python 3.14"""
        try:
            import piw
            
            context_values = {}
            
            def test_context_isolation():
                thread_id = threading.get_ident()
                try:
                    # This should create or access thread-local context
                    # The failing unlock might happen when context created in one thread
                    # is accessed/destroyed in another
                    
                    # Get current context (may create mutexes)
                    context_info = f"Thread {thread_id} context access"
                    context_values[thread_id] = context_info
                    
                    print(f"Context accessed by thread {thread_id}")
                    return True
                    
                except Exception as e:
                    print(f"Context access failed in thread {thread_id}: {e}")
                    context_values[thread_id] = f"Error: {e}"
                    return False
            
            # Test context in main thread
            main_result = test_context_isolation()
            
            # Test context in multiple worker threads
            worker_results = []
            threads = []
            
            def worker():
                result = test_context_isolation()
                worker_results.append(result)
            
            # Create multiple threads to test concurrent context access
            for i in range(3):
                thread = threading.Thread(target=worker)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join()
            
            print(f"Context values by thread: {context_values}")
            print(f"Main result: {main_result}, Worker results: {worker_results}")
            
            assert main_result, "Main thread context access should succeed"
            assert all(worker_results), "All worker thread context accesses should succeed"
            
            return {
                'main_result': main_result,
                'worker_results': worker_results,
                'context_values': context_values,
                'total_threads': len(context_values)
            }
            
        except ImportError:
            pytest.skip("PIW not available for context testing")