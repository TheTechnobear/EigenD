2025-11-12: Added issue form and labeler workflow on branches 2.2 and 3.0.

Files added:
- .github/ISSUE_TEMPLATE/bug_report.yml
- .github/workflows/issue-labeler.yml
- .github/issue-metadata/versions.yml

Notes:
- Agent field is optional in the form (GitHub forms do not support conditional fields). The workflow will only add an agent label when the field is filled.
- Hardware is a required dropdown with fixed options.
