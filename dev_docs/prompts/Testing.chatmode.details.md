# EigenD Testing Framework — details (moved from chatmode)

This file contains the detailed guidance and procedures for the testing-focused agent. The chatmode file is intentionally minimal; refer here for exact commands, workflow, and mappings.

Core Expertise & Approach

Testing Framework Knowledge
- ALWAYS use `./run_tests.sh` (from PROJECT ROOT) for test execution — never run pytest directly.
- Use the root `/Users/kodiak/projects/EigenD/run_tests.sh`, not copies in subdirectories.
- The test hierarchy: Foundation → Core → Data → Plugins → Applications → Integration.
- Pytest-based framework with timeout protection, centralized fixtures, and markers.

TDD Development Workflow
1. Extend existing tests FIRST — add to existing test files before creating new ones.
2. Run tests before/after changes.
3. Fix issues at current level before moving on.
4. Maintain a clean test structure and remove temporary artifacts.
5. Use centralized fixtures from conftest.py.

Test Level Structure
```
tests/unit/
├── test_00_foundation.py    # Python 3.14 environment, module imports
├── test_01_core_piw.py      # PIW engine, sessions, real-time ops
├── test_02_data_layer.py    # Serialization, encoding, data types
├── test_03_plugins.py       # Plugin system, agent framework
├── test_04_applications.py  # Command-line tools, backend services
└── test_05_integration.py   # End-to-end workflows, system integration
```

Professional Standards
- Timeout protection (default 10s) to prevent hanging tests.
- Use pytest.skip() defensively when components are absent.
- Provide descriptive error messages in tests.
- Organize tests with markers for selective execution.

Key Migration Issues to Watch
- PIW session context and timeout handling.
- String/bytes encoding in serialization.
- Range concatenation and other py3 compatibility fixes.
- Native module loading nuances in test envs.

Agent Instructions — testing actions
- When the user asks to run tests, prefer `./run_tests.sh --level <level> --verbose` from project root.
- Map natural language levels (foundation/core/data/plugins/applications/integration/all) to `--level` values.
- If `run_in_terminal` is unavailable, provide the exact command and explain expected outputs succinctly.

Automatic Test Execution Protocol
- On natural-language test commands, run `./run_tests.sh --level <level>` immediately (no confirmation), then report:
  - Status: pass/fail/skip summary
  - Root cause analysis for failures (one-paragraph)
  - Next steps (1-3 actions)

Command Examples
- `./run_tests.sh --level foundation`
- `./run_tests.sh --level applications`
- `./run_tests.sh --level all --verbose`
- `./run_tests.sh --html`

Test Addition Template
```python
@pytest.mark.<level>
def test_<short_name>():
    """Brief docstring: reproduces <issue> and asserts expected behavior."""
    # minimal reproducible example using fixtures
```

Result Reporting Format
- Keep results brief and action-focused:
  - Status: X passed, Y failed, Z skipped
  - Root cause: single concise paragraph
  - Next: 1-3 concrete actions

Files and artifacts
- Keep tests/ directory clean.
- Use `conftest.py` for fixtures and shared setup.
- Update `dev_docs/copilot-session_resume.md` after substantive session changes (date-stamped).

When Tools Are Limited
- If `run_in_terminal` is disabled: provide the exact command(s) and the expected key results succinctly; offer to analyze results when provided.

Mapping common failures → target test files
- eigend startup failure → test_04_applications.py (TestEigendBackend)
- browser/commander crash → test_05_integration.py (TestApplicationIntegration)
- plugin loading error → test_03_plugins.py
- PIW session hang → test_01_core_piw.py
- import/module error → test_00_foundation.py

Quick reference (short)
- Natural-language mapping: "test foundation|core|data|plugins|applications|integration|all"
- Run from project root using `./run_tests.sh --level <level> [--verbose] [--html]`

Keep this file as the authoritative source for process and mapping details. The chatmode file should remain minimal and stable.
