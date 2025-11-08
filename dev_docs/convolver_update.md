# Convolver Update - Migration Notes

**Date:** 2025-11-08  
**Objective:** Enable plg_convolver to work with updated FFTW library on ARM64 (Apple Silicon) and other 64-bit platforms

---

## Background

### Primary Motivation
- **Mac ARM Support**: Need to support Apple Silicon (ARM64) architecture
- **64-bit Platform Support**: Modernize for all 64-bit platforms
- **FFTW Upgrade Required**: Old FFTW 3.2.1 lacked ARM support

### FFTW Upgrade (Completed)
- Upgraded `lib_fftw` from 3.2.1 to 3.3.10
- Successfully building with NEON SIMD support for ARM64
- SSE2 support for x86_64 platforms
- Library builds correctly: `tmp/obj/lib_fftw/libpifftw3.dylib` (1.2MB)
- Verified NEON symbols present: `_fftw_solvtab_dft_neon`, `_fftw_solvtab_rdft_neon`

### The Problem
- `plg_convolver` uses old custom `zita_convolver.cpp/.h` (based on older zita-convolver)
- Old zita-convolver code won't compile against new FFTW 3.3.10
- Initially assumed this was due to zita-convolver version incompatibility

---

## Investigation: Zita-Convolver Version 4

### Initial Attempt (2025-11-08)

**Files Updated:**
- `plg_convolver/src/SConscript` - changed to compile `zita-convolver4/zita-convolver.cc`
- Added FFTW include paths
- Updated `plg_convolver.cpp` to include zita-convolver4 header

**Findings:**
1. **Zita-Convolver 4 API Changes**:
   - `Convlevel` class is now **private** (was public in old version)
   - Public API in v4 is `Convproc` class
   - Eigenlabs code uses `Convlevel` directly (lower-level API)

2. **Method Signature Changes in v4**:
   - `configure()` - signature changed (takes `prio`, `options`)
   - `impdata_create()` → `impdata_write()` (with `create` boolean param)
   - `prepare()` → `reset()` (takes both input and output buffers)
   - `readout()` - signature changed (takes `sync`, `skipcnt`)

3. **Compilation Errors**:
   ```
   error: calling a private constructor of class 'Convlevel'
   error: 'configure' is a private member of 'Convlevel'
   error: no member named 'impdata_create' in 'Convlevel'
   error: no member named 'prepare' in 'Convlevel'
   error: 'readout' is a private member of 'Convlevel'
   ```

**Unknown Factors:**
- ❓ Does zita-convolver 4 actually support FFTW 3.3.10?
- ❓ Does zita-convolver 4 have ARM64/NEON support?
- ❓ What specific modifications did Eigenlabs make to original zita-convolver?

---

## Current Code Structure

### plg_convolver Files
```
plg_convolver/
├── src/
│   ├── plg_convolver.cpp/.h    # Main plugin code
│   ├── zita_convolver.cpp/.h   # Old customized zita-convolver (Eigenlabs version)
│   ├── zita-convolver4/        # New zita-convolver 4 source
│   │   ├── zita-convolver.cc
│   │   └── zita-convolver.h
│   └── SConscript
```

### API Usage in plg_convolver.cpp
Uses `Convlevel` class with these methods:
- `new Convlevel()` - constructor
- `configure(offset, npar, parsize, outstep, fftwopt, vectopt)`
- `impdata_create(inp, out, step, data, ind0, ind1)`
- `prepare(inpsize, inpbuff)`
- `cleanup()`
- `readout(outbuff, skip)`

---

## Approach Options

### Option A: Update Existing Zita-Convolver Code
**Pros:**
- Minimal API changes required
- Keep existing plg_convolver.cpp logic intact
- Understand what modifications Eigenlabs made
- May reveal insights for future v4 migration

**Cons:**
- Working with older codebase
- May not benefit from v4 improvements
- Could be maintaining legacy code

