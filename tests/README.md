# EigenD Testing Framework
# ======================

## Overview
Professional testing framework for EigenD Python 3.14 migration using pytest.

## Installation
```bash
cd /Users/kodiak/projects/EigenD
.venv/bin/pip install pytest pytest-xdist pytest-html pytest-cov
```

## Framework Structure

### Test Organization
```
tests/
├── conftest.py              # Shared fixtures and configuration
├── pytest.ini              # Pytest configuration
├── unit/                    # Unit tests (isolated functionality)
│   ├── test_00_foundation.py
│   ├── test_01_core_piw.py
│   ├── test_02_data_layer.py
│   ├── test_03_plugins.py
│   ├── test_04_applications.py
│   └── test_05_integration.py
├── integration/             # Integration tests (cross-component)
├── performance/             # Performance regression tests
└── cpp/                     # C++ unit tests (Google Test)
```

### Naming Conventions
- **Test files**: `test_<level>_<component>.py`
- **Test classes**: `Test<Component><Functionality>`
- **Test methods**: `test_<functionality>_<scenario>`
- **Fixtures**: `<component>_<resource>` (e.g., `piw_session`, `test_database`)

### Test Categories (pytest markers)
- `@pytest.mark.foundation` - Core dependency tests
- `@pytest.mark.core` - Core library tests  
- `@pytest.mark.data` - Data layer tests
- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.cpp` - C++ integration tests

## Running Tests
```bash
# Run all tests
./run_tests.sh

# Run specific level
./run_tests.sh --level foundation

# Run specific markers
./run_tests.sh --markers core,data

# Generate HTML report
./run_tests.sh --html-report

# Run with coverage
./run_tests.sh --coverage
```

## Test Development Guidelines

### 1. Test Structure
Each test file should have:
- Clear docstring describing test scope
- Consistent class organization
- Proper use of fixtures
- Meaningful assertions with messages

### 2. Environment Setup
- NO manual sys.path manipulation in test files
- Use conftest.py fixtures for environment setup
- Shared test data in fixtures
- Automatic cleanup

### 3. Test Documentation
```python
class TestPiwDataCreation:
    """
    Tests PIW data object creation and type validation.
    
    Covers:
    - makestring(), makebool(), makelong() functions
    - Type code validation (0x02=STRING, 0x03=BOOL, 0x04=LONG)
    - Data serialization/deserialization
    - Python 3.14 migration issues: string encoding, type assertions
    
    Dependencies: PIW module import, session context
    """
```

### 4. Consistent Assertions
```python
# Good - descriptive failure messages
assert data.is_string(), f"Data with type_code {data.type()} should be string type"

# Bad - unclear failures  
assert data.is_string()
```

## Migration from Current Structure

1. **Convert debug scripts** → proper unit tests with assertions
2. **Consolidate similar tests** → single test class with multiple methods
3. **Extract common setup** → shared fixtures
4. **Add test metadata** → docstrings and markers
5. **Standardize naming** → consistent conventions