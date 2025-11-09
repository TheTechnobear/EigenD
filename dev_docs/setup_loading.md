# EigenD Setup Loading Process

## Date: 2025-11-09

## Overview
This document describes the complete setup loading process in EigenD, including the order of operations, state file format, rig handling, and connection creation timing.

## Setup File Format

### Database Structure
- Setup files are SQLite databases (opened via `state.open_database()`)
- Format defined in C++ piw layer (native code)
- Contains snapshot (trunk) with versioned state
- Each snapshot contains:
  - Agent list with addresses
  - Agent state (properties, children, connections)
  - Checkpoint versions
  - Agent types (0=persistent, 1=volatile/transient)

### State Term Format
State is stored as Prolog-like terms, parsed by `piw.parse_state_term()`:
- Terms have predicates and arguments
- Nested structure: `pred(arg1, arg2, pred2(...))`
- Example: `conn(index, flags, target_id, src_path, dst_path)`
- State serialized as strings and chunked for RPC (max 1200 chars)

### File Naming
Format: `<timestamp>~<label>` (split by `upgrade.split_setup()`)
- Timestamp: File modification/creation time
- Label: Human-readable setup name
- Examples: `1234567890~My Setup`, `~Factory`

## Loading Phases

### 1. Preparation Phase
**Location:** `workspace.py` `load_file()` line 416

```python
def load_file(self, path, upgrade_flag=False, post_load=True):
    # Status: "Preparing" (0%)
    snapshot = self.__backend.run_foreground_sync(upgrade.prepare_file, path, version.version)
```

**Operations:**
1. Copy setup file to temp location if needed
2. Open database and get trunk snapshot
3. Check version and upgrade if necessary
4. Call `preload` RPC on all existing agents

**File:** `upgrade.py` `prepare_file()` line 291
- Copies file to temp database
- Checks if upgrade needed (version mismatch)
- Runs upgrade scripts if needed
- Returns snapshot ready for loading

### 2. Agent Queue Building
**Location:** `workspace.py` `__load1()` line 476

```python
def __load1(self, snapshot, label, path):
    # Copy snapshot to trunk
    self.trunk.copy(snapshot, mapping, True)
    
    # Build load queue
    pending = set()
    parked = set()
    
    for i in range(0, self.trunk.agent_count()):
        a = self.trunk.get_agent_index(i)
        addr = a.get_address()
        
        if a.get_type() == 0:  # Persistent agents
            pending.add(addr)
        if a.get_type() == 1:  # Transient agents
            parked.add(addr)
```

**Agent Order:**
- Agents loaded in **index order** from database (0 to N)
- Order determined by creation/storage order, NOT dependencies
- No sorting by connections or dependencies

### 3. Sequential Agent Loading
**Location:** `workspace.py` `__doload()` line 362

```python
def __doload(self):
    while self.__load_queue:
        f = self.__load_queue[0]
        s = self.find_agent(f.address)
        
        # Async callback chain
        r = f.reload(s, self.__load_path)
        r.setCallback(ok)  # ok() pops queue and calls __doload() again
```

**Key Points:**
- **Strictly sequential** - one agent at a time
- Each agent must complete before next starts
- Callback chain: `reload()` → Deferred → `ok()` → `__doload()`
- If any agent's Deferred doesn't complete, loading **stops**

### 4. Per-Agent State Loading
**Location:** `workspace.py` `Controller.reload()` line 131

```python
@piasync.coroutine('internal error')
def reload(self, snap, filename):
    myid = self.servername_fq().as_string()
    
    # Get state diff
    diff = self.get_diff(snap.get_root(), state.Mapping()).render()
    
    # Chunk into RPC-sized pieces (1200 chars max)
    spl = []
    while diff:
        s = diff[:rpc_chunksize]
        diff = diff[len(s):]
        spl.append(s)
    
    # Send chunks via RPC
    for (i, s) in enumerate(spl):
        r = rpc.invoke_rpc(myid, 'loadstate', '%d:%d:%s' % (i, len(spl), s))
        yield r
```

