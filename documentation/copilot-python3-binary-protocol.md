# EigenD Binary Protocol Layer - Python 2→3 Migration Analysis

## Overview

EigenD uses a custom binary protocol for communication between components that must remain stable across Python versions and even machine architectures. This protocol is critical for client-server communication and data serialization.

## Architecture

```
┌─────────────────┐    Binary Protocol    ┌─────────────────┐
│   Client Tools  │◄──────────────────────►│   eigend Server │
│   (bls, rpc,    │                        │                 │
│    cheatsheet)  │                        │                 │ 
└─────────────────┘                        └─────────────────┘
        │                                           │
        │                                           │
    Python 3.14                                Python 3.14
   (any version)                              (any version)
        │                                           │
        │                                           │
┌─────────────────┐                        ┌─────────────────┐
│  Native Modules │                        │  Native Modules │
│  (piw_native,   │                        │  (piw_native,   │
│   etc.)         │                        │   etc.)         │
└─────────────────┘                        └─────────────────┘
```

## Binary Protocol Components

### 1. Data Objects (`piw::data_t`)

Data objects are type-safe wrappers around raw values with binary-stable representation:

```cpp
// C++ side
class data_t {
    unsigned data_type();        // Type identifier (2=string, 6=bool, etc.)
    bool is_string();           // Type checking
    bool is_bool();
    const char* as_string();    // Value extraction
    bool as_bool();
    // ... binary serialization methods
};
```

**Critical Migration Issue**: The Python 3 PIP bindings were partially updated:
- ✅ `makestring()` correctly handles Unicode → UTF-8 conversion
- ❌ `term(data)` constructor binding is broken

### 2. Term Objects (`piw::term_t`)

Terms are the fundamental message format for client-server communication:

```cpp
// C++ side  
class term_t {
    unsigned type();            // Term type
    unsigned arity();           // Number of children
    term_t arg(unsigned);       // Access children
    void add_arg(int, term_t);  // Build structures
    std::string render();       // Serialize to text
    // ... binary serialization
};
```

**Python Constructors (from PIP analysis)**:
1. `term()` - Empty constructor ✅ **Works**
2. `term(const data &)` - From data object ❌ **BROKEN in Python 3**
3. `term(unsigned)` - Type constructor ✅ **Works**  
4. `term(const char *, unsigned)` - String + type ✅ **Works** (uses `PyUnicode_AsUTF8`)
5. `term(const term &)` - Copy constructor ✅ **Works**

### 3. String Encoding Protocol

**Python 2.7 (Original)**:
```python
# Python 2 strings are bytes by default
string_data = piw.makestring("user 2", 0)      # Passes bytes
term = piw.term(string_data)                    # Works
```

**Python 3.14 (Current)**:
```python  
# Python 3 strings are Unicode by default
string_data = piw.makestring("user 2", 0)      # Converts Unicode → UTF-8
term = piw.term(string_data)                    # BROKEN: binding issue

# Workaround preserves protocol:
term = data_to_term(string_data)                # Extracts value, uses working constructor
```

## Migration Strategy: Surgical Workaround

Our approach preserves the binary protocol while working around the broken binding:

```python
def data_to_term(data_obj):
    """Convert piw data objects to terms - workaround for Python 3 binding issue"""
    if sys.version_info[0] >= 3:
        # Python 3: Extract value and use working constructor
        data_type = data_obj.data_type()
        
        if data_obj.is_string():
            return piw.term(data_obj.as_string(), data_type)
        elif data_obj.is_bool():
            bool_val = data_obj.as_bool()
            return piw.term('y' if bool_val else 'n', 7)  # Boolean protocol
        # ... handle other types
    else:
        # Python 2: Use original constructor
        return piw.term(data_obj)
```

**Key Insight**: We still use `makestring()`/`makebool()` for type safety and encoding, but bypass the broken `term(data)` constructor.

## Cross-Version Compatibility Testing

### Test Scenarios

1. **Client-Server Protocol Stability**
   ```bash
   # Test Python 3.14 client → Python 2.7 server
   python3.14 bls → eigend-python27
   
   # Test Python 2.7 client → Python 3.14 server  
   python2.7 bls → eigend-python314
   ```

2. **Cross-Architecture Support**
   ```bash
   # Test ARM client → x86_64 server
   arm64-python3.14 bls → x86_64-eigend
   ```

3. **Setup File Compatibility**
   ```bash
   # Setup files created by Python 2.7 should load in Python 3.14
   # and vice versa
   ```

### Binary Protocol Validation

Our tests verify:

1. **Data Type Consistency**
   - String data objects always return `data_type() == 2`
   - Boolean data objects always return `data_type() == 6`

2. **Term Structure Compatibility**
   - Menu term structures maintain same hierarchy
   - Term rendering produces identical output

3. **Unicode Handling**
   - Unicode strings properly convert to UTF-8 for wire protocol
   - No bytes/string mixing in protocol messages

## Implementation Files

### Core Protocol Implementation
- `tools/pip_cmd/template` - PIP binding generation (uses `PyUnicode_AsUTF8`)
- `piw/piw.pip` - Protocol interface definitions
- `pisession/agentd.py` - Our `data_to_term()` workaround

### Test Coverage
- `tests/unit/test_term_constructors.py` - Individual constructor validation
- `tests/unit/test_binary_protocol_compatibility.py` - Protocol stability tests

## Critical Insight: Why This Approach Works

The PIP binding system was **partially** updated for Python 3:

1. **String Input** (`fpcvt_str`): ✅ Uses `PyUnicode_AsUTF8AndSize()` correctly
2. **Data Conversion** (`fpcvt_data`): ❌ Dispatcher unwrap broken
3. **Type System**: ✅ Type identifiers unchanged
4. **Serialization**: ✅ Binary format unchanged

Our workaround leverages the working parts (string input, type system) while avoiding the broken data conversion.

## Future Considerations

### Complete Fix Options

1. **Fix PIP Bindings**: Update `fpcvt_data` dispatcher to handle Python 3 properly
2. **Replace PIP System**: Migrate to modern binding system (Pybind11, etc.)
3. **Protocol Version**: Add protocol version negotiation

### Compatibility Matrix

| Component | Python 2.7 | Python 3.14 | Status |
|-----------|-------------|--------------|---------|
| `makestring()` | ✅ | ✅ | Compatible |
| `makebool()` | ✅ | ✅ | Compatible |
| `term(data)` | ✅ | ❌ | **Workaround needed** |
| `term(string, type)` | ✅ | ✅ | Compatible |
| Menu structures | ✅ | ✅ | Compatible with workaround |
| RPC messages | ✅ | ✅ | Compatible |

## Summary

Our migration preserves binary protocol compatibility by:

1. **Maintaining data wrappers** - Still use `makestring()`/`makebool()` for type safety
2. **Working around broken binding** - Use `data_to_term()` instead of `term(data)`  
3. **Preserving encoding** - Unicode strings correctly convert to UTF-8
4. **Maintaining term structures** - Same hierarchy and types

This ensures Python 3.14 clients can communicate with Python 2.7 servers and vice versa, critical for gradual migration and cross-platform deployment.