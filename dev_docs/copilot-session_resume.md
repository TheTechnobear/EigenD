# EigenD Python 3.14 Migration - Session Resume Context

**Date:** 2025-11-09  
**Branch:** python3  
**Status:** 🔍 **RESUMING SETUP LOADING ANALYSIS & TESTING**

## 🎯 CURRENT PRIORITY: Large Setup File Loading Issue (2025-11-09)

**Status:** FFTW upgrade complete, subject to testing. Resuming setup loading analysis.

### ✅ LATEST: Setup Loading Failure Analysis Complete (2025-11-09)

### **ROOT CAUSE IDENTIFIED: Forward-Reference Connection Problem**
**Location:** `pi/atom.py` line 623 → `pi/rpc.py` line 53 → `piw/src/piw_tsd.cpp` line 136  
**Issue:** Agents create connections during loading to not-yet-loaded agents, causing RPC exceptions that break the async callback chain.

#### **The Problem in Detail:**

**Non-Deterministic Loading Order:**
- Agents load sequentially from `self.index.members()` (dict iteration)
- Order varies between runs due to dict/set iteration in Python
- Same setup fails at different points each time (phase 24 vs 26)
- Agent N may load before or after Agent M unpredictably

**Connection Timing:**
- Connections created during **phase 2** of each agent's `rpc_loadstate`
- `update_slaves()` sends async RPC to target agents: `invoke_async_rpc(target_id, 'connected', self_id)`
- If target agent not loaded yet: **RPC throws exception** ("can't create async rpc")
- Exception breaks Deferred callback chain → next agent never loads → setup incomplete

**Python 2 vs 3 Difference:**
- Python 2.7: Exception handling in coroutines allows graceful continuation
- Python 3: Exception propagates and breaks callback chain
- Same non-deterministic loading, different exception handling

#### **Evidence:**
1. ✅ 60+ agents WITHOUT wiring: Loads successfully
2. ❌ 60 agents WITH wiring: Fails at variable points
3. ✅ Same setup on Python 2.7: Loads successfully (60/60 phases, 15.42s)
4. ❌ Same setup on Python 3: Fails consistently (phase 24-26)
5. ✅ Non-deterministic order confirmed: ed.log vs ed2.log have completely different agent sequences

#### **Documentation Created:**

**Log Files:** All logs moved to `dev_docs/logs/`
- `ed.log` - Failed Python 3 load (24/60 phases)
- `ed2.log` - Failed Python 3 load (26/60 phases) - same setup, different order
- `ed22.log` - Successful Python 2.7 load (60/60 phases) - same setup
- `ed_success.log` - Successful Python 3 small setup (9/9 phases)

**Analysis Documents:**
- `dev_docs/setup_loading.md` (7.5KB) - Complete loading process documentation
  - File format and database structure
  - All 6 loading phases with code references  
  - Connection timing and forward-reference problem
  - Rig handling (nested workspaces)
  - Investigation steps

- `dev_docs/loading_order_nondeterministic.md` - Order analysis
  - Proof that ed.log vs ed2.log have different agent sequences
  - Only first 2 agents consistent (eigend, interpreter)
  - After phase 2: completely different order

- `dev_docs/agload_wiring_hypothesis.md` - Connection analysis
- `dev_docs/agload_comparison.md` - Log comparisons
- `dev_docs/agload_python3_issue.md` - Python 2/3 differences

**Command-Line Tools:**
- `dev_docs/cmdline.md` (12KB) - Complete tool reference
  - 19 tools documented: bstdump, bstlist, bls, brpc, etc.
  - Usage examples for debugging
  - Connection term format
  - Python 2/3 cross-check procedures
  - Unit test potential identified

**Analysis Script:**
- `tools/analyze_setup.py` - Automated setup analysis
  - Extracts agent loading order from database
  - Finds all connections in setup
  - Identifies forward references
  - Shows which connections cause problems

#### **Solution Approaches:**

