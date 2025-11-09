# Investigation: Setup Loading Hang - Attach/Detach Loop

**Date:** 2025-11-09  
**Issue:** EigenD setup loading hangs during Python 3 migration, works in Python 2.7

## Key Findings

### Threading Model (Confirmed Working)
- **1 Fast Thread (DSP)**: Non-blocking trywlock(), processes fastq_
- **N Slow Threads (Context)**: Blocking rguard_t read locks, run Python callbacks
- **Fastcall Mechanism**: Slow thread creates synccaller_t on stack, queues callback, blocks on semaphore. Fast thread processes queue, executes callback, signals semaphore.
- **No deadlock detected**: 0 write locks observed, threads making progress

### What We Observed

**Multi-sample analysis (10 samples @ 15s intervals, 3+ minutes observation):**

1. **Thread #9 (context thread) executing normally**
   - Frame depth varies: #10, #29, #33, #38, #42
   - Proves thread making progress (not stuck)
   - Same bytecode offset (+13776) = loop in Python code

2. **9 out of 10 samples caught DETACH operation**
   - Only 1 sample caught ATTACH
   - Detach much slower (long destructor chain, frames 6-38)
   - All in same thread (context thread)

3. **Call chain identified:**
   ```
   ctxthread_t::thread_main
   → client_t::sync_thunk
     → client_wrapper_::client_sync (C++ → Python)
       → _PyEval_EvalFrameDefault +13776
         → node_changed({'domain'})  [proxy.py:295]
           → xxcontrolled_wrapper_::detach_method_ (Python → C++)
             → xxcontrolled_t::detach
               → ~ctlsignal_t cascade
                 → ~wire_ctl_t::disconnect
                   → ~filter_wire_t cascade
                     → ~dataqueue_t::clear
                       → fastcall (semaphore block)
   ```

4. **Root cause location:** `plg_language/controller_plg.py:150-154`
   ```python
   def node_changed(self, parts):
       if 'domain' in parts:
           self.node_removed()  # Calls detach
           self.node_ready()     # Calls attach
   ```

### Current Hypothesis

**Setup is stuck in attach/detach loop, not deadlock:**

- Controller's `domain` metadata keeps changing
- Each change triggers `node_changed({'domain'})`
- This calls `node_removed()` (detach) + `node_ready()` (attach)
- Detach involves expensive destructor cascade + fastcall
- Loop never completes → setup never finishes loading

**Why domain keeps changing (theories):**
1. Target agent keeps reloading/failing to load
2. Metadata propagation timing issues in Py3
3. GIL changes in Python 3.14 causing race conditions
4. Successfully loaded agent (controller) preventing OTHER agents from loading

### What We DON'T Know Yet

⚠️ **Unverified assumptions:**
- Which specific controller is looping?
- What is the controller trying to connect to?
- Is attach succeeding or failing?
- Is this tight retry loop or normal (but slow) behavior?
- Why does different agent fail each run?

### Evidence Base

**Logs analyzed:**
- `l.log` - instrumented run, thread #11 in Python bytecode
- `l2.log` - instrumented run, CLIENT_SYNC showed `<controller3>`
- `l_clean.log` - clean build, detach in semaphore_destroy
- `l_clean2.log` - clean build, detach waiting on fastcall
- `sh.log` - 5 samples @ 1s intervals
- `sh2.log` - 10 samples @ 15s intervals (definitive evidence)

**All runs showed:**
- 5/6 first samples caught context thread in `detach_method_`
- Only l.log showed different pattern (pure Python bytecode)
- Instrumentation didn't change behavior (not artifact)

## Next Steps

1. **Add targeted logging** (remove lock tracking, keep CLIENT_SYNC timing)
   - Log which controller calling detach/attach
   - Log what domain changed
   - Log target agent being connected to

2. **Run without lldb** - prove not sampling artifact

3. **Compare with Python 2.7 behavior** - is detach/attach normal?

4. **Identify victim agent** - what's failing to load?

## Eliminated Theories

❌ **Lock contention** - 0 write locks observed  
❌ **Infinite tight loop** - frame depth varies, thread progressing  
❌ **Deadlock** - fast thread processing, context thread executing  
❌ **Semaphore hang** - operations are sampling artifacts (mach_msg2_trap)  
❌ **Instrumentation artifact** - clean builds show same behavior
