# EigenD Architecture Roadmap

**Version**: 2.3.0 (Community Edition)  
**Python**: 3.14 (from python.org)  
**Build System**: SCons 4.5.0 (embedded) + Make wrappers  
**Updated**: 2025-11-10

---

## Build System & Dependencies

### Core Build Tools
- **SCons 4.5.0**: Embedded build system in `tools/packages/SCons4/`
  - Launched via `tools/scons.py`
  - Required version check: ≥ 4.5.0 (enforced in `tools/SConstruct`)
  - Custom platform tools: `darwin_tools.py`, `windows_tools.py`, `linux_tools.py`, `unix_tools.py`
  - Build configuration: `SConscript.first` (release info), individual `SConscript` files per module
  
- **Python 3.14**: Build and runtime environment
  - **macOS**: `/usr/local/bin/python3.14` (python.org installer)
  - **Windows**: `C:\Python314\python.exe` (python.org installer)
  - **Linux**: `/usr/bin/python3.14` (distro package: `python3.14` or python.org source)
  - Runtime: `python314.dll` / `python3.14.dylib` / `libpython3.14.so`
  - Note: Linux supports multiple Python versions side-by-side

- **Make**: Cross-platform build wrapper
  - `make` or `make parallel`: Build runnable system in `tmp/`
  - `make mpkg`: Build installers for distribution
  - `make dev-setup`: Create `.venv_dev/` for testing (pytest, etc.)
  - Platform detection: Auto-detects macOS/Windows(MSYS2)/Linux

- **CMake 3.15+**: IDE integration wrapper (delegates to SCons)
  - `cmake -B build`: Configure build directory
  - `cmake --build build`: Build with default target (8 parallel jobs)
  - `cmake --build build --target parallel`: Parallel build
  - `cmake --build build --target single`: Single-threaded build
  - `cmake --build build --target clean-all`: Clean all artifacts
  - Note: CMake is a wrapper - actual build system is SCons
  - Provides VS Code task integration and IDE support

- **Windows (MSYS2 Required)**:
  - **MSYS2 MinGW64**: Unified build environment (matches macOS/Linux workflow)
  - **MSVC 2019/2022**: Compiler with auto-detection in SCons
  - **DirectX SDK**: Optional, warns if missing (may be in Windows SDK)
  - See `NOTES_WINDOWS.md` for setup instructions

### Third-Party Libraries (Vendored)

- **FFTW 3.3.10** (`lib_fftw/`)
  - MIT licensed FFT library
  - Built as shared library (`pifftw.dll`/`.dylib`/`.so`)
  - Depends only on `picross` for `pic_config.h`

- **JUCE 6.0.8** (`lib_juce/`)
  - Cross-platform GUI/audio toolkit
  - Built as shared library (`pijuce.dll`/`.dylib`/`.so`)
  - Custom look-and-feel: `ejuce_laf.cpp`

- **liblo** (`lib_lo/`)
  - OSC (Open Sound Control) library
  - Built as shared library (`pilo.dll`/`.dylib`/`.so`)
  - Depends only on `picross` for `pic_config.h`

- **libsamplerate** (`lib_samplerate/`)
  - Sample rate conversion library (SRC)
  - Built as shared library (`pisamplerate.dll`/`.dylib`/`.so`)
  - Files: `src_linear.c`, `src_sinc.c`, `src_zoh.c`

- **SQLite** (`lib_sqlite/`)
  - Embedded database for session/configuration storage

- **VST3 SDK** (`vst3sdk/`)
  - Steinberg VST3 plugin hosting support

