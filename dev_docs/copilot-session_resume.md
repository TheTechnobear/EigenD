# EigenD Python 3.14 Migration - Session Resume Context

**Date:** 2025-11-06  
**Branch:** copilot  
**Status:** � **ROOT CAUSE IDENTIFIED** - PIW string corruption in Python 3 bindings

## 🎯 BREAKTHROUGH: Root Cause 100% Confirmed

### **CRITICAL ISSUE: PyUnicode_AsUTF8 Pointer Corruption**
**Location:** `agentd.py` line 1035
**Problem:** `piw.term(string, type_code)` uses wrong constructor
**Root Cause:** Python 3 binding `fpcvt_str()` creates dangling pointers

#### **Exact Technical Details:**
```cpp
// In tmp/obj/piw/src/piw_native_python.cpp (generated binding):
int fpcvt_str(PyObject *o, void *a) {
    const char *s = PyUnicode_AsUTF8(o);  // ← DANGEROUS
    if(s) { *((const char **)a) = s; return 1; }  // ← STORES INTERNAL BUFFER POINTER
    return 0;
}

// Called by: piw.term(string, type_code) 
// → PyArg_ParseTuple(args,"O&O&", fpcvt_str, &a0, fpcvt_ui, &a1)
// → term_wrapper_(..., const char *a0, unsigned int a1)
// → term_type_(a0, a1)  // PREDICATE constructor, NOT data constructor!
```

#### **Why This Fails:**
1. **Wrong Constructor:** `term_t(const char *, unsigned)` is for **predicates** ("foo(arg1,arg2)"), NOT string data
2. **Pointer Corruption:** `PyUnicode_AsUTF8()` returns pointer to internal Python Unicode buffer
3. **Dangling Reference:** When Python string gets garbage collected, pointer becomes invalid  
4. **Segfault:** Later access to `.pred()` → `PyUnicode_FromString(corrupted_ptr)` → crash

#### **Migration Factor:**
- **Python 2.7:** Used `PyString_AsString()` with different lifetime semantics
- **Python 3.x:** Uses `PyUnicode_AsUTF8()` with internal buffer tied to object lifetime
- **Impact:** Same semantic bug now causes corruption instead of working by accident

#### **Evidence - Stack Trace from Segfault:**
```
PyUnicode_FromString+0x14 [corrupted pointer]
term_wrapper_::pred_method_ [calling .pred() on corrupted term]
```

#### **SOLUTION:**
```python
# WRONG (current agentd.py line 1035):
term = piw.term(string, type_code)  # Creates predicate term with dangling pointer

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
