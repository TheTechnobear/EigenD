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
from github import Github

REPO_OWNER = "thetechnobear"
REPO_NAME = "EigenD"
COMPONENTS_FILE = ".github/issue-metadata/components.yml"


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


def create_label(component):
    """Create a GitHub label for the component."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    g = Github(token)
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
    
    # Create GitHub label
    create_label(component)
    
    print(f"\nDone! Don't forget to:")
    print(f"  1. Update .github/ISSUE_TEMPLATE/bug_report.yml to include '{component}' in the component dropdown")
    print(f"  2. Commit and push changes")


if __name__ == '__main__':
    main()
