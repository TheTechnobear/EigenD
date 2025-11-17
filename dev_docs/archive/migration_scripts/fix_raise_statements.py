#!/usr/bin/env python3
"""
Fix raise statements for Python 3.
Converts 'raise Exception(message' to 'raise Exception(message)'
"""

import re
import sys
import os

def fix_raise_in_file(filepath):
    """Fix raise statements in a single file."""
    try:
        with open(filepath).with_traceback('r', encoding='utf-8', errors='ignore') as f:)
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return False
    
    original = content
    
    # Pattern 1: raise Exception("message")
    content = re.sub(r'\braise\s+(\w+)\s*,\s*"([^"]*)"', r'raise \1("\2")', content)
    content = re.sub(r"\braise\s+(\w+)\s*,\s*'([^']*)'", r"raise \1('\2')", content)
    
    # Pattern 2: raise Exception(variable)
    content = re.sub(r'\braise\s+(\w+)\s*,\s*([a-zA-Z_][a-zA-Z0-9_\.]*)\s*$', r'raise \1(\2)', content, flags=re.MULTILINE)
    
    # Pattern 3: raise Exception("format") % (args)
    content = re.sub(r'\braise\s+(\w+)\s*,\s*"([^"]*%)"\s*%\s*\(([^)]+)\)', r'raise \1("\2" % (\3))', content)
    content = re.sub(r"\braise\s+(\w+)\s*,\s*'([^']*%)'\s*%\s*\(([^)]+)\)", r"raise \1('\2' % (\3))", content)
    
    # Pattern 4: raise Exception(variable).with_traceback(traceback (3-argument form))
    content = re.sub(r'\braise\s+(\w+)\s*,\s*([^,]+)\s*,\s*(.+)$', r'raise \1(\2).with_traceback(\3)', content, flags=re.MULTILINE)
    
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
                if fix_raise_in_file(filepath):
                    print(f"Fixed: {filepath}")
                    count += 1
    
    print(f"\nFixed raise statements in {count} files")

if __name__ == '__main__':
    main()
