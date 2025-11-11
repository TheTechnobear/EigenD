#!/usr/bin/env python3
"""
Fix exception handling for Python 3.
Converts 'except Exception as e:' to 'except Exception as e:'
"""

import re
import sys
import os

def fix_except_in_file(filepath):
    """Fix except statements in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return False
    
    original = content
    
    # Pattern 1: except Exception as e:
    # Match: except SomeException as variable_name:
    content = re.sub(r'\bexcept\s+(\w+)\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'except \1 as \2:', content)
    
    # Pattern 2: except (Exception1, Exception2) as e:
    # Match: except (Exception1, Exception2) as variable_name:
    content = re.sub(r'\bexcept\s+\(([^)]+)\)\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'except (\1) as \2:', content)
    
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
        if any(skip in root for skip in ['.git', '__pycache__', 'tmp', '.egg-info', '.venv']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_except_in_file(filepath):
                    print(f"Fixed: {filepath}")
                    count += 1
    
    print(f"\nFixed except statements in {count} files")

if __name__ == '__main__':
    main()
