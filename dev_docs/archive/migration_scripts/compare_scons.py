#!/usr/bin/env python3
"""
Compare current SCons 2.5.1 with SCons 4.x to identify modifications
"""
import os
import sys
import filecmp
import difflib

def compare_scons_versions():
    """Compare the embedded SCons versions"""

    old_scons = "tools/packages/SCons"
    new_scons = "tools/packages/SCons4/SCons"  # SCons module is inside the pip package

    if not os.path.exists(old_scons):
        print(f"Old SCons not found at {old_scons}")
        return

    if not os.path.exists(new_scons):
        print(f"New SCons not found at {new_scons}")
        return

    print("Comparing SCons versions...")
    print(f"Old: {old_scons}")
    print(f"New: {new_scons}")
    print()

    # Get file lists
    old_files = []
    new_files = []

    for root, dirs, files in os.walk(old_scons):
        for file in files:
            if file.endswith('.py'):
                old_files.append(os.path.relpath(os.path.join(root, file), old_scons))

    for root, dirs, files in os.walk(new_scons):
        for file in files:
            if file.endswith('.py'):
                new_files.append(os.path.relpath(os.path.join(root, file), new_scons))

    # Find common files
    common_files = set(old_files) & set(new_files)
    only_old = set(old_files) - set(new_files)
    only_new = set(new_files) - set(old_files)

    print(f"Common Python files: {len(common_files)}")
    print(f"Files only in old SCons: {len(only_old)}")
    print(f"Files only in new SCons: {len(only_new)}")
    print()

    # Compare common files
    modified_files = []
    for file in sorted(common_files):
        old_path = os.path.join(old_scons, file)
        new_path = os.path.join(new_scons, file)

        if not filecmp.cmp(old_path, new_path, shallow=False):
            modified_files.append(file)

    print(f"Modified files: {len(modified_files)}")
    if modified_files:
        print("\nModified files:")
        for file in modified_files[:10]:  # Show first 10
            print(f"  {file}")
        if len(modified_files) > 10:
            print(f"  ... and {len(modified_files) - 10} more")

    # Check for EigenD-specific customizations
    print("\nChecking for EigenD-specific customizations...")

    # Look for references to EigenD-specific paths or variables
    eigend_specific = []
    for file in modified_files:
        old_path = os.path.join(old_scons, file)
        try:
            with open(old_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if any(term in content for term in ['eigend', 'EigenD', 'PI_', 'generic_tools']):
                    eigend_specific.append(file)
        except:
            pass

    if eigend_specific:
        print(f"Files with potential EigenD customizations: {len(eigend_specific)}")
        for file in eigend_specific:
            print(f"  {file}")
    else:
        print("No obvious EigenD-specific customizations found")

if __name__ == "__main__":
    compare_scons_versions()