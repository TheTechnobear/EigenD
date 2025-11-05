#!/usr/bin/env python3
"""
Simple test for the natsort_key fix without full imports.
"""

import re

def try_int(s):
    try: return int(s)
    except: return s

def natsort_key(s):
    return list(map(try_int, re.findall(r'(\d+|\D+)', s)))

def test_natsort_fix():
    """Test that our natsort_key fix returns a list, not a map iterator."""
    
    result = natsort_key("test123")
    print(f"natsort_key('test123') = {result}")
    print(f"Type: {type(result)}")
    
    # Should be a list, not a map object
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    
    # Should be comparable
    result2 = natsort_key("test456")
    print(f"natsort_key('test456') = {result2}")
    
    # This should work without TypeError
    try:
        comparison = result > result2
        print(f"Comparison works: {result} > {result2} = {comparison}")
    except TypeError as e:
        print(f"❌ Comparison failed: {e}")
        return False
    
    print("✅ natsort_key fix is working correctly")
    return True

if __name__ == '__main__':
    test_natsort_fix()