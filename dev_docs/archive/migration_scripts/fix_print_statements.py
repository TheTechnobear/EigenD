#!/usr/bin/env python3
"""
Fix print statements to print() function calls for Python 3.
This script handles various print statement patterns.
"""

import re
import sys
import os

def fix_print_in_file(filepath):
    """Fix print statements in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return False
    
    original = content
    
    # Pattern 1: print 'string' or print "string"
    content = re.sub(r"^(\s*)print\s+'([^']*)'$", r"\1print('\2')", content, flags=re.MULTILINE)
    content = re.sub(r'^(\s*)print\s+"([^"]*)"$', r'\1print("\2")', content, flags=re.MULTILINE)
    
    # Pattern 2: print 'string',var or print "string",var (with trailing comma)
    content = re.sub(r"^(\s*)print\s+'([^']*)',(.+)$", r"\1print('\2',\3)", content, flags=re.MULTILINE)
    content = re.sub(r'^(\s*)print\s+"([^"]*)",(.+)$', r'\1print("\2",\3)', content, flags=re.MULTILINE)
    
    # Pattern 3: print var,'string' (variable first)
    content = re.sub(r"^(\s*)print\s+([^'\"]+),'([^']*)'$", r"\1print(\2,'\3')", content, flags=re.MULTILINE)
    content = re.sub(r'^(\s*)print\s+([^"]+),"([^"]*)"$', r'\1print(\2,"\3")', content, flags=re.MULTILINE)
    
    # Pattern 4: print var (just a variable)
    content = re.sub(r"^(\s*)print\s+([a-zA-Z_][a-zA-Z0-9_\.\[\]]+)$", r"\1print(\2)", content, flags=re.MULTILINE)
    
    # Pattern 5: print (already has parens but space between)
    content = re.sub(r"^(\s*)print\s+\(", r"\1print(", content, flags=re.MULTILINE)
    
    if content != original:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing {filepath}: {e}", file=sys.stderr)
            return False
    
    return False

def main():
    """Find and fix all Python files."""
    count = 0
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip in root for skip in ['.git', '__pycache__', 'tmp', '.egg-info']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_print_in_file(filepath):
                    print(f"Fixed: {filepath}")
                    count += 1
    
    print(f"\nFixed print statements in {count} files")

if __name__ == '__main__':
    main()
