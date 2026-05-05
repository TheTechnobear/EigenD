# EigenD Windows Build Guide: MinGW-w64

> **Status: Phase A (active development, untested)**
> This is the new default Windows build path. See `implement_mingw.md` for
> the SCons integration details and known implementation issues.

---

## Quick Reference

```bash
# Open MSYS2 UCRT64 shell, then:
cd /c/Projects/EigenD
make dev-setup   # one-time only
make             # build
make clean       # clean build artefacts
```

No `vcvars64.bat` sourcing. No Visual Studio required.

---

## Platform Requirements

**Minimum Windows version: Windows 10 1803 (April 2018 Update)**

| Platform | Status |
|----------|--------|
| Windows 10 x86_64 | Supported |
| Windows 11 x86_64 | Supported |
| Windows 11 ARM64 | x86_64 builds run under Prism emulation — see note below |
| Windows 7 / 8 / 8.1 | Not supported |

The UCRT64 environment links against `ucrtbase.dll` (Universal C Runtime), which ships
with Windows 10 and is not available on Windows 7/8.

### Windows ARM64 note

This build system targets **x86_64 only**. Native ARM64 Windows binaries are not
currently produced.

However, Windows 11 on ARM64 hardware (e.g. Snapdragon X Elite / Copilot+ PCs)
includes **Prism**, Microsoft's x86_64 emulation layer. x86_64 EigenD binaries run
under Prism without modification. Performance for typical MIDI/audio workloads should
be acceptable, but audio DSP paths that rely on SSE2 vectorisation will run at emulated
speed rather than native NEON speed.

Native ARM64 support is a future consideration — see `implement_mingw.md` for the
options and what would be required.

---

## Prerequisites

### 1. Python 3.14 (python.org)

Download from **https://www.python.org/downloads/** and install to the default location
`C:\Python314\`.

During installation:
- Check **"Add Python to PATH"**
- Choose "Install for all users" (or note your custom path)

This Python is used for:
- Running SCons (the build system)
- Compiling Python extension modules (`.pyd`) — headers from `C:\Python314\include\`
- Linking Python extension modules — import lib at `C:\Python314\libs\python314.lib`
- Runtime: `python314.dll` is shipped with the application

> If Python is installed elsewhere, override the path: `make PYTHON_BUILD=/c/Python316/python.exe`

### 2. MSYS2 — UCRT64 environment

Download from **https://www.msys2.org/** and install to `C:\msys64\` (default).

After installation, open the **MSYS2 UCRT64** shell (yellow/cyan icon — not MinGW64 or plain MSYS2).

```bash
# Update MSYS2
pacman -Syu
# Close shell when prompted, reopen UCRT64 shell, then:
pacman -Syu

# Install MinGW-w64 UCRT64 toolchain
pacman -S --needed base-devel mingw-w64-ucrt-x86_64-toolchain

# Install libusb (required for Eigenharp USB hardware support)
pacman -S mingw-w64-ucrt-x86_64-libusb

# Install make and git
pacman -S make git
```

**Why UCRT64 and not MinGW64?**
UCRT64 uses the Universal C Runtime (`ucrtbase.dll`), which is the modern Windows C
runtime targeting Windows 10+. Package prefix: `mingw-w64-ucrt-x86_64-*`.

MinGW64 uses the older MSVCRT (`msvcrt.dll`, Windows 7+). If you need Windows 7
compatibility in the future, switch to the MinGW64 shell and update the package prefix.

### 3. Verify the toolchain

```bash
# From UCRT64 shell:
gcc --version      # GCC 14.x or later
g++ --version
python.exe --version   # Should find C:\Python314\python.exe via Windows PATH
```

---

## Build Session

All commands run from the **MSYS2 UCRT64** shell.

```bash
cd /c/Projects/EigenD

# One-time: create Python virtual environment for dev tools
make dev-setup

# Build (parallel, 8 jobs)
make

# Build single-threaded (easier to read error output)
make single

# Build a specific target
make lib_juce

# Clean all build outputs
make clean

