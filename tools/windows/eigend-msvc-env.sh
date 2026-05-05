#!/usr/bin/env bash
# Source this file from MSYS2 bash to load default Visual Studio Build Tools
# and LLVM toolchain environment variables for clang-cl/lld-link builds.

if [[ -n "${ZSH_VERSION:-}" ]]; then
    echo "error: this helper currently supports bash only" >&2
    return 1 2>/dev/null || exit 1
fi

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    echo "error: source this script instead of executing it:" >&2
    echo "  source tools/windows/eigend-msvc-env.sh" >&2
    exit 1
fi

set -u

# Allow override when vcvars64/VsDevCmd are installed in non-default locations.
if [[ -n "${EIGEND_VCVARS64:-}" ]]; then
    _vcvars64_path="$EIGEND_VCVARS64"
else
    _vcvars64_path=""
fi

if [[ -n "${EIGEND_VSDEVCMD:-}" ]]; then
    _vsdevcmd_path="$EIGEND_VSDEVCMD"
else
    _vswhere_exe="/c/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe"
    _vsdevcmd_path=""
    _vcvars64_path="${_vcvars64_path:-}"

    if [[ -f "$_vswhere_exe" ]]; then
        _vs_install_win="$("$_vswhere_exe" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath 2>/dev/null | tr -d '\r')"
        if [[ -n "$_vs_install_win" ]]; then
            _vs_install_unix="$(cygpath -u "$_vs_install_win" 2>/dev/null || true)"
            if [[ -n "$_vs_install_unix" && -f "$_vs_install_unix/Common7/Tools/VsDevCmd.bat" ]]; then
                _vsdevcmd_path="$_vs_install_unix/Common7/Tools/VsDevCmd.bat"
            fi
            if [[ -n "$_vs_install_unix" && -f "$_vs_install_unix/VC/Auxiliary/Build/vcvars64.bat" ]]; then
                _vcvars64_path="$_vs_install_unix/VC/Auxiliary/Build/vcvars64.bat"
            fi
        fi
    fi

    _vsdevcmd_candidates=(
        "/c/Program Files/Microsoft Visual Studio/2022/BuildTools/Common7/Tools/VsDevCmd.bat"
        "/c/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/Common7/Tools/VsDevCmd.bat"
        "/c/Program Files/Microsoft Visual Studio/2022/Community/Common7/Tools/VsDevCmd.bat"
        "/c/Program Files (x86)/Microsoft Visual Studio/2022/Community/Common7/Tools/VsDevCmd.bat"
        "/c/Program Files/Microsoft Visual Studio/2022/Professional/Common7/Tools/VsDevCmd.bat"
        "/c/Program Files (x86)/Microsoft Visual Studio/2022/Professional/Common7/Tools/VsDevCmd.bat"
        "/c/Program Files/Microsoft Visual Studio/2022/Enterprise/Common7/Tools/VsDevCmd.bat"
        "/c/Program Files (x86)/Microsoft Visual Studio/2022/Enterprise/Common7/Tools/VsDevCmd.bat"
        "/c/Program Files/Microsoft Visual Studio/2022/Preview/Common7/Tools/VsDevCmd.bat"
        "/c/Program Files (x86)/Microsoft Visual Studio/2022/Preview/Common7/Tools/VsDevCmd.bat"
    )

    if [[ -z "$_vsdevcmd_path" ]]; then
        for _candidate in "${_vsdevcmd_candidates[@]}"; do
            if [[ -f "$_candidate" ]]; then
                _vsdevcmd_path="$_candidate"
                break
            fi
        done
    fi
fi

if [[ -z "${_vcvars64_path:-}" || ! -f "$_vcvars64_path" ]]; then
    _vcvars64_candidates=(
        "/c/Program Files/Microsoft Visual Studio/2022/BuildTools/VC/Auxiliary/Build/vcvars64.bat"
        "/c/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Auxiliary/Build/vcvars64.bat"
        "/c/Program Files/Microsoft Visual Studio/2022/Community/VC/Auxiliary/Build/vcvars64.bat"
        "/c/Program Files (x86)/Microsoft Visual Studio/2022/Community/VC/Auxiliary/Build/vcvars64.bat"
        "/c/Program Files/Microsoft Visual Studio/2022/Professional/VC/Auxiliary/Build/vcvars64.bat"
        "/c/Program Files (x86)/Microsoft Visual Studio/2022/Professional/VC/Auxiliary/Build/vcvars64.bat"
        "/c/Program Files/Microsoft Visual Studio/2022/Enterprise/VC/Auxiliary/Build/vcvars64.bat"
        "/c/Program Files (x86)/Microsoft Visual Studio/2022/Enterprise/VC/Auxiliary/Build/vcvars64.bat"
        "/c/Program Files/Microsoft Visual Studio/2022/Preview/VC/Auxiliary/Build/vcvars64.bat"
        "/c/Program Files (x86)/Microsoft Visual Studio/2022/Preview/VC/Auxiliary/Build/vcvars64.bat"
    )

    for _candidate in "${_vcvars64_candidates[@]}"; do
        if [[ -f "$_candidate" ]]; then
            _vcvars64_path="$_candidate"
            break
        fi
    done
