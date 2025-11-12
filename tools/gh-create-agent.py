#!/usr/bin/env python3
"""
Create a new agent entry and GitHub label.

Usage:
    python tools/gh-create-agent.py <agent>

Example:
    python tools/gh-create-agent.py sampler

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
AGENTS_FILE = ".github/issue-metadata/agents.yml"
BUG_REPORT_FILE = ".github/ISSUE_TEMPLATE/bug_report.yml"


def load_agents():
    """Load existing agents from YAML file."""
    if os.path.exists(AGENTS_FILE):
        with open(AGENTS_FILE, 'r') as f:
            data = yaml.safe_load(f) or {}
            return data.get('agents', [])
    return []


def save_agents(agents):
    """Save agents list to YAML file."""
    os.makedirs(os.path.dirname(AGENTS_FILE), exist_ok=True)
    with open(AGENTS_FILE, 'w') as f:
        yaml.dump({'agents': agents}, f, default_flow_style=False, sort_keys=False)


def update_bug_report(agents):
    """Update bug_report.yml with the new agent list."""
    if not os.path.exists(BUG_REPORT_FILE):
        print(f"Warning: {BUG_REPORT_FILE} not found, skipping update")
        return
    
    with open(BUG_REPORT_FILE, 'r') as f:
        data = yaml.safe_load(f)
    
    # Find the agent dropdown and update its options
    for item in data.get('body', []):
        if item.get('id') == 'agent':
            item['attributes']['options'] = agents
            break
    
    with open(BUG_REPORT_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    print(f"Updated {BUG_REPORT_FILE} with new agent list")


def create_label(agent):
    """Create a GitHub label for the agent."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    auth = Auth.Token(token)
    g = Github(auth=auth)
    repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    
    label_name = f"agent: {agent}"
    
    # Check if label already exists
    try:
        existing = repo.get_label(label_name)
        print(f"Label '{label_name}' already exists")
        return
    except:
        pass
    
    # Create the label (purple color)
    repo.create_label(name=label_name, color="6f42c1", description=f"Agent: {agent}")
    print(f"Created label: {label_name}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python tools/gh-create-agent.py <agent>", file=sys.stderr)
        print("Example: python tools/gh-create-agent.py sampler", file=sys.stderr)
        sys.exit(1)
    
    agent = sys.argv[1]
    
    # Load and update agents
    agents = load_agents()
    if agent in agents:
        print(f"Agent '{agent}' already exists in {AGENTS_FILE}")
    else:
        agents.append(agent)
        save_agents(agents)
        print(f"Added agent '{agent}' to {AGENTS_FILE}")
    
    # Update bug report template
    update_bug_report(agents)
    
    # Create GitHub label
    create_label(agent)
    
    print(f"\nDone! Don't forget to commit and push changes.")


if __name__ == '__main__':
    main()
