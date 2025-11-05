#!/usr/bin/env python3
"""
Fix async keyword issues for Python 3 compatibility.
Replaces 'from pi import ...async...' with 'from pi import piasync' 
and updates all async. references to piasync.
"""

import re
import sys

files = [
    "./app_browser2/browse_db.py",
    "./app_browser2/browse.py",
    "./app_cmdline/bcat2.py",
    "./app_cmdline/capture.py",
    "./app_cmdline/download.py",
    "./app_cmdline/mirror.py",
    "./app_cmdline/rexec.py",
    "./app_cmdline/rpc.py",
    "./app_cmdline/script.py",
    "./app_juceworkbench/workbench.py",
    "./pisession/agentd.py",
    "./pisession/gui.py",
    "./pisession/session.py",
    "./pisession/workspace.py",
    "./plg_arranger/arranger_plg.py",
    "./plg_audio/audio_plg.py",
    "./plg_conductor/clip_manager_plg.py",
    "./plg_conductor/conductor_plg.py",
    "./plg_convolver/convolver_plg.py",
    "./plg_host/host_plg.py",
    "./plg_illuminator/illuminator_plg.py",
    "./plg_keyboard/test.py",
    "./plg_language/builtin_misc.py",
    "./plg_language/context.py",
    "./plg_language/controller_plg.py",
    "./plg_language/database.py",
    "./plg_language/deferred.py",
    "./plg_language/imperative.py",
    "./plg_language/interpreter.py",
    "./plg_language/language_plg.py",
    "./plg_language/noun.py",
    "./plg_language/plumber.py",
    "./plg_language/referent.py",
    "./plg_language/script.py",
    "./plg_language/stage_server.py",
    "./plg_language/variable.py",
    "./plg_language/verb.py",
    "./plg_loop/drummer_plg.py",
    "./plg_midi/midi_converter_plg.py",
    "./plg_midi/midi_input_plg.py",
    "./plg_midi/midi_output_plg.py",
    "./plg_recorder/recorder_plg.py",
    "./plg_rig/rig_plg.py",
    "./plg_sampler2/sampler_oscillator_plg.py",
    "./plg_simple/keygroup_plg.py",
    "./plg_simple/scheduler_plg.py",
    "./plg_simple/talker_plg.py",
    "./plg_stk/blownstring_oscillator_plg.py",
    "./plg_stk/cello_oscillator_plg.py",
    "./plg_stk/clarinet_oscillator_plg.py",
    "./plg_stk/panpipe_oscillator_plg.py",
    "./plg_synth/console_mixer_plg.py",
    "./plg_synth/delay_plg.py",
    "./plg_synth/polyphonic_summer_plg.py",
]

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Replace 'from pi import ...async...' patterns
    # Case 1: async in middle or end: 'from pi import a,b,async,c,d'
    content = re.sub(
        r'(from pi import [^;\n]*?),\s*async\s*,',
        r'\1,',
        content
    )
    content = re.sub(
        r'(from pi import [^;\n]*?),\s*async\s*$',
        r'\1',
        content,
        flags=re.MULTILINE
    )
    
    # Case 2: async at start: 'from pi import async,a,b'
    content = re.sub(
        r'(from pi import )\s*async\s*,',
        r'\1',
        content
    )
    
    # Case 3: Only async: 'from pi import async'
    content = re.sub(
        r'from pi import\s+async\s*$',
        'from pi import piasync',
        content,
        flags=re.MULTILINE
    )
    
    # Add the import if there was any async reference
    if 'async' in original and 'from pi import' in original:
        # Find the first "from pi import" line and add our import after it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.match(r'from pi import ', line) and 'async as piasync' not in line:
                lines.insert(i+1, 'from pi import piasync')
                break
        content = '\n'.join(lines)
    
    # Replace all async. with piasync.
    content = re.sub(r'\basync\.', 'piasync.', content)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed: {filepath}")
        return True
    return False

count = 0
for filepath in files:
    try:
        if fix_file(filepath):
            count += 1
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)

print(f"\nFixed {count} files")
