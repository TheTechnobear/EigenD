# How the Python 3 Migration Works

## Overview
Quick reference for understanding the Python 3.14 migration architecture.
Not comprehensive - just key concepts for debugging/maintenance.

## PIP Binding System

### What is PIP?
Custom Python Interface Protocol - generates C++ bindings for Python
Similar to SWIG but custom-built for EigenD's needs

### Key Files
- `.pip` files: Interface definitions (like `.h` headers with Python decorations)
- `tools/pip_cmd/template`: C++ code skeleton with `<<variable>>` placeholders
- `tools/pip_cmd/parse.py`: Parses .pip files using PLY lexer/yacc
- `tools/pip_cmd/expand.py`: Substitutes variables into template
- `tools/pip_cmd/pip.py`: Main orchestrator

### Build Flow
1. SCons4 (Python 3 compatible) reads SConscript files
2. SCons calls `pip.py` with `.pip` file as input
3. `parse.py` tokenizes .pip, extracts classes/methods/docstrings
4. `expand.py` substitutes parsed data into template
5. Generates `*_python.cpp` file in `tmp/obj/`
6. C++ compiler builds native module (`.so` file)
7. Python imports `modulename_native` at runtime

### PLY Parser/Lexer
Uses PLY (Python Lex-Yacc) for parsing .pip files
`lex.py` and `yacc.py` in `tools/pip_cmd/` directory
Updated to Python 3 compatible version from PLY project

### Critical Template Variables
- `<<module>>`: Module name (e.g., `piw_native`)
- `<<moddoc>>`: Module docstring (already quoted by parse.py)
- `<<name>>`: Class or function name
- `<<flags>>`: Compilation flags (locked, etc)

## Python/C++ Bridge

### Type Conversions
`tpcvt_*` functions: C++ → Python object
`fpcvt_*` functions: Python object → C++

Examples:
- `tpcvt_stdstr`: std::string → PyUnicode
- `tpcvt_bytearray`: bytearray → PyBytes
- `fpcvt_str`: PyUnicode → const char*
- `fpcvt_bytearray`: PyBytes → bytearray

### Thread Safety (lock_c2p)
When C++ code calls Python, must acquire GIL (Global Interpreter Lock)
`lock_c2p` class: RAII wrapper for thread-safe Python calls

**Python 3 changes:**
- No `PyGILState_Ensure/Release` (simplified)
- Creates new thread state with `PyThreadState_New`
- Acquires with `PyEval_AcquireThread`
- Releases with `PyEval_ReleaseThread`

### Binary Data (bytearray)
Python 3 distinguishes `str` (text) from `bytes` (binary)
`bytearray` class: C++ wrapper for binary data
Used for MIDI messages, firmware uploads, raw USB data

## Module Initialization

### Python 2 vs Python 3
**Python 2:** `initmodulename()` function
**Python 3:** `PyInit_modulename()` function returns `PyObject*`

### Module Structure
```cpp
PyInit_modulename() {
    // Create module with PyModuleDef
    // Add types to module
    // Add functions to module
    // Set __doc__ from module_docstring
    // Return module object
}
```

## String Handling

### Python 2: PyString (bytes)
All strings were byte strings (ASCII/bytes)

### Python 3: PyUnicode (text)
Strings are Unicode text by default
`PyBytes` for binary data

**Migration pattern:**
- `PyString_*` → `PyUnicode_*` for text
- Use `PyBytes_*` for binary data (MIDI, firmware, etc)
- `PyUnicode_AsUTF8` returns `const char*` (temporary!)

## Object Types (PyTypeObject)

### Structure Changes in Python 3
- `ob_size` removed (now in `PyVarObject_HEAD_INIT`)
- `tp_print` removed (debugging feature obsolete)
- `tp_compare` removed (use `tp_richcompare`)
- `tp_as_async` added (for `async`/`await` support)

### Member Access
**Python 2:** `obj->ob_type->tp_free(obj)`
**Python 3:** `Py_TYPE(obj)->tp_free(obj)` (macro for safety)

## Session Management

### Startup Flow
1. `eigend` main() in `app_eigend2/eigend.cpp`
2. Creates `piagent::scaffold` (multi-threaded or GUI)
3. Scaffold creates context threads (fast/slow/worker)
4. Python session initialized via `pisession/session.py`
5. Agents loaded via `pisession/agentd.py`
6. Plugins connect via `piw` (Pi Wire) signal graph

### Context Threads
- Fast context: Real-time audio processing
- Slow context: UI updates, non-realtime work
- Each context has own thread state for Python calls

## Common Gotchas

### Unicode vs Bytes
Python 3 will error if you mix text (str) and binary (bytes)
MIDI/firmware code must use `bytes`/`bytearray`, not `str`

### Dictionary Views
`dict.keys()` returns view, not list
Must use `list(dict.keys())` if you need list operations

### Integer Division
`5/2` returns `2.5` in Python 3 (was `2` in Python 2)
Use `5//2` for integer division

### Range Returns Iterator
`range(10)` is iterator, not list
Use `list(range(10))` if you need list
Affects concatenation: `[x] + range(y,z)` → `[x] + list(range(y,z))`

### Print is Function
`print x, y` → `print(x, y)`
Affects stderr redirect: `print >>sys.stderr, msg` → `print(msg, file=sys.stderr)`

### File Operations
`file()` constructor removed, use `open()`
`'rU'` mode deprecated, use `'r'` (universal newlines default)

### Input Functions
`raw_input()` unified into `input()` (Python 3 input returns string)

### Comparison
`cmp()` function removed
Use `functools.cmp_to_key()` to wrap old comparison functions
Sort key functions preferred over comparison functions

## Debugging Tips

### Module Loading Issues
Check `PyInit_modulename` is defined (not `initmodulename`)
Verify module name matches between .pip and SConscript

### GIL Deadlocks
Check all C++ → Python calls use `lock_c2p`
Verify no Python 2 locking APIs remain

### Type Errors
Check PyUnicode vs PyBytes usage
Verify bytearray used for binary data, not strings

### Build Issues
Delete `tmp/obj/*_python.cpp` to force regeneration
Check template syntax with `<<variable>>` not `${variable}`
