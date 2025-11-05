#!/usr/bin/env python3
# Test script to check resource.py functionality
import sys
import os
sys.path.insert(0, '/Users/kodiak/projects/EigenD/tmp/modules')

try:
    import pi.resource as resource
    print("Successfully imported pi.resource")
    
    # Test the get_logfile function that's failing
    logfile = resource.get_logfile('test')
    print(f"get_logfile returned: {logfile}")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()