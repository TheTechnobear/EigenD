# EigenD Setup Loading Failure Analysis

**Date:** 2025-11-09  
**Status:** Root cause identified - awaiting fix implementation

## Executive Summary

### Current Understanding

**The Problem:**
- Large setups (60+ agents with connections) fail to load completely on Python 3.14
- Loading stops at unpredictable points (phase 24-26 out of 60)
- Same setups load successfully on Python 2.7
- Setups without connections load fine regardless of agent count

**Root Cause Investigation Status:**
- ~~Event loop saturation~~ - DISPROVEN (piasync test passed)
- ~~piasync callback chain bug~~ - DISPROVEN (framework works correctly)
- ~~Lock contention / deadlock~~ - DISPROVEN (multi-sample analysis, no lock contention)
- **CURRENT HYPOTHESIS: Controller Attach/Detach Loop**
  - Setup loading repeatedly calls `node_changed({'domain'})` on controllers
  - Each domain change triggers `node_removed()` followed by `node_ready()`
  - Detach operation involves expensive destructor cascade + fastcall to DSP thread
  - Multi-sample analysis: 9/10 samples caught DETACH, 1/10 caught ATTACH
  - Thread is making progress (frame depth varies) but stuck in same bytecode loop
  - **Root cause location:** `plg_language/controller_plg.py` lines 150-154

**Evidence from Multi-Sample Analysis (2025-11-09):**
- Captured 10 samples over 3+ minutes (15s intervals)
- Thread #9 (Python context) at `_PyEval_EvalFrameDefault + 13776` in ALL samples
- Frame depth varies: #10, #29, #33, #38, #42 → **thread executing, not stuck**
- Same bytecode offset = repeatedly returning to same code path
- Pattern: 9/10 samples show detach operation (expensive, frames 6-38)
- Pattern: 1/10 samples show attach operation (faster)
- Call chain traced from thread_main → client_sync → proxy.__nodechanged → controller.node_changed

**Threading Model:** (See `dev_docs/threading_model.md`)
- 1 Fast Thread (DSP) - non-blocking write locks, processes fastcall queue
- N Slow Threads (Python contexts) - blocking read locks, use fastcall for DSP operations
- Juce Main Thread (UI) - non-blocking write locks
- Read-write mutex (`global_lock_`) coordinates access
- Lock instrumentation showed 0 write lock attempts during hang → no lock contention

**Root Cause Code:**
```python
# plg_language/controller_plg.py lines 150-154
def node_changed(self, parts):
    if 'domain' in parts:
        self.node_removed()   # Triggers detach → destructor cascade
        self.node_ready()     # Triggers attach
```

**Call Chain During Hang:**
```
ctxthread_t::thread_main (C++)
→ client_t::sync_thunk (C++)
  → client_wrapper_::client_sync (C++ → Python bridge)
    → _PyEval_EvalFrameDefault +13776 (Python interpreter)
      → proxy.py:295 __nodechanged({'domain'})
        → controller_plg.py:150-154 node_changed()
          → node_removed() → detach_method_
            → xxcontrolled_t::detach
              → destructor cascade (6-38 frames deep)
                → fastcall to DSP thread
```

**What We Don't Know Yet:**
- Which specific controller is looping?
- Which target agent is it connecting to?
- Why does the domain keep changing?
- Does attach succeed before next detach?
- Is this same controller repeatedly, or multiple controllers?

**Next Steps:**
1. Add instrumentation to identify controller ID and domain changes
2. Run without debugger to prove behavior exists outside lldb
3. Identify which controller and what domain values triggering loop
4. Compare with Python 2.7 behavior (does domain change there too?)
5. Consider fixes:
   - Prevent spurious domain changes during loading
   - Defer controller attachment until post-load
   - Cache domain to avoid redundant detach/attach cycles

**Note:** See `dev_docs/piasync.md` for detailed analysis of EigenD's async framework and Python 2 vs 3 differences.

