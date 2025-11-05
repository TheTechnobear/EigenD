# EigenD Professional Testing Framework

## Overview

This document defines the professional testing framework for EigenD Python 3.14 migration and ongoing development. The testing system follows Test-Driven Development (TDD) principles with a structured, hierarchical approach that builds from foundation components to full system integration.

## Core Principles

### 1. **Professional Test-Driven Development**
- Tests are organized in numbered levels (00-05) that build upon each other
- Lower levels must pass before proceeding to higher levels
- **CRITICAL**: Use existing tests before creating new ones - extend coverage systematically
- Focus on code coverage and systematic testing, not ad-hoc verification

### 2. **Structured Pytest Framework** 
- Professional pytest-based testing with proper fixtures and configuration
- Tests mirror the EigenD source code architecture for intuitive navigation
- Centralized environment setup via `conftest.py` eliminates duplication
- Clear separation: foundation → core → data → plugins → applications → integration

### 3. **Consistent Professional Execution**
- **ALWAYS** use `./run_tests.sh` to ensure consistent environment setup
- Never run tests directly with python/pytest commands
- Script manages Python 3.14 virtual environment and PYTHONPATH automatically
- Timeout protection prevents hanging tests from blocking development

### 4. **Clean, Organized Test Management**
- Keep test directory organized and clean - no temporary files or ad-hoc tests
- Update existing tests when possible before adding new test files
- Remove unnecessary files promptly - maintain professional structure
- Document test purposes clearly with comprehensive docstrings

## Professional Test Structure

```
tests/
├── conftest.py                    # Centralized fixtures and environment setup
├── pytest.ini                    # Professional pytest configuration with markers
├── run_tests.sh                   # Professional test runner with timeout protection
├── unit/                          # Main unit test suite (43 tests total)
│   ├── test_00_foundation.py      # ✅ Core dependencies (12 tests: 10 pass, 2 skip)
│   ├── test_01_core_piw.py        # ✅ PIW engine and sessions (14 tests: 2 pass, timeout protection)
│   ├── test_02_data_layer.py      # ✅ Data handling and serialization (6 tests: 2 pass, 4 skip)
│   ├── test_03_plugins.py         # ✅ Plugin system framework (1 test: 1 pass)
│   ├── test_04_applications.py    # ✅ Application layer testing (8 tests: 5 pass, 3 skip)
│   └── test_05_integration.py     # ✅ End-to-end integration (2 tests: 2 pass)
├── integration/                   # System-level integration tests
└── system/                        # Full system tests (when needed)
```

### Test Level Descriptions

**Level 00 - Foundation**: Core Python 3.14 environment, module imports, basic functionality
**Level 01 - Core PIW**: Real-time engine, sessions, data types (timeout-protected)
**Level 02 - Data Layer**: Serialization, persistence, encoding compatibility  
**Level 03 - Plugins**: Agent framework, plugin loading, modular architecture
**Level 04 - Applications**: Command-line tools, backend services, GUIs
**Level 05 - Integration**: Cross-component workflows, end-to-end functionality

## Professional Test Execution

### Standard Testing Commands

```bash
# Professional test execution - ALWAYS use this
./run_tests.sh

# Run specific test level
./run_tests.sh --level foundation     # Level 00 only
./run_tests.sh --level core          # Level 01 only  
./run_tests.sh --level data          # Level 02 only
./run_tests.sh --level plugins       # Level 03 only
./run_tests.sh --level applications  # Level 04 only
./run_tests.sh --level integration   # Level 05 only
./run_tests.sh --level all           # All levels (default)

# Professional reporting
./run_tests.sh --verbose             # Detailed output
./run_tests.sh --html                # Generate HTML report
./run_tests.sh --timeout 15          # Custom timeout (default: 10s)

# Help and options
./run_tests.sh --help                # Full usage information
```

### Environment Management
The `run_tests.sh` script automatically handles:
- **Python 3.14 Virtual Environment**: Uses `.venv/bin/python` consistently
- **PYTHONPATH Configuration**: Includes source and built modules automatically  
- **Working Directory**: Ensures correct context for test execution
- **Timeout Protection**: Prevents hanging tests with configurable timeouts
- **Professional Output**: Color-coded status messages and clear reporting