**Option 1: Defer Connection RPC to Post-Load**
```python
# In pi/atom.py update_slaves()
# Queue connections instead of sending RPC immediately
self.__pending_connections = []  # During load
# In agent_postload() send queued RPCs when all agents exist
```

**Option 2: Wrap invoke_async_rpc in Exception Handler**
```python
# In pi/atom.py update_slaves()
try:
    rpc.invoke_async_rpc(id_abs, 'connected', myrid)
except Exception as e:
    # Queue for retry in post_load
    self.__failed_connections.append((id_abs, myrid))
```

**Option 3: Make Loading Order Deterministic**
```python
# In pisession/workspace.py __load1()
# Sort agents by dependency graph before loading
agents_sorted = dependency_sort(agents)
```

**Recommended:** Option 1 (defer to post-load) - cleanest and most robust.

#### **Next Steps:**
1. Implement connection deferral fix
2. Test with large setup
3. Verify no regression on small setups
4. Cross-check state decoding Python 2 vs 3 using `bstdump`
5. Create unit tests using cmdline tools

---

## ✅ COMPLETED: FFTW 3.3.10 Upgrade with Hybrid Build System (2025-11-09)

**Status:** ✅ Complete and working, subject to runtime testing  
**Root Issue:** Build artifacts incorrectly placed in source tree  
**Solution:** Hybrid path approach - relative for SCons tracking, absolute for glob operations

### Final Working Solution

**Problem Evolution:**
1. **Initial approach (2025-11-08):** Absolute paths everywhere
   - ✅ Glob worked correctly
   - ❌ 613 build artifacts created in `lib_fftw/fftw-3.3.10/` source tree
   
2. **Second attempt (2025-11-09 AM):** Relative paths everywhere
   - ✅ Artifacts correctly placed in `tmp/obj/`
   - ❌ Glob failed to find 170+ SIMD codelet files
   - ❌ Undefined symbols at link time

3. **Final solution (2025-11-09 PM):** Hybrid approach
   - ✅ Relative paths for SCons file tracking → builds to `tmp/obj/`
   - ✅ Absolute paths for glob operations → finds all SIMD files
   - ✅ All 170+ codelet files included
   - ✅ Source tree clean, no build artifacts

**Key Lesson:** SCons requires relative paths for variant directory tracking, but Python's `glob.glob()` needs absolute paths in SCons context. Solution: glob with absolute, convert results to relative.

### Implementation Details

```python
# In lib_fftw/SConscript
fftw_base = 'fftw-3.3.10'  # Relative for SCons
fftw_base_abs = os.path.join(Dir('.').srcnode().abspath, fftw_base)  # Absolute for glob

# Glob with absolute, store as relative
for f in glob.glob(os.path.join(fftw_base_abs, 'dft/simd/neon/n*.c')):
    neon_dft_files.append(os.path.relpath(f, Dir('.').srcnode().abspath))
```

**SIMD Codelet Patterns (must capture all three):**
- `n*.c` - N-point transforms (67 files)
- `t*.c` - Twiddle transforms (95 files)  
- `q*.c` - Q transforms (8 files)
- Plus: `codlist.c` and `genus.c` (solver registration)

### Cleanup & Verification

- ✅ Deleted 613 `.o`/`.os` files from source tree
- ✅ Verified clean source: no build artifacts remain
- ✅ Verified correct placement: all objects in `tmp/obj/lib_fftw/`
- ✅ Build completes successfully
- ⏳ Runtime testing pending

### Documentation

- Updated `dev_docs/convolver_update.md` with complete build system details
- Removed `dev_docs/fftw_upgrade_3.3.10.md` (merged into convolver doc)

---

## ✅ PREVIOUS: Build Artifacts in lib_fftw Source Tree (2025-11-09)

**Issue:** 613 `.o` and `.os` files created in `lib_fftw/fftw-3.3.10/` instead of `tmp/obj/`  
**Root Cause:** `lib_fftw/SConscript` path handling issues with glob operations  
**Impact:** SCons couldn't track files properly, leading to two separate problems