# List available targets
make list-targets
```

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `PYTHON_BUILD` | `/c/Python314/python.exe` | Python used to run SCons |
| `BUILD_TOOLCHAIN` | `mingw` | Set to `msvc` to use legacy MSVC path |
| `MINGW_PREFIX` | (empty) | Cross-compile prefix, e.g. `x86_64-w64-mingw32-` |
| `PI_PYTHON` | same as `PYTHON_BUILD` | Override Python used for building |
| `JOBS` | `8` | Parallel build jobs |

### Switching back to MSVC (legacy)

```bash
BUILD_TOOLCHAIN=msvc make
```

---

## VSCode Integration

**Install VSCode normally as a Windows application** — download from code.visualstudio.com
and run the installer. Do not launch it from inside MSYS2 and do not add MSYS2 to your
Windows system PATH.

VSCode is a native Windows process. It finds MSYS2 tools via absolute paths in the
`.vscode/` config files (`C:\msys64\...`), not via the Windows system PATH. Tasks
invoke `bash.exe --login` which runs MSYS2's own startup scripts to set up the UCRT64
toolchain inside that shell session.

> **Do not add `C:\msys64\ucrt64\bin` to your Windows system PATH.** MSYS2 ships
> Unix tools (`find`, `sort`, `link`, `cc`) that shadow Windows equivalents and break
> unrelated software.

### Required extension

**C/C++** (`ms-vscode.cpptools`) — provides IntelliSense and GDB debugging.
Already listed in `EigenD.code-workspace` recommendations.

### Integrated terminal

When VSCode opens on Windows, the integrated terminal (`Ctrl+\``) automatically uses
the **MSYS2 UCRT64** shell (configured in `.vscode/settings.json`). You can run `make`
directly from it.

If the terminal does not pick up MSYS2, verify the setting manually:
`File → Preferences → Settings → "terminal.integrated.defaultProfile.windows"` → `MSYS2 UCRT64`

### IntelliSense

A `MinGW-w64 UCRT64 (Windows)` configuration is defined in `.vscode/c_cpp_properties.json`.
Select it from the IntelliSense configuration picker in the bottom status bar (click where
it shows the current config name, e.g. `macOS (Clang)`).

This points IntelliSense at MinGW headers and Python 3.14 headers so errors are
correctly reported without false positives from MSVC-only headers.

### Build tasks

Windows-specific SCons tasks are available via `Ctrl+Shift+B`:

| Task | Action |
|------|--------|
| `SCons: Build (MinGW)` | `make` — parallel build |
| `SCons: Build Single-threaded (MinGW)` | `make single` — sequential, easier to read errors |
| `SCons: Build Verbose (MinGW)` | `PI_VERBOSE=1 make single` — full compiler commands shown |
| `SCons: Clean (MinGW)` | `make clean` |

All tasks route through `C:\msys64\usr\bin\bash.exe --login` with `MSYSTEM=UCRT64`,
so the UCRT64 toolchain is on PATH regardless of how VSCode was launched.

### Debugging (GDB)

Install GDB via MSYS2 first:
```bash
pacman -S mingw-w64-ucrt-x86_64-gdb
```

Two GDB launch configurations are defined in `.vscode/launch.json`:

- **Windows: Debug eigend (MinGW GDB)** — builds then launches `tmp/bin/eigend.exe` under GDB
- **Windows: Debug eigend — no build (MinGW GDB)** — launches without rebuilding

Launch via `F5` or the Run & Debug panel (`Ctrl+Shift+D`).

### Note: MSYS2 path must be set

