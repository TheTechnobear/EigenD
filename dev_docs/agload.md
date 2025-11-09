# Setup Load Analysis

**Test Setup:** `pico 2 ~ 4 VST or Audio Unit and 4 Midi Out`  
**Location:** `./tmp/resources/state/pico 2 ~ 4 VST or Audio Unit and 4 Midi Out`  
**Log Source:** Analysis of module loading from `dev_docs/logs/ed.log`

## Testing Commands

```bash
# Run eigend with this setup
./tmp/bin/eigend --stdout 2>&1 | tee eigend.log

# Analyze setup structure
./tmp/bin/analyze_setup --db "./tmp/resources/state/pico 2 ~ 4 VST or Audio Unit and 4 Midi Out"

# Dump setup details
./tmp/bin/bstdump --db "./tmp/resources/state/pico 2 ~ 4 VST or Audio Unit and 4 Midi Out"

# List agents
./tmp/bin/bstlist --db "./tmp/resources/state/pico 2 ~ 4 VST or Audio Unit and 4 Midi Out"
```

## Overview

Analysis of module loading from `dev_docs/logs/ed.log`.

Each module is listed with the actions performed on it during setup loading:
- **loading**: Module is being loaded into an enclosure
- **relation**: Relation/connection is being created for the module
- **canonicalised**: Module version is being canonicalised/upgraded

## Module Actions Summary

| Module | Loading | Relation | Canonicalised |
|--------|---------|----------|---------------|
| `<audio1>` | 1 | 1 | 1 |
| `<audio_unit1>` | 5 | 5 | 5 |
| `<audio_unit2>` | 5 | 5 | 5 |
| `<clicker1>` | 1 | 1 | 1 |
| `<console_mixer1>` | 1 | 1 | 1 |
| `<controller1>` | 1 | 1 | 1 |
| `<controller11>` | 1 | 1 | 1 |
| `<controller12>` | 1 | 1 | 1 |
| `<controller13>` | 1 | 1 | 1 |
| `<controller14>` | 1 | 1 | 1 |
| `<controller2>` | 1 | 1 | 1 |
| `<controller3>` | 1 | 1 | 1 |
| `<controller7>` | 1 | 1 | 1 |
| `<controller8>` | 1 | 1 | 1 |
| `<delay1>` | 1 | 1 | 1 |
| `<drummer1>` | 1 | 1 | 1 |
| `<interpreter1>` | 1 | 1 | 2 |
| `<keygroup1>` | 1 | 1 | 1 |
| `<keygroup2>` | 1 | 1 | 1 |
| `<keygroup3>` | 1 | 1 | 1 |
| `<keygroup4>` | 1 | 1 | 1 |
| `<metronome1>` | 1 | 1 | 1 |
| `<midi_clock1>` | 4 | 4 | 4 |
| `<midi_converter1>` | 4 | 4 | 4 |
| `<midi_input1>` | 1 | 1 | 1 |
| `<midi_output1>` | 1 | 1 | 1 |
| `<midi_output2>` | 1 | 1 | 1 |
| `<midi_output3>` | 1 | 1 | 1 |
| `<midi_output4>` | 1 | 1 | 1 |
| `<pico_manager1>` | 1 | 1 | 1 |
| `<recorder1>` | 8 | 8 | 8 |
| `<rig1>` | 1 | 1 | 1 |
| `<rig2>` | 1 | 1 | 1 |
| `<rig3>` | 1 | 1 | 1 |
| `<rig4>` | 1 | 1 | 1 |
| `<rig5>` | 1 | 1 | 1 |
| `<rig6>` | 1 | 1 | 1 |
| `<rig7>` | 1 | 1 | 1 |
| `<rig8>` | 1 | 1 | 1 |
| `<scale_manager1>` | 1 | 1 | 1 |
| `<scaler1>` | 8 | 8 | 8 |
| `<scheduler1>` | 1 | 1 | 1 |
| `<summer1>` | 4 | 4 | 4 |
| `<talker1>` | 1 | 1 | 1 |
| `<talker10>` | 1 | 1 | 1 |
| `<talker11>` | 1 | 1 | 1 |
| `<talker14>` | 1 | 1 | 1 |
| `<talker15>` | 1 | 1 | 1 |
| `<talker16>` | 1 | 1 | 1 |
| `<talker17>` | 1 | 1 | 1 |
| `<talker18>` | 1 | 1 | 1 |
| `<talker19>` | 1 | 1 | 1 |
| `<talker2>` | 1 | 1 | 1 |
| `<talker20>` | 1 | 1 | 1 |
| `<talker21>` | 1 | 1 | 1 |
| `<talker22>` | 1 | 1 | 1 |
| `<talker23>` | 1 | 1 | 1 |
| `<talker24>` | 1 | 1 | 1 |
| `<talker25>` | 1 | 1 | 1 |
| `<talker26>` | 1 | 1 | 1 |
| `<talker3>` | 1 | 1 | 1 |
| `<talker4>` | 1 | 1 | 1 |
| `<talker5>` | 1 | 1 | 1 |
| `<talker6>` | 1 | 1 | 1 |

