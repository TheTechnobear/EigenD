#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test if piw.makestring actually works better with bytes in Python 3
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
    print(f"Python version: {sys.version_info}")
    
    # Test both unicode and bytes with makestring
    test_string = "user 2"
    
    print(f"\n🧪 Testing piw.makestring with different string types:")
    
    # 1. Unicode string (current approach)
    try:
        result1 = piw.makestring(test_string, 0)
        print(f"✅ Unicode string: {result1}")
    except Exception as e:
        print(f"❌ Unicode string: {e}")
    
    # 2. Bytes (potentially better approach) 
    try:
        bytes_string = test_string.encode('utf-8')
        result2 = piw.makestring(bytes_string, 0)
        print(f"✅ Bytes string: {result2}")
    except Exception as e:
        print(f"❌ Bytes string: {e}")
    
    # 3. Test with different encodings
    for encoding in ['utf-8', 'ascii', 'latin1']:
        try:
            encoded = test_string.encode(encoding)
            result = piw.makestring(encoded, 0)
            print(f"✅ {encoding} bytes: {result}")
        except Exception as e:
            print(f"❌ {encoding} bytes: {e}")
    
    # 4. Test problematic strings that might have encoding issues
    problematic = ["user 2", "café", "naïve", "résumé", "🎵"]
    
    print(f"\n🧪 Testing problematic strings:")
    for test_str in problematic:
        print(f"\nString: {test_str!r}")
        
        # Unicode
        try:
            result_unicode = piw.makestring(test_str, 0)
            print(f"  ✅ Unicode: {result_unicode}")
        except Exception as e:
            print(f"  ❌ Unicode: {e}")
        
        # UTF-8 bytes
        try:
            result_bytes = piw.makestring(test_str.encode('utf-8'), 0)
            print(f"  ✅ UTF-8 bytes: {result_bytes}")
        except Exception as e:
            print(f"  ❌ UTF-8 bytes: {e}")
    
    context.release()

except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()