### Problem Evolution:

**2025-11-08:** Initial FFTW 3.3.10 upgrade used absolute paths everywhere:
```python
script_dir = Dir('.').srcnode().abspath  
fftw_base = os.path.join(script_dir, 'fftw-3.3.10')  # Absolute!
```
- ✅ Glob worked: `glob.glob(os.path.join(fftw_base, 'dft/simd/neon/*.c'))`
- ❌ Build artifacts created in source tree (613 files)
- ❌ SCons couldn't track files relative to source → built in-place

**2025-11-09 (morning):** Changed to relative paths:
```python
fftw_base = 'fftw-3.3.10'  # Relative
```
- ✅ Build artifacts now go to `tmp/obj/` correctly
- ❌ Glob failed: `glob.glob()` with relative path doesn't work in SCons
- ❌ Missing 170+ SIMD codelet files → undefined symbols at link time

### Solution: Hybrid Approach

Use relative paths for SCons file tracking, absolute paths for glob operations:

```python
# Relative for SCons (so builds go to tmp/obj/)
fftw_base = 'fftw-3.3.10'

# Absolute for glob operations (so glob.glob() finds files)
fftw_base_abs = os.path.join(Dir('.').srcnode().abspath, fftw_base)

# Add SIMD codelets
neon_dft_files = [
    os.path.join(fftw_base, 'dft/simd/neon/codlist.c'),  # Relative
    os.path.join(fftw_base, 'dft/simd/neon/genus.c'),
]
# Use absolute for glob, convert back to relative for SCons
for f in glob.glob(os.path.join(fftw_base_abs, 'dft/simd/neon/n*.c')):
    neon_dft_files.append(os.path.relpath(f, Dir('.').srcnode().abspath))
for f in glob.glob(os.path.join(fftw_base_abs, 'dft/simd/neon/t*.c')):
    neon_dft_files.append(os.path.relpath(f, Dir('.').srcnode().abspath))
for f in glob.glob(os.path.join(fftw_base_abs, 'dft/simd/neon/q*.c')):
    neon_dft_files.append(os.path.relpath(f, Dir('.').srcnode().abspath))
```

### Files Changed:
- `lib_fftw/SConscript` - Added `fftw_base_abs`, updated all glob operations

### SIMD Codelet Patterns:
Must capture all three patterns for complete symbol table:
- `n*.c` - N-point transforms (67 files)
- `t*.c` - Twiddle transforms (95 files)
- `q*.c` - Q transforms (8 files)
- Plus: `codlist.c` and `genus.c` (solver tables)

Initially missed `q*.c` pattern → additional undefined symbols → added in second iteration.

### Cleanup:
- Deleted 613 build artifacts from `lib_fftw/fftw-3.3.10/` subdirectories
- Verified source tree clean: no `.o` or `.os` files remain
- Verified builds go to `tmp/obj/lib_fftw/` correctly

### Lesson:
**SCons requires relative paths for proper build directory tracking.**  
Using absolute paths breaks the variant directory mechanism, causing builds in the source tree.  
However, Python's `glob.glob()` needs absolute paths when running in SCons context.  
Solution: Use absolute for glob, convert results to relative for file lists.

### Documentation:
- Updated `dev_docs/convolver_update.md` with build system details
- Removed `dev_docs/fftw_upgrade_3.3.10.md` (merged into convolver doc)

---

## ✅ PREVIOUS: FFTW Library Upgraded from 3.2.1 to 3.3.10 (2025-11-08)
**Upgrade:** FFTW 3.2.1 → 3.3.10
**Reason:** Enable ARM support on macOS and improve multi-platform builds

#### **Platforms Now Supported:**
- ✅ macOS x86_64 (SSE2 optimizations)
- ✅ macOS ARM64 (NEON optimizations) **NEW**
- ✅ Windows x86_64 (SSE2 optimizations)
- ✅ Linux x86_64 (SSE2 optimizations)
- ✅ Linux ARM64 (NEON optimizations) **NEW**

