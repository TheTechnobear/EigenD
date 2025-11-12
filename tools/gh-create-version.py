#!/usr/bin/env python3
"""
Create a new version entry and GitHub label.

Usage:
    python tools/gh-create-labels.py <version>

Example:
    python tools/gh-create-labels.py 3.1.0-release

Requires:
    - GITHUB_TOKEN environment variable set
    - PyGithub: pip install PyGithub
"""

import os
import sys
import yaml
from github import Github, Auth

REPO_OWNER = "thetechnobear"
REPO_NAME = "EigenD"
VERSIONS_FILE = ".github/issue-metadata/versions.yml"
BUG_REPORT_FILE = ".github/ISSUE_TEMPLATE/bug_report.yml"


def load_versions():
    """Load existing versions from YAML file."""
    if os.path.exists(VERSIONS_FILE):
        with open(VERSIONS_FILE, 'r') as f:
            data = yaml.safe_load(f) or {}
            return data.get('versions', [])
    return []


def save_versions(versions):
    """Save versions list to YAML file."""
    os.makedirs(os.path.dirname(VERSIONS_FILE), exist_ok=True)
    with open(VERSIONS_FILE, 'w') as f:
        yaml.dump({'versions': versions}, f, default_flow_style=False, sort_keys=False)


def update_bug_report(versions):
    """Update bug_report.yml with the new version list."""
    if not os.path.exists(BUG_REPORT_FILE):
        print(f"Warning: {BUG_REPORT_FILE} not found, skipping update")
        return
    
    with open(BUG_REPORT_FILE, 'r') as f:
        data = yaml.safe_load(f)
    
    # Find the version dropdown and update its options
    for item in data.get('body', []):
        if item.get('id') == 'version':
            item['attributes']['options'] = versions
            break
    
    with open(BUG_REPORT_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    print(f"Updated {BUG_REPORT_FILE} with new version list")


def create_label(version):
    """Create a GitHub label for the version."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    auth = Auth.Token(token)
    g = Github(auth=auth)
    repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    
    label_name = f"version: {version}"
    
    # Check if label already exists
    try:
        existing = repo.get_label(label_name)
        print(f"Label '{label_name}' already exists")
        return
    except:
        pass
    
    # Create the label (blue color)
    repo.create_label(name=label_name, color="0366d6", description=f"Version {version}")
    print(f"Created label: {label_name}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python tools/gh-create-labels.py <version>", file=sys.stderr)
        print("Example: python tools/gh-create-labels.py 3.1.0-release", file=sys.stderr)
        sys.exit(1)
    
    version = sys.argv[1]
    
    # Load and update versions
    versions = load_versions()
    if version in versions:
        print(f"Version '{version}' already exists in {VERSIONS_FILE}")
    else:
        versions.append(version)
        save_versions(versions)
        print(f"Added version '{version}' to {VERSIONS_FILE}")
    
    # Update bug report template
    update_bug_report(versions)
    
    # Create GitHub label
    create_label(version)
    
    print(f"\nDone! Don't forget to commit and push changes.")


if __name__ == '__main__':
    main()