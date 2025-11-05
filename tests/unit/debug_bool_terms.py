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
    
    # Test different ways to create boolean terms
    bool_data = piw.makebool(True, 0)
    extracted_bool = bool_data.as_bool()
    bool_type = bool_data.data_type()  # This was 6
    
    print(f"Bool data type: {bool_type}")
    print(f"Extracted bool: {extracted_bool} (type: {type(extracted_bool)})")
    
    # Try different term constructors for booleans
    test_cases = [
        ("piw.term(True, 6)", lambda: piw.term(True, 6)),
        ("piw.term(extracted_bool, bool_type)", lambda: piw.term(extracted_bool, bool_type)),
        ("piw.term(1, 6)", lambda: piw.term(1, 6)),  # bool as int
        ("piw.term(0, 6)", lambda: piw.term(0, 6)),  # false as int
    ]
    
    for desc, test_func in test_cases:
        try:
            result = test_func()
            print(f"✅ {desc}: {result}")
        except Exception as e:
            print(f"❌ {desc}: {e}")
    
    # Also test string type to confirm
    string_data = piw.makestring("test", 0)
    string_type = string_data.data_type()  # This was 2
    print(f"\nString data type: {string_type}")
    
    try:
        string_term = piw.term(string_data.as_string(), string_type)
        print(f"✅ String term with correct type: {string_term}")
    except Exception as e:
        print(f"❌ String term failed: {e}")
    
    context.release()

except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()