2025-11-17: updating test suide to use plugins and public rpc interface
2026-05-05: added tools/windows/eigend-msvc-env.sh and clang4win quick-start docs for sourcing VS Build Tools + LLVM env from MSYS2 bash.
2026-05-05: updated tools/windows/eigend-msvc-env.sh to use a temp .cmd runner with vcvars64-first loading and VsDevCmd fallback to avoid MSYS2 pipe hangs.
2026-05-05: replaced cmd.exe-based env import in tools/windows/eigend-msvc-env.sh with direct MSVC/Windows SDK path discovery to eliminate terminal blocking.
