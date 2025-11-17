# EigenD Copilot Instructions

## Project Overview

EigenD is an application suite designed for musicians with Eigenharp hardware (Pico, Tau, and Alpha). EigenD is the main application, running the server.

## Technical Architecture

Agents are functional blocks with data and connection points. These agents are connected together with wires. Plugins are a compilation unit containing multiple agents. The Rig agent is a container that can contain other agents and exposes an interface as a gateway.

## Technologies Used

**C++**
- C++17
**Juce** 
- GUI and Audio framework, currently Juce 8.0.10
**Python**
- C++ interfaces to Python using CPython
- PIP files are C++ to Python definitions; these are used to generate C++ bindings to Python
- Runtime : use python3.14 from python.org
- Buildtime : use virtual environment, setup in .venv_dev
**Crossplatform**
- support for macOS, Windows and Linux
**Build tools**
- SCons4 embedded within project tools/packages/SCons4
- CMake and Make are wrappers to invoke Sons4

## Project Structure

### Folder Naming Convention

Prefixes for folders:
- `app_`: Applications
- `lib_`: Lower-level C++ libraries
- `plg_`: Plugins

### Root Folders

- `app_browser2`: Browser application for EigenD
- `app_cmdline`: Command line tools and utilities
- `app_commander`: Commander application interface
- `app_eigend2`: Core EigenD application and backend
- `app_stage`: Stage application for performance
- `app_workbench`: Workbench development environment
- `dev_docs`: Development documentation and guides
- `documentation`: User documentation and manuals
- `lib_alpha2`: Alpha and Tau hardware interface
- `lib_fftw`: FFTW fast Fourier transform library
- `lib_juce`: JUCE cross-platform framework
- `lib_lo`: Liblo OSC library
- `lib_micro`: Microcontroller interface library
- `lib_midi`: MIDI processing library
- `lib_op`: OSC library
- `lib_pico`: Pico hardware interface
- `lib_samplerate`: Sample rate conversion library
- `lib_sqlite`: SQLite database library
- `pi`: Core PI system components
- `piagent`: Agent management component
- `pibelcanto`: Belcanto synthesis component
- `picross`: Cross-platform utilities
- `piembedded`: Embedded system components
- `pigui`: Graphical user interface components
- `pisession`: Session management system
- `piw`: Widget library
- `plg_arranger`: Arranger plugin
- `plg_audio`: Audio processing plugin
- `plg_conductor`: Conductor plugin
- `plg_convolver`: Convolution reverb plugin
- `plg_finger`: Finger tracking plugin
- `plg_host`: Host plugin interface
- `plg_illuminator`: Illuminator plugin
- `plg_keyboard`: Alpha and Tau keyboard plugin
- `plg_language`: Language processing plugin
- `plg_livepad`: Livepad performance plugin
- `plg_loop`: Looping plugin
- `plg_midi`: MIDI plugin
- `plg_midi_device`: MIDI device plugin
- `plg_midi_monitor`: MIDI monitoring plugin
- `plg_osc`: OSC communication plugin
- `plg_pkbd`: Pico keyboard plugin
- `plg_primitive`: Primitive synthesis plugin
- `plg_recorder`: Recording plugin
- `plg_rig`: Rig management plugin
- `plg_sampler2`: Sampler plugin
- `plg_scale_illuminator`: Scale illuminator plugin
- `plg_simple`: Simple plugin
- `plg_stk`: STK synthesis toolkit plugin
- `plg_strummer`: Strummer plugin
- `plg_synth`: Synthesizer plugin
- `plg_t3d`: 3D visualization plugin
- `plg_tabulator`: Tabulator plugin
- `plg_ukbd`: Micro keyboard plugin
- `tools`: Build tools and scripts

## Guidelines

### Behavior
- Answer concisely. Use short bullets: done / discovered / next steps.
- Keep replies neutral and brief.
- use ripgrep in preference to grep

### Preferred Reply Format
- 1–3 short bullets: (done, discovered, next steps).
- If producing or modifying files, include filepaths.

### Mandatory Actions
- After major changes, update `.github/copilot-session_resume.md`.
- Date-stamp notable updates (YYYY-MM-DD).

### Documentation Policy
- Do not add general top-level docs without consent.
- Update existing `dev_docs/*` where required.

### Session summarization and context window management
- Purpose: avoid excessive context use by summarising long sessions into a compact session summary and keeping only recent active context.
- Triggers (agent should auto-summarise when any condition met):
	- > 30 messages exchanged in current session, OR
	- Estimated tokens for conversation > 8000, OR
	- > 10 file edits in workspace during session.
- Summarisation behaviour:
	- Produce a compact summary (6–10 bullets) containing: decisions made, open tasks, modified files, important parameters/thresholds, commands to re-run build/tests.
	- Keep the last 5 full messages (most recent user + assistant exchanges) verbatim; compress older messages into the summary.
	- Store summaries under `.github/session_summaries/{YYYY-MM-DD}_{session_id}.md` and append a one-line session_resume entry in `.github/copilot-session_resume.md` (date-stamped).
	- Before dropping or pruning any user-provided code or large blocks, ask for confirmation if the code is flagged as "important" (e.g., test code, new feature code).
- Format for stored summary (example):
	- Date: YYYY-MM-DD
	- Session ID: <auto-id>
	- Key decisions: (short bullets)
	- Open tasks: (short bullets with file paths)
	- Files changed: (list)
	- Commands to reproduce: (one-line make / scons command)
- Compression rules:
	- Convert long dialogues into numbered bullets with references to file paths and line ranges where applicable.
	- Strip verbose conversational filler; retain explicit instructions, config values, and file paths.
- Safety & provenance:
	- Never auto-delete user files; only summarise conversation context.
	- Keep at least the last 5 messages and the session summary in active context to preserve continuity.
- Configuration:
	- Default thresholds are editable by maintainers; list the current values in this file for transparency.
- Minimal prompt to user when summarising:
	- "Context limit reached; I'll summarise older messages to save tokens. Proceed? (yes / no / adjust threshold)"
- Note: After major instruction/file changes, update `.github/copilot-session_resume.md` with a date-stamped note (YYYY-MM-DD).

## Tools - Building and Testing

### Guidelines for Building
- Use `make` in preference.
- Use tee and `|` to retain build output, e.g., `make 2>&1 | tee build.log`.
- Build specific modules via SCons using Python path:

```bash
PYTHONPATH=tools/packages/SCons4 python3 tools/packages/SCons4/bin/scons -f tools/SConstruct <module>
```
    
