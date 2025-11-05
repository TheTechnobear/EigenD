#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test different argument types for piw.makestring to find what works.
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
    
    # Set up context like session.run_session() does
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
    
    # Test different argument types
    test_string = "test"
    
    print(f"\n🧪 Testing argument types for piw.makestring:")
    print(f"String: '{test_string}', type: {type(test_string)}")
    
    # 1. Raw Python 3 string (Unicode)
    try:
        result1 = piw.makestring(test_string, 0)
        print(f"✅ Unicode string works: {result1}")
    except Exception as e:
        print(f"❌ Unicode string failed: {e}")
    
    # 2. Encoded bytes
    try:
        encoded = test_string.encode('utf-8')
        print(f"Encoded: {encoded}, type: {type(encoded)}")
        result2 = piw.makestring(encoded, 0)
        print(f"✅ Bytes works: {result2}")
    except Exception as e:
        print(f"❌ Bytes failed: {e}")
    
    # 3. Encoded bytes with different encodings
    for encoding in ['utf-8', 'ascii', 'latin1']:
        try:
            encoded = test_string.encode(encoding)
            result = piw.makestring(encoded, 0)
            print(f"✅ {encoding} encoding works: {result}")
        except Exception as e:
            print(f"❌ {encoding} encoding failed: {e}")
    
    # 4. Test what actually gets passed from encode_for_piw
    import pisession.agentd as agentd
    processed = agentd.encode_for_piw(test_string)
    print(f"encode_for_piw result: {processed}, type: {type(processed)}")
    
    try:
        result_processed = piw.makestring(processed, 0)
        print(f"✅ encode_for_piw result works: {result_processed}")
    except Exception as e:
        print(f"❌ encode_for_piw result failed: {e}")
    
    # 5. Test different numeric arguments  
    for second_arg in [0, None]:
        try:
            result = piw.makestring(test_string, second_arg)
            print(f"✅ Second arg {second_arg} works: {result}")
        except Exception as e:
            print(f"❌ Second arg {second_arg} failed: {e}")
    
    context.release()
    print("\n✅ Context cleaned up")

except Exception as e:
    print(f"❌ Setup failed: {e}")
    import traceback
    traceback.print_exc()