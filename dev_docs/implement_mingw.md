# MinGW-w64 SCons Integration: Implementation Reference

> **Status: Phase A (active development, untested)**
> This document is for developers working on or debugging the MinGW Windows
> build system. For end-user build instructions, see `build_mingw.md`.

---

## SCons Project Overview

EigenD uses a custom SCons 4.x wrapper, not plain CMake or make. Understanding the
wrapper layer is essential for diagnosing Windows build issues.

### Entry points

```
Makefile
  └── calls: python $(TOOLS)/packages/SCons4/bin/scons -f tools/SConstruct
                  tools/SConstruct
                    └── import select_tools
                          └── select_tools.select()
                                └── returns a PiXxxEnvironment instance
                                      └── master_env.Initialise()
                                      └── walks all SConscript files
                                      └── master_env.Finalise()
```

All `SConscript` files receive `master_env` as `env`. They call methods like
`env.PiSharedLibrary(...)`, `env.PiProgram(...)`, `env.PiPipBinding(...)` which are
defined on the environment class.

### Platform dispatch: `tools/select_tools.py`

```python
def select():
    if sys.platform in globals():
        return globals()[sys.platform]()
```

Platform → function:
- `darwin` → `posix()` → `posix_Darwin_arm64()` / `posix_Darwin_x86_64()` → `darwin_tools.PiDarwinEnvironment`
- `linux` → `posix()` → `posix_Linux_x86_64()` etc. → `linux_tools.PiLinuxEnvironment`
- `win32` → `win32()` → **new: `mingw_tools.PiMingwEnvironment`** (default) or `windows_tools.PiWindowsEnvironment` if `BUILD_TOOLCHAIN=msvc`

`sys.platform` is `'win32'` on all Windows builds, including from MSYS2.

### Environment class hierarchy

```
SCons.Environment.Environment
  └── generic_tools.PiGenericEnvironment   (platform-neutral base)
        ├── unix_tools.PiUnixEnvironment   (Unix linker/LIBMAPPER setup)
        │     ├── darwin_tools.PiDarwinEnvironment
        │     └── linux_tools.PiLinuxEnvironment
        ├── mingw_tools.PiMingwEnvironment  ← NEW (Phase A)
        └── windows_tools.PiWindowsEnvironment  (legacy MSVC)
```

`PiMingwEnvironment` extends `PiGenericEnvironment` directly (not `PiUnixEnvironment`)
because the Unix environment adds RPATH flags (`-Wl,-rpath,...`) that are meaningless
on Windows. The LIBMAPPER wiring from `PiUnixEnvironment` is replicated manually:

```python
self.Append(SHLINKCOM=' $LIBMAPPER')
self.Append(LINKCOM=' $LIBMAPPER')
```

---

## How LIBMAPPER Works

`LIBMAPPER` is a SCons substitution variable set to a Python function
(`PiGenericEnvironment.libmapper`). It resolves the list of `PILIBS` into linker
arguments at link time.

When a target specifies `libraries=['foo', 'bar']`:
1. The environment appends them to `PILIBS`
2. At link time, `$LIBMAPPER` expands by calling `libmapper()`
3. For each library: if EigenD built it (registered via `addlibname`), emit the absolute
   path to its import lib; otherwise emit `-lfoo`
4. This ensures correct link ordering and avoids `-l` name clashes with system libs

The function is appended to `SHLINKCOM` (for DLLs) and `LINKCOM` (for executables).
This is the same pattern used by `PiUnixEnvironment`. The MSVC environment instead
appended to `SHLINK`/`LINK` (the program name strings) — that is specific to how
SCons handles the MSVC tool and does NOT work for MinGW.

---

## Key Platform Flags

```python
IS_WINDOWS = True   # Set for both MinGW and MSVC paths
IS_MINGW   = True   # Set only for MinGW; use this to distinguish from MSVC
IS_LINUX   = False
IS_MACOSX  = False
```

All SConscripts that previously checked `env['IS_WINDOWS']` for MSVC-specific flags
(e.g. `/arch:SSE2`, `WS2_32.Lib`, `/nodefaultlib:libcmt.lib`) must now check
`env['IS_MINGW']` first and provide GCC-equivalent flags.

