# EigenD Terms and Predicates System

**Purpose:** Explain how EigenD uses Prolog-style terms for structured data representation  
**Status:** Working correctly in Python 3.14  
**Context:** Terms are the primary serialization and communication format in EigenD

## Overview

### What are Terms?

EigenD uses **Prolog-style terms** as its primary data representation format for:
- Agent state serialization (saving/loading setups)
- Inter-agent communication (RPC messages)
- Configuration data structures
- Connection metadata

**Two Types of Terms:**

1. **Data Terms** (Atoms): Hold actual values (strings, numbers, timestamps)
2. **Predicate Terms** (Compound Terms): Hold structured data with named functors and arguments

### Term Hierarchy

```
piw::term_t (base class)
├── term_atom_t      → Data terms (wraps piw::data_t)
└── term_pred_t      → Predicate terms (functor + arguments)
```

**Key Characteristic:** Terms are immutable once created - modifications create new terms.

---

## Data Terms

### Purpose
Data terms wrap `piw::data_t` values to represent atomic data like strings, numbers, and binary blobs.

### C++ Interface

```cpp
// From piw/src/piw_state.cpp
term_t::term_t(const piw::data_t &data) 
    : body_(new term_atom_t(data))
{
}
```

### Python Usage

```python
import piw

# Create data term from string
label_data = piw.makestring("My Setup", 0)  # timestamp=0
label_term = piw.term(label_data)

# Create data term from number
count_data = piw.makefloat_bounded(1, 0, 0, 10, 0, 0)
count_term = piw.term(count_data)

# Access underlying data
value = label_term.value()  # Returns piw::data_t
assert value.is_string()
print(value.as_string())  # "My Setup"
```

### Common Patterns

**String terms:**
```python
# Correct pattern for string terms
def make_string_term(text):
    data = piw.makestring(text, 0)
    return piw.term(data)

# Usage
name_term = make_string_term("audio unit rig 1")
path_term = make_string_term("/path/to/file")
```

**Numeric terms:**
```python
# Integer
int_data = piw.makelong(42, 0)
int_term = piw.term(int_data)

# Float
float_data = piw.makefloat(3.14159, 0)
float_term = piw.term(float_data)
```

### Data Term Properties

- **Has value:** `term.value()` returns valid `piw::data_t`
- **No children:** Data terms are leaf nodes
- **Immutable:** Cannot modify after creation
- **Type checking:** Use `value().is_string()`, `value().is_long()`, etc.

---

## Predicate Terms

### Purpose
Predicate terms represent structured data with a **functor** (name) and fixed number of **arguments**.

Think of them like Prolog terms or function calls: `functor(arg0, arg1, arg2, ...)`

### C++ Interface

```cpp
// From piw/src/piw_state.cpp
term_t::term_t(const std::string &pred, unsigned arity) 
    : body_(new term_pred_t(pred, arity))
{
}

class term_pred_t {
    std::string predicate_;  // Functor name
    term_t *args_;          // Array of arguments
    unsigned arity_;        // Number of arguments
};
```

### Python Usage

```python
import piw

# Create predicate term with functor 'n' and 7 arguments
menu_term = piw.term('n', 7)

# Set arguments (must set all arity slots)
menu_term.set_arg(0, piw.term(piw.makestring("Setup Name", 0)))
menu_term.set_arg(1, piw.term(piw.makestring("path/to/file", 0)))
menu_term.set_arg(2, piw.term(0))  # Empty term for unused slot
# ... set remaining args ...

# Access predicate metadata
predicate = menu_term.predicate()  # Returns "n"
arity = menu_term.arity()          # Returns 7
arg0 = menu_term.arg(0)            # Get first argument
```

### Common Predicate Examples