#### **Files Created:**
1. **Platform-specific config headers:**
   - `config_macosx_x86_64.h` - macOS Intel with SSE2
   - `config_macosx_arm64.h` - macOS Apple Silicon with NEON
   - `config_windows_x86_64.h` - Windows with SSE2
   - `config_linux_x86_64.h` - Linux x86_64 with SSE2
   - `config_linux_arm64.h` - Linux ARM64 with NEON

2. **Updated build system:**
   - `SConscript` - Complete rewrite for 3.3.10
   - `SConscript.old` - Backup of original
   - Added platform detection: `get_platform_config()`
   - Updated 380+ source files to new FFTW 3.3.10 structure
   - Added conditional SIMD compilation (SSE2/NEON)

3. **Documentation:**
   - `dev_docs/fftw_upgrade_3.3.10.md` - Complete upgrade notes

#### **Key Changes:**
- Source directory: `src/` → `fftw-3.3.10/`
- Added automatic platform/architecture detection
- Platform-specific config via `-include config_[platform].h`
- SIMD support: SSE2 for x86_64, NEON for ARM64
- All core FFTW modules updated: kernel, dft, rdft, reodft, api
- ARM build now enabled (removed old ARMHACK disable)

#### **Build Configuration:**
```python
# Auto-detects platform and selects correct config
config_file = get_platform_config()  # e.g., config_macosx_arm64.h

# Includes based on platform:
- macOS x86_64: SSE2, -msse2 flag
- macOS ARM64: NEON support
- Linux x86_64: SSE2, -msse2 flag
- Linux ARM64: NEON support
- Windows: SSE2, Windows-specific malloc
```

#### **Next Steps:**
1. Test build on macOS ARM64
2. Verify performance vs 3.2.1
3. Test on other platforms
4. Run existing test suite

---

## ✅ PREVIOUS FIX: Python Source File Installation for Python 3

### **FIXED: ModuleNotFoundError for keyboard_X and other plugin modules**
**Date:** 2025-11-08  
**Location:** `tools/generic_tools.py` line 412-421
**Error:** `ModuleNotFoundError: No module named 'keyboard_X'`
**Problem:** Build system only installed `.pyc` bytecode, not `.py` source files
**Solution:** Modified `__installpy()` to install source `.py` files instead of pre-compiled `.pyc`

#### **Root Cause - Python 2 vs 3 Bytecode and Import System:**
- **Python 2:** Could import from `.pyc` files alone, bytecode format was stable
- **Python 3:** Changed bytecode format, stricter import system, prefers source files
- **Old build system:** Pre-compiled to `.pyc` and only installed bytecode
- **Migration Issue:** Python 3 couldn't use old `.pyc` format, needed source files

#### **Exact Technical Fix:**
```python
# BEFORE (Python 2 style - only .pyc bytecode):
def __installpy(self,root1,root2,src,subdirs,dest=None):
    ...
    pyc_node=self.Command(join(root1,fqd+'c'),fqs,'"$PI_PYTHON" "$PI_COMPILER" $TARGET $SOURCE')
    if root2:
        self.InstallAs(self.File(join(root2,fqd+'c')),pyc_node)

# AFTER (Python 3 style - source .py files):
def __installpy(self,root1,root2,src,subdirs,dest=None):
    ...
    # Skip dynamically generated files
    if f in ('version.py', 'lexicon.py', 'alpha_manager_version.py'):
        continue
    
    # Install source .py file (Python 3 handles __pycache__ automatically)
    self.InstallAs(join(root1,fqd),fqs)
    if root2:
        self.InstallAs(join(root2,fqd),fqs)
```

#### **Impact:**
- **Before:** Plugins couldn't import their own modules (keyboard_X, etc.)
- **After:** All plugin Python files available for import
- **Lesson:** Python 3 prefers source files; uses __pycache__/ for automatic bytecode caching

---

