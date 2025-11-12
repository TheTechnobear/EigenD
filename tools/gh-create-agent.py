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
from github import Github

REPO_OWNER = "thetechnobear"
REPO_NAME = "EigenD"
AGENTS_FILE = ".github/issue-metadata/agents.yml"


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


def create_label(agent):
    """Create a GitHub label for the agent."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    g = Github(token)
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
    
    # Create GitHub label
    create_label(agent)
    
    print(f"\nDone! Don't forget to:")
    print(f"  1. Update .github/ISSUE_TEMPLATE/bug_report.yml to include '{agent}' in the agent dropdown")
    print(f"  2. Commit and push changes")


if __name__ == '__main__':
    main()
