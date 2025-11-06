# overview

a doc just to help me (thetechobear) get a grip on how thing are runing in eigend 'ecosystem'
it'll help understand threadings and coroutines etc.


WARNING: 
this is a working doc, so it is very likely to be incomplete/inaccurate,
I may well have not updated it, so my understandings have very likely moved on from whats written here! 
I am NOT trying to document EigenD here.... !!! 



# command line

going to start with a very simple command line tools.

(python based) command line tools are in app_cmdline
they use a pystub  to make them native executable that run python.


this is done in tools/generic_tools.py
with a (horrible) hardcode string to define the pystub c program 
in generic_py_template
e.g
```
generic_py_template = """
#ifdef _WIN32  
#ifdef _DEBUG
#define __REDEF_DEBUG__
#undef _DEBUG
#endif
#endif

#include <Python.h>

#ifdef __REDEF_DEBUG__
#define _DEBUG
#undef __REDEF_DEBUG__

etc etc
```

so in bcat2.py we have the actualy python cde that is run as a 'string' by this python stub




```

    def coroutine():
        (a,p) = paths.breakid_list(id)
        p = ''.join(chr(c) for c in p)
        r = pisync.Deferred()
        c = Opener(a,p,flags,r if not opt.monitor else None,fast)
        yield r

    def handler(ei):
        traceback.print_exception(file=sys.stderr,*ei)
        return pisync.Coroutine.failure('internal error')

    def failed(msg):
        print (msg)
        picross.exit(-1)

    def succeeded():
        picross.exit(0)

    def startup(dummy):
        print('startup',file=sys.stderr)
        result = pisync.Coroutine(coroutine(),handler)
        result.setErrback(failed).setCallback(succeeded)
        return result

    session.run_session(startup,clock=False,rt=False)

```

here we can see we use a pisession to kick things off.. which then uses a coroutine to do stuff.

so we end up in pisession.. which in turn then uses agent.
```

    scaffold = piagent.scaffold_mt(mt,utils.stringify(logfunc),utils.stringify(None),clock,rt)
    context = scaffold.context('main',utils.statusify(ctxdun),utils.stringify(logfunc),name)
    stdio = (sys.stdout,sys.stderr)
    x = None

    try:
        if logger:
            sys.stdout = Logger()
            sys.stderr = sys.stdout

        piw.setenv(context.getenv())
        piw.tsd_lock()

        try:
            x = session(scaffold)
            context.trigger()
        finally:
            piw.tsd_unlock()

        scaffold.wait()

    finally:
        sys.stdout,sys.stderr = stdio

    return x
```

so pi agent creates a scaffold (hint there is a gui and non gui variant ! )
which is then used to build a context.

note session here = function we passed in, in this case startup(), so basically its startup(scaffold)


so the question is.. what is a context/scaffold.
(this is the bit Im working thru now ... so may be inaccurate/incomplete if ive not updated this doc)


scaffold is really just here to creat the relevant context.

context, is where things get interesting...

we quickly get into the reams of pia:manager pia:glue and context threads.

it appears context is usually one of these 'threads', it could be fast thread/slow thread, or any context thread.
the manager is responsible for holding these threads/contexts... and thats where scaffold get them
however, its appeas that pia:glue is actually the thing thats really doing alll the work...

basically pia:manager_t is the interface, but pia::manager_impl is where the action happens, and is defined in pia:glue





