# EigenD Windows Build: clang-cl Investigation

> **Status: Active investigation (branch `clang4win`)**
> This branch starts clean — no changes from `mingw-w64` are present here.
> The `mingw-w64` branch is retained for reference only.
> This is a living document. Sections will be updated as findings are confirmed.

---

## Overview: Why clang-cl?

The MinGW-w64 investigation (`build_mingw.md`, `implement_mingw.md`) established that
GCC on Windows can build all EigenD non-GUI components, but hits a hard wall with
JUCE 8:

```cpp
// juce_core/system/juce_TargetPlatform.h
#ifdef __MINGW32__
    #error "MinGW is not supported. Please use an alternative compiler."
#endif
```

The underlying reason is not style preference: JUCE 8's Windows renderer uses COM
interfaces via `__declspec(uuid("..."))` and `__uuidof(T)`. These are MSVC language
extensions that GCC does not implement. They are not patchable.

**`clang-cl`** is the answer to this. It is a Clang front-end mode that:
- Accepts MSVC-compatible command-line syntax (`/O2`, `/W3`, `/EHsc` …)
- Implements `__declspec(uuid)`, `__uuidof`, `__forceinline`, and other MSVC extensions
- Links against the MSVC CRT (`ucrt`, `vcruntime`) rather than the MinGW CRT
- Produces object code and PDB files compatible with MSVC tooling
- Is approved and actively tested by the JUCE team on Windows

At the same time, `clang-cl` is a full modern Clang (C++17/20/23 support, excellent
diagnostics), not a fork of old MSVC. It is free, open source, and ships as part
of the LLVM project.

### Why not plain MSVC (`cl.exe`)?

Plain `cl.exe` works for JUCE but requires a full Visual Studio installation (several
GB), ties the build to a Windows-only workflow, and its SCons integration is already
in the project (`windows_tools.py`) but has not been maintained. `clang-cl` gives us
the same ABI and extension support, a better developer experience (faster compiles,
cleaner errors), and a smaller install footprint via VS Build Tools alone.

---

## Target Developer Environment

The goal is to keep the developer experience as close as possible to the MinGW
experience — a Unix-like terminal in MSYS2 plus VS Code, **not** a Visual Studio
Developer Command Prompt.

### What will be installed

| Tool | Source | Notes |
|------|--------|-------|
| MSYS2 (UCRT64 environment) | https://www.msys2.org | Same as MinGW setup |
| VS Build Tools 2022 | https://aka.ms/vs/17/release/vs_BuildTools.exe | Free. Provides CRT headers, `link.exe`, `lib.exe`, Windows SDK |
| LLVM for Windows | https://github.com/llvm/llvm-project/releases | Provides `clang-cl.exe`, `lld-link.exe` |
| Python 3.14 (python.org) | https://www.python.org/downloads/windows/ | Same as now |
| VS Code | https://code.visualstudio.com | Same as now |

MSYS2 itself does **not** provide the compiler in this configuration. It still
provides the shell (`bash`), `make`, `pacman`, and Unix tools. The LLVM/MSVC compilers
are installed on the Windows side and called from within MSYS2 by translating the
Windows paths.

### Shell and workflow

- Terminal: **MSYS2 UCRT64** bash (launched from VS Code or the MSYS2 shortcut)
- `make` / `make clean` / `make dev-setup` — same entry points as the MinGW build
- VS Code tasks (build, clean, verbose) — same task IDs, updated shell commands
- GDB replaced by **LLDB** (ships with LLVM) for debugging, or VS Code's native
  MSVC debugger via the C/C++ extension

The `PATH` inside MSYS2 will need to include the VS Build Tools and LLVM `bin/`
directories. This is handled by sourcing a small helper or by extending
`MSYS2_PATH_TYPE=inherit` plus adding them to the Windows PATH.

### Quick start (default install, MSYS2 bash)

For a default LLVM + VS Build Tools install, run:

```bash
source tools/windows/eigend-msvc-env.sh
```

This helper:
- Finds Build Tools via `vcvars64.bat` location (with default path fallbacks)
- Builds MSVC/Windows SDK environment directly from installed folder layout (`INCLUDE`, `LIB`, `LIBPATH`, etc.)
- Adds LLVM `bin` to `PATH` (default `C:\Program Files\LLVM\bin`)

It does **not** run `cmd.exe` to import a batch-script environment, so it avoids
the MSYS2/VS Code pipe hangs seen with `VsDevCmd`-based approaches.

After sourcing, validate tool discovery:

```bash
which clang-cl
which lld-link
```

If your install is non-default, set overrides before sourcing:

```bash
export EIGEND_VCVARS64='/c/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Auxiliary/Build/vcvars64.bat'
export EIGEND_WINSDK_ROOT='/c/Program Files (x86)/Windows Kits/10'  # optional
export EIGEND_LLVM_BIN_WIN='C:\Program Files\LLVM\bin'
source tools/windows/eigend-msvc-env.sh
```

