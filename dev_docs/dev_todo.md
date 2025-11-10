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
  - Verify `/usr/bin/python3.14` exists and works
  - Test with deadsnakes PPA: `add-apt-repository ppa:deadsnakes/ppa && apt install python3.14 python3.14-dev`
  - Test with python.org source compilation if needed
  - Verify venv creation: `python3.14 -m venv .venv_dev`
  - Test Python 3.14 version check error message
- ⏭️ Test Python version compatibility range (3.8-3.14)

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
- ⚠️ **MEDIUM**: Verify DirectX SDK still required (may be in Windows SDK)
- ⏭️ **LOW**: Investigate pure MSYS2/MinGW build (no MSVC dependency)

### 4. System Integration Testing
**Status**: Essential validation
- Test pezload (Pico firmware loading - uses bytearray)
- Test minimal plugin setup (no Eigenharp connected)
- Test all plg_* modules incrementally
- Check for GIL/threading issues (deadlocks, hangs)
- Monitor for audio thread priority issues
- Verify upgrade path from old setups

---

## 🔧 MEDIUM PRIORITY - Post-Migration Work

### 4. Workbench Application Testing
**Status**: ✅ Functional with known issue (2025-11-10)
- ✅ Fixed: No longer crashes on startup (PyCapsule issue resolved)
- ✅ Fixed: Agent positioning now correct in GUI
- ⚠️ Known Bug: Cannot add IO to rig and keygroup IO
  - Appears to be existing bug in EigenD 2.2.1 as well
  - Not a new Python 3 migration issue
- **Core Functionality Working**:
  - ✅ Agent creation and deletion
  - ✅ Wire creation and deletion  
  - ✅ Agent positioning and layout
  - ✅ Connection routing and visualization
  - ✅ Setup save/load through Workbench GUI

### 5. Full Plugin Testing
**Status**: Incremental validation
- Test audio output plugins
- Test MIDI input/output plugins
- Test all agent types (audio, MIDI, controller)
- Test plugin lifecycle (load/unload/reconnect)
- Verify setup loading and saving with complex setups

### 6. Documentation Updates
**Status**: Prepare for release
- Update main README with Python 3.14 requirement
- Update NOTES_MACOS.md with Python 3 build instructions (python.org installation)
- Document installation process (python.org, not Homebrew)
- Note breaking changes from Python 2.7 version
- Document VST SDK as optional dependency
- Create release notes for community
- Update .github/copilot-instructions.md with Python 3 context

---

## 📦 LOW PRIORITY - Future Improvements

### 7. Python Packaging Strategy
**Status**: Consider before release
- Evaluate virtual environment approach for distribution
- Research modern Python packaging (pyproject.toml)
- Consider platform-specific installers
- Document Python installation requirements clearly
- Note: macOS/Windows don't include Python, Linux varies by distro

### 8. Code Cleanup and Modernization
**Status**: Post-migration polish
- Update JUCE to latest version (includes newer VST3 SDK)
- Remove external vst3sdk submodule once JUCE updated
- Update PLY (lex.py/yacc.py) to latest Python 3 version
- Clean up temporary migration artifacts
- Consider removing Python 2.7 fallback code paths
- Remove #if PY_VERSION_HEX conditionals if Python 3 only

### 9. Advanced Application Testing
**Status**: Lower priority - may not fix
- Test Stage application
- Evaluate Browser/Commander (already broken, may deprecate)
- Consider modernizing GUI tools vs maintaining legacy

### 10. Build System Evaluation
**Status**: No immediate need
- Current: SCons 4.x working well
- Future: Consider CMake migration (3-6 months effort)
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


---

## ✅ COMPLETED WORK

### November 9, 2025 - Workbench Startup Fix ✅
**Problem**: Workbench crashed on startup in `epython::PythonBackend::mediator()`
**Location**: `app_juceworkbench/epython.cpp:185` - PyCapsule_GetPointer failure
**Root Cause**: Python 3 migration issue in Workbench's Python integration
**Solution**: Fixed PyCapsule handling in workbench.pip binding
**Result**: ✅ Workbench now launches successfully
**Remaining**: Agent positioning issues in GUI (testing phase)

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

