# Agent Load Comparison: Failed vs Successful Setups

## 🔴 CRITICAL FINDING: Python 3 Migration Bug

**SAME SETUP, DIFFERENT RESULTS:**

Log files located in `dev_docs/logs/`:

- ✅ **Python 2.7** (`ed22.log`): Completes successfully - 60/60 phases in 15.42s
- ❌ **Python 3** (`ed.log`): Fails at phase 24/60 
- ❌ **Python 3** (`ed2.log`): Fails at phase 26/60

**This is a Python 3 async callback bug, NOT an agent problem.**

See `agload_python3_issue.md` for detailed analysis.

---

## Summary

Log files located in `dev_docs/logs/`:

Analyzed four log files:
- **FAIL-1** (`ed.log`): Large setup on Python 3, stopped at phase 24/60 after "audio unit rig 1 controller"
- **FAIL-2** (`ed2.log`): Same setup on Python 3, stopped at phase 26/60 after "mixer controller"  
- **SUCCESS-SMALL** (`ed_success.log`): Smaller setup on Python 3, completed 9/9 phases successfully
- **SUCCESS-LARGE** (`ed22.log`): Large setup on Python 2.7, completed 60/60 phases successfully ✅

## Key Findings

### 1. Failures Stop at DIFFERENT Points
- FAIL-1: Phase 24/60 - "audio unit rig 1 controller"
- FAIL-2: Phase 26/60 - "mixer controller"
- **Both involve controllers**, but not the same one
- **This is NOT deterministic** - suggests timing/race condition

### 2. Controller Pattern
Both failures occurred after loading a **controller** agent:
- FAIL-1: Only 1 controller loaded before hang
- FAIL-2: 3 controllers loaded (2 midi input controllers, then mixer controller hung)

The successful setup has NO controllers at all.

### 3. Setup Size Difference
- **Failed setup**: 64 unique modules, 60 phases expected
- **Successful setup**: 23 modules, 9 phases, loads in 1.38s

Failed setup contains:
- 8 rigs (vs 1 in successful)
- 4 MIDI outputs + 1 MIDI input (vs 0 in successful)
- 26 talkers (vs 0 in successful)
- 14 controllers (vs 0 in successful)
- 4 keygroups (vs 1 in successful)
- Multiple audio_unit instances

### 4. What Happens After Last Load?

**FAIL-1** - After phase 24:
```
eigend: <interpreter1>: send any  /audio_unit_rig_1_talker/key/key_1/activate5
eigend: <interpreter1>: sending /audio_unit_rig_1_talker/key/key_1/activate 3
...
log:total audio dropouts 0 average tick 11610
```
- Interpreter continues sending key activation commands
- Audio system is ticking normally
- No further loading progress

**FAIL-2** - After phase 26:
```
eigend: <delay1>: ch 0 tn 1 ti 0 cutoff 2000 g 0.247949
eigend: <delay1>: ch 1 tn 1 ti 0 cutoff 2000 g 0.247949
log:total audio dropouts 0 average tick 11610
eigend: <main:pico_manager1/1> proxy closing down
log:total audio dropouts 0 average tick 11611
```
- Delay agent continues initialization
- Audio system ticking
- pico_manager proxy closing down (normal shutdown - when eigend killed)
- Still more log activity after "hung" point

### 5. Module Types Unique to Failed Setup

The failed setup has many modules the successful one lacks:
- Multiple rigs (rig2-8)
- MIDI I/O (midi_input1, midi_output1-4)
- Many talkers (talker1-26)
- Many controllers (controller1-14)
- metronome, drummer, clicker
- Multiple recorders (recorder1 in each rig)

## Analysis

### The Loading Mechanism

From `pisession/workspace.py`:
1. Agents load **one at a time** from a queue
2. Each agent calls `reload()` which returns a Deferred
3. On completion, callback fires → `progress()` → prints "loaded: X/Y" → calls `__doload()` for next
4. This is a **sequential async chain**

### Why It Stops

When loading stops at phase 24 or 26:
- That agent's `reload()` callback **never fires**
- Neither `ok()` nor `not_ok()` is called
- Without callback, `__doload()` never runs again
- **The chain is broken** - remaining agents never get loaded

### What's Different About Controllers?

Controllers in the failed setup that don't appear in successful:
- `controller1-14`: Multiple controller instances
- Associated with rigs, keygroups, or MIDI

The successful setup has NO separate controller agents - just integrated control.

### The Race Condition Hypothesis

Two runs of the same setup fail at **different** points:
- Run 1: After 1st controller
- Run 2: After 3rd controller (midi input controllers succeeded, mixer controller hung)

This suggests:
1. **Not a specific broken agent** - different controllers hang
2. **Timing-dependent** - sometimes gets further
3. **Resource contention?** - something gets exhausted
4. **Async callback lost** - callback registration fails under load?

## Theories

### Theory 1: Callback Registration Failure
- Under heavy async load, callback might not get registered properly
- Agent completes but callback never fires
- More agents = higher chance of callback loss

### Theory 2: RPC Response Lost
- `reload()` makes RPC call to agent
- Response gets lost in transit
- Agent loaded but Python never receives completion

### Theory 3: Resource Exhaustion
- Too many agents cause resource limits
- File descriptors, memory, threads?
- After ~24-26 phases, something runs out

### Theory 4: Event Loop Starvation
- Too many async operations queued
- Event loop not processing some callbacks
- Controller initialization particularly async-heavy?

## Next Steps

1. **Add detailed logging to reload() callback chain**:
   - Log when `reload()` is called
   - Log when RPC is sent
   - Log when callback fires (ok/not_ok)
   - Log the agent being loaded

2. **Check for lost callbacks**:
   - Add timeout per agent (currently 5000ms watchdog for whole load)
   - Detect which agent is "current" when hung

3. **Monitor resources during load**:
   - File descriptors
   - Thread count
   - Memory usage
   - Check limits

4. **Investigate pico_manager**:
   - Why does proxy close down during load in FAIL-2?
   - Is this normal or a sign of problem?

5. **Test with intermediate setup sizes**:
   - 1 rig: works
   - 8 rigs: fails around agent 24-26
   - Try 2, 3, 4 rigs - find the threshold

6. **Check controller initialization**:
   - All failures involve controllers
   - What makes controller reload() special?
   - Does it wait for something external?
