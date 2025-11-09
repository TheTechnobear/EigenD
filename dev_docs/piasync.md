# EigenD piasync System - Coroutine-Based Async Framework

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

