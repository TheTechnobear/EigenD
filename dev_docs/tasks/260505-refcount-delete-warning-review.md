# Task: Review `-Wfree-nonheap-object` Warning in Refcounted Delete Path

Date: 2026-05-05
Scope: GCC/MinGW warnings emitted while building `piw/src/piw_lights.cpp` and related units.

## Error Detail

Observed warning chain (representative):
- Inlined call stack reaches `pic::counted_t::counted_deallocate()` and `pic::counted_t::~counted_t()`.
- Compiler reports:
  - `warning: 'void operator delete(void*, std::size_t)' called on pointer ... with nonzero offset 32 [-Wfree-nonheap-object]`
- Primary location in project code:
  - `picross/pic_ref.h` (`counted_t::counted_deallocate()` uses `delete this;`)
- Triggered through type:
  - `light_t` in `piw/src/piw_lights.cpp` (multiple inheritance including `pic::counted_t` and `virtual pic::lckobject_t`).

## Findings

1. Deallocation is initiated from base class refcount logic (`pic::counted_t`).
2. The triggered concrete type (`light_t`) participates in mixed/virtual inheritance.
3. GCC 16 inlining appears to lose enough provenance to conclude delete target is a full object and emits `-Wfree-nonheap-object`.
4. This warning pattern is likely a compiler false positive for this path, but the inheritance/deallocation design makes static analysis harder and can mask real ownership bugs.
5. Similar inheritance patterns exist elsewhere (some classes already use `virtual public pic::counted_t`), indicating style inconsistency.

## Possible Solutions

### Option A: Local fix on `light_t` (recommended now)
- Add in `light_t`:
  - `virtual void counted_deallocate() override { delete this; }`
- Keep deletion anchored in the most-derived class for this warning site.

Pros:
- Minimal, low-risk, very targeted.
- Often silences this warning for GCC in heavily inlined paths.

Cons:
- Does not address consistency across all refcounted classes.

### Option B: Normalize inheritance style for refcounted/lckobject types
- Prefer a consistent pattern such as:
  - `virtual public pic::counted_t`
  - `virtual public pic::lckobject_t`
- Apply to classes that use both refcounting and custom alloc/dealloc semantics.

Pros:
- Reduces future ambiguity and warning recurrence.

Cons:
- Medium-to-high churn across many files.
- ABI/layout and subtle behavior risks in legacy code.

### Option C: Refactor base deallocation mechanism
- Rework `counted_t`/`atomic_counted_t` deallocation path to reduce `delete this` ambiguity (e.g., out-of-line non-inlined helper, stricter ownership contract).

Pros:
- Strong long-term design clarity.

Cons:
- Highest complexity/risk.
- Requires broad testing of object lifetime behavior.

### Option D: Suppress compiler warning only
- Add targeted warning suppression for this diagnostic.

Pros:
- Fastest path to quiet logs.

Cons:
- Hides potential real defects.
- Not recommended unless code-level options are impractical.

## Risk Assessment

### Current warning if left unresolved
- Runtime risk: Low-to-Medium (likely false positive here, but pattern is fragile).
- Maintenance risk: Medium (difficult-to-reason ownership/deallocation path).
- Tooling risk: High (warning noise can hide new real problems).

### Option risk summary
- Option A risk: Low
- Option B risk: Medium-High
- Option C risk: High
- Option D risk: Medium (process risk; technical debt)

## Recommendation

1. Implement Option A immediately for `light_t` to reduce noise and local ambiguity.
2. Rebuild and verify warning reduction in affected units.
3. If recurring in other types, schedule Option B as a separate cleanup task with test coverage focus.

## Verification Plan

- Rebuild on Windows MinGW toolchain.
- Confirm whether `-Wfree-nonheap-object` for `light_t` path is removed.
- Ensure no new warnings/errors introduced by override.
- Spot-check runtime behavior for light source creation/destruction paths.