fi

if [[ -z "${_vcvars64_path:-}" || ! -f "$_vcvars64_path" ]]; then
    echo "error: vcvars64.bat not found." >&2
    echo "set EIGEND_VCVARS64 to the full path if your install is non-default." >&2
    return 1 2>/dev/null || exit 1
fi

# Optional LLVM override. Defaults to a standard LLVM for Windows install.
_llvm_bin_win="${EIGEND_LLVM_BIN_WIN:-C:\\Program Files\\LLVM\\bin}"
_llvm_bin_unix="$(cygpath -u "$_llvm_bin_win" 2>/dev/null || true)"

_vcvars64_dir_unix="$(dirname "$_vcvars64_path")"
_vc_aux_dir_unix="$(dirname "$_vcvars64_dir_unix")"
_vc_root_unix="$(dirname "$_vc_aux_dir_unix")"
_vs_install_unix="$(dirname "$(dirname "$(dirname "$_vc_root_unix")")")"
_msvc_tools_root_unix="$_vc_root_unix/Tools/MSVC"

if [[ ! -d "$_msvc_tools_root_unix" ]]; then
    echo "error: MSVC tools root not found at $_msvc_tools_root_unix" >&2
    return 1 2>/dev/null || exit 1
fi

_msvc_ver_dir_unix="$(find "$_msvc_tools_root_unix" -mindepth 1 -maxdepth 1 -type d | sort -V | tail -n 1)"
if [[ -z "$_msvc_ver_dir_unix" || ! -d "$_msvc_ver_dir_unix" ]]; then
    echo "error: no MSVC version directory found under $_msvc_tools_root_unix" >&2
    return 1 2>/dev/null || exit 1
fi

_msvc_bin_unix="$_msvc_ver_dir_unix/bin/Hostx64/x64"
_msvc_include_unix="$_msvc_ver_dir_unix/include"
_msvc_lib_unix="$_msvc_ver_dir_unix/lib/x64"

if [[ ! -d "$_msvc_bin_unix" || ! -d "$_msvc_include_unix" || ! -d "$_msvc_lib_unix" ]]; then
    echo "error: MSVC tool directories are incomplete under $_msvc_ver_dir_unix" >&2
    return 1 2>/dev/null || exit 1
fi

_winsdk_root_candidates=(
    "${EIGEND_WINSDK_ROOT:-}"
    "/c/Program Files (x86)/Windows Kits/10"
    "/c/Program Files/Windows Kits/10"
)
_winsdk_root_unix=""
for _candidate in "${_winsdk_root_candidates[@]}"; do
    [[ -z "$_candidate" ]] && continue
    if [[ -d "$_candidate" ]]; then
        _winsdk_root_unix="$_candidate"
        break
    fi
done

if [[ -z "$_winsdk_root_unix" ]]; then
    echo "error: Windows SDK root not found (expected Windows Kits/10)." >&2
    return 1 2>/dev/null || exit 1
fi

_winsdk_include_base_unix="$_winsdk_root_unix/Include"
_winsdk_lib_base_unix="$_winsdk_root_unix/Lib"

if [[ ! -d "$_winsdk_include_base_unix" || ! -d "$_winsdk_lib_base_unix" ]]; then
    echo "error: Windows SDK Include/Lib folders missing under $_winsdk_root_unix" >&2
    return 1 2>/dev/null || exit 1
fi

_winsdk_ver_dir_unix="$(find "$_winsdk_include_base_unix" -mindepth 1 -maxdepth 1 -type d | sort -V | tail -n 1)"
if [[ -z "$_winsdk_ver_dir_unix" || ! -d "$_winsdk_ver_dir_unix" ]]; then
    echo "error: no Windows SDK include version found under $_winsdk_include_base_unix" >&2
    return 1 2>/dev/null || exit 1
fi

_winsdk_ver="$(basename "$_winsdk_ver_dir_unix")"
_winsdk_lib_ver_dir_unix="$_winsdk_lib_base_unix/$_winsdk_ver"