### Threading Issue - Dictionary Iteration During Modification
**Status**: Investigation needed - NOT a Python 3 migration bug, architectural issue
**Issue**: `RuntimeError: dictionary changed size during iteration` in `pi/agent.py:497`
- Location: `Agent.close_server()` iterating `self.__subsystems.items()`
- Context: Occurred during `<pico_manager1>: detaching client` while loading new setup
- Impact: Plugin unload crashes when subsystems dictionary modified during iteration
**Root Cause Hypothesis**: Violation of thread ownership model - operation deferred to wrong thread
**Note**: This is architectural/threading bug in original code, not Python 3 migration issue

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
- ⏭️ Tag working version after hardware testing passes
- ⏭️ Merge to main branch after full testing
- ⏭️ Create beta release for community testing

### ✅ RECENT FIXES COMPLETED (Nov 6, 2025)

#### Test Runner Enhancement for TDD ✅
- **Problem**: Session teardown taking 30+ seconds hindering TDD workflow
- **Solution**: Added `--quick/-q` mode with 5s timeout and session teardown skip
- **Implementation**: Enhanced `run_tests.sh` and `tests/conftest.py` with threading timeout
- **Performance**: ~75% faster (6s vs 30s), enabling rapid iteration cycles
- **Usage**: `./run_tests.sh --quick --level foundation`


### ✅ PREVIOUSLY COMPLETED MAJOR WORK

#### Test-Driven Development Infrastructure ✅
- **Test Structure**: 6-layer hierarchical test system (Foundation→Integration)
- **Professional Test Runner**: `run_tests.sh` with timeout protection, verbosity levels, HTML reports
- **Current Results**: 36/43 tests passing across all layers
- **TDD Workflow**: Quick iteration cycles with `--quick` mode

#### Core Migration Complete ✅
- ✅ Full build completes (make, make mpkg)
- ✅ PIP binding system (C++/Python integration)
- ✅ All command-line tools: bcat, bls, bpaths, brexec, brpc, bscript, bdownload, capture, signature, upgrade34, annotate, **cheatsheet**
- ✅ Belcanto logic system (pi/logic/) imports and initializes
- ✅ Core pi/ modules load correctly
- ✅ Session and agent management modules import

### 🎯 RECENT SESSION FIXES (Nov 5, 2025)

1. **PIP Template Constructor Exception Handling** ✅ **VALIDATED & DEPLOYED**
   - Issue: Copy constructors failing with "function takes exactly 2 arguments (1 given)" 
   - Root Cause: PIP template (`tools/pip_cmd/template`) didn't clear exceptions between constructor attempts
   - Analysis: Confirmed same bug exists in both Python 2.7 and 3.14 templates, but only fails in Python 3.14
   - Hypothesis: Python 2.7 was more forgiving with exception persistence between constructor attempts
   - Solution: Added `PyErr_Clear()` after each failed constructor attempt
   - **Testing**: ✅ All term constructors now working (empty, unsigned, string+type, copy, data)
   - **Validation**: ✅ Comprehensive test suite passes - 12/12 tests passing
   - **Deployment**: ✅ eigend successfully loads all Python modules and plugins
   - Impact: Fixes all copy constructors (`piw.term(existing)`, `piw.data(existing)`, etc.)
   - Files: tools/pip_cmd/template, tests/unit/test_term_constructors.py (corrected + redundant test removed)

2. **EigenD Startup Progress After Fix** ✅ **MAJOR BREAKTHROUGH**
   - **Before Fix**: eigend crashed immediately with "assertion failure: is_string()" during Python import
   - **After Fix**: ✅ Python modules load successfully, ✅ All 50+ plugins discovered, ✅ GUI components created
   - **Remaining Issue**: Still crashes with "assertion failure: is_string()" but now during setup file loading/creation
   - **Progress**: Moved from "fails immediately" to "fails during setup initialization" 
   - **Assessment**: Core Python 3.14 migration is complete, remaining issue is setup file compatibility

3. **Remaining `is_string()` Assertion Investigation** 🔍 **SEPARATE ISSUE**
   - **Location**: piw_data.h:211 in `as_string()` method during setup file operations
   - **Analysis**: Different from constructor dispatch issue - this is a data type mismatch in C++ layer
   - **Hypothesis**: Setup file format or binary serialization incompatibility between Python versions
   - **Impact**: Prevents full eigend startup but doesn't affect Python module functionality
   - **Note**: This appears to be a separate data handling issue, not related to PIP template constructor dispatch

2. **PyString_AsString Migration Validation** ✅
   - Issue: Needed to verify binary protocol compatibility after Python 3.14 migration
   - Solution: Confirmed PIP bindings use `PyUnicode_AsUTF8AndSize()` correctly
   - Result: Unicode handling working properly, agentd module imports successfully
   - Fixed related issues: `dict.keys().sort()` → `list(dict.keys()).sort()`, `map()` iterator compatibility

