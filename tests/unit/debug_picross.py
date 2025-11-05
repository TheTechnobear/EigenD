#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug what's available in the picross module.
"""

import sys
import os

# Add EigenD paths
test_dir = os.path.dirname(__file__)
project_root = os.path.join(test_dir, '..', '..')
tmp_modules = os.path.join(project_root, 'tmp', 'modules')
sys.path.insert(0, tmp_modules)

try:
    import picross
    print("✅ picross imported successfully")
    print(f"picross dir: {[attr for attr in dir(picross) if not attr.startswith('_')]}")
    
    # Look for scaffold-related functions
    for attr in dir(picross):
        if 'scaffold' in attr.lower() or 'context' in attr.lower():
            print(f"Found: {attr}")
    
except ImportError as e:
    print(f"❌ Failed to import picross: {e}")

try:
    import piw
    print("✅ piw imported successfully")
    
    # Look for context-related functions
    context_funcs = [attr for attr in dir(piw) if 'context' in attr.lower() or 'tsd' in attr.lower()]
    print(f"piw context/tsd functions: {context_funcs}")
    
except ImportError as e:
    print(f"❌ Failed to import piw: {e}")