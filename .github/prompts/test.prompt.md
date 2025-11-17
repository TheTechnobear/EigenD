# Test Creation Prompt

You are an expert testing assistant for the EigenD project. When given a test request in the format "/test <description>", follow these steps:

1. **Analyze the Request**: Understand what the test should verify. Identify the component, functionality, or scenario being tested.

2. **Determine Test Level**: Map the test to the appropriate level based on the Unit Test Structure:
   - **Foundation**: Python environment, module imports, basic setup
   - **Core**: PIW engine, sessions, real-time operations
   - **Data**: Serialization, encoding, data types
   - **Plugins**: Plugin system, agent framework
   - **Applications**: Command-line tools, backend services
   - **Integration**: End-to-end workflows, system integration

3. **Check Existing Tests**:
   - Search the `tests/unit/` directory for existing test files at the determined level.
   - Look for similar tests that could be extended rather than creating duplicates.
   - If a relevant test file exists, add to it; otherwise, create a new test function in the appropriate file.

4. **Create or Extend Test**:
   - Use the Test Addition Template:
     ```python
     @pytest.mark.<level>
     def test_<short_name>():
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

**Test Level Structure**
```
tests/unit/
├── test_00_foundation.py    # Python environment, module imports
├── test_01_core_piw.py      # PIW engine, sessions, real-time ops
├── test_02_data_layer.py    # Serialization, encoding, data types
├── test_03_plugins.py       # Plugin system, agent framework
├── test_04_applications.py  # Command-line tools, backend services
└── test_05_integration.py   # End-to-end workflows, system integration
```

**Testing Framework Knowledge**
- Use `./run_tests.sh` (from PROJECT ROOT) for test execution to ensure proper environment.
- Use the root `~/run_tests.sh`, not copies in subdirectories.
- The test hierarchy: Foundation → Core → Data → Plugins → Applications → Integration.
- Pytest-based framework with timeout protection, centralized fixtures, and markers.
- Use centralized fixtures from conftest.py.