#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test different ways to create string terms
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
    
    test_string = "user 2"
    
    print(f"\n🧪 Testing different ways to create string terms:")
    
    # Method 1: Direct string + type (this worked!)
    try:
        term1 = piw.term(test_string, 0)
        print(f"✅ piw.term(string, 0): {term1}")
    except Exception as e:
        print(f"❌ piw.term(string, 0): {e}")
    
    # Method 2: The failing pattern
    try:
        string_data = piw.makestring(test_string, 0)
        print(f"String data: {string_data} (type: {type(string_data)})")
        term2 = piw.term(string_data)
        print(f"✅ piw.term(makestring(...)): {term2}")
    except Exception as e:
        print(f"❌ piw.term(makestring(...)): {e}")
    
    # Method 3: Check if we need a different function
    if hasattr(piw, 'term_from_data'):
        try:
            term3 = piw.term_from_data(string_data)
            print(f"✅ piw.term_from_data: {term3}")
        except Exception as e:
            print(f"❌ piw.term_from_data: {e}")
    
    # Method 4: Check parse_term
    if hasattr(piw, 'parse_term'):
        try:
            term4 = piw.parse_term(test_string)
            print(f"✅ piw.parse_term: {term4}")
        except Exception as e:
            print(f"❌ piw.parse_term: {e}")
    
    context.release()

except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()