mv # EigenD Threading Model

**Date:** 2025-11-09  
**Status:** Under Investigation - Setup Loading Hang Issue

## Overview

EigenD uses a multi-threaded architecture with careful separation between real-time (DSP) and non-real-time (control/UI) operations.

### Active Threads

1. **Fast Thread (DSP Thread)**
   - **Purpose:** Real-time audio processing
   - **Priority:** High/Real-time
   - **Code:** `fastloop_` in `pia_glue.cpp`
   - **Characteristics:**
     - Non-blocking lock strategy (uses `trywlock()`)
     - Falls back to stale data if lock unavailable
     - Must complete within audio buffer deadline
     - Continues running during setup loading (unless `DISABLE_FAST_THREAD_AT_LOAD` defined)

2. **Slow Threads (Context Threads)**
   - **Purpose:** Python code execution (RPC handlers, agent logic)
   - **Count:** Multiple (organized by context group)
   - **Code:** `process_ctx()` in `pia_glue.cpp`
   - **Characteristics:**
     - Blocking lock strategy (uses `rguard_t` - read lock)
     - Multiple threads can hold READ lock simultaneously
     - Execute Python via `h->appq()->run(now)`
     - Each context has own queue (`appq()`)

3. **Juce Main Thread**
   - **Purpose:** UI event loop, window management
   - **Characteristics:**
     - Uses `global_lock()` / `global_unlock()` for coordination
     - Non-blocking write lock (`trywlock()`)
     - Updates loading progress UI

4. **Timer Thread(s)**
   - **Purpose:** Scheduled callbacks, timeouts
   - **Status:** ⚠️ **NEEDS INVESTIGATION**
   - **Potential:** May acquire locks during callbacks


5. Threading & memory
  - Use `piw.tsd_lock()` for thread safety.
  - C++ objects often use `pic::tracked_t` for ownership tracking.
  
## Areas Requiring Further Analysis

- ❓ **Timer thread lock acquisition:** Does timer thread ever need WRITE lock?
- ❓ **RPC timeout handling:** How do RPC timeouts interact with locks?
- ❓ **Context thread count:** How many slow threads actually run? Fixed or dynamic?
- ❓ **Lock priority:** Does rwmutex favor readers or writers? (Likely writer-preferring)
- ❓ **Deadlock prevention:** What prevents slow thread from starving on write-locked mutex?
- ❓ **UI update mechanism:** How does loading progress get to UI without deadlock?
- ❓ **Garbage collection:** When/where does Python GC run? Does it acquire locks?

## Lock Implementation Details

### Global Lock (`global_lock_`)

**Type:** `pic::rwmutex_t` (Read-Write Mutex)  
**Implementation:** POSIX `pthread_rwlock_t` (on macOS/Linux)  
**Location:** `pia::manager_t::impl_t` in `pia_glue.cpp` line 1305

**Lock Acquisition Strategies:**

```cpp
// WRITE LOCK (Exclusive - UI/System Operations)
bool pia::manager_t::impl_t::global_lock() {
    return global_lock_.trywlock();  // Non-blocking
}

void pia::manager_t::impl_t::global_unlock() {
    global_lock_.wunlock();
}
```

**Used by:**
- Fast thread (DSP) - non-blocking try
- UI thread (Juce main) - non-blocking try
- System operations (fast_pause/resume)

```cpp
// READ LOCK (Shared - Python Execution)
pic::rwmutex_t::rguard_t rwguard(global_lock_);  // BLOCKING
h->appq()->run(now);  // Execute Python code
// Auto-releases on scope exit
```

**Used by:**
- Slow threads (context threads) - **BLOCKS until available**
- Multiple simultaneous readers allowed

### POSIX Read-Write Lock Characteristics

**From `picross/pic_thread_posix.h`:**
```cpp
class rwmutex_t {
    void rlock();      // Block until read lock acquired
    void runlock();    // Release read lock
    bool tryrlock();   // Non-blocking read lock attempt
    void wlock();      // Block until write lock acquired (EXCLUSIVE)
    void wunlock();    // Release write lock
    bool trywlock();   // Non-blocking write lock attempt
private:
    pthread_rwlock_t data_;
};
```

