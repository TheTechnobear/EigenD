# Python 3.14 Migration Notes - Copilot Branch

## Current Status (Updated: 2025-11-05)

**✅ BUILD COMPLETE** - Full system builds successfully with Python 3.14  
**✅ BASIC RUNTIME WORKING** - Most command-line tools functional  
**🔄 IN PROGRESS** - Testing daemon startup and plugins

### What's Working
- ✅ Full build completes (make, make mpkg)
- ✅ PIP binding system (C++/Python integration)
- ✅ Command-line tools: bcat, bls, bpaths, brexec, brpc, bscript, bdownload, capture, signature, upgrade34, annotate
- ✅ Belcanto logic system (pi/logic/) imports and initializes
- ✅ Core pi/ modules load correctly
- ✅ Session and agent management modules import

### What's Not Yet Tested
- ⚠️ EigenD daemon startup (eigend)
- ⚠️ Plugin loading and initialization
- ⚠️ Audio/MIDI real-time processing
- ⚠️ Hardware communication (Eigenharp devices)
- ⚠️ GUI applications (Workbench, Stage)

### Known Minor Issues
- cheatsheet: range() concatenation needs list() wrapper
- brecdump: Expected failure (needs plg_recorder plugin built)

## Overview
Migration of EigenD from Python 2.7 to Python 3.14 on copilot branch.
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

## Next Steps (see copilot-python_dev_todo.md)
