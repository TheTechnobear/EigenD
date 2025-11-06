# EigenD Development Guide for AI Agents

## Current Project Status: Python 3.14 Migration (TDD Approach)

**CRITICAL**: This workspace follows Test-Driven Development. Always:
1. Run tests before making changes: `./run_tests.sh --level <level>`
2. Current status: 36/43 tests passing across 6 layers
3. Focus: Complete integration layer, address PIW string segfault
4. Test hierarchy: Foundation→Core→Data→Plugins→Applications→Integration

## Migration Documentation
**ALWAYS check these files for current status and context:**
- `dev_docs/dev_notes.md` - Complete migration changelog and fixes applied
- `dev_docs/dev_todo.md` - Current task tracking and priorities  
- `dev_docs/copilot-session_resume.md` - Complete context for resuming work
- `dev_docs/dev_howitworks.md` - Quick system reference
- `dev_docs/binary_protocol.md` - Binary protocol compatibility analysis

**CRITICAL - Keep Documentation Current:**
- **ALWAYS** update `copilot-session_resume.md` with current TDD status, test results, and recent fixes
- **ALWAYS** add completed fixes to `dev_notes.md` with technical details
- **ALWAYS** update `dev_todo.md` priorities as work progresses
- **ALWAYS** keep `dev_docs/README.md` current with file list and organization changes
- **DATE STAMP** all significant updates with current date in YYYY-MM-DD format

## Documentation Policy
**CRITICAL - Avoid Documentation Redundancy:**
- **DO NOT** create new documentation files (README-*.md, *-instructions.md, etc.) without explicit user consent
- **DO** update existing `dev_docs/copilot-*.md` files with new information
- **DO** ask user before creating new docs: "Should I create a new file or update existing documentation?"
- **EXCEPTION**: If you believe a genuinely new type of documentation is essential, explain why before creating
- **REMEMBER**: We removed redundant files (.vscode/workspace-instructions.md, README-TDD.md, CONTINUE_HERE.md) to maintain single source of truth

## Quick Commands
- `./run_tests.sh --quick --level foundation` - Fast TDD cycles (recommended)
- `./run_tests.sh --level all --verbose` - Full test suite validation
- Tests located in `tests/unit/test_XX_*.py` (XX = 00-05)

## Architecture Overview

EigenD is a modular music software system for Eigenharp instruments built on a Python/C++ hybrid architecture:

- **Core Runtime**: `eigend` daemon (`app_eigend2/`) manages the plugin ecosystem and provides GUI
- **Plugin System**: Agent-based plugins (`plg_*/`) implement musical functionality (synthesizers, MIDI, audio processing)
- **Language Layer**: Belcanto natural language system (`plg_language/`) for live performance control
- **Real-time Engine**: `piw` (Pi Wire) library provides low-latency audio/control signal processing
- **Session Management**: `pisession/` handles agent lifecycle and inter-agent communication

## Key Development Patterns

### VST3 SDK Integration (Temporary Hybrid Approach)
**Current Status**: Uses external VST3 SDK v3.8.0 headers with JUCE's built-in implementation + utility functions
- **Issue**: JUCE's embedded VST3 SDK was v3.6.13 (older), external submodule has v3.8.0
- **Solution**: Removed JUCE's embedded VST3 SDK, use external headers, compile only missing utility functions
- **Files**: `lib_juce/SConscript` compiles `stringconvert.cpp` and `commonstringconvert.cpp` from external VST3 SDK
- **Build Location**: VST3 utility objects built in `tmp/obj/vst3sdk/` (not in submodule)
- **TODO**: Update JUCE to latest version (includes newer VST3 SDK), then remove external vst3sdk submodule

### Plugin Structure
All plugins follow the Agent pattern in `pi/agent.py`:
```python
from pi import agent, atom, bundles
class Agent(agent.Agent):
    def __init__(self, address, ordinal):
        agent.Agent.__init__(self, signature=version, names='plugin_name', ordinal=ordinal)
        # Set up inputs/outputs, domain, etc.
agent.main(Agent)
```

### Build System (SCons)
- Use `env.PiAgent()` to register plugins: `env.PiAgent('name','package','module',cversion='1.0.0')`
- `env.PiPythonPackage()` for Python modules, `env.PiSharedLibrary()` for C++ libraries
- `env.PiPipBinding()` creates Python bindings for C++ code using `.pip` interface files
- Build with `make` (or `make mpkg` for full package), not `scons` directly