**Semantics:**
- Multiple readers can hold lock simultaneously
- Writer requires exclusive access (no readers, no writers)
- **Priority:** Typically writer-preferring (readers starve if writer waiting)
- **Re-entrant:** NO - same thread cannot re-acquire

### Other Lock Types in Codebase

1. **`pic::mutex_t`** - Standard mutex (recursive or non-recursive)
   - Implementation: `pthread_mutex_t` (POSIX)
   - Used for: Internal data structure protection

2. **`pic::spinlock`** - Busy-wait spinlock
   - Implementation: Atomic compare-and-swap
   - Used for: Very short critical sections (JUCE usage)

3. **`pic::gate_t`** - Event/semaphore
   - Implementation: `pthread_cond_t` + `pthread_mutex_t`
   - Used for: Thread synchronization

4. **`pia_mainguard_t`** - Scope guard for main queue lock
   - Protects context list access

## Python Threading Implications

### Python Global Interpreter Lock (GIL)

**Status:** Python 3.14 uses per-interpreter GIL (not truly global)

**Key Characteristics:**
- Python bytecode execution is atomic at instruction level
- C extension code releases GIL for blocking operations
- EigenD's C++ layer likely releases GIL before blocking locks
- Multiple Python interpreters possible (though EigenD uses one)

**Interaction with EigenD Locks:**
```
Thread enters C++ (releases Python GIL)
  → Acquires global_lock_ (read lock - may block here)
  → Re-acquires Python GIL
  → Executes Python code (appq()->run())
  → Releases Python GIL
  → Releases global_lock_ (read lock)
```

### Python Garbage Collection

**Python 3.14 GC Characteristics:**
- Generational garbage collector (gen 0, 1, 2)
- Triggered by allocation counts
- Can run during any Python code execution
- Does NOT run during C++ code (GIL released)

**Potential Issues:**
- ⚠️ GC running during `appq()->run()` holds READ lock
- ⚠️ Long GC pause extends READ lock hold time
- ⚠️ Could block writer (fast thread, UI thread) temporarily

**Location of GC Triggers:**
- Automatic during Python object allocation
- `gc.collect()` calls (not seen in EigenD code)
- Module cleanup during interpreter shutdown

## Lock Hierarchy and Deadlock Prevention

**Known Lock Ordering:**
1. `pia_mainguard_t` (protects context list)
2. `global_lock_` (read or write)
3. Context-specific locks (inside agents)

**Potential Deadlock Scenarios:**
- ❌ Thread A: READ lock → waits for resource
- ❌ Thread B: Holds resource → tries WRITE lock → blocked by A
- ✅ **Mitigation:** Non-blocking write locks (`trywlock()`)

## Fast Thread / Slow Thread Coordination (Fastcall Mechanism)

### Overview

When a slow thread needs the fast thread to execute an operation (e.g., wire disconnect, dataqueue clear), it uses **`fastcall()`**. This is a synchronous coordination mechanism where the slow thread blocks until the fast thread completes the requested operation.

### Implementation Details

**Source Files:**
- `piagent/src/pia_glue.cpp` lines 40-102 (fastcall implementation)
- `piagent/src/pia_eventq.cpp` lines 346-427 (queue management)
- `piagent/src/pia_scaffold.cpp` lines 446-505 (fast thread loop)

**Slow Thread Side** (`pia_glue.cpp:75-102`):
```cpp
int pia::manager_t::impl_t::fastcall(int (*cb)(...), void *a1, void *a2, void *a3, void *a4) {
    // 1. Check if already on fast thread - if so, call directly
    if(handle_->service_isfast()) {
        return (cb)(a1,a2,a3,a4);
    }
    
    // 2. Check if fast thread not running - call with lock
    if(!fastactive_) {
        pic::mutex_t::guard_t g(fast_lock_);
        return (cb)(a1,a2,a3,a4);
    }

    // 3. Create synccaller_t ON STACK
    synccaller_t s;
    s.cb = cb;
    s.a1 = a1; s.a2 = a2; s.a3 = a3; s.a4 = a4;
    // s.g is pic::semaphore_t initialized to 0
    
    // 4. Queue callback to fast thread
    fastq_.idlecall(pia_make_cpoint(), synccaller, &s);
    
    // 5. BLOCK waiting for fast thread to signal
    s.g.untimeddown();  // semaphore_wait() - BLOCKS HERE
    
    // 6. Return result set by fast thread
    return s.r;
}
```