## ✅ PREVIOUS FIX: Binary Data Handling in Plugin State

### **FIXED: UnicodeDecodeError in audio_unit blob handling**
**Date:** 2025-11-08  
**Location:** `plg_host/host_plg.py` line 234, `app_juceworkbench/workbench.py` line 209
**Error:** `'utf-8' codec can't decode byte 0x9c in position 1: invalid start byte`
**Problem:** Python 3 string operations on binary data from C++ `as_blob2()`
**Solution:** Use `b''.join()` for bytes instead of `''.join()` for strings

#### **Root Cause - Python 2 vs 3 String/Bytes Distinction:**
- **Python 2:** Strings were bytes by default, no strict unicode enforcement
- **Python 3:** Strings are unicode, bytes are separate type
- **C++ SWIG binding:** `as_blob2()` returns binary data (compressed zlib)
- **Migration Issue:** Joining binary chunks with `''.join()` tried UTF-8 decode

#### **Exact Technical Fix:**
```python
# BEFORE (crashes on binary data):
def get_blob(self):
    z = ''.join([ n.get_data().as_blob2() for n in self.values() ])
    return piw.makeblob2(zlib.decompress(z) if z else '',0)

# AFTER (handles bytes correctly):
def get_blob(self):
    z = b''.join([ n.get_data().as_blob2() for n in self.values() ])
    return piw.makeblob2(zlib.decompress(z) if z else b'',0)
```

#### **Files Changed:**
- `plg_host/host_plg.py`: Fixed `PluginStateBlob.get_blob()`
- `app_juceworkbench/workbench.py`: Fixed `WorkbenchStateBlob.get_state()`

#### **Impact:**
- **Before:** audio_unit plugin crashed during postload with UTF-8 decode error
- **After:** Binary state data handled correctly as bytes
- **Lesson:** C++ SWIG bindings return bytes in Python 3, must use bytes operations

---

## ✅ MAJOR FIX: Node Dictionary Recursion Resolved

### **FIXED: RecursionError in pi/node.py keys(), values(), items() methods**
**Date:** 2025-11-07  
**Location:** `pi/node.py` lines 287, 290, 293
**Problem:** Python 2→3 dictionary iteration behavior causing infinite recursion
**Solution:** 3-line minimal fix to call iter* methods

#### **Root Cause - Python 2 vs 3 Dictionary Behavior:**
- **Python 2.7:** `dict.keys()` returned lists, `dict.iterkeys()` returned iterators
- **Python 3:** `dict.keys()` returns views (iterator-like), `iter*` methods removed
- **Migration Issue:** Code had `return list(self.keys())` calling itself infinitely

#### **Exact Technical Fix:**
```python
# BEFORE (recursive calls):
def values(self): return list(self.values())
def items(self):  return list(self.items()) 
def keys(self):   return list(self.keys())

# AFTER (calls iterator methods):
def values(self): return list(self.itervalues())
def items(self):  return list(self.iteritems())
def keys(self):   return list(self.iterkeys())
```

#### **Impact:**
- **Before:** RecursionError crashed all plugin loading
- **After:** EigenD loads plugins successfully (cycler, sampler_oscillator, ahdsr, audio_unit, etc.)
- **Lesson:** Always try minimal fix first, then build/recompile Python changes

## 🎯 PREVIOUS FIX: PIP Binding Generation Restored

### **FIXED: AttributeError 'piw_native.data' object has no attribute 'as_dict_lookup'**
**Location:** `tools/pip_cmd/process.py` lines 84, 94
**Problem:** Python 3 `dict.values()` returns view object, not list
**Solution:** Wrap with `list()` conversion

#### **Exact Technical Fix:**
```python
# BEFORE (Python 2 compatible):
k['handlers'] = kh.values()
k['methods'] = km.values()

# AFTER (Python 3 compatible):
k['handlers'] = list(kh.values())
k['methods'] = list(km.values())
```

