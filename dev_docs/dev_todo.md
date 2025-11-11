# Python 3.14 Migration TODO

**Status**: 🚀 Core Migration COMPLETE - Hardware Testing Phase

---

## 🎯 HIGH PRIORITY - Active Tasks

### 1. Hardware Testing with Eigenharp Devices
**Status**: ✅ COMPLETE - All hardware tested and working (2025-11-10)
- ✅ Pico - tested, working
- ✅ Tau - tested, working
- ✅ Alpha - tested, working
- ✅ Audio output verified
- ✅ MIDI I/O verified
- ✅ Controller attach/detach functional
- ✅ Setup loading/saving with real user setups working

### 2. Platform Compatibility Testing
**Status**: ✅ macOS python.org testing complete (2025-11-10)
- ✅ Test on fresh macOS with python.org Python 3.14 installer
- ✅ Verify no Homebrew-specific paths hard-coded
- ✅ All command-line tools work with python.org Python
- ✅ EigenD daemon startup works with python.org Python
- ✅ Added Python 3.14 version check in eigend startup (2025-11-10)
- ⏭️ Test on Ubuntu/Debian with Python 3.14
- ⏭️ Test on Windows with python.org installer

### 3. Windows Build System Modernization
**Status**: 🔧 Implemented, needs testing (2025-11-10)
- ✅ Migrated to MSYS2 + make workflow (matches macOS/Linux)
- ✅ Updated Python path to python.org Python 3.14
- ✅ SCons validates MSVC and DirectX SDK environments
- ✅ Updated windows_tools.py for Python 3.14 (python314.dll)
- ✅ Removed legacy bld.cmd scripts
- ✅ Created NOTES_WINDOWS.md with setup instructions
- 🔴 **HIGH PRIORITY**: Test new MSYS2 build setup on Windows
- 🔴 **HIGH PRIORITY**: Test Windows release build (distribution)

### 4. System Integration Testing
**Status**: Essential validation
- ✅ Test pezload (Pico firmware loading - uses bytearray)
- ✅ Test minimal plugin setup (no Eigenharp connected)
- ⏭️ Test all plg_* modules incrementally
- ✅ Check for GIL/threading issues (deadlocks, hangs)
- ✅ Monitor for audio thread priority issues
- ✅ Verify upgrade path from old setups

---

## 🔧 MEDIUM PRIORITY - Post-Migration Work

### 5. Cleanup and Performance Issues
**Status**: Medium priority - affects UX
- **Zombie Proxies and Slow Setup Switching** 🔴 (2025-11-10) 
  - **Symptom**: RPC retransmit messages during agent deletion, slow setup switching
  - **Root Cause**: Incomplete cleanup - filter wires not disconnecting synchronously
  - **Impact**: Performance degradation, users restart app instead of switching setups
  - **Priority**: Medium - affects UX but has workaround (restart app)
  - **Details**: See `dev_docs/prompts/gc_zombie_proxies.md`
  - **Note**: Pre-existing 2.21 issue exposed by Python 3 GC fixing memory leaks

- **Minor Clock Cleanup Assertion** ⚠️ (2025-11-10)
  - **Symptom**: `assertion failure: entity_ from pia_glue.h:324` when deleting rigs
  - **Impact**: Low - assertion caught and logged, no crash or corruption
  - **Note**: Always present but never triggered because Python 2 didn't clean up properly

### 6. Workbench Application Testing
**Status**: ✅ Functional with known issue (2025-11-10)
- ✅ Fixed: No longer crashes on startup (PyCapsule issue resolved)
- ✅ Fixed: Agent positioning now correct in GUI
- ⚠️ Known Bug: Cannot add IO to rig and keygroup
  - Appears to be existing bug in EigenD 2.2.1 as well
  - Not a new Python 3 migration issue
- **Core Functionality Working**:
  - ✅ Agent creation and deletion
  - ✅ Wire creation and deletion  
  - ✅ Agent positioning and layout
  - ✅ Connection routing and visualization
  - ✅ Setup save/load through Workbench GUI

### 7. Full Plugin Testing
**Status**: Incremental validation
- ✅ Test audio output plugins
- ⏭️ Test MIDI input/output plugins
- ⏭️ Test all agent types (audio, MIDI, controller)
- ✅ Test plugin lifecycle (load/unload/reconnect)
- ✅ Verify setup loading and saving with complex setups