**Menu entry predicate (`n`):**
```python
def create_menu_entry(label, filepath, name, slot, ordinal):
    """Creates a menu entry term with functor 'n' and 7 arguments."""
    t = piw.term('n', 7)
    t.set_arg(0, make_string_term(label))      # Display label
    t.set_arg(1, make_string_term(filepath))   # File path
    t.set_arg(2, make_string_term(name))       # Setup name
    t.set_arg(3, make_string_term(slot))       # Slot identifier
    t.set_arg(4, make_string_term(ordinal))    # Sort order
    t.set_arg(5, piw.term(0))                  # Reserved
    t.set_arg(6, piw.term(0))                  # Reserved
    return t
```

**Connection predicate (`conn`):**
```python
def create_connection(index, flags, target_id, src_path, dst_path):
    """Creates a connection term with functor 'conn' and 5 arguments."""
    t = piw.term('conn', 5)
    t.set_arg(0, piw.term(piw.makelong(index, 0)))
    t.set_arg(1, piw.term(piw.makelong(flags, 0)))
    t.set_arg(2, make_string_term(target_id))
    t.set_arg(3, path_list_to_term(src_path))
    t.set_arg(4, path_list_to_term(dst_path))
    return t
```

**List predicate (arity 0 for empty, or nested):**
```python
def create_term_list(items):
    """Creates a list of terms."""
    if not items:
        return piw.term(0)  # Empty term
    
    # Build nested list structure
    result = piw.term(0)
    for item in items:
        result.add_arg(-1, item)  # Add to end
    return result
```

### Predicate Term Properties

- **No value:** `term.value()` returns null/empty `piw::data_t`
- **Has functor:** `term.predicate()` returns functor string
- **Has arity:** `term.arity()` returns argument count
- **Has children:** Access via `term.arg(index)`
- **Immutable:** Set all args during construction

---

## Term Construction Patterns

### From Python to C++

**Python code:**
```python
# Data term
data = piw.makestring("hello", 0)
term = piw.term(data)
```

**Generated binding:**
```cpp
// In piw_native_python.cpp
term_wrapper_(PyObject *o, PyInterpreterState *i, const data & a0)
    : term_type_(a0), object(o), _interp(i)
{
}
```

**C++ constructor:**
```cpp
// In piw_state.cpp
term_t::term_t(const piw::data_t &data)
    : body_(new term_atom_t(data))
{
}
```

### Binding Layer

The PIP template generates Python bindings that map to C++ constructors:

```python
# Python interface (from piw.pip)
class term:
    def __init__(self):                    # term_t()
    def __init__(self, data):              # term_t(const data_t&)
    def __init__(self, arity):             # term_t(unsigned)
    def __init__(self, pred, arity):       # term_t(const char*, unsigned)
    def __init__(self, other):             # term_t(const term_t&)
```

**String Handling:**
- Python 2.7: Used `PyString_AsString()` for `const char*` parameters
- Python 3.x: Uses `PyUnicode_AsUTF8()` for `const char*` parameters
- Both immediately copy to `std::string` in C++ - no dangling pointer issues

---

## Practical Examples

### Example 1: Setup Menu Structure

**Goal:** Create a menu with multiple setup entries

```python
def create_setup_menu(setups):
    """
    Creates a menu term structure.
    
    Args:
        setups: dict of {name: (label, filepath, slot, ordinal)}
    
    Returns:
        piw.term with menu structure
    """
    # Create children list
    children = piw.term(0)  # Start with empty term
    
    for name, (label, filepath, slot, ordinal) in setups.items():
        # Create menu entry predicate
        entry = piw.term('n', 7)
        entry.set_arg(0, make_string_term(label))
        entry.set_arg(1, make_string_term(filepath))
        entry.set_arg(2, make_string_term(name))
        entry.set_arg(3, make_string_term(slot))
        entry.set_arg(4, make_string_term(ordinal))
        entry.set_arg(5, piw.term(0))
        entry.set_arg(6, piw.term(0))
        
        # Add to children list
        children.add_arg(-1, entry)
    
    return children
```