#### **Why This Failed:**
1. **Python 2→3 Change:** `dict.values()` returns `dict_values` view, not list
2. **PIP Template Expectation:** Code generation expects list for iteration
3. **Missing Methods:** `as_dict_lookup`, `as_dict_value` methods not generated
4. **Inheritance Issue:** Only base class methods generated, derived class methods lost

#### **Impact:**
- **Before:** `piw_native.data` missing critical dictionary access methods
- **After:** Full method set available including `as_dict_lookup`, `as_dict_value`
- **Root Issue:** upgrade_tools_v1.py couldn't access dictionary metadata
- **Result:** Setup file processing restored

#### **Validation:**
```bash
# Test confirms fix:
python3 -c "import piw_native; print('as_dict_lookup' in dir(piw_native.data()))"
# Returns: True ✅
```

# CORRECT:  
term = piw.term(piw.makestring(string, 0))  # Creates data term properly
```

### **Test Evidence Created:**
- **test_pyunicode_asuft8_pointer_corruption()** - Reproduces the exact corruption mechanism
- **test_term_constructor_semantic_analysis()** - Confirms predicate vs data constructor semantics
- **Segfault confirmed** when accessing `.pred()` on corrupted predicate terms

## Quick Start for New Session

### Environment Setup  
```bash
# Clone and checkout
git clone https://github.com/TheTechnobear/EigenD.git
cd EigenD
git checkout copilot

# Verify Python 3.14
which python3.14
# Should be: /opt/homebrew/opt/python@3.14/bin/python3.14

# Build
make clean
make -j8

# Test with TDD approach
./run_tests.sh --quick --level foundation  # Should pass all tests
./run_tests.sh -q --level core            # Shows current progress
```

### Current Status - 2024-11-06
- **VST3 SDK Integration**: ✅ **COMPLETED** - Hybrid approach successfully implemented and tested
  - **Issue**: JUCE's embedded VST3 SDK v3.6.13 vs external submodule v3.8.0 causing object files in submodule
  - **Solution**: Removed JUCE's embedded VST3 SDK, using external headers, compiling only missing utility functions
  - **Status**: ✅ Clean rebuild test passed, VST3 utility objects built in tmp/obj/vst3sdk/, no submodule pollution
  - **Verification**: `git status` in vst3sdk shows "working tree clean" - no untracked files

## Recent Commits (Most Recent First)

### 779bddcb - Restore vst3sdk submodule (Nov 5, 2025)
**What:** Re-added VST3 SDK submodule that was incorrectly removed  
**Files:** .gitmodules, vst3sdk/ submodule  
**Result:** Build completes successfully, VST3 support restored

### d431988d - Python 3 fixes for pi/logic/ and command-line tools
**What:** Fixed cascading import errors, Python 2→3 compatibility  
**Files:** pi/logic/*.py, pi/constraints.py, pisession/registry.py, app_cmdline/rexec.py  
**Result:** Most command-line tools now functional

Key changes:
- All pi/logic/ modules: bare/relative imports → absolute imports
- terms.py: Added cmp() polyfill, long=int, bytes.translate for strings
- tpg.py: parser.suite() → compile(), xrange → range
- builtin.py: Removed exceptions module import
- registry.py: Removed unused imp module import
- rexec.py: Use getpass.getuser() instead of session.get_username()

### 98f03aa8 - Template and import fixes for Python 3.14
**What:** Fixed PIP template for Python 3, fixed pi/ module imports  
**Files:** tools/pip_cmd/template, pi/*.py modules  
**Result:** Native modules build and import correctly

Key changes:
- Template: Fixed lock_c2p (removed PyGILState calls)
- Template: Added bytearray class support
- Template: Fixed moddoc quote handling
- pi/node.py, stateproxy.py, etc: Fixed bare imports

### 55a8e099 - Build system and syntax fixes for Python 3.14
**What:** Initial Python 3 build working  
**Files:** Hundreds of .py files, SConscript files, tools/  
**Result:** Full build completes successfully

## Next Steps (Priority Order)

### 1. Fix cheatsheet (5 minutes)
**File:** app_cmdline/cheat.py line 27  
**Issue:** `TypeError: can only concatenate list (not "range") to list`  
**Fix:** Change `[x] + range(y)` to `[x] + list(range(y))`  

### 2. Test EigenD Daemon (30-60 minutes)
**Command:** `./tmp/bin/eigend --cmdline`  
**Expect:** May encounter additional import/compatibility issues  
**Strategy:** Fix errors as they appear, similar to command-line tools  

**Common issues to watch for:**
- More bare imports in agent modules
- Python 2→3 API changes (dict methods, string handling)
- Threading/GIL issues
- Plugin loading errors

### 3. Test base_loader (15 minutes)
**Command:** `./tmp/bin/base_loader`  
**Purpose:** Minimal setup without hardware  
**Tests:** Agent initialization, basic plugin loading  

### 4. Incremental Plugin Testing
**Strategy:** Test plugins one at a time to isolate issues  
**Start with:** plg_primitive (simplest), plg_simple  
**Later:** plg_audio, plg_midi, plg_synth  

## Testing Methodology

### Command-Line Tools Status
```
✅ WORKING:
- bcat, bls, bpaths         (basic tools)
- brexec, brpc, bscript     (RPC/execution)
- bdownload, capture        (data tools)
- signature, upgrade34      (system tools)
- annotate                  (setup annotation)
- bbrowse, brsh, mirror     (need running daemon)