## Detailed Module List

### `<audio1>`

Actions: canonicalised (1), loading (1), relation (1)

### `<audio_unit1>`

Actions: canonicalised (5), loading (5), relation (5)

### `<audio_unit2>`

Actions: canonicalised (5), loading (5), relation (5)

### `<clicker1>`

Actions: canonicalised (1), loading (1), relation (1)

### `<console_mixer1>`

Actions: canonicalised (1), loading (1), relation (1)

### `<controller1>`

Actions: canonicalised (1), loading (1), relation (1)

### `<controller11>`

Actions: canonicalised (1), loading (1), relation (1)

### `<controller12>`

Actions: canonicalised (1), loading (1), relation (1)

### `<controller13>`

Actions: canonicalised (1), loading (1), relation (1)

### `<controller14>`

Actions: canonicalised (1), loading (1), relation (1)

### `<controller2>`

Actions: canonicalised (1), loading (1), relation (1)

### `<controller3>`

Actions: canonicalised (1), loading (1), relation (1)

### `<controller7>`

Actions: canonicalised (1), loading (1), relation (1)

### `<controller8>`

Actions: canonicalised (1), loading (1), relation (1)

### `<delay1>`

Actions: canonicalised (1), loading (1), relation (1)

### `<drummer1>`

Actions: canonicalised (1), loading (1), relation (1)

### `<interpreter1>`

Actions: canonicalised (2), loading (1), relation (1)

### `<keygroup1>`

Actions: canonicalised (1), loading (1), relation (1)

### `<keygroup2>`

Actions: canonicalised (1), loading (1), relation (1)

### `<keygroup3>`

Actions: canonicalised (1), loading (1), relation (1)

### `<keygroup4>`

Actions: canonicalised (1), loading (1), relation (1)

### `<metronome1>`

Actions: canonicalised (1), loading (1), relation (1)

### `<midi_clock1>`

Actions: canonicalised (4), loading (4), relation (4)

### `<midi_converter1>`

Actions: canonicalised (4), loading (4), relation (4)

### `<midi_input1>`

Actions: canonicalised (1), loading (1), relation (1)

### `<midi_output1>`

Actions: canonicalised (1), loading (1), relation (1)

### `<midi_output2>`

Actions: canonicalised (1), loading (1), relation (1)

### `<midi_output3>`

Actions: canonicalised (1), loading (1), relation (1)

### `<midi_output4>`

Actions: canonicalised (1), loading (1), relation (1)

### `<pico_manager1>`

Actions: canonicalised (1), loading (1), relation (1)

### `<recorder1>`

Actions: canonicalised (8), loading (8), relation (8)

### `<rig1>`

Actions: canonicalised (1), loading (1), relation (1)

### `<rig2>`

Actions: canonicalised (1), loading (1), relation (1)

### `<rig3>`

Actions: canonicalised (1), loading (1), relation (1)

### `<rig4>`

Actions: canonicalised (1), loading (1), relation (1)

### `<rig5>`

Actions: canonicalised (1), loading (1), relation (1)

### `<rig6>`

Actions: canonicalised (1), loading (1), relation (1)

### `<rig7>`

Actions: canonicalised (1), loading (1), relation (1)

### `<rig8>`

Actions: canonicalised (1), loading (1), relation (1)

### `<scale_manager1>`

Actions: canonicalised (1), loading (1), relation (1)

### `<scaler1>`

Actions: canonicalised (8), loading (8), relation (8)

### `<scheduler1>`

Actions: canonicalised (1), loading (1), relation (1)

### `<summer1>`

Actions: canonicalised (4), loading (4), relation (4)

### `<talker1>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker10>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker11>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker14>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker15>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker16>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker17>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker18>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker19>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker2>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker20>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker21>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker22>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker23>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker24>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker25>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker26>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker3>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker4>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker5>`

