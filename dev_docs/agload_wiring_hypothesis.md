# EigenD Loading Issue: Wiring Hypothesis

## Date: 2025

## Summary
Large EigenD setups fail to load completely on Python 3 - loading stops partway through at non-deterministic points (phases 24-26 out of 60). User testing revealed: **60+ agent setup WITHOUT wiring loads successfully**, suggesting the problem is wiring/connections, not agent count.

## Key Evidence

### Loading Behavior
- **Python 3 Small Setup (9 agents)**: Loads successfully ✓
- **Python 3 Large Setup (60+ agents, NO wiring)**: Loads successfully ✓  
- **Python 3 Large Setup (60 agents WITH wiring)**: FAILS at phase 24-26 ✗
- **Python 2.7 Large Setup (60 agents WITH wiring)**: Loads successfully (15.4s) ✓

### Failure Characteristics
- Non-deterministic: Same setup fails at different points (phase 24 vs 26)
- Process alive, Workbench connects, but setup incomplete
- Missing connections/wires in loaded setup
- No hung threads (verified in debugger)
- Last loaded agent in ed.log: "audio unit rig 1 controller" at phase 24/60

## State Loading Mechanism

### Agent Loading Phase
Located in `pisession/workspace.py`:

```python
def __doload(self):
    while self.__load_queue:
        f = self.__load_queue[0]
        s = self.find_agent(f.address)
        
        # Callback chain:
        r = f.reload(s, self.__load_path)
        r.setCallback(ok)  # ok() calls __doload() again
```

Each agent's `reload()` method (in `workspace.py` line 131):
1. Calls `rpc.invoke_rpc(myid, 'loadstate', ...)` 
2. Returns a Deferred
3. Callback fires to load next agent

### State Loading RPC Handler
Located in `pi/agent.py` line 236 `rpc_loadstate()`:

**Phase 1:** Load basic agent state (properties, children)
```python
while delegate.residual:
    yield k.load_state(v, delegate, 1)
```

**Phase 2:** Load deferred state (connections)
```python
delegate.residual = delegate.deferred
while delegate.residual:
    yield k.load_state(v, delegate, 2)
```

### Connection Loading
Located in `pi/atom.py` line 623:

```python
def set_connections(self, srcs):
    old = self.get_property_termlist('master')
    self.set_property_string('master', srcs)
    self.update_slaves(old)  # Sends RPC to connected agents

def update_slaves(self, old):
    for id in new_listeners:
        id = paths.to_absolute(id, self.__connection_scope)
        rpc.invoke_async_rpc(id, 'connected', myrid)
```

**Connections are created during phase 2 of each agent's state loading**, NOT in a separate post_load phase.

### Post-Load Phase
Located in `pisession/workspace.py` line 395:

```python
def post_load(self, path):
    # Called AFTER all agents loaded
    for qa in trunk.keys():
        yield rpc.invoke_rpc(qa, 'postload', path)
```

The `agent_postload()` method (pi/agent.py line 323) is an empty stub overridden by subclasses for custom initialization.

## Analysis

### Working Theory
When an agent loads connections in phase 2 of `rpc_loadstate`, it sends async RPC calls to target agents via `update_slaves()`. If:
1. Target agent not yet loaded, RPC may fail/timeout
2. Python 3 async/coroutine handling differs from Python 2.7
3. Race condition in RPC handling causes deadlock

The reload() Deferred for the loading agent may never complete, blocking the callback chain and halting further agent loading.

### Evidence Supporting This
1. **Agent count NOT the issue**: 60+ agents without wiring loads fine
2. **Wiring IS the issue**: Same 60 agents WITH wiring fails
3. **Non-deterministic**: Different failure points suggest race condition
4. **Python 2/3 difference**: Same setup succeeds on Python 2.7
5. **Connection creation timing**: Connections loaded DURING agent loading, not after

### What Doesn't Match
- No hung threads found (connections are created via async RPC)
- Process continues running (suggests callback chain stopped, not deadlock)

## Next Investigation Steps

1. **Check if connections reference not-yet-loaded agents**
   - Parse state file connections
   - Map to agent loading order
   - See if agent 24 tries to connect to agent 60+

2. **Add logging to connection creation**
   - Log every `set_connections()` call
   - Log every `update_slaves()` RPC
   - See which connection call never returns

3. **Check Python 3 RPC/async differences**
   - Look for changes in `rpc.invoke_async_rpc()`
   - Check Deferred/coroutine handling differences
   - Search for Python 3 migration issues in async code

4. **Test connection order hypothesis**
   - Create setup where agent 1 connects to agent 60
   - See if loading fails at agent 1
   - Confirms forward-reference problem

## Related Files
- `pisession/workspace.py`: Agent loading orchestration
- `pi/agent.py`: Agent state loading, rpc_loadstate
- `pi/atom.py`: Connection management, update_slaves
- `pi/talker.py`: Example of connection creation in set_phrase
- `piasync/rpc.py`: RPC handling (need to examine)

## Logs Analyzed

All log files located in `dev_docs/logs/`:

- `ed.log`: Failed Python 3 load (24/60 phases)
- `ed2.log`: Failed Python 3 load (26/60 phases) - same setup
- `ed22.log`: Successful Python 2.7 load (60/60 phases) - same setup
- `ed_success.log`: Successful Python 3 small setup (9/9 phases)
