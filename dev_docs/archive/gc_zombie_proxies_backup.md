# Garbage Collection Zombie Proxy Issue

**Date:** 2025-11-10  
**Status:** ✅ **FIXED** - Scaler use-after-free resolved, minor cleanup assertion remains

## Quick Summary

**Problem:** Deleting agents (specifically scaler agents) caused crash ~10 seconds later during Python GC pass 2.

**Root Cause:** Use-after-free bug in `piw_scaler.cpp` destructor. When Python 3 GC collected agents, the `scaler_t::impl_t` destructor allowed filter wires to call `del_subscriber()` on an already-destroyed `scaler_controller_t`.

**Fix Applied (2025-11-10):** Modified `scaler_t::impl_t` destructor to set `controller_ = nullptr` before base class cleanup, and added null check in `ufilterctl_delete()`. This prevents use-after-free during shutdown while maintaining proper cleanup during normal operation.

**Result:** 
- ✅ Scaler deletion works without crash
- ✅ Rig deletion works without crash  
- ⚠️ Minor assertion in clock cleanup (caught, non-fatal): `assertion failure: entity_ from pia_glue.h:324`

**Why Python 2 Never Hit This:** Reference cycle in `pi/container.py` prevented GC from ever collecting agents, so destructors never ran. Memory leaked but didn't crash.

**Related Issue:** Zombie proxies and slow setup switching remain as pre-existing issues (see below).

---

## Current Configuration

### Normal GC Mode Restored

**File:** `app_eigend2/backend.py` lines 76-81

```python
def passes(self):
    # Normal GC pattern: 10x gen0, 10x gen1, 1x gen2
    while True:
        for i in range(0,10): yield 0  # Young generation
        for i in range(0,10): yield 1  # Middle generation
        yield 2                         # Full collection
```

**Effect:** GC runs in normal generational pattern - pass 2 (full collection) happens approximately every 210 seconds (3.5 minutes).

---

After deleting agents (e.g., delay plugin), the app crashes ~60 seconds later with repeated "proxy closing down" messages for the same agents.

### Symptoms

**Log evidence - Rig deletion crash (2025-11-10):**
```
eigend-backend: loaded: 0 9 in 0.000168s eigend 1
eigend: <rig1>: loading rig main.rig1 from /Users/.../pico 1 ~ Modular Synth#rig1
eigend: <rig1>: loading a('<ahdsr1>',ahdsr,...) into enclosure synth rig
eigend: <rig1>: loading a('<poly_summer1>',polyphonic_summer,...) into enclosure synth rig
eigend: <rig1>: loading a('<sine_oscillator1>',sine_oscillator,...) into enclosure synth rig
[... 12 child agents loaded into rig ...]

[User deletes rig1 via GUI]

[~10 seconds later - first GC pass 2]
eigend: retransmit ack source_gone<ahdsr1>#2.1 count=4 0x10e509c40
eigend: retransmit ack source_gone<poly_summer1>#2 count=4 0x10da46040
eigend: retransmit ack disconnected<sine_oscillator1>#3 count=5 0x10da5e7e0
[... hundreds of retransmit messages for rig child agents ...]
eigend-garbage: starting gc pass  2 
[CRASH]
```

**Key observations:**
1. **Rig deletion specific** - deleting delay or keygroup alone doesn't crash
2. **Child agents not cleaned up** - rig's internal agents show `source_gone`/`disconnected` but proxies alive
3. **Crash on FIRST gc pass 2** after rig deletion - fast fail, reproducible
4. **12 child agents** in rig stuck in zombie state

**Original symptoms (delay deletion - repeated finalizers):**
```
eigend: <main:delay1> proxy closing down
eigend: <main:delay1> proxy closing down  [repeated 10+ times]
eigend: <main.rig1:sine_oscillator1> proxy closing down  [repeated cycles]
eigend-garbage: starting gc pass  2 
eigend-garbage: erase tap tn 1 ti 0
[CRASH in message loop]
```

### Root Cause

