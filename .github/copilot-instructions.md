# EigenD Copilot Instructions

Keep this file small and editable. Move detailed, workspace-specific information into `dev_docs/prompts/`.

- Behaviour
    - Answer concisely. Use short bullets: done / discovered / next steps.
    - Keep replies neutral and brief.

- Mandatory actions
    - After major changes, update `dev_docs/copilot-session_resume.md`
    - Date-stamp notable updates (YYYY-MM-DD).

- Documentation policy
    - Do not add general top-level docs without consent. 
    - Updating existing `dev_docs/*` where required
    - It's allowed to create/update files under `dev_docs/prompts/` to hold moved technical details.

- Where to find details
    - See `dev_docs/prompts/` for migration notes, build/test commands, and gotchas.

- Preferred reply format
    - 1–3 short bullets: (done, discovered, next steps).
    - If producing or modifying files, include filepaths.


- Notes for building
    - use `make` in preference
    - if you need to build a specific module use `PYTHONPATH=tools/packages/SCons4 python3 tools/packages/SCons4/bin/scons -f tools/SConstruct <module>`
    - when building, pipe full output to a logile (default : build.log), so that contents can be inspected later
    
(Keep this file minimal — move specifics to `dev_docs/prompts/`)