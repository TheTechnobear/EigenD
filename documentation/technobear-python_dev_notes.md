# Overview 
Development notes on moving EigenD to Python 3.
Idea is just to gather my thoughts, and collect info as I start ! 


# Background
Python 2.7, used by EigenD has been deprecated for many years.. and is no longer supported
Apple completly removed Python 2.7 in macOS 12.3.
we are unable to build Python 2.7 for Apple Silicon (apple did not release approach source changes)

really EigenD and Python 2.7 has been an issue for years now, starting when 32 bit support was dropped by Apple.
at that time all the python based UIs (EigenBrowser/EigenCommander) stopped working, since we could not get 64 bit versions of some the python libraries.

we therefore need to 'bite the bullet' and upgrade EigenD to python 3.

I posted a few more details here:  https://community.polyexpression.com/t/eigend-broken-w-macos-12-3


# Why have I not done before?
I already tried converting to Python 3, quite a while back, and unfortunaltey, I found EigenD would get into some kind of 'lock' issue.
basically, some complexity I believe with the way the global memory allocator work in Python, and likely some big changes in v2 vs v3.
I tried debugging, but after a few days gave up, as it was unclear why we were getting the deadlock scenario.

unfortunatly its a pretty low-level python issue, which I dont have experience with - and very difficult to debug.. so very time consuming, and frustrating.
so after a while, I shelved it... then of course, afer a while, Id forgotten what id tried, so would have to start from scratch.
... which is where Im at now ! 


# Important Note: 
the way forward is NEW software only, I dont have time/resources to do backwards compatiblity.
so we are talking python3 / 64 bit only... no attempts at 32 bit/python 2 back compatiblity.
(for older platforms need to use older released version on EigenD)

Im targeting python 3.10.5 directly from python.org
this will require users to also install from python.org
this will shield us from Apple OS changes, and also be consistent for both windows/mac users.
(linux : you should just be able to install 3.10 from distro tools)


# Final Goal
move all plaforms to Python 3, modern version - only (see above) 
minimal install possible.. whatever that means... Id like to use system python where possible.

# Todo
this is a working in progress, check the python_dev_todo.md for what I already know is still ncessary to do.



# Disclaimer
this document is not intended to be complete, just notes... 
ive tried many things not mentioned here, and this doc is likely out of date , and/or missing details.
the only true reference is the code ... and even that is 'work in progress', so some decisions Ive made may not be coded yet ;) 


----------------------------------------------------------------------------------------------------------------------------------
# Tracking / Comments
discussing progress etc on this topic
https://community.polyexpression.com/t/eigend-upgrade-to-python-3




# Approach
need to 'prototype issue' initally.
ignore complications like installation and cross-platform  - so just Mac M1, as thats the pressing issue.
focus on python 3 (code) changes required, then we can minise install requirements once we know whats needed


# macOS 12.3 - what do we have?
(see above link to polyexpresson.com)

EigenD% otool -L /usr/bin/python3 
/usr/bin/python3:
	/usr/lib/libxcselect.dylib (compatibility version 1.0.0, current version 1.0.0)
	/usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1311.100.3)

frameworks as part of Xcode.
/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework


later on a 'clean mac', I need to see if this framework exists... or do we even need it?

also we could install complete Python3 from python.org, it'll likely install in 
/System/Library/Frameworks

DECISION NOTE: will use python.org, Python 3.10.5 at present.

# Commander/Browser
these python apps are already broken, as such are liely to be discontinued 'officially'
however, 
moving to Python3 may open up the opportunity of importing new versions of the libraries they use.this could 'unbreak' them.
the 'issue' is even if these libraries exists as python3 (with apple silicon support), 
they could require major changes to get working again... so the future is still very much 'in doubt' for them
they do NOT have any priority at this time



# EigenD - which python used?
tools/darwin_tools.py - line 111
```
unix_tools.PiUnixEnvironment.__init__(self,platform,'usr/local/pi','Library/Eigenlabs',python='/Library/Frameworks/Python.framework/Versions/2.7/bin/python')
```
can we just use /usr/bin/python3?


Important Note:
for future compatibilty purposes, Ive decided to get users to install from python.org.
this means I can target the latest python version (currently 3.10.5)



