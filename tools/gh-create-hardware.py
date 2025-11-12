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
from github import Github, Auth

REPO_OWNER = "thetechnobear"
REPO_NAME = "EigenD"
HARDWARE_FILE = ".github/issue-metadata/hardware.yml"
BUG_REPORT_FILE = ".github/ISSUE_TEMPLATE/bug_report.yml"


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


def update_bug_report(hardware_list):
    """Update bug_report.yml with the new hardware list."""
    if not os.path.exists(BUG_REPORT_FILE):
        print(f"Warning: {BUG_REPORT_FILE} not found, skipping update")
        return
    
    with open(BUG_REPORT_FILE, 'r') as f:
        data = yaml.safe_load(f)
    
    # Find the hardware dropdown and update its options
    for item in data.get('body', []):
        if item.get('id') == 'hardware':
            item['attributes']['options'] = hardware_list
            break
    
    with open(BUG_REPORT_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    print(f"Updated {BUG_REPORT_FILE} with new hardware list")


def create_label(hardware):
    """Create a GitHub label for the hardware."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    auth = Auth.Token(token)
    g = Github(auth=auth)
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
    
    # Update bug report template
    update_bug_report(hardware_list)
    
    # Create GitHub label
    create_label(hardware)
    
    print(f"\nDone! Don't forget to commit and push changes.")


if __name__ == '__main__':
    main()
