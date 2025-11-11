#!/usr/bin/env python3
"""
Fix remaining Python 2 to 3 incompatibilities in pip_cmd tools:
1. func_code -> __code__
2. sort(lambda x,y: cmp(...)) -> sort(key=lambda x: ...)
"""

import re
import sys

def fix_file(filepath):
    """Fix Python 2/3 compatibility issues in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original = content
        
        # Fix func_code -> __code__
        content = re.sub(r'\.func_code\.', '.__code__.', content)
        
        # Fix sort with cmp lambda for co_firstlineno specifically
        # Old: symbols.sort(lambda x,y: cmp(x.func_code.co_firstlineno,y.func_code.co_firstlineno))
        # New: symbols.sort(key=lambda x: x.__code__.co_firstlineno)
        content = re.sub(
            r'\.sort\(\s*lambda\s+\w+\s*,\s*\w+\s*:\s*cmp\(\s*\w+\.__code__\.co_firstlineno\s*,\s*\w+\.__code__\.co_firstlineno\s*\)\s*\)',
            '.sort(key=lambda x: x.__code__.co_firstlineno)',
            content
        )
        
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
        "tools/pip_cmd/yacc.py",
    ]
    
    fixed_count = 0
    for filepath in files_to_fix:
        if fix_file(filepath):
            print(f"Fixed {filepath}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} file(s)")
