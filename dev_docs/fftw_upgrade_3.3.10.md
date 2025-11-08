# FFTW Upgrade Summary: 3.2.1 → 3.3.10

**Date:** 2025-11-08

## Overview
Upgraded lib_fftw from FFTW 3.2.1 to 3.3.10 to support ARM on macOS and multiple platforms.

## Supported Platforms
- macOS x86_64 (SSE2 optimizations)
- macOS ARM64 (NEON optimizations) **NEW**
- Windows x86_64 (SSE2 optimizations)
- Linux x86_64 (SSE2 optimizations)
- Linux ARM64 (NEON optimizations) **NEW**

## Changes Made

### 1. Platform-Specific Config Headers Created
- `config_macosx_x86_64.h` - macOS x86_64 with SSE2
- `config_macosx_arm64.h` - macOS ARM64 with NEON
- `config_windows_x86_64.h` - Windows x86_64 with SSE2
- `config_linux_x86_64.h` - Linux x86_64 with SSE2
- `config_linux_arm64.h` - Linux ARM64 with NEON

### 2. SConscript Updates
- Updated base directory from `src/` to `fftw-3.3.10/`
- Added platform detection function `get_platform_config()`
- Updated all source file paths to use FFTW 3.3.10 structure
- Added conditional SIMD support:
  - SSE2 for x86_64 platforms
  - NEON for ARM64 platforms
- Updated include paths to match new directory structure
- Added platform-specific compiler flags:
  - macOS: `-msse2` (x86_64), NEON support (ARM64)
  - Linux: `-msse2` (x86_64), NEON support (ARM64)
  - Windows: SSE2 with `/wd4244 /wd4305` to suppress warnings

### 3. Source Files
Updated to use FFTW 3.3.10 source structure:
- **Kernel**: Core FFTW functions (45 files)
- **DFT**: Discrete Fourier Transform (23 base + 46 codelets)
- **RDFT**: Real DFT (44 base + 180+ codelets for r2cf/r2cb/r2r)
- **REODFT**: Real even/odd DFT (10 files)
- **API**: Public API functions (73 files)
- **SIMD Support**: Platform-specific SIMD (sse2.c, neon.c, taint.c)

### 4. Key Differences from 3.2.1
- Moved from `src/` to `fftw-3.3.10/` directory structure
- Added `simd-support/` directory for SIMD backends
- Improved SIMD detection and support
- Added NEON support for ARM processors
- Updated config system to use platform-specific headers

## Build Configuration

### Compiler Defines
- All platforms: `-DHAVE_CONFIG_H=1`
- Windows: Additional `-DFFTW_DLL`
- Config file included via: `-include config_[platform].h`

### SIMD Optimizations
- **x86_64 platforms**: SSE2 enabled with `-msse2`
- **ARM64 platforms**: NEON enabled via config headers
- Generic fallback available when SIMD not supported

## Testing Recommendations
1. Build on macOS x86_64 and verify SSE2 code paths
2. Build on macOS ARM64 and verify NEON code paths (PRIMARY TARGET)
3. Test on Linux x86_64 with existing workloads
4. Verify Windows build with SSE2 support
5. Check performance compared to 3.2.1 baseline

## Backward Compatibility
- API remains compatible with FFTW 3.2.1
- Library name unchanged: `pifftw3`
- No changes required to calling code

## Files Modified
- `lib_fftw/SConscript` - Complete rewrite for 3.3.10
- `lib_fftw/SConscript.old` - Backup of original

## Files Created
- `lib_fftw/config_macosx_x86_64.h`
- `lib_fftw/config_macosx_arm64.h`
- `lib_fftw/config_windows_x86_64.h`
- `lib_fftw/config_linux_x86_64.h`
- `lib_fftw/config_linux_arm64.h`

## Notes
- FFTW 3.3.10 source files should be in `lib_fftw/fftw-3.3.10/`
- Old source files in `lib_fftw/src/` are no longer used
- Config detection is automatic based on platform and architecture
- ARM build is now enabled (previously disabled with ARMHACK comment)

## Next Steps
1. Test build on current platform (macOS)
2. Verify ARM64 build works
3. Run performance benchmarks
4. Update any documentation that references FFTW version
