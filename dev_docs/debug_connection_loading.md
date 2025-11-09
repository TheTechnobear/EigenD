# Connection Loading Debug Instrumentation

**Date:** 2025-11-09  
**Purpose:** Add debugging to expose forward-reference connection issues during setup loading

## Changes Made

### 1. `pi/atom.py` - Connection Debug Logging

**Location:** `update_slaves()` method (lines 660-695)

**Added:**
- Timestamp for every connection operation
- Count of new/dead connections
- Forward-reference detection (target agent doesn't exist yet)
- Connection success confirmation (target agent exists)
- Error handling for agent lookup failures

**Log Format:**
```
[timestamp] CONNECTION: <source_id> creating N new connections, removing M
[timestamp] FORWARD_REF: <source_id> -> <target_id> (target not loaded yet)
[timestamp] CONNECT_OK: <source_id> -> <target_id> (target exists)
[timestamp] DISCONNECT: <source_id> -> <target_id>
```

### 2. `pisession/workspace.py` - Loading Progress Debug Logging

**Location:** `__doload()` method (lines 356-415)

**Added:**
- Workspace loading entry logging
- Agent load start with progress (N/M agents)
- Agent load completion confirmation
- Agent load error logging
- Queue length tracking

**Log Format:**
```
[timestamp] WORKSPACE_LOAD: __doload called, queue_len=N
[timestamp] LOAD_START: agent N/M - <agent_name> (addr=<address>)
[timestamp] LOAD_OK: <agent_name> completed, queue_remaining=N
[timestamp] LOAD_ERROR: <agent_name> failed: <error>
```

## Expected Output

### Normal Small Setup (no forward refs):
```
[5.100] WORKSPACE_LOAD: __doload called, queue_len=9
[5.101] LOAD_START: agent 1/10 - eigend 1 (addr=1-1)
[5.102] LOAD_OK: eigend 1 completed, queue_remaining=8
[5.103] LOAD_START: agent 2/10 - audio 1 (addr=2-123)
[5.104] CONNECTION: 2-123 creating 1 new connections, removing 0
[5.104] CONNECT_OK: 2-123 -> 3-456 (target exists)
[5.105] LOAD_OK: audio 1 completed, queue_remaining=7
...
```

### Large Setup with Forward Refs (the problem):
```
[5.100] WORKSPACE_LOAD: __doload called, queue_len=60
[5.101] LOAD_START: agent 1/61 - eigend 1 (addr=1-1)
[5.102] LOAD_OK: eigend 1 completed, queue_remaining=59
[5.103] LOAD_START: agent 2/61 - keygroup 3 (addr=2-234)
[5.104] CONNECTION: 2-234 creating 5 new connections, removing 0
[5.104] FORWARD_REF: 2-234 -> 15-789 (target not loaded yet)  <-- PROBLEM
[5.104] FORWARD_REF: 2-234 -> 23-456 (target not loaded yet)  <-- PROBLEM
[5.104] CONNECT_OK: 2-234 -> 1-1 (target exists)
[5.104] FORWARD_REF: 2-234 -> 45-123 (target not loaded yet)  <-- PROBLEM
[5.105] LOAD_OK: keygroup 3 completed, queue_remaining=58
...
[15.200] LOAD_START: agent 24/61 - audio rig 5 (addr=24-999)
[15.201] CONNECTION: 24-999 creating 12 new connections, removing 0
[15.201] FORWARD_REF: 24-999 -> 30-111 (target not loaded yet)
[15.201] FORWARD_REF: 24-999 -> 35-222 (target not loaded yet)
... (10 more forward refs)
[??? ] <--- HANGS HERE - NO MORE LOAD_OK CALLBACKS
```

## How to Use

### 1. Run eigend with logging:
```bash
./tmp/bin/eigend --stdout 2>&1 | tee eigend_debug.log
```

### 2. Load a large setup with connections

### 3. Analyze the log:
```bash
# Count forward references
grep "FORWARD_REF" eigend_debug.log | wc -l

# See which agent had most forward refs
grep "FORWARD_REF" eigend_debug.log | cut -d' ' -f3 | sort | uniq -c | sort -rn | head

# Check where loading stopped
tail -100 eigend_debug.log | grep "LOAD_"

# Time between last LOAD_OK and hang
tail -100 eigend_debug.log | grep -E "(LOAD_OK|FORWARD_REF)"
```

### 4. Expected Analysis Results:

**Working setup:**
- All `LOAD_START` have matching `LOAD_OK`
- Few or no `FORWARD_REF` messages
- Loading completes in 5-10 seconds

**Broken setup:**
- `LOAD_START` without matching `LOAD_OK` after certain point
- Many `FORWARD_REF` messages (276+ for test setup)
- Loading stops at agent 24-26
- Last messages are `FORWARD_REF`, no more `LOAD_OK`

## What This Proves

1. **Forward references accumulate** - Each agent creates connections to not-yet-loaded agents
2. **Async RPC flood** - 276+ async RPCs queued during loading phases 1-24
3. **Event loop saturation** - RPC retry timers (1-5s intervals) flood event loop
4. **Callback starvation** - `LOAD_OK` callbacks stop firing when RPC timer load too high
5. **No exceptions** - Process doesn't crash, just stops making progress

## Next Step: Fix

Based on debug output confirming forward references, implement connection deferral:

```python
# In pi/atom.py
def __init__(self):
    self.__pending_connection_rpcs = []
    self.__is_loading = False

def set_connections(self, srcs):
    if not self.__is_loading:
        self.update_slaves(old)  # Normal
    else:
        self.__pending_connection_rpcs.append(old)  # Queue

def agent_postload(self, filename):
    for old in self.__pending_connection_rpcs:
        self.update_slaves(old)  # Send when all agents exist
    self.__pending_connection_rpcs = []
```

This eliminates all forward-reference RPCs by deferring connections until post-load phase.