**RPC Handler:** `pi/agent.py` `rpc_loadstate()` line 236

```python
@piasync.coroutine('internal error')
def rpc_loadstate(self, arg):
    # Reassemble chunks
    (i, c, a) = arg.split(':', 2)
    self.__state_buffer[i] = a
    
    if i != c:
        yield piasync.Coroutine.success('[]')  # Wait for more chunks
    
    # Parse complete state
    arg = ''.join(self.__state_buffer)
    state = piw.parse_state_term(arg)
    
    # Phase 1: Basic properties, children, structure
    while delegate.residual:
        yield k.load_state(v, delegate, 1)
    
    # Phase 2: Deferred items (connections)
    delegate.residual = delegate.deferred
    while delegate.residual:
        yield k.load_state(v, delegate, 2)
```

### 5. Connection Creation (During Phase 2)
**Location:** `pi/atom.py` `set_connections()` line 623

```python
def set_connections(self, srcs):
    old = self.get_property_termlist('master')
    self.set_property_string('master', srcs)
    self.update_slaves(old)  # ← Sends RPC to target agents

def update_slaves(self, old):
    # Calculate connection diff
    masterids = set([x.args[2] for x in self.get_property_termlist('master')])
    previous = set([x.args[2] for x in old])
    dead_listeners = previous.difference(masterids)
    new_listeners = masterids.difference(previous)
    
    # Notify disconnections
    for id in dead_listeners:
        id = paths.to_absolute(id, self.__connection_scope)
        rpc.invoke_async_rpc(id, 'disconnected', myrid)
    
    # Notify connections
    for id in new_listeners:
        id = paths.to_absolute(id, self.__connection_scope)
        rpc.invoke_async_rpc(id, 'connected', myrid)  # ← CRITICAL
```