if [[ ! -d "$_winsdk_lib_ver_dir_unix" ]]; then
    _winsdk_lib_ver_dir_unix="$(find "$_winsdk_lib_base_unix" -mindepth 1 -maxdepth 1 -type d | sort -V | tail -n 1)"
fi

if [[ -z "$_winsdk_lib_ver_dir_unix" || ! -d "$_winsdk_lib_ver_dir_unix" ]]; then
    echo "error: no Windows SDK lib version found under $_winsdk_lib_base_unix" >&2
    return 1 2>/dev/null || exit 1
fi

_winsdk_ver="$(basename "$_winsdk_lib_ver_dir_unix")"
_winsdk_include_ucrt_unix="$_winsdk_include_base_unix/$_winsdk_ver/ucrt"
_winsdk_include_um_unix="$_winsdk_include_base_unix/$_winsdk_ver/um"
_winsdk_include_shared_unix="$_winsdk_include_base_unix/$_winsdk_ver/shared"
_winsdk_include_winrt_unix="$_winsdk_include_base_unix/$_winsdk_ver/winrt"
_winsdk_include_cppwinrt_unix="$_winsdk_include_base_unix/$_winsdk_ver/cppwinrt"
_winsdk_lib_ucrt_unix="$_winsdk_lib_base_unix/$_winsdk_ver/ucrt/x64"
_winsdk_lib_um_unix="$_winsdk_lib_base_unix/$_winsdk_ver/um/x64"

if [[ ! -d "$_winsdk_include_ucrt_unix" || ! -d "$_winsdk_include_um_unix" || ! -d "$_winsdk_lib_ucrt_unix" || ! -d "$_winsdk_lib_um_unix" ]]; then
    echo "error: Windows SDK include/lib x64 directories are incomplete for version $_winsdk_ver" >&2
    return 1 2>/dev/null || exit 1
fi

_winsdk_bin_x64_unix="$_winsdk_root_unix/bin/$_winsdk_ver/x64"

_msvc_include_win="$(cygpath -w "$_msvc_include_unix")"
_winsdk_include_ucrt_win="$(cygpath -w "$_winsdk_include_ucrt_unix")"
_winsdk_include_um_win="$(cygpath -w "$_winsdk_include_um_unix")"
_winsdk_include_shared_win="$(cygpath -w "$_winsdk_include_shared_unix")"
_winsdk_include_winrt_win="$(cygpath -w "$_winsdk_include_winrt_unix")"
_winsdk_include_cppwinrt_win="$(cygpath -w "$_winsdk_include_cppwinrt_unix")"
_msvc_lib_win="$(cygpath -w "$_msvc_lib_unix")"
_winsdk_lib_ucrt_win="$(cygpath -w "$_winsdk_lib_ucrt_unix")"
_winsdk_lib_um_win="$(cygpath -w "$_winsdk_lib_um_unix")"
_msvc_tools_install_win="$(cygpath -w "$_msvc_ver_dir_unix")"
_winsdk_root_win="$(cygpath -w "$_winsdk_root_unix")"

export INCLUDE="$_msvc_include_win;$_winsdk_include_ucrt_win;$_winsdk_include_um_win;$_winsdk_include_shared_win;$_winsdk_include_winrt_win;$_winsdk_include_cppwinrt_win"
export LIB="$_msvc_lib_win;$_winsdk_lib_ucrt_win;$_winsdk_lib_um_win"
export LIBPATH="$LIB"
export VCToolsInstallDir="$_msvc_tools_install_win\\"
export VCINSTALLDIR="$(cygpath -w "$_vc_root_unix")\\"
export UniversalCRTSdkDir="$_winsdk_root_win\\"
export WindowsSdkDir="$_winsdk_root_win\\"
export WindowsSDKVersion="$_winsdk_ver\\"

_prepend_path_parts=(
    "$_msvc_bin_unix"
)

if [[ -d "$_winsdk_bin_x64_unix" ]]; then
    _prepend_path_parts+=("$_winsdk_bin_x64_unix")
fi

if [[ -n "$_llvm_bin_unix" && -d "$_llvm_bin_unix" ]]; then
    _prepend_path_parts+=("$_llvm_bin_unix")
fi

for _part in "${_prepend_path_parts[@]}"; do
    case ":$PATH:" in
        *":$_part:"*) ;;
        *) PATH="$_part:$PATH" ;;
    esac
done
export PATH

hash -r

