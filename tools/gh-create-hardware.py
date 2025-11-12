#!/usr/bin/env python3
"""
Create a new hardware entry and GitHub label.

Usage:
    python tools/gh-create-hardware.py <hardware>

Example:
    python tools/gh-create-hardware.py BaseStation

Requires:
    - GITHUB_TOKEN environment variable set
    - PyGithub: pip install PyGithub PyYAML
"""

import os
import sys
import yaml
from github import Github

REPO_OWNER = "thetechnobear"
REPO_NAME = "EigenD"
HARDWARE_FILE = ".github/issue-metadata/hardware.yml"


def load_hardware():
    """Load existing hardware from YAML file."""
    if os.path.exists(HARDWARE_FILE):
        with open(HARDWARE_FILE, 'r') as f:
            data = yaml.safe_load(f) or {}
            return data.get('hardware', [])
    return []


def save_hardware(hardware_list):
    """Save hardware list to YAML file."""
    os.makedirs(os.path.dirname(HARDWARE_FILE), exist_ok=True)
    with open(HARDWARE_FILE, 'w') as f:
        yaml.dump({'hardware': hardware_list}, f, default_flow_style=False, sort_keys=False)


def create_label(hardware):
    """Create a GitHub label for the hardware."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    g = Github(token)
    repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    
    label_name = f"hardware: {hardware}"
    
    # Check if label already exists
    try:
        existing = repo.get_label(label_name)
        print(f"Label '{label_name}' already exists")
        return
    except:
        pass
    
    # Create the label (orange color)
    repo.create_label(name=label_name, color="d93f0b", description=f"Hardware: {hardware}")
    print(f"Created label: {label_name}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python tools/gh-create-hardware.py <hardware>", file=sys.stderr)
        print("Example: python tools/gh-create-hardware.py BaseStation", file=sys.stderr)
        sys.exit(1)
    
    hardware = sys.argv[1]
    
    # Load and update hardware
    hardware_list = load_hardware()
    if hardware in hardware_list:
        print(f"Hardware '{hardware}' already exists in {HARDWARE_FILE}")
    else:
        hardware_list.append(hardware)
        save_hardware(hardware_list)
        print(f"Added hardware '{hardware}' to {HARDWARE_FILE}")
    
    # Create GitHub label
    create_label(hardware)
    
    print(f"\nDone! Don't forget to:")
    print(f"  1. Update .github/ISSUE_TEMPLATE/bug_report.yml to include '{hardware}' in the hardware dropdown")
    print(f"  2. Commit and push changes")


if __name__ == '__main__':
    main()
