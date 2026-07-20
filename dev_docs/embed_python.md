# Embedding Python (libpython) in EigenD — Feasibility & Plan

**Date:** 2026-07-20
**Status:** Analysis / Proposal

---

## 1. Motivation

Currently EigenD requires users to install Python 3.14 separately (from python.org on macOS/Windows, or via distro packages on Linux). Embedding libpython would:

- Make EigenD a **self-contained** application — no separate Python install needed.
- **Pin the Python version** — eliminates version mismatch bugs; always tested against one known Python.
- **Linux advantage** — ship Python 3.14 even on distros that haven't packaged it yet.
- **Simpler user experience** — download, install, run.

---

## 2. How EigenD Currently Uses Python

### 2.1 Architecture Overview

Python serves as the **"glue" layer** between C++ native modules and plugin logic:

```
┌─────────────────────────────────────────────────┐
│  Python (.py files)                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ pi/      │  │pisession/│  │ plg_*/   │       │
│  │ (agents, │  │(session, │  │ (plugin  │       │
│  │  atoms,  │  │ agentd,  │  │  logic)  │       │
│  │  logic)  │  │ registry)│  │          │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │              │              │             │
│       ▼              ▼              ▼             │
│  ┌──────────────────────────────────────────┐    │
│  │        PIP-generated bindings            │    │
│  │  (*_native.so / *_python.cpp)            │    │
│  └────────────────────┬─────────────────────┘    │
│                       │                          │
├───────────────────────┼──────────────────────────┤
│  C++                  ▼                          │
│  ┌──────────────────────────────────────────┐    │
│  │  piw, picross, piagent, lib_*            │    │
│  │  (native C++ libraries)                  │    │
│  └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### 2.2 Startup Flow

1. `eigend` main() in `app_eigend2/eigend.cpp`
2. Calls `epython::PythonInterface::py_startup()` in `lib_juce/epython.cpp`
3. `Py_SetPythonHome()` — points to system Python prefix
4. `Py_Initialize()` — starts embedded Python interpreter
5. Sets up `sys.path` to find EigenD's Python modules
6. Saves thread state via `PyEval_SaveThread()`
7. Later, `pisession/session.py` creates scaffold, loads agents via `agentd.py`

### 2.3 Python as "Glue" — Example: plg_finger

```
plg_finger/
├── __init__.py              (empty)
├── finger_plg.py            ← Main plugin logic (~400 lines Python)
├── SConscript               ← Build: declares agent + native module
├── Factory Fingerings.txt   ← Data file
├── User Fingerings.txt      ← Data file
└── src/
    ├── finger.pip           ← PIP interface definition
    └── fng_finger.h         ← C++ header
