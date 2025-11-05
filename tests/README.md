# EigenD Python 3.14 Migration Test Suite

## Overview

This test suite ensures the Python 3.14 migration maintains compatibility and functionality across all components of EigenD. Tests are organized by scope and source code structure.

## Test Organization

### `/tests/unit/` - Unit Tests
Tests for individual modules and functions in isolation.

### `/tests/integration/` - Integration Tests  
Tests for interactions between components and subsystems.

### `/tests/system/` - System Tests
End-to-end tests with full EigenD daemon and hardware interaction.

## Test Structure

Each test directory mirrors the source code structure:
- `unit/pi/` - Tests for `pi/` module functionality
- `unit/app_eigend2/` - Tests for eigend daemon components
- `unit/app_cmdline/` - Tests for command-line tools
- `unit/pisession/` - Tests for session management
- `unit/piw/` - Tests for Pi Wire system
- `unit/tools/` - Tests for build tools and PIP system

## Prerequisites

### General
- Python 3.14 with EigenD built in `/tmp/`
- `DYLD_LIBRARY_PATH=/Users/kodiak/projects/EigenD/tmp/bin` (macOS)
- `PYTHONPATH=/Users/kodiak/projects/EigenD/tmp/modules`

### Hardware Tests
- Eigenharp hardware connected
- EigenD daemon not already running

### System Tests  
- EigenD daemon process management
- Network ports 55555+ available
- Audio/MIDI system access

## Running Tests

### Individual Test
```bash
cd /Users/kodiak/projects/EigenD
DYLD_LIBRARY_PATH=tmp/bin PYTHONPATH=tmp/modules python3 tests/unit/pi/test_resource.py
```

### Test Suite (planned)
```bash
cd /Users/kodiak/projects/EigenD
./run_tests.py --unit      # Unit tests only
./run_tests.py --integration # Integration tests only
./run_tests.py --all       # All tests
./run_tests.py --compare   # Compare Python 2.7 vs 3.14 outputs
```

## Test File Index

### Unit Tests

#### `/tests/unit/pi/`
| File | Description | Parameters | Expected Output | Prerequisites |
|------|-------------|------------|-----------------|---------------|
| `test_resource.py` | Tests resource management functions (get_logfile, rotate_logfile) | None | Creates log files, returns paths | Writable user directory |
| `test_agent.py` | Tests basic agent functionality and RPC system | None | Agent creation/destruction | Libraries loaded |
| `test_database.py` | Tests Belcanto database and lookup functions | None | Dictionary lookups succeed | None |

#### `/tests/unit/app_eigend2/`
| File | Description | Parameters | Expected Output | Prerequisites |
|------|-------------|------------|-----------------|---------------|
| `test_backend.py` | Tests backend module Python 2→3 compatibility | None | Backend creates, methods callable | Libraries loaded |
| `test_bugs_cli.py` | Tests bug reporting system | None | Bug logger functional | None |

#### `/tests/unit/app_cmdline/`
| File | Description | Parameters | Expected Output | Prerequisites |
|------|-------------|------------|-----------------|---------------|
| `test_cheat.py` | Tests cheatsheet range concatenation fix | None | Cheatsheet generates without errors | Belcanto database |
| `test_bls.py` | Tests bls agent listing tool | None | Agent list output | None |
| `test_rpc.py` | Tests RPC command execution | None | RPC calls succeed | None |

#### `/tests/unit/pisession/`
| File | Description | Parameters | Expected Output | Prerequisites |
|------|-------------|------------|-----------------|---------------|
| `test_agentd.py` | Tests agent management and cmp function fixes | None | Agent enumeration works | None |
| `test_session.py` | Tests session initialization | None | Session creates | None |

#### `/tests/unit/piw/`
| File | Description | Parameters | Expected Output | Prerequisites |
|------|-------------|------------|-----------------|---------------|
| `test_piw_native.py` | Tests Pi Wire native module loading | None | Module imports and initializes | Native libraries |

#### `/tests/unit/tools/`
| File | Description | Parameters | Expected Output | Prerequisites |
|------|-------------|------------|-----------------|---------------|
| `test_pip_system.py` | Tests PIP binding generation and Python 3 template | `.pip` file | Generated C++ code compiles | SCons, C++ compiler |

### Integration Tests

#### `/tests/integration/`
| File | Description | Parameters | Expected Output | Prerequisites |
|------|-------------|------------|-----------------|---------------|
| `test_daemon_startup.py` | Tests eigend startup sequence | Daemon args | Daemon starts without crashes | No other eigend running |
| `test_plugin_loading.py` | Tests plugin discovery and loading | Plugin names | Plugins load successfully | Built plugins |
| `test_command_tools.py` | Tests command-line tools end-to-end | Tool commands | Tools execute and return expected output | None |

### System Tests

#### `/tests/system/`
| File | Description | Parameters | Expected Output | Prerequisites |
|------|-------------|------------|-----------------|---------------|
| `test_hardware_detection.py` | Tests Eigenharp hardware detection | None | Hardware detected and initialized | Connected Eigenharp |
| `test_audio_pipeline.py` | Tests audio processing pipeline | Audio params | Audio flows without dropouts | Audio interface |
| `test_belcanto_execution.py` | Tests Belcanto command execution | Belcanto phrases | Commands execute correctly | Running eigend |
| `test_python27_compatibility.py` | Compares Python 2.7 vs 3.14 behavior | Test scenarios | Identical outputs | Both versions available |

## Test Utilities

### `/tests/utils/`
| File | Description |
|------|-------------|
| `test_runner.py` | Test execution framework |
| `comparison.py` | Python 2.7 vs 3.14 comparison utilities |
| `daemon_manager.py` | EigenD daemon start/stop/status management |
| `hardware_mock.py` | Mock hardware for testing without Eigenharp |

## Adding New Tests

1. **Choose appropriate directory** based on test scope
2. **Follow naming convention**: `test_<module_name>.py`
3. **Update this documentation** with test description
4. **Include error cases** and edge conditions
5. **Test both success and failure paths**
6. **Verify cleanup** of resources/processes

## Migration-Specific Test Focus

### Critical Areas
- **PIP binding system**: C++/Python interface compatibility
- **String handling**: bytes vs str, encoding issues  
- **Iterator behavior**: range(), map(), dict methods
- **Exception handling**: Python 2→3 syntax changes
- **Import system**: relative vs absolute imports
- **Comparison functions**: cmp() removal, sorting changes

### Regression Prevention
- **Command-line tools**: All tools produce identical output
- **Daemon startup**: No crashes during initialization
- **Plugin system**: All plugins load and initialize
- **Hardware interface**: Device detection and communication
- **Session management**: Save/load functionality

## Status

**Created:** 2025-11-05  
**Python 3.14 Migration:** In Progress  
**Test Coverage:** Initial framework setup  
**Hardware Testing:** Pending daemon fixes  

This test suite will be expanded as the migration progresses and issues are identified.