**`synccaller_t` Structure** (`pia_glue.cpp:52-60`):
```cpp
struct synccaller_t {
    int (*cb)(void *, void *, void *, void *);  // Callback function
    void *a1, *a2, *a3, *a4;                     // Arguments
    int r;                                        // Return value
    pic::semaphore_t g;                          // Semaphore (mach semaphore on macOS)
};
```

**Fast Thread Side** (`pia_scaffold.cpp:446-505`, `pia_eventq.cpp:410-427`):
```cpp
// Fast thread main loop
void fastthread_t::thread_main() {
    while(!shutdown) {
        // Process all queued work
        for(;;) {
            manager_->process_fast(now, &next_timer, &activity);
            if(!activity) break;
        }
        
        // Sleep until next work or timeout
        gate_.pass_and_shut_timed(next_timer - now);
    }
}

// Process fast queue
void pia::manager_t::impl_t::process_fast(...) {
    if(fastq()->run(now)) {
        *activity = true;
    }
}

// Run one item from queue
template <class T> bool pia_eventq_impl_t<T>::run(unsigned long long now) {
    // ... process other queue types ...
    
    // Process idlecall queue (fastcall callbacks)
    if((ic = idlecall_.head()) != 0) {
        ic->remove();           // Remove from queue
        ic->run();              // Execute callback
        delete ic;              // Free wrapper
        return true;
    }
}

// Callback execution (pia_glue.cpp:63-74)
static void synccaller(void *ctx) {
    synccaller_t *s = (synccaller_t *)ctx;
    
    try {
        // Execute callback IN FAST THREAD CONTEXT
        s->r = (s->cb)(s->a1, s->a2, s->a3, s->a4);
    }
    CATCHLOG()
    
    // SIGNAL SEMAPHORE - wakes blocked slow thread
    s->g.up();  // semaphore_signal()
}
```

**Wakeup Mechanism**:
```cpp
// idlecall() wakes fast thread via pinger callback
fastq_.idlecall(cpoint, synccaller, &s);
  → add(idlecall_insert<T>, i, 0, 0, 0)
    → fast_pinger(ctx)  // pia_glue.cpp:1283
      → service_fast()  // pia_scaffold.cpp:828
        → gate_.open()  // Wake fast thread
```

### Semaphore Lifecycle

**Creation** (`pic_thread_posix.cpp:513-519`):
```cpp
pic::semaphore_t::semaphore_t() {
    kern_return_t kr;
    kr = semaphore_create(mach_task_self(), &sem_, SYNC_POLICY_FIFO, 0);
    // Creates Mach semaphore via mach_msg system call
}
```

**Destruction** (`pic_thread_posix.cpp:523-525`):
```cpp
pic::semaphore_t::~semaphore_t() {
    semaphore_destroy(mach_task_self(), sem_);
    // Destroys Mach semaphore via mach_msg system call
}
```

**Key Properties:**
- Semaphore allocated ON STACK in slow thread (part of `synccaller_t`)
- Lifetime managed by stack frame - destroyed when `fastcall()` returns
- **Destruction requires mach_msg system call** - CAN BLOCK
- ONE semaphore per fastcall (no shared pool)
- Queue contains POINTERS to stack-allocated `synccaller_t` structures


## References

- `piagent/src/pia_glue.cpp` - Main threading and lock implementation
- `piagent/src/pia_scaffold.cpp` - Thread initialization
- `picross/pic_thread_posix.h` - POSIX threading primitives
- `picross/src/pic_thread_posix.cpp` - Thread implementation
- `dev_docs/setup_loading.md` - Setup loading process (where hang occurs)
