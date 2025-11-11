#!/usr/bin/env python3
"""Fix remaining Python 2 print statements to Python 3 print() functions."""

import os
import re
import sys

def fix_print_statements(content):
    """Fix all remaining print statement patterns."""
    lines = content.split('\n')
    fixed_lines = []
    modified = False
    
    for line in lines:
        original = line
        
        # Skip comments and docstrings
        stripped = line.lstrip()
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            fixed_lines.append(line)
            continue
        
        # Pattern 1: print >>file, args (Python 2 file redirection)
        # Convert to: print(args, file=file)
        match = re.match(r'^(\s*)print\s+>>(\w+)\s*,\s*(.+)$', line)
        if match:
            indent, filehandle, args = match.groups()
            fixed_lines.append(f'{indent}print({args}, file={filehandle})')
            modified = True
            continue
        
        # Pattern 2: print "string" % args (with modulo formatting)
        match = re.match(r'^(\s*)print\s+"([^"]+)"\s*%\s*(.+)$', line)
        if match:
            indent, string, args = match.groups()
            fixed_lines.append(f'{indent}print("{string}" % {args})')
            modified = True
            continue
        
        # Pattern 3: print 'string' % args (single quote version)
        match = re.match(r"^(\s*)print\s+'([^']+)'\s*%\s*(.+)$", line)
        if match:
            indent, string, args = match.groups()
            fixed_lines.append(f"{indent}print('{string}' % {args})")
            modified = True
            continue
        
        # Pattern 4: print "string", args (comma-separated, ends with comma keeps it)
        match = re.match(r'^(\s*)print\s+"([^"]+)"\s*,\s*(.+)$', line)
        if match:
            indent, string, args = match.groups()
            fixed_lines.append(f'{indent}print("{string}", {args})')
            modified = True
            continue
        
        # Pattern 5: print 'string', args (single quote version)
        match = re.match(r"^(\s*)print\s+'([^']+)'\s*,\s*(.+)$", line)
        if match:
            indent, string, args = match.groups()
            fixed_lines.append(f"{indent}print('{string}', {args})")
            modified = True
            continue
        
        # Pattern 6: simple print "string" or print 'string'
        match = re.match(r'^(\s*)print\s+(["\'])([^\2]+)\2\s*$', line)
        if match:
            indent, quote, string = match.groups()
            fixed_lines.append(f'{indent}print({quote}{string}{quote})')
            modified = True
            continue
        
        # Pattern 7: print variable (no quotes, no formatting)
        match = re.match(r'^(\s*)print\s+([a-zA-Z_]\w*)(?:\s*$|(?=\s+#))', line)
        if match:
            indent, var = match.groups()
            # Preserve inline comments if any
            comment_match = re.search(r'(\s+#.*)$', line)
            comment = comment_match.group(1) if comment_match else ''
            fixed_lines.append(f'{indent}print({var}){comment}')
            modified = True
            continue
        
        # No match, keep original
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), modified

def process_file(filepath):
    """Process a single Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        fixed_content, modified = fix_print_statements(content)
        
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