To auto-load for every MSYS2 session, add this to `~/.bashrc`:

```bash
if [[ -f /c/msys64/home/$USER/projects/EigenD/tools/windows/eigend-msvc-env.sh ]]; then
  source /c/msys64/home/$USER/projects/EigenD/tools/windows/eigend-msvc-env.sh
fi
```

### What developers will NOT need

- Visual Studio IDE
- `vcvars64.bat` in a CMD or PowerShell window
- The MinGW-w64 GCC toolchain (can be retained alongside, but not required)

---

## SCons Integration Changes Required

The current build system has three environment classes for Windows:

```
windows_tools.PiWindowsEnvironment   ← legacy MSVC (maintained but not primary)
[new] clangcl_tools.PiClangClEnvironment  ← target for this branch
```

The new environment class needs to handle:

### Compiler and linker selection

`clang-cl` uses MSVC-style flags, so `clangcl_tools.py` will extend
`PiGenericEnvironment` (or possibly a thin `PiWindowsEnvironment` subset) and
configure:

```python
env['CC']  = 'clang-cl'
env['CXX'] = 'clang-cl'
env['AR']  = 'llvm-lib'
env['LINK'] = 'lld-link'  # or 'link.exe' from VS Build Tools
```

MSVC-style flags replace GCC-style flags (`/EHsc` not `-fexceptions`, etc.).

### DLL / import library handling

Unlike MinGW, `clang-cl`/`lld-link` uses MSVC conventions:
- Import libraries are `.lib` files (not `.dll.a`)
- DEF files are passed via `/DEF:` (same as MSVC, not as a bare source file like MinGW)
- `__declspec(dllexport)` / `__declspec(dllimport)` are used (same as the existing
  `DECLSPEC` macros in the EigenD codebase — these already target MSVC ABI)

The `LIBMAPPER` mechanism (resolving `PILIBS` to absolute paths) will need updating:
- It currently maps to `.dll.a` import libraries (MinGW)
- For `clang-cl` it should map to `.lib` import libraries

### SHLIB action (`SHLINKCOM`)

The MinGW investigation revealed that SCons4's `mingw.py` uses a Python generator for
`SHLINKCOM`, which required patching (`mingw.py` — see `implement_mingw.md`). The
`msvc.py` tool uses a standard string action, so `Append(SHLINKCOM=...)` works as
expected. `clangcl_tools.py` should therefore be able to use SCons's `msvc` tool as
a base and override `CC`/`CXX`/`LINK` to point at `clang-cl`/`lld-link`.

### `select_tools.py` dispatch

A new build toolchain selector:

```python
# tools/select_tools.py  (win32 block)
def win32():
    toolchain = os.environ.get('BUILD_TOOLCHAIN', 'clangcl')
    if toolchain == 'msvc':
        return windows_tools.PiWindowsEnvironment()
    else:
        return clangcl_tools.PiClangClEnvironment()
```


---

## Things to Check / Open Questions

### USB: libusb linking 

With `clang-cl`:
- `clang-cl` links against MSVC-ABI `.lib` files
- The official libusb Windows release ships a `libusb-1.0.lib` (MSVC) alongside
  the DLL — this is the one to use
- Headers are the same; the MinGW `#include <libusb.h>` vs `#include <libusb-1.0/libusb.h>` path difference may need a SConscript tweak
- `pic_usb_libusb.cpp` will need `<winsock2.h>` added before `<libusb.h>` (same
  platform issue seen in `mingw-w64`; not yet applied in this branch)

**Action:** Obtain official libusb Windows binary release; confirm `.lib` file is
present; test link under `clang-cl`.

### JUCE support

JUCE 8 explicitly supports `clang-cl` on Windows. The CI matrix for JUCE itself tests
with Clang for Windows. Expected issues are:

- **AppConfig.h / Projucer**: JUCE module path and config headers may need verifying
  for the `clang-cl` + VS Build Tools combination
- **Windows SDK version**: `lld-link` needs to find the correct Windows SDK. The
  VS Build Tools installer sets up the necessary environment variables; these must be
  visible from within MSYS2 (via `MSYS2_PATH_TYPE=inherit` or manual `PATH` export)
- **Direct2D / DirectComposition**: These are the very features that blocked MinGW.
  They require MSVC headers (`d2d1.h`, `dcomp.h`) from the Windows SDK — VS Build
  Tools provides these

### Anonymous-namespace `__declspec` (arranger)

The `mingw-w64` branch removed `PIARRANGER_DECLSPEC_CLASS` from `grid_t` and
`cell_t` in `arranger_model.cpp` / `arranger_view.cpp`. GCC 16 rejects
`dllexport` on types in anonymous namespaces (internal linkage); MSVC silently
accepts it, but GCC is correct.

**This fix is valid regardless of compiler and should be applied in this branch.**

