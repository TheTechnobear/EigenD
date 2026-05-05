2025-11-17: updating test suide to use plugins and public rpc interface
2026-05-05: added tools/windows/eigend-msvc-env.sh and clang4win quick-start docs for sourcing VS Build Tools + LLVM env from MSYS2 bash.
2026-05-05: updated tools/windows/eigend-msvc-env.sh to use a temp .cmd runner with vcvars64-first loading and VsDevCmd fallback to avoid MSYS2 pipe hangs.
2026-05-05: replaced cmd.exe-based env import in tools/windows/eigend-msvc-env.sh with direct MSVC/Windows SDK path discovery to eliminate terminal blocking.
2026-05-05: fixed Windows clang-cl toolchain path normalization to convert MSYS-style /c/... paths for lld-link; moved /std:c++17 to CXXFLAGS to avoid warnings on .c files.
2026-05-05: improved incremental builds by skipping unconditional stage/pkg cleanup in normal builds and adding missing .exp placeholder creation for lld-link outputs to avoid perpetual relinks.
2026-05-05: moved /DJUCE_DLL from global clang-cl flags to JUCE-consuming Windows modules only (app_stage, app_eigend2, app_workbench, plg_audio, plg_host, plg_conductor, plg_midi, lib_midi) to keep defines targeted.
2026-05-06: fixed Windows JUCE linking by defining JUCE_DLL in lib_juce build (ensuring pijuce exports JUCE API symbols) and gating plg_audio ASIO factory usage behind JUCE_ASIO.
