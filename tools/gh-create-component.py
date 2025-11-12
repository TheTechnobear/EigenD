#!/usr/bin/env python3
"""
Create a new component entry and GitHub label.

Usage:
    python tools/gh-create-component.py <component>

Example:
    python tools/gh-create-component.py Plugin

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
COMPONENTS_FILE = ".github/issue-metadata/components.yml"
BUG_REPORT_FILE = ".github/ISSUE_TEMPLATE/bug_report.yml"


def load_components():
    """Load existing components from YAML file."""
    if os.path.exists(COMPONENTS_FILE):
        with open(COMPONENTS_FILE, 'r') as f:
            data = yaml.safe_load(f) or {}
            return data.get('components', [])
    return []


def save_components(components):
    """Save components list to YAML file."""
    os.makedirs(os.path.dirname(COMPONENTS_FILE), exist_ok=True)
    with open(COMPONENTS_FILE, 'w') as f:
        yaml.dump({'components': components}, f, default_flow_style=False, sort_keys=False)


def update_bug_report(components):
    """Update bug_report.yml with the new component list."""
    if not os.path.exists(BUG_REPORT_FILE):
        print(f"Warning: {BUG_REPORT_FILE} not found, skipping update")
        return
    
    with open(BUG_REPORT_FILE, 'r') as f:
        data = yaml.safe_load(f)
    
    # Find the component dropdown and update its options
    for item in data.get('body', []):
        if item.get('id') == 'component':
            item['attributes']['options'] = components
            break
    
    with open(BUG_REPORT_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    print(f"Updated {BUG_REPORT_FILE} with new component list")


def create_label(component):
    """Create a GitHub label for the component."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    auth = Auth.Token(token)
    g = Github(auth=auth)
    repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    
    label_name = f"component: {component}"
    
    # Check if label already exists
    try:
        existing = repo.get_label(label_name)
        print(f"Label '{label_name}' already exists")
        return
    except:
        pass
    
    # Create the label (green color)
    repo.create_label(name=label_name, color="28a745", description=f"Component: {component}")
    print(f"Created label: {label_name}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python tools/gh-create-component.py <component>", file=sys.stderr)
        print("Example: python tools/gh-create-component.py Plugin", file=sys.stderr)
        sys.exit(1)
    
    component = sys.argv[1]
    
    # Load and update components
    components = load_components()
    if component in components:
        print(f"Component '{component}' already exists in {COMPONENTS_FILE}")
    else:
        components.append(component)
        save_components(components)
        print(f"Added component '{component}' to {COMPONENTS_FILE}")
    
    # Update bug report template
    update_bug_report(components)
    
    # Create GitHub label
    create_label(component)
    
    print(f"\nDone! Don't forget to commit and push changes.")


if __name__ == '__main__':
    main()