### Example 2: Agent State Serialization

**Goal:** Serialize agent connections for database storage

```python
def serialize_connections(connections):
    """
    Serializes connection list to term format.
    
    Args:
        connections: list of (target_id, src_path, dst_path) tuples
    
    Returns:
        piw.term containing all connections
    """
    conn_list = piw.term(0)
    
    for index, (target_id, src_path, dst_path) in enumerate(connections):
        # Create connection predicate
        conn_term = piw.term('conn', 5)
        conn_term.set_arg(0, piw.term(piw.makelong(index, 0)))
        conn_term.set_arg(1, piw.term(piw.makelong(0, 0)))  # flags
        conn_term.set_arg(2, make_string_term(target_id))
        conn_term.set_arg(3, path_to_term(src_path))
        conn_term.set_arg(4, path_to_term(dst_path))
        
        conn_list.add_arg(-1, conn_term)
    
    return conn_list

def path_to_term(path):
    """Convert integer list path to term list."""
    path_term = piw.term(0)
    for cookie in path:
        path_term.add_arg(-1, piw.term(piw.makelong(cookie, 0)))
    return path_term
```

### Example 3: Parsing Terms

**Goal:** Extract data from received term structure

```python
def parse_menu_entry(entry_term):
    """
    Parses a menu entry term.
    
    Args:
        entry_term: piw.term with functor 'n' and arity 7
    
    Returns:
        dict with parsed fields
    """
    assert entry_term.predicate() == 'n'
    assert entry_term.arity() == 7
    
    return {
        'label': entry_term.arg(0).value().as_string(),
        'filepath': entry_term.arg(1).value().as_string(),
        'name': entry_term.arg(2).value().as_string(),
        'slot': entry_term.arg(3).value().as_string(),
        'ordinal': entry_term.arg(4).value().as_string(),
    }

def parse_connection(conn_term):
    """
    Parses a connection term.
    
    Args:
        conn_term: piw.term with functor 'conn' and arity 5
    
    Returns:
        dict with connection details
    """
    assert conn_term.predicate() == 'conn'
    assert conn_term.arity() == 5
    
    return {
        'index': conn_term.arg(0).value().as_long(),
        'flags': conn_term.arg(1).value().as_long(),
        'target_id': conn_term.arg(2).value().as_string(),
        'src_path': term_to_path(conn_term.arg(3)),
        'dst_path': term_to_path(conn_term.arg(4)),
    }

def term_to_path(path_term):
    """Convert term list to integer list."""
    path = []
    for i in range(path_term.arity()):
        path.append(path_term.arg(i).value().as_long())
    return path
```

---

## Term Manipulation

### Adding Arguments Dynamically

```python
# Create empty term
term = piw.term(0)

# Add arguments to end
term.add_arg(-1, make_string_term("first"))
term.add_arg(-1, make_string_term("second"))
term.add_arg(-1, make_string_term("third"))

# Access by index
assert term.arity() == 3
assert term.arg(0).value().as_string() == "first"
assert term.arg(2).value().as_string() == "third"
```

### Nested Structures

```python
# Create nested predicate structure
outer = piw.term('outer', 2)

# First arg: string
outer.set_arg(0, make_string_term("label"))

# Second arg: nested predicate
inner = piw.term('inner', 3)
inner.set_arg(0, piw.term(piw.makelong(1, 0)))
inner.set_arg(1, piw.term(piw.makelong(2, 0)))
inner.set_arg(2, piw.term(piw.makelong(3, 0)))

outer.set_arg(1, inner)

# Access nested data
assert outer.arg(1).predicate() == 'inner'
assert outer.arg(1).arg(0).value().as_long() == 1
```

---

## Implementation Details

### C++ Term Classes

**Location:** `piw/src/piw_state.cpp`

