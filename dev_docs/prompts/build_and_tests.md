# Build & Test Commands (prompt reference)

- Tests
  - Quick: `./run_tests.sh --quick --level foundation`
  - Full: `./run_tests.sh --level all --verbose`
  - After tests record results in `dev_docs/copilot-session_resume.md`.

- Builds
  - Basic: `make`
  - Full package: `make mpkg`
  - Use SCons via bundled script for specific targets:
    PYTHONPATH=tools/packages/SCons4 python3 tools/packages/SCons4/bin/scons -f tools/SConstruct -j8 <target>

- Example targets
  - lib_juce, plg_midi, app_eigend2

Keep this file short — include only commands the agent should use. Add details only when necessary.