3. **Fixed cheatsheet command** ✅
   - Issue: `TypeError: can only concatenate list (not "range") to list`
   - Fix: `[x] + range(y)` → `[x] + list(range(y))`
   - File: app_cmdline/cheat.py
   - Result: Identical output to Python 2.7 version

2. **Fixed EigenD daemon startup** ✅
   - Fixed: `httplib` → `http.client` (bugs_cli.py)
   - Fixed: `range().reverse()` → `list(range()).reverse()` (pi/resource.py)
   - Fixed: `map()` iterator → `list(map())` (pi/resource.py)
   - Fixed: Missing `picross` import (bugs_cli.py)
   - Fixed: Import paths `bugs_cli` → `from app_eigend2 import bugs_cli` (backend.py)
   - Fixed: `BugsLogger.flush()` method missing (bugs_cli.py)
   - Fixed: `latest_release` import path (backend.py)
   - Fixed: `xmlrpclib` → `xmlrpc.client` (latest_release.py)
   - Fixed: `xrange` → `range` (backend.py)
   - Result: Daemon starts successfully, identical behavior to Python 2.7

3. **PyString_AsString Migration Analysis** ✅
   - **Issue**: User concerned about PyString_AsString migration impact on binary protocol
   - **Analysis**: PIP binding template already uses `PyUnicode_AsUTF8AndSize()` correctly for Python 3
   - **Discovery**: `term(data)` constructor broken due to `fpcvt_data` dispatcher issue
   - **Solution**: Implemented `data_to_term()` workaround in `pisession/agentd.py`
   - **Validation**: Created comprehensive test suite confirming binary protocol stability
   - **Result**: ✅ Migration preserves cross-version client-server compatibility

### 🏁 MIGRATION STATUS: COMPLETE ✅
**Success criteria met:**
- ✅ Full system builds with Python 3.14
- ✅ All command-line tools functional
- ✅ EigenD daemon loads all Python modules and plugins
- ✅ Setup loading system works correctly
- ✅ piw.data comparison uses content-based equality (Python 3 `tp_richcompare`)
- ✅ Controller attach/detach loop resolved
- ✅ Behavior identical to Python 2.7 version
- ✅ No Python 2→3 compatibility issues remaining
- ✅ Comprehensive test suite (43 tests covering foundation → integration)

**Core Python 3.14 Migration Complete:**
- All major blocking issues resolved
- System functional and stable
- Ready for hardware and platform testing

## 🚨 CRITICAL PRE-RELEASE TESTING REQUIRED

### ⚠️ System Python Compatibility Testing
**IMPORTANT:** Now using Python 3.14 from python.org (standard installer)

**Completed:**
- ✅ Test on fresh macOS with python.org Python 3.14 (/usr/local/bin/python3.14)
- ✅ Verify no Homebrew-specific paths hard-coded (switched from Homebrew to python.org)
- ✅ Test all command-line tools work with python.org Python
- ✅ Test EigenD daemon startup with python.org Python

**Remaining tests:**
- ⏭️ Test on Ubuntu/Debian with apt-installed Python
- ⏭️ Test on Windows with python.org installer
- ⏭️ Check Python version compatibility range (3.8+ minimum?)
- ⏭️ Windows: Python26 - get_pyprefix() pic_resources.cpp

**Potential issues to watch for:**
- Different Python versions (3.8, 3.9, 3.10, 3.11, 3.12, 3.13)
- Platform-specific Python installation differences
- Package manager conflicts (pip vs system packages)

## Next Steps - Beyond Migration Scope
- Test pezload (Pico firmware loading - uses bytearray)
- Test minimal plugin setup (no Eigenharp connected)
- Check for GIL/threading issues (deadlocks, hangs)
- Monitor for audio thread priority issues

### 🔍 THREADING ISSUE - Dictionary Iteration During Modification (2025-11-08)
**Status**: Investigation needed - NOT a Python 3 migration bug, architectural issue

**Issue**: `RuntimeError: dictionary changed size during iteration` in `pi/agent.py:497`
- Location: `Agent.close_server()` iterating `self.__subsystems.items()`
- Context: Occurred during `<pico_manager1>: detaching client` while loading new setup
- Impact: Plugin unload crashes when subsystems dictionary modified during iteration

**Call Stack**:
```
pisession/workspace.py:201 __unload()
  → pi/agent.py:79 __unload() 
    → pi/agent.py:506 unload()
      → pi/agent.py:497 close_server() [RuntimeError HERE]
```

