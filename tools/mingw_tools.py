
#
# Copyright 2009 Eigenlabs Ltd.  http://www.eigenlabs.com
#
# This file is part of EigenD.
#
# EigenD is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EigenD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EigenD.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import os.path
import sys
import generic_tools

from os.path import join
from SCons.Util import Split


class PiMingwEnvironment(generic_tools.PiGenericEnvironment):
    """
    SCons environment for building EigenD with MinGW-w64 on Windows.

    Supports two modes:
      - Native Windows: run inside MSYS2 MinGW64/UCRT64 shell, no vcvars needed
      - Cross-compilation (Phase C): Linux/macOS host with x86_64-w64-mingw32- toolchain
        Set MINGW_PREFIX=x86_64-w64-mingw32- in environment.

    Phase A (current): compilation only, no packaging.
    Phase B (future): NSIS-based installer generation.
    Phase C (future): cross-compilation from Linux/macOS.
    """

    def __init__(self, cross_prefix=None):
        # Determine Python path.
        # Native Windows: Python.org Python (headers + libs for extension building).
        # Cross-compile: host Python runs SCons; PI_PYTHON_WIN must point to
        #   a Windows Python installation root for headers/libs.
        if sys.platform == 'win32':
            python_path = os.environ.get('PI_PYTHON', 'C:\\Python314\\python.exe')
        else:
            # Cross-compilation mode.  detect.py will run on the host, so point
            # PI_PYTHON at the host Python.  Headers/libs are handled via CPPPATH
            # and LIBPATH overrides (see NOTES_MINGW.md Phase C section).
            python_path = os.environ.get('PI_PYTHON', sys.executable)

        generic_tools.PiGenericEnvironment.__init__(
            self, 'win32-mingw64', 'EigenLabs', 'Belcanto',
            python=python_path
        )

        # Cross-compilation prefix (e.g. 'x86_64-w64-mingw32-')
        self._cross_prefix = cross_prefix or os.environ.get('MINGW_PREFIX', '')

        if sys.platform == 'win32' and not self._cross_prefix:
            # Native Windows build: let SCons locate MinGW from PATH.
            # The 'mingw' tool sets SHLIBSUFFIX='.dll', PROGSUFFIX='.exe', etc.
            self.Tool('mingw')
        else:
            # Cross-compile or explicit prefix.
            prefix = self._cross_prefix or 'x86_64-w64-mingw32-'
            self.Replace(CC=prefix + 'gcc')
            self.Replace(CXX=prefix + 'g++')
            self.Replace(AR=prefix + 'ar')
            self.Replace(RANLIB=prefix + 'ranlib')
            self.Replace(RC=prefix + 'windres')
            self.Replace(SHLIBPREFIX='')
            self.Replace(SHLIBSUFFIX='.dll')
            self.Replace(LIBPREFIX='lib')
            self.Replace(LIBSUFFIX='.a')
            self.Replace(PROGPREFIX='')
            self.Replace(PROGSUFFIX='.exe')
            self.Replace(SHLINK=prefix + 'g++')
            self.Replace(LINK=prefix + 'g++')
            self.Replace(SHLINKFLAGS=Split('-shared'))

        # Platform identity
        self.Replace(IS_WINDOWS=True)
        self.Replace(IS_MINGW=True)
        self.Replace(PI_PLATFORMTYPE='windows')

        # Python extension modules use .pyd on Windows regardless of compiler
        self.Replace(PI_MODPREFIX='')
        self.Replace(PI_MODSUFFIX='.pyd')
        self.Replace(PI_MODLINKFLAGS='$SHLINKFLAGS')

        # Stage/release directory layout
        self.Replace(RELEASESTAGEROOTDIR=join('$STAGEDIR'))
        self.Replace(RELEASESTAGEDIR=join('$STAGEDIR', '$PI_COLLECTION-$PI_RELEASE'))

        # GCC-style compiler flags for Windows target
        self.Append(CXXFLAGS=Split('-std=c++17'))
        self.Append(CCFLAGS=Split(
            '-DWIN32 -D_WIN32 -DWINDOWS -D_REENTRANT '
            '-O2 -msse2 -g '
            '-Wall -Wno-narrowing -Wno-deprecated-declarations '
            '-Wno-unused-function -Wno-unused-but-set-variable '
            '-Wno-format -fmessage-length=0 -fno-strict-aliasing'
        ))

        # LIBMAPPER wiring: append to link command strings (same as unix_tools)
        self.Append(SHLINKCOM=' $LIBMAPPER')
        self.Append(LINKCOM=' $LIBMAPPER')

        # Windows DLL linker flags
        self.Append(SHLINKFLAGS=Split('-Wl,--enable-auto-import'))
        self.Append(LINKFLAGS=Split('-Wl,--enable-auto-import'))

        # Windows system libraries available on all targets
        self.Append(LIBS=Split('shell32'))

        # Packaging state (populated by PiPackageInit / PiMergeModule from SConscripts)
        self.shared.merge_modules = []
        self.shared.package_init = []
        self.shared.shortcuts = {}

    # ------------------------------------------------------------------
    # Compiler helpers
    # ------------------------------------------------------------------

    def set_hidden(self, hidden):
        if hidden:
            self.Append(CCFLAGS='-fvisibility=hidden')

    def sign(self, tgt):
        # Code signing not yet implemented; would use signtool or osslsigncode
        pass

    def cache_dir(self):
        temp = os.environ.get('TEMP') or os.environ.get('TMP') or '/tmp'
        return os.path.join(temp, '.sconscache')

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def doenv(self):
        pth_file = self.File('env.sh', self.subst('#')).abspath
        pth_template = "export PATH=%(bindir)s:$PATH\n"
        pp = self.Dir(self['BINRUNDIR']).abspath
        pth_node = self.baker(pth_file, pth_template, bindir=pp)
        self.Alias('target-default', pth_node)

    def Initialise(self):
        generic_tools.PiGenericEnvironment.Initialise(self)

    def Finalise(self):
        generic_tools.PiGenericEnvironment.Finalise(self)
        self.doenv()
        # Phase B: packaging goes here; skipped for Phase A

    # ------------------------------------------------------------------
    # Packaging (Phase B stubs)
    # ------------------------------------------------------------------

    def make_package(self, package_name):
        # NSIS-based packaging will be added in Phase B (see NOTES_MINGW.md)
        print("NOTE: packaging not yet implemented for MinGW builds (Phase B)")
        return None

    def PiPackageInit(self, package, program, as_user=False, order=1):
        self.shared.package_init.append((package, program, as_user, order))

    def PiMergeModule(self, target):
        self.shared.merge_modules.append(self.File(target).srcnode().abspath)

    def PiReleaseFile(self, package, name, bigname):
        etc_env = self.Clone()
        etc_env.set_package(package)
        etc_env.Install(etc_env.subst('$ETCSTAGEDIR'), name)

    # ------------------------------------------------------------------
    # Build targets
    # ------------------------------------------------------------------

    def PiBinaryDLL(self, target, package=None):
        """Install a pre-built DLL (not compiled by this build)."""
        env = self.Clone()
        f_dll = env.File(target + '.dll')
        f_lib = env.File('lib' + target + '.dll.a')

        run_dll = env.Install(env.subst('$BINRUNDIR'), f_dll)
        env.Alias('target-runtime', run_dll)

        if package:
            env.set_package(package)
            env.Install(env.subst('$BINSTAGEDIR'), f_dll)

        if os.path.exists(f_lib.srcnode().abspath):
            run_lib = env.Install(env.subst('$BINRUNDIR'), f_lib)
            return env.addlibname(run_lib[0], target)
        return env.addlibname(run_dll[0], target)

    def PiRuntime(self, package):
        """Install the Python runtime DLL alongside the application."""
        if sys.platform != 'win32':
            return  # Cannot auto-detect when cross-compiling
        env = self.Clone()
        python_dir = os.path.dirname(self['PI_PYTHON'])
        import sysconfig as _sc
        ver = _sc.get_config_var('VERSION') or ('%d%d' % (sys.version_info.major, sys.version_info.minor))
        dll_name = 'python%s.dll' % ver
        target_path = os.path.join(python_dir, dll_name)
        if os.path.exists(target_path):
            f = env.File(target_path)
            run_file = env.Install(env.subst('$BINRUNDIR'), f)
            env.add_runtime_files(run_file)
            if package:
                env.set_package(package)
                env.Install(env.subst('$BINSTAGEDIR'), f)

    def PiSharedLibrary(self, target, sources, libraries=[], package=None, hidden=True,
                         deffile=None, per_agent=None, public=False, locked=False):
        env = self.Clone()
        env.Append(PILIBS=libraries)
        env.Append(CCFLAGS='-DBUILDING_%s' % target.upper())
        env.Replace(SHLIBNAME=target)
        env.set_hidden(hidden)
        env.set_agent_group(per_agent)

        objects = env.SharedObject(sources)
        self.Depends(objects, self.PiExports(target, package, public))

        if deffile:
            objects = list(objects) + [deffile]

        # SCons mingw tool: SharedLibrary produces [dll, import_lib]
        lib_result = env.SharedLibrary(target, objects)
        bin_dll = lib_result[0]
        bin_lib = lib_result[1] if len(lib_result) > 1 else lib_result[0]

        run_dll = env.Install(env.subst('$BINRUNDIR'), bin_dll)
        run_lib = env.Install(env.subst('$BINRUNDIR'), bin_lib)
        env.Depends(run_lib, run_dll)

        env.addlibuser(bin_dll, libraries)
        env.addlibname(run_lib[0], target, dependencies=libraries)

        inst_dll = []
        if package:
            env.set_package(package)
            inst_dll = env.Install(env.subst('$BINSTAGEDIR'), run_dll)
            if public:
                env.Install(env.subst('$BINSTAGEDIR'), run_lib)

        return inst_dll + [run_lib[0]]

    def PiProgram(self, name, sources, libraries=[], package=None, gui=False, hidden=True):
        env = self.Clone()
        env.Append(PILIBS=libraries)
        env.set_hidden(hidden)

        bld_binary = env.Program(name, env.Split(sources))
        env.add_runtime_user(bld_binary)
        env.addlibuser(bld_binary, libraries)

        run_binary = env.Install(env.subst('$BINRUNDIR'), bld_binary)
        inst_binary = []
        if package:
            env.set_package(package)
            inst_binary = env.Install(env.subst('$BINSTAGEDIR'), run_binary)

        return run_binary + inst_binary

    def PiGuiProgram(self, target, sources, bg=False, di=False, package=None,
                      appname=None, private=False, libraries=[], hidden=True):
        bigname = appname or target[0:1].upper() + target[1:].lower()
        if package and not private:
            self.shared.shortcuts.setdefault(package, []).append((bigname, 'bin\\%s.exe' % target))
        return self.PiProgram(target, sources, package=package, libraries=libraries, gui=True)

    def PiPythonwWrapper(self, name, pypackage, module, main, appname=None, bg=False,
                          di=False, private=False, usegil=False, package=None):
        bigname = appname or name[0:1].upper() + name[1:].lower()
        if package and not private:
            self.shared.shortcuts.setdefault(package, []).append((bigname, 'bin\\%s.exe' % name))
        return generic_tools.PiGenericEnvironment.PiPythonwWrapper(
            self, name, pypackage, module, main, appname=appname,
            bg=bg, di=di, private=private, usegil=usegil, package=package
        )

    def PiPipBinding(self, module, spec, locked=False, **kwds):
        return generic_tools.PiGenericEnvironment.PiPipBinding(self, module, spec, **kwds)

    def PiExternalRelease(self, version, compatible, organisation):
        if not self.PiRelease('contrib', compatible, compatible, organisation):
            return
        root = (os.environ.get('ProgramFiles(x86)')
                or os.environ.get('ProgramFiles', 'C:\\Program Files'))
        dist = os.path.join(root, 'Eigenlabs', 'release-%s' % version)
        self.Append(LIBPATH=[os.path.join(dist, 'bin')])
        self.Append(CPPPATH=[os.path.join(dist, 'include')])
