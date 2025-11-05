#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test term(unsigned) constructor
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
    
    # Test term(unsigned) constructor
    test_cases = [
        ("piw.term(0)", lambda: piw.term(0)),
        ("piw.term(1)", lambda: piw.term(1)),
        ("piw.term(2)", lambda: piw.term(2)),
        ("piw.term(6)", lambda: piw.term(6)),
    ]
    
    for desc, test_func in test_cases:
        try:
            result = test_func()
            print(f"✅ {desc}: {result}")
        except Exception as e:
            print(f"❌ {desc}: {e}")
    
    # Test the workaround for the original problem
    print(f"\n🧪 Testing complete workaround:")
    
    # String case - this should work
    string_data = piw.makestring("test string", 0)
    try:
        # Use extracted string with type 
        string_term = piw.term(string_data.as_string(), string_data.data_type())
        print(f"✅ String workaround: {string_term}")
    except Exception as e:
        print(f"❌ String workaround failed: {e}")
    
    # Bool case - try different approaches
    bool_data = piw.makebool(True, 0)
    print(f"Bool data: {bool_data}, type: {bool_data.data_type()}")
    
    # Maybe we need to create a term of the right type first, then set its value?
    try:
        bool_term = piw.term(bool_data.data_type())  # Create term of type 6
        print(f"✅ Bool term created: {bool_term}")
        # But how to set the value? Look for setter methods
        print(f"Bool term methods: {[m for m in dir(bool_term) if not m.startswith('_')]}")
    except Exception as e:
        print(f"❌ Bool term creation failed: {e}")
    
    context.release()

except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()