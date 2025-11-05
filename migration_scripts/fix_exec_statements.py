#!/usr/bin/env python3
"""Fix Python 2 exec statements to Python 3 exec() functions."""

import os
import re
import sys

def fix_exec_statements(content):
    """Fix all exec statement patterns."""
    lines = content.split('\n')
    fixed_lines = []
    modified = False
    
    for line in lines:
        # Skip comments
        stripped = line.lstrip()
        if stripped.startswith('#'):
            fixed_lines.append(line)
            continue
        
        # Pattern: exec "string" or exec 'string' or exec expression
        # Match: exec followed by space and NOT followed by (
        match = re.match(r'^(\s*)exec\s+(?!\()(.+)$', line)
        if match:
            indent, expression = match.groups()
            # Wrap the expression in parentheses
            fixed_lines.append(f'{indent}exec({expression})')
            modified = True
            continue
        
        # No modification needed
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), modified

def process_file(filepath):
    """Process a single Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        fixed_content, modified = fix_exec_statements(content)
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def main():
    """Find and fix all Python files with exec statements."""
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
    
    print(f"\nFixed exec statements in {len(fixed_files)} files")

if __name__ == '__main__':
    main()
