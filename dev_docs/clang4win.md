# EigenD Windows Build: clang-cl

> **Status: Active development (branch `clang4win`)**
> Last updated: 2026-05-05

---

## Overview: Why clang-cl?

The MinGW-w64 investigation established that GCC on Windows can build all EigenD
non-GUI components but hits a hard blocker with JUCE 8:

```cpp
// juce_core/system/juce_TargetPlatform.h
#ifdef __MINGW32__
    #error "MinGW is not supported. Please use an alternative compiler."
#endif
```

The underlying reason: JUCE 8 uses COM interfaces via `__declspec(uuid("..."))` and
`__uuidof(T)` — MSVC language extensions that GCC does not implement.

**`clang-cl`** is a Clang front-end mode that:
- Accepts MSVC-compatible command-line syntax (`/O2`, `/EHsc`, ...)
- Implements `__declspec(uuid)`, `__uuidof`, `__forceinline`, and other MSVC extensions
- Links against the MSVC CRT, not the MinGW CRT
- Is approved and actively tested by the JUCE team on Windows
- Is free, open source, ships with the LLVM project

---

## Developer Prerequisites

Install the following **in order**. All are free.

### 1. MSYS2

Download and install from https://www.msys2.org

After install, open the **MSYS2 UCRT64** terminal and update:

```bash
pacman -Syu
pacman -S make git p7zip
```

> `p7zip` is required to unpack the vendored libusb archive on first build.

### 2. Python 3.14 (python.org)

Download the 64-bit Windows installer from https://www.python.org/downloads/windows/

Install to the default location: `C:\Python314\`

Do **not** use the MSYS2 Python or the Microsoft Store Python -- the build system
requires the python.org CPython runtime and its `libs/python314.lib`.

### 3. VS Build Tools 2022

Download from https://aka.ms/vs/17/release/vs_BuildTools.exe

Select the workload: **Desktop development with C++**

This provides:
- MSVC CRT headers and `*.lib` files
- Windows SDK headers and libraries
- `link.exe`, `lib.exe`, `editbin.exe`

Default install path: `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools`

### 4. LLVM for Windows

Download the latest LLVM Windows installer (`.exe`) from:
https://github.com/llvm/llvm-project/releases

Select **Add LLVM to the system PATH for all users** during install.

Default install path: `C:\Program Files\LLVM`

This provides `clang-cl.exe`, `lld-link.exe`, `llvm-lib.exe`, and `lldb.exe`.

### 5. VS Code (optional but recommended)

https://code.visualstudio.com

---

## Environment Setup (MSYS2 bash)

Before building, source the environment helper so the shell can see MSVC CRT/SDK
headers and the LLVM tools:

```bash
cd /home/$USER/projects/EigenD
source tools/windows/eigend-msvc-env.sh
```

This script:
- Locates VS Build Tools via the default install path (overrides available)
- Exports `INCLUDE`, `LIB`, `LIBPATH` from the installed folder layout
- Adds `C:\Program Files\LLVM\bin` to `PATH`

Validate after sourcing:

```bash
which clang-cl      # /c/Program Files/LLVM/bin/clang-cl
which lld-link      # same location
clang-cl --version
```

If your install paths differ from the defaults, set overrides before sourcing:

```bash
export EIGEND_VCVARS64='/c/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Auxiliary/Build/vcvars64.bat'
export EIGEND_WINSDK_ROOT='/c/Program Files (x86)/Windows Kits/10'
export EIGEND_LLVM_BIN_WIN='C:\Program Files\LLVM\bin'
source tools/windows/eigend-msvc-env.sh
```

To auto-load for every MSYS2 session, add the source call to `~/.bashrc`.

---

## Building

```bash
cd /home/$USER/projects/EigenD
make dev-setup      # one-time: creates .venv_dev
make                # builds all targets (8 parallel jobs by default)
```

On Windows, `make` automatically unpacks the vendored libusb archive before invoking
SCons. See [libusb for Windows](#libusb-for-windows) below.

Other useful targets:

```bash
make clean               # remove build artifacts
make picross             # build a single module
make VERBOSE=PI_VERBOSE=1  # verbose SCons output
make JOBS=2 # use 2 cores, 8 default
```

---

## libusb for Windows

### How it works

The USB layer on Linux and Windows both use **libusb-1.0**
(`picross/src/pic_usb_libusb.cpp`). The Windows-specific WinUSB/openwindev driver
has been retired.

The official libusb Windows binary release is vendored in the repository at:

```
resources/libusb-1.0.29.7z
```

On first `make` (and whenever the archive is newer than the sentinel), it is
automatically unpacked into `tmp/libusb/`:

```
tmp/libusb/
  include/
    libusb-1.0/
      libusb.h          <- headers for compilation
  lib/
    libusb-1.0.lib      <- MSVC import library (VS2022/MS64/dll)
    libusb-1.0.dll      <- runtime DLL