⚠️ MINOR ISSUES:
- cheatsheet                (range concatenation - easy fix)

❌ EXPECTED FAILURES:
- brecdump                  (needs plg_recorder plugin built)
```

### Testing Commands
```bash
# Basic system info
./tmp/bin/brelease          # Should show: 2.2.1-community
./tmp/bin/bpaths            # Should show paths

# Test without daemon (should fail gracefully)
./tmp/bin/bls               # Should say "can't connect"
./tmp/bin/bcat --help       # Should show usage

# Test RPC tools
./tmp/bin/brexec --help     # Should show usage
./tmp/bin/brpc --help       # Should show usage

# Fix and test cheatsheet
./tmp/bin/cheatsheet        # Currently fails on range concatenation
```

## Key Technical Details

### Python 3 Import Behavior
**Problem:** Bytecode-only distribution (tmp/modules/ has only .pyc files)  
**Solution:** Must use absolute imports: `from pi.logic import terms`  
**Won't work:** Relative imports like `import terms` or `from . import terms`  

### PIP Binding System
**Files:** tools/pip_cmd/*.py, template  
**Process:** .pip file → C++ code → native .so module  
**Key fix:** Template now has correct Python 3 API (PyInit_*, PyCapsule, bytearray)  

### Build System
**Tool:** SCons 4.x (Python 3 compatible)  
**Command:** Use `make` not `scons` directly  
**Parallel:** `make -j8` for faster builds  
**Clean:** `make clean` removes tmp/ directory  

## Common Patterns for Fixes

### Import Errors in pi/ modules
```python
# WRONG (Python 2 style)
import const, utils

# RIGHT (Python 3 with packages)
from pi import const, utils
```

### Import Errors in pi/logic/ modules
```python
# WRONG (relative)
import terms
from . import terms

# RIGHT (absolute)
from pi.logic import terms
```

### Python 2 API Removals
| Python 2 | Python 3 |
|----------|----------|
| `cmp(a,b)` | `(a > b) - (a < b)` or functools.cmp_to_key |
| `long` | `int` (unified) |
| `xrange` | `range` |
| `string.maketrans` | `bytes.translate` or `str.maketrans` |
| `parser` module | `compile()` or `ast` module |
| `exceptions` module | builtin `Exception` |
| `imp` module | `importlib` (or remove if unused) |

### Exception Syntax
```python
# WRONG
except ValueError, e:
    raise RuntimeError, msg

# RIGHT  
except ValueError as e:
    raise RuntimeError(msg)
