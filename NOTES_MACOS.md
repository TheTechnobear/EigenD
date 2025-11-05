## STATUS

experimental pre-release 2.2.0



## PYTHON 3.14 MIGRATION STATUS

### Completed ✅
- **pi/ modules**: All Python modules in the pi/ directory have been successfully migrated to Python 3.14
  - Fixed print statements → print() function calls
  - Updated exception handling: `except X, e:` → `except X as e:`
  - Replaced `raise Exception, msg` → `raise Exception(msg)`
  - Fixed file() → open() calls
  - Updated exec statements for Python 3 syntax
  - Replaced has_key() → 'in' operator
  - Updated types module references (ListType→list, DictType→dict, etc.)
  - Fixed hashlib string encoding issues
  - Replaced func_code → __code__ attributes
  - Updated imports and other Python 2/3 incompatibilities
  - **Validation**: All pi/ modules compile successfully with `python3 -m py_compile`

- **Build System Core**: 
  - Integrated SCons4 (modern SCons version) to replace incompatible embedded SCons
  - SCons initialization and basic functionality working
  - Build process starts and reads SConscript files correctly

### In Progress 🚧
- **pip_cmd Tools**: Extensive fixes applied to PLY-based parser tools (lex.py, yacc.py, parse.py, process.py, expand.py, error.py, pip.py)
  - Fixed major syntax issues from automated conversion corruption
  - Corrected corrupted has_key() replacements (e.g., `Terminals in n` → `n in Terminals`)
  - Updated types module references (types.InstanceType removed, types.ListType→list, etc.)
  - Fixed func_code → __code__ attributes
  - Updated StandardError → Exception
  - Fixed cmp() function usage in sorting → key functions
  - Resolved dict_keys concatenation issues (Python 3 dict.keys() not addable)
  - **Current Status**: yacc.yacc() execution progressing but still encountering corrupted "in" operator replacements

### Remaining Work 📋
- **Complete pip_cmd Tools Migration**:
  - Fix all remaining corrupted "in" operator replacements from sed commands
  - Test yacc.yacc() execution success
  - Validate complete parser pipeline (lex → yacc → parse → process → expand)
  
- **C++ Wrapper Generation**:
  - Ensure pip_cmd tools generate correct C++ bindings for native extensions
  - Test compilation of generated wrapper code
  
- **Full Build Pipeline**:
  - Validate end-to-end build from Python modules → C++ wrappers → native extensions
  - Test plugin loading and functionality
  
- **Integration Testing**:
  - Verify EigenD daemon (eigend2) starts with Python 3.14
  - Test plugin ecosystem functionality
  - Validate Belcanto command processing

### Known Issues
- Build currently fails during yacc.yacc() execution due to remaining corrupted dictionary membership tests
- Some automated conversion tools (sed) introduced syntax errors that require manual correction
- Extensive PLY library (Python Lex-Yacc) contains many Python 2 idioms requiring systematic fixes

### Next Steps
1. Complete all corrupted "in" operator fixes in yacc.py and other pip_cmd files
2. Test successful yacc.yacc() execution
3. Validate C++ wrapper generation
4. Test full native extension build pipeline
5. Perform integration testing of complete system

### Migration Strategy Notes
- **Validation Approach**: Iterative build testing to identify and fix Python 2/3 incompatibilities as they surface
- **Tool Issues**: Automated conversion tools can corrupt code; manual verification essential
- **Scope**: Migration covers both Python modules and build system tools for complete Python 3.14 compatibility
- **Testing**: Each fix validated through build attempts to ensure progress toward working native extensions



## requirements 

MIN macos 10.13 (High Sierra)

system python at /System/Library/Frameworks/Python.framework/Versions/2.7/bin/python



## Known issues 
(will fix)
- convolver is disabled on apple silicon (only)


## Limitations (will not change)
- Carbon is not supported on arm
- can only load plugins of same architecture , i.e. intel 64 bit only , or arm only, no bridging
- no universal binary


## currently not support
- EigenCommander & EigenBrowser



## BUILDING on macos

arm  build
export BUILD_TARGET=arm
make
make mpkg

64 bit intel  build
export BUILD_TARGET=x86_64
make
make mpkg




------


## Code issues/notes

//ARMHACK

pic_resources.cpp : 561 ///HACKED - no close function... move to fopen/fclose?
libfftw:  disabled  SConfig, no ARM
plg_convolver disabled SConfig no libfftw




not used anymore since default has changed, but useful to know
export PI_PYTHON=/System/Library/Frameworks/Python.framework/Versions/2.7/bin/python


