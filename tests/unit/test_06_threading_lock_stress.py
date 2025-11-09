"""
Threading and Lock Stress Tests for EigenD

Tests the interaction between fast (DSP) thread and slow (Python) threads
to reproduce the setup loading hang issue.

Key Scenarios:
1. Fast thread with trywlock() - should never block
2. Multiple slow threads with rlock() - should coexist
3. Write lock starvation - slow threads waiting for write lock to release
4. Deadlock detection - identify lock ordering issues
"""

import pytest
import threading
import time
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


class MockRWLock:
    """Mock read-write lock that mimics picross rwmutex_t behavior"""
    def __init__(self):
        self._lock = threading.Lock()
        self._readers = 0
        self._writer = False
        self._writer_thread = None
        self._waiting_writers = 0
        
        # Track lock acquisition for debugging
        self.read_acquisitions = []
        self.write_acquisitions = []
        self.write_failures = []
        
    def rlock(self, thread_id=None):
        """Blocking read lock (used by slow threads)"""
        if thread_id is None:
            thread_id = threading.get_ident()
            
        # Writer-preferring: wait if writer or waiting writers
        while True:
            with self._lock:
                if not self._writer and self._waiting_writers == 0:
                    self._readers += 1
                    self.read_acquisitions.append({
                        'thread': thread_id,
                        'time': time.time(),
                        'readers': self._readers
                    })
                    return
            time.sleep(0.001)  # Small backoff
            
    def runlock(self, thread_id=None):
        """Release read lock"""
        with self._lock:
            self._readers -= 1
            
    def trywlock(self, thread_id=None):
        """Non-blocking write lock attempt (used by fast thread / UI)"""
        if thread_id is None:
            thread_id = threading.get_ident()
            
        with self._lock:
            if not self._writer and self._readers == 0:
                self._writer = True
                self._writer_thread = thread_id
                self.write_acquisitions.append({
                    'thread': thread_id,
                    'time': time.time()
                })
                return True
            else:
                self.write_failures.append({
                    'thread': thread_id,
                    'time': time.time(),
                    'readers': self._readers,
                    'writer': self._writer
                })
                return False
                
    def wlock(self, thread_id=None):
        """Blocking write lock"""
        if thread_id is None:
            thread_id = threading.get_ident()
            
        self._waiting_writers += 1
        try:
            while True:
                with self._lock:
                    if not self._writer and self._readers == 0:
                        self._writer = True
                        self._writer_thread = thread_id
                        self.write_acquisitions.append({
                            'thread': thread_id,
                            'time': time.time()
                        })
                        return
                time.sleep(0.001)
        finally:
            self._waiting_writers -= 1
                
    def wunlock(self):
        """Release write lock"""
        with self._lock:
            assert self._writer, "Attempting to unlock non-locked write lock"
            self._writer = False
            self._writer_thread = None