Actions: canonicalised (1), loading (1), relation (1)

### `<talker6>`

Actions: canonicalised (1), loading (1), relation (1)


---

## Load Progress Analysis

### Critical Finding: Log Stops Abruptly

**The log file ends unexpectedly after backend reports "loaded: 24 60" at 9.67 seconds.**

The last messages in the log are:
```
eigend-backend: loaded:  24  60  in  9.6706862449646  s  audio unit rig 1 controller 
eigend: <interpreter1>: send any  /audio_unit_rig_1_talker/key/key_1/activate5
eigend: <interpreter1>: sending /audio_unit_rig_1_talker/key/key_1/activate 3
... (a few more interpreter messages)
log:total audio dropouts 0 average tick 11610
```

### Key Facts

1. **All 64 canonicalised modules DID start loading** - no modules were skipped
2. **Backend counter shows "24/60"** - this counts loading *phases*, not modules
3. **Each module loads in 2 phases** - explaining why the counter advances by 2
4. **Log stops mid-stream** - no error, no completion message, no exception

### Loading Pattern Observed

The backend loading follows this pattern:
- Loads eigend, interpreter, core infrastructure
- Loads 4 MIDI outputs
- Loads 8 rigs (rig1-rig8) sequentially  
- Each rig loads internal agents (recorder, scaler, midi_converter, midi_clock)
- Loads audio system
- Starts loading talkers/controllers/keygroups
- **Log stops at phase 24/60**

### Modules with Multiple Instances

Multiple instances loaded successfully across different rigs:
- `<recorder1>`: 8 instances (one per rig)
- `<scaler1>`: 8 instances (one per rig)
- `<audio_unit1>` & `<audio_unit2>`: 4 instances each (in audio unit rigs)
- `<midi_converter1>`: 4 instances (in midi rigs)
- `<midi_clock1>`: 4 instances (in midi rigs)
- `<summer1>`: 4 instances (in audio unit rigs)

### The Real Question

**Why does loading stop at 24/60?**

#### Understanding the Loading Mechanism

From `pisession/workspace.py`:
- Loading is **asynchronous** and **callback-driven**
- Agents load one at a time from a queue
- Each agent calls `reload()` which returns a Deferred
- When an agent completes, it calls `ok()` → `progress()` → prints "loaded: X Y"
- The `progress()` callback then triggers `__doload()` to load the **next** agent
- The counter shows: `loaded: <completed> <total>`

#### What "24/60" Means

- **24 agents successfully loaded** (their callbacks fired)
- **36 agents still in queue** waiting to load
- **Agent #25 started loading** but its `reload()` callback **never completed**
- Neither `ok()` nor `not_ok()` was called
- Without the callback, `__doload()` is never called again
- **The chain is broken** - remaining agents never get a chance to load

#### Root Cause

**Agent #25's reload() is stuck** - the async operation started but never finished.

This could be:
1. **Waiting for RPC response** that never comes
2. **Blocked on resource** (file, socket, lock)
3. **Waiting for callback** from C++ native code
4. **Async coroutine suspended** mid-execution
5. **Exception swallowed** in async handler

The process is alive, Workbench can connect, but **the loading state machine is frozen** waiting for a callback that will never arrive.

### Recommendations for Investigation

1. **Identify Agent #25**: What agent was it trying to load next?
   - Check `self.__load_queue` state when hung
   - The last "loaded:" was "audio unit rig 1 controller"
   - Next in queue would be agent #25

2. **Check reload() for Agent #25**:
   - Which agent type?  
   - Where does its `reload()` call hang?
   - Is it waiting on RPC `rpc_loadstate`?
   
3. **RPC tracing**:
   - Add logging to all RPC calls in reload path
   - Track which RPC was sent but never returned
   - Check if eigend is waiting for a response

4. **Async coroutine state**:
   - Dump all pending coroutines
   - Check if `load_state()` is suspended mid-execution
   - Look for uncaught exceptions in async handlers

5. **Comparison with working setup**:
   - How many agents in working vs failing setup?
   - Which agents are in position #25 in working setups?
   - Is there a size threshold where this breaks?

6. **Add diagnostics**:
   - Log when `reload()` is called for each agent
   - Log when `ok()` and `not_ok()` callbacks fire  
   - Print `__load_queue` contents periodically
   - Add timeout detection for individual agent loads

7. **Check C++ native callbacks**:
   - Some agents have native code (audio_unit, recorder, etc.)
   - Callbacks from C++ to Python may not be firing
   - Check ref counting / object lifecycle issues