```

**`finger.pip`** defines C++ classes exposed to Python:
```
class fingering[fng::fingering_t] { ... }
class finger[fng::finger_t] { ... }
```

**`finger_plg.py`** imports:
- EigenD Python modules: `pi.agent`, `pi.atom`, `piw`, etc.
- PIP-generated native: `finger_native` (built from `finger.pip`)
- Stdlib: `configparser`, `os`, `shutil`

The Python code handles: fingering data management, file I/O, RPC enumeration, user/factory fingering loading. The C++ side handles: real-time key evaluation, audio signal processing.

### 2.4 Python Standard Library Usage

Comprehensive list of stdlib modules imported by the core project (excluding `app_commander/`, `app_browser2/`, `tools/`, `tests/`):

| Module | Used In | Purpose |
|--------|---------|---------|
| `os` / `os.path` | ~30 files | File paths, environment |
| `sys` | ~20 files | sys.path, stdout/stderr |
| `re` | ~10 files | Regex parsing |
| `threading` | ~8 files | Thread management |
| `time` | ~8 files | Timestamps, sleep |
| `gc` | ~5 files | Garbage collection control |
| `traceback` | ~5 files | Error formatting |
| `shutil` | ~5 files | File copy operations |
| `glob` | ~4 files | File pattern matching |
| `configparser` | ~4 files | INI-style config files |
| `struct` | ~4 files | Binary data packing |
| `json` | ~3 files | JSON serialization |
| `math` | ~3 files | Math functions |
| `random` | ~3 files | Random numbers |
| `sqlite3` | `plg_loop/loopdb.py` | Loop database |
| `zipfile` | `pisession/registry.py` | Setup packaging |
| `zlib` | `plg_host/host_plg.py` | Compression |
| `xml.dom.*` / `xml.etree` | `plg_language/stage_server.py` | XML parsing |
| `xmlrpc.client` | `plg_language/stage_server.py` | Stage-EigenD RPC |
| `xml.sax.saxutils` | `plg_language/stage_server.py` | XML escaping |
| `urllib.parse` | `plg_host/host_plg.py`, `pisession/agentd.py` | URL encoding |
| `urllib.request` | `plg_host/host_plg.py` | HTTP requests |
| `urllib.error` | `plg_host/host_plg.py` | HTTP error handling |
| `socket` | `plg_language/stage_server.py` | Network |
| `hashlib` | `app_cmdline/` tools | Hashing |
| `base64` | `app_cmdline/` tools | Encoding |
| `binascii` | `app_cmdline/` tools | Binary/ASCII |
| `argparse` | `app_cmdline/` tools | CLI parsing |
| `optparse` | `app_cmdline/` tools | CLI parsing (legacy) |
| `getpass` | `app_cmdline/` tools | Password input |
| `mimetypes` | `app_cmdline/` tools | MIME type detection |
| `datetime` | `app_cmdline/` tools | Date handling |
| `logging` | `app_cmdline/` tools | Logging |
| `copy` | `pi/` | Deep copy |
| `weakref` | `pi/agent.py` | Weak references |
| `inspect` | `pi/agent.py` | Introspection |
| `types` | `pi/agent.py`, `pigui/mathutils.py` | Type checking |
| `operator` | `plg_host/host_plg.py` | Operator functions |
| `itertools` | `pi/` | Iterator tools |
| `string` | `plg_host/host_plg.py` | String constants |
| `collections` | `pi/upgrade.py` | Container types |
| `heapq` | `pi/upgrade.py` | Heap queue |
| `unittest` | `pi/database_test.py` | Unit testing |

**Third-party modules (build-time only):**
| Module | Used In | Purpose |
|--------|---------|---------|
| `numpy` | `plg_synth/src/minblep.py` | Wavetable generation (build-time) |
| `scipy` | `plg_synth/src/minblep.py` | Wavetable generation (build-time) |

**Key observation:** All runtime Python dependencies are **standard library only**. No third-party pip packages are needed at runtime. The numpy/scipy usage in `minblep.py` is a build-time code generation tool.

---

## 3. Current Python Linking Model

### 3.1 How Python is Found

The build system (`tools/detect.py`) queries the build-time Python's `sysconfig`:

- **macOS (framework):** Links against `/Library/Frameworks/Python.framework/Versions/3.14/Python`
- **macOS (non-framework):** Links against `libpython3.14` in `lib/python3.14/config`
- **Linux:** Links against `libpython3.14` in `/usr/lib/python3.14/config`
- **Windows:** Links against `Python26.lib` (note: still references Python26!)

### 3.2 How Python is Located at Runtime

`picross/src/pic_resources.cpp` — `get_pyprefix()`:

| Platform | Debug | Release |
|----------|-------|---------|
| **macOS** | `PI_PREFIX` (compile-time define) | `PI_PREFIX` (compile-time define) |
| **Linux** | `/usr/local/pi` | `/usr` |
| **Windows** | `C:\Program Files\Eigenlabs` | `<exe>/../../runtime-1.0.0/Python26` |

`PI_PREFIX` is set during build from the detected Python's `sys.prefix`.

### 3.3 The epython.cpp Layer

`lib_juce/epython.cpp`:
- Calls `Py_SetPythonHome(pic::python_prefix_dir())` — tells Python where its standard library lives
- Calls `Py_Initialize()` — starts the interpreter
- Sets up `sys.path` to include EigenD's `modules/` and `bin/` directories
- Saves thread state for later use by context threads

---

## 4. Feasibility Assessment

### 4.1 Is It Viable? **YES**

Embedding libpython is viable and is actually a well-established pattern. Python is explicitly designed for embedding. The CPython `--enable-shared` build produces `libpython3.14.so`/`.dylib`/`.dll` that can be bundled with an application.

### 4.2 What Would Need to Change

#### A. Build System Changes

1. **Add libpython as a build dependency** — either:
   - **Option A (Recommended):** Download pre-built Python 3.14 from python.org, extract the shared library + standard library, and bundle them.
   - **Option B:** Build CPython from source as part of the EigenD build (slower, more complex).

2. **Modify `tools/detect.py`** — instead of detecting system Python, point to the bundled Python:
   - Include path → bundled `include/python3.14/`
   - Library path → bundled `lib/`
   - Library → `python3.14`

3. **Modify `pic_resources.cpp`** — `get_pyprefix()` should point to the bundled Python stdlib location relative to the executable, not the system Python prefix.

4. **Modify `lib_juce/epython.cpp`** — `py_startup()` already uses `Py_SetPythonHome()`, just needs the correct bundled path.

5. **SCons/SConstruct changes** — add a step to download/extract Python, or add a CMake external project.

#### B. Runtime Changes

1. **Python home directory** — bundle the Python standard library (`lib/python3.14/`) inside the app package.
2. **Shared library** — bundle `libpython3.14.so`/`.dylib`/`.dll` alongside the executable.
3. **RPATH/loader path** — ensure the executable can find the bundled libpython at runtime.

#### C. Packaging Changes

| Platform | Current | Proposed |
|----------|---------|----------|
| **macOS** | Links to `/Library/Frameworks/Python.framework` | Bundle `libpython3.14.dylib` + stdlib in `.app/Contents/Frameworks/` |
| **Windows** | Links to system `Python26.lib`, runtime looks for `runtime-1.0.0/Python26/` | Bundle `python314.dll` + stdlib in app directory |
| **Linux** | Links to `/usr/lib/libpython3.14.so`, uses `/usr` as prefix | Bundle `libpython3.14.so.1.0` + stdlib in `lib/` directory; use `$ORIGIN/../lib` RPATH |

### 4.3 What Does NOT Need to Change

- **PIP binding system** — no changes needed; it generates standard CPython extension modules.
- **Plugin Python code** — all `.py` files continue to work unchanged.
- **Native modules** (`*_native.so`) — continue to link against the Python C API as before.
- **Thread safety** (`lock_c2p`) — continues to work with bundled libpython.
- **SCons build tool** — SCons runs at build time with the build-environment Python (`.venv_dev`), unaffected by runtime Python changes.

---

## 5. Distribution Plan

### 5.1 macOS

```
EigenD.app/
└── Contents/
    ├── MacOS/
    │   └── eigend              (executable, rpath = @executable_path/../Frameworks)
    ├── Frameworks/
    │   └── libpython3.14.dylib (bundled shared library)
    └── Resources/
        └── python314/          (Python standard library)
            ├── os.py
            ├── sys.py
            ├── ...
            └── lib-dynload/    (C extension modules like _sqlite3, _ssl, etc.)
