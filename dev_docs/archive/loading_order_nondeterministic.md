# Setup Loading Order Analysis: NON-DETERMINISTIC

## Date: 2025-11-09

## Critical Finding: Loading Order is Non-Deterministic

### Comparison: ed.log vs ed2.log (Same Setup, Different Runs)

Log files located in `dev_docs/logs/`

Both logs are from **same setup file**, loaded on Python 3, both **failed** at different points.

#### ed.log Sequence (Failed at phase 24):
```
Phase  Agent
-----  -----
0-1    eigend 1
1-2    interpreter 1
2-3    midi output 1
3-4    midi output 2
4-5    midi rig 1          ← Rig loads here
5-6    effect audio unit 1
6-7    midi output 3
7-8    audio unit rig 4     ← Rig loads here
8-9    audio unit rig 1     ← Rig loads here
9-10   midi output 4
10-11  midi rig 2           ← Rig loads here
11-12  effect audio unit 2
12-13  midi rig 4           ← Rig loads here
13-14  midi input 1
14-15  audio unit rig 2     ← Rig loads here
15-16  midi rig 3           ← Rig loads here
16-17  audio 1
17-18  audio unit rig 3     ← Rig loads here
...
24     audio unit rig 1 controller ← STOPPED HERE
```

#### ed2.log Sequence (Failed at phase 26):
```
Phase  Agent
-----  -----
0-1    eigend 1
1-2    interpreter 1
2-3    effect audio unit 1  ← DIFFERENT! Was #5 in ed.log
3-4    audio unit rig 2     ← DIFFERENT! Was #14 in ed.log
4-5    midi rig 4           ← DIFFERENT! Was #12 in ed.log
5-6    midi output 1        ← DIFFERENT! Was #2 in ed.log
6-7    midi input 1         ← DIFFERENT! Was #13 in ed.log
7-8    audio unit rig 4     ← DIFFERENT! Was #7 in ed.log
8-9    midi output 2        ← DIFFERENT! Was #3 in ed.log
9-10   midi rig 1           ← DIFFERENT! Was #4 in ed.log
10-11  midi output 3        ← DIFFERENT! Was #6 in ed.log
11-12  midi output 4        ← DIFFERENT! Was #9 in ed.log
12-13  audio unit rig 3     ← DIFFERENT! Was #17 in ed.log
13-14  midi rig 3           ← DIFFERENT! Was #15 in ed.log
14-15  effect audio unit 2  ← DIFFERENT! Was #11 in ed.log
15-16  midi rig 2           ← DIFFERENT! Was #10 in ed.log
16-17  audio unit rig 1     ← DIFFERENT! Was #8 in ed.log
17-18  audio 1              ← Same as ed.log
...
26     ??? ← STOPPED HERE
```

### Analysis

**Only the first 2 agents are consistent:**
- Phase 0-1: eigend 1
- Phase 1-2: interpreter 1

**After phase 2, order is COMPLETELY DIFFERENT** between runs.

### Implications

1. **Source of Non-Determinism:**
   - NOT from file reading (file is static)
   - NOT from database iteration (should be deterministic)
   - LIKELY from async operations or dict/set iteration

2. **Where Non-Determinism Comes From:**

   **Location:** `pisession/workspace.py` line 537-545
   ```python
   for c in self.index.members():
       if c.address in pending or c.address in parked:
           self.__load_queue.append(c)
   ```
   
   - `self.index.members()` may not have deterministic iteration order
   - `pending` and `parked` are **sets** (unordered in Python)
   - In Python 3.6+, dicts maintain insertion order BUT sets don't
   - Set iteration order can vary between runs

3. **Why This Matters:**
   - Different load orders create different connection timing
   - Agent X connecting to Agent Y depends on which loads first
   - Explains why failure point varies (phase 24 vs 26)
   - NOT actually a race condition - just non-deterministic ordering

4. **Why Python 2.7 Works:**
   - May have different set iteration behavior
   - May handle connection exceptions differently
   - Same non-determinism but doesn't break loading

### Code Inspection

**Location:** `pisession/workspace.py` line 476-505

```python
def __load1(self, snapshot, label, path):
    # ...
    pending = set()  # ← SET = UNORDERED
    parked = set()   # ← SET = UNORDERED
    
    for i in range(0, self.trunk.agent_count()):
        a = self.trunk.get_agent_index(i)
        addr = a.get_address()
        
        if a.get_type() == 0:
            pending.add(addr)      # ← Adding to set
        if a.get_type() == 1:
            parked.add(addr)       # ← Adding to set
    
    # ...
    
    for c in self.index.members():  # ← Iteration order?
        if c.address in pending or c.address in parked:
            self.__load_queue.append(c)
```

The queue is built by iterating `self.index.members()` and checking membership in sets. This iteration order determines loading order.

### Root Cause Update

The loading failure is caused by:
1. **Non-deterministic loading order** (set iteration)
2. **Forward-reference connections** (agent N → agent M where M not loaded yet)
3. **Exception in connection RPC** when target doesn't exist
4. **Python 3 coroutine exception handling** breaks the loading chain

The non-determinism explains why:
- Same setup fails at different points each run
- Sometimes agent X loads before Y, sometimes after
- Connection timing varies unpredictably
- Can't reproduce exact failure sequence

### Solution Requirements

Any fix must handle:
1. Connections to not-yet-loaded agents (forward references)
2. Non-deterministic loading order (can't rely on sequence)
3. Exception handling in async RPC (must not break chain)

**Best approach:** Defer ALL connection RPC until post_load phase when all agents guaranteed to exist.
