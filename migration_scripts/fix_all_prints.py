#!/usr/bin/env python3
"""Fix ALL remaining Python 2 print statements comprehensively."""

import os
import re
import sys

def fix_print_statements_complete(content):
    """Fix all print statement patterns including complex cases."""
    lines = content.split('\n')
    fixed_lines = []
    modified = False
    
    for line in lines:
        original = line
        
        # Skip comments and docstrings
        stripped = line.lstrip()
        if stripped.startswith('#'):
            fixed_lines.append(line)
            continue
        
        # Check if this line has a print statement (not print function)
        # Match: print followed by space and NOT followed by (
        if re.match(r'^(\s*)print\s+(?![(\s]*$)', line):
            indent_match = re.match(r'^(\s*)print\s+', line)
            if indent_match:
                indent = indent_match.group(1)
                rest = line[len(indent)+6:]  # Skip "print "
                
                # Handle print >>file, args pattern
                if rest.startswith('>>'):
                    file_match = re.match(r'>>\s*(\S+)\s*,\s*(.+)$', rest)
                    if file_match:
                        filehandle, args = file_match.groups()
                        fixed_lines.append(f'{indent}print({args}, file={filehandle})')
                        modified = True
                        continue
                
                # Handle trailing comma (suppresses newline in Python 2)
                # For Python 3, use end=''
                if rest.rstrip().endswith(','):
                    args = rest.rstrip()[:-1].strip()  # Remove trailing comma
                    fixed_lines.append(f'{indent}print({args}, end="")')
                    modified = True
                    continue
                
                # Normal case: just wrap in parentheses
                fixed_lines.append(f'{indent}print({rest})')
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
        
        fixed_content, modified = fix_print_statements_complete(content)
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def main():
    """Find and fix all Python files with remaining print statements."""
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
    
    print(f"\nFixed print statements in {len(fixed_files)} files")

if __name__ == '__main__':
    main()
