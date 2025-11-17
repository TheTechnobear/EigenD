# Test Creation Prompt

You are an expert testing assistant for the EigenD project. When given a test request in the format "/test <description>", follow these steps:

1. **Analyze the Request**: Understand what the test should verify. Identify the component, functionality, or scenario being tested.

2. **Determine Test Level**: Map the test to the appropriate level based on the Unit Test Structure:
   - **Foundation** (`test_00_foundation.py`): Python environment, module imports, basic setup
   - **Core** (`test_01_core_piw.py`): PIW engine, sessions, real-time operations
   - **Data** (`test_02_data_layer.py`): Serialization, encoding, data types
   - **Plugins** (`test_03_plugins.py`): Plugin system, agent framework, **plugin instantiation with PIW session context**
   - **Applications** (`test_04_applications.py`): Command-line tools, backend services
   - **Integration** (`test_05_integration.py`): Cross-plugin workflows, full application integration scenarios

   **Important**: Plugin instantiation tests should use the `piw_session` fixture and be placed in the **Plugins** level. The **Integration** level is for tests that involve multiple plugins working together or full application scenarios.

3. **Check Existing Tests**:
   - Search the `tests/unit/` directory for existing test files at the determined level.
   - Look for similar tests that could be extended rather than creating duplicates.
   - If a relevant test file exists, add to it; otherwise, create a new test function in the appropriate file.

4. **Create or Extend Test**:
   - Use the Test Addition Template:
     ```python
     @pytest.mark.<level>
     def test_<short_name>(<fixtures>):
         """Brief docstring: reproduces <issue> and asserts expected behavior."""
         # minimal reproducible example using fixtures
     ```
   - Ensure the test is minimal, reproducible, and uses appropriate fixtures from `conftest.py`.
   - Add necessary imports and setup.

5. **Run and Validate**: After creating the test, run it to ensure it passes or fails as expected. Use `runTests` tool if available.

6. **Report**: Provide a brief summary of what was done, any discoveries, and next steps.

**Response Format**:
- Done: <what was accomplished>
- Discovered: <any findings or issues>
- Next: <next actionable steps>

Keep the `tests/` directory clean and maintain proper test structure.

## Available Fixtures (from conftest.py)

### Environment Setup
- `setup_eigend_environment()`: Auto-configures paths, library paths, and environment variables
- `eigend_database_path()`: Path to test database file

### Session Management
- `piw_session`: Provides PIW session context with automatic cleanup handling
  - Use `piw_session['run'](test_function)` to execute code in session context
  - Handles timeouts and cleanup automatically in quick mode
- `eigend_agentd_session()`: Full agentd initialization with mock backend
  - Returns `{'agentd': ad, 'agent': agent, 'session': ctx, 'success': True/False}`

### Module Access
- `piw_modules()`: Returns dict with imported PIW modules (`piw`, `state`, `session`, `belcanto`)

### Data Types
- `type_codes()`: Valid PIW type code mappings
- `assert_piw_data_valid()`: Helper for PIW data assertions

## Testing Patterns

### Plugin Testing
Plugin instantiation tests should be placed in the **Plugins** level using the `piw_session` fixture for full application context. The `tmp/plugins` path is automatically available for all tests.

```python
@pytest.mark.plugins
@pytest.mark.timeout(15)
def test_plugin_instantiation_in_application_context(piw_session):
    """Test plugin instantiation in full application context."""
    def test_in_session(session_ctx):
        try:
            from Eigenlabs.plg_example import example_plg
            agent = example_plg.Agent('test_address', 1)
            return {
                'success': True,
                'agent': agent,
                'has_required_attributes': hasattr(agent, 'domain'),
                # Add plugin-specific checks
            }
        except ImportError as e:
            return {'success': False, 'error': f"Plugin not available: {e}"}
    
    results = piw_session['run'](test_in_session)
    
    if results is None:
        pytest.skip("Session timed out")
    
    if not results.get('success', False):
        pytest.skip(results.get('error', 'Unknown error'))
    
    assert results['has_required_attributes'], "Plugin should have required attributes"
    # Additional assertions
```

For basic infrastructure tests (imports, directory structure), use simpler patterns without session context.

### Integration Testing with Sessions
```python
@pytest.mark.integration
@pytest.mark.timeout(15)
def test_component_in_application_context(piw_session):
    """Test component in full application context."""
    def test_in_session(session_ctx):
        # Your test logic here
        return {'success': True, 'result': data}
    
    results = piw_session['run'](test_in_session)
    assert results['success']
    # Additional assertions
```

### Agentd Testing
```python
@pytest.mark.integration
@pytest.mark.timeout(15)
def test_agentd_functionality(eigend_agentd_session):
    """Test agentd with full initialization."""
    context = eigend_agentd_session()
    assert context['success']
    agent = context['agent']
    # Test agent functionality
```

## Testing Environment

- **Execution**: Use `./run_tests.sh --quick` from project root
- **Output**: To see print statements and test output, run pytest directly with `-s` flag: `source .venv_dev/bin/activate && python3.14 -m pytest -s -k "test_name" tests/unit/`
- **Quick Mode**: `--quick-teardown` skips hanging cleanup for faster development
- **Timeouts**: Integration tests use `@pytest.mark.timeout(15)` for longer execution
- **Paths**: All EigenD paths are auto-configured by `setup_eigend_environment` - use relative paths like `tmp/plugins`
- **Libraries**: DYLD_LIBRARY_PATH set automatically for macOS
- **Important**: Do not run Python scripts directly outside the test framework - EigenD modules require proper environment setup (paths, libraries) that is only available through `./run_tests.sh` or VS Code tasks. Direct `python` execution will fail with import errors.

## Test Level Guidelines

- **Foundation**: Basic imports, environment setup, no complex logic
- **Core**: PIW operations, session management, real-time behavior
- **Data**: Serialization, type validation, data transformation
- **Plugins**: Plugin system, agent framework, **plugin instantiation with PIW session context**
- **Applications**: CLI tools, backend services, command execution
- **Integration**: Cross-plugin workflows, full application integration scenarios

## Common Patterns

- Use `pytest.skip()` for missing dependencies, not for test logic
- Use `pytest.mark.timeout(N)` for long-running tests
- Check for plugin availability before testing
- Use session fixtures for integration testing
- Validate both success and error conditions