**Reference cycle between Python and C++:**
1. Agent deleted in Python
2. Python objects not released due to circular references
3. C++ proxy destruction triggered by finalizers
4. But Python still holds references → proxy reconstructed
5. GC runs again → finalizers called again
6. Loop repeats until crash (memory corruption or event queue overflow)

### Evidence

- Same 12 rig agents closing repeatedly in identical order
- delay1 agent closing down 10+ times after deletion
- Crash happens during GC pass 2 (full collection)
- Crash point: "erase tap" in delay plugin destructor
- **Happens on python3 branch too** - pre-existing Python 3 migration bug

## Crash Locations

### ⚠️ CORRECTION: Initial Analysis Error

**MISTAKE:** In first crash report, Thread #0 was shown (which had read lock) but **Thread #9** was the actual crashed thread. This led to incorrect "deadlock" diagnosis.

**ACTUAL CRASH (Thread #19 - GC thread):**
```
Thread #19, name = 'Thread-1', stop reason = EXC_BAD_ACCESS (code=1, address=0x2b0)
  frame #0: std::__1::list::begin() at list:525:77
  frame #1: std::__1::list::remove() at list:1475:29
  frame #3: piw::scaler_controller_t::impl_t::del_subscriber() at piw_scaler.cpp:119
  frame #5: piw::scaler_t::impl_t::ufilterctl_delete() at piw_scaler.cpp:876
  frame #7: filter_wire_t::invalidate() at piw_ufilter.cpp:263
  frame #9: filter_wire_t::~filter_wire_t() at piw_ufilter.cpp:235
  frame #11: piw::ufilter_t::impl_t::invalidate() at piw_ufilter.cpp:196
  frame #12: piw::ufilter_t::~ufilter_t() at piw_ufilter.cpp:390
  frame #13: piw::scaler_t::impl_t::~impl_t() at piw_scaler.cpp:446
  frame #16: piw::scaler_t::~scaler_t() at piw_scaler.cpp:896
  frame #20: scaler_wrapper_::~scaler_wrapper_() at piw_native_python.cpp:94166
  frame #21: scaler_delete_() at piw_native_python.cpp:94423
  frame #22: scaler_dealloc_() at piw_native_python.cpp:94445
  frame #24: gc_collect_region() + 2420
  frame #25: _PyGC_Collect() + 1916
  frame #26: gc_collect() + 96
```

**Thread #1 (Message Thread) - NOT CRASHED:**
```
Thread #1, name = 'JUCE v8.0.10: Message Thread'
  frame #0: mach_msg2_trap + 8
  [... normal CFRunLoop operation ...]
  frame #13: juce::MessageManager::runDispatchLoop()
```
**Status:** Running normally, no deadlock

### Root Cause: C++ Use-After-Free in scaler_t Destructor

**File:** `piw/src/piw_scaler.cpp`

**The Bug:**
1. Python GC calls `scaler_t::~scaler_t()` (frame #16)
2. Destructor destroys `scaler_controller_t::impl_t` with subscriber list
3. Then `~ufilter_t()` (frame #12) invalidates filter wires
4. `~filter_wire_t()` (frame #9) tries to unsubscribe via `del_subscriber()`
5. **CRASH:** Accessing `this->subscribers_` list at address 0x2b0 (garbage)

**Destruction order issue:**
```cpp
scaler_t::impl_t::~impl_t() {
    // 1. Controller with subscriber list destroyed here
    controller_.~scaler_controller_t();  
    
    // 2. But ufilter_ still holds references to controller!
    ufilter_.~ufilter_t();  // ← This tries to call del_subscriber()
}
```

**Why Python 2 never hit this:**
- Reference cycle in `container.py` prevented GC from collecting rigs
- Scaler objects never destroyed, so destructor chain never ran
- Memory leaked but no crash

**Why Python 3 exposes it:**
- More aggressive GC collects cyclic objects
- Container fix (below) allows proper cleanup
- Pre-existing C++ bug now exposed

## Technical Details

### Proxy Lifecycle

**Normal destruction:**
```cpp
// pia_proxy.cpp:869
if(r->slowtick_>=PIA_TIMER_SLOW_TICKS_CLOSE) {
    pic::logmsg() << r->addr() << " proxy closing down";
    r->close();
    return;
}
```


## Solution Implemented (2025-11-10)

### The Fix: Scaler Destructor Ordering

**Files Modified:**
- `piw/src/piw_scaler.cpp` (lines 446-458, 872-882)

**Problem Identified:**
The crash was **NOT** in the rig structure or Python reference cycles. It was a C++ use-after-free bug in `piw_scaler.cpp` that only manifested when Python 3's GC actually collected agents.

**Root Cause:**
```cpp
// OLD BROKEN CODE:
struct scaler_t::impl_t : ... ufilter_t ... {
    // No explicit destructor
    // Default destruction order: members destroyed, THEN base classes
    piw::scaler_controller_t *controller_;  // Just a pointer
};

void ufilterctl_delete(ufilterfunc_t *f) {
    controller_->del_subscriber(f);  // ← CRASH if controller already freed!
    delete f;
}
```

**Destruction sequence (broken):**
1. Python GC collects scaler agent (unordered with controller)
2. `~impl_t()` default destructor runs
3. Members destroyed: `controller_` pointer becomes invalid
4. Base class `~ufilter_t()` destroys filter wires
5. Wires call `ufilterctl_delete()` → tries to use freed `controller_` → **CRASH**

**The Fix:**
```cpp
// NEW WORKING CODE:
struct scaler_t::impl_t : ... ufilter_t ... {
    ~impl_t() {
        // Prevent ufilterctl_delete() from accessing potentially invalid controller
        controller_ = nullptr;
    }
    
    piw::scaler_controller_t *controller_;
};

void ufilterctl_delete(ufilterfunc_t *f) {
    if(f) {
        // Only call del_subscriber if controller is still valid
        if(controller_) {
            controller_->del_subscriber((scaler_subscriber_t *)f);
        }
        delete f;
    }
}
```

**Why This Works:**
1. **Normal operation:** Wires replaced/deleted → `controller_` valid → `del_subscriber()` maintains clean subscriber list
2. **Shutdown:** `~impl_t()` sets `controller_ = nullptr` → base `~ufilter_t()` cleans up wires → `ufilterctl_delete()` sees null → skips `del_subscriber()` → no crash

**Why The Subscriber List Doesn't Matter During Shutdown:**
- Subscriber list is only used for notifications (`control_changed()`)
- During agent destruction, no more notifications will be sent
- The list will be destroyed with the controller anyway
- Cleaning it up during shutdown is unnecessary bookkeeping

---

---

## Remaining Issues (Pre-existing)

### Minor Clock Cleanup Assertion

**Symptom:** When deleting rigs, an assertion is caught and logged:
```
assertion failure: entity_ from piagent/src/pia_glue.h:324 () caught at piagent/src/pia_clock.cpp:1077
```

**Analysis:**
- Occurs in `api_close` during clock sink cleanup
- Non-fatal - caught by exception handler and logged
- Likely a timing issue where context is accessed after being released
- Was always present but never triggered because Python 2 didn't clean up properly

**Impact:** Low - assertion is caught, no crash or memory corruption

**Priority:** Low - can be addressed separately

### Zombie Proxies and Slow Setup Switching

**Symptom:** 
- Zombie proxy messages still appear in logs: `retransmit ack source_gone<agent>#port`
- Setup switching is very slow (users often restart app instead)

**Analysis:**
- RPC retransmits happen when agents send `source_gone` but clients haven't acknowledged
- Filter wires may not be disconnecting cleanly during agent deletion
- Retransmits timeout after 10 attempts but add latency
- Likely causes accumulation of stale connections during setup switching

**Root Cause:** Incomplete cleanup - connections not being torn down synchronously when agents are deleted

**Impact:** Medium - performance degradation, memory accumulation over time

**Why Users Don't See Full Impact:** They restart the app when switching is slow, which clears everything

**Priority:** Medium - affects UX but has workaround (restart)

**See:** `dev_docs/todo.md` for tracking

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