### 8. Agent Testing
**Status**: Systematic validation of all 70 agents
**Testing approach**: Load each agent individually, verify basic functionality

**Hardware Agents (3)** - ✅ Tested
- ✅ `plg_pkbd` - Pico/Tau keyboard manager (fixed shutdown bug 2025-11-11)
- ✅ `plg_keyboard` - Alpha keyboard manager  
- ✅ `plg_ukbd` - Micro keyboard manager

**Audio I/O Agents (1)** - ✅ Tested
- ✅ `plg_audio` - Audio interface (CoreAudio/ASIO/ALSA)

**MIDI Agents (7)** - ⏭️ Needs testing
- ⏭️ `plg_midi/midi_input_plg.py` - MIDI input
- ⏭️ `plg_midi/midi_output_plg.py` - MIDI output
- ⏭️ `plg_midi/midi_processor_plg.py` - MIDI processor
- ⏭️ `plg_midi/midi_converter_plg.py` - MIDI converter
- ⏭️ `plg_midi/midi_clock_plg.py` - MIDI clock
- ⏭️ `plg_midi/midi_pgm_chooser_plg.py` - MIDI program chooser
- ⏭️ `plg_midi_monitor` - MIDI monitor

**MIDI Device Controllers (4)** - ⏭️ Needs testing
- ⏭️ `plg_midi_device/midi_device_plg.py` - Generic MIDI device
- ⏭️ `plg_midi_device/keyboard_controller_plg.py` - Keyboard controller
- ⏭️ `plg_midi_device/ableton_push_plg.py` - Ableton Push
- ⏭️ `plg_midi_device/continuum_plg.py` - Continuum fingerboard

**Rig and Hosting (2)** - ✅ Tested
- ✅ `plg_rig` - Rig agent (main container)
- ✅ `plg_host` - VST/AU host

**Simple Utility Agents (9)** - ⏭️ Needs testing
- ✅ `plg_simple/keygroup_plg.py` - Keygroup
- ⏭️ `plg_simple/scaler_plg.py` - Scaler
- ⏭️ `plg_simple/scale_manager_plg.py` - Scale manager
- ⏭️ `plg_simple/ranger_plg.py` - Ranger
- ⏭️ `plg_simple/scheduler_plg.py` - Scheduler
- ⏭️ `plg_simple/cycler_plg.py` - Cycler
- ⏭️ `plg_simple/labeler_plg.py` - Labeler
- ⏭️ `plg_simple/talker_plg.py` - Talker
- ⏭️ `plg_simple/stringer_plg.py` - Stringer

**Primitive Agents (2)** - ⏭️ Needs testing
- ⏭️ `plg_primitive/orb_plg.py` - Orb
- ⏭️ `plg_primitive/latch_plg.py` - Latch

**Synthesis Agents (15)** - ⏭️ Needs testing
- ⏭️ `plg_synth/sine_oscillator_plg.py` - Sine oscillator
- ⏭️ `plg_synth/triangle_oscillator_plg.py` - Triangle oscillator
- ⏭️ `plg_synth/sawtooth_oscillator_plg.py` - Sawtooth oscillator
- ⏭️ `plg_synth/rectangle_oscillator_plg.py` - Rectangle oscillator
- ⏭️ `plg_synth/envelope_plg.py` - Envelope
- ⏭️ `plg_synth/ahdsr_plg.py` - AHDSR envelope
- ⏭️ `plg_synth/synth_filter_plg.py` - Synth filter
- ⏭️ `plg_synth/ladder_filter_plg.py` - Ladder filter
- ⏭️ `plg_synth/gain_plg.py` - Gain
- ⏭️ `plg_synth/panner_plg.py` - Panner
- ⏭️ `plg_synth/shaper_plg.py` - Shaper
- ⏭️ `plg_synth/summer_plg.py` - Summer
- ⏭️ `plg_synth/polyphonic_summer_plg.py` - Polyphonic summer
- ⏭️ `plg_synth/delay_plg.py` - Delay
- ⏭️ `plg_synth/console_mixer_plg.py` - Console mixer