```cpp
class term_atom_t : public term_body_t {
    piw::data_t data_;
public:
    term_atom_t(const piw::data_t &data) : data_(data) {}
    const piw::data_t &value() const { return data_; }
    bool valid() const { return data_.is_null() == false; }
};

class term_pred_t : public term_body_t {
    std::string predicate_;
    term_t *args_;
    unsigned arity_;
public:
    term_pred_t(const std::string &pred, unsigned arity)
        : predicate_(pred), arity_(arity)
    {
        args_ = new term_t[arity];
    }
    
    const std::string &predicate() const { return predicate_; }
    unsigned arity() const { return arity_; }
    const term_t &arg(unsigned i) const { return args_[i]; }
    void set_arg(unsigned i, const term_t &t) { args_[i] = t; }
};
```

### Python Binding Generation

**Template:** `tools/pip_cmd/template`

The PIP template generates binding code that handles:
- Constructor overloading (4 constructors for `piw.term`)
- Type conversion (Python str → C++ `const char*`)
- Memory management (reference counting)
- Interpreter state tracking (multi-interpreter support)

**String Conversion (Python 3.x):**
```cpp
int fpcvt_str(PyObject *o, void *a)
{
    const char *s = PyUnicode_AsUTF8(o);
    if(s) { 
        *((const char **)a) = s; 
        return 1; 
    }
    return 0;
}
```

The pointer returned by `PyUnicode_AsUTF8()` is valid for the lifetime of the Python string object. The C++ constructor immediately copies it to `std::string`, so there are no dangling pointer issues.

---

## Common Functors in EigenD

| Functor | Arity | Purpose | Used In |
|---------|-------|---------|---------|
| `n` | 7 | Menu entry | Setup menus, agentd |
| `conn` | 5 | Connection | Agent state, connections |
| `prop` | 2 | Property | Agent properties |
| `list` | Variable | List container | Generic lists |
| `dict` | Variable | Dictionary | Key-value stores |
| `agent` | Variable | Agent state | Setup serialization |

### Functor Conventions

- **Single letter:** System-level structures (`n` for menu)
- **Short name:** Common operations (`conn`, `prop`)
- **Descriptive:** Plugin-specific (`audio_config`, `midi_event`)

---

## Best Practices

### 1. Always Use Correct Constructor

```python
# ✅ CORRECT: Data term from string
term = piw.term(piw.makestring("text", 0))

# ❌ WRONG: Predicate term (creates functor="text", arity=0)
term = piw.term("text", 0)
```

### 2. Set All Arguments

```python
# ✅ CORRECT: Set all arity slots
term = piw.term('pred', 3)
term.set_arg(0, arg0)
term.set_arg(1, arg1)
term.set_arg(2, arg2)

# ❌ WRONG: Leaving arguments unset leads to null access
term = piw.term('pred', 3)
term.set_arg(0, arg0)
# args 1 and 2 are uninitialized!
```

### 3. Check Types Before Access

```python
# ✅ CORRECT: Type checking
value = term.value()
if value.is_string():
    text = value.as_string()
elif value.is_long():
    number = value.as_long()

# ❌ WRONG: Assuming type
text = term.value().as_string()  # Crashes if not string!
```

### 4. Use Helper Functions

```python
# Create reusable helpers
def make_string_term(text):
    """Safely create string term."""
    return piw.term(piw.makestring(text, 0))

def make_int_term(value):
    """Safely create integer term."""
    return piw.term(piw.makelong(value, 0))

# Use throughout codebase
label_term = make_string_term("My Label")
count_term = make_int_term(42)
```

---

## References

**Source Files:**
- `piw/piw.pip` - Python interface definitions
- `piw/src/piw_state.cpp` - C++ term implementation
- `tools/pip_cmd/template` - Binding generator template
- `pisession/agentd.py` - Menu term creation example
- `pi/atom.py` - Connection term handling

**Related Documentation:**
- `dev_docs/setup_loading.md` - How terms are used in setup serialization
- `dev_docs/pip_template.md` - PIP binding system details