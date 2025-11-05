#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Investigate piw data objects and term creation patterns
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
    
    # Test what makestring returns
    print(f"\n🧪 Investigating piw.makestring return type:")
    string_data = piw.makestring("test", 0)
    print(f"makestring result: {string_data}")
    print(f"makestring type: {type(string_data)}")
    print(f"makestring dir: {[attr for attr in dir(string_data) if not attr.startswith('_')]}")
    
    # Test what makebool returns
    print(f"\n🧪 Investigating piw.makebool return type:")
    bool_data = piw.makebool(True, 0)
    print(f"makebool result: {bool_data}")
    print(f"makebool type: {type(bool_data)}")
    print(f"makebool dir: {[attr for attr in dir(bool_data) if not attr.startswith('_')]}")
    
    # Test if there are different term constructors
    print(f"\n🧪 Looking for alternative term creation methods:")
    
    # Check if data objects have a method to convert to terms
    if hasattr(string_data, 'term'):
        try:
            term_from_data = string_data.term()
            print(f"✅ string_data.term() works: {term_from_data}")
        except Exception as e:
            print(f"❌ string_data.term() failed: {e}")
    
    # Check parse_term function
    try:
        parsed_term = piw.parse_term("test")
        print(f"✅ piw.parse_term('test') works: {parsed_term}")
    except Exception as e:
        print(f"❌ piw.parse_term('test') failed: {e}")
    
    # Look for data-to-term conversion functions
    data_funcs = [attr for attr in dir(piw) if 'data' in attr.lower()]
    print(f"\nData-related functions: {data_funcs}")
    
    # Look for term creation functions
    term_funcs = [attr for attr in dir(piw) if 'term' in attr.lower()]
    print(f"Term-related functions: {term_funcs}")
    
    # Test if we can introspect the data object more
    print(f"\n🧪 Data object introspection:")
    try:
        print(f"string_data methods: {[m for m in dir(string_data) if callable(getattr(string_data, m)) and not m.startswith('_')]}")
    except:
        pass
    
    context.release()

except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()