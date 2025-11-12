# GitHub Issue Management Tools

Python scripts to manage GitHub issue labels and metadata for the EigenD project.

## Setup

Install dependencies:
```bash
pip install PyGithub PyYAML
```

Set your GitHub token:
```bash
export GITHUB_TOKEN=your_personal_access_token_here
```

## Scripts

### gh-create-version.py
Add a new version and create its label.

```bash
python tools/gh-create-version.py 3.1.0-release
```

Updates: `.github/issue-metadata/versions.yml`  
Creates label: `version: 3.1.0-release` (blue)

### gh-create-component.py
Add a new component and create its label.

```bash
python tools/gh-create-component.py Plugin
```

Updates: `.github/issue-metadata/components.yml`  
Creates label: `component: Plugin` (green)

### gh-create-agent.py
Add a new agent and create its label.

```bash
python tools/gh-create-agent.py sampler
```

Updates: `.github/issue-metadata/agents.yml`  
Creates label: `agent: sampler` (purple)

### gh-create-hardware.py
Add a new hardware type and create its label.

```bash
python tools/gh-create-hardware.py BaseStation
```

Updates: `.github/issue-metadata/hardware.yml`  
Creates label: `hardware: BaseStation` (orange)

### gh-create-status.py
Create a status label (no metadata file).

```bash
python tools/gh-create-status.py investigating
```

Creates label: `status: investigating` (yellow)

## After Running Scripts

1. Update `.github/ISSUE_TEMPLATE/bug_report.yml` to include the new values in dropdowns
2. Commit and push changes
3. The issue-labeler workflow will automatically apply these labels based on form selections

## Initial Setup

To create all default labels, run:

```bash
# Versions
python tools/gh-create-version.py 2.2.1-release
python tools/gh-create-version.py 3.0.0-beta-1

# Components
python tools/gh-create-component.py EigenD
python tools/gh-create-component.py Workbench
python tools/gh-create-component.py Stage
python tools/gh-create-component.py Agent
python tools/gh-create-component.py Hardware
python tools/gh-create-component.py Setup
python tools/gh-create-component.py Other

# Agents
python tools/gh-create-agent.py audio
python tools/gh-create-agent.py pico
python tools/gh-create-agent.py alpha
python tools/gh-create-agent.py tau
python tools/gh-create-agent.py keygroup
python tools/gh-create-agent.py scaler
python tools/gh-create-agent.py talker
python tools/gh-create-agent.py rig
python tools/gh-create-agent.py host
python tools/gh-create-agent.py midi_device
python tools/gh-create-agent.py midi_converter

# Hardware
python tools/gh-create-hardware.py Alpha
python tools/gh-create-hardware.py Tau
python tools/gh-create-hardware.py Pico

# Status
python tools/gh-create-status.py triage
python tools/gh-create-status.py confirmed
python tools/gh-create-status.py in-progress
python tools/gh-create-status.py fixed
python tools/gh-create-status.py wont-fix
```
