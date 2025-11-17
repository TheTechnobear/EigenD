#!/usr/bin/env python3
"""Fix remaining 'from pi import piasync' to 'from pi import piasync'."""

import os
import re
import sys

def fix_async_imports(content):
    """Replace 'from pi import piasync' with 'from pi import piasync'."""
    modified = False
    original = content
    
    # Replace the pattern
    content = re.sub(r'from pi import piasync', 'from pi import piasync', content)
    
    if content != original:
        modified = True
    
    return content, modified

def process_file(filepath):
    """Process a single Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        fixed_content, modified = fix_async_imports(content)
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def main():
    """Find and fix all Python files with 'from pi import piasync'."""
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
    
    print(f"\nFixed async imports in {len(fixed_files)} files")

if __name__ == '__main__':
    main()
