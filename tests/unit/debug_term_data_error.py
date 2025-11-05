#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test the exact failing pattern with detailed error info
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
    
    # Test the exact failing pattern
    string_data = piw.makestring("test", 0)
    print(f"Created string data: {string_data} (type: {type(string_data)})")
    
    # Try to create term - this is the failing line
    print(f"\n🧪 Attempting piw.term(string_data)...")
    
    try:
        # Enable detailed Python error reporting
        import traceback
        term_obj = piw.term(string_data)
        print(f"✅ Success: {term_obj}")
    except Exception as e:
        print(f"❌ Exception type: {type(e)}")
        print(f"❌ Exception message: {e}")
        print(f"❌ Exception args: {e.args}")
        
        # Get full traceback
        print(f"\n🔍 Full traceback:")
        traceback.print_exc()
        
        # Try to get more info about the exception
        if hasattr(e, '__cause__'):
            print(f"Exception cause: {e.__cause__}")
        if hasattr(e, '__context__'):
            print(f"Exception context: {e.__context__}")
    
    # Test with bool data too
    print(f"\n🧪 Testing with bool data...")
    bool_data = piw.makebool(True, 0)
    print(f"Created bool data: {bool_data} (type: {type(bool_data)})")
    
    try:
        bool_term = piw.term(bool_data)
        print(f"✅ Bool term success: {bool_term}")
    except Exception as e:
        print(f"❌ Bool term failed: {e}")
    
    context.release()

except Exception as e:
    print(f"❌ Setup failed: {e}")
    import traceback
    traceback.print_exc()