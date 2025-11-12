#!/usr/bin/env python3
"""
Create a new platform entry and GitHub label.

Usage:
    python tools/gh-create-platform.py <platform>

Example:
    python tools/gh-create-platform.py macOS

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
PLATFORMS_FILE = ".github/issue-metadata/platforms.yml"
BUG_REPORT_FILE = ".github/ISSUE_TEMPLATE/bug_report.yml"


def load_platforms():
    """Load existing platforms from YAML file."""
    if os.path.exists(PLATFORMS_FILE):
        with open(PLATFORMS_FILE, 'r') as f:
            data = yaml.safe_load(f) or {}
            return data.get('platforms', [])
    return []


def save_platforms(platforms):
    """Save platforms list to YAML file."""
    os.makedirs(os.path.dirname(PLATFORMS_FILE), exist_ok=True)
    with open(PLATFORMS_FILE, 'w') as f:
        yaml.dump({'platforms': platforms}, f, default_flow_style=False, sort_keys=False)


def update_bug_report(platforms):
    """Update bug_report.yml with the new platform list."""
    if not os.path.exists(BUG_REPORT_FILE):
        print(f"Warning: {BUG_REPORT_FILE} not found, skipping update")
        return
    
    with open(BUG_REPORT_FILE, 'r') as f:
        data = yaml.safe_load(f)
    
    # Find the platform dropdown and update its options
    for item in data.get('body', []):
        if item.get('id') == 'platform':
            item['attributes']['options'] = platforms
            break
    
    with open(BUG_REPORT_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    print(f"Updated {BUG_REPORT_FILE} with new platform list")


def create_label(platform):
    """Create a GitHub label for the platform."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    auth = Auth.Token(token)
    g = Github(auth=auth)
    repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    
    label_name = f"platform: {platform}"
    
    # Check if label already exists
    try:
        existing = repo.get_label(label_name)
        print(f"Label '{label_name}' already exists")
        return
    except:
        pass
    
    # Create the label (teal color)
    repo.create_label(name=label_name, color="20c997", description=f"Platform: {platform}")
    print(f"Created label: {label_name}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python tools/gh-create-platform.py <platform>", file=sys.stderr)
        print("Example: python tools/gh-create-platform.py macOS", file=sys.stderr)
        sys.exit(1)
    
    platform = sys.argv[1]
    
    # Load and update platforms
    platforms = load_platforms()
    if platform in platforms:
        print(f"Platform '{platform}' already exists in {PLATFORMS_FILE}")
    else:
        platforms.append(platform)
        save_platforms(platforms)
        print(f"Added platform '{platform}' to {PLATFORMS_FILE}")
    
    # Update bug report template
    update_bug_report(platforms)
    
    # Create GitHub label
    create_label(platform)
    
    print(f"\nDone! Don't forget to commit and push changes.")


if __name__ == '__main__':
    main()