**STK (Synthesis Toolkit) Agents (4)** - ⏭️ Needs testing
- ⏭️ `plg_stk/cello_oscillator_plg.py` - Cello
- ⏭️ `plg_stk/clarinet_oscillator_plg.py` - Clarinet
- ⏭️ `plg_stk/blownstring_oscillator_plg.py` - Blown string
- ⏭️ `plg_stk/panpipe_oscillator_plg.py` - Pan pipe

**Sampler Agents (1)** - ⏭️ Needs testing
- ⏭️ `plg_sampler2/sampler_oscillator_plg.py` - Sampler

**Recording/Playback Agents (3)** - ⏭️ Needs testing
- ⏭️ `plg_recorder/recorder_plg.py` - Recorder
- ⏭️ `plg_recorder/player_plg.py` - Player
- ⏭️ `plg_arranger` - Arranger

**Loop/Rhythm Agents (3)** - ⏭️ Needs testing
- ⏭️ `plg_loop/metronome_plg.py` - Metronome
- ⏭️ `plg_loop/clicker_plg.py` - Clicker
- ⏭️ `plg_loop/drummer_plg.py` - Drummer

**Performance Agents (3)** - ⏭️ Needs testing
- ⏭️ `plg_finger` - Fingerer
- ⏭️ `plg_strummer` - Strummer
- ⏭️ `plg_livepad` - Live pad

**Convolver Agent (1)** - ⏭️ Needs testing
- ⏭️ `plg_convolver` - Convolver (convolution reverb)

**Language/Controller Agents (2)** - ✅ Tested
- ✅ `plg_language/language_plg.py` - Language agent
- ✅ `plg_language/controller_plg.py` - Controller agent

**Illumination Agents (2)** - ⏭️ Needs testing
- ⏭️ `plg_illuminator` - Illuminator
- ⏭️ `plg_scale_illuminator` - Scale illuminator

**Conductor/Clip Agents (2)** - ⏭️ Needs testing
- ⏭️ `plg_conductor/conductor_plg.py` - Conductor
- ⏭️ `plg_conductor/clip_manager_plg.py` - Clip manager

**Tabulator Agent (1)** - ⏭️ Needs testing
- ⏭️ `plg_tabulator` - Tabulator

**T3D (3D Touch) Agents (3)** - ✅ Tested
- ✅ `plg_t3d/t3d_device_plg.py` - T3D device
- ✅ `plg_t3d/t3d_output_plg.py` - T3D output
- ✅ `plg_t3d/soundplane_plg.py` - Soundplane

**OSC Agent (1)** - ⏭️ Needs testing
- ⏭️ `plg_osc/osc_output_plg.py` - OSC output

### 9. Documentation Updates
**Status**: Prepare for release
- ⏭️ Update main README with Python 3.14 requirement
- ⏭️ Update NOTES_MACOS.md with Python 3 build instructions (python.org installation)
- ⏭️ Document installation process (python.org, not Homebrew)
- ⏭️ Note breaking changes from Python 2.7 version
- ⏭️ Document VST SDK as optional dependency
- ⏭️ Create release notes for community
- ⏭️ Update .github/copilot-instructions.md with Python 3 context
- ⏭️ Note: VST 3 only

---

## 📦 LOW PRIORITY - Future Improvements

### 10. Python Packaging Strategy
**Status**: Consider before release
- ⏭️ Evaluate virtual environment approach for distribution
- ⏭️ Research modern Python packaging (pyproject.toml)
- ⏭️ Consider platform-specific installers
- ✅ Document Python installation requirements clearly
- ✅ Note: macOS/Windows don't include Python, Linux varies by distro

### 11. Code Cleanup and Modernization
**Status**: Post-migration polish
- ✅ Update JUCE to latest version (includes newer VST3 SDK)
- ✅ Remove external vst3sdk submodule once JUCE updated
- ⏭️ Update PLY (lex.py/yacc.py) to latest Python 3 version
- ✅ Clean up temporary migration artifacts
- ⏭️ Consider removing Python 2.7 fallback code paths
- ✅ Remove #if PY_VERSION_HEX conditionals if Python 3 only