@pytest.mark.threading
class TestLockStressScenarios:
    """Test lock contention scenarios that could cause setup loading hang"""
    
    def test_fast_thread_never_blocks(self):
        """Fast thread (DSP) should never block on lock acquisition"""
        lock = MockRWLock()
        fast_blocked = []
        
        # Slow thread holds read lock
        def slow_thread():
            lock.rlock()
            time.sleep(0.5)  # Hold lock for 500ms
            lock.runlock()
            
        # Fast thread tries to acquire write lock periodically
        def fast_thread():
            for _ in range(100):
                start = time.time()
                result = lock.trywlock()
                duration = time.time() - start
                
                if duration > 0.01:  # 10ms threshold
                    fast_blocked.append(duration)
                    
                if result:
                    lock.wunlock()
                    
                time.sleep(0.01)  # 10ms cycle (100Hz like DSP)
                
        t1 = threading.Thread(target=slow_thread)
        t2 = threading.Thread(target=fast_thread)
        
        t1.start()
        time.sleep(0.01)  # Let slow thread acquire lock first
        t2.start()
        
        t1.join()
        t2.join()
        
        assert len(fast_blocked) == 0, f"Fast thread blocked {len(fast_blocked)} times: {fast_blocked}"
        assert len(lock.write_failures) > 0, "Fast thread should have some failures (expected)"
        
    def test_multiple_slow_threads_concurrent(self):
        """Multiple slow threads should be able to hold read locks simultaneously"""
        lock = MockRWLock()
        concurrent_readers = []
        
        def slow_thread(tid):
            lock.rlock(tid)
            # Check how many readers when we acquired
            with lock._lock:
                concurrent_readers.append(lock._readers)
            time.sleep(0.1)
            lock.runlock(tid)
            
        threads = []
        for i in range(5):
            t = threading.Thread(target=slow_thread, args=(i,))
            threads.append(t)
            t.start()
            time.sleep(0.01)  # Stagger starts slightly
            
        for t in threads:
            t.join()
            
        # Should have seen multiple concurrent readers
        assert max(concurrent_readers) > 1, f"Expected concurrent readers, got max={max(concurrent_readers)}"
        
    def test_write_lock_blocks_readers(self):
        """When write lock held, readers should block"""
        lock = MockRWLock()
        reader_blocked = threading.Event()
        reader_acquired = threading.Event()
        
        def writer_thread():
            lock.wlock()
            time.sleep(0.2)  # Hold write lock
            lock.wunlock()
            
        def reader_thread():
            reader_blocked.set()  # Signal we're about to block
            lock.rlock()
            reader_acquired.set()  # Signal we got the lock
            lock.runlock()
            
        t1 = threading.Thread(target=writer_thread)
        t2 = threading.Thread(target=reader_thread)
        
        t1.start()
        time.sleep(0.05)  # Let writer acquire lock
        t2.start()
        
        # Wait for reader to attempt acquisition
        reader_blocked.wait(timeout=1.0)
        time.sleep(0.05)
        
        # Reader should still be blocked
        assert not reader_acquired.is_set(), "Reader should be blocked by write lock"
        
        t1.join()
        t2.join()
        
        # Now reader should have acquired
        assert reader_acquired.is_set(), "Reader should have acquired after writer released"
        
    def test_reader_starvation_by_writer(self):
        """
        Test if readers can starve waiting for write lock to release.
        This is the suspected cause of setup loading hang.
        """
        lock = MockRWLock()
        reader_times = []
        writer_hold_time = 1.0  # Writer holds lock for 1 second
        
        def writer_thread():
            """Simulates a thread that acquires write lock and doesn't release"""
            lock.wlock()
            time.sleep(writer_hold_time)
            lock.wunlock()
            
        def reader_thread(tid):
            """Simulates Python RPC handler waiting for read lock"""
            start = time.time()
            lock.rlock(tid)
            wait_time = time.time() - start
            reader_times.append((tid, wait_time))
            time.sleep(0.01)
            lock.runlock(tid)
            
        # Start writer
        t_writer = threading.Thread(target=writer_thread)
        t_writer.start()
        time.sleep(0.05)  # Let writer acquire lock
        
        # Start multiple readers
        t_readers = []
        for i in range(10):
            t = threading.Thread(target=reader_thread, args=(i,))
            t_readers.append(t)
            t.start()
            time.sleep(0.01)
            
        # All threads complete
        t_writer.join(timeout=2.0)
        for t in t_readers:
            t.join(timeout=2.0)
            
        # Check if readers were starved
        for tid, wait_time in reader_times:
            assert wait_time >= writer_hold_time * 0.9, \
                f"Reader {tid} should have waited ~{writer_hold_time}s, got {wait_time:.3f}s"
                
        print(f"\nReader starvation test:")
        print(f"  Writer held lock for: {writer_hold_time}s")
        print(f"  Reader wait times: {[(tid, f'{t:.3f}s') for tid, t in reader_times]}")
        
    def test_forgotten_write_lock_deadlock(self):
        """
        Test scenario where write lock is acquired but never released.
        This simulates the suspected hang condition.
        """
        lock = MockRWLock()
        reader_timeout = threading.Event()
        
        def bad_writer_thread():
            """Thread that acquires write lock but forgets to release"""
            lock.wlock()
            # Oops! Forgot to unlock (simulating bug)
            time.sleep(2.0)  # Keep running but never unlock
            
        def reader_thread():
            """Reader that will be starved forever"""
            start = time.time()
            # Try to acquire with timeout
            timeout = 0.5
            acquired = False
            
            # Manual timeout since our rlock blocks
            while time.time() - start < timeout:
                # In real code this would be a blocking call
                # Here we simulate checking if we can acquire
                if lock.trywlock():  # Try write lock as proxy
                    lock.wunlock()
                    break
                time.sleep(0.01)
            else:
                reader_timeout.set()
                
        t1 = threading.Thread(target=bad_writer_thread)
        t2 = threading.Thread(target=reader_thread)
        
        t1.start()
        time.sleep(0.05)  # Let writer acquire
        t2.start()
        t2.join(timeout=1.0)
        
        # Reader should have timed out
        assert reader_timeout.is_set(), "Reader should timeout waiting for forgotten write lock"
        
        t1.join(timeout=0.1)  # Don't wait for bad writer
        
    @pytest.mark.slow
    def test_high_load_lock_contention(self):
        """
        Stress test with many threads competing for lock.
        Simulates setup loading with many agents.
        """
        lock = MockRWLock()
        completed = []
        failed = []
        
        def reader_worker(tid):
            """Simulates agent RPC handler"""
            try:
                start = time.time()
                lock.rlock(tid)
                # Simulate some work
                time.sleep(0.001)
                lock.runlock(tid)
                duration = time.time() - start
                completed.append((tid, duration))
            except Exception as e:
                failed.append((tid, str(e)))
                
        def writer_worker(tid):
            """Simulates fast thread or UI update"""
            try:
                for _ in range(100):
                    if lock.trywlock(tid):
                        time.sleep(0.0001)  # Very brief
                        lock.wunlock()
                    time.sleep(0.01)
            except Exception as e:
                failed.append((tid, str(e)))
                
        threads = []
        
        # Start writer threads (fast threads)
        for i in range(2):
            t = threading.Thread(target=writer_worker, args=(f"writer-{i}",))
            threads.append(t)
            t.start()
            
        # Start many reader threads (Python contexts)
        for i in range(50):
            t = threading.Thread(target=reader_worker, args=(f"reader-{i}",))
            threads.append(t)
            t.start()
            time.sleep(0.002)  # Stagger to simulate sequential loading
            
        # Wait for all to complete
        for t in threads:
            t.join(timeout=5.0)
            
        assert len(failed) == 0, f"Some threads failed: {failed}"
        assert len(completed) >= 50, f"Expected 50+ readers, got {len(completed)}"
        
        # Check for excessive wait times (> 1s indicates starvation)
        long_waits = [(tid, dur) for tid, dur in completed if dur > 1.0]
        assert len(long_waits) == 0, f"Some threads starved: {long_waits}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