```

**Key considerations:**
- macOS code signing — bundled dylibs must be signed.
- Notarization — the .app must pass Apple notarization.
- The Python framework is ~80MB; the stdlib alone (without site-packages, tests) is ~30MB.

### 5.2 Windows

```
EigenD/
├── eigend.exe
├── python314.dll              (bundled shared library)
├── python314.zip              (or directory: Python standard library)
└── modules/                   (EigenD Python modules)
```

**Key considerations:**
- Windows can use a `python314.zip` for the stdlib (Python natively supports zip imports via `sys.path`).
- Alternatively, use a `python314/` directory for easier debugging.
- The DLL must be in the same directory as the exe or in PATH.

### 5.3 Linux

```
eigenlabs/
├── bin/
│   └── eigend
├── lib/
│   ├── libpython3.14.so.1.0   (bundled shared library)
│   └── python314/             (Python standard library)
│       └── ...
└── share/
    └── eigend/
        └── modules/           (EigenD Python modules)
```

**Key considerations:**
- Use `$ORIGIN/../lib` RPATH so the executable finds libpython relative to itself.
- AppImage or Flatpak are good distribution formats for self-contained Linux apps.
- Must bundle `lib-dynload/` C extensions (`.so` files like `_sqlite3.cpython-314-x86_64-linux-gnu.so`).

---

## 6. Phase 0: macOS Proof of Concept (Dev Machine Only)

Goal: test bundled Python on a dev machine with minimal changes, no packaging concerns.

### 6.1 Current State

- eigend binary links directly against `/Library/Frameworks/Python.framework/Versions/3.14/Python` (absolute path)
- `pic_resources.cpp` `get_pyprefix()` returns `PI_PREFIX` (compile-time constant, currently `/Library/Frameworks/Python.framework/Versions/3.14`)
- `epython.cpp` calls `Py_SetPythonHome(pic::python_prefix_dir())` before `Py_Initialize()`
- `Py_SetPythonHome()` overrides `PYTHONHOME` env var, so we can't use env vars alone
- App bundle at `tmp/app/EigenD.app/` — `MacOS/EigenD` is a symlink to `tmp/bin/eigend`

### 6.2 PoC Steps

#### Step 1: Create bundled directory structure

```bash
# Create directories in the app bundle
mkdir -p tmp/app/EigenD.app/Contents/Frameworks
mkdir -p tmp/app/EigenD.app/Contents/Resources/python314