### Audio Signal Flow
- `bundles.Output()` and `bundles.Input()` for audio/control connections
- `piw.clockdomain_ctl()` manages real-time scheduling domains
- Signal types: audio (continuous), control (sparse events), trigger (momentary)

### Python/C++ Integration (PIP Files)
EigenD uses a custom binding system to connect Python agent code with C++ real-time processing:

1. **C++ Implementation**: Real-time audio/MIDI processing in `src/*.cpp` files using `piw` library
2. **PIP Interface**: `.pip` files define Python-accessible C++ class interfaces (like SWIG but custom)
3. **Python Binding**: `env.PiPipBinding()` generates native Python modules from PIP files
4. **Agent Integration**: Python agents import and use the native module for real-time operations

Example flow for `plg_midi_device`:
```cpp
// midi_device.h - C++ class definition
class midi_device_t {
    midi_device_t(piw::clockdomain_ctl_t *, const piw::cookie_t &);
    piw::cookie_t cookie();
    void channel(unsigned);
};
```

```plaintext
// midi_device_plg.pip - Interface definition
from piw[piw/piw.pip] import cookie,clockdomain_ctl
class midi_device[midi_device_plg::midi_device_t] {
    midi_device(clockdomain_ctl *, const cookie &)
    cookie cookie()
    void channel(unsigned)
}
```

```python
# midi_device_plg.py - Python agent
from .midi_device_plg_native import midi_device
class Agent(agent.Agent):
    def __init__(self, address, ordinal):
        self.device = midi_device(self.domain, output_cookie)
```

### Command Processing (Belcanto)
- Natural language commands processed through `plg_language/language_plg.py`
- Commands translated between English and musical notation in `pi/database.py`
- RPC system (`pi/rpc.py`, `piw/piw_rpc.h`) handles inter-agent communication

## Critical Build Dependencies

### Platform Requirements
- **macOS**: Xcode, Python 2.7 framework, architecture-specific builds (`BUILD_TARGET=arm` vs `BUILD_TARGET=x86_64`)
- **Windows**: Visual Studio 2015, NSIS, WiX, DirectX SDK
- **Linux**: build-essential, ALSA, X11 development packages

### External Dependencies
- **Steinberg VST SDK**: Required in `steinberg/` subdirectory for plugin hosting
- **JUCE Framework**: Embedded in `lib_juce/` for cross-platform GUI and audio
- **Python Runtime**: Must use system Python on macOS (`/System/Library/Frameworks/Python.framework/`)

## Development Workflows

### Building
```bash
# Basic build (creates tmp/app/EigenD.app)
make

# Full package with installer
make mpkg

# Architecture-specific macOS builds
export BUILD_TARGET=arm && make
export BUILD_TARGET=x86_64 && make

# Direct SCons build for specific targets (use when make doesn't pass parameters)
PYTHONPATH=tools/packages/SCons4 python3 tools/packages/SCons4/bin/scons -f tools/SConstruct -j8 <target>
# Example: PYTHONPATH=tools/packages/SCons4 python3 tools/packages/SCons4/bin/scons -f tools/SConstruct -j8 lib_juce
```

### Adding New Plugins
1. Create `plg_name/` directory with `SConscript` and Python module
2. Register with `env.PiAgent()` in SConscript
3. Follow Agent pattern with proper signature and version
4. Add to appropriate setup files if needed for default configurations

### Command Line Tools
- `bls` - list/browse agents and connections
- `rpc` - execute RPC calls on agents  
- `rexec` - execute Belcanto commands
- `rbrowse` - interactive agent browser

## Common Gotchas

- **Thread Safety**: Use `piw.tsd_lock()` when accessing agents from different threads
- **Memory Management**: C++ objects often managed through `pic::tracked_t` smart pointers
- **Build Warnings as Errors**: Fix all compiler warnings immediately; builds treat warnings as errors
- **Architecture Mixing**: Cannot mix ARM and x86_64 plugins on macOS, no universal binaries
- **Python Version**: Must use exact system Python version, not custom installs

## Key Files for Understanding System

- `pi/agent.py` - Base agent class and RPC infrastructure
- `piw/` - Real-time audio engine interfaces  
- `app_eigend2/eigend.cpp` - Main daemon application
- `tools/generic_tools.py` - SCons build system extensions
- `pisession/session.py` - Session and agent lifecycle management
- `plg_language/language_plg.py` - Belcanto command interpreter

This system prioritizes real-time performance and modular extensibility over conventional software patterns.