### Build Outputs
- **tmp/**: All build products, runnable system
  - `tmp/bin/`: Command-line executables
  - `tmp/app/`: GUI applications (macOS: `.app` bundles)
  - `tmp/pkg/`: Distribution installers (after `make mpkg`)
- **build/**: CMake build directory (experimental, SCons is primary)

---

## Core Infrastructure

### Build System (`tools/`)
Cross-platform SCons build system with platform-specific configurations:
- `SConstruct`: Root build file, discovers all `SConscript` files
- `darwin_tools.py`: macOS-specific compiler/linker settings
- `windows_tools.py`: Windows MSVC + DirectX SDK configuration
- `linux_tools.py`: Linux GCC configuration
- `unix_tools.py`: Shared Unix (macOS/Linux) utilities
- `select_tools.py`: Platform detection and tool selection
- `pip_cmd/`: Python wrapper generator (`.pip` → `.cpp` files)

### Top-Level Build Configuration
- **SConscript.first**: Release version, compatibility tags, package metadata
  - Current: v2.3.0-community
  - Compatible: v2.3-community
  - Packages: `eigend` (application), `eigend-build` (build system)

---

## Fundamental Libraries

### Platform Abstraction
- **picross**: Cross-platform utilities and abstractions
  - No external dependencies
  - Foundation for all other libraries
  - Provides: `pic_config.h`, threading, atomics, platform detection

- **piembedded**: Message handling for embedded systems
  - Lightweight message queue implementation
  - Originally for kernel/DSP usage
  - Depends: `picross`

### Hardware Libraries
- **lib_alpha2**: Eigenharp Alpha (v2 production) and Tau support
  - USB communication, LED control, key/breath sensing
  - Test/utility programs included
  - Depends: `picross` only

- **lib_pico**: Eigenharp Pico support
  - USB communication, button/strip sensing
  - Firmware loading utilities
  - Depends: `picross` only

- **lib_micro**: Eigenharp Micro support (early Pico prototype)
  - Legacy hardware support
  - Test/utility programs included
  - Depends: `picross` only

---

## High-Level Libraries

### Protocol & Language
- **pibelcanto**: Belcanto language lexicon and protocol
  - Language constants and keywords
  - C API for agents
  - Protocol-level message definitions

### Agent Framework
- **piagent**: Core EigenD agent hosting system
  - Host-side API implementation from `pibelcanto`
  - Agent lifecycle management
  - Message routing and scheduling
  - Depends: low-level libs, `pibelcanto`

- **piw**: Agent-side C++ utilities and wrappers
  - Data flow management
  - Agent port abstractions
  - Python wrappers via `piw.pip`
  - Depends: low-level libs, `pibelcanto`, JUCE (⚠️ tight coupling)

- **pi**: High-level agent utilities
  - Common agent patterns and helpers
  - Depends: `piw`, `piagent`

### UI & Session
- **pigui**: wxPython GUI utilities
  - Used by Browser and Commander applications

- **pisession**: Session management and persistence
  - Setup upgrade logic
  - Standalone program embedding utilities
  - SQLite-based session storage

---

## Agents (Plugins)

### Hardware Agents
- **plg_keyboard**: Eigenharp Alpha and Tau
- **plg_pkbd**: Eigenharp Pico
- **plg_ukbd**: Eigenharp Micro

### Audio/MIDI I/O
- **plg_audio**: Audio input/output (macOS CoreAudio, Windows WASAPI)
- **plg_midi**: MIDI input/output/conversion
- **plg_midi_device**: MIDI device management
- **plg_midi_monitor**: MIDI activity monitoring

### Instruments & Sound
- **plg_sampler2**: Sample playback engine
- **plg_synth**: Modular synthesis (oscillators, envelopes)
- **plg_stk**: Synthesis Toolkit instruments (Cello, Clarinet)
- **plg_convolver**: Convolution reverb (used by Cello)

### Control & Performance
- **plg_arranger**: Performance arrangement and scene management
- **plg_conductor**: Tempo and timing control (Metronome, Drummer, Clicker)
- **plg_loop**: Loop recording and playback
- **plg_recorder**: Audio recording
- **plg_scale_illuminator**: Key illumination for scales
- **plg_illuminator**: General LED/key illumination

### Advanced Features
- **plg_host**: VST/AU plugin hosting
- **plg_language**: Belcanto interpreter agent
- **plg_osc**: OSC (Open Sound Control) communication example
- **plg_simple**: Single-file agents using `pi`/`piw` facilities
- **plg_rig**: Signal routing and patching
- **plg_tabulator**: Tabulature/tablature support
- **plg_t3d**: 3D input support

### Experimental/Legacy
- **plg_finger**: (Status unknown)
- **plg_livepad**: (Status unknown)
- **plg_primitive**: (Status unknown)
- **plg_strummer**: String instrument simulation

---

## Applications

### End-User Applications
- **app_juceworkbench** (`Workbench.app`/`Workbench.exe`):
  - Main JUCE-based GUI application
  - Modern UI, integrated session management
  - Launch: `./tmp/app/Workbench.app/Contents/MacOS/Workbench` (macOS)

- **app_browser2**: Python/wxPython setup browser
  - Visual agent browsing and configuration
  - Belcanto command panel
  - Legacy UI (Python 2 → 3 migration)

- **app_commander**: Python/wxPython command interface
  - Belcanto command-line interface
  - History and dictionary features
  - Legacy UI (Python 2 → 3 migration)

- **app_eigend2** (`eigend`):
  - EigenD daemon/backend process
  - C++ core with Python embedding
  - Handles agent lifecycle and audio threads
  - Built as both GUI and console versions (Windows)

### Development Tools (`app_cmdline/`)
Command-line utilities for development and administration:
- `bls`: List agent setup/configuration
- `bcat2`: Display agent properties
- `bcopyrel`: Copy release configurations
- `bstdump`, `bstlist`: Setup state inspection
- `analyze_setup.py`: Setup analysis
- `capture.py`: Data capture utilities
- `mirror.py`: Setup mirroring
- `rbrowse.py`: Remote browsing
- `rexec.py`, `rsh.py`: Remote execution
- `rpc.py`: RPC utilities
- `script.py`: Scripting interface
- `signature.py`: Cryptographic signing
- `upgrade_user.py`, `upgrade34.py`: Migration scripts

### Installation
- **app_install**: Post-installation configuration
  - JUCE-based installer components
  - Platform-specific post-flight scripts
  - Python setup verification

- **app_stage**: Staging utilities for releases

---

## Resources & Documentation

### Assets
- **resources/**: Non-free resource files, bundled DLLs
- **branding/**: Logos, icons, application branding
- **sys_init/**: Release packaging and initialization

### Documentation
- **documentation/**: User manuals, API documentation
- **dev_docs/**: Development notes and internal docs
  - `dev_todo.md`: Current development priorities
  - `copilot-session_resume.md`: Session state for AI assistant
  - `prompts/`: Detailed technical notes and migration guides
- **NOTES_MACOS.md**: macOS-specific build/development notes
- **NOTES_WINDOWS.md**: Windows MSYS2 setup guide
- **README**: Original project overview
- **COPYING**: GPLv3 license

### Testing
- **tests/**: Unit tests (pytest framework)
- **run_tests.sh**: Test runner (auto-activates `.venv_dev/`)
- **py_requirements.txt**: Testing dependencies (pytest ≥8.0.0)
- **.venv_dev/**: Isolated Python environment for development

### Migration & Scripts
- **migration_scripts/**: Database/setup migration utilities
- **tools/packages/**: SCons packaging utilities

---

## Development Workflow

### Quick Start
```bash
# Setup development environment (creates .venv_dev/)
make dev-setup

# Build EigenD (parallel build, default)
make

# Build single-threaded (for debugging)
make single

# Run tests
./run_tests.sh

# Launch Workbench
./tmp/app/Workbench.app/Contents/MacOS/Workbench  # macOS
```

### Platform-Specific Setup
- **macOS**: Install Python 3.14 from python.org, Xcode Command Line Tools
- **Windows**: See `NOTES_WINDOWS.md` - MSYS2 + MSVC 2019/2022 + DirectX SDK
- **Linux**: Install Python 3.14 and dev headers
  - Ubuntu/Debian: `apt install python3.14 python3.14-dev` (or add deadsnakes PPA if not in repos)
  - Fedora/RHEL: `dnf install python3.14 python3.14-devel`
  - Arch: `pacman -S python` (usually latest)
  - Or compile from python.org source
  - Also install: GCC, build-essential, development headers

### Build Targets
- `make` / `make parallel`: Default parallel build (8 jobs)
- `make single`: Single-threaded build
- `make verbose`: Verbose compiler output
- `make quiet`: Minimal output
- `make clean-all`: Clean all build artifacts
- `make mpkg`: Build distribution packages
- `make tags`: Generate ctags for navigation

---

## Architecture Notes

### Key Design Principles
1. **Agent-based**: Modular plugin architecture, agents communicate via `piagent`
2. **Real-time audio**: Low-latency audio processing with priority threads
3. **Cross-platform**: Unified codebase for macOS/Windows/Linux
4. **Belcanto**: Domain-specific language for musical control
5. **Hardware integration**: Direct USB communication with Eigenharp devices

### Critical Dependencies
- **JUCE coupling**: `piw` depends on JUCE (audio buffers, threading) - limits portability
- **Python embedding**: Agent scripting, UI applications embed Python 3.14
- **Real-time constraints**: Audio thread cannot allocate, block, or call Python

### Known Issues & TODOs
- See `dev_docs/dev_todo.md` for current development priorities
- Windows build modernization in progress (MSYS2 mandate, MSVC validation)
- Python 3.14 migration complete, testing ongoing
- Legacy Python 2 UI applications (Browser, Commander) need modernization

---

## License

**EigenD** is licensed under the **GNU General Public License v3.0** (GPLv3).  
See `COPYING` for full license text.

**Community Edition**: Open-source release maintained by community contributors.

---

*For detailed build instructions, see platform-specific notes: `NOTES_MACOS.md`, `NOTES_WINDOWS.md`*  
*For development status, see: `dev_docs/dev_todo.md`*