# Copy libpython dylib (14MB)
cp /Library/Frameworks/Python.framework/Versions/3.14/Python \
   tmp/app/EigenD.app/Contents/Frameworks/libpython3.14.dylib

# Copy stdlib, skipping unnecessary bits (~66MB instead of 196MB)
# Skip: test/ (112MB), site-packages/ (18MB), idlelib/, tkinter/, turtledemo/, __pycache__/
rsync -av \
  --exclude='test/' --exclude='site-packages/' \
  --exclude='idlelib/' --exclude='tkinter/' --exclude='turtledemo/' \
  --exclude='__pycache__/' \
  /Library/Frameworks/Python.framework/Versions/3.14/lib/python3.14/ \
  tmp/app/EigenD.app/Contents/Resources/python314/
```

#### Step 2: Modify `pic_resources.cpp` — one function

File: `picross/src/pic_resources.cpp`, function `get_pyprefix()` for `PI_MACOSX`:

```cpp
// BEFORE:
static void get_pyprefix(char *buffer)
{
    strcpy(buffer,PI_PREFIX);
}

// AFTER:
static void get_pyprefix(char *buffer)
{
    // Look for Python stdlib relative to the executable
    // executable is at: EigenD.app/Contents/MacOS/EigenD
    // stdlib is at:     EigenD.app/Contents/Resources/python314
    get_exe(buffer);           // .../EigenD.app/Contents/MacOS/EigenD
    dirname(buffer);           // .../EigenD.app/Contents/MacOS
    dirname(buffer);           // .../EigenD.app/Contents
    strcat(buffer, RES_SEPERATOR_STR);
    strcat(buffer, "Resources");
    strcat(buffer, RES_SEPERATOR_STR);
    strcat(buffer, "python314");
}
```

#### Step 3: Rebuild affected components

Only `libpic` (contains `pic_resources.cpp`) and `eigend` need rebuilding:

```bash
# Rebuild libpic + eigend (SCons incremental — only changed files recompile)
make 2>&1 | tee build.log
```

#### Step 4: Fix Python linkage in eigend binary

After rebuild, eigend will still link against the absolute framework path. Fix with `install_name_tool`:

```bash
install_name_tool -change \
  /Library/Frameworks/Python.framework/Versions/3.14/Python \
  @executable_path/../Frameworks/libpython3.14.dylib \
  tmp/bin/eigend

# Also fix libepython.dylib (it also links against Python framework)
install_name_tool -change \
  /Library/Frameworks/Python.framework/Versions/3.14/Python \
  @executable_path/../Frameworks/libpython3.14.dylib \
  tmp/bin/libepython.dylib

# Verify the change
otool -L tmp/bin/eigend | grep -i python
# Should show: @executable_path/../Frameworks/libpython3.14.dylib
```

Note: `libepython.dylib` is at `@rpath/libepython.dylib` — need to find its actual location.

#### Step 5: Test

```bash
# Run EigenD from the app bundle
open tmp/app/EigenD.app

