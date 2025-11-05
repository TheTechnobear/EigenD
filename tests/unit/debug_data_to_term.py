#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Look for alternative ways to convert data to terms without bypassing the data wrappers
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
    
    # Create data objects
    string_data = piw.makestring("test", 0)
    bool_data = piw.makebool(True, 0)
    
    print(f"String data: {string_data}")
    print(f"Bool data: {bool_data}")
    
    # Look for alternative ways to create terms from data
    
    # 1. Check if we can extract the underlying string and use term(string, type)
    print(f"\n🧪 Testing data extraction methods:")
    
    try:
        extracted_string = string_data.as_string()
        print(f"✅ string_data.as_string(): {extracted_string!r} (type: {type(extracted_string)})")
        
        # Try to create term with extracted string
        term_from_extracted = piw.term(extracted_string, 0)
        print(f"✅ piw.term(extracted_string, 0): {term_from_extracted}")
        
    except Exception as e:
        print(f"❌ String extraction failed: {e}")
    
    try:
        extracted_bool = bool_data.as_bool()
        print(f"✅ bool_data.as_bool(): {extracted_bool!r} (type: {type(extracted_bool)})")
        
        # Try to create term with extracted bool - what constructor to use?
        # Look for bool term constructor
        
    except Exception as e:
        print(f"❌ Bool extraction failed: {e}")
    
    # 2. Check data object properties that might help
    print(f"\n🧪 Data object properties:")
    print(f"string_data.data_type(): {string_data.data_type()}")
    print(f"string_data.type(): {string_data.type()}")
    print(f"bool_data.data_type(): {bool_data.data_type()}")
    print(f"bool_data.type(): {bool_data.type()}")
    
    # 3. Look for functions that might convert data to terms
    conversion_funcs = []
    for attr in dir(piw):
        if ('data' in attr.lower() and 'term' in attr.lower()) or \
           ('convert' in attr.lower()) or \
           ('make' in attr.lower() and 'term' in attr.lower()):
            conversion_funcs.append(attr)
    
    print(f"\nPossible conversion functions: {conversion_funcs}")
    
    # 4. Test if we can use parse_term with the string representation
    try:
        # parse_term needs 2 args according to earlier error
        # Maybe it needs a context or delegate?
        pass  # Skip for now, need to figure out args
    except:
        pass
    
    context.release()

except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()