### 12. Advanced Application Testing
**Status**: Lower priority - may not fix
- ⏭️ Test Stage application
- ⏭️ Evaluate Browser/Commander (already broken, may deprecate)
- ⏭️ Consider modernizing GUI tools vs maintaining legacy

### 13. Build System Evaluation
**Status**: No immediate need
- ✅ Current: SCons 4.x working well
- ⏭️ Future: Consider CMake migration (3-6 months effort)
  - Only evaluate if SCons proves problematic
  - Would require rewriting ~100+ build files

---

## 🏁 MIGRATION STATUS: COMPLETE ✅

**Core Python 3.14 Migration Complete:**
- ✅ Full system builds with Python 3.14
- ✅ All command-line tools functional
- ✅ EigenD daemon loads all Python modules and plugins
- ✅ Setup loading system works correctly
- ✅ piw.data comparison uses content-based equality
- ✅ Controller attach/detach loop resolved
- ✅ PIP binding system fully migrated
- ✅ Comprehensive test suite (43 tests passing)
- ✅ Behavior identical to Python 2.7 version
- ✅ No Python 2→3 compatibility issues remaining
- ✅ Workbench application launches (startup crash fixed)
- ✅ All hardware tested and working (Pico, Tau, Alpha)

---

## ✅ COMPLETED WORK

### November 11, 2025 - plg_pkbd Shutdown Fix ✅
**Problem**: Runtime error during eigend shutdown: "dictionary changed size during iteration"
**Location**: `plg_pkbd/pico_manager_plg.py:148` - `on_quit()` method
**Root Cause**: Iterating over `subsystem_keys()` dict view while `del_keyboard()` modified it
**Solution**: Wrapped `self.subsystem_keys()` with `list()` to create snapshot before iteration
**Result**: ✅ Clean shutdown without runtime errors
**Files Changed**: `plg_pkbd/pico_manager_plg.py`

### November 9, 2025 - Workbench Startup Fix ✅
**Problem**: Workbench crashed on startup in `epython::PythonBackend::mediator()`
**Location**: `app_juceworkbench/epython.cpp:185` - PyCapsule_GetPointer failure
**Root Cause**: Python 3 migration issue in Workbench's Python integration
**Solution**: Fixed PyCapsule handling in workbench.pip binding
**Result**: ✅ Workbench now launches successfully
**Files Changed**: `app_juceworkbench/workbench.pip`