# Or run directly and check logs
tmp/bin/eigend 2>&1 | head -20
```

#### Step 6: Verification

Check that the bundled Python is being used:
- Look for log messages about Python home directory
- Verify `sys.path` includes the bundled `python314/` directory
- Test a plugin that uses Python stdlib (e.g., plg_finger with `configparser`)

### 6.3 Success Criteria

- [ ] EigenD launches without `/Library/Frameworks/Python.framework` present (rename it temporarily to test)
- [ ] Plugin Python code runs correctly (e.g., fingering loading)
- [ ] All `*_native.so` modules import successfully
- [ ] No errors about missing stdlib modules

### 6.4 What This PoC Does NOT Cover

- Code signing / notarization
- Clean build system integration (still using `install_name_tool` hack)
- Windows or Linux
- The `USE_BUNDLED_PYTHON` build flag
- Stripping unused stdlib modules

**Important:** This PoC copies files from the already-installed system Python framework. This is a **quick dev-machine test only**. The production approach (§10) builds CPython from source with `--enable-shared` as a CMake external project — the standard, reproducible approach used by projects like Blender and Calibre.

---

## 7. Implementation Plan

### Phase 1: Research & Preparation (1-2 days)

1. **Complete macOS PoC** (§6) — validate the approach works end-to-end.
2. **Verify python-build-standalone** has Python 3.14 for Linux. If not, set up manylinux build.
3. **Test macOS python.org installer extraction** — verify we can extract just the pieces we need (for CI automation).
4. **Test Windows embeddable package** — verify it works with EigenD's embedding approach.

### Phase 2: Build System (2-3 days)

1. **Add Python download/extract step** to CMake/SCons:
   - Download Python 3.14.x embeddable package for Windows
   - Download Python 3.14.x framework for macOS
   - Build or download shared Python for Linux
2. **Modify `tools/detect.py`** — add "bundled" mode that points to the downloaded Python.
3. **Modify `pic_resources.cpp`** — update `get_pyprefix()` for bundled layout.
4. **Update RPATH/linker flags** — ensure native modules link against bundled libpython.

### Phase 3: Runtime Integration (1-2 days)

1. **Update `lib_juce/epython.cpp`** — adjust `py_startup()` for bundled paths.
2. **Test Python import system** — verify all stdlib imports resolve correctly.
3. **Test all native module imports** — verify `*_native.so` modules load.
4. **Test thread safety** — verify GIL handling with bundled libpython.

### Phase 4: Packaging (2-3 days)

1. **macOS:** Create `.app` bundle with embedded Python framework.
2. **Windows:** Create installer that places all files correctly.
3. **Linux:** Create AppImage or tar.gz with correct directory layout.
4. **Test on clean systems** — verify no system Python required.

### Phase 5: Cleanup & Polish (1-2 days)

1. **Remove old Python detection code** — no longer needed for runtime.
2. **Update documentation** — remove "install Python 3.14" from user docs.
3. **Update CI/CD** — build with bundled Python.
4. **Strip unused stdlib modules** — reduce bundle size (optional).

**Total estimated effort: ~7-12 days**

---

## 7. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Bundle size increase** | +30-80MB per platform | Strip unused stdlib modules; use zip imports on Windows |
| **C extension modules in lib-dynload** | `_sqlite3`, `_ssl`, `_socket` etc. must be bundled | Audit which are actually used; only bundle needed ones |
| **macOS code signing** | Bundled dylibs need signing | Add to existing signing pipeline |
| **Linux ABI compatibility** | libpython built on newer glibc may not run on older distros | Build on oldest supported distro (e.g., Ubuntu 20.04) |
| **Python version upgrade process** | Need to rebuild/re-bundle when upgrading Python | Script the download/extract; make it a build step |
| **GIL/compatibility** | Bundled libpython must match the headers used at build time | Ensure exact version match between build-time headers and bundled library |

---

## 8. Decisions & Resolved Questions

### 8.1 Stdlib Size — Keep Full Stdlib

**Decision:** Bundle the full Python standard library (~67MB on macOS 3.14, including `lib-dynload/`).

Rationale: 67MB is acceptable for modern download speeds and desktop storage. Keeping the full stdlib avoids the maintenance burden of maintaining an exclusion list and the risk of missing a transitive import. The threshold for concern would be >1GB.

### 8.2 Build-time Python Unaffected

**Decision:** `plg_synth/src/minblep.py` uses numpy/scipy at **build time only**. The build environment (`.venv_dev`) will continue to use a separate Python with whatever packages are needed. The embedding work is about **runtime Python only**.

### 8.3 System Python Fallback

**Decision:** Keep the option to use system Python as a fallback, controlled by a build flag (e.g., `USE_BUNDLED_PYTHON=ON/OFF`).

When the fallback is active, EigenD must **log clearly** which Python is being used:
```
[python] Using bundled Python 3.14.3 at: /app/Frameworks/libpython3.14.dylib
-- or --
[python] Using system Python 3.14.3 at: /Library/Frameworks/Python.framework
```

This is useful for development/debugging and as an escape hatch if the bundled Python has issues on a particular system.

### 8.4 Linux Distribution — AppImage

**Decision:** Target AppImage for Linux distribution. AppImage provides a self-contained single-file format that works across most Linux distributions.

The key challenge is **cross-distro ABI compatibility** — a libpython built on one distro may not run on another. This ties directly into Question 1 (pre-built vs build-from-source). See §8.6 below.

### 8.5 lib-dynload C Extension Modules

Based on the actual Python 3.14.3 installation on macOS, the `lib-dynload/` directory contains **76 `.so` files** (including test modules). After excluding test modules (`_test*`, `_xx*`), there are **~60 production modules**.

**Modules definitely needed** (based on stdlib imports found in §2.4):

| C Extension | Imported via | Notes |
|-------------|-------------|-------|
| `_sqlite3` | `sqlite3` | Loop database |
| `_socket` | `socket` | Stage server networking |
| `_ssl` | `ssl` (via `xmlrpc`, `urllib`) | HTTPS support |
| `_hashlib` | `hashlib` | Hashing in cmdline tools |
| `_json` | `json` | JSON speedup (pure Python fallback exists) |
| `_struct` | `struct` | Binary data packing |
| `_elementtree` | `xml.etree` | XML parsing |
| `pyexpat` | `xml.dom.*`, `xml.etree` | XML parsing |
| `_zlib` / `zlib` | `zlib`, `zipfile` | Compression |
| `_queue` | `queue` (via threading) | Thread-safe queues |
| `_heapq` | `heapq` | Heap queue (speedup) |
| `_random` | `random` | Random numbers |
| `math` | `math` | Math functions |
| `_datetime` | `datetime` | Date/time (speedup) |
| `_pickle` | `pickle` (transitive) | Object serialization |
| `_csv` | `csv` (transitive) | CSV parsing |
| `_bisect` | `bisect` (transitive) | Binary search |
| `_lsprof` | `cProfile` (transitive) | Profiling |
| `array` | `array` (transitive) | Array type |
| `binascii` | `binascii` | Binary/ASCII conversion |
| `_collections` | `collections` | OrderedDict speedup |
| `_weakref` | `weakref` | Weak references |
| `fcntl` | `fcntl` (transitive) | File control (Unix) |
| `select` | `select` (transitive) | I/O multiplexing |
| `unicodedata` | `unicodedata` (transitive) | Unicode database |
| `_decimal` | `decimal` (transitive) | Decimal math |
| `_multiprocessing` | `multiprocessing` (transitive) | Process management |
| `_posixsubprocess` | `subprocess` (transitive) | Subprocess management |
| `_ctypes` | `ctypes` (transitive) | C foreign function interface |
| `_asyncio` | `asyncio` (transitive) | Async I/O |
| `_blake2` | `hashlib` (transitive) | BLAKE2 hash |
| `_sha1`/`_sha2`/`_sha3`/`_md5` | `hashlib` (transitive) | Hash algorithms |
| `_hmac` | `hmac` (transitive) | HMAC |
| `_bz2` | `bz2` (transitive) | Bzip2 compression |
| `_lzma` | `lzma` (transitive) | LZMA compression |
| `_zstd` | `zstd` (transitive) | Zstandard compression |
| `_uuid` | `uuid` (transitive) | UUID generation |
| `_zoneinfo` | `zoneinfo` (transitive) | Timezone data |
| `_scproxy` | `urllib` (transitive, macOS) | System proxy config |
| `mmap` | `mmap` (transitive) | Memory-mapped files |
| `grp` | `grp` (transitive, Unix) | Group database |
| `resource` | `resource` (transitive, Unix) | Resource limits |
| `syslog` | `syslog` (transitive, Unix) | System logger |
| `termios` | `termios` (transitive, Unix) | Terminal I/O |
| `readline` | `readline` (transitive) | Line editing |
| `_curses`/`_curses_panel` | `curses` (transitive) | Terminal UI |
| `_dbm` | `dbm` (transitive) | Database |
| `_multibytecodec` + `_codecs_*` | Asian codec support | Text encoding |
| `_statistics` | `statistics` (transitive) | Statistics speedup |
| `_interpchannels`/`_interpqueues`/`_interpreters` | Sub-interpreters | Python 3.14 feature |
| `_remote_debugging` | Debug support | Remote debugging |
| `_posixshmem` | `multiprocessing` (transitive) | Shared memory |

**Decision:** Since we're keeping the full stdlib (§8.1), we bundle all of `lib-dynload/` (~60 modules, ~15MB). No need to cherry-pick. This list serves as documentation of what's actually used vs what's bundled but unused.

### 8.6 Linux: Pre-built Python Challenge

**The problem:** Unlike macOS and Windows, python.org does **not** provide pre-built binaries of CPython for Linux. Only source tarballs are available.

**Options for obtaining libpython for Linux:**

| Option | Pros | Cons |
|--------|------|------|
| **A. Build from source** | Full control over compile flags; can target old glibc for broad compatibility | Slow; adds complexity to CI; must maintain build scripts |
| **B. Use manylinux Docker images** | Standardized build environment; produces widely-compatible binaries | Requires Docker in CI; still effectively building from source |
| **C. Use conda-forge pre-built Python** | Pre-built; cross-platform; includes libpython | Adds conda as dependency; licensing considerations |
| **D. Extract from deadsnakes PPA** (Ubuntu) | Pre-built .deb packages | Ubuntu-specific; not universal |
| **E. Use python-build-standalone** (indygreg) | Pre-built, statically linked Python; no external deps; works on any Linux | Relatively new project; may not have 3.14 yet |

**Recommendation:** **Option E (python-build-standalone)** is the most promising. The [python-build-standalone](https://github.com/indygreg/python-build-standalone) project by Gregory Szorc provides pre-built, statically-linked Python distributions that run on any Linux distro (built on CentOS 7 for maximum glibc compatibility). These include `libpython3.14.so` and the full stdlib.

If python-build-standalone doesn't have 3.14 yet, fall back to **Option B** (manylinux build) as a one-time setup.

For macOS and Windows, python.org provides official pre-built binaries, so those are straightforward.

---

## 9. Updated Distribution Plan

### 9.1 macOS

```
EigenD.app/
└── Contents/
    ├── MacOS/
    │   └── eigend              (rpath = @executable_path/../Frameworks)
    ├── Frameworks/
    │   └── libpython3.14.dylib (built from source with --enable-shared)
    └── Resources/
        └── python314/          (full stdlib, ~67MB)
            ├── *.py
            └── lib-dynload/
                └── *.cpython-314-darwin.so
