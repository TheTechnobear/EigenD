# C++17 Migration Progress

**Date Started:** 2025-11-10  
**Date Completed:** 2025-11-10  
**Reason:** JUCE 8.0.10 requires C++17 or later

## Impact Summary by Module

**Testing Priority Guide:** H=High, M=Medium, L=Low

| Module/Library | Changes | Impact | Notes |
|----------------|---------|--------|-------|
| plg_keyboard | auto_ptr(23) | **H** | Most instances, core key handling |
| plg_arranger | auto_ptr(7) | **M** | Mode controllers, loop handling |
| plg_host | auto_ptr(7) | **M** | Plugin hosting, MIDI params |
| plg_pkbd | auto_ptr(5) | **M** | Pico keyboard, strips & breath |
| plg_ukbd | auto_ptr(4) | **L** | Micro keyboard, simple wiring |
| piagent | auto_ptr(4) | **L** | Clock sync, exception safety only |
| lib_midi | auto_ptr(2) | **L** | MIDI param inputs |
| plg_audio | auto_ptr(1) | **L** | Audio output |
| plg_rig | auto_ptr(1) | **L** | Rig connector |
| piw | auto_ptr(1) | **L** | Wire connector |
| tools/* | compiler flags | **L** | Build system only |

**Cross-module Risk:** Low - All instances follow same exception-safe wrapper pattern

## Build System Changes

### ✅ Completed
- **tools/darwin_tools.py**: Changed `-std=c++11` → `-std=c++17` for all macOS platforms
- **tools/linux_tools.py**: Changed `-std=c++11` → `-std=c++17`
- Windows uses MSVC which defaults to latest standard

## Code Changes Required

### 1. std::auto_ptr → std::unique_ptr
**Status:** ✅ COMPLETED (2025-11-10)  
**Risk Level:** ⚠️ MEDIUM - Ownership semantics may differ  
**Impact:** std::auto_ptr was deprecated in C++11 and removed in C++17

#### Files Changed (55 instances total):
- [x] `piagent/src/pia_clock.cpp` (4 instances)
- [x] `plg_arranger/src/arranger_view.cpp` (7 instances)
- [x] `plg_keyboard/src/kbd_bundle2.cpp` (23 instances)
- [x] `plg_host/src/host.cpp` (5 instances)
- [x] `plg_host/src/scanctl.cpp` (1 instance)
- [x] `plg_host/src/scan.cpp` (1 instance)
- [x] `piw/src/piw_connector.cpp` (1 instance)
- [x] `plg_rig/src/rig_connector.cpp` (1 instance)
- [x] `plg_ukbd/src/ukbd_bundle.cpp` (4 instances)
- [x] `plg_pkbd/src/pkbd_bundle.cpp` (5 instances)
- [x] `plg_audio/src/audio_juce.cpp` (1 instance)
- [x] `lib_midi/src/midi_converter.cpp` (2 instances)

#### ⚠️ OWNERSHIP PATTERN ANALYSIS:

**Pattern Found:**  
Most uses follow this exception-safe allocation pattern:
```cpp
Type *obj = new Type(...);
std::auto_ptr<Type> ptr(obj);  // Ensures cleanup if next line throws
container.push_back(obj);       // Container stores raw pointer
ptr.release();                  // Transfer ownership to container
```

Later, container manually `delete`s objects (e.g., `cancel_notify()` does `delete n`).

**Migration Strategy:** ✅ SAFE
- Replace `std::auto_ptr` → `std::unique_ptr` directly
- Keep `release()` calls - behavior is identical
- Smart pointer is only for exception safety during construction
- Container owns lifetime via manual `delete`

**Alternative Considered:** Storing `std::unique_ptr` in containers would be better modern C++ but requires:
- Changing container types (e.g., `std::list<notifier_t*>` → `std::list<std::unique_ptr<notifier_t>>`)
- Updating all iteration/access code
- Risk of breaking working code
- Should be separate refactoring effort

**Decision:** Keep current pattern, just update smart pointer type.

---

### 2. Other Potential C++17 Issues (To Be Discovered)

Issues will be added here as they're encountered during build.

---

## Testing Required

After migration:
- [ ] Build all targets successfully
- [ ] Test basic functionality
- [ ] Test plugins that use auto_ptr heavily (keyboard, host, arranger)
- [ ] Memory leak testing with valgrind/instruments
- [ ] Verify no ownership issues in containers

---

## Notes

- `lib_juce/juce/` submodule contains `std::auto_ptr` in AAX SDK headers but this is vendor code
- `vst3sdk/` contains some C++17 code but is external dependency
