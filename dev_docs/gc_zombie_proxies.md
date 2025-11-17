# Zombie Proxies and Slow Setup Switching

## Problem Description

### Symptoms
- Zombie proxy messages still appear in logs: `retransmit ack source_gone<agent>#port`
- Setup switching is very slow (users often restart app instead)

### Analysis
- RPC retransmits happen when agents send `source_gone` but clients haven't acknowledged
- Filter wires may not be disconnecting cleanly during agent deletion
- Retransmits timeout after 10 attempts but add latency
- Likely causes accumulation of stale connections during setup switching

### Root Cause
Incomplete cleanup - connections not being torn down synchronously when agents are deleted

### Impact
- **Severity:** Medium - performance degradation, memory accumulation over time
- **User Experience:** They restart the app when switching is slow, which clears everything
- **Priority:** Medium - affects UX but has workaround (restart)

**See:** `dev_docs/todo.md` for tracking

--------------------------- 


## Technical Details

### Zombie Pattern
- Proxy `slowtick_` counter reaches `PIA_TIMER_SLOW_TICKS_CLOSE`
- `close()` called, proxy destroyed
- But Python finalizer runs again later
- Proxy recreated and destroyed repeatedly

### Python 2 vs 3 Differences

**Python 2.7:**
- `__del__` finalizers called once when refcount=0
- GC less aggressive on generation 2 collection
- Weaker cycle detection

**Python 3:**
- `__del__` can be called multiple times if cycles exist
- GC more aggressive, runs generation 2 more frequently
- Better cycle detection exposes hidden reference issues

## Debugging Plan

### 1. Identify Which Objects Are Zombies

Add instrumentation to track object lifecycle:

```python
# In pi/agent.py
class Agent:
    def __init__(self, ...):
        print(f"Agent.__init__: {self.get_address()}")
        # ... existing code

    def __del__(self):
        print(f"Agent.__del__ CALLED: {getattr(self, '_Agent__address', 'unknown')}")
        # Add stack trace to see who's calling
        import traceback
        traceback.print_stack()
```

### 2. Find Reference Cycles

Use `gc` module to inspect cycles:

```python
# Add to backend.py run_pass() before gc.collect():
import gc
gc.set_debug(gc.DEBUG_SAVEALL)  # Save all garbage to gc.garbage
o = gc.collect(p)
if gc.garbage:
    print(f"Found {len(gc.garbage)} uncollectable objects:")
    for obj in gc.garbage[:10]:  # Show first 10
        print(f"  {type(obj)}: {repr(obj)[:100]}")
        # Show what's referencing it
        referrers = gc.get_referrers(obj)
        print(f"    {len(referrers)} referrers")
```

### 3. Check C++ Proxy State

Add logging to proxy destructor:

```cpp
// In piagent/src/pia_proxy.cpp around line 869
pic::logmsg() << r->addr() << " proxy closing down (tick=" << r->slowtick_ << ")";

// Add in pia_proot_t::close() to track state
pic::logmsg() << addr() << " proxy close() called (already_closed=" << (closed_ ? "yes" : "no") << ")";
```

### 4. Likely Culprits


**Structure:**
```python
class OuterAgent(agent.Agent):  # The rig itself
    def __init__(self):
        self.__inner_agent = InnerAgent(self)  # Nested agent
        self.__workspace = ...  # Holds child agents

class InnerAgent(agent.Agent):  # Inside the rig
    def __init__(self, outer):
        self.__workspace = workspace(...)  # CYCLE: holds outer ref

    def unload(self, destroy):
        self.__workspace.unload_all(destroy)  # Should clean up children
        self.__workspace.shutdown()
```

**Suspected reference cycle:**
```
OuterAgent (rig)
  ├─> __inner_agent (InnerAgent)
  │     ├─> __workspace (Workspace)
  │     │     ├─> members dict {id: child_agent}
  │     │     │     ├─> ahdsr1 (Agent)
  │     │     │     ├─> poly_summer1 (Agent)
  │     │     │     └─> sine_oscillator1 (Agent)
  │     │     └─> parent ref back to outer?  ← CYCLE!
  │     └─> __outer ref?  ← CYCLE!
  └─> __domain (clockdomain)
```

**Evidence from logs:**
- Child agents (`ahdsr1`, `poly_summer1`, etc.) show `source_gone`
- But their proxies never close
- Workspace likely holds references even after `unload_all()`
- GC finds cycle → calls `__del__` → partial cleanup → crash

**Other files to check for reference cycles:**

1. **`pisession/workspace.py`** - Workspace management
   - Check `members` dict, `index` references
   - Verify `unload_all()` breaks all references
   - Look for parent/child bidirectional links

2. **`pi/agent.py`** - `__subsystems` dict
3. **`pi/atom.py`** - `__slaves` and connection tracking
4. **`pi/node.py`** - Server/Client cross-references
5. **`pi/proxy.py`** - Callbacks and proxy references

**Common patterns to look for:**
```python
# Parent holds child
self.__children[id] = child

# Child holds parent
child.parent = self  # ← CYCLE!

# Fix: Use weakref
import weakref
child.parent = weakref.ref(self)  # or WeakValueDictionary
```

## Proposed Solutions

### 1. Identify Reference Cycles

Add logging to track object lifetimes:

```python
# In pi/agent.py
def __del__(self):
    print(f"Agent finalizer called: {self.address()}")

# In pi/atom.py
def close_server(self):
    print(f"Atom close_server: {self.address()}")
    # Break cycles explicitly
    self.__slaves = None
    self.__connections = None
```

### 2. Break Cycles in Cleanup

Likely culprits:
- `pi/agent.py`: `__subsystems` dict holding references
- `pi/atom.py`: `__slaves` and connection management
- `pi/node.py`: `Server` and `Client` cross-references
- `pi/proxy.py`: Proxy holding Python callbacks

### 3. Use weakref Where Appropriate

```python
import weakref

class Agent:
    def __init__(self):
        self.__subsystems = weakref.WeakValueDictionary()
```

### 4. Explicit Cleanup Protocol

```python
def close_server(self):
    # Break cycles BEFORE calling parent
    if hasattr(self, '__subsystems'):
        for subsys in list(self.__subsystems.values()):
            subsys.close_server()
        self.__subsystems.clear()

    # Now safe to call parent
    super().close_server()
```

---

## Related Files

- `piagent/src/pia_proxy.cpp` - C++ proxy management
- `pi/agent.py` - Python agent base class
- `pi/atom.py` - Connection management
- `pi/node.py` - Server/Client infrastructure
- `app_eigend2/backend.py` - GC thread

## References

- Python 3 `__del__` behavior: https://docs.python.org/3/reference/datamodel.html#object.__del__
- Reference cycles: https://docs.python.org/3/library/gc.html
- weakref module: https://docs.python.org/3/library/weakref.html