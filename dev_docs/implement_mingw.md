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

## JUCE on Windows with MinGW

JUCE 8.x compiles on MinGW-w64 with some caveats:

**Module extension:** `.cpp` (same as Linux). macOS uses `.mm` (Objective-C++).
This is already handled in `lib_juce/SConscript`.

**System libraries required:** `ws2_32 kernel32 user32 gdi32 winspool comdlg32 advapi32
shell32 ole32 oleaut32 uuid wininet shlwapi version imm32 winmm dbghelp`
Added via `-l` flags in the `IS_MINGW` branch of `lib_juce/SConscript`.

**AppConfig.h:** JUCE requires this configuration header in the include path.
Its absence will produce `#include <AppConfig.h>` not-found errors. The file must
exist in `lib_juce/` (it is project-specific JUCE configuration).

**Known JUCE/MinGW compatibility issues to watch for:**
- `juce_audio_devices`: uses COM for audio device enumeration. MinGW-w64 ships
  COM headers (`objbase.h`, `mmdeviceapi.h`) but they may have gaps vs MSVC SDK.
  Expect potential compile errors here until tested.
- `juce_gui_basics`: uses Win32 GDI extensively; this is well-supported in MinGW-w64.
- `juce_core`: uses `windows.h`, `winsock2.h` — well-supported.
- Exception handling: JUCE assumes SEH on Windows 64-bit. UCRT64's GCC uses SEH
  (`-fexceptions` with SEH). This should be compatible, but stack unwinding through
  Windows callbacks (e.g. audio callbacks) should be tested carefully.

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

## What Still Needs Doing (Phase A Gaps)

Before Phase A can be declared working, the following need testing and likely fixing
on an actual Windows machine with MSYS2 UCRT64:

1. **Verify `Tool('mingw')` output format:** Confirm `env.SharedLibrary()` produces
   `[foo.dll, libfoo.dll.a]` (two elements). If not, `PiMingwEnvironment.PiSharedLibrary`
   needs its index adjusted.

2. **Python linking:** Confirm `-lpython314` with `-LC:/Python314/libs` links successfully.
   If MinGW's ld rejects the MSVC `.lib`, use `gendef` + `dlltool` to create `.dll.a`
   (see `build_mingw.md` troubleshooting section).

3. **SHLINKCOM / LINKCOM appending:** Verify that appending `' $LIBMAPPER'` to the
   command string works correctly with the MinGW tool's link commands. SCons' MinGW
   tool may define `SHLINKCOM` differently from the default. Check with `env.Dump()`.

4. **JUCE compilation:** `juce_audio_devices` is the most likely source of
   MinGW-specific compilation failures due to COM interface headers.

5. **`.pyd` extension modules:** Verify that `PiPipBinding` produces `.pyd` files that
   Python can import. The suffix is set, but the DLL entry point (`PyInit_modulename`)
   must also be correctly exported — check `__declspec(dllexport)` is being emitted
   (it comes from `exports_template` in `generic_tools.py`, which already handles
   `_WIN32` correctly for both MSVC and MinGW).

6. **`guicon.cpp` (app_stage):** This file handles Windows console allocation for GUI
   apps. Verify it compiles under MinGW.

7. **Any remaining SConscripts with MSVC-only `IS_WINDOWS` flags:** Grep for
   `IS_WINDOWS` in all SConscripts to find any not yet updated:
   ```bash
   grep -rn "IS_WINDOWS" --include="SConscript" .
   ```

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
