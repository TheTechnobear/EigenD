# Python 3.14 Migration TODO

## Status: Updated 2025-11-05

### ✅ COMPLETED
- ✅ Build system fully working (make, make mpkg)
- ✅ PIP binding system (Python/C++ integration)
- ✅ Template fixes (lock_c2p, bytearray, moddoc, PyCapsule)
- ✅ Import fixes in pi/ modules (bare imports → from pi import)
- ✅ Import fixes in pi/logic/ (relative → absolute imports)
- ✅ Python 2→3 compatibility (cmp, long, string.maketrans, parser, exceptions, imp)
- ✅ Basic command-line tools: bcat, bls, bpaths, brexec, brpc, bscript, bdownload, capture, signature, upgrade34, annotate
- ✅ Belcanto logic system (pi/logic/) imports and initializes

### 🔄 IN PROGRESS - Next Session
**Start here on new computer:**

1. **Fix cheatsheet command** (minor)
   - Issue: `TypeError: can only concatenate list (not "range") to list`
   - Location: app_cmdline/cheat.py line 27
   - Fix: Wrap range() with list() - `[x] + range(y)` → `[x] + list(range(y))`

2. **Test EigenD daemon startup**
   - Command: `./tmp/bin/eigend --cmdline`
   - Expected: May have additional import/compatibility issues
   - Watch for: GIL issues, threading problems, plugin loading errors

3. **Test base_loader (minimal setup)**
   - Command: `./tmp/bin/base_loader`
   - Expected: Should load without Eigenharp hardware
   - Tests: Agent initialization, plugin loading basics

## High Priority - Runtime Testing
- Test pezload (Pico firmware loading - uses bytearray)
- Test minimal plugin setup (no Eigenharp connected)
- Check for GIL/threading issues (deadlocks, hangs)
- Monitor for audio thread priority issues

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
- ✅ Committed build system fixes (commit 55a8e099)
- ✅ Committed template fixes (commit 98f03aa8)  
- ✅ Committed pi/logic and runtime fixes (commit d431988d)
- ⏭️ Tag working version after daemon testing passes
- ⏭️ Merge to main branch after full testing
- ⏭️ Create beta release for community testing

## Future Considerations
- Evaluate CMake vs SCons (SCons 4.x working, no immediate need)
- CMake migration would require rewriting ~100+ build files (3-6 months effort)
- Only consider if SCons proves problematic during full runtime testing

## Comparison with TheTechnobear's python3 Branch
Our copilot branch is MORE COMPLETE than the python3 branch:
- ✅ We fixed lock_c2p GIL API properly
- ✅ We added bytearray support  
- ✅ We fixed cmp(), long, string.maketrans (python3 branch has typos)
- ✅ We fixed parser module (python3 branch incomplete)
- ✅ We tested command-line tools (python3 branch untested)
- ⚠️ python3 branch has bugs: encoder() vs encode() typo, unfixed long/cmp references
