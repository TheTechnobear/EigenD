# EigenD Binary Protocol Layer
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

**Python Constructors**:
1. `term()` - Empty constructor
2. `term(unsigned)` - Type constructor  
3. `term(const char *, unsigned)` - String + type (uses `PyUnicode_AsUTF8`)
4. `term(const term &)` - Copy constructor

### 3. String Encoding Protocol

**Current Implementation**:
```python  
# Python 3 strings are Unicode by default
string_data = piw.makestring("user 2", 0)      # Converts Unicode → UTF-8
term = piw.term(string_data.as_string(), 2)    # Uses working constructor
```

## Binary Protocol Implementation

### Test Scenarios

1. **Client-Server Protocol Stability**
   ```bash
   # Test Python 3.14 client → Python 3.14 server
   python3.14 bls → eigend
   ```

2. **Cross-Architecture Support**
   ```bash
   # Test ARM client → x86_64 server
   arm64-python3.14 bls → x86_64-eigend
   ```

3. **Setup File Compatibility**
   ```bash
   # Setup files maintain compatibility across Python 3 versions
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

### Test Coverage
- `tests/unit/test_term_constructors.py` - Individual constructor validation
- `tests/unit/test_binary_protocol_compatibility.py` - Protocol stability tests

## Implementation Details

The PIP binding system provides proper Unicode handling:

1. **String Input** (`fpcvt_str`): Uses `PyUnicode_AsUTF8AndSize()` correctly
2. **Type System**: Type identifiers unchanged
3. **Serialization**: Binary format unchanged

## Future Considerations

### Potential Improvements

1. **Modernize Bindings**: Consider migrating to Pybind11 for better Python 3 support
2. **Protocol Versioning**: Add protocol version negotiation for future compatibility
3. **Performance Optimization**: Optimize serialization for high-throughput scenarios

### Component Status

| Component | Status | Notes |
|-----------|---------|--------|
| `makestring()` | ✅ Working | Unicode → UTF-8 conversion |
| `makebool()` | ✅ Working | Type-safe boolean creation |
| `term(string, type)` | ✅ Working | Primary constructor used |
| Menu structures | ✅ Working | Maintains hierarchy |
| RPC messages | ✅ Working | Protocol stable |

## Summary

The binary protocol provides stable communication between EigenD components:

1. **Type-safe data objects** - `makestring()`/`makebool()` ensure proper encoding
2. **Unicode support** - Strings correctly convert to UTF-8 for wire protocol
3. **Stable term structures** - Same hierarchy and types across versions
4. **Cross-architecture compatibility** - Works across different CPU architectures

This ensures reliable client-server communication and data serialization in Python 3.14.