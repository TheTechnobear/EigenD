#!/usr/bin/env python3
"""
Fix async keyword issues in Python files for Python 3 migration.
Changes:
1. 'from pi import ...async...' -> 'from pi import ...piasync...'
2. All 'async.' references -> 'piasync.'
"""

import re
import sys
import os

def fix_async_imports_and_usage(content):
    """Fix both imports and usage of async module."""
    
    # Step 1: Fix imports - replace 'async' with 'piasync' in import statements
    # Handle various import patterns
    
    # Pattern 1: async at the start: "from pi import async,..."
    content = re.sub(
        r'(\bfrom pi import\s+)async\b',
        r'\1piasync',
        content
    )
    
    # Pattern 2: async in the middle or end: "from pi import ...,async,..."
    content = re.sub(
        r'(\bfrom pi import\s+[^;\n]*?),\s*async\b',
        r'\1,piasync',
        content
    )
    
    # Step 2: Replace all usage of 'async.' with 'piasync.'
    # Use word boundary to avoid replacing 'asyncio' or other similar words
    content = re.sub(
        r'\basync\.',
        r'piasync.',
        content
    )
    
    # Step 3: Fix 'piasync as async' back to just 'piasync' if it exists
    content = re.sub(
        r'\bpiasync\s+as\s+async\b',
        r'piasync',
        content
    )
    
    return content

def process_file(filepath):
    """Process a single Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        fixed_content = fix_async_imports_and_usage(original_content)
        
        if fixed_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"Fixed: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def main():
    """Main function to process all Python files."""
    import subprocess
    
    # Find all Python files in relevant directories
    files = []
    for pattern in ['pi', 'pisession', 'plg_*', 'app_*']:
        try:
            result = subprocess.run(
                ['find', pattern, '-name', '*.py', '-type', 'f'],
                capture_output=True,
                text=True,
                check=False,
                shell=False
            )
            if result.returncode == 0:
                files.extend(result.stdout.strip().split('\n'))
        except Exception as e:
            print(f"Warning: Could not search {pattern}: {e}", file=sys.stderr)
    
    fixed_count = 0
    for filepath in files:
        if filepath and os.path.isfile(filepath):
            if process_file(filepath):
                fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
