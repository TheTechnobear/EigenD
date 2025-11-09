# EigenD piasync System - Coroutine-Based Async Framework

**Date:** 2025-11-09  
**Context:** Python 3.14 migration - analyzing async behavior differences

---

## Executive Summary

### What is piasync?

**piasync** is EigenD's custom coroutine-based asynchronous framework, built on Python generators. It provides:
- **Deferred results** (like Twisted's Deferred)
- **Coroutines** via generator-based cooperative multitasking
- **Aggregates** for parallel async operation coordination
- **Event loop integration** via callback chains

**Important:** piasync predates Python 3.5's `asyncio` module and does **not** use it. EigenD's event loop is implemented in C++ (`piw` layer), not Python.

### Migration Context

**Python 2.7 → Python 3.14:**
- Module renamed: `pi.async` → `pi.piasync` (Python 3 made `async` a keyword)
- **Implementation unchanged** - no code changes to piasync.py internals
- Simple search/replace: `async.` → `piasync.` everywhere
- All functionality preserved

### Critical Question: Generator Behavior Changes?

**Status:** ⚠️ **POTENTIAL ISSUE IDENTIFIED**

While piasync implementation is unchanged, **Python 3 changed generator exception handling** in ways that could affect EigenD's async behavior.

---

## piasync Architecture

### 1. Deferred Class

**Purpose:** Represents a future result (success or failure) with callbacks.

**States:**
- `__result = None` - Not completed
- `__result = (True, args, kwds)` - Succeeded
- `__result = (False, args, kwds)` - Failed

**Usage Pattern:**
```python
def do_something():
    r = piasync.Deferred()
    
    def callback():
        # ... do work ...
        r.succeeded(result)  # or r.failed(error)
    
    schedule_callback(callback)
    return r  # Return immediately

# Caller attaches callbacks
r = do_something()
r.setCallback(on_success).setErrback(on_error)
```

**Key Properties:**
- Callbacks fire immediately if result already set
- Thread-safe via `@utils.nothrow` decorator
- Can chain: one Deferred's callback returns another Deferred
- Single-fire: callbacks trigger only once

### 2. Coroutine Class

**Purpose:** Generator-based cooperative multitasking via `yield`.

**Usage Pattern:**
```python
@piasync.coroutine('internal error')
def load_agents(agents):
    for agent in agents:
        result = yield agent.load()  # Wait for async operation
        if not result:
            yield piasync.Coroutine.failure('load failed')
    yield piasync.Coroutine.success()
```

**How It Works:**

1. **Decorator wraps generator function:**
   ```python
   def coroutine(*fargs,**fkwds):
       def handler(ei):
           traceback.print_exception(*ei)
           return Coroutine.failure(*fargs,**fkwds)
       
       def decorator(func):
           def newfunc(*gargs,**gkwds):
               return Coroutine(func(*gargs,**gkwds),handler)
           return newfunc
       return decorator
   ```

2. **Coroutine drives generator via send()/throw():**
   ```python
   def __doit(self,*a_,**k_):
       while True:
           try:
               result = self.__generator.send(result)
           except StopIteration:
               result = self.success()
           except:
               result = self.__handler(sys.exc_info())
           
           # If result is Deferred, attach callback and wait
           if isinstance(result,DeferredDecoder):
               if result.deferred.status() is None:
                   result.deferred.setCallback(self.__doit).setErrback(self.__doit)
                   return
   ```

3. **Yield protocol:**
   - `yield Deferred` - Wait for async operation
   - `yield Coroutine.success()` - Complete successfully
   - `yield Coroutine.failure()` - Complete with error
   - `yield Coroutine.exception(e)` - Raise exception in generator

**Exception Handling:**
```python
@piasync.coroutine('default error message')
def my_func():
    try:
        result = yield some_operation()
    except SomeError as e:
        yield piasync.Coroutine.failure(str(e))
    yield piasync.Coroutine.success(result)
```

### 3. Aggregate Class

**Purpose:** Coordinate multiple parallel async operations.

**Usage Pattern:**
```python
agg = piasync.Aggregate(accumulate=True, progress=callback)
for i, item in enumerate(items):
    r = item.process()
    agg.add(i, r)
agg.enable()

# Wait for all to complete
result = yield agg
if result.status():
    print("Successes:", agg.successes())
    print("Failures:", agg.failures())
```

**Key Features:**
- Tracks outstanding operations
- Can accumulate successes/failures separately
- Progress callback: `progress(agg, completed, total)`
- Completes when all operations finish (after `enable()` called)
- Single result: success if all succeed, failure if any fail

---

## Loading Process and piasync

### Workspace Loading Flow

**File:** `pisession/workspace.py` lines 356-399

```python
def __doload(self):
    while self.__load_queue:
        f = self.__load_queue[0]
        s = self.find_agent(f.address)
        
        def ok(*args,**kwds):
            if self.__load_queue and self.__load_queue[0]==f:
                self.__load_queue = self.__load_queue[1:]
            f.enable_save()
            self.__doload()  # RECURSIVE CALLBACK
        
        def not_ok(*args,**kwds):
            if self.__load_queue and self.__load_queue[0]==f:
                self.__load_queue = self.__load_queue[1:]
            f.enable_save()
            self.__doload()  # RECURSIVE CALLBACK
        
        r = f.reload(s,self.__load_path)
        r.setCallback(ok).setErrback(not_ok)
        break
```

**Critical Pattern:**
- **Sequential loading:** One agent at a time
- **Callback-based recursion:** `ok()` calls `__doload()` for next agent
- **Deferred chain:** Each `reload()` returns Deferred, callback advances queue

### Agent State Loading

**File:** `pi/agent.py` lines 236-280

```python
@piasync.coroutine('internal error')
def rpc_loadstate(self,arg):
    # Phase 1: Reassemble chunked state
    state = piw.parse_state_term(arg)
    delegate = LoadResults()
    delegate.set_residual(self,state)
    
    # Phase 2: Load agent state (connections created here!)
    yield self.load_agent_state(delegate)
    
    # Phase 3: Process residual state
    while delegate.residual:
        r = delegate.residual
        delegate.residual = {}
        while r:
            (k,v) = r.popitem()
            yield k.load_state(v,delegate,1)
    
    # Return errors
    yield piasync.Coroutine.success(delegate.retval())
```

**Each `yield`:**
- Suspends coroutine
- Waits for nested Deferred/Coroutine to complete
- Resumes when result available

---

## Python 2 vs 3 Generator Differences

### 1. StopIteration Handling (PEP 479)

**Python 2.7:**
```python
def generator():
    yield 1
    raise StopIteration  # Silently ends iteration
```

**Python 3.7+:**
```python
def generator():
    yield 1
    raise StopIteration  # RuntimeError: generator raised StopIteration
```

**Impact on piasync:**
```python
# In Coroutine.__doit():
except StopIteration:
    result = self.success()
```

✅ **No issue** - piasync catches StopIteration explicitly at generator boundary.

### 2. Generator Exception Propagation

**Python 2.7:**
- Exceptions in generators could be caught at multiple levels
- Generator.throw() behavior less strict
- Exception context less explicit

**Python 3:**
- Stricter exception chain tracking (`__context__`, `__cause__`)
- Generator.throw() more predictable
- Unhandled exceptions propagate more consistently

**Impact on piasync:**
```python
def __doit(self):
    try:
        result = self.__generator.send(result)
    except GeneratorExit:
        raise
    except StopIteration:
        result = self.success()
    except:
        traceback.print_exc(limit=None)
        result = self.__handler(sys.exc_info())
```

⚠️ **POTENTIAL ISSUE** - Broad `except:` clause may handle exceptions differently.

### 3. Generator Cleanup (Context Managers)

**Python 2.7:**
- Generator cleanup less strict
- `finally` blocks sometimes skipped on GC

**Python 3:**
- Generators properly close with GeneratorExit
- `finally` blocks always execute

✅ **Improvement** - Python 3 is more predictable.

### 4. Async/Await Keywords (Python 3.5+)

**Python 2.7:** `async` and `await` are regular identifiers

**Python 3.5+:** `async` and `await` are keywords

✅ **Handled** - Module renamed `piasync`, no `async`/`await` syntax used.

### 5. Python's asyncio Module

**Important:** EigenD does **NOT** use Python's `asyncio` module at all.

- ❌ No `import asyncio` in EigenD codebase (only in SCons build tools)
- ❌ No `async def` or `await` syntax anywhere
- ❌ No asyncio event loop integration
- ✅ Uses custom `piasync` framework predating Python 3.5's asyncio
- ✅ Event loop is C++ based (`piw` layer), not Python asyncio

**Why this matters:**
- Python 3.5+ asyncio changes are **irrelevant** to EigenD
- Generator-based coroutines predate native async/await
- piasync uses old-style `@coroutine` + `yield`, not `async`/`await`
- Event loop scheduling is in C++, not affected by asyncio changes

**Conclusion:** Python's asyncio module and its evolution have zero impact on EigenD's async behavior.

---

## Could asyncio Replace piasync?

### Short Answer: No - Different Purposes and Incompatible Architecture

While both piasync and asyncio provide async/await-style programming, they serve **fundamentally different purposes** and are **architecturally incompatible**.

### Purpose Comparison

| Aspect | piasync | asyncio |
|--------|---------|---------|
| **Created** | 2009 (EigenD project) | 2012 (PEP 3156), stdlib in Python 3.4+ |
| **Event Loop** | C++ (piw layer) | Pure Python |
| **I/O Model** | Custom UDP-based RPC, audio callbacks, MIDI | TCP/UDP sockets, files, subprocesses |
| **Integration** | Deeply embedded in C++ audio engine | Python-only |
| **Real-time** | Audio-thread safe, RT constraints | No RT guarantees |
| **Threading** | Tight C++/Python integration | Python GIL bound |

### Architectural Incompatibility

**1. Event Loop Ownership**

```python
# piasync: Event loop is C++ (piw layer)
r.thing = piw.thing()                           # C++ object
piw.tsd_thing(r.thing)                          # Register with C++ thread-specific data
r.thing.set_slow_trigger_handler(callback)     # C++ callback mechanism
r.thing.trigger_slow()                          # C++ event loop schedules

# asyncio: Event loop is Python
loop = asyncio.get_event_loop()                 # Pure Python
loop.call_soon(callback)                        # Python scheduler
```

**piasync bridges Python ↔ C++ event loops.** asyncio is Python-only.

**2. Real-Time Audio Integration**

EigenD's core is a **real-time audio engine**:
- Audio callbacks run on RT thread (microsecond precision)
- RPC system uses UDP with custom protocol
- Network layer uses `select()` in C++ (see `pia_udpnet_*.cpp`)
- Python callbacks scheduled via `piw.tsd_thing()` (thread-specific data)

**asyncio cannot:**
- Schedule callbacks on C++ audio threads
- Integrate with custom C++ event loops
- Provide RT guarantees
- Bridge Python GIL with RT audio threads

**3. RPC and Network Protocol**

```python
# piasync + C++ RPC layer
rpc.invoke_async_rpc(agent_id, 'method', args)
# → Python calls into C++ (pia_rpc.cpp)
# → C++ sends UDP packet with custom protocol
# → C++ timer retries if no ACK/RSP
# → C++ schedules Python callback via tsd_thing()

# asyncio equivalent would need:
async def call_rpc(agent_id, method, args):
    # Would need to rewrite entire RPC system in Python
    # Would lose RT audio integration
    # Would need to reimplement UDP protocol
    # Cannot schedule on C++ threads
```

**4. Backwards Compatibility**

EigenD codebase has:
- 100+ `@piasync.coroutine` decorated functions
- Deeply integrated with C++ `piw` layer (audio, MIDI, network)
- 15+ years of production use
- Complex timing dependencies on C++ event loop

**Migrating to asyncio would require:**
- ❌ Rewrite entire async framework (~5000+ lines)
- ❌ Rewrite C++/Python bridge
- ❌ Rewrite RPC protocol implementation
- ❌ Lose RT audio integration
- ❌ Break all existing plugins

### Why "async" Name Collision Was Coincidence

**piasync (2009):**
- Named "async" because it provides asynchronous operations
- Predates Python 3.5's `async`/`await` by 6 years
- Generic English word for async programming

**Python asyncio (2012-2015):**
- PEP 3156 (2012): Proposed asyncio
- Python 3.4 (2014): Added asyncio to stdlib
- Python 3.5 (2015): Made `async`/`await` keywords
- Generic approach to async I/O

**Collision:** Both chose obvious English word for async operations. Pure coincidence.

### When You WOULD Use asyncio

asyncio is great for:
- ✅ Pure Python async I/O (web servers, HTTP clients)
- ✅ Concurrent network operations
- ✅ New Python 3.5+ projects
- ✅ Standard library integration (aiohttp, etc.)

asyncio is NOT suitable for:
- ❌ Bridging Python with C++ event loops
- ❌ Real-time audio applications
- ❌ Custom network protocols in C++
- ❌ Legacy codebases with custom async frameworks

### Conclusion

**piasync and asyncio are like:**
- **piasync:** Custom racing suspension system for a Formula 1 car (integrated with engine, transmission, aerodynamics)
- **asyncio:** Off-the-shelf suspension kit for a street car (works great for intended purpose)

You can't swap one for the other without rebuilding the entire vehicle.

**For EigenD:** piasync is the correct tool. It's deeply integrated with the C++ audio engine and designed for EigenD's specific real-time requirements. The name collision with Python 3's `async` keyword was unfortunate but coincidental.

---

## Setup Loading Issue: Potential piasync Factors

### Current Problem Recap

**Symptoms:**
- Large setups (60+ agents, 276 forward-ref connections) stop loading at phase 24-26
- No exceptions logged
- Same setup loads on Python 2.7
- Setup without connections loads fine

**Current Hypothesis:** Event loop saturation from 276+ async RPC retries

### piasync-Related Considerations

#### 1. Exception Handling in Coroutines

**Code:** `pi/atom.py` lines 659-674
```python
def update_slaves(self, old):
    # Calculate diff
    for id_abs in added:
        rpc.invoke_async_rpc(id_abs, 'connected', myrid)
        # NO ERROR CHECKING - fire and forget
```

**Question:** If invoke_async_rpc throws in Python 3, does it break parent coroutine?

**Analysis:**
- `invoke_async_rpc()` doesn't raise exceptions (returns immediately)
- No `yield` in `update_slaves()` - not a coroutine itself
- Called from `set_connections()` which IS in a coroutine context

**Code:** `pi/atom.py` lines 618-630
```python
def set_connections(self, srcs):
    # ... parse connections ...
    self.update_slaves(old)  # SYNCHRONOUS CALL
```

**Conclusion:** `update_slaves()` is synchronous - exceptions would propagate to caller.

**Verification needed:** Does `rpc.invoke_async_rpc()` ever raise? Check `pi/rpc.py`.

#### 2. Deferred Callback Chain Integrity

**Critical code:** `pisession/workspace.py` lines 356-399

```python
def __doload(self):
    # ...
    r = f.reload(s,self.__load_path)
    r.setCallback(ok).setErrback(not_ok)
    break

def ok(*args,**kwds):
    # ...
    self.__doload()  # Next iteration
```

**Question:** Could Python 3 prevent callback from firing?

**Scenarios:**
1. **Deferred never completes** - callback never fires
2. **Exception in callback** - caught by `@utils.nothrow`, logged
3. **Event loop starvation** - callbacks queued but not executed

**Analysis:**
- Deferred callbacks fire synchronously when result available
- If result already set, `setCallback()` calls immediately
- Only async if result not yet available

**Python 2 vs 3 difference:**
- Callback execution mechanism unchanged
- Event loop (piw C++ layer) handles scheduling
- Pure Python differences shouldn't affect this

#### 3. Generator State Preservation

**Code:** `pi/agent.py` lines 236-280
```python
@piasync.coroutine('internal error')
def rpc_loadstate(self,arg):
    # Multiple yields across phases
    yield self.load_agent_state(delegate)  # Phase 2
    while delegate.residual:
        yield k.load_state(v,delegate,1)  # Phase 3
```

**Question:** Could Python 3 lose generator state during suspension?

**Analysis:**
- Generator state (locals, stack) managed by interpreter
- Python 3 more robust about preserving state than Python 2
- No evidence of state corruption

**Conclusion:** ✅ Python 3 is better at this, not worse.

### 4. Uncaught Exceptions Breaking Chains

**Most Likely Issue:**

**Hypothesis:** Some exception occurs during loading that:
1. Python 2.7: Caught by loose exception handling, logged, loading continues
2. Python 3.14: Propagates differently, breaks callback chain silently

**Evidence:**
- No exception logged → exception caught somewhere
- Loading stops → callback chain broken
- Non-deterministic → depends on load order (timing)

**Test needed:**
```python
# In pisession/workspace.py __doload()
def ok(*args,**kwds):
    print(f"DEBUG: ok() called for {f.address}, args={args}, kwds={kwds}")
    if self.__load_queue and self.__load_queue[0]==f:
        self.__load_queue = self.__load_queue[1:]
    # ... rest of function ...

def not_ok(*args,**kwds):
    print(f"DEBUG: not_ok() called for {f.address}, args={args}, kwds={kwds}")
    # ... rest of function ...
```

---

## Recommendations

### 1. Immediate Testing

Add debug logging to confirm callback execution:

**File:** `pisession/workspace.py` line 365

```python
def ok(*args,**kwds):
    print(f"[PIASYNC] ok() fired: {f.address}, queue_len={len(self.__load_queue)}")
    # ... existing code ...

def not_ok(*args,**kwds):
    print(f"[PIASYNC] not_ok() fired: {f.address}, queue_len={len(self.__load_queue)}")
    # ... existing code ...
```

**Expected behavior:**
- Should see one `ok()` or `not_ok()` per agent
- Should see queue decreasing: 60 → 59 → 58 → ... → 0

**Actual behavior (predicted):**
- See callbacks up to phase 24-26
- Then silence → callback chain broken

### 2. Exception Audit

Check if `invoke_async_rpc` can raise:

**File:** `pi/rpc.py` line 53

```python
def invoke_async_rpc(id, name, arg, timeout=30000):
    try:
        (addr, path) = paths.breakid(id)
        network.call_async(addr, path, name, arg, timeout)
    except Exception as e:
        print(f"[PIASYNC] invoke_async_rpc EXCEPTION: {e}")
        traceback.print_exc()
        # Should we suppress or propagate?
```

### 3. Coroutine Exception Handling

Verify piasync exception handling is robust:

**File:** `pi/piasync.py` line 265

```python
def __doit(self,*a_,**k_):
    while True:
        try:
            # ... generator.send() ...
        except GeneratorExit:
            print('[PIASYNC] GeneratorExit caught')  # Should never happen
            raise
        except StopIteration:
            result = self.success()
        except:
            print('[PIASYNC] Exception in coroutine:')
            traceback.print_exc(limit=None)
            result = self.__handler(sys.exc_info())
```

### 4. Compare Python 2 vs 3 Exception Traces

Run same setup on both, compare exception logs:

```bash
# Python 2.7 (release branch)
./release/bin/eigend --stdout 2>&1 | grep -E 'Exception|Error|Traceback' > py2_errors.log

# Python 3.14 (current branch)
./tmp/bin/eigend --stdout 2>&1 | grep -E 'Exception|Error|Traceback' > py3_errors.log

diff py2_errors.log py3_errors.log
```

---

## Conclusions

### Summary of Findings

1. **Migration was minimal:** Just renamed `async` → `piasync` (keyword conflict)
2. **No piasync implementation changes:** Core framework unchanged
3. **Generator differences exist:** Python 3 stricter exception handling
4. **Callback chain integrity critical:** `__doload()` depends on callbacks firing

### Likely vs Unlikely Causes

**Unlikely:**
- ❌ Generator state corruption - Python 3 more robust
- ❌ StopIteration propagation - piasync handles explicitly
- ❌ Event loop changes - C++ layer unchanged

**Likely:**
- ⚠️ Exception handling differences - Python 3 stricter propagation
- ⚠️ Exception suppression - different behavior in broad `except:` clauses
- ✅ Event loop saturation - too many timer callbacks (original hypothesis)

### Connection to Setup Loading Issue

**Primary issue remains:** Event loop saturation from 276+ async RPC operations

**piasync contribution:** None directly, BUT:
- Callback chains depend on event loop responsiveness
- If event loop saturated, callbacks delayed indefinitely
- Python 3 may schedule callbacks differently under load

**Recommendation:** Original fix (defer connections to post-load) still best approach.

### Other Implications

**General robustness:**
- Python 3's stricter exception handling may expose latent bugs
- Broad `except:` clauses may behave differently
- More predictable cleanup (finally blocks) is an improvement

**Potential issues elsewhere:**
- Any code that assumes Python 2's loose exception handling
- Generator functions with `raise StopIteration` (PEP 479)
- Code that relies on specific exception chain behavior

---

## Further Investigation

### If setup loading fix doesn't work:

1. **Add comprehensive debug logging** to piasync.py:
   - Log every Deferred state change
   - Log every Coroutine yield/resume
   - Track callback execution

2. **Profile event loop saturation:**
   - Count active timer callbacks
   - Count pending Deferred objects
   - Measure callback execution time

3. **Bisect Python versions:**
   - Test on Python 3.7, 3.9, 3.11, 3.14
   - Identify when behavior changed

4. **Unit test piasync:**
   - Create stress test with 1000+ Deferred objects
   - Test callback chain integrity under load
   - Compare Python 2 vs 3 behavior

---

**Last Updated:** 2025-11-09  
**Status:** Documentation complete, testing needed