```

**Source:** Build CPython from source with `--enable-shared`. Bundle `libpython3.14.dylib` + `lib/python3.14/` from the install prefix.

### 9.2 Windows

```
EigenD/
├── eigend.exe
├── python314.dll              (from python.org Windows embeddable package)
├── python314.zip              (stdlib as zip, or directory)
└── modules/                   (EigenD Python modules)
```

**Source:** [python.org Windows embeddable package](https://www.python.org/downloads/windows/) — the standard, officially-supported approach for embedding Python on Windows. Available on each release page (e.g., `python-3.14.3-embed-amd64.zip`). Includes `python314.dll` + `python314.zip` (stdlib). Direct URL pattern: `https://www.python.org/ftp/python/3.14.X/python-3.14.X-embed-amd64.zip`

### 9.3 Linux (AppImage)

```
EigenD-x86_64.AppImage/
├── bin/
│   └── eigend                  (RPATH = $ORIGIN/../lib)
├── lib/
│   ├── libpython3.14.so.1.0   (built from source or python-build-standalone)
│   └── python314/             (full stdlib, ~67MB)
│       ├── *.py
│       └── lib-dynload/
│           └── *.cpython-314-x86_64-linux-gnu.so
└── share/
    └── eigend/
        └── modules/           (EigenD Python modules)
```