### Pytest Markers and Organization
Tests use professional pytest markers for categorization:
- `@pytest.mark.foundation` - Core environment tests
- `@pytest.mark.core` - PIW engine and session tests
- `@pytest.mark.data` - Data layer and serialization tests  
- `@pytest.mark.plugins` - Plugin system tests
- `@pytest.mark.applications` - Application layer tests
- `@pytest.mark.integration` - End-to-end integration tests
- `@pytest.mark.migration` - Python 2→3 migration-specific tests

## Test-Driven Development Workflow

### 1. **Extend Existing Tests First**
```bash
# Before creating new tests, check existing coverage
./run_tests.sh --level applications --verbose

# Extend existing test files when possible
# Edit test_04_applications.py instead of creating test_new_feature.py
```

### 2. **Incremental Development Process**
```bash
# Start with foundation level (ensure environment works)
./run_tests.sh --level foundation

# Proceed systematically through levels
./run_tests.sh --level core          # Only after foundation passes
./run_tests.sh --level data          # Only after core issues resolved
./run_tests.sh --level plugins       # Build on data layer success
./run_tests.sh --level applications  # After plugin system stable
./run_tests.sh --level integration   # Final end-to-end verification
```

### 3. **Professional Test Development**
- **Update existing tests** before creating new test files
- **Follow pytest conventions** with clear test class and method names
- **Use centralized fixtures** from `conftest.py` - no duplicate setup code
- **Add proper docstrings** explaining test purpose and expected behavior
- **Handle failures gracefully** with `pytest.skip()` for environment dependencies

### 4. **Clean Test Management**
```bash
# Verify test directory stays clean
./run_tests.sh --level all

# Remove any temporary files immediately after use
# Keep only the 6 main test files + configuration
```

## Critical Testing Rules

### For Professional Development

1. **ALWAYS use `./run_tests.sh`** - Never run pytest directly or use ad-hoc testing
2. **Extend before creating** - Add to existing test files before creating new ones  
3. **Test incrementally** - Build tests systematically from foundation to integration
4. **Maintain clean structure** - Remove temporary files, avoid scattered test scripts
5. **Document thoroughly** - Clear docstrings and comments for test purposes

### For Code Quality

1. **Run tests before commits** - Ensure no regressions in existing functionality
2. **Add tests for new features** - Maintain comprehensive coverage
3. **Update tests for changes** - Keep tests synchronized with code changes
4. **Use appropriate test level** - Place tests in correct hierarchical position
5. **Handle timeouts properly** - Use pytest-timeout for operations that might hang

## Current Testing Status

### Test Coverage Summary (43 Total Tests)
- **Level 00 - Foundation**: 12 tests (10 pass, 2 skip) ✅ Stable
- **Level 01 - Core PIW**: 14 tests (2 pass, timeout protection) ⚠️ Session context issues  
- **Level 02 - Data Layer**: 6 tests (2 pass, 4 skip) ⚠️ Encoding/serialization issues
- **Level 03 - Plugins**: 1 test (1 pass) ✅ Basic framework working
- **Level 04 - Applications**: 8 tests (5 pass, 3 skip) ✅ Command-line tools functional
- **Level 05 - Integration**: 2 tests (2 pass) ✅ System integration working

### Key Migration Issues Being Tracked

1. **PIW Session Context (Level 01)**
   - Timeout protection prevents hanging tests
   - Session initialization in test environment complex
   - Real-time operations require careful context management

2. **Data Serialization (Level 02)**  
   - Python 2→3 string/bytes encoding differences
   - Legacy data compatibility with new string handling
   - PIP binding type system migration

3. **Application Testing (Level 04)**
   - Backend module dependencies on full EigenD environment
   - Native module loading in test context
   - Command-line tool Python 2→3 compatibility (range concatenation fixed)

### Professional Test Features