```

`tools/clangcl_tools.py` adds these paths automatically:
- `/I tmp/libusb/include` to compile flags
- `/LIBPATH: tmp/libusb/lib` to link flags

You can also run the unpack step manually:

```bash
make libusb-setup
```

### Updating libusb

If a newer libusb release is needed:

1. Download the new `.7z` from https://github.com/libusb/libusb/releases
   (choose `libusb-X.Y.Z-binaries.7z`)

2. Replace the vendored archive:
   ```bash
   cp libusb-X.Y.Z-binaries.7z resources/libusb-X.Y.Z.7z
   ```

3. Update the filename in `Makefile`:
   ```makefile
   LIBUSB_ARCHIVE = resources/libusb-X.Y.Z.7z
   ```

4. Delete the old unpacked tree and re-unpack:
   ```bash
   rm -rf tmp/libusb
   make libusb-setup
   ```

5. Verify the expected files are present:
   ```bash
   ls tmp/libusb/include/libusb-1.0/libusb.h
   ls tmp/libusb/lib/libusb-1.0.lib
   ls tmp/libusb/lib/libusb-1.0.dll
   ```

The archive must contain `VS2022/MS64/dll/libusb-1.0.lib` and `.dll`. If the folder
layout in a new release changes, update the `7z e` commands in the
`$(LIBUSB_SENTINEL)` Makefile rule accordingly.

---

## Architecture: What Changed

### USB layer

`picross/src/pic_usb_win32.cpp` (WinUSB/openwindev) has been retired. Both Windows
and Linux now use `picross/src/pic_usb_libusb.cpp` (libusb-1.0).

Windows-specific guards in `pic_usb_libusb.cpp`:

```cpp
#ifdef _WIN32
// Must include winsock2 before libusb pulls in windows.h (struct timeval conflict)
#include <winsock2.h>
#endif
```

```cpp
#ifndef _WIN32
// libusb_set_detach_kernel_driver is Linux/macOS only
//    libusb_set_detach_kernel_driver(dhandle_,1);
#endif
```

`sleep(1000)` (POSIX, seconds) replaced with `pic_microsleep(1000000)` -- consistent
with the macOS USB implementation and portable to Windows.

### Build environment (`tools/clangcl_tools.py`)

| Setting | Value |
|---------|-------|
| `CC` / `CXX` | `clang-cl` |
| `AR` | `llvm-lib` |
| `LINK` / `SHLINK` | `lld-link` |
| CRT | `/MD` (MSVC release CRT) |
| Compile flags | `/EHsc /O2 /fp:precise /std:c++17 /DWIN32 /D_WIN64 /D_WINDOWS` |
| Lib suffix | `.lib` |
| DLL suffix | `.dll` |
| Python module suffix | `.pyd` |

`LIBMAPPER` resolves `PILIBS` to `.lib` import libraries (not `.dll.a` as MinGW used).

### JUCE Configuration (`lib_juce/AppConfig.h`)

Key settings:

| Setting | Value | Notes |
|---------|-------|-------|
| `JUCE_ASIO` | `0` | ASIO SDK (Steinberg) not vendored; WASAPI + DirectSound available |
| `JUCE_WASAPI` | `1` | Modern Windows audio (Vista+, recommended) |
| `JUCE_DIRECTSOUND` | `1` | Legacy fallback for older Windows |
| Floating-point mode | `/fp:precise` | Allows `std::numeric_limits<double>::infinity()` usage |

**About ASIO:**

ASIO (low-latency audio driver interface from Steinberg) is disabled because the SDK is not included
in the repository. JUCE can still provide audio via WASAPI (Windows Audio Session API, modern) and
DirectSound (legacy). For most users, WASAPI is the preferred modern interface.

To add ASIO support:

1. Download the ASIO SDK from https://www.steinberg.net/developers/asio/
2. Extract it to a known location, e.g. `C:\asio_sdk`
3. Add the `common` subdirectory to the include path in `lib_juce/SConscript`:
   ```python
   if env['IS_WINDOWS']:
       juce_env.Append(CPPPATH='C:/asio_sdk/common')
   ```
4. Enable in [lib_juce/AppConfig.h](lib_juce/AppConfig.h):
   ```cpp
   #define JUCE_ASIO 1
   ```
5. Rebuild: `make clean && make lib_juce`

The floating-point mode is `/fp:precise` (not `/fp:fast`) to allow JUCE's use of infinity and NaN
for double-precision float parsing; this trades minimal optimization for full IEEE 754 compliance.

### picross SConscript

```python
if env['IS_LINUX']:
    pic_files += Split('pic_thread_posix.cpp pic_usb_libusb.cpp ...')
    pic_env.Append(LIBS=Split('libusb-1.0'))