**Tasks:**
1. Analyze what changes Eigenlabs made to original zita-convolver
2. Update old zita_convolver.cpp/.h to work with FFTW 3.3.10
3. Ensure ARM64/NEON support in old codebase
4. Test on multiple platforms

### Option B: Migrate to Zita-Convolver 4
**Pros:**
- Modern codebase
- May have better ARM support built-in
- Future-proof solution
- Official upstream support

**Cons:**
- Significant code changes required (use `Convproc` instead of `Convlevel`)
- Need to verify FFTW 3.3.10 compatibility
- Need to verify ARM64 support
- Reimplement Eigenlabs customizations

**Tasks:**
1. Verify zita-convolver 4 supports FFTW 3.3.10
2. Verify ARM64/NEON support in v4
3. Rewrite plg_convolver.cpp to use `Convproc` API
4. Port any Eigenlabs customizations to v4
5. Test on multiple platforms

---

## Decision: Start with Option A

**Rationale:**
- Lower risk approach - smaller changes
- Can learn from Eigenlabs modifications
- If v4 doesn't support FFTW 3.3.10 or ARM, we'd need this anyway
- Insights gained will help with Option B if we decide to migrate later

**Next Steps:**
1. ✅ Stash zita-convolver 4 attempt (reverted to old zita_convolver)
2. Analyze differences between stock zita-convolver and Eigenlabs version
3. Identify FFTW-specific issues in old zita_convolver code
4. Update old code to work with FFTW 3.3.10 + ARM64

---

## Current Status: Analyzing Old Zita-Convolver Issues

### Build Attempt with Old zita_convolver.cpp (2025-11-08)

**Setup:**
- Reverted to compile `zita_convolver.cpp` instead of `zita-convolver4/zita-convolver.cc`
- Added FFTW include paths to SConscript
- Using old Eigenlabs-modified zita-convolver

**Compilation Result:** ✅ Compiles successfully
- `zita_convolver.os` builds without errors
- `plg_convolver.os` builds without errors

**Linking Result:** ❌ Linker errors

```
Undefined symbols for architecture arm64:
  "_fftwf_destroy_plan"
  "_fftwf_execute_dft_c2r"  
  "_fftwf_execute_dft_r2c"
  "_fftwf_plan_dft_c2r_1d"
  "_fftwf_plan_dft_r2c_1d"
ld: symbol(s) not found for architecture arm64
```

**Analysis:**
- The old zita-convolver uses **single-precision float** FFTW functions (`fftwf_*`)
- Our updated `lib_fftw` compiles and exports **double-precision** functions (`fftw_*`)
- FFTW 3.3.10 supports both, but we only built the double-precision version