```

## Files Modified (Tracking)

### Commit d431988d
- pi/logic/terms.py (cmp, long, string ops)
- pi/logic/tpg.py (parser module, xrange)
- pi/logic/parse.py, parse_new.py (imports)
- pi/logic/builtin.py (exceptions module)
- pi/logic/cli.py, logic_test.py (imports)
- pi/logic/__init__.py (imports)
- pi/constraints.py (imports)
- pisession/registry.py (imp module)
- app_cmdline/rexec.py (getpass.getuser)

### Commit 98f03aa8
- tools/pip_cmd/template (lock_c2p, bytearray, moddoc)
- pi/node.py, stateproxy.py (imports)
- pi/atom_test.py, domain_test.py (imports)
- pi/logic/__init__.py, engine.py, shortcuts.py, fixture.py (imports)
- documentation/*.md (created/updated)

### Commit 55a8e099
- Hundreds of .py files (print, except, dict methods, etc)
- Many SConscript files
- tools/*.py (build system)

## Debugging Tips

### Import Errors
1. Check if module uses bare imports
2. Change to `from pi import ...` or `from pi.logic import ...`
3. Remove bytecode: `rm -f tmp/modules/path/to/module.pyc`
4. Rebuild: `make -j8`

### Module Not Found
1. Check spelling and case
2. Verify module exists in source tree
3. Check if it's a Python 2→3 renamed module
4. Search git history: `git log --all -S "module_name"`

### Runtime Errors
1. Check error traceback for line number
2. Look for Python 2 API usage (cmp, long, xrange, etc)
3. Compare with python3 branch (but be aware it has bugs)
4. Test incrementally with small changes

### Build Errors
1. Make sure using Python 3.14: `which python3.14`
2. Clean build: `make clean && make -j8`
3. Check for C++ compilation errors (usually in PIP bindings)
4. Verify SCons4 in path: `echo $PYTHONPATH`

## Reference Documentation

**In this repo:**
- documentation/copilot-python_dev_notes.md - Detailed changelog
- documentation/copilot-python_dev_todo.md - Task tracking
- documentation/copilot-python_dev_howitworks.md - Quick reference
- .github/copilot-instructions.md - System architecture

**External:**
- Python 3 What's New: https://docs.python.org/3/whatsnew/
- Python 2→3 Porting: https://docs.python.org/3/howto/pyporting.html
- C API Changes: https://docs.python.org/3/c-api/

## Expected Issues in Daemon Testing

Based on patterns so far, expect:

1. **More import errors** in agent modules (plg_*/*)
2. **Dictionary iteration** - .iteritems() → .items()
3. **String/bytes confusion** - especially in MIDI/binary protocols
4. **Unicode handling** - file paths, agent names
5. **Threading issues** - GIL behavior changes
6. **Plugin loading** - dynamic import changes

## Success Criteria for This Phase

**Daemon starts:** `./tmp/bin/eigend --cmdline` runs without crashes  
**Base setup loads:** Can initialize minimal agent system  
**RPC works:** Can execute commands via brexec  
**No deadlocks:** System doesn't hang on startup  

**NOT required yet:**
- Hardware communication (Eigenharp devices)
- Audio processing (real-time DSP)
- All plugins working (test incrementally)
- GUI applications (Workbench, Stage)

## Contact/Resources

**Repository:** https://github.com/TheTechnobear/EigenD  
**Branch:** copilot  
**Base work:** TheTechnobear's python3 branch (but with fixes)  
**Original:** EigenD 2.2.x (Python 2.7)

---

**Ready to continue!** Start with fixing cheatsheet, then test daemon.

---
**2025-11-07:** Split `.github/chatmodes/Testing.chatmode.md` into a concise chatmode and a detailed prompt file at `dev_docs/prompts/Testing.chatmode.details.md`. The concise file directs agents to respond with three short bullets (Done / Discovered / Next). Changes made by automated assistant during this session.
nin 