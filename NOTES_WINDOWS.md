# EigenD Windows Development with MSYS2

## Overview

EigenD Windows development **requires MSYS2** for a unified Unix-like workflow across all platforms. This provides the same `make` commands on Windows, macOS, and Linux.

**Important:** End users only need Python 3.14 from python.org. MSYS2 is only for developers.

---

## Initial Setup (Required)

### 1. Install Python 3.14

Download and install from: https://www.python.org/downloads/

**Default location:** `C:\Python314\`

Make sure to:
- ✅ Check "Add Python to PATH" during installation
- ✅ Install for all users (or remember custom path)

### 2. Install MSYS2

Download from: https://www.msys2.org/

**Install to:** `C:\msys64\` (default)

After installation:

```bash
# Open "MSYS2 MinGW64" shell (purple icon - NOT blue MSYS2 MSYS shell)

# Update MSYS2
pacman -Syu
# Close terminal when prompted, reopen and run again:
pacman -Syu

# Install development tools
pacman -S --needed base-devel mingw-w64-x86_64-toolchain
pacman -S make git
```

### 3. Install Visual Studio Build Tools

**Required** for MSVC compiler and Windows SDK.

Download: https://visualstudio.microsoft.com/downloads/

Install "Build Tools for Visual Studio 2022" with:
- ✅ Desktop development with C++
- ✅ Windows 10/11 SDK (includes DirectX headers)
- ✅ MSVC v143 (or latest)

---

## Building EigenD

### Every Build Session

**Important:** You must source the MSVC environment before building:

```bash
# Open MSYS2 MinGW64 shell
cd /c/Projects/EigenD

# Source MSVC environment (required every session)
source /c/Program\ Files/Microsoft\ Visual\ Studio/2022/Community/VC/Auxiliary/Build/vcvars64.bat

# Now you can build
make
```

**Tip:** Create a helper script to make this easier:

```bash
# Save as ~/eigend-env.sh
source /c/Program\ Files/Microsoft\ Visual\ Studio/2022/Community/VC/Auxiliary/Build/vcvars64.bat
cd /c/Projects/EigenD

# Then just run:
source ~/eigend-env.sh
make
```

### Standard Build Commands

```bash
# One-time setup: Create dev environment
make dev-setup

# Build (parallel, faster)
make

# Build single-threaded (for debugging build issues)
make single

# Clean
make clean

# Create Windows installer
make pkg
```

### What Happens During Build

1. **SCons checks for MSVC environment**
   - Looks for `VCINSTALLDIR` environment variable
   - If not found: Shows error with instructions
   - If found: Verifies Visual Studio location

2. **SCons checks for DirectX SDK**
   - Checks `WindowsSdkDir` (modern, from Visual Studio)
   - Checks `DXSDK_DIR` (legacy DirectX SDK)
   - If neither found: Shows warning but continues
   - Build will fail later if DirectX actually needed

---

## Compiler Selection

Currently **MSVC only**. MinGW support may be added later for comparison.

**MSVC (Microsoft Visual C++):**
- Required for Windows builds
- Provides best Windows API compatibility
- Includes Windows SDK with DirectX headers

---

## Testing

```bash
# From MSYS2 MinGW64 shell (after sourcing MSVC environment):
./run_tests.sh --quick --level foundation
```

**Note:** Testing currently focused on macOS/Linux. Windows testing is lower priority but distribution is important.

---

## Legacy Build Method

**REMOVED:** The old `bld.cmd` script has been removed. MSYS2 is now required for Windows development.

If you try to run `bld.cmd`, it will show an error directing you to use MSYS2.

---

## Distribution

**End users do NOT need MSYS2.** They only need:
- Python 3.14 from python.org
- EigenD installer (.msi)

The installer includes all necessary runtime DLLs.

---

## GitHub Actions (Future)

Release builds will be automated via GitHub Actions:
- macOS build on macOS runner
- Linux build on Ubuntu runner  
- Windows build on Windows runner (likely using MSVC)

---

## Troubleshooting

### "ERROR: MSVC environment not detected"

You forgot to source the MSVC environment:

```bash
# Run this before 'make':
source /c/Program\ Files/Microsoft\ Visual\ Studio/2022/Community/VC/Auxiliary/Build/vcvars64.bat
```

If Visual Studio is installed elsewhere, adjust the path.

### "Python not found at /c/Python314/python.exe"

Check Python installation:
```bash
# Should show Python 3.14
/c/Python314/python.exe --version

# If installed elsewhere, set explicitly:
make PYTHON_BUILD=/c/Path/To/python.exe
```

### "WARNING: DirectX SDK not detected"

Usually means MSVC environment not sourced properly. The Windows SDK (with DirectX) should be available after sourcing vcvars64.bat.

If warning persists but build succeeds, DirectX may not be needed for your build configuration.

### "bld.cmd is deprecated" error

Don't use `bld.cmd`. Use MSYS2 and `make` instead. See setup instructions above.

---

## Platform Differences

| Feature | macOS | Linux | Windows |
|---------|-------|-------|---------|
| Dev shell | Terminal | Terminal | MSYS2 MinGW64 |
| Python path | `/usr/local/bin/python3.14` | `/usr/local/bin/python3.14` | `/c/Python314/python.exe` |
| Build cmd | `make` | `make` | `make` (after sourcing MSVC) |
| Compiler | Clang | GCC | MSVC |
| Extra setup | None | None | Source vcvars64.bat |
| Testing | ✅ Primary | ✅ Secondary | ⚠️ Lower priority |
| Distribution | ✅ Critical | ✅ Critical | ✅ Critical |

---

## Summary

**Windows Development = MSYS2 + MSVC**

1. Install Python 3.14 (python.org)
2. Install MSYS2
3. Install Visual Studio Build Tools
4. Open MSYS2 MinGW64 shell
5. Source MSVC environment
6. Run `make`

Once set up, the workflow matches macOS/Linux exactly.
