# CRITICAL: Python 3 Migration Bug in Agent Loading

## The Smoking Gun

Log files located in `dev_docs/logs/`

**SAME SETUP:**
- ✅ **Python 2.7**: Loads successfully - 60/60 phases in 15.42s
- ❌ **Python 3**: Fails at phase 24 or 26 - hangs forever

This is **NOT** a problem with the agents or the setup file. This is a **Python 3 migration bug** in the async callback system.

## Evidence

Log files located in `dev_docs/logs/`

### Python 2.7 (ed22.log) - SUCCESS
```
Phase 24: recorder talker
Phase 24: metronome controller 1
Phase 25: metronome controller 1
Phase 26: main keygroup
...continues...
Phase 60: audio unit rig 2 controller
✅ COMPLETE - All 24 controllers loaded successfully
```

### Python 3 FAIL-1 (ed.log)
```
Phase 24: audio unit rig 1 controller
❌ HANGS - Never proceeds to phase 25
```

### Python 3 FAIL-2 (ed2.log)
```
Phase 26: mixer controller  
❌ HANGS - Never proceeds to phase 27
```

## What This Tells Us

1. **The agents work fine** - Python 2.7 loads all of them
2. **The setup file is valid** - Python 2.7 loads it completely
3. **The async callback chain is broken in Python 3**
4. **Controllers are NOT special** - Python 2.7 loads all 24 controllers
5. **It's probabilistic** - Python 3 fails at different points each time

## The Async Callback System

From `pisession/workspace.py`, loading works via:
```python
def __doload(self):
    # Load one agent at a time
    r = f.reload(s, self.__load_path)
    r.setCallback(ok).setErrback(not_ok)
```

The `reload()` returns a Deferred, and when complete, fires a callback that loads the next agent.

### What's Different in Python 3?

Python 2 → Python 3 changes that could break this:
1. **Deferred/Future behavior changes**
2. **Callback registration timing**
3. **Exception handling in async code**
4. **String/bytes differences in RPC**
5. **Dictionary iteration order** (though fixed in 3.7+)
6. **Weak reference behavior**

## The Bug

**Hypothesis**: The callback registration or execution fails silently under Python 3.

Possible mechanisms:
1. **Callback never registered** - `setCallback()` silently fails
2. **Callback registered but never called** - execution path broken
3. **Callback called but exception swallowed** - error handler issue
4. **Deferred never fires** - completion signal lost

The fact it's **probabilistic** (fails at different phases) suggests:
- Race condition in async code
- Resource exhaustion (descriptors, memory)
- Callback queue overflow

## Why Controllers?

Controllers aren't special - Python 2.7 loads all of them fine. The pattern of "fails near controllers" is likely:
- Controllers tend to be loaded mid-to-late in sequence
- By phase 24-26, enough async load has accumulated
- Something in Python 3's async handling breaks under this load

## Investigation Path

### 1. Check Deferred Implementation
Look at `piw` module's Deferred/async implementation:
- Was it updated for Python 3?
- Are callbacks properly firing?
- Exception handling correct?

### 2. Add Callback Tracing
Instrument `workspace.py`:
```python
def __doload(self):
    print(f"__doload: loading {f.address}")
    r = f.reload(s, self.__load_path)
    
    def traced_ok(*args, **kwds):
        print(f"CALLBACK OK: {f.address}")
        ok(*args, **kwds)
    
    def traced_not_ok(*args, **kwds):
        print(f"CALLBACK NOT_OK: {f.address}")
        not_ok(*args, **kwds)
    
    r.setCallback(traced_ok).setErrback(traced_not_ok)
    print(f"Callback registered for {f.address}")
```

### 3. Check RPC Layer
In `Controller.reload()`:
```python
@async.coroutine('internal error')
def reload(self, snap, filename):
    # Does this RPC call work in Python 3?
    r = rpc.invoke_rpc(myid, 'loadstate', ...)
    yield r
    # Does yield work correctly?
```

### 4. Exception Handling
Python 3 changed exception handling. Check:
- `except:` blocks (should be `except Exception:`)
- Exception chaining
- Finally blocks in async code

### 5. String/Bytes Issues
RPC might be mixing strings and bytes:
```python
# Python 2: strings are bytes
# Python 3: strings are unicode, bytes are bytes
# If RPC layer doesn't handle this, callbacks could fail
```

## Quick Test

Add this to `workspace.py` in `__doload()`:
```python
import sys
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"About to call reload() for {f.address}", file=sys.stderr)
sys.stderr.flush()

r = f.reload(s, self.__load_path)

print(f"reload() returned: {r}", file=sys.stderr)
print(f"Setting callbacks...", file=sys.stderr)
sys.stderr.flush()

r.setCallback(ok).setErrback(not_ok)

print(f"Callbacks set, exiting __doload", file=sys.stderr)
sys.stderr.flush()
```

Run the failed setup and see:
- Does it print "Callbacks set" for phase 24?
- Does it print "About to call reload()" for phase 25?
- If not, the callback never fired

## Expected Outcome

With proper logging, we'll see one of:
1. `reload()` called for phase 25 but callback never fires
2. Callback fires but `__doload()` is never called again
3. Exception thrown somewhere and swallowed
4. `reload()` never completes (RPC hangs)

## Fix Strategy

Once we identify which async mechanism is broken:
1. Update the Deferred/coroutine implementation for Python 3
2. Fix exception handling to not swallow errors
3. Ensure callbacks are always fired
4. Add timeout per agent (not just whole load)

## Workaround (if needed)

Until fixed, could try:
- Synchronous loading (remove async)
- Smaller batch sizes
- Load agents one-by-one with explicit waits
- Revert async changes from Python 2 version

## References

Key files to investigate:
- `pisession/workspace.py` - Loading loop
- `pi/async.py` or similar - Deferred implementation  
- `pi/rpc.py` - RPC layer
- `pisession/controller.py` - Controller.reload()