## Python Changes required

https://www.cmi.ac.in/~madhavan/courses/prog2-2011/docs/diveintopython3/porting-code-to-python-3-with-2to3.html




### tools

dict haskey removed, change to in

so 
    if cv.has_key('PYTHONFRAMEWORK'):

to
    if 'PYTHONFRAMEWORK' in cv:

----------------

print need brackets
 print ';'.join(do_detect()) ... errror

 print (';'.join(do_detect())) ... ok


----------------

exception needs 'as'

tmp/plugins/Eigenlabs/plg_arranger/Manifest (build_manifest(["tmp/plugins/Eigenlabs/plg_arranger/Manifest"],)
tmp/plugins/Eigenlabs/plg_arranger/__init__.pyc ("/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.8/Resources/Python.app/Contents/MacOS/Python")
  File "/Users/kodiak/projects/EigenD/tools/compile.py", line 31
    except py_compile.PyCompileError,err:
                                    ^
SyntaxError: invalid syntax
scons: *** [tmp/plugins/Eigenlabs/plg_arranger/__init__.pyc] Error 1
scons: building terminated because of errors.
make: *** [all] Error 2

except py_compile.PyCompileError as err:



----------------


raise needs brackets

  File "/Users/kodiak/projects/EigenD/tools/pip_cmd/yacc.py", line 127
    raise ValueError, "Expected a positive value"
                    ^


raise ValueError ("Expected a positive value")



----------------

  File "/Users/kodiak/projects/EigenD/tools/pip_cmd/yacc.py", line 2145
    exec "import %s as parsetab" % module


    exec ("import %s as parsetab" % module)


----

ModuleNotFoundError: No module named 'cStringIO'

https://salishsea-meopar-docs.readthedocs.io/en/latest/work_env/porting_to_python3.html



----


File "/Users/kodiak/projects/EigenD/tools/pip_cmd/lex.py", line 469, in lex
    if not (isinstance(tokens,types.ListType) or isinstance(tokens,types.TupleType)):
AttributeError: module 'types' has no attribute 'ListType'


    if not (isinstance(tokens,list) or isinstance(tokens,tuple)):




  File "/Users/kodiak/projects/EigenD/tools/pip_cmd/lex.py", line 505, in lex
    elif isinstance(ldict[f], types.StringType):
AttributeError: module 'types' has no attribute 'StringType'
scons: *** [tmp/obj/plg_arranger/src/arranger_native_python.cpp] Error 1

to: 

        elif isinstance(ldict[f], bytes):


-------


lex: t_OPENCURLY not defined as a function or string
lex: t_CLOSECURLY not defined as a function or string
lex: t_OPENROUND not defined as a function or string
lex: t_CLOSEROUND not defined as a function or string
lex: t_OPENSQUARE not defined as a function or string
lex: t_CLOSESQUARE not defined as a function or string
lex: t_SEMICOLON not defined as a function or string
lex: t_COMMA not defined as a function or string
lex: t_COLON not defined as a function or string
lex: t_SLASH not defined as a function or string
lex: t_EQUALS not defined as a function or string
lex: t_ZERO not defined as a function or string
lex: t_TILDE not defined as a function or string
lex: t_STAR not defined as a function or string
lex: t_AMPERSAND not defined as a function or string
lex: t_DOT not defined as a function or string
lex: t_ignore not defined as a function or string
Traceback (most recent call last):
  File "/Users/kodiak/projects/EigenD/tools/pip_cmd/pip.py", line 31, in <module>
    from pip_cmd import process,expand,error
  File "/Users/kodiak/projects/EigenD/tools/pip_cmd/process.py", line 21, in <module>
    import parse
  File "/Users/kodiak/projects/EigenD/tools/pip_cmd/parse.py", line 544, in <module>
    lex.lex()
  File "/Users/kodiak/projects/EigenD/tools/pip_cmd/lex.py", line 512, in lex
    fsymbols.sort(lambda x,y: cmp(x.func_code.co_firstlineno,y.func_code.co_firstlineno))
TypeError: sort() takes no positional arguments


https://docs.python.org/3/howto/sorting.html
https://bobbyhadz.com/blog/python-typeerror-sort-takes-no-positional-arguments


https://stackoverflow.com/questions/2531952/how-to-use-a-custom-comparison-function-in-python-3


to:








----





## yacc.py/lex.py

Ive adapted but is there a python 3 version?


is there a new python 3 version

#-----------------------------------------------------------------------------
# ply: lex.py
#
# Author: David M. Beazley (beazley@cs.uchicago.edu)
#         Department of Computer Science
#         University of Chicago
#         Chicago, IL  60637
#
# Copyright (C) 2001, David M. Beazley
#
# $Header: /cvs/projects/PLY/lex.py,v 1.1.1.1 2004/05/21 15:34:10 beazley Exp $
#

#-----------------------------------------------------------------------------
# ply: yacc.py
#
# Author(s): David M. Beazley (beazley@cs.uchicago.edu)
#            Department of Computer Science
#            University of Chicago
#            Chicago, IL 60637
#
# Copyright (C) 2001-2004, David M. Beazley
#
# $Header: /cvs/projects/PLY/yacc.py,v 1.6 2004/05/26 20:51:34 beazley Exp $




git clone https://github.com/dabeaz/ply 


upgraded tools/pip_cmd/lex and yacc.py


-----


File "/Users/kodiak/projects/EigenD/tools/pip_cmd/process.py", line 121, in process
    input = file(specfile,"rU")
NameError: name 'file' is not defined



https://stackoverflow.com/questions/16736833/python-nameerror-name-file-is-not-defined




file -> open 




----
```
    text = re.sub(r'(?s)<<(?P<tag>[a-zA-Z0-9_\.]+)(\((?P<arg>[a-zA-Z_0-9\.]+)\))?{(?P<code>.*?)}(?P=tag)>>',self.macro,text)
  File "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.8/lib/python3.8/re.py", line 210, in sub
    return _compile(pattern, flags).sub(repl, string, count)
TypeError: cannot use a string pattern on a bytes-like object
```

https://stackoverflow.com/questions/31019854/typeerror-cant-use-a-string-pattern-on-a-bytes-like-object-in-re-findall

        text = text.decode()
        text = re.sub(r'(?s)<<(?P<tag>[a-zA-Z0-9_\.]+)(\((?P<arg>[a-zA-Z_0-9\.]+)\))?{(?P<code>.*?)}(?P=tag)>>',self.macro,text)




---
upgraded pi/logic/tpg.py


--- 

pip are converted to C++ (python native objects from the yacc/lexx template

tools/pip_cmd/template

---




---



pi/async.py → pi/pisync.py

so, I noticed the other day, eigend was NOT using async, but its own decorator called async, and this appeared to creating some kind of clash…
so for now Ive rename pi/async.py to pi/pisync.py , and changed references where necessary.
but this is no guarantee it’ll work :slight_smile:
… but it compiles, and kind of looks right


---


piw ->TypeObject… tp_compare → tp_as_async

this one could be problematic… and will need a bit of digging I suspect… and its pretty much ‘commented out’ for now… so nothing is likely to work.

so, EigenD is defining its own python object types, and this includes iterating over some types.
the issue is python 2 used to so this with a simple compare function, returning -1,0,1
where python 3, uses iterators using PyAsyncMethods. which as the name implies not only is working as an iterator , but also handling ‘async’ functionality (eg. wait etc) - so to implement this, Im going to really need to understand now only the python3 functionality in this area , but also what EigenD is doing with its PiSync decorator… and is that even compatible, with this functionality.


THIS IS A BROKEN CHANGE : It will need fixing


----

no Int, so use Long

#define PyInt_FromLong(x) PyLong_FromLong(x)
#define PyInt_AsLong(x) PyLong_AsLong(x)
#define PyInt_Check(x) PyLong_Check(x)

---
using capsure instead of void pointers (possible cause of bugs!)


#define PyCObject_FromVoidPtr(a,b) PyCapsule_New(a,"pi",b)
#define PyCObject_AsVoidPtr(a) PyCapsule_GetPointer(a,"pi");
#define PyCObject_Check(a) PyCapsule_IsValid(a,"pi")


Im now assuming one namespace as there was only one before

---
PyString has now been replaced with PyUnicode/UTF8 , see below 

-----

module init function changes for v3


PyMODINIT_FUNC MODULE_VISIBILITY init<<module>>(void)
-> 
PyMODINIT_FUNC MODULE_VISIBILITY PyInit_<<module>>(void)


----

framework , needs to be on path , for now Ive done...
```
ln -s /Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework tmp/bin
```
will need to consider this futher... looks in : 

'~/tmp/bin/Python3.framework/Versions/3.8/Python3' (no such file), '~/tmp/bin/Python3.framework/Versions/3.8/Python3' (no such file), '/Library/Frameworks/Python3.framework/Versions/3.8/Python3' (no such file), '/System/Library/Frameworks/Python3.framework/Versions/3.8/Python3'

seems to be standard rpath behaviour.

not too problematic, as I dont want to use the xcode path that im using anyway!



------

```
tmp/bin/cheatsheet 
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "app_cmdline/cheat.py", line 70, in main
    print (makecheat(lexicon.lexicon))
  File "app_cmdline/cheat.py", line 27, in makecheat
    keys = [ chr(x) for x in [ord('!')]+range(ord('a'),ord('z')+1) ]
TypeError: can only concatenate list (not "range") to list
```

use +=/extend to concat lists ?

```
clist = [ord('!')]
clist += [*range(ord('a'),ord('z')+1)]
keys = [ chr(x) for x in clist ]
```


-----

```
    PyEval_InitThreads();
```

```
    //PyEval_InitThreads();
```

PyEval_InitThreads does nothing from 3.9 onwards, from 3.7 it was unnecesary
https://docs.python.org/3/c-api/init.html#non-python-created-threads

commented out.. as removing in 3.12, but left in places, as its 'position' in code may be valueable for debugging.


------

% ./tmp/bin/bcat 122                      
log:using portbase 55555
Fatal Python error: PyEval_AcquireLock: current thread state is NULL
Python runtime state: initialized


Fatal Python error: PyEval_AcquireLock: current thread state is NULL


we need to have called, Py_Initialize and PyEval_InitThreads(?, see above), before PyEval_AcquireLock

I'd assume this is not happening here for some reason.

 grep -Ilr 'PyEval_InitThreads' . 
./tools/pip_cmd/template
./picross/picross.pip
./piw/piw.pip
./tmp/obj/lib_micro/src/micro_native_python.cpp
etc


grep -Ilr 'Py_Initialize' . 
./tools/generic_tools.py
./lib_juce/epython.cpp
./app_juceworkbench/epython.cpp
./tmp/obj/lib_micro/pystub_uezload.cpp
./tmp/obj/lib_micro/pystub_utest.cpp
./tmp/obj/lib_micro/pystub_uezq.cpp
./tmp/obj/lib_micro/pystub_uled.cpp
etc
./tmp/obj/app_cmdline/pystub_bcat.cpp






upgraded to python 3.10.5, similar error but a bit more info! 
```
log:using portbase 55555
run_session
Fatal Python error: PyEval_AcquireLock: the function must be called with the GIL held, but the GIL is released (the current Python thread state is NULL)
Python runtime state: initialized

Current thread 0x00000001004f0580 (most recent call first):
  File "pisession/session.py", line 64 in run_session
  File "app_cmdline/bcat2.py", line 109 in main
  File "<string>", line 1 in <module>

Extension modules: picross_native, piw_native, piagent_native (total: 3)

```



PyEval_AcquireLock() depreciated since 3.2, 
use PyEval_RestoreThread() or PyEval_AcquireThread() 

PyEval_ReleaseLock() depreciated since 3.2,
use PyEval_SaveThread() or PyEval_ReleaseThread()


issue was placement of 

-----

```
 ./tmp/bin/pezload 
using version 5 of firmware
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "lib_pico/ezload.py", line 97, in main
    code = firmware(vendor,product)
  File "lib_pico/ezload.py", line 60, in firmware
    return find_release_resource('firmware','pico.ihx')
  File "lib_pico/ezload.py", line 46, in find_release_resource
    reldir = os.path.join(res_root,category)
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/posixpath.py", line 90, in join
    genericpath._check_arg_types('join', a, *p)
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/genericpath.py", line 155, in _check_arg_types
    raise TypeError("Can't mix strings and bytes in path components") from None
TypeError: Can't mix strings and bytes in path components
```


FIXED : 
this was caused by my choice of using PyBytes for PyString , fixed by using new PyUnicode and UTF 8 
see full translation below

------
Py2->3 layers

using
```
// TB : Py2->3, may remove and fix code later
#define PyInt_FromLong(x) PyLong_FromLong(x)
#define PyInt_AsLong(x) PyLong_AsLong(x)
#define PyInt_Check(x) PyLong_Check(x)

#define PyString_FromString(x) PyUnicode_FromString(x) 
#define PyString_FromStringAndSize(x,y) PyUnicode_FromStringAndSize(x,y)
#define PyString_AsString(x) (char*) PyUnicode_AsUTF8(x)
inline long PyString_AsStringAndSize(PyObject* x,char** buffer,long* length) { *buffer = (char*) PyUnicode_AsUTF8AndSize(x,length); return *length; }
#define PyString_Check(x) PyUnicode_Check(x)

#define PyCObject_Check(a) PyCapsule_IsValid(a,"pi")
#define PyCObject_FromVoidPtr(a,b) PyCapsule_New(a,"pi",b)
#define PyCObject_AsVoidPtr(a) PyCapsule_GetPointer(a,"pi")

```

tools/pip_cmd/template
piw/src/pip_termparse.cpp
pisession/src/pis_python.cpp
lib_juce/epython.cpp
app_juceworkbench/epython.cpp






-----
/tmp/bin/eigend , initial errors

```
locking /Users/kodiak/projects/EigenD/tmp/bin/libpic.dylib
locking /Users/kodiak/projects/EigenD/tmp/bin/libpia.dylib
locking /Users/kodiak/projects/EigenD/tmp/bin/libpiw.dylib
locking /Users/kodiak/projects/EigenD/tmp/bin/libpie.dylib
open lock file /Users/kodiak/Library/Eigenlabs/Lock/EigenD.lck 3
locked lock file
release root: /Users/kodiak/projects/EigenD/tmp
log:using portbase 55555
Traceback (most recent call last):
  File "<string>", line 6, in <module>
  File "app_eigend2/bugs_cli.py", line 28, in <module>
    import httplib
ModuleNotFoundError: No module named 'httplib'
Traceback (most recent call last):
  File "<string>", line 1, in <module>
NameError: name 'bugs_cli' is not defined
Traceback (most recent call last):
  File "app_eigend2/backend.py", line 23, in <module>
    from pi import agent,resource,utils,state
  File "pi/agent.py", line 25, in <module>
    from pi import atom,node,action,container,index,guid,files,utils,logic,rpc,pisync,const,paths,upgrade
  File "pi/atom.py", line 21, in <module>
    from pi import const, node, domain,errors, utils, policy, vocab, pisync, logic, files, action, rpc, paths
  File "pi/domain.py", line 22, in <module>
    from pi import const,utils,logic
  File "pi/logic/__init__.py", line 21, in <module>
    from pi.logic.terms import render_result, render_termlist,render_term, match, unify
  File "pi/logic/terms.py", line 23, in <module>
    __tx = string.maketrans('','')
AttributeError: module 'string' has no attribute 'maketrans'
```

bugs_cli.py, can almost certainly go ;) 



maketrans
caused by pi.logic.terms 
```

import string

__tx = string.maketrans('','')

def quotevarname(name):
    h=name[0].translate(__tx,'ABCDEFGHIJKLMNOPQRSTUVWXYZ_')
    t=name[1:].translate(__tx,'ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz0123456789')
    if not h and not t: return name
    return "%%'%s'" % name.replace('%','%25').replace("'","%27")

```
python 3, no longers uses maketrans like this
it has str.maketrans/translate but its slightly different... so need to check behaviour of the new maketrans/translate

interestingly the bytes version of maketrans/translates do seem to be same as 

so we go to something like
```

bytes.maketrans(b'',b'')
(name[0].encode().translate(tx_,b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')).decode()
```
----

File "pi/logic/builtin.py", line 22, in <module>
    import exceptions
ModuleNotFoundError: No module named 'exceptions'

Exception is now built-in, 
so just use Exception

from 
class LogicError(exceptions.Exception):
to
class LogicError(Exception):

---

ile "pi/vocab.py", line 48, in add_words
    for (e,(m,t)) in lex.iteritems():
AttributeError: 'dict' object has no attribute 'iteritems'

use dict.items() instead
https://wiki.python.org/moin/Python3.0#Built-In_Changes


----
bugs_cli / latest version
given no current eigenlabs development, Ive disabled this functionality rather than upgrade it to 3.0


------


EigenD stalling 
```
    2322 Thread_1170571   DispatchQueue_1: com.apple.main-thread  (serial)
    + 2322 start  (in dyld) + 516  [0x102839088]
    +   2322 juce::JUCEApplicationBase::main(int, char const**)  (in libpijuce.dylib) + 96  [0x1040356cc]  juce_ApplicationBase.cpp:240
    +     2322 juce::JUCEApplicationBase::main()  (in libpijuce.dylib) + 52  [0x104035758]  juce_ApplicationBase.cpp:256
    +       2322 juce::JUCEApplication::initialiseApp()  (in libpijuce.dylib) + 16  [0x10412f1e8]  juce_Application.cpp:92
    +         2322 juce::JUCEApplicationBase::initialiseApp()  (in libpijuce.dylib) + 84  [0x104035884]  juce_ApplicationBase.cpp:297
    +           2322 EigenD::initialise(juce::String const&)  (in eigend) + 576  [0x10251f42c]  eigend.cpp:1992
    +             2322 (anonymous namespace)::c2p_wrapper_::set_args(char const*)  (in eigend_native.so) + 36  [0x102b6344c]  eigend_native_python.cpp:1090
    +               2322 (anonymous namespace)::lock_c2p::lock_c2p(_is*, bool)  (in eigend_native.so) + 56  [0x102b6321c]  eigend_native_python.cpp:75
    +                 2322 take_gil  (in Python) + 512  [0x1033d8044]
    +                   2305 _pthread_cond_wait  (in libsystem_pthread.dylib) + 1236  [0x18b09683c]
    +                   ! 2304 __psynch_cvwait  (in libsystem_kernel.dylib) + 8  [0x18b05c290]
    +                   ! 1 _pthread_cond_wait  (in libsystem_pthread.dylib) + 1236  [0x18b09683c]
    +                   17 _pthread_cond_wait  (in libsystem_pthread.dylib) + 344  [0x18b0964c0]
    +                     16 __gettimeofday  (in libsystem_kernel.dylib) + 12  [0x18b05ca2c]
    +                     1 _pthread_cond_wait  (in libsystem_pthread.dylib) + 572  [0x18b0965a4]
```


----
IMPORTANT: 

lock_c2p is how eigend locks the interpreter

this used
```
    class lock_c2p
    {
        public:
            lock_c2p(PyInterpreterState *interp, bool fake=false): t_(0), gs_(PyGILState_LOCKED), f_(fake)
            {
                if(!f_)
                {
                    if(!pip_usegil)
                    {
                        PyEval_AcquireLock();
                        t_=PyThreadState_New(interp);
                        PyEval_ReleaseLock();
                        PyEval_AcquireThread(t_);
                        return;
                    }

                    gs_ = PyGILState_Ensure();
                }
             }

            ~lock_c2p()
            {
                if(!f_)
                {
                    if(!pip_usegil)
                    {
                        PyEval_ReleaseThread(t_);
                        PyEval_AcquireLock();
                        PyThreadState_Delete(t_);
                        PyEval_ReleaseLock();
                        return;
                    }

                    PyGILState_Release(gs_);
                }
            }

        private:
            PyThreadState *t_;
            PyGILState_STATE gs_;
            bool f_;
    };

```
this has chagned too...


```
    class lock_c2p
    {
        public:
            lock_c2p(PyInterpreterState *interp, bool fake=false): 
                t_(0), 
                f_(fake)
            {
                if(!f_)
                {
                    if(!pip_usegil)
                    {
                        t_=PyThreadState_New(interp);
                        PyEval_AcquireThread(t_);
                        return;
                    }

                }
             }

            ~lock_c2p()
            {
                if(!f_)
                {
                    if(!pip_usegil)
                    {
                        PyEval_ReleaseThread(t_);
                        PyThreadState_Delete(t_);
                        return;
                    }
                }
            }

        private:
            PyThreadState *t_;
            bool f_;
    };
```



note how we no longer use PyGILStateEnsure/Release 
also PyEval_AquireLock has basically been removed from 3.x, 

we also no longer have init threads.
my understanding is all of this has been folded into PyEval_AcquireThread


---- 
pezload 
control_out requires byte data but uses a string , python layer usign PyUnicode 'corrupts' this.
solution: created new bytearray class, and use this within pip where we are actually passing byte data around rather than real strings.


--- 
eigend failing to start - pip call issue?

```
locking /Users/kodiak/projects/EigenD/tmp/bin/libpic.dylib
locking /Users/kodiak/projects/EigenD/tmp/bin/libpia.dylib
locking /Users/kodiak/projects/EigenD/tmp/bin/libpiw.dylib
locking /Users/kodiak/projects/EigenD/tmp/bin/libpie.dylib
open lock file /Users/kodiak/Library/Eigenlabs/Lock/EigenD.lck 3
locked lock file
release root: /Users/kodiak/projects/EigenD/tmp
log:using portbase 55555
libc++abi: terminating with uncaught exception of type (anonymous namespace)::pip_err_t: get_logfile - call problem
```

```
./app_eigend2/backend.py:    def get_logfile(self):
./app_eigend2/backend.py:        return resource.get_logfile('eigend') if not self.opts.stdout else ''
./app_eigend2/eigend.h:        virtual std::string get_logfile() = 0;
./app_eigend2/eigend.pip:    virtual stdstr get_logfile() = 0
./app_eigend2/eigend.cpp:            std::string logfile = backend->get_logfile();
```

```
./tmp/obj/app_eigend2/eigend_native_python.cpp:    std::string get_logfile(  )
```

not the real issue !!! 
the issue was the backend module not being loaded, due to errors in backend.py (see below)
but we could not see these since libjuce/epython was sending stderr to stdout, which was also being captured by logfile handler
which due to above error was not initialising, and so error never got logged! 

for now, commented out the python log redirect so I get errors in console !



----
backend.py

rotate_logfile -  'range' object has no attribute 'reverse' 

find_installed_versions - cannot sort dictkeys ,use sorted()


---
```
  File "pisession/agentd.py", line 451, in copy_old_setup
    if upgrade.upgrade_trunk(src,dst,tweaker=tweaker):
  File "pisession/upgrade.py", line 137, in upgrade_trunk
    if do_upgrade(dst_snap):
  File "pisession/upgrade.py", line 127, in do_upgrade
    upgrade_tools_v1.do_upgrade(snap)
  File "pisession/upgrade_tools_v1.py", line 566, in do_upgrade
    tools = UpgradeTools(snap)
  File "pisession/upgrade_tools_v1.py", line 372, in __init__
    self.__build_mapping()
  File "pisession/upgrade_tools_v1.py", line 394, in __build_mapping
    plugin = old_signature.as_dict_lookup('plugin').as_string()
AttributeError: 'piw_native.data' object has no attribute 'as_dict_lookup'
```
hmm...
```
class data[piw::data_t]: data_base
{
    data()
    data(const data &)

    data as_dict_lookup(const stdstr &)
```

FIXED: issue with pip_cmd.process using dict.values()


--- 
  File "app_eigend2/backend.py", line 337, in upgrade_setups
    agentd.upgrade_old_setups()
  File "pisession/agentd.py", line 700, in upgrade_old_setups
    if 0 == find_user_setups().number_of_setups():
  File "pisession/agentd.py", line 301, in find_user_setups
    m.add_setup(urllib.unquote(s3[0]),s3[1],os.path.join(rd,s),False,True)
AttributeError: module 'urllib' has no attribute 'unquote'

usr urllib.parse
>>> import urllib.parse
>>> print(urllib.parse.unquote(s3[0]))

---

agentd... sorting
        # fs.sort(natcmp,reverse=False)
        fs=sorted(fs,key=functools.cmp_to_key(natcmp),reverse=False)


start traceback:
Traceback (most recent call last):
  File "pisession/agentd.py", line 372, in find_all_setups
    return m.term()
  File "pisession/agentd.py", line 271, in term
    children.add_arg(-1,c.term())
  File "pisession/agentd.py", line 262, in term
    names = sorted(names, key=functools.cmp_to_key(slotcmp))
  File "pisession/agentd.py", line 68, in slotcmp
    return cmp(natsort_key(a), natsort_key(b))
NameError: name 'cmp' is not defined

cmp is no longer a method... need fine alternative


can keep testing intial setup with

```
rm -rf ~/Library/Eigenlabs/2.3.0-community
```

suggestion to add cmp as 
```
def cmp(a, b):
    return (a > b) - (a < b) 
```
however, then we get 
```
    names = sorted(names, key=functools.cmp_to_key(slotcmp))
  File "pisession/agentd.py", line 71, in slotcmp
    return cmp(natsort_key(a), natsort_key(b))
  File "pisession/agentd.py", line 58, in cmp
    return (a > b) - (a < b)
TypeError: '>' not supported between instances of 'map' and 'map'
```

unsurprising, since 
```
def natsort_key(s):
    return map(try_int, re.findall(r'(\d+|\D+)', s))
```

really need to determine this was trying to do 


note: File "pisession/agentd.py", line 375, in find_all_setups



---
Traceback (most recent call last):
  File "pisession/upgrade_tools_v1.py", line 519, in call_phase
    upgrader = self.__registry.get_instance(module)
  File "pisession/upgrade_tools_v1.py", line 362, in get_instance
    m = registry.import_module(agent.module)
  File "pisession/registry.py", line 60, in import_module
    pkg = __import__('%s.%s' % (pkg_name,mod_name))
  File "plg_language/language_plg.py", line 23, in <module>
    from . import interpreter,database,feedback,noun,builtin_misc,context,variable,script,stage_server,widget,deferred,plumber
  File "plg_language/stage_server.py", line 27, in <module>
    from SimpleXMLRPCServer import SimpleXMLRPCServer
ModuleNotFoundError: No module named 'SimpleXMLRPCServer'

./plg_language/stage_server.py:from SimpleXMLRPCServer import SimpleXMLRPCServer

need to move to 
xmlrpc.server.SimpleXMLRPCServer

FIXED

---



```
TypeError: function takes exactly 0 arguments (1 given)

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "pisession/agentd.py", line 372, in find_all_setups
    return m.term()
  File "pisession/agentd.py", line 271, in term
    children.add_arg(-1,c.term())
  File "pisession/agentd.py", line 278, in term
    children.add_arg(-1,self.children2[c].term())
  File "pisession/agentd.py", line 278, in term
    children.add_arg(-1,self.children2[c].term())
  File "pisession/agentd.py", line 284, in term
    t.set_arg(0,piw.term(piw.makestring(self.label,0)))
SystemError: <class 'piw_native.term'> returned a result with an exception set
end traceback:
libc++abi: terminating with uncaught exception of type (anonymous namespace)::pip_err_t: wrong type result converting term_copy
```


-------

fresh updates 
```
rm -rf ~/Library/Eigenlabs/2.3.0-community
```
./tmp/bin/eigend


```
Traceback (most recent call last):
  File "pisession/upgrade_tools_v1.py", line 521, in call_phase
    if upgrader(self.oldcversion(address),self.newcversion(address),self,address,phase) == False:
  File "pisession/upgrade_agentd.py", line 171, in upgrade
    return Upgrader().upgrade(oldv,newv,tools,address,phase)
  File "pi/upgrade.py", line 87, in upgrade
    return self.postupgrade(tools,address)
  File "pisession/upgrade_agentd.py", line 166, in postupgrade
    return upgrade_plugins_v1(tools,address)
  File "pisession/upgrade_agentd.py", line 50, in upgrade_plugins_v1
    ncversion = tools.newcversion(address)
  File "pisession/upgrade_tools_v1.py", line 506, in newcversion
    return self.__mapping[agent][1].cversion
KeyError: '<talker13>'
upgrade v1 phase 3 failed <eigend1>
```

IDEA: tracing thru, only appears to happen for plugins Ive not yet converted ! 