**Source:** Build CPython from source in a manylinux container (CentOS 7 glibc) for maximum cross-distro compatibility. Alternatively, python-build-standalone provides pre-built, statically-linked Python.

---

## 10. How to Obtain Python for Embedding

### 10.1 The Standard Approach: Build from Source

The standard, well-documented approach for embedding Python is to **build CPython from source** as part of your project's build. This is what Blender, Calibre, and most other projects that embed Python do. It gives you:

- **Reproducibility** — same source, same flags, same output every time
- **Control** — `--enable-shared`, `--prefix`, optimization flags, minimum macOS/iOS SDK
- **No dependency on external package formats** — no `.pkg` extraction, no fragile layout assumptions
- **Cross-platform consistency** — same build process on all platforms

Building CPython is straightforward:

```bash
# Download source
curl -O https://www.python.org/ftp/python/3.14.3/Python-3.14.3.tar.xz
tar xf Python-3.14.3.tar.xz
cd Python-3.14.3

# Configure for embedding (shared library)
./configure --enable-shared --prefix=/path/to/install

# Build and install
make -j$(nproc)
make install
```

This produces:
```
/path/to/install/
├── bin/python3.14
├── include/python3.14/       (headers for compiling against)
├── lib/
│   ├── libpython3.14.so/dylib  (the shared library to bundle)
│   └── python3.14/             (the standard library to bundle)
└── share/
```

### 10.2 Platform-Specific Notes

**macOS & Linux:** Build from source. This is the standard approach and is well-supported by CPython's build system. CMake can handle this via `ExternalProject_Add`.