Files updated in Phase A:

| File | Change |
|------|--------|
| `lib_juce/SConscript` | Added `IS_MINGW` branch with GCC flags + `-l` libs |
| `lib_lo/SConscript` | `ws2_32` via `-l` for MinGW instead of `WS2_32.Lib` |
| `app_stage/SConscript` | MinGW GCC flags replacing MSVC flags |
| `app_workbench/SConscript` | MinGW GCC flags replacing MSVC flags |

Any SConscript that adds Windows-specific compiler or linker flags needs this split.
Grep for `IS_WINDOWS` to find others that may need updating when encountering build errors.

---

## Windows ARM64

The current build system targets **x86_64 only**. This section documents the options
if native ARM64 support is ever needed.

### Near-term: x86_64 under Prism emulation

Windows 11 on ARM64 hardware (Snapdragon X Elite, Copilot+ PCs) ships with Prism,
Microsoft's x86_64 binary translation layer. x86_64 EigenD binaries run under Prism
transparently. No build changes are required. The `-msse2` flag in `mingw_tools.py`
is fine — Prism translates SSE2 instructions to the equivalent NEON operations.

This is the practical answer for the foreseeable future.

### Future: native ARM64

If native ARM64 binaries are required, three options exist:

**Option 1: MSYS2 CLANGARM64 (recommended if ARM64 is pursued)**
MSYS2 provides a `CLANGARM64` environment that runs natively on ARM64 Windows using
Clang as the compiler. Package prefix: `mingw-w64-clang-aarch64-*`.
- New `select_tools.py` dispatch function needed (detecting ARM64 vs x86_64)
- New `clangarm64_tools.py` environment class, similar to `mingw_tools.py`
- Replace `-msse2` with appropriate ARM64 CCFLAGS (no equivalent; use `-O2` alone,
  NEON is always available on ARM64)
- JUCE 8 supports ARM64 Windows with Clang — this is the most viable path
- `sys.platform` is still `'win32'` on ARM64 Windows; architecture detection needs
  `platform.machine()` which returns `'ARM64'` on ARM64 Windows

**Option 2: `aarch64-w64-mingw32-gcc` cross-toolchain**
A GCC-based cross-toolchain for Windows ARM64 exists in some MinGW-w64 distributions.
It is significantly less mature than x86_64, and JUCE has limited ARM64/GCC/Windows
testing. Not recommended.

**Option 3: MSVC ARM64 (BUILD_TOOLCHAIN=msvc path)**
Visual Studio 2022 supports ARM64 targets natively. The existing `windows_tools.py`
MSVC path would need the `TARGET_ARCH='x86'` changed to `'arm64'`. This is the most
official path but reintroduces all the MSVC setup complexity.

### What would need changing for CLANGARM64

| Component | Change required |
|-----------|----------------|
| `select_tools.py` | Detect `platform.machine() == 'ARM64'` and dispatch to CLANGARM64 |
| New `clangarm64_tools.py` | Mirror `mingw_tools.py`, use `clang`/`clang++`, ARM64 flags |
| `mingw_tools.py` CCFLAGS | `-msse2` is x86-only; remove or conditionalize |
| `lib_juce/SConscript` | Add `IS_CLANGARM64` branch (remove `-msse2`, add ARM64 JUCE flags) |
| `app_stage`, `app_workbench` | Same — remove `-msse2` for ARM64 |
| MSYS2 shell | Use CLANGARM64 shell (not UCRT64) |
| Package prefix | `mingw-w64-clang-aarch64-*` instead of `mingw-w64-ucrt-x86_64-*` |

---

## Python Extension Modules (.pyd)

Python extension modules (compiled via `PiPipBinding`) produce `.pyd` files on Windows
regardless of compiler. This is a Windows convention.

SCons key variables:
```python
PI_MODPREFIX = ''
PI_MODSUFFIX = '.pyd'
PI_MODLINKFLAGS = '$SHLINKFLAGS'   # DLL link flags
```

