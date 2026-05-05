
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

"""
clangcl_tools.py – SCons build environment for EigenD on Windows using
  clang-cl (compiler) + lld-link (linker) + llvm-lib (archiver).

Key design points:
  - Extends PiGenericEnvironment (same as PiWindowsEnvironment).
  - Uses the SCons 'msvc' tool as a starting point so that SHLINKCOM,
    LINKCOM, etc. are standard string actions (not generators), which
    lets us Append() to them freely.
  - Overrides CC / CXX / AR / LINK / SHLINK to LLVM tools.
  - LIBMAPPER resolves PILIBS to .lib import libraries (not .dll.a).
  - MSVC-style compile/link flags (/EHsc, /MD, /O2, …).
  - DLL suffix: .dll  Import lib: .lib  Python module: .pyd
  - DEF files passed via /DEF: to lld-link (SHLINKFLAGS).
"""

import os
import os.path
import glob

import SCons.Environment
import generic_tools

from os.path import join
from SCons.Util import Split


class PiClangClEnvironment(generic_tools.PiGenericEnvironment):

    def __init__(self):
        generic_tools.PiGenericEnvironment.__init__(
            self,
            'win32',
            'EigenLabs',
            'Belcanto',
            python='C:\\Python314\\python.exe',
            # Tell SCons to initialise msvc tool so LINKCOM/SHLINKCOM are
            # standard string actions (not generators). We override the actual
            # executables below.
            tools=['msvc', 'mslink', 'mslib', 'msvs'],
            TARGET_ARCH='amd64',
        )

        # ---- Compiler / linker / archiver --------------------------------
        self.Replace(CC='clang-cl')
        self.Replace(CXX='clang-cl')
        self.Replace(AR='llvm-lib')
        self.Replace(LINK='lld-link')
        self.Replace(SHLINK='lld-link')

        # clang-cl does not use the MSVC response-file prefix (@) that SCons
        # inserts for long command lines; keep the default for now.

        # ---- Platform flags -----------------------------------------------
        self.Replace(IS_WINDOWS=True)
        self.Replace(PI_PLATFORMTYPE='windows')

        # ---- Output naming ---------------------------------------------------
        self.Replace(PI_MODPREFIX='')
        self.Replace(PI_MODSUFFIX='.pyd')
        self.Replace(PI_MODLINKFLAGS='$SHLINKFLAGS')

        # .dll for shared libs, .lib for import libs.
        self.Replace(SHLIBPREFIX='')
        self.Replace(SHLIBSUFFIX='.dll')
        self.Replace(LIBPREFIX='')
        self.Replace(LIBSUFFIX='.lib')

        # ---- Compile flags (MSVC-style) -------------------------------------
        self.Append(CCFLAGS=Split(
            '/EHsc /w34355 /MD /O2 /fp:fast'
            ' /DWIN32 /D_WIN64 /D_WINDOWS'
        ))

        # ---- Link flags (lld-link style) ------------------------------------
        # /MANIFEST, /INCREMENTAL:NO are lld-link compatible.
        self.Append(LINKFLAGS=Split('/INCREMENTAL:NO /LARGEADDRESSAWARE'))
        self.Append(SHLINKFLAGS=Split('/INCREMENTAL:NO'))

        # LIBMAPPER appends resolved .lib paths to linker command line.
        self.Append(SHLINK=' $LIBMAPPER')
        self.Append(LINK=' $LIBMAPPER')

        # Default Windows system libs every EigenD binary needs.
        self.Append(LIBS=Split('shell32'))

        # ---- Stage / release paths -----------------------------------------
        self.Replace(RELEASESTAGEROOTDIR=join('$STAGEDIR'))
        self.Replace(RELEASESTAGEDIR=join('$STAGEDIR', '$PI_COLLECTION-$PI_RELEASE'))

        # ---- Optional debug info -------------------------------------------
        if os.environ.get('PI_DEBUGBUILD'):
            self.Append(CCFLAGS=Split('/Zi'))
            self.Append(LINKFLAGS=Split('/DEBUG'))
            self.Append(SHLINKFLAGS=Split('/DEBUG'))

        self.shared.merge_modules = []
        self.shared.package_init = []
        self.shared.shortcuts = {}

    # ------------------------------------------------------------------
    # LIBMAPPER override
    # Resolves PILIBS to .lib import libs (not .dll.a as MinGW uses).
    # ------------------------------------------------------------------
    def libmapper(self, target, source, env, for_signature):
        libs = env['PILIBS']
        parts = []
        for lib_name in libs:
            ll = env.get_shlib(lib_name)
            if ll.libnode is None:
                parts.append('%s.lib' % lib_name)
            else:
                # libnode points to the installed .lib; replace suffix if DLL.
                lib_path = os.path.splitext(ll.libnode.abspath)[0] + '.lib'
                parts.append('"%s"' % lib_path)
        return ' '.join(parts)

    # ------------------------------------------------------------------
    # Toolchain no-ops / thin wrappers
    # sign: no-op in dev builds (no cert).
    # add_manifest: lld-link embeds a default manifest; mt post-step skipped.
    # set_subsystem: use editbin from Windows SDK (same as MSVC path).
    # ------------------------------------------------------------------
    def sign(self, tgt):
        pass

    def add_manifest(self, tgt):
        pass

    def set_subsystem(self, tgt, subsys):
        self.AddPostAction(tgt, 'editbin /nologo /subsystem:%s "${TARGET}"' % subsys)

    # ------------------------------------------------------------------
    # PiSharedLibrary
    # lld-link produces: .dll  .lib  .exp  (and .pdb when /DEBUG).
    # SCons mslink builder returns them in that order.
    # ------------------------------------------------------------------
    def PiSharedLibrary(self, target, sources, libraries=[],
                        package=None, hidden=True, deffile=None,
                        per_agent=None, public=False, locked=False):
        env = self.Clone()
        env.Append(PILIBS=libraries)
        env.Append(CCFLAGS='/DBUILDING_%s' % target.upper())
        env.Replace(SHLIBNAME=target)
        env.Replace(PDB='%s.pdb' % target)
        env.set_agent_group(per_agent)

        if deffile is not None:
            deffile_win = env.File(deffile).abspath.replace('/', '\\')
            env.Append(SHLINKFLAGS='/DEF:"%s"' % deffile_win)

        objects = env.SharedObject(sources)
        self.Depends(objects, self.PiExports(target, package, public))

        outputs = env.SharedLibrary(target, objects)
        # outputs[0] = .dll, outputs[-2] = .lib (before optional .pdb/.exp)
        bin_dll = outputs[0]
        # Locate the import lib among the outputs.
        bin_lib = next((o for o in outputs if str(o).endswith('.lib')), outputs[0])

        self.add_manifest(bin_dll)

        run_dll = env.Install(env.subst('$BINRUNDIR'), bin_dll)
        run_lib = env.Install(env.subst('$BINRUNDIR'), bin_lib)
        env.Depends(run_lib, run_dll)

        env.addlibuser(bin_dll, libraries)
        env.addlibname(run_lib[0], target, dependencies=libraries)

        inst_dll = []
        if package:
            env.set_package(package)
            inst_dll = env.Install(env.subst('$BINSTAGEDIR'), run_dll)
            self.sign(inst_dll)
            if public:
                env.Install(env.subst('$BINSTAGEDIR'), run_lib)

        return inst_dll + run_lib

    # ------------------------------------------------------------------
    # PiProgram / PiGuiProgram / PiPythonwWrapper
    # ------------------------------------------------------------------
    def PiProgram(self, name, sources, libraries=[], package=None, gui=False, hidden=True):
        env = self.Clone()
        env.Append(PILIBS=libraries)
        env.Replace(PDB='%s.pdb' % name)

        ico = self.subst('$PI_ICOLOGO')
        srcs = env.Split(sources)

        if ico and gui:
            rc_source = env.File('%s.rc' % name)
            rc_source_node = env.baker(rc_source, '1 ICON "%s"\r\n' % ico.replace('\\', '\\\\'))
            rc_res = env.Command('%s.res' % name, rc_source_node,
                                 'rc /R /Fo "${TARGET}" "${SOURCE}"')
            env.Depends(rc_res, ico)
            srcs.extend(rc_res)

        outputs = env.Program(name, srcs)
        bld_binary = (outputs[0],)

        self.add_manifest(bld_binary)
        env.add_runtime_user(bld_binary)
        env.addlibuser(bld_binary, libraries)

        rv = []
        run_binary = env.Install(env.subst('$BINRUNDIR'), bld_binary)
        rv.extend(run_binary)

        if gui:
            con_binary = env.InstallAs(
                env.File(join(env.subst('$BINRUNDIR'), '%s_con.exe' % name)),
                bld_binary)
            self.set_subsystem(run_binary, 'WINDOWS')
            self.set_subsystem(con_binary, 'CONSOLE')
            rv.extend(con_binary)
        else:
            self.set_subsystem(run_binary, 'CONSOLE')

        if package:
            env.set_package(package)
            inst_binary = env.Install(env.subst('$BINSTAGEDIR'), run_binary)
            self.sign(inst_binary)
            rv.extend(inst_binary)
            if gui:
                inst_con = env.Install(env.subst('$BINSTAGEDIR'), con_binary)
                self.sign(inst_con)
                rv.extend(inst_con)

        return rv

    def PiGuiProgram(self, target, sources, bg=False, di=False, package=None,
                     appname=None, private=False, libraries=[], hidden=True):
        bigname = appname or target[0:1].upper() + target[1:].lower()
        if package and not private:
            self.shared.shortcuts.setdefault(package, []).append(
                (bigname, 'bin\\%s.exe' % target))
        return self.PiProgram(target, sources, package=package,
                              libraries=libraries, gui=True)

    def PiPythonwWrapper(self, name, pypackage, module, main, appname=None,
                         bg=False, di=False, private=False, usegil=False, package=None):
        bigname = appname or name[0:1].upper() + name[1:].lower()
        if package and not private:
            self.shared.shortcuts.setdefault(package, []).append(
                (bigname, 'bin\\%s.exe' % name))
        return generic_tools.PiGenericEnvironment.PiPythonwWrapper(
            self, name, pypackage, module, main,
            appname=appname, bg=bg, di=di, private=private,
            usegil=usegil, package=package)

    # ------------------------------------------------------------------
    # PiRuntime – installs the Python DLL alongside EigenD binaries.
    # ------------------------------------------------------------------
    def PiRuntime(self, package):
        env = self.Clone()
        target = os.path.join(os.path.dirname(self['PI_PYTHON']), 'python314.dll')
        f = env.File(target)
        run_file = env.Install(env.subst('$BINRUNDIR'), f)
        env.add_runtime_files(run_file)
        if package:
            env.set_package(package)
            env.Install(env.subst('$BINSTAGEDIR'), f)

    # ------------------------------------------------------------------
    # PiBinaryDLL – installs a pre-built DLL + import lib.
    # ------------------------------------------------------------------
    def PiBinaryDLL(self, target, package=None):
        env = self.Clone()
        f_lib = env.File(target + '.lib')
        f_dll = env.File(target + '.dll')
        run_lib = env.Install(env.subst('$BINRUNDIR'), f_lib)
        run_dll = env.Install(env.subst('$BINRUNDIR'), f_dll)
        env.Depends(run_lib, run_dll)
        env.Alias('target-runtime', run_lib)
        if package:
            env.set_package(package)
            env.Install(env.subst('$BINSTAGEDIR'), f_dll)
        return env.addlibname(run_lib[0], target)

    # ------------------------------------------------------------------
    # PiPipBinding
    # ------------------------------------------------------------------
    def PiPipBinding(self, module, spec, locked=False, **kwds):
        env = self.Clone()
        if locked:
            env.Append(LINKFLAGS=env.subst('$LINKFLAGS_LOCKED'))
        return generic_tools.PiGenericEnvironment.PiPipBinding(env, module, spec, **kwds)

    # ------------------------------------------------------------------
    # Windows packaging helpers
    # ------------------------------------------------------------------
    def PiPackageInit(self, package, program, as_user=False, order=1):
        self.shared.package_init.append((package, program, as_user, order))

    def PiMergeModule(self, target):
        self.shared.merge_modules.append(self.File(target).srcnode().abspath)

    def PiReleaseFile(self, package, name, bigname):
        etc_env = self.Clone()
        etc_env.set_package(package)
        etc_env.Install(etc_env.subst('$ETCSTAGEDIR'), name)
        self.shared.shortcuts.setdefault(package, []).append(
            (bigname, 'etc\\%s\\%s' % (package, name)))

    def PiExternalRelease(self, version, compatible, organisation):
        if not self.PiRelease('contrib', compatible, compatible, organisation):
            return
        root = os.environ.get('ProgramFiles(x86)') or os.environ.get('ProgramFiles')
        dist = os.path.join(root, 'Eigenlabs', 'release-%s' % version)
        self.Append(LIBPATH=[os.path.join(dist, 'bin')])
        self.Append(CPPPATH=[os.path.join(dist, 'include')])

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------
    def cache_dir(self):
        return os.path.join(os.environ.get('TEMP', 'C:\\Temp'), '.sconscache')

    def doenv(self):
        pth_file = self.File('env.cmd', self.subst('#')).abspath
        pth_template = 'set PATH=%(bindir)s;%%PATH%%\n'
        pp = self.Dir(self['BINRUNDIR']).abspath
        pth_node = self.baker(pth_file, pth_template, bindir=pp)
        self.Alias('target-default', pth_node)