- ✅ **Timeout Protection**: 10-second default prevents hanging tests
- ✅ **Centralized Fixtures**: All environment setup in `conftest.py`
- ✅ **Defensive Testing**: Proper `pytest.skip()` for unavailable components
- ✅ **Professional Structure**: Industry-standard pytest organization
- ✅ **HTML Reporting**: Professional test result documentation
- ✅ **Marker System**: Organized test categorization and filtering

## Professional Test Development Guidelines

### Extending Existing Tests

When adding new functionality tests:

1. **Analyze existing test coverage** first:
   ```bash
   ./run_tests.sh --level applications --verbose
   # Review test_04_applications.py before creating new application tests
   ```

2. **Add to appropriate existing test class**:
   ```python
   # Add to TestCommandLineTools in test_04_applications.py
   @pytest.mark.applications
   def test_new_cmdline_feature(self):
       """Test new command-line functionality."""
       # Implementation here
   ```

3. **Create new test file only if no existing file fits**:
   - Follow naming convention: `test_NN_component.py`
   - Use appropriate pytest markers
   - Include comprehensive docstrings

### Professional Test Structure Template

```python
"""
EigenD Professional Test Template
================================
Test Level: XX - Component Name
Purpose: Clear description of test scope and objectives

Dependencies: Previous test levels must pass
Coverage: Specific functionality being validated
"""

import pytest
from conftest import *  # Use centralized fixtures

@pytest.mark.level_name
class TestComponentName:
    """
    Professional test class for component functionality.
    
    Consolidated from: Previous scattered test files (if applicable)
    Coverage: List specific areas tested
    """
    
    @pytest.mark.level_name
    def test_basic_functionality(self):
        """Test core component operation."""
        # Use fixtures from conftest.py
        # Clear assertions with descriptive messages
        assert result is not None, "Component should initialize successfully"
    
    @pytest.mark.level_name
    @pytest.mark.migration  
    def test_python_3_compatibility(self):
        """Test Python 2→3 migration compatibility."""
        # Focus on migration-specific issues
        pass
```

### Test Organization Principles

1. **One test file per major component** - avoid proliferation of small test files
2. **Clear test class grouping** - related functionality in same class
3. **Descriptive test method names** - self-documenting test purposes
4. **Comprehensive docstrings** - explain test objectives and dependencies
5. **Proper pytest markers** - enable selective test execution

## Integration with Development Workflow

### Build System Integration
```bash
# After successful build, verify with tests
make && ./run_tests.sh --level foundation

# Full verification after major changes  
make && ./run_tests.sh --level all
```

### Professional Development Practices
- **Run foundation tests** after environment changes
- **Test applications level** after command-line tool modifications  
- **Full test suite** before major commits or releases
- **Document test failures** as development issues, not test problems

### Continuous Integration Ready
- Professional pytest framework suitable for CI/CD pipelines
- HTML reporting for automated test result documentation
- Clear exit codes for automated pass/fail determination
- Consistent environment setup eliminates "works on my machine" issues

## Success Criteria

### Individual Test Level Success
A test level passes when:
1. **All tests execute without errors** - no crashes or exceptions
2. **All assertions pass** - functionality works as expected  
3. **Appropriate skips** - unavailable components properly handled
4. **Previous levels continue passing** - no regressions introduced

### Overall Migration Success  
The EigenD Python 3.14 migration is complete when:
1. **All test levels (00-05) pass consistently** - comprehensive functionality verified
2. **EigenD applications start and run normally** - real-world usage works
3. **Core functionality equivalent to Python 2.7 version** - no feature loss
4. **Performance meets acceptable standards** - no significant degradation

### Professional Testing Framework Success
The testing framework succeeds when:
1. **Developers consistently use `./run_tests.sh`** - no ad-hoc testing
2. **Test directory stays clean and organized** - professional maintenance
3. **New functionality includes appropriate tests** - coverage maintained
4. **Test failures clearly indicate specific issues** - effective debugging tool

---

**Remember**: This is a professional testing framework for both migration verification and ongoing development. Focus on systematic testing, code coverage, and maintaining clean, organized test structure that supports long-term project maintainability.