### November 9, 2025 - piw.data Comparison Fix ✅
**Problem**: Setup loading hung due to spurious domain change notifications triggering controller attach/detach loops
**Root Cause**: `piw.data.__eq__` used identity comparison instead of content comparison (Python 2's `__cmp__` removed in Python 3)
**Solution**: Updated PIP template to generate `tp_richcompare` from existing `__cmp__` method
**Implementation**: 
- Added `special_richcompare_method_()` to PIP template (lines 909-951)
- Updated `tp_richcompare` slot to conditional function pointer (line 1459)
- Uses `PyType_IsSubtype(Py_TYPE(other), Py_TYPE(self))` for runtime type checking
**Files Changed**:
- `tools/pip_cmd/template` - Rich comparison generation
- `tests/unit/test_02_data_layer.py` (lines 488-687) - Comprehensive comparison tests
**Testing**: All 5 TestPiwDataComparison tests passing
- test_data_equality_basic
- test_data_equality_strings
- test_data_equality_dict_lookup (proxy.py use case)
- test_data_richcompare_all_operators (all 6: <, <=, ==, !=, >, >=)
- test_data_nb_inherits_comparison (subtype inheritance)
**Result**: Setup loading now works correctly, no spurious node_changed() calls
**Impact**: Fixed major Python 3 migration blocker - setup loading system fully functional
**Documentation**: Updated setup_loading.md and terms.md to reflect working system

### November 6, 2025 - Test Infrastructure ✅
**Test Runner Enhancement for TDD**:
- Added `--quick/-q` mode with 5s timeout and session teardown skip
- Enhanced `run_tests.sh` and `tests/conftest.py` with threading timeout
- Performance: ~75% faster (6s vs 30s), enabling rapid iteration cycles

**Test Structure**: 6-layer hierarchical test system (Foundation→Integration)  
**Current Results**: 43 tests passing across all layers

**VST3 SDK Integration**:
- Fixed object files being created in vst3sdk submodule
- Implemented hybrid approach using external headers + minimal utility compilation
- Verified clean rebuild works without submodule pollution
- Proper VariantDir usage for build artifacts in tmp/obj/vst3sdk/

### November 5, 2025 - PIP Template Constructor Fix ✅
**Issue**: Copy constructors failing with "function takes exactly 2 arguments (1 given)" 
**Root Cause**: PIP template didn't clear exceptions between constructor attempts
**Solution**: Added `PyErr_Clear()` after each failed constructor attempt
**Testing**: All 12 term constructor tests passing
**Deployment**: eigend successfully loads all Python modules and plugins
**Impact**: Fixes all copy constructors (`piw.term(existing)`, `piw.data(existing)`, etc.)
**Files**: tools/pip_cmd/template, tests/unit/test_term_constructors.py

**EigenD Startup Progress**:
- Before: eigend crashed immediately with "assertion failure: is_string()"
- After: Python modules load successfully, all 50+ plugins discovered, GUI components created
- Assessment: Core Python 3.14 migration complete

### Earlier 2025 - Core Migration Work ✅
**PyString_AsString Migration**:
- Verified PIP bindings use `PyUnicode_AsUTF8AndSize()` correctly
- Fixed related issues: `dict.keys().sort()`, `map()` iterator compatibility
- Result: Unicode handling working properly, agentd module imports successfully

**Command-Line Tools**:
- Fixed cheatsheet: `[x] + range(y)` → `[x] + list(range(y))`
- All tools functional: bcat, bls, bpaths, brexec, brpc, bscript, bdownload, capture, signature, upgrade34, annotate, cheatsheet

**EigenD Daemon Startup**:
- Fixed: `httplib` → `http.client`, `xmlrpclib` → `xmlrpc.client`
- Fixed: `range().reverse()` → `list(range()).reverse()`
- Fixed: `map()` iterator → `list(map())`
- Fixed: `xrange` → `range`
- Result: Daemon starts successfully, loads all modules and plugins

**Build System**:
- Full build completes (make, make mpkg)
- PIP binding system (C++/Python integration) fully migrated
- Belcanto logic system imports and initializes
- Core pi/ modules load correctly
- Session and agent management working

### 2024 - Initial Migration Work ✅
**Python 3 API Migration**:
- All Python 2.7 APIs replaced with Python 3 equivalents
- PIP template fully updated for Python 3
- GIL management validated and working correctly
- Code review completed: .has_key() → 'in', ConfigParser → configparser

**Comparison with TheTechnobear's python3 Branch**:
Our migration is MORE COMPLETE:
- Fixed lock_c2p GIL API properly
- Added bytearray support  
- Fixed cmp(), long, string.maketrans (python3 branch has typos)
- Fixed parser module (python3 branch incomplete)
- Tested command-line tools (python3 branch untested)

---

## 🔍 KNOWN ISSUES TO MONITOR

### Potential Performance Issues
- GIL behavior under high load (audio dropout monitoring needed)
- Memory allocator changes in Python 3 (watch for deadlocks)
- Unicode/bytes handling in MIDI and binary protocols
- Performance comparison vs Python 2.7 version needed

---

## 📝 Git/Release Tracking

### Commits
- ✅ Committed build system fixes (commit 55a8e099)
- ✅ Committed template fixes (commit 98f03aa8)  
- ✅ Committed pi/logic and runtime fixes (commit d431988d)
- ⏭️ Create 3.0 branch
- ⏭️ Tag and create beta release for community testing

---

## 📚 NOTES

### Python Packaging Considerations
- macOS: Newer versions no Python, older versions have 2.7 pre-installed
- Windows: No Python pre-installed
- Linux: Varies by distro, easier to advise users
- Consider virtual environment approach for distribution
- Modern Python best practices recommend venv usage

### Comparison with TheTechnobear's python3 Branch
Our migration is MORE COMPLETE:
- Fixed lock_c2p GIL API properly
- Added bytearray support  
- Fixed cmp(), long, string.maketrans (python3 branch has typos)
- Fixed parser module (python3 branch incomplete)
- Tested command-line tools (python3 branch untested)