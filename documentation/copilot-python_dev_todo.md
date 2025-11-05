# Python 3.14 Migration TODO

## Immediate - Ready to Test
- Test bcat command to verify basic Python 3.14 module loading
- Test bls command (browse/list agents)
- Test rpc command (RPC calls)
- Test rexec command (execute Belcanto commands)

## High Priority - Runtime Testing
- Test simple command-line tools (cheatsheet, signature, etc)
- Test pezload (Pico firmware loading - uses bytearray)
- Start EigenD daemon and verify initialization
- Test minimal plugin setup (no Eigenharp connected)
- Check for GIL/threading issues (deadlocks, hangs)

## Medium Priority - Full System
- Test with Eigenharp connected (Alpha/Tau/Pico)
- Test audio output plugins
- Test MIDI input/output
- Test all plg_* modules incrementally
- Test setup loading and saving
- Verify upgrade path from old setups

## Lower Priority - Advanced Tools
- Test Workbench application (GUI tool)
- Test Stage application
- Decide fate of Browser/Commander (already broken, may not fix)

## Code Review Needed
- Verify bytearray usage in pezload and MIDI code
- Check all uses of pip_usegil flag behavior
- Review any remaining #if PY_VERSION_HEX conditionals
- Search for any missed Python 2 API calls

## Documentation
- Update main README with Python 3.14 requirement
- Update NOTES_MACOS.md with Python 3 build instructions
- Update .github/copilot-instructions.md with Python 3 context
- Document installation process (Homebrew Python)
- Note breaking changes from Python 2.7 version
- Document VST SDK as optional dependency
- Create release notes for community
- Consider removing Python 2.7 fallback code paths

## Platform Support
- Windows: Update tools/windows_tools.py for Python 3
- Linux: Update tools/linux_tools.py for Python 3
- Test builds on all platforms

## Known Issues to Monitor
- GIL behavior under high load (audio dropout?)
- Memory allocator changes in Python 3 (potential deadlocks?)
- Unicode/bytes handling in MIDI and binary protocols
- Performance comparison vs Python 2.7 version

## Potential Improvements
- Remove #if PY_VERSION_HEX < 0x03000000 conditionals (Python 2 support)
- Clean up compatibility macros in template
- Update PLY (lex.py/yacc.py) to latest Python 3 version
- Consider Python 3.14 specific optimizations

## Git/Release
- Commit template fixes with clear message
- Tag working version after basic testing passes
- Merge to main branch after full testing
- Create beta release for community testing

## Future Considerations
- Evaluate CMake vs SCons (SCons 4.x working, no immediate need)
- CMake migration would require rewriting ~100+ build files (3-6 months effort)
- Only consider if SCons proves problematic during full runtime testing
