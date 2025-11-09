# Python 3.14 Migration Notes - Python3 Branch


## ✅ Completed - November 2025

### piw.data Comparison Fix - Python 3 Rich Comparison Protocol ✅ (Nov 9, 2025)
**Problem**: Setup loading hung due to spurious domain change notifications
**Root Cause**: `piw.data.__eq__` used identity comparison instead of content comparison (Python 2's `__cmp__` removed in Python 3)
**Solution**: Updated PIP template to generate `tp_richcompare` from existing `__cmp__` method

**Implementation**:
- Added `special_richcompare_method_()` to PIP template (lines 909-951)
- Updated `tp_richcompare` slot to conditional function pointer (line 1459)
- Uses `PyType_IsSubtype(Py_TYPE(other), Py_TYPE(self))` for runtime type checking

**Files Changed**:
- `tools/pip_cmd/template` - Rich comparison generation
- `tests/unit/test_02_data_layer.py` (lines 488-687) - Comprehensive comparison tests

**Testing**: ✅ All 5 TestPiwDataComparison tests passing
- test_data_equality_basic
- test_data_equality_strings
- test_data_equality_dict_lookup (proxy.py use case)
- test_data_richcompare_all_operators (all 6: <, <=, ==, !=, >, >=)
- test_data_nb_inherits_comparison (subtype inheritance)

**Result**: ✅ Setup loading now works correctly, no spurious node_changed() calls
**Impact**: Fixed major Python 3 migration blocker - setup loading system fully functional

### PIW String Term Corruption Fix ✅ (Nov 6, 2025)

**ROOT CAUSE IDENTIFIED**: PyUnicode_AsUTF8 Pointer Corruption in Python 3 Bindings

**Issue**: `eigend` startup failed with corrupted PIW string terms
**Location**: `agentd.py:1035` - `piw.term(string, type_code)` 
**Symptoms**: Segfaults, assertion failures, "null term" errors

**Technical Root Cause**:
1. **Wrong Constructor Used**: `piw.term(string, arity)` creates **predicate terms**, not **data terms**
2. **Pointer Corruption**: Python 3 binding `fpcvt_str()` uses `PyUnicode_AsUTF8()` which returns internal buffer pointer
3. **Dangling Reference**: When Python string gets GC'd, C++ term stores invalid pointer
4. **Segfault on Access**: Later `.pred()` calls → `PyUnicode_FromString(corrupted_ptr)` → crash

**Migration Impact**:
- **Python 2.7**: Used `PyString_AsString()` - different lifetime semantics allowed wrong usage to work
- **Python 3.x**: `PyUnicode_AsUTF8()` buffer lifetime tied to Python object - exposes the bug

**Solution**:
```python
# BROKEN:
term = piw.term(string, type_code)  # Predicate constructor + dangling pointer

# FIXED:
term = piw.term(piw.makestring(string, 0))  # Data constructor, proper lifetime
```

**Constructor Semantics**:
- `piw.term(const char *, unsigned)` → **Predicate term** for "foo(arg1, arg2)" structures
- `piw.term(const piw::data_t &)` → **Data term** for storing actual values

**Status**: Fixed and validated with comprehensive test suite

### EigenD Empty String Display Issue ✅ (Nov 6, 2025)
- **Problem**: EigenD GUI showing empty strings instead of values  
- **Root Cause**: Added defensive `is_string()` checks in `app_eigend2/eigend.cpp` but `is_string()` function had issues
- **Solution**: Reverted all defensive checks to original direct `as_string()` calls
- **Files Fixed**: `app_eigend2/eigend.cpp` (restored slot_, selected_, setup logic)
- **Result**: String display working correctly again

### Test Runner Enhancement for TDD ✅ (Nov 6, 2025)
- **Problem**: Session teardown taking 30+ seconds hindering TDD workflow
- **Solution**: Added `--quick/-q` mode with 5s timeout and session teardown skip
- **Implementation**: Enhanced `run_tests.sh` and `tests/conftest.py` with threading timeout
- **Performance**: ~75% faster (6s vs 30s), enabling rapid iteration cycles
- **Usage**: `./run_tests.sh --quick --level foundation`

### PIP Template Constructor Exception Handling Fix ✅ (Nov 5, 2025)
**Issue**: Copy constructor failures with "function takes exactly 2 arguments (1 given)"
**Root Cause**: PIP template didn't clear exceptions between constructor attempts
**Analysis**: Same bug exists in both Python 2.7 and 3.14 templates, but only manifests as failure in Python 3.14
**Fix**: Added `PyErr_Clear()` after each failed constructor attempt in `tools/pip_cmd/template`
**Impact**: Fixes all copy constructors across PIW binding system (`piw.term(existing)`, `piw.data(existing)`, etc.)
**Validation**: All term constructor tests pass (12/12)
**Files**: tools/pip_cmd/template

### Timer Race Condition Fix ✅ (Nov 5, 2025)
**Issue**: Timer callbacks firing during constructor exceptions caused additional crashes
**Analysis**: Using LLDB revealed timer was accessing partially-constructed objects
**Fix**: Identified root cause vs secondary symptoms in crash analysis
**Result**: Clean exception reporting without timer interference

### Cheatsheet Command Fix ✅ (Nov 5, 2025)
**Issue**: `TypeError: can only concatenate list (not "range") to list`
**Fix**: `[x] + range(y)` → `[x] + list(range(y))` in app_cmdline/cheat.py
**Result**: Identical output to Python 2.7 version

### EigenD Daemon Startup Fixes ✅ (Nov 5, 2025)
Multiple Python 2→3 compatibility issues resolved:
- Fixed: `httplib` → `http.client` (bugs_cli.py)
- Fixed: `range().reverse()` → `list(range()).reverse()` (pi/resource.py)  
- Fixed: `map()` iterator → `list(map())` (pi/resource.py)
- Fixed: Missing imports and method implementations (bugs_cli.py, backend.py)
- Fixed: `xmlrpclib` → `xmlrpc.client` (latest_release.py)
- Fixed: `xrange` → `range` (backend.py)
- Result: Daemon starts successfully, identical behavior to Python 2.7

### Core Migration Work ✅ (Completed Earlier)
- ✅ Full build completes (make, make mpkg)
- ✅ PIP binding system (C++/Python integration)
- ✅ All command-line tools: bcat, bls, bpaths, brexec, brpc, bscript, bdownload, capture, signature, upgrade34, annotate, cheatsheet
- ✅ Belcanto logic system (pi/logic/) imports and initializes
- ✅ Core pi/ modules load correctly
- ✅ Session and agent management modules import
- ✅ All 50+ plugins discovered and loaded
- ✅ Python modules load successfully

---

## 📚 Migration Reference Documentation

### Migration Status Summary
**Core Python 3.14 migration: COMPLETE** ✅
- All Python modules load and function correctly
- PIP binding system works with Python 3.14  
- Constructor dispatch issues resolved
- All command-line tools functional
- Setup loading system working
- Controller attach/detach loop fixed
- Comprehensive test suite in place

**Ready for**: Hardware testing, platform validation, final release preparation

## Overview
Migration of EigenD from Python 2.7 to Python 3.14 on python branch.
Building on earlier work by TheTechnobear (python3 branch) but with more complete fixes and testing.

## Target Environment
- Python 3.14 from Homebrew (/opt/homebrew/opt/python@3.14/bin/python3.14)
- macOS Apple Silicon (arm64)
- No backwards compatibility - Python 3 only

## Python Syntax Changes Fixed

### Print statements
`print x` → `print(x)`

### Exception handling
`except Exception, e:` → `except Exception as e:`
`raise ValueError, msg` → `raise ValueError(msg)`

### Long integers
`0L` → `0` (Python 3 unifies int/long)

### Dictionary methods
`dict.has_key(x)` → `x in dict`
`dict.iteritems()` → `dict.items()`
`dict.keys().sort()` → `sorted(dict.keys())`

### Imports
`import cStringIO` → `import io`
`import types; types.StringType` → `isinstance(x, str)`
`types.ListType/DictType/TupleType` → `list/dict/tuple`
`import httplib` → `import http.client`
`from SimpleXMLRPCServer import` → `from xmlrpc.server import`
`import urllib; urllib.unquote` → `import urllib.parse; urllib.parse.unquote`
`import ConfigParser` → `import configparser`
`StandardError` → `Exception` (StandardError removed)

### Reserved keywords
`async` → `piasync` (async became keyword in Python 3.5)
Renamed `pi/async.py` → `pi/piasync.py` and updated all imports

### String/bytes handling
`string.maketrans` → `str.maketrans` (different API in Python 3)
Range returns iterator not list: `[x]+range(y,z)` → `[x]+list(range(y,z))`

### Comparison
`cmp()` function removed → use `functools.cmp_to_key()` with sorted()

### Tabs to spaces
All Python files converted to spaces for Python 3 compatibility

### File operations
`file()` → `open()` (file() removed in Python 3)
`open(f, 'rU')` → `open(f, 'r')` (universal newlines deprecated)

### Input functions
`raw_input()` → `input()` (Python 3 unifies input functions)

### Octal literals
`0755` → `0o755` (explicit octal prefix required)

### Function attributes
`func.func_code` → `func.__code__` (dunder naming convention)

### Hash updates
`hashlib.sha256().update(str)` → `.update(str.encode('utf-8'))` (bytes required)

## C API Changes in tools/pip_cmd/template

### Module initialization
`init<<module>>()` → `PyInit_<<module>>()` (line 1683)

### PyTypeObject structure
`PyObject_HEAD_INIT(NULL) 0` → `PyVarObject_HEAD_INIT(NULL, 0)`
Removed: `ob_size`, `tp_print`, `tp_cmp` fields
`ob_type->tp_free` → `Py_TYPE(self)->tp_free` (line 1267)

### Void function returns
`return NULL;` → `return;` in void functions (line 726)

### PyCObject → PyCapsule API
`PyCObject_FromVoidPtr(a,b)` → `PyCapsule_New(a, NULL, b)` (line 1754)
`PyCObject_AsVoidPtr(a)` → `PyCapsule_GetPointer(a, NULL)` (line 1711)
`PyCObject_Check(a)` → `PyCapsule_CheckExact(a)` (line 1705)

### String API
`PyString_FromString` → `PyUnicode_FromString`
`PyString_AsString` → `PyUnicode_AsUTF8`
`PyString_AsStringAndSize` → `PyUnicode_AsUTF8AndSize`
`PyString_Check` → `PyUnicode_Check`

### Integer API
`PyInt_FromLong` → `PyLong_FromLong`
`PyInt_AsLong` → `PyLong_AsLong`
`PyInt_Check` → `PyLong_Check`

### Thread locking (CRITICAL FIX)
**OLD (Python 2):**
```cpp
PyEval_AcquireLock()
PyGILState_Ensure()
```

**NEW (Python 3):**
```cpp
PyThreadState_New(interp)
PyEval_AcquireThread(t_)
```
Removed `PyGILState_STATE gs_` member variable
Removed all `PyGILState_Ensure/Release` calls

### Docstring handling
Template had `"<<moddoc>>"` → changed to `<<moddoc>>` (no quotes)
The parse.py already wraps lines in quotes, extra quotes caused `""""""` syntax errors

### Binary data support
Added `bytearray` class for passing binary data (not strings) between Python/C++
Added `tpcvt_bytearray()` and `fpcvt_bytearray()` conversion functions
Uses `PyBytes_FromStringAndSize` and `PyBytes_AsStringAndSize`

### Term Constructor Analysis (PyString Migration)
**Root Cause**: `term(data)` constructor broken due to `fpcvt_data` dispatcher issue
**Solution**: Use `data_to_term()` workaround in `pisession/agentd.py`

| Constructor | Status | Notes |
|-------------|--------|-------|
| `term()` | ✅ Working | Empty term creation |
| `term(unsigned)` | ✅ Working | Numeric values |
| `term(string, type)` | ✅ Working | Strings (type ignored, auto-assigned as 3) |
| `term(term)` | ❌ Broken | Copy constructor has parameter mismatch |
| `term(data)` | ❌ Broken | Data wrapper conversion fails |

**Key Findings**:
- All string terms automatically assigned type 3
- Binary protocol compatibility preserved across Python versions
- PIP bindings correctly use `PyUnicode_AsUTF8AndSize()` for Python 3

## C API Changes in Other Files

### pisession/src/pis_python.cpp
`PyEval_AcquireLock` → `PyEval_RestoreThread` (lines 62-64)
`PyEval_ReleaseLock` → `PyEval_SaveThread` (line 93)
`PyString_FromString` → `PyUnicode_FromString` (lines 103, 172)
`PyCObject_FromVoidPtr` → `PyCapsule_New` (lines 178, 218)
`PyString_AsStringAndSize` → `PyUnicode_AsUTF8AndSize` (line 236)

### lib_juce/epython.cpp
`Py_SetPythonHome` now takes `wchar_t*` (lines 43-47)
`PyString_Check` → `PyUnicode_Check` (line 148)
`PyString_AsString` → `PyUnicode_AsUTF8` (line 156)
`PyCObject_AsVoidPtr` → `PyCapsule_GetPointer` (line 181)

### app_juceworkbench/epython.cpp
Already correct - no changes needed

## PIP System Issues Fixed

### tools/pip_cmd/expand.py
**BUG:** Line 30 had `type(dict) != dict` which shadowed built-in `dict` type
**FIX:** Changed to `isinstance(dict_obj, dict)`
This was blocking module name expansion causing `PyInit_()` instead of `PyInit_modulename()`

### .pip files with PyCObject
Found lingering `PyCObject_*` calls in:
- app_eigend2/eigend.pip (line 41)
- app_install/post_install.pip (line 17)
- app_juceworkbench/workbench.pip (lines 14, 92)
- piagent/piagent.pip (line 93)
- piw/piw.pip (lines 2017, 2066)

All replaced with `PyCapsule_*` equivalents

## Build System

### SCons4 Integration
Upgraded from SCons 2.5.1 (2016, Python 2 only) to SCons 4.x (Python 3 compatible)
Old versions archived in `tools/packages/archive/`
Build configured via `PYTHONPATH=$(TOOLS)/packages/SCons4`
No EigenD-specific modifications to core SCons code

### VST3 SDK Integration
VST SDK 3.8.0_build_66 integrated as separate library (not git submodule)
SConscript files updated to link vst3sdk library

### Parallel builds
Added `parallel:` target to tools/Makefile using `-j8` flag
Speeds up build significantly on multi-core systems

### Migration artifacts
Old migration scripts archived in `migration_scripts/` directory
Old SCons versions in `tools/packages/archive/` for potential future removal

## Known Issues Encountered and Fixed

### Initial import error
"ImportError: dynamic module does not define module export function (PyInit_piw_native)"
**CAUSE:** expand.py type bug prevented module name expansion
**FIXED:** Changed type comparison to isinstance check
**COMMIT:** 98f03aa8

### Docstring C syntax errors
Generated code had `""""""` causing compilation errors
**CAUSE:** Template had extra quotes around `<<moddoc>>`
**FIXED:** Removed quotes - parse.py already adds them
**COMMIT:** 98f03aa8

### PyCObject deprecation
Old API still in template and .pip files
**FIXED:** Replaced all with PyCapsule API
**COMMIT:** 98f03aa8

### Python 3 GIL API changes
Template used deprecated PyGILState_Ensure/Release in lock_c2p
**FIXED:** Removed GIL calls - not needed for simple callback context
**COMMIT:** 98f03aa8

### Missing bytearray support
Template lacked bytearray class for Python 3 bytes handling
**FIXED:** Added bytearray class with converters (tpcvt_bytearray, fpcvt_bytearray)
**COMMIT:** 98f03aa8

### Import errors in pi/ modules
Bare imports like `import const, utils` failed in Python 3 package context
**FIXED:** Changed to `from pi import const, utils` throughout pi/ modules
**COMMIT:** 98f03aa8

### Import errors in pi/logic/ subpackage
Relative imports failed with bytecode-only distribution
**FIXED:** Changed all to absolute imports `from pi.logic import ...`
**COMMIT:** d431988d

### Python 2 standard library removals
- `parser` module (removed Python 3.9): Fixed with compile() in tpg.py
- `exceptions` module (removed Python 3): Changed to builtin Exception
- `imp` module (removed Python 3.12): Removed unused import from registry.py
**COMMIT:** d431988d

### Python 2→3 compatibility in pi/logic/terms.py
- `cmp()` function removed: Added polyfill
- `long` type removed: Added `long = int` alias  
- `string.maketrans()` removed: Used bytes.translate() pattern
**COMMIT:** d431988d

### session.get_username() not found
rexec.py called non-existent module function
**FIXED:** Use getpass.getuser() instead
**COMMIT:** d431988d

### Thread locking (potential deadlock issue)
Using old Python 2 GIL locking could cause hangs on startup
**FIXED:** Updated lock_c2p to Python 3 API (removed PyGILState calls)

## Testing Status
- Build completes successfully with no errors ✅
- All native modules compile and link ✅
- Python module compilation: All modules validate with `python3 -m py_compile` ✅
- C++ binding generation: pip_cmd tools successfully generate wrappers ✅
- Native libraries: libpic, libpia, libpie, libpiw, libpisamplerate compile ✅
- Plugin extensions: plg_* native modules build and link ✅
- Runtime testing: NOT YET DONE ⚠️
- Command-line tools (bcat, bls, rpc): NOT TESTED
- EigenD daemon: NOT TESTED
- Plugins: NOT TESTED

## Comparison with TheTechnobear's python3 Branch
- Core C API changes: IDENTICAL ✅
- Template fixes: SAME APPROACH ✅
- Critical difference found: lock_c2p implementation (now fixed) ✅
- bytearray class: ADDED (was in python3 branch) ✅
- Documentation copied with "technobear-" prefix for reference

