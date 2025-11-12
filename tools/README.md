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

#