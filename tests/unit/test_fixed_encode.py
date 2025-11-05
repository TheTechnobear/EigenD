#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test the fixed encode_for_piw function directly
"""

import sys
import os

# Add EigenD paths
test_dir = os.path.dirname(__file__)
project_root = os.path.join(test_dir, '..', '..')
tmp_modules = os.path.join(project_root, 'tmp', 'modules')
sys.path.insert(0, tmp_modules)

# Test the fixed function
print(f"Python version: {sys.version_info}")

def encode_for_piw(s):
    """Ensure string is properly formatted for piw.makestring in both Python 2 and 3"""
    if s is None:
        return s
    
    # In Python 3, piw.makestring expects Unicode strings, not bytes
    if sys.version_info[0] >= 3:
        # Python 3: just ensure it's a string (don't encode to bytes)
        if isinstance(s, bytes):
            return s.decode('utf-8')  # Decode bytes to string if needed
        return str(s)  # Ensure it's a string
    else:
        # Python 2: encode unicode to bytes for piw.makestring
        if hasattr(s, 'encode'):  # Python 2 unicode
            return s.encode('utf-8')
        return s  # Python 2 str (already bytes)

# Test cases
test_cases = [
    "test string",
    "user 2",
    b"bytes input",
    "",
    None,
    123  # number
]

for test_input in test_cases:
    result = encode_for_piw(test_input)
    print(f"Input: {test_input!r} ({type(test_input)}) -> Output: {result!r} ({type(result)})")

# Test with actual piw
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
    
    print(f"\n🧪 Testing with actual piw.makestring:")
    
    test_string = "user 2"
    processed = encode_for_piw(test_string)
    print(f"Original: {test_string!r}")
    print(f"Processed: {processed!r} ({type(processed)})")
    
    try:
        result = piw.makestring(processed, 0)
        print(f"✅ piw.makestring works: {result}")
    except Exception as e:
        print(f"❌ piw.makestring failed: {e}")
    
    context.release()
    
except Exception as e:
    print(f"❌ piw test failed: {e}")
    import traceback
    traceback.print_exc()