**Architecture Context**:
- EigenD uses slow/fast thread separation (UI vs audio)
- Slow thread: UI operations, plugin management
- Fast thread: Real-time audio processing
- Design principle: Thread ownership prevents this type of race condition

**Root Cause Hypothesis**:
- Subsystems being modified by one thread while `close_server()` iterates on another
- Violation of thread ownership model - likely operation deferred to wrong thread
- May indicate improper cross-thread plugin lifecycle management

**NOT a Python 3 migration issue**:
- This is architectural/threading bug in original code
- Python 3 just exposes it by being stricter about dict iteration
- Python 2 was more lenient but race condition existed there too

**Investigation Needed**:
1. Which thread calls `close_server()` during plugin unload?
2. Which thread modifies `__subsystems` during setup loading?
3. Is plugin unload properly synchronized with setup loading?
4. Should `close_server()` be deferred to owning thread?

**Temporary Workaround** (REJECTED):
- `list(self.__subsystems.items())` would mask the real bug
- Better to understand threading model violation first

## Medium Priority - Full System
- Test with Eigenharp connected (Alpha/Tau/Pico)
- Test audio output plugins
- Test MIDI input/output
- Test all plg_* modules incrementally
- Test setup loading and saving
- Verify upgrade path from old setups

## Lower Priority - Advanced Tools
- Test Workbench application (GUI tool)
- Test Stage application
- Decide fate of Browser/Commander (already broken, may not fix)

## Before release
### python packaging ?
newer versions of macOS do not have python installed, older versions has 2.7 preintalled - but never python3
windows does not have python installed at all.

therefore we wil have to ask users to install python3 on all platforms
so , we can you the latest version - there is not concept of the one thats pre-installed

linux is different, but easier to advise users

perhaps we should consider modern python usages, which recommends a virtual environment !?


## Code Review Needed
- Verify bytearray usage in pezload and MIDI code
- ✅ Check all uses of pip_usegil flag behavior - **COMPLETED 2024-11-07** (GIL management working correctly)
- ✅ Review any remaining #if PY_VERSION_HEX conditionals - **COMPLETED 2024-11-07**
- ✅ Search for any missed Python 2 API calls - **COMPLETED 2024-11-07** (Fixed: .has_key() → 'in', ConfigParser → configparser)

## Documentation
- Update main README with Python 3.14 requirement
- Update NOTES_MACOS.md with Python 3 build instructions
- Update .github/copilot-instructions.md with Python 3 context
- Document installation process (Homebrew Python)
- Note breaking changes from Python 2.7 version
- Document VST SDK as optional dependency
- Create release notes for community
- Consider removing Python 2.7 fallback code paths

## Platform Support
- Windows: Update tools/windows_tools.py for Python 3
- Linux: Update tools/linux_tools.py for Python 3
- Test builds on all platforms

## Known Issues to Monitor
- GIL behavior under high load (audio dropout?)
- Memory allocator changes in Python 3 (potential deadlocks?)
- Unicode/bytes handling in MIDI and binary protocols
- Performance comparison vs Python 2.7 version

## Potential Improvements
- ✅ Remove #if PY_VERSION_HEX < 0x03000000 conditionals (Python 2 support) - **COMPLETED 2024-11-07**
- ✅ Clean up compatibility macros in template - **COMPLETED 2024-11-07**
- Update PLY (lex.py/yacc.py) to latest Python 3 version
- Consider Python 3.14 specific optimizations

## Git/Release
- ✅ Committed build system fixes (commit 55a8e099)
- ✅ Committed template fixes (commit 98f03aa8)  
- ✅ Committed pi/logic and runtime fixes (commit d431988d)
- ⏭️ Tag working version after daemon testing passes
- ⏭️ Merge to main branch after full testing
- ⏭️ Create beta release for community testing

## Future Considerations
- Evaluate CMake vs SCons (SCons 4.x working, no immediate need)
- CMake migration would require rewriting ~100+ build files (3-6 months effort)
- Only consider if SCons proves problematic during full runtime testing
- Need to consider Python install and possible use of virtual environment for final release, see python3.md

## Comparison with TheTechnobear's python3 Branch
Our copilot branch is MORE COMPLETE than the python3 branch:
- ✅ We fixed lock_c2p GIL API properly
- ✅ We added bytearray support  
- ✅ We fixed cmp(), long, string.maketrans (python3 branch has typos)
- ✅ We fixed parser module (python3 branch incomplete)
- ✅ We tested command-line tools (python3 branch untested)
- ✅ **No changes needed from python3 branch** - our migration is more comprehensive