### Inline assembly in libsamplerate (`float_cast.h`)

The MSVC `_asm` block in `float_cast.h` (active when `HAVE_LRINT` is not defined) is
only valid for 32-bit MSVC. For 64-bit `clang-cl`, `HAVE_LRINT` and `HAVE_LRINTF`
should be defined to `1` in `lib_samplerate/src/win32/config.h`. This is needed
here independently — the same issue was also addressed in the `mingw-w64` branch.

### `#pragma warning` and MSVC-isms

`clang-cl` accepts most `#pragma warning(disable: NNNN)` directives (it maps MSVC
warning numbers to Clang warnings where possible). `_MSC_VER` **is** defined when
compiling with `clang-cl`, so any `#ifdef _MSC_VER` guards behave as expected.

### `COMPILER_IS_GCC` and other compiler-detection macros

`clang-cl` does **not** define `__GNUC__`. Any `__GNUC__`-conditional code (e.g.
`COMPILER_IS_GCC` in `lib_samplerate/src/win32/config.h`) will correctly evaluate
to 0 under `clang-cl`.

### winsock2 / include order

`pic_usb_libusb.cpp` will need `<winsock2.h>` included before `<libusb.h>` under
`PI_WINDOWS`. libusb's Windows header pulls in `windows.h` which beats
`Ws2tcpip.h` to the include guard. This is a platform issue, not compiler-specific;
it is not yet applied in this branch.

### Platform fixes to apply (from `mingw-w64` reference)

The `mingw-w64` branch identified several platform-level issues that are independent
of the compiler choice. None of these are in this branch yet. They should be applied
as part of the initial `clang4win` bring-up:

| Fix | File(s) | Notes |
|-----|---------|-------|
| `<winsock2.h>` before `<libusb.h>` | `picross/src/pic_usb_libusb.cpp` | Include order; platform, not compiler |
| `GetWindowLongPtr` / `GWLP_HINSTANCE` | `picross/src/pic_winloop.cpp` | 64-bit Windows API |
| `ws2_32` in LIBS | `piagent/src/SConscript` | Library name is the same for clang-cl |
| Remove `DECLSPEC_CLASS` on anonymous types | `plg_arranger/src/arranger_*.cpp` | Correct regardless of compiler |
| `HAVE_LRINT` / `HAVE_LRINTF` = 1 | `lib_samplerate/src/win32/config.h` | Avoids dead MSVC `_asm` path |

The MinGW-specific SCons work (`mingw.py` LIBMAPPER patch, `deffile=` workaround,
`PiMingwEnvironment`) is not applicable here and should not be carried over.

---

## ARM Windows Notes

### Running x64 builds on ARM Windows

x64 EigenD binaries run under Windows 11's x64 emulation layer on ARM hardware
(e.g. Snapdragon X, Apple Silicon + Parallels). No build changes required.

### Cross-compiling x64 from an ARM64 Windows host

This is a useful setup for developers on Apple Silicon Macs running Windows ARM in
Parallels — the ARM64 VM runs at full native speed and cross-compiles x64 output:

```bash
clang-cl --target=x86_64-pc-windows-msvc ...
```

VS Build Tools supports this via the optional component
**"MSVC v143 - VS 2022 C++ x64/x86 build tools for ARM64"** (inside the
"Desktop development with C++" workload). The Windows SDK ships both ARM64 and x64
lib trees so no additional SDK install is needed.

SCons will need the correct `--target` flag forwarded to `clang-cl` and the
x64 SDK lib path selected — this is a `clangcl_tools.py` concern when the time comes.

### Native ARM64 builds

JUCE 8 and LLVM both support `arm64-pc-windows-msvc`. The additional VS Build Tools
component is **"MSVC v143 - VS 2022 C++ ARM64 build tools"**.

The USB layer is the key dependency: libusb's official Windows binary release includes
an ARM64 `.lib`, and libusb already runs on ARM Linux with EigenD hardware. Native
ARM64 Windows is therefore viable once the clang-cl x64 build is stable.

---

## Next Steps

- [X] Install VS Build Tools 2022 + LLVM; verify `clang-cl --version` from MSYS2 bash
- [X] Wire up `PATH` / environment so `lld-link` can find MSVC CRT and Windows SDK
- [ ] Create `tools/clangcl_tools.py` (extend or fork `windows_tools.py`)
- [ ] Update `tools/select_tools.py` to dispatch on `BUILD_TOOLCHAIN=clangcl`
- [ ] Build `picross` as first target; confirm DLL + import lib produced correctly
- [ ] Build `lib_samplerate` with DEF file via `/DEF:` (revert `deffile=` if needed)
- [ ] Build `piagent`, `piw`, `plg_*` non-JUCE plugins
- [ ] Build a JUCE target (`lib_juce`) — this is the key gate
- [ ] Build `app_stage` / `app_workbench` end-to-end
