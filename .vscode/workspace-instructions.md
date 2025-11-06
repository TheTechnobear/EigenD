# EigenD TDD Workflow Instructions

## Quick Start
- **Test Command**: `./run_tests.sh --level <foundation|core|data|plugins|applications|integration|all>`
- **Current Status**: Python 3.14 migration - 36/43 tests passing across all layers
- **Next Focus**: Complete remaining plugin/integration tests, address PIW string segfault

## TDD Approach
1. **Test First**: Always run tests before making changes
2. **Fix Current Level**: Don't proceed until current test level passes
3. **Systematic Progression**: Foundation → Core → Data → Plugins → Applications → Integration
4. **Use Existing Tests**: Extend existing test files rather than creating new ones

## Test Structure (43 tests)
```
tests/unit/
├── test_00_foundation.py    # Environment, imports (12 tests)
├── test_01_core_piw.py      # PIW engine, sessions (14 tests) 
├── test_02_data_layer.py    # Serialization, encoding (6 tests)
├── test_03_plugins.py       # Plugin system (1 test)
├── test_04_applications.py  # CLI tools, backend (8 tests)
└── test_05_integration.py   # End-to-end (2 tests)
```

## Key Commands
- `./run_tests.sh --level foundation` - Basic environment check
- `./run_tests.sh --level all --verbose` - Full suite with details
- `./run_tests.sh --html` - Generate HTML reports

## Current Issues
- PIW string creation segfault (mitigated with error handling)
- 2 integration tests require full EigenD environment

## Recent Achievements
- Fixed critical PIW is_array() bug affecting all functionality
- Python 2→3 range concatenation fixes in command line tools
- Comprehensive session management improvements
- All major EigenD layers validated for Python 3.14

## Next Actions
1. Complete plugin layer testing
2. Run full migration validation suite
3. Address remaining segfault in string creation