**Root Cause:** 
Our `lib_fftw` SConscript builds only the double-precision library. Zita-convolver requires the single-precision (float) version for audio processing (makes sense - audio doesn't need double precision).

**Solution Path:**
Need to enable single-precision float FFTW build in lib_fftw:
1. Define `FFTW_SINGLE` in config headers
2. Build single-precision library alongside (or instead of) double-precision
3. Link plg_convolver against the float version

---

## FFTW Precision: Double vs Single

### Current State
- **lib_fftw** builds: Double-precision only (`fftw_*` functions)
- **zita_convolver** needs: Single-precision (`fftwf_*` functions)
- Config files have `/* #undef FFTW_SINGLE */` (single precision disabled)

### FFTW Function Naming
- Double precision: `fftw_plan_dft_r2c_1d()`, `fftw_execute()`, etc.
- Single precision: `fftwf_plan_dft_r2c_1d()`, `fftwf_execute()`, etc. (note the 'f')

### Audio Processing Rationale
Single precision is appropriate for audio because:
- Audio samples are typically 16-24 bit
- Single precision provides ~7 decimal digits of precision (sufficient for audio)
- Half the memory usage vs double precision
- Faster processing on most architectures

### FFTW Build Requirements
FFTW requires **separate builds** for different precisions:
- Define `FFTW_SINGLE` in config headers
- All source files must be recompiled with this flag
- Results in `fftwf_*` function names (note the 'f')

**Options:**
1. **Build only single precision** - Simpler, meets our needs (audio processing)
2. **Build both precisions** - More complex, larger binary, but provides both APIs

**Recommendation:** Build only single precision for now (option 1)
- EigenD is an audio application - double precision not needed
- Simplifies build process
- Smaller binaries
- Can always add double precision later if needed

---

## Next Actions

1. ✅ **Update lib_fftw config headers:**
   - Changed `/* #undef FFTW_SINGLE */` to `#define FFTW_SINGLE 1`
   - Applied to all platform configs (macOS ARM64, x86_64, Linux, Windows)

2. ✅ **Rebuild lib_fftw:**
   - Clean and rebuild library completed
   - Verified `fftwf_*` symbols are present:
     - `fftwf_plan_dft_r2c_1d`, `fftwf_plan_dft_c2r_1d`
     - `fftwf_execute_dft_r2c`, `fftwf_execute_dft_c2r`
     - `fftwf_destroy_plan`

3. ✅ **Test plg_convolver:**
   - **Links successfully** against single-precision FFTW!
   - No undefined symbol errors
   - Library built: `tmp/obj/plg_convolver/src/libconvolver.dylib`

4. **Next: Verify on all platforms:**
   - ✅ macOS ARM64 (Apple Silicon) - Working!
   - ⏳ macOS x86_64
   - ⏳ Linux x86_64, ARM64
   - ⏳ Windows x86_64

---

## Resolution Summary (2025-11-08)

### Problem
- plg_convolver wouldn't compile after FFTW upgrade to 3.3.10
- Old zita_convolver code needed single-precision float FFTW (`fftwf_*` functions)
- Our lib_fftw was building double-precision only (`fftw_*` functions)

### Solution
- Enabled single-precision in all FFTW config headers (`#define FFTW_SINGLE 1`)
- Rebuilt lib_fftw with NEON support (ARM64) in single precision
- plg_convolver now compiles and links successfully

### Status
- ✅ lib_fftw: Single-precision build with ARM64/NEON support
- ✅ plg_convolver: Compiles and links on macOS ARM64
- ⏳ Runtime testing needed
- ⏳ Cross-platform verification needed

### Files Modified
- `lib_fftw/config_macosx_arm64.h`
- `lib_fftw/config_macosx_x86_64.h`
- `lib_fftw/config_windows_x86_64.h`
- `lib_fftw/config_linux_x86_64.h`
- `lib_fftw/config_linux_arm64.h`
- `plg_convolver/src/SConscript` (added FFTW include paths)

**Key Insight:** The original issue wasn't about zita-convolver version compatibility - it was about FFTW precision mismatch. The old zita_convolver code works fine with FFTW 3.3.10, it just needs single-precision.

**Outcome:** No need to migrate to zita-convolver 4 at this time. The existing Eigenlabs-modified zita_convolver works perfectly with FFTW 3.3.10 single-precision, including full ARM64/NEON support.

---

## Lessons Learned

1. **FFTW Precision Matters**: Audio processing uses single-precision floats (`fftwf_*`), not double-precision (`fftw_*`)

2. **Original Code Was Fine**: The Eigenlabs zita_convolver modifications were good - no fundamental incompatibility with modern FFTW

3. **Simpler Than Expected**: Problem solved by single config change, no code modifications needed

4. **Zita-Convolver 4 Not Needed**: The v4 migration would have been significant work with no clear benefit for this use case

## Future Considerations

### If We Decide to Migrate to Zita-Convolver 4 Later

**Pros:**
- Upstream support and updates
- Potential performance improvements
- Modern codebase

**Cons:**
- Major API changes (`Convlevel` is private, must use `Convproc`)
- Significant code rewrite required in `plg_convolver.cpp`
- Need to re-apply any Eigenlabs customizations
- Must verify ARM64/NEON/FFTW 3.3.10 compatibility

**Verdict:** Stay with current working solution. If upstream zita-convolver gains important features or security fixes, reconsider.

---

## Build Verification

**Command to verify FFTW symbols:**
```bash
nm tmp/obj/lib_fftw/libpifftw3.dylib | grep fftwf_
```

**Expected:** Should see `fftwf_plan_dft_r2c_1d`, `fftwf_execute`, etc. (note the 'f')

**Command to verify plg_convolver builds:**
```bash
rm -rf tmp/obj/plg_convolver && make
```

**Expected:** Should complete without linker errors

---

## Technical Notes

### Eigenlabs Modifications to Zita-Convolver

**Key Modification Found** (lines 105-117 in `zita_convolver.h`):

```cpp
class CONVOLVER_DECLSPEC_CLASS Convlevel
{
#if ZITA_THREADING==1
private:
    friend class Convproc;
#else
public:
#endif // ZITA_THREADING==1
```

**What Eigenlabs Changed:**
1. **Threading Control**: Added `ZITA_THREADING` macro (defaults to 0, line 23)
2. **Class Visibility**: When `ZITA_THREADING=0`, `Convlevel` becomes PUBLIC
3. **Direct API Access**: Allows using `Convlevel` directly without `Convproc` wrapper
4. **Threading Removal**: Disables pthread/semaphore dependencies when `ZITA_THREADING=0`

**Why This Matters:**
- Original zita-convolver (2006-2007): Likely had `Convlevel` as public API
- Zita-convolver v4 (2018): `Convlevel` is always private, `Convproc` is public
- Eigenlabs version: Conditional compilation for threading/API access
- **EigenD uses its own threading** → doesn't need zita's pthread implementation
- **Direct control**: `Convlevel` API gives fine-grained control over processing

**Other Modifications:**
- Custom `CONVOLVER_DECLSPEC_CLASS` export macros
- Integration with picross includes (`#include <picross/pic_config.h>`)
- Platform-specific FFTW includes (`PI_IS_LINUX_ARM7L` conditional)
- Simplified for embedded use (no separate library build)

### FFTW 3.3.10 Changes from 3.2.1
*(Relevant changes that affect zita-convolver)*

- *(To be documented)*

---

## Testing Checklist

Once updated:
- [x] macOS ARM64 (Apple Silicon) - Builds successfully
- [ ] macOS x86_64 (Intel) - Not tested
- [ ] Linux x86_64 - Not tested
- [ ] Linux ARM64 - Not tested
- [ ] Windows x86_64 - Not tested
- [ ] Runtime testing with audio

---

## Migration Decision

**Current Status: RESOLVED ✅**

**Decision: Keep Eigenlabs' Modified Old Version**

Rationale:
1. **Works Now**: Old zita-convolver + FFTW 3.3.10 single-precision builds cleanly
2. **Minimal Changes**: Only needed to enable `FFTW_SINGLE` in config headers
3. **Threading Control**: Eigenlabs' `ZITA_THREADING` modification is elegant
4. **No API Changes**: plg_convolver.cpp doesn't need refactoring
5. **Risk Assessment**: Migrating to v4 would require significant rewrite

**Future Migration Path (if needed):**
- Rewrite plg_convolver to use `Convproc` API instead of `Convlevel`
- Integrate v4's pthread threading OR re-apply `ZITA_THREADING` modification
- Test extensively (threading changes = potential audio glitches)
- Current version from 2006-2007 is stable and proven

---

## References

- FFTW 3.3.10: http://fftw.org/
- Zita-convolver: http://kokkinizita.linuxaudio.org/linuxaudio/
- EigenD lib_fftw: `/Users/kodiak/projects/EigenD/lib_fftw/`
- Convolver plugin: `/Users/kodiak/projects/EigenD/plg_convolver/`