MSYS2 must be installed at `C:\msys64\`. If installed elsewhere, update these paths in
`.vscode/`:

| File | Paths to update |
|------|----------------|
| `settings.json` | `terminal.integrated.profiles.windows` → `path` |
| `tasks.json` | `options.shell.executable` in each SCons task |
| `launch.json` | `miDebuggerPath` in GDB configs |
| `c_cpp_properties.json` | `includePath` and `compilerPath` in MinGW config |

---

## Runtime Dependencies

When distributing a built EigenD on Windows, the following DLLs must accompany
the application binaries. These are **not** present on a standard Windows installation.

### Python runtime

| DLL | Source |
|-----|--------|
| `python314.dll` | `C:\Python314\python314.dll` |

Installed automatically by the build system (`PiRuntime()` in `mingw_tools.py`).

### MinGW-w64 runtime DLLs

Built with UCRT64, the application picks up these DLLs from the MSYS2 installation:

| DLL | Source path |
|-----|-------------|
| `libgcc_s_seh-1.dll` | `C:\msys64\ucrt64\bin\` |
| `libstdc++-6.dll` | `C:\msys64\ucrt64\bin\` |
| `libwinpthread-1.dll` | `C:\msys64\ucrt64\bin\` |

`ucrtbase.dll` (Universal C Runtime) is already present on Windows 10+.

These must be bundled in the installer (Phase B). Until then, for developer testing,
copy them into `tmp/bin/` alongside the built executables, or add
`C:\msys64\ucrt64\bin\` to `PATH`.

**Note on static linking:**
`-static-libgcc` can eliminate `libgcc_s_seh-1.dll` for executables. However,
`-static-libstdc++` must NOT be applied to shared libraries (DLLs), as each DLL
would embed its own copy of libstdc++, causing multiple heaps and exception-handling
failures across DLL boundaries. The approach taken is dynamic linking + ship the DLLs.

---

## Troubleshooting

### `python.exe` not found in MSYS2 shell

MSYS2 inherits the Windows PATH. If Python was installed with "Add to PATH" checked,
`python.exe` should be accessible. If not:

```bash
export PATH="/c/Python314:$PATH"
# Or override the make variable:
make PYTHON_BUILD=/c/Python314/python.exe
```

### Python import library linking fails

Python.org ships MSVC-format `.lib` files. MinGW's linker can use these for simple
import libraries (Python's qualifies), but if it fails:

```bash
# Generate a MinGW-compatible import library from the DLL
cd /c/Python314/libs
gendef /c/Python314/python314.dll
dlltool --input-def python314.def \
        --output-lib libpython314.dll.a \
        --dllname python314.dll
```

The build system will then pick up `libpython314.dll.a` from the `libs/` directory.

### Missing `AppConfig.h` (JUCE)

JUCE builds require this file in `lib_juce/`. Check that it exists:

```bash
ls lib_juce/AppConfig.h
```

If missing, it needs to be created as part of JUCE configuration — see `lib_juce/README` or existing JUCE documentation.

### Exception handling crashes at runtime

All DLLs must be compiled with the same exception model. Only use the UCRT64 shell
and its toolchain consistently — do not mix DLLs from UCRT64 and MinGW64 environments.

### Build uses MSVC unexpectedly

Check that `BUILD_TOOLCHAIN` is not set to `msvc` in your environment:

```bash
echo $BUILD_TOOLCHAIN
unset BUILD_TOOLCHAIN
```

---

## Phase B: Packaging (Planned)

The plan is to use **NSIS (Nullsoft Scriptable Install System)**:

- Free, no MSVC dependency
- The existing `windows_tools.py` already has NSIS support that will be ported to `mingw_tools.py`
- Installer will bundle MinGW runtime DLLs, Python DLL, and application binaries

Install NSIS via MSYS2: `pacman -S mingw-w64-ucrt-x86_64-nsis`

---

## Phase C: Cross-Compilation (Planned)

Cross-compiling from macOS or Linux for CI/CD pipelines.

**macOS host:**
```bash
brew install mingw-w64
export MINGW_PREFIX=x86_64-w64-mingw32-
make
```

**Linux (Ubuntu) host:**
```bash
sudo apt-get install gcc-mingw-w64-x86-64 g++-mingw-w64-x86-64 binutils-mingw-w64
export MINGW_PREFIX=x86_64-w64-mingw32-
make
```

Windows Python headers and import libraries must be extracted from a Python.org Windows
installer and made available on the host. See `implement_mingw.md` for the full
cross-compilation design details and current limitations.
