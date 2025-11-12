#!/usr/bin/env python3
"""
Create a status GitHub label.

Usage:
    python tools/gh-create-status.py <status>

Example:
    python tools/gh-create-status.py investigating

Requires:
    - GITHUB_TOKEN environment variable set
    - PyGithub: pip install PyGithub
"""

import os
import sys
from github import Github, Auth

REPO_OWNER = "thetechnobear"
REPO_NAME = "EigenD"


def create_label(status):
    """Create a GitHub label for the status."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    auth = Auth.Token(token)
    g = Github(auth=auth)
    repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    
    label_name = f"status: {status}"
    
    # Check if label already exists
    try:
        existing = repo.get_label(label_name)
        print(f"Label '{label_name}' already exists")
        return
    except:
        pass
    
    # Create the label (yellow color for status)
    repo.create_label(name=label_name, color="fbca04", description=f"Status: {status}")
    print(f"Created label: {label_name}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python tools/gh-create-status.py <status>", file=sys.stderr)
        print("Example: python tools/gh-create-status.py investigating", file=sys.stderr)
        sys.exit(1)
    
    status = sys.argv[1]
    
    # Create GitHub label
    create_label(status)
    
    print(f"\nCreated status label: status: {status}")


if __name__ == '__main__':
    main()