echo "EigenD Windows toolchain environment loaded."
echo "  vcvars64: $_vcvars64_path"
echo "  VS install: $_vs_install_unix"
echo "  MSVC tools: $_msvc_ver_dir_unix"
echo "  Windows SDK: $_winsdk_root_unix (version $_winsdk_ver)"
if [[ -n "$_llvm_bin_unix" ]]; then
    echo "  LLVM bin: $_llvm_bin_unix"
fi

if command -v clang-cl >/dev/null 2>&1; then
    echo "  clang-cl: $(command -v clang-cl)"
else
    echo "  clang-cl: not found on PATH" >&2
fi

if command -v lld-link >/dev/null 2>&1; then
    echo "  lld-link: $(command -v lld-link)"
else
    echo "  lld-link: not found on PATH" >&2
fi

# ---------------------------------------------------------------------------
# Sanity-check that the resolved headers and libs are actually present.
# Errors here mean the MSVC/SDK install is incomplete or paths are wrong.
# ---------------------------------------------------------------------------
_env_ok=1
# Save paths needed for validation before the cleanup unset block below.
_chk_msvc_inc="$_msvc_include_unix"
_chk_msvc_lib="$_msvc_lib_unix"
_chk_ucrt_inc="$_winsdk_include_ucrt_unix"
_chk_um_inc="$_winsdk_include_um_unix"
_chk_ucrt_lib="$_winsdk_lib_ucrt_unix"
_chk_um_lib="$_winsdk_lib_um_unix"

_check_header() {
    local desc="$1" path="$2"
    if [[ ! -f "$path" ]]; then
        echo "  MISSING header [$desc]: $path" >&2
        _env_ok=0
    fi
}

_check_lib() {
    local desc="$1" path="$2"
    if [[ ! -f "$path" ]]; then
        echo "  MISSING lib    [$desc]: $path" >&2
        _env_ok=0
    fi
}

# MSVC CRT headers
_check_header "vcruntime.h"        "$_chk_msvc_inc/vcruntime.h"
_check_header "stdint.h (msvc)"    "$_chk_msvc_inc/stdint.h"
# UCRT headers
_check_header "stdio.h (ucrt)"     "$_chk_ucrt_inc/stdio.h"
_check_header "stdint.h (ucrt)"    "$_chk_ucrt_inc/stdint.h"
# Windows SDK headers
_check_header "windows.h"          "$_chk_um_inc/Windows.h"
_check_header "d2d1.h"             "$_chk_um_inc/d2d1.h"
_check_header "dcomp.h"            "$_chk_um_inc/dcomp.h"
# Import libs
_check_lib    "kernel32.lib"       "$_chk_um_lib/kernel32.lib"
_check_lib    "ucrt.lib"           "$_chk_ucrt_lib/ucrt.lib"
_check_lib    "msvcrt.lib"         "$_chk_msvc_lib/msvcrt.lib"

if [[ "$_env_ok" -eq 1 ]]; then
    echo "  environment check: OK"
else
    echo "  environment check: some headers/libs are MISSING (see above)" >&2
fi

unset -f _check_header _check_lib
unset _env_ok _chk_msvc_inc _chk_msvc_lib _chk_ucrt_inc _chk_um_inc _chk_ucrt_lib _chk_um_lib

unset _candidate _line _llvm_bin_unix _llvm_bin_win
unset _msvc_bin_unix _msvc_include_unix _msvc_include_win _msvc_lib_unix _msvc_lib_win
unset _msvc_tools_install_win _msvc_tools_root_unix _msvc_ver_dir_unix
unset _part _prepend_path_parts
unset _vcvars64_candidates _vcvars64_path _vc_aux_dir_unix _vc_root_unix _vcvars64_dir_unix
unset _vs_install_unix _vs_install_win
unset _winsdk_bin_x64_unix _winsdk_include_base_unix _winsdk_include_cppwinrt_unix
unset _winsdk_include_cppwinrt_win _winsdk_include_shared_unix _winsdk_include_shared_win
unset _winsdk_include_ucrt_unix _winsdk_include_ucrt_win _winsdk_include_um_unix
unset _winsdk_include_um_win _winsdk_include_ver_dir_unix _winsdk_include_winrt_unix
unset _winsdk_include_winrt_win _winsdk_lib_base_unix _winsdk_lib_ucrt_unix
unset _winsdk_lib_ucrt_win _winsdk_lib_um_unix _winsdk_lib_um_win _winsdk_lib_ver_dir_unix
unset _winsdk_root_candidates _winsdk_root_unix _winsdk_root_win _winsdk_ver
unset _vsdevcmd_candidates _vsdevcmd_path _vswhere_exe
unset _vsdevcmd_win