**CRITICAL TIMING ISSUE:**
When agent N loads its connections in phase 2, it calls `update_slaves()` which sends **async RPC to target agents**. If target agent M (where M > N) hasn't been loaded yet:
1. RPC may fail (agent doesn't exist yet)
2. RPC may timeout
3. RPC may block waiting for agent
4. In Python 3, async handling may differ from Python 2.7

**This is likely the root cause of the loading failure.**

### 6. Post-Load Phase
**Location:** `workspace.py` `load_file()` line 456

```python
if post_load:
    self.call_load_status('Final Initialisation', 100)
    yield self.post_load(path)

def post_load(self, path):
    # Called AFTER all agents loaded
    for qa in trunk.keys():
        yield rpc.invoke_rpc(qa, 'postload', path)
```

**Agent Handler:** `pi/agent.py` `rpc_postload()` line 319

```python
def rpc_postload(self, arg):
    return self.agent_postload(arg)

def agent_postload(self, filename):
    pass  # Empty stub - override in subclasses
```

**Purpose:**
- Final initialization after all agents exist
- Subclasses override for custom post-load actions
- Example: Rigs load their inner workspace here

## Rig Handling

### Rig Architecture
**Location:** `plg_rig/rig_plg.py`

Rigs are "nested workspaces":
- Outer agent: `OuterAgent` (the rig plugin in main setup)
- Inner agent: `InnerAgent` (separate workspace for rig contents)
- Rig file: Separate `.state` file, same format as main setup

### Rig File Naming
```python
def rig_file(self, filename):
    # Main: /path/to/my_setup
    # Rig:  /path/to/my_setup-rig_name
    return filename + '-' + self.inner_name
```

Example:
- Main setup: `~/Setups/my_setup`
- Audio Rig 1: `~/Setups/my_setup-audio unit rig 1`
- MIDI Rig 1: `~/Setups/my_setup-midi rig 1`

### Rig Loading Timing
**Location:** `plg_rig/rig_plg.py` line 824

```python
@piasync.coroutine('internal error')
def load_state(self, state, delegate, phase):
    # Load outer agent state first
    yield agent.Agent.load_state(self, state, delegate, phase)
    
    # Then load inner workspace (rig contents)
    rig_file = self.rig_file(delegate.path)
    if resource.os_path_exists(rig_file):
        print('loading rig', self.inner_name, 'from', rig_file)
        r = self.__inner_agent.load(rig_file)
        yield r

def agent_postload(self, filename):
    # Post-load for inner workspace
    rig_file = self.rig_file(filename)
    return self.__inner_agent.post_load(rig_file)
```

**Rig Loading Order:**
1. Outer rig agent loads in main sequence (agent N)
2. During rig's `load_state()`, inner workspace loads **recursively**
3. Inner workspace goes through full loading process
4. Creates its own `__load_queue` and `__doload()` loop
5. Rig connections loaded during inner agent phase 2
6. After all main agents loaded, rig's `agent_postload()` calls inner `post_load()`

**Implication:**
- Rig loading happens **synchronously during main agent load**
- If rig has 20 agents, main load waits for all 20
- Rig connections may reference main setup agents
- Main setup agents may reference rig agents

## Connection Forward-Reference Problem

### Scenario
Given agents loading in order: A, B, C, D, E, F...

If agent B has connection to agent E:
1. Agent B loads (phase 1: properties)
2. Agent B loads connections (phase 2)
3. Calls `set_connections()` with target "E"
4. Calls `update_slaves()` → `rpc.invoke_async_rpc("E", "connected", "B")`
5. **Agent E doesn't exist yet** (not loaded)
6. RPC behavior:
   - Python 2.7: May queue or handle gracefully
   - Python 3: May throw exception or block

### Evidence This Is The Problem
1. **Agent count works**: 60+ agents without wiring loads fine
2. **Wiring fails**: Same agents WITH wiring fail
3. **Non-deterministic**: Failure point varies (race condition)
4. **Python 2/3 difference**: Same setup works on 2.7, fails on 3
5. **Stops mid-load**: reload() Deferred never completes

## Potential Decode Issues

### Unicode/Encoding Issues
**Location:** `pisession/upgrade_tools_v1.py` line 29

```python
def list_children_safe(snap):
    """
    Wrapper for list_children() that handles Python 3 Unicode decode errors.
    """
    try:
        return snap.list_children()
    except UnicodeDecodeError:
        # Python 3's C++ binding sometimes tries to decode as UTF-8
        # We need to get the raw bytes first
        ...
```

**Potential Issues:**
1. State terms contain binary data (piw.data)
2. Python 3 str/bytes distinction
3. C++ bindings may auto-decode
4. Connection IDs contain special characters

### Chunking Issues
**Location:** `workspace.py` line 143

```python
rpc_chunksize = 1200

# Split state into chunks
spl = []
while diff:
    s = diff[:rpc_chunksize]
    diff = diff[len(s):]
    spl.append(s)
```

**Potential Issues:**
1. Character vs byte slicing in Python 3
2. Multi-byte UTF-8 characters split mid-sequence
3. State term structure broken by split
4. RPC reassembly fails

**Mitigation:** Agent reassembles chunks before parsing:
```python
if i != c:
    self.__state_buffer[i] = a
    yield piasync.Coroutine.success('[]')  # Wait for all chunks

arg = ''.join(self.__state_buffer)  # Reassemble
state = piw.parse_state_term(arg)   # Parse complete term
```

## Investigation Steps

### 1. Log Connection Attempts
Add logging to `pi/atom.py` `update_slaves()`:

```python
def update_slaves(self, old):
    masterids = set([x.args[2] for x in self.get_property_termlist('master')])
    
    for id in new_listeners:
        id_abs = paths.to_absolute(id, self.__connection_scope)
        myrid = paths.to_relative(self.id(), scope=paths.id2scope(id_abs))
        
        print(f"CONNECT: {self.id()} -> {id_abs}")
        rpc.invoke_async_rpc(id_abs, 'connected', myrid)
        print(f"CONNECT DONE: {self.id()} -> {id_abs}")
```

### 2. Check Agent Existence
Verify target agents exist before connecting:

```python
def update_slaves(self, old):
    for id in new_listeners:
        id_abs = paths.to_absolute(id, self.__connection_scope)
        
        # Check if target exists
        try:
            r = rpc.invoke_rpc(id_abs, 'enumerate')
            r.wait(100)  # 100ms timeout
            if not r.status():
                print(f"WARNING: Target {id_abs} doesn't exist yet")
        except:
            print(f"ERROR: Can't reach {id_abs}")
```

### 3. Analyze Setup File
Parse setup to find forward references:

```python
# List all agents in load order
for i in range(snap.agent_count()):
    agent = snap.get_agent_index(i)
    addr = agent.get_address()
    root = agent.get_root()
    
    # Find connections
    for conn in find_connections(root):
        target = conn.args[2]
        print(f"Agent {i} ({addr}) -> {target}")
```

### 4. Test Rig Loading
Check if rigs cause the issue:
- Load setup without rigs → success?
- Load setup with rigs → failure?
- Rig connections to main setup → problem?

### 5. Compare Python 2/3 RPC
**Location:** `pi/rpc.py` line 53

```python
def invoke_async_rpc(id, name, arg, timeout=30000):
    (addr, path) = paths.breakid(id)
    arg = piw.makestring_len(arg, len(arg), 0)
    name = piw.makestring(name, 0)
    piw.tsd_rpcasync(addr.as_string(), path.make_normal(), name, arg, timeout)
```

**C++ Implementation:** `piw/src/piw_tsd.cpp` line 136

```cpp
void piw::tsd_rpcasync(const char *id, ...) {
    bct_entity_t e = tsd_getcontext();
    
    if (bct_entity_rpcasync(e, id, ...) < 0) {
        PIC_THROW("can't create async rpc");  // ← THROWS EXCEPTION
    }
}
```

**CRITICAL:** `invoke_async_rpc()` can **throw exception** if:
- Target agent ID doesn't exist
- RPC creation fails
- Entity context invalid

In Python 2.7, exception handling may differ from Python 3:
- Python 2: Exception may be caught silently or handled gracefully
- Python 3: Exception may propagate and break coroutine chain

## Related Files

### Core Loading
- `pisession/workspace.py`: Main loading orchestration
- `pisession/upgrade.py`: File preparation and version upgrade
- `pi/agent.py`: Agent-level state loading
- `pi/atom.py`: Connection management

### State System
- `piw` (C++ module): State database and term parsing
- `pi/state.py`: Python wrapper for state system
- `pi/node.py`: Node-level state loading

### RPC System
- `piasync/rpc.py`: RPC invocation
- `piasync/deferred.py`: Async/coroutine system

### Rigs
- `plg_rig/rig_plg.py`: Rig plugin with nested workspace
- Rig files: Separate `.state` files for each rig

## Logs Analysis

Log files located in `dev_docs/logs/`

### Failed Load (ed.log) - Python 3
```
eigend-backend: loaded:  24  60  in  9.6706862449646  s  audio unit rig 1 controller
```
**Stopped at agent 24/60** - "audio unit rig 1 controller" was last loaded agent

### Successful Load (ed22.log) - Python 2.7
```
eigend-backend: loaded:  60  60  in  15.4187390804  s  audio unit rig 2 controller
```
**Completed 60/60 agents** - all loaded successfully

### Key Difference
Same setup, same agents, same order - but:
- Python 2.7: Handles forward-reference connections gracefully
- Python 3: Connection RPC fails/blocks, stopping load chain

## Conclusion

The setup loading process is:
1. **Sequential** - agents load one at a time in database order
2. **Connection-unaware** - no dependency sorting
3. **Forward-referencing** - connections created during load, may target not-yet-loaded agents
4. **Rig-recursive** - rigs load nested workspaces synchronously
5. **Async RPC-based** - connections use async RPC that may fail if target doesn't exist

The Python 2→3 migration likely introduced different behavior in `invoke_async_rpc()` when the target agent doesn't exist yet, causing the loading chain to break.