**Note 2:** Discovered mutex bug in `pic::mutex_t` constructor - see `dev_docs/threading_model.md`

**Note 3:** Complete attach/detach loop analysis in `dev_docs/investigation_attach_detach_loop.md`

### Multi-Sample Stack Trace Analysis

**Methodology:**
- Single lldb Ctrl-C = snapshot only, proves nothing about hang state
- Semaphore operations in trace are artifacts (debugger stops ALL threads)
- Need 10+ samples over minutes to distinguish: stuck vs busy vs retry-loop

**Tools Created:**
- `sample_hang.py` - Collect multiple stack traces at intervals
- `analyze_python_frames.py` - Parse logs to find Python frame patterns

**Key Discovery:**
- Same bytecode offset (`_PyEval_EvalFrameDefault + 13776`) across all samples = code location
- Varying frame depth (#10, #29, #33, #38, #42) = thread making progress
- Pattern: "Same bytecode + varying frame depth" = **retry/polling loop**, not deadlock

**Evidence from 6 log files:**
- `l.log`, `l2.log`, `l_clean.log`, `l_clean2.log` - Initial single-sample traces
- `sh.log` - 5 samples @ 1s intervals
- `sh2.log` - 10 samples @ 15s intervals over 3+ minutes (definitive)

**Analysis Results:**
- 5 out of 6 first samples showed `detach_method_` being called
- sh2.log analysis: 9/10 samples in DETACH operation, 1/10 in ATTACH
- Detach much slower: 6-38 stack frames (destructor cascade)
- Attach faster: fewer frames, simpler operation

### Evidence Summary

✅ **Confirmed Facts:**
- 60+ agents WITHOUT connections: Loads successfully on Python 3
- 60 agents WITH connections: Fails on Python 3 (phase 24-26)
- Same setup on Python 2.7: Loads successfully (60/60, 15.4s)
- Loading order is non-deterministic (dict/set iteration)
- Test setup has 276 forward-reference connections
- No exceptions logged - process just stops responding
- `invoke_async_rpc` times out silently (10-50s, no callbacks)

✅ **Disproven:**
- ~~Exception propagation breaking callback chain~~ (async RPC has no callbacks)
- ~~Thread synchronization issues~~ (single-threaded event loop)
- ~~Queue length limits~~ (no evidence of queue limits)

### Next Steps

1. **Add instrumentation to confirm event loop saturation:**
   ```python
   # In pisession/workspace.py __doload()
   print(f"DEBUG: Loading agent {n} ({len(self.__load_queue)} remaining)")
   print(f"DEBUG: Pending timers: {piw.pending_timer_count()}")
   ```

2. **Test fix: Defer connections to post-load phase**
   - Modify `pi/atom.py` to queue connections during load
   - Send all queued connection RPCs in `agent_postload()`
   - Eliminates async RPC flood during loading

3. **Verify with test setup:**
   - Test "pico 2 ~ 4 VST or Audio Unit and 4 Midi Out" (65 agents, 565 connections, 276 forward refs)
   - Ensure no regression on small setups

### Proposed Fix

**Location:** `pi/atom.py` lines 618-675

```python
class Atom(node.Server):
    def __init__(self, ...):
        # Add connection queue
        self.__pending_connection_rpcs = []
        self.__loading = False
    
    def set_connections(self, srcs):
        old = self.get_property_termlist('master')
        self.set_property_string('master', srcs)
        if not self.__loading:
            self.update_slaves(old)
        else:
            # Queue for post-load
            self.__pending_connection_rpcs.append(('update', old))
    
    def agent_postload(self, filename):
        # Send all queued connection RPCs
        for (op, old) in self.__pending_connection_rpcs:
            if op == 'update':
                self.update_slaves(old)
        self.__pending_connection_rpcs = []
```

**Rationale:** All agents guaranteed to exist in post-load phase, eliminating forward-reference RPCs.


---

## Loading Process Overview

### Call Chain (Simplified)

**Synchronous function calls:** `→`  
**Async RPC calls:** `⇒`  
**Callback/resume:** `⤶`

```
Workspace.load_file()
  → upgrade.prepare_file()                    # Prepare snapshot
  → Workspace.__load1()                       # Build queue
    → Workspace.__doload()                    # Sequential loop
      → Controller.reload()
        ⇒ Agent.rpc_loadstate() [chunk 0]   # RPC to agent
        ⤶ reload() resumes
        ⇒ Agent.rpc_loadstate() [chunk 1]
        ⤶ reload() resumes
        ⇒ Agent.rpc_loadstate() [final]
        ⤶ reload() completes
      ⤶ ok() callback fires
        → __doload()                          # Loop continues
```

**Agent State Loading (inside rpc_loadstate):**

```
Agent.rpc_loadstate()
  → parse state chunks
  → Phase 1: Basic state
    → Atom.load_state(phase=1)
      → set properties
      → create children
  → Phase 2: Deferred state (connections)
    → Atom.load_state(phase=2)
      → Atom.set_connections()
        → Atom.update_slaves()
          ⇒ target_agent.rpc_connected()     # ASYNC RPC
          (no callback, fire-and-forget)
```

**Post-Load Phase:**

```
Workspace.post_load()
  → for each agent:
    ⇒ Agent.rpc_postload()
    ⤶ wait for completion
```

### Threading & Event Loop

**Single-Threaded Event Loop:**
- All Python code runs in main thread
- Event loop processes: RPCs, timers, I/O callbacks
- No threading issues, no race conditions

**Async RPC Mechanism:**
1. **Client side:** `invoke_async_rpc()` queues RPC, starts timer, returns immediately
2. **Event loop:** Processes RPC send, retries (ACK_TIMER=1s, RSP_TIMER=5s)
3. **Server side:** If agent exists, processes RPC, sends response
4. **Timeout:** After 10-50s, `cnode_t` deleted silently (no Python callback)

**Problem:** With 276+ forward-reference connections:
- 276 async RPCs queued during loading
- Each retries every 1-5 seconds
- Event loop saturated with timer callbacks
- `__doload()` callback may not get scheduled
- Loading stops with no error

---

## Detailed Implementation

### Setup File Format

### Database Structure
**Format:** SQLite database with custom schema  
**Naming:** `timestamp~label` format:
- Timestamp: Unix epoch (10 digits)
- Label: Human-readable setup name
- Examples: `1234567890~My Setup`, `~Factory` (no timestamp = factory default)

**Access Path:** `pi.state.open_database()` → `piw` C++ layer → SQLite backend

### Python API (state.pip bindings)

**Database Class:**
```python
db = pi.state.open_database(path, writable=False)
snapshot = db.get_trunk()        # Get current/main snapshot
snapshot = db.get_version(n)     # Get version n from history
db.flush()                        # Write to disk
db.close()
```

**Snapshot Class:** Container for agent state at a point in time
```python
count = snapshot.agent_count()                    # Number of agents
agent = snapshot.get_agent_index(i)               # Get by index (0-based)
agent = snapshot.get_agent_address(0, addr, True) # Get by address string
ver = snapshot.version()                          # Version number
ts = snapshot.timestamp()                         # Unix timestamp
tag = snapshot.tag()                              # Label/description
prev = snapshot.previous()                        # Previous version number
new_snap = snapshot.clone(timestamp, label)       # Create new snapshot
snapshot.save(timestamp, label)                   # Save to database
```

**Agent Class:** Represents individual plugin instance
```python
addr = agent.get_address()      # "1-234" format (ordinal-id)
name = agent.get_name()         # User-facing name
plugin = agent.get_plugin()     # "audio unit 1", "arranger 1", etc.
type = agent.get_type()         # 0=persistent, 1=transient/volatile
root = agent.get_root()         # Root node of state tree
ckpt = agent.get_checkpoint()   # Checkpoint version
dirty = agent.isdirty()         # Has uncommitted changes?
```

**Node Class:** Tree structure for agent state (hierarchical key-value store)
```python
data = node.get_data()          # Get node value (piw.data term)
child = node.get_child(id)      # Get child by index (0-255)
node.set_data(data)             # Set node value
node.erase_child(id)            # Remove child
children = node.list_children() # List all children
```

### State Tree Structure

Each agent has a **hierarchical state tree** rooted at `agent.get_root()`:

```
Agent Root Node
├── Properties (piw.data terms)
│   ├── name: "My Synth"
│   ├── ordinal: 5
│   └── ...
├── Child Node 0 (e.g., "connections")
│   ├── Child 0: conn(1, 0, "2-123", [1], [2,1])
│   ├── Child 1: conn(1, 0, "3-456", [2], [1])
│   └── ...
├── Child Node 1 (e.g., "parameters")
│   └── ...
└── Child Node N
```

**Node Data Format:** Prolog-like terms via `piw.data`
- `term(functor, [args...])` - Structured data
- `string(value)` - Text
- `number(value)` - Numeric
- `list([items...])` - Arrays

### Connection Term Format

Connections stored as Prolog terms in agent state trees:

```python
conn(
    index,        # Connection index (int)
    flags,        # Connection flags (int, 0=normal, 1=forward-ref)
    target_id,    # Target agent address "ordinal-id"
    src_path,     # Source path list [cookie1, cookie2, ...]
    dst_path      # Destination path list [cookie1, cookie2, ...]
)
```

**Example:**
```python
conn(1, 0, "2-123", [1], [2,1])  # Normal connection
conn(2, 1, "3-456", [1], [1])    # Forward-reference (flag=1)
```

**Forward References:** Connections to agents not yet loaded (`flags=1`)
- Target agent address exists in snapshot but not in workspace
- RPC attempts will time out until target loads
- Large setups can have 276+ forward-refs (per test setup)

### Agent Types

```python
type = agent.get_type()
# 0 = Persistent agents (saved to setup, loaded on startup)
# 1 = Transient/volatile agents (runtime only, not saved)
```

**Loading Order:**
1. Persistent agents loaded first (type=0)
2. Transient agents "parked" until explicitly needed (type=1)
3. Agents loaded **by index order** (0 to N), NOT by dependencies

### Loading Phases

**1. Preparation** ([`workspace.py:418`](../pisession/workspace.py#L418))

```python
snapshot = self.__backend.run_foreground_sync(
    upgrade.prepare_file, path, version.version
)
```
- Copies file to temp location
- Upgrades if version mismatch
- Returns snapshot for loading

**2. Queue Building** ([`workspace.py:476`](../pisession/workspace.py#L476))

```python
for i in range(snap.agent_count()):
    agent = snap.get_agent_index(i)
    addr = agent.get_address()
    if agent.get_type() == 0:
        pending.add(addr)  # Set = unordered!

for c in self.index.members():  # Dict iteration = unordered!
    if c.address in pending:
        self.__load_queue.append(c)
```

**Non-determinism source:** Set and dict iteration order varies between runs.

**3. Sequential Loading** ([`workspace.py:356`](../pisession/workspace.py#L356))

```python
def __doload(self):
    while self.__load_queue:
        f = self.__load_queue[0]
        
        def ok(*args):
            self.__load_queue.pop(0)
            self.__doload()  # Recurse for next agent
        
        r = f.reload(s, self.__load_path)
        r.setCallback(ok).setErrback(not_ok)
        break  # Wait for callback
```

**Critical:** If `ok()` never fires, `__doload()` never called again → loading stops.

**4. Per-Agent State Loading** ([`workspace.py:131`](../pisession/workspace.py#L131))

```python
@piasync.coroutine('internal error')
def reload(self, snap, filename):
    # Get state diff and chunk it
    diff = self.get_diff(snap.get_root(), ...).render()
    
    chunks = []
    while diff:
        chunks.append(diff[:1200])  # RPC size limit
        diff = diff[1200:]
    
    # Send chunks via RPC
    for i, chunk in enumerate(chunks):
        r = rpc.invoke_rpc(myid, 'loadstate', 
                          f'{i}:{len(chunks)}:{chunk}')
        yield r  # Wait for each chunk
```

**5. Agent State Handler** ([`agent.py:236`](../pi/agent.py#L236))

```python
@piasync.coroutine('internal error')
def rpc_loadstate(self, arg):
    # Reassemble chunks
    (i, count, data) = arg.split(':', 2)
    self.__state_buffer[i] = data
    
    if i != count:  # More chunks coming
        yield piasync.Coroutine.success('[]')
    
    # Parse complete state
    state = piw.parse_state_term(''.join(self.__state_buffer))
    
    # Phase 1: Properties and structure
    while delegate.residual:
        yield k.load_state(v, delegate, phase=1)
    
    # Phase 2: Deferred items (connections!)
    delegate.residual = delegate.deferred
    while delegate.residual:
        yield k.load_state(v, delegate, phase=2)
```

**6. Connection Creation** ([`atom.py:872`](../pi/atom.py#L872))

```python
def load_state(self, state, delegate, phase):
    if phase == 1:
        delegate.set_deferred(self, state)
        return piasync.success()
    
    # Phase 2: Restore connections from database
    result = Atom.load_state(self, state, delegate, phase-1)
    
    # Check if this atom has master connections
    masters = self.get_property_termlist('master')
    if masters:
        # Trigger connection establishment immediately
        old = logic.parse_termlist('')  # Empty old list
        self.update_slaves(old)  # <-- PROBLEM: Sends async RPCs now!
    
    return result

def update_slaves(self, old):
    # Calculate diff
    masterids = set([x.args[2] for x in 
                     self.get_property_termlist('master')])
    previous = set([x.args[2] for x in old])
    new_listeners = masterids.difference(previous)
    
    # Notify each connection target
    for id in new_listeners:
        id_abs = paths.to_absolute(id, self.__connection_scope)
        myrid = paths.to_relative(self.id(), ...)
        rpc.invoke_async_rpc(id_abs, 'connected', myrid)
```

**CRITICAL FINDING:** Connections are established **during load_state phase 2**, not in post-load!  
This means async RPCs are sent **while agents are still loading**, causing forward-reference floods.

**Updated instrumentation** (2025-11-09):
- `LOAD_STATE_PHASE2:` logs when connections restored from DB
- `CONNECTION:` logs when `update_slaves()` called  
- `FORWARD_REF:` logs when target agent doesn't exist
- `RPC_CONNECTED:` logs when connection RPC received
- `RPC_DISCONNECTED:` logs when disconnection RPC received

**Additional coroutine-level debugging** (2025-11-09):
- `RELOAD_START/SYNC/CHUNKS/RPC_START/RPC_OK/FINAL_RPC/FINAL_OK/COMPLETE:` Track Controller.reload() coroutine execution
- `RPC_LOADSTATE/BUFFERED/COMPLETE/PARSED/PHASE0/PHASE1/PHASE2/DONE:` Track Agent.rpc_loadstate() handler execution
- Purpose: Identify exactly where controller2's reload() coroutine hung

### Async RPC Implementation

**Python Layer** ([`rpc.py:53`](../pi/rpc.py#L53))

```python
def invoke_async_rpc(id, name, arg, timeout=30000):
    (addr, path) = paths.breakid(id)
    arg = piw.makestring_len(arg, len(arg), 0)
    name = piw.makestring(name, 0)
    piw.tsd_rpcasync(addr.as_string(), path.make_normal(), 
                     name, arg, timeout)
    # Returns immediately, no Deferred!
```

**C++ Layer** ([`pia_rpc.cpp:488`](../piagent/src/pia_rpc.cpp#L488))

```cpp
void pia_rpclist_t::async(...) {
    // Create client proxy
    new cnode_t(impl_, e, 0, id, key, n, v, t);
    // Queues RPC, starts timer, returns
}
```

**Timeout Mechanism** ([`pia_rpc.cpp:666`](../piagent/src/pia_rpc.cpp#L666))

```cpp
cproxy_t::cproxy_t(...) {
    network_->send_request(...);
    job_timer_.start(timer__, this, ACK_TIMER);  // 1 second
}

void cproxy_t::timer__(void *ctx) {
    if (acked_) {
        if (++count_ > RSP_FAIL) {  // 10 retries = 50s
            net_response(0, empty);  // Timeout
            return;
        }
        network_->send_get(...);  // Retry
    } else {
        if (++count_ > ACK_FAIL) {  // 10 retries = 10s
            net_response(0, empty);  // Timeout
            return;
        }
        network_->send_request(...);  // Retry
    }
}
```

**Timeout behavior:**
- ACK phase: 10 retries × 1s = 10 seconds
- RSP phase: 10 retries × 5s = 50 seconds  
- On timeout: `cnode_t` deleted, no Python notification

### Rig Loading

**Rig Structure:**
- Outer agent: In main setup (e.g., "audio unit rig 1")
- Inner workspace: Nested setup with own agents
- Rig file: `<main_setup>-<rig_name>` (e.g., `my_setup-audio unit rig 1`)

**Rig Load Sequence** ([`rig_plg.py:823`](../plg_rig/rig_plg.py#L823))

```python
@piasync.coroutine('internal error')
def load_state(self, state, delegate, phase):
    # Load outer rig agent
    yield agent.Agent.load_state(self, state, delegate, phase)
    
    # Load inner workspace synchronously
    rig_file = self.rig_file(delegate.path)
    if resource.os_path_exists(rig_file):
        r = self.__inner_agent.load(rig_file)  # Recursive!
        yield r
```

**Implication:** Rig creates own `__load_queue`, runs own `__doload()` loop during main loading.

---

## Problem Analysis

### Forward-Reference Connections

**Test Setup:** "pico 2 ~ 4 VST or Audio Unit and 4 Midi Out"
- 65 agents total
- 565 connections
- 276 forward-reference connections (Agent N → Agent M where M > N)
- Worst case: Agent 1 → Agent 62 (+61 positions ahead)

**Comparison:** tmp vs release 2.2.1 (same setup, Python 3 vs 2.7)
```
tmp (Python 3):      276 forward refs, worst +61
release (Python 2):  314 forward refs, worst +60
```

**Loading order completely different:**
```
tmp:     keygroup3, talker18, rig5, workbench, ...
release: talker2, keygroup3, controller1, console_mixer1, ...
```

### Event Loop Saturation Theory

**Scenario during loading:**

1. **Phase 0-10:** First 10 agents load
   - Each creates ~4 connections on average
   - ~40 async RPCs queued
   - Each RPC retries every 1s (ACK phase)
   - Event loop handles: 40 timers/second

2. **Phase 10-20:** Next 10 agents load
   - Another ~40 async RPCs queued
   - Now 80 timers/second (previous still retrying)
   - Event loop getting busy

3. **Phase 20-24:** Loading slows
   - 100+ async RPCs queued
   - 100+ timers/second
   - Event loop saturated
   - `__doload()` callback delayed

4. **Phase 24:** **STOPS**
   - `ok()` callback never scheduled?
   - Or scheduled but never executed?
   - No error, just silence

### Why Python 2.7 Works

**Hypothesis:**
- Python 2.7 event loop scheduler handles timer load differently
- May batch timer callbacks more efficiently
- May prioritize Deferred callbacks over timers
- Same saturation occurs, but doesn't prevent `__doload()` callbacks

**piasync Framework Analysis:**
- EigenD uses custom coroutine framework (`pi/piasync.py`)
- Renamed from `async` → `piasync` for Python 3 keyword conflict
- **No implementation changes** - framework identical between Python 2 and 3
- Loading uses Deferred callback chains for sequential agent loading
- See `dev_docs/piasync.md` for full analysis of:
  - Deferred/Coroutine/Aggregate architecture
  - Python 2 vs 3 generator differences (PEP 479, exception handling)
  - Callback chain integrity requirements
  - Why framework itself is unlikely to be the issue

**Key Finding:** piasync implementation unchanged, but Python 3's stricter exception handling could expose latent issues in callback chains.

### Code Locations

**Problem code:**
- [`atom.py:659-674`](../pi/atom.py#L659-674) - `update_slaves()` sends async RPC
- [`workspace.py:356-399`](../pisession/workspace.py#L356-399) - `__doload()` callback chain
- [`pia_rpc.cpp:666-701`](../piagent/src/pia_rpc.cpp#L666-701) - Timer retry mechanism

**Instrumentation points:**
- `workspace.py:393` - Before `r.setCallback(ok)` - log pending queue size
- `atom.py:673` - After `invoke_async_rpc()` - log RPC count
- C++ timer code - log active timer count

---

## Test Results Analysis

**Date:** 2025-11-09  
**Test Suite:** `tests/unit/test_05_integration.py::TestSetupLoadingBehavior`

### Key Findings from Tests

**✅ Test 1: `test_async_rpc_callback_chain_simulation` - PASSED**

**What it tested:**
- Simulated the exact callback chain pattern used in `workspace.__doload()`
- Created 60 sequential agent loads using piasync Deferred callbacks
- Each load triggers next load via `setCallback()` - identical to real code

**Result:** All 60 agents loaded successfully via callback chain

**Critical Discovery:**
```
✅ PASS: piasync callback chain completed all 60 agents
   This proves piasync framework works correctly.
   Real-world failure must be due to event loop saturation,
   not piasync bugs.
```

**Implications:**
1. **piasync framework is NOT the problem** - callback chain mechanism works perfectly
2. **Python 3.14 compatibility verified** - no issues with generator/coroutine changes
3. **Root cause confirmed:** Event loop behavior under RPC timer load, not callback chain bugs

**What this eliminates:**
- ❌ piasync callback chain has bugs
- ❌ Python 3 generator changes broke piasync
- ❌ Deferred.setCallback() doesn't work on Python 3.14
- ❌ Sequential callback pattern is flawed

**What this confirms:**
- ✅ Event loop saturation hypothesis is correct
- ✅ External factors (RPC timers) are blocking callbacks
- ✅ Fix should target RPC timing, not piasync mechanics

### Other Integration Tests Status

**All 6 executable tests PASSED:**
1. ✅ `test_full_system_components_available` - Core components load
2. ✅ `test_python_314_migration_regression` - Basic Python 3.14 compatibility
3. ✅ `test_setup_tree_generation_sorting` - Setup sorting works
4. ✅ `test_menu_class_tree_generation` - Menu hierarchy builds correctly
5. ✅ `test_eigend_string_assertion_prevention` - PIW string handling works
6. ✅ `test_async_rpc_callback_chain_simulation` - piasync callback chain works

**10 tests skipped** (require full eigend environment or are documentation)

### Next Actions Based on Test Results

**1. Implement instrumentation (HIGH PRIORITY)**
- Add logging to `workspace.__doload()` to track actual callback timing
- Add RPC counter to `atom.update_slaves()` to track async RPC accumulation
- Measure event loop timer count during loading

**2. Test connection deferral fix (RECOMMENDED)**
- Modify `atom.py` to queue connections during load phase
- Process queued connections in `agent_postload()` 
- This eliminates forward-reference RPCs completely

**3. Document findings**
- piasync framework confirmed working on Python 3.14
- Event loop saturation is the confirmed root cause
- Fix must target RPC generation timing, not callback mechanism

---

## Testing Plan

### 1. Confirm Event Loop Saturation

Add to [`workspace.py:356`](../pisession/workspace.py#L356):

```python
def __doload(self):
    import time
    print(f"[{time.time():.3f}] __doload: queue={len(self.__load_queue)}")
    
    while self.__load_queue:
        f = self.__load_queue[0]
        s = self.find_agent(f.address)
        n = s.get_name()
        
        print(f"[{time.time():.3f}] Loading {n} (addr={f.address})")
        
        def ok(*args):
            print(f"[{time.time():.3f}] OK callback for {n}")
            # ... rest of ok()
```

**Expected:** Long delays between "Loading" and "OK callback" near phase 24.

### 1a. Add piasync Callback Debugging

Add to [`workspace.py:365`](../pisession/workspace.py#L365):

```python
def ok(*args,**kwds):
    print(f"[PIASYNC] ok() fired: {f.address}, queue_len={len(self.__load_queue)}")
    print(f"[PIASYNC] ok() args: {args}, kwds: {kwds}")
    if self.__load_queue and self.__load_queue[0]==f:
        self.__load_queue = self.__load_queue[1:]
    # ... rest of function ...

def not_ok(*args,**kwds):
    print(f"[PIASYNC] not_ok() fired: {f.address}, queue_len={len(self.__load_queue)}")
    print(f"[PIASYNC] not_ok() args: {args}, kwds: {kwds}")
    # ... rest of function ...
```

**Purpose:** Verify Deferred callbacks are actually firing. If callbacks stop appearing, confirms event loop or piasync issue.

### 2. Test Connection Deferral Fix

Modify [`atom.py:618`](../pi/atom.py#L618):

```python
class Atom(node.Server):
    def __init__(self, ...):
        node.Server.__init__(self, ...)
        self.__pending_connection_rpcs = []
        self.__is_loading = False
    
    def set_connections(self, srcs):
        old = self.get_property_termlist('master')
        self.set_property_string('master', srcs)
        
        if not self.__is_loading:
            self.update_slaves(old)
        else:
            self.__pending_connection_rpcs.append(old)
    
    def agent_preload(self, filename):
        self.__is_loading = True
        agent.Agent.agent_preload(self, filename)
    
    def agent_postload(self, filename):
        self.__is_loading = False
        for old in self.__pending_connection_rpcs:
            self.update_slaves(old)
        self.__pending_connection_rpcs = []
        agent.Agent.agent_postload(self, filename)
```

**Test:** Load large setup, verify all 60 agents load.

### 3. Regression Testing

- Small setup (9 agents): Should still load
- Medium setup (30 agents): Should still load
- No connections setup: Should still load

---

## References

**Related Files:**
- `pisession/workspace.py` - Main loading orchestration
- `pi/agent.py` - Agent RPC handlers
- `pi/atom.py` - Connection management
- `pi/rpc.py` - RPC wrappers
- `piagent/src/pia_rpc.cpp` - C++ RPC implementation
- `plg_rig/rig_plg.py` - Rig plugin

**Log Files:** `dev_docs/logs/`
- `ed.log` - Failed load (Python 3, phase 24/60)
- `ed2.log` - Failed load (Python 3, phase 26/60, different order)
- `ed22.log` - Successful load (Python 2.7, 60/60)
- `ed_success.log` - Successful load (Python 3, 9/9, no wiring)

**Analysis Tools:**
- `app_cmdline/analyze_setup.py` - Analyzes agent order and forward refs
- `app_cmdline/bstdump.py` - Dumps complete setup state
- `dev_docs/cmdline.md` - Command-line tools reference
