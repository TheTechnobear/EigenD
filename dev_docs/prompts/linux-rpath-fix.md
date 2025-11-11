# Linux RPATH Fix (2025-11-11)

## Problem
On Linux, eigend required manually adding plugin directories to LD_LIBRARY_PATH:
```bash
for i in $ED/bin $ED/plugins/Eigenlabs/*; do 
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$i
done
```

This was not necessary on macOS or Windows.

## Root Cause
Linux binaries only had `$ORIGIN/../bin` embedded as rpath. When plugins in `plugins/Eigenlabs/*/` tried to load dependencies, the relative path would point to non-existent locations.

**macOS (correct):**
- Uses multiple rpath entries: `@loader_path/` and `@loader_path/../bin`
- Each library has proper install_name with `@rpath`

**Linux (was broken):**
- Only had: `$ORIGIN/../bin`
- Missing: `$ORIGIN` (current directory)

## Fix
Updated `tools/linux_tools.py` lines 46-47 to add `$ORIGIN` rpath:

```python
# Before:
self.Append(LINKFLAGS=Split('-g -z origin -Wl,--rpath-link=tmp/bin -Wl,--rpath=\\$$ORIGIN/../bin'))

# After:
self.Append(LINKFLAGS=Split('-g -z origin -Wl,--rpath-link=tmp/bin -Wl,--rpath=\\$$ORIGIN -Wl,--rpath=\\$$ORIGIN/../bin'))
```

Same change applied to SHLINKFLAGS.

## Result
After rebuild, Linux binaries will find dependencies in:
1. Current directory (`$ORIGIN`)
2. ../bin directory (`$ORIGIN/../bin`)

No LD_LIBRARY_PATH manipulation needed.