**Windows:** The python.org **embeddable package** is the exception — it IS specifically designed for embedding scenarios. Building Python on Windows requires Visual Studio and is significantly more complex. The embeddable package is the standard approach on Windows and is stable/predictable (it's a simple `.zip` with a known layout).

**Linux cross-distro compatibility:** Build on the oldest glibc you need to support (e.g., CentOS 7 / manylinux2014 container) to ensure the resulting `libpython3.14.so` runs on older distros. Alternatively, python-build-standalone provides pre-built, statically-linked Python for Linux.

### 10.3 PoC vs Production

The Phase 0 PoC (§6) copies files from the already-installed system Python framework — this is a **quick dev-machine test only**, not the production approach. The production build will compile CPython from source as a CMake external project.

---

## 11. Updated Implementation Plan

### Phase 1: Research & Preparation (1-2 days)

1. **Test CPython build-from-source** on macOS — verify `--enable-shared` produces a usable `libpython3.14.dylib` + stdlib.
2. **Test Windows embeddable package** — verify it works with EigenD's embedding approach (this IS the standard Windows approach).
3. **Test Linux build-from-source** — verify in a manylinux container for cross-distro compatibility.
4. **Measure final bundle size impact** on each platform.

### Phase 2: Build System Integration (2-3 days)

1. **Add CPython as a CMake ExternalProject:**
   - macOS/Linux: Download source tarball, `./configure --enable-shared`, `make`, `make install` into build directory
   - Windows: Download [embeddable `.zip`](https://www.python.org/downloads/windows/), extract (standard Windows embedding approach)
2. **Add `USE_BUNDLED_PYTHON` build flag** (default ON for release builds, OFF for dev).
3. **Modify `tools/detect.py`** — add "bundled" mode that points to the built/downloaded Python.
4. **Port PoC changes to proper build integration:**
   - Replace `install_name_tool` hack with proper linker flags pointing to built Python
   - Make `get_pyprefix()` changes conditional on `USE_BUNDLED_PYTHON`
   - Update RPATH/linker flags for all native modules
5. **Clean up Windows/Linux `Python26` references** in `pic_resources.cpp`.

### Phase 3: Runtime Integration (1-2 days)

1. **Update `lib_juce/epython.cpp`** — adjust `py_startup()` for bundled paths; add logging of which Python is used.
2. **Test Python import system** — verify all stdlib imports resolve correctly.
3. **Test all native module imports** — verify `*_native.so` modules load.
4. **Test thread safety** — verify GIL handling with bundled libpython.

### Phase 4: Packaging (2-3 days)

1. **macOS:** Finalize `.app` bundle with embedded Python; test code signing.
2. **Windows:** Create installer that places all files correctly.
3. **Linux:** Create AppImage build script (separate from current RPM packaging).
4. **Test on clean systems** — verify no system Python required.

### Phase 5: Cleanup & Polish (1-2 days)

1. **Remove old Python detection code** — no longer needed for runtime (keep for fallback mode).
2. **Update documentation** — remove "install Python 3.14" from user docs.
3. **Update CI/CD** — build with bundled Python.

**Total estimated effort: ~7-12 days** (plus Phase 0 PoC: ~2-4 hours)

---

## 11. Open Questions (Remaining)

1. **python-build-standalone for Linux:** Does it have Python 3.14 builds? Need to verify. If not, what's the fallback plan — manylinux Docker build or conda-forge?

2. **macOS code signing:** Not planning to distribute via App Store. With a standard Apple Developer ID, signing a bundled `libpython3.14.dylib` should work for direct distribution (outside the App Store, no notarization required for user-launched apps). For notarization (if desired later), the bundled dylib needs to be signed with a valid Developer ID and meet hardened runtime requirements.

3. **Windows `Python26` cleanup:** Planned as a separate task, before or alongside the embedding work. The `pic_resources.cpp` Windows code still references `Python26` from the Python 2.6 era — needs updating to `Python314`.

4. **Linux `Python26` references:** Also need to verify and clean up any legacy Python references in Linux code paths.

5. **AppImage tooling:** Leave open for now. Currently using RPM for Linux distribution. Moving to AppImage is a separate packaging step. Which tool (`linuxdeploy`, `appimage-builder`, custom script) to be decided when we reach Linux packaging.

---

## 12. Summary

Embedding Python is **viable and recommended**. The project already embeds the Python interpreter (via `Py_Initialize()`), it just relies on an external Python installation for the shared library and standard library. The change is primarily about:

1. **Bundling** `libpython` + full stdlib (~67MB) with the application
2. **Pointing** `Py_SetPythonHome()` to the bundled location
3. **Adjusting** build system to link against the bundled library

**Key decisions made:**
- **Full stdlib** — bundle all ~67MB, no stripping needed
- **System Python fallback** — keep as option with clear logging
- **Linux** — use python-build-standalone (or manylinux fallback) for cross-distro compatibility; distribute as AppImage
- **macOS/Linux** — build CPython from source (`--enable-shared`), the standard approach for embedding
- **Windows** — use python.org embeddable package (the standard Windows embedding approach)
- **Build-time Python** — unaffected; numpy/scipy in minblep.py is build-time only

No changes to the PIP binding system, plugin architecture, or Python glue code are needed. All runtime Python dependencies are standard library only.
