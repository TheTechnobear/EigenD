#!/usr/bin/env python3
"""
Create a new severity entry and GitHub label.

Usage:
    python tools/gh-create-severity.py <severity>

Example:
    python tools/gh-create-severity.py critical

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
SEVERITIES_FILE = ".github/issue-metadata/severities.yml"
BUG_REPORT_FILE = ".github/ISSUE_TEMPLATE/bug_report.yml"


def load_severities():
    """Load existing severities from YAML file."""
    if os.path.exists(SEVERITIES_FILE):
        with open(SEVERITIES_FILE, 'r') as f:
            data = yaml.safe_load(f) or {}
            return data.get('severities', [])
    return []


def save_severities(severities):
    """Save severities list to YAML file."""
    os.makedirs(os.path.dirname(SEVERITIES_FILE), exist_ok=True)
    with open(SEVERITIES_FILE, 'w') as f:
        yaml.dump({'severities': severities}, f, default_flow_style=False, sort_keys=False)


def update_bug_report(severities):
    """Update bug_report.yml with the new severity list."""
    if not os.path.exists(BUG_REPORT_FILE):
        print(f"Warning: {BUG_REPORT_FILE} not found, skipping update")
        return
    
    with open(BUG_REPORT_FILE, 'r') as f:
        data = yaml.safe_load(f)
    
    # Find the severity dropdown and update its options
    for item in data.get('body', []):
        if item.get('id') == 'severity':
            item['attributes']['options'] = severities
            break
    
    with open(BUG_REPORT_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    print(f"Updated {BUG_REPORT_FILE} with new severity list")


def create_label(severity):
    """Create a GitHub label for the severity."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    auth = Auth.Token(token)
    g = Github(auth=auth)
    repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    
    label_name = f"severity: {severity}"
    
    # Check if label already exists
    try:
        existing = repo.get_label(label_name)
        print(f"Label '{label_name}' already exists")
        return
    except:
        pass
    
    # Create the label with color based on severity
    colors = {
        'critical': 'b60205',  # red
        'major': 'ff9800',     # orange
        'minor': 'fef2c0',     # light yellow
    }
    color = colors.get(severity, 'ededed')  # default gray
    
    repo.create_label(name=label_name, color=color, description=f"Severity: {severity}")
    print(f"Created label: {label_name}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python tools/gh-create-severity.py <severity>", file=sys.stderr)
        print("Example: python tools/gh-create-severity.py critical", file=sys.stderr)
        sys.exit(1)
    
    severity = sys.argv[1]
    
    # Load and update severities
    severities = load_severities()
    if severity in severities:
        print(f"Severity '{severity}' already exists in {SEVERITIES_FILE}")
    else:
        severities.append(severity)
        save_severities(severities)
        print(f"Added severity '{severity}' to {SEVERITIES_FILE}")
    
    # Update bug report template
    update_bug_report(severities)
    
    # Create GitHub label
    create_label(severity)
    
    print(f"\nDone! Don't forget to commit and push changes.")


if __name__ == '__main__':
    main()
