#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug piw.term constructor arguments
"""

import sys
import os

# Add EigenD paths
test_dir = os.path.dirname(__file__)
project_root = os.path.join(test_dir, '..', '..')
tmp_modules = os.path.join(project_root, 'tmp', 'modules')
sys.path.insert(0, tmp_modules)

try:
    import piw
    import piagent
    from pi import utils
    
    # Set up context
    def logfunc(msg):
        pass
        
    scaffold = piagent.scaffold_mt(1, utils.stringify(logfunc), 
                                 utils.stringify(None), False, False)
    
    def ctxdun(status):
        pass
        
    context = scaffold.context('test', utils.statusify(ctxdun), 
                             utils.stringify(logfunc), 'test')
    
    piw.setenv(context.getenv())
    
    print("✅ Context set up successfully")
    
    # Check what piw.term is
    print(f"\npiw.term type: {type(piw.term)}")
    print(f"piw.term: {piw.term}")
    
    # Try to get help/documentation
    try:
        print(f"piw.term.__doc__: {piw.term.__doc__}")
    except:
        print("No __doc__ available")
    
    # Try different ways to create a term
    test_cases = [
        ("No arguments", lambda: piw.term()),
        ("Empty string", lambda: piw.term("")),
        ("String argument", lambda: piw.term("test")),
        ("String + int", lambda: piw.term("test", 0)),
        ("Data argument", lambda: piw.term(piw.makestring("test", 0))),
    ]
    
    for desc, test_func in test_cases:
        try:
            result = test_func()
            print(f"✅ {desc}: {result} (type: {type(result)})")
        except Exception as e:
            print(f"❌ {desc}: {e}")
    
    # Check if there are other term-related functions
    term_funcs = [attr for attr in dir(piw) if 'term' in attr.lower()]
    print(f"\nTerm-related functions in piw: {term_funcs}")
    
    context.release()

except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()