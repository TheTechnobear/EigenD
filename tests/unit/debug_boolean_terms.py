#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test boolean term creation
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
    
    print(f"\n🧪 Testing boolean term creation:")
    
    # Test different ways to create boolean terms
    test_cases = [
        ("piw.term(True, type)", lambda: piw.term(True, 2)),  # Type 2 for bool?
        ("piw.term(False, type)", lambda: piw.term(False, 2)),
        ("piw.term(makebool)", lambda: piw.term(piw.makebool(True, 0))),
        ("makebool alone", lambda: piw.makebool(True, 0)),
    ]
    
    for desc, test_func in test_cases:
        try:
            result = test_func()
            print(f"✅ {desc}: {result} (type: {type(result)})")
        except Exception as e:
            print(f"❌ {desc}: {e}")
    
    # Check term types
    print(f"\n🧪 Testing different term types:")
    for i in range(10):
        try:
            term = piw.term("test", i)
            print(f"✅ Type {i}: {term}")
        except Exception as e:
            print(f"❌ Type {i}: {e}")
    
    context.release()

except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()