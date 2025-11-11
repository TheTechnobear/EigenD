#!/usr/bin/env python3
"""Fix Exception to Exception for Python 3 compatibility."""

import os
import re
import sys

def fix_standard_error(content):
    """Replace all Exception with Exception."""
    # Simple replacement - Exception was removed in Python 3
    # It was the base class for all built-in exceptions except StopIteration,
    # GeneratorExit, KeyboardInterrupt and SystemExit.
    # In Python 3, Exception serves this purpose.
    modified = False
    original = content
    
    # Replace Exception with Exception
    content = re.sub(r'\bStandardError\b', 'Exception', content)
    
    if content != original:
        modified = True
    
    return content, modified

def process_file(filepath):
    """Process a single Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        fixed_content, modified = fix_standard_error(content)
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def main():
    """Find and fix all Python files with Exception."""
    root_dir = '.'
    fixed_files = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip hidden directories and common exclusions
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in ['__pycache__', 'build', 'dist']]
        
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                if process_file(filepath):
                    fixed_files.append(filepath)
                    print(f"Fixed: {filepath}")
    
    print(f"\nFixed Exception in {len(fixed_files)} files")

if __name__ == '__main__':
    main()
