#!/usr/bin/env python3
"""
Fix Python 2 types module references for Python 3 compatibility.
In Python 3, types.ListType, types.StringType, etc. don't exist.
Use the built-in types directly: list, tuple, str, dict, int
"""

import re
import sys

def fix_types_in_file(filepath):
    """Fix types.XxxType references in a Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original = content
        
        # Replace types module references with built-in types
        # types.ListType -> list
        content = re.sub(r'\btypes\.ListType\b', 'list', content)
        
        # types.TupleType -> tuple
        content = re.sub(r'\btypes\.TupleType\b', 'tuple', content)
        
        # types.DictType -> dict
        content = re.sub(r'\btypes\.DictType\b', 'dict', content)
        
        # types.StringType -> str (in Python 3, all strings are unicode)
        content = re.sub(r'\btypes\.StringType\b', 'str', content)
        
        # types.IntType -> int
        content = re.sub(r'\btypes\.IntType\b', 'int', content)
        
        # types.LongType -> int (no separate long type in Python 3)
        content = re.sub(r'\btypes\.LongType\b', 'int', content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    files_to_fix = [
        "tools/pip_cmd/lex.py",
        "tools/pip_cmd/expand.py",
        "tools/pip_cmd/yacc.py",
    ]
    
    fixed_count = 0
    for filepath in files_to_fix:
        if fix_types_in_file(filepath):
            print(f"Fixed types in {filepath}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} file(s)")
