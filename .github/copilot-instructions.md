# EigenD Development Guide for AI Agents

## Architecture Overview

EigenD is a modular music software system for Eigenharp instruments built on a Python/C++ hybrid architecture:

- **Core Runtime**: `eigend` daemon (`app_eigend2/`) manages the plugin ecosystem and provides GUI
- **Plugin System**: Agent-based plugins (`plg_*/`) implement musical functionality (synthesizers, MIDI, audio processing)
- **Language Layer**: Belcanto natural language system (`plg_language/`) for live performance control
- **Real-time Engine**: `piw` (Pi Wire) library provides low-latency audio/control signal processing
- **Session Management**: `pisession/` handles agent lifecycle and inter-agent communication

## Key Development Patterns

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