The build uses `SharedLibrary(..., SHLIBPREFIX='', SHLIBSUFFIX='.pyd', ...)` for
Python bindings. This is handled in `PiGenericEnvironment.PiPipBinding`.

---

## Python Detection: `tools/detect.py`

`detect.py` is run by SCons at startup via `PiGenericEnvironment.__getpython()` to
discover Python headers, libraries, and prefix. It prints a semicolon-separated string.

On Windows (`sys.platform == 'win32'`) it calls `do_win32()`:
```python
def do_win32():
    incpath = sysconfig.get_path('include')   # C:\Python314\include
    libpath = os.path.join(sys.prefix, 'libs') # C:\Python314\libs
    lib = 'python' + cv['VERSION']             # 'python314'
    return (executable, incpath, libpath, lib, '', sys.prefix)
```

**Bug fixed in Phase A:** The original code hardcoded `'Python26'` as the library name
(Python 2.6 era). This would have caused a linker error with Python 3.14.

**Cross-compilation limitation:** When cross-compiling from Linux/macOS,
`sys.platform != 'win32'`, so `detect.py` follows the non-Windows path and discovers
host Python headers instead of Windows Python headers. The cross-compile build
(Phase C) will need to override `CPPPATH` and `LIBPATH` for Python manually,
or extend `detect.py` to accept an explicit Windows Python root via environment variable.

---

## Shared Library Output: MinGW vs MSVC

MinGW and MSVC produce different sets of files from `SharedLibrary()`:

| File | MSVC | MinGW-w64 |
|------|------|-----------|
| DLL | `foo.dll` | `foo.dll` |
| Import library | `foo.lib` | `libfoo.dll.a` |
| PDB (debug) | `foo.pdb` | N/A (debug in `.dll` via DWARF/CTF) |
| Export file | `foo.exp` | N/A |

The old `PiWindowsEnvironment.PiSharedLibrary` expected four outputs: `[dll, pdb, lib, exp]`.
`PiMingwEnvironment.PiSharedLibrary` expects `[dll, dll.a]`.

SCons' MinGW tool sets `SHLIBSUFFIX='.dll'` and the import library suffix to `.dll.a`.
The `lib_result` from `env.SharedLibrary()` is typically `[foo.dll, libfoo.dll.a]`.

If the import library is not produced (some MinGW configurations), `lib_result[0]`
(the DLL itself) is used as the link target for dependents. This is workable but
less clean than having a dedicated import library.

---

## JUCE on Windows with MinGW — BLOCKED

> **2026-05-05: This section documents why the MinGW path cannot build JUCE 8.x
> and what the forward path is. The MinGW build covers all non-JUCE components
> successfully. A separate branch will investigate clang-cl as the JUCE compiler.**

### Hard blocker: JUCE 8 explicitly rejects MinGW

`lib_juce/juce/modules/juce_core/system/juce_TargetPlatform.h` contains:

```cpp
#ifdef __MINGW32__
    #error "MinGW is not supported. Please use an alternative compiler."
#endif
```

This is not a soft warning — it is a hard `#error` that terminates compilation of
any translation unit that includes JUCE headers. `__MINGW32__` is defined by all
MinGW-w64 GCC variants (including UCRT64).

### Root cause: `__uuidof` / `__declspec(uuid)` are MSVC-only

The real incompatibility behind the guard is that JUCE 8's Windows renderer
(Direct2D, DirectComposition) and COM integration rely on:

- `__declspec(uuid("..."))` — attaches a GUID to a type
- `__uuidof(T)` — retrieves that GUID at compile time

These are MSVC-specific language extensions. GCC ignores the `uuid` attribute
(emitting a warning) and has no `__uuidof`. Any call to `__uuidof` produces an
undefined reference at link time. UCRT64 ships the required headers (`d2d1.h`,
`dwrite.h`, `dcomp.h`) but the extension language required to use them is absent.

Confirmed by test:

```bash
# GCC UCRT64 — fails:
echo '#include <windows.h>
struct __declspec(uuid("12345678-1234-1234-1234-123456789abc")) Foo {};
int main() { auto x = __uuidof(Foo); return 0; }' | g++ -x c++ - -o /tmp/test.exe
# → warning: uuid attribute ignored
# → undefined reference to `_GUID const& __mingw_uuidof<Foo>()'
```

### Scope of impact

Components blocked by JUCE incompatibility:

| Component | Uses JUCE | Status |
|-----------|-----------|--------|
| `plg_audio` | Yes (`audio_juce.cpp`) | Blocked |
| `app_stage` | Yes (full JUCE GUI) | Blocked |
| `app_workbench` | Yes (full JUCE GUI) | Blocked |
| `app_eigend2` | Yes (JUCE audio backend) | Blocked |
| All `plg_*` others | No | Build successfully |
| `picross`, `piagent`, `piw` | No | Build successfully |
| `lib_samplerate`, `lib_lo` etc. | No | Build successfully |

### Forward path: clang-cl with VS Build Tools

`clang-cl` is a Clang front-end that emulates the MSVC compiler interface and ABI.
It supports `__declspec(uuid)` and `__uuidof`, satisfying JUCE's requirements, while
using Clang's GCC-compatible dialect for non-Windows code.

Requirements:
- **VS Build Tools** (free from Microsoft): provides MSVC CRT headers, `link.exe`,
  `lib.exe`. `clang-cl` cannot function without these.
- **LLVM for Windows** (from llvm.org): provides `clang-cl.exe`.
- SCons `msvc` tool scaffolding as the base (sets up `LIB`, `INCLUDE`, `PATH`
  from a VS installation), with `CC`/`CXX` overridden to `clang-cl`.

This will be investigated in a dedicated branch. See `build_mingw.md` for the
recommended next steps and reference links.

---

## Packaging Stubs (Phase B)

`PiMingwEnvironment.Finalise()` currently calls `doenv()` (generates `env.sh`) and
returns. Packaging is deliberately omitted for Phase A.

When Phase B is implemented:
1. `make_package(package_name)` should call an NSIS-based packager
2. `Finalise()` should call `make_package` for each entry in `self.shared.packages`
3. The existing NSIS infrastructure in `windows_tools.py` (`make_setup_nsis`) can be
   ported — it generates `.nsi` scripts and invokes `makensis.exe`
4. The installer must copy MinGW runtime DLLs from `C:\msys64\ucrt64\bin\`

State tracked in `self.shared`:
- `packages`: list of package names (populated by `PiPackageDescription` in SConscripts)
- `package_init`: list of `(package, program, as_user, order)` post-install actions
- `shortcuts`: dict of `package → [(name, exe_path)]` Start Menu shortcuts
- `merge_modules`: list of `.msm` paths (MSVC merge modules; not applicable to NSIS)

---

## Cross-Compilation Design (Phase C)

The goal is to build Windows binaries from a Linux/macOS CI runner.

**Toolchain:** `x86_64-w64-mingw32-` prefix (installed via `brew install mingw-w64` or
`apt-get install gcc-mingw-w64-x86-64`).

**SCons dispatch:** When `MINGW_PREFIX` is set in the environment, `select_tools.win32()`
passes it to `PiMingwEnvironment(cross_prefix=...)`. The environment then sets
`CC`, `CXX`, `AR`, `RANLIB`, `RC` explicitly instead of calling `Tool('mingw')`.

**The Python detection problem:** `detect.py` runs on the host and tries to auto-detect
Python headers. On a Linux host, this finds Linux Python — wrong for a Windows build.

Options for Phase C:
1. Add a `MINGW_PYTHON_ROOT` environment variable that, when set, bypasses `detect.py`
   and directly sets `CPPPATH` and `LIBPATH` to the Windows Python directory (extracted
   from a python.org Windows installer on the host).
2. Extend `detect.py` to detect cross-compile mode and print a placeholder that the
   environment then overrides.
3. Use the Python stable ABI (`python3.lib` / `python3-embed`) which is simpler to
   mock for cross-compilation.

For GitHub Actions, the Windows Python installer can be extracted with `msiexec` (on a
Windows runner) or with `wine msiexec` / `innoextract` on Linux, providing the
`include/` and `libs/` directories needed for compilation.

---

## Phase A Status (2026-05-05)

### Completed

All non-JUCE components build and link successfully on Windows UCRT64 / GCC 16.1.0.
Issues encountered and resolved:

| Fix | File(s) |
|-----|---------|
| `ssize_t` redefinition conflict with UCRT | `piagent/src/pia_udpnet_windows.cpp` |
| `get_global_resources()` missing on Windows/Linux | `picross/src/pic_resources.cpp` |
| `DWORD` → `SIZE_T` for working set functions | `picross/src/pic_thread_win32.cpp` |
| Signed/unsigned comparison in `InterlockedCompareExchange` | `picross/pic_atomic.h` |
| `sleep()` → `pic_microsleep()` (cross-platform, correct units) | `picross/src/pic_usb_libusb.cpp` |
| `GWL_HINSTANCE` → `GWLP_HINSTANCE` + `GetWindowLongPtr` (64-bit) | `picross/src/pic_winloop.cpp` |
| `#pragma warning` guarded with `#ifdef _MSC_VER` | `lib_samplerate/src/win32/config.h` |
| `HAVE_LRINT`/`HAVE_LRINTF` enabled (MinGW has C99 versions) | `lib_samplerate/src/win32/config.h` |
| `libsamplerate.def` passed via `deffile=` not MSVC `/DEF:` | `lib_samplerate/SConscript` |
| `WS2_32.Lib` → `ws2_32` via `LIBS` | `piagent/src/SConscript` |
| `user32`, `gdi32` added for `pic_winloop` symbols | `picross/src/SConscript` |
| `DECLSPEC_CLASS` removed from anonymous-namespace structs | `plg_arranger/src/arranger_model.cpp`, `arranger_view.cpp` |
| USB: created shared `pic_usb_libusb.cpp` for Linux+Windows | `picross/src/pic_usb_libusb.cpp` |
| USB: deleted `pic_usb_linux.cpp` (superseded) | deleted |
| USB: SConscript updated; Windows links `usb-1.0` | `picross/src/SConscript` |
| LIBMAPPER not called in shlib display string (VS Code open-with dialog) | `tools/packages/SCons4/SCons/Tool/mingw.py` |
| `winsock2.h` included before `libusb.h` to fix include order warning | `picross/src/pic_usb_libusb.cpp` |

### Blocked: JUCE components

`plg_audio`, `app_stage`, `app_workbench`, `app_eigend2` cannot build with MinGW.
See the **JUCE on Windows with MinGW — BLOCKED** section above for full details.

### Next branch: clang-cl investigation

The `investigate-clang-cl` branch will explore:
1. Installing VS Build Tools + LLVM `clang-cl`
2. A new `clangcl_tools.py` SCons environment (or extending `windows_tools.py`)
3. Building the JUCE components with `clang-cl` while keeping MinGW for the rest

Reference: https://clang.llvm.org/docs/UsersManual.html#clang-cl

---

## Debugging SCons Build Issues

### See the full compiler command line

```bash
make VERBOSE="PI_VERBOSE=1"
# or
PI_VERBOSE=1 make
```

The `PI_VERBOSE` env var suppresses SCons' abbreviated output (`print_cmd` in
`generic_tools.py`). Without it, only target names are printed.

### Dump the SCons environment

Add to `tools/SConstruct` temporarily:
```python
print(master_env.Dump())
```

This prints all SCons variables, useful for checking that `SHLINKCOM`, `CC`, `CPPPATH`,
`LIBPATH`, etc. are set as expected.

### Single-threaded build

```bash
make single
```

This passes `-j1` to SCons, giving sequential output that's much easier to read
when diagnosing errors.

### Check which compiler is being invoked

```bash
PI_VERBOSE=1 make 2>&1 | grep "^gcc\|^g++\|^x86_64"
```

### SCons dependency graph

```bash
python3 tools/packages/SCons4/bin/scons -f tools/SConstruct --tree=status lib_juce
```

Shows the dependency tree for a specific target, useful for understanding why something
is or isn't being rebuilt.