if env['IS_WINDOWS']:
    pic_files += Split('pic_thread_win32.cpp pic_usb_libusb.cpp ...')
    pic_env.Append(LIBS=Split('shell32 libusb-1.0'))
    # openwindev removed
```

### Platform fixes applied

| Fix | File | Notes |
|-----|------|-------|
| `GetWindowLongPtr` / `GWLP_HINSTANCE` | `picross/src/pic_winloop.cpp` | 64-bit Windows API |
| `SIZE_T` for `GetProcessWorkingSetSize` | `picross/src/pic_thread_win32.cpp` | x64 pointer-sized type |
| `get_global_resources` in `PI_WINDOWS` block | `picross/src/pic_resources.cpp` | Was missing |
| `Python26` -> `Python314` in `get_pyprefix` | `picross/src/pic_resources.cpp` | Current Python |
| Python lib name derived from `sysconfig` | `tools/detect.py` | No longer hardcoded |
| `LIBPATH` as list not string | `tools/generic_tools.py` | SCons path resolution fix |
| `CPPPATH` as `Dir` node | `tools/generic_tools.py` | Correct `$EXPDIR` expansion |
| `python.exe -m pip` in dev-setup | `Makefile` | Windows pip restriction |
| `<winsock2.h>` before libusb | `picross/src/pic_usb_libusb.cpp` | Include order |
| `#ifndef _WIN32` on detach driver | `picross/src/pic_usb_libusb.cpp` | Linux/macOS only API |
| `pic_microsleep` replaces `sleep()` | `picross/src/pic_usb_libusb.cpp` | POSIX sleep not on Windows |

---

## Progress

- [x] Install VS Build Tools 2022 + LLVM; verify `clang-cl` from MSYS2 bash
- [x] Wire up environment (`eigend-msvc-env.sh`): MSVC CRT, Windows SDK, LLVM PATH
- [x] `tools/clangcl_tools.py` -- clang-cl/lld-link/llvm-lib build environment
- [x] `tools/select_tools.py` dispatches to `PiClangClEnvironment` on Windows
- [x] `make dev-setup` works on Windows
- [x] picross platform fixes (64-bit API, Python detection, resources)
- [x] USB layer consolidated to libusb (`pic_usb_libusb.cpp` on Linux + Windows)
- [x] libusb vendored archive auto-unpack on `make`
- [x] `clangcl_tools.py` adds libusb include/lib paths
- [x] C++17 flags added to clang-cl and lib_juce SConscript
- [x] `/arch:SSE2` removed (invalid on x64)
- [x] Floating-point mode set to `/fp:precise` for JUCE compatibility
- [x] JUCE_ASIO disabled (SDK not included; WASAPI/DirectSound available)
- [ ] Full `make` build completes without errors
- [ ] Build `lib_juce` -- key JUCE gate
- [ ] Build `app_stage` / `app_workbench` end-to-end

---

## ARM Windows Notes

### Running x64 builds on ARM Windows

x64 EigenD binaries run under Windows 11 x64 emulation (Snapdragon X, Apple Silicon
+ Parallels). No build changes required.

### Cross-compiling x64 from ARM64 Windows

```bash
clang-cl --target=x86_64-pc-windows-msvc ...
```

Requires VS Build Tools component: **"MSVC v143 - VS 2022 C++ x64/x86 build tools
for ARM64"**. Windows SDK ships both ARM64 and x64 lib trees.

### Native ARM64 builds

JUCE 8 and LLVM both support `arm64-pc-windows-msvc`. The libusb official release
includes an ARM64 `.lib`. Viable once the x64 build is stable.