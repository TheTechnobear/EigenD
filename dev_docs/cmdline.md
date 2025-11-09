# EigenD Command-Line Tools Reference

## Date: 2025-11-09

## Overview
The `app_cmdline` directory contains command-line utilities for inspecting, manipulating, and debugging EigenD setups and the running system. These tools are essential for understanding setup structure, agent state, and troubleshooting loading issues.

## Setup Database Tools

### bstdump - Dump Complete Setup State
**Command:** `bstdump`  
**Purpose:** Dumps the complete hierarchical state tree of all agents in a setup file.

**Usage:**
```bash
bstdump [--db FILE] [--version VERSION] [--target NAME]
```

**Options:**
- `--db FILE`: Specify setup database file path
- `--version VERSION`: Dump specific version number (default: trunk/latest)
- `--target NAME`: Target setup name (default: 'micro')

**Output Format:**
```
version: <version> (<previous>), <N> agents
<agent>#<path>: <data>
  <agent>#<path>.1: <child1_data>
  <agent>#<path>.2: <child2_data>
    <agent>#<path>.2.1: <grandchild_data>
```

**Example:**
```bash
# Dump current setup
bstdump --db ~/Setups/my_setup

# Dump specific version
bstdump --db ~/Setups/my_setup --version 12345

# Output shows full tree:
version: 12345 (12344), 60 agents
eigend 1#: [root data]
eigend 1#1: [agent name]
eigend 1#2: [protocols]
eigend 1#3: [version]
interpreter 1#: [root data]
...
```

**Use Cases:**
- **Inspect agent properties**: See all property values
- **Find connections**: Look for 'master' properties containing connection terms
- **Verify state structure**: Check if agents loaded correctly
- **Debug loading issues**: Compare before/after state

**For Our Investigation:**
```bash
# Dump failed setup to see what connections exist
bstdump --db ~/Setups/large_setup > dev_docs/logs/dump.txt

# Search for connections:
grep "master" dev_docs/logs/dump.txt

# Find specific agent:
grep "audio unit rig 1 controller" dev_docs/logs/dump.txt
```

---

### bstlist - List Agents and Versions
**Command:** `bstlist`  
**Purpose:** Lists agents in a setup or shows version history.

**Usage:**
```bash
bstlist [--db FILE] [--version VERSION|TAG] [--target NAME] [ADDRESS]
```

**Options:**
- `--db FILE`: Specify setup database file
- `--version VERSION|TAG`: Specific version number or tag name
- `--target NAME`: Target setup name (default: 'micro')
- `ADDRESS`: Optionally show specific agent details (e.g., 'interpreter 1')

**Output Modes:**

**1. List all agents (no ADDRESS):**
```
Snapshot: 12345
Agent                               Type Version Signature
-----                               ---- ------- ---------
eigend 1                            0    12340   [signature]
interpreter 1                       0    12341   [signature]
midi output 1                       0    12342   [signature]
audio unit rig 1                    0    12343   [signature]
...
```

**2. Show agent details (with ADDRESS):**
```
Snapshot: 12345 Agent: interpreter 1 Type: 0 Value: [root data]
   1: [child 1 data]
   2: [child 2 data]
   3: [child 3 data]
```

**3. List version history (--versions):**
```
Version     Timestamp                  Tag
-------     ---------                  ---
12345       Fri Nov  9 10:30:00 2025   My Latest Change
12344       Fri Nov  9 10:20:00 2025   -
12343       Fri Nov  9 10:00:00 2025   Working Version
...
```

**Example:**
```bash
# List all agents in setup
bstlist --db ~/Setups/my_setup

# Show specific agent
bstlist --db ~/Setups/my_setup 'audio unit rig 1'

# Show version history
bstlist --db ~/Setups/my_setup --versions
```

**For Our Investigation:**
```bash
# List agents in load order from database
bstlist --db ~/Setups/large_setup

# Count agents
bstlist --db ~/Setups/large_setup | wc -l

# Find rig agents
bstlist --db ~/Setups/large_setup | grep rig

# Check agent that failed to load
bstlist --db ~/Setups/large_setup 'audio unit rig 1 controller'
```

---

### signature - Generate Setup Signature
**Command:** `signature`  
**Purpose:** Generates a cryptographic signature of a setup for version comparison.

**Usage:**
```bash
signature [--text] db-file
```

**Options:**
- `--text`: Output text version instead of hash

**Output:**
- Binary mode: MD5 hash of setup structure
- Text mode: Human-readable setup signature

**Example:**
```bash
# Get hash signature
signature ~/Setups/my_setup

# Get text signature
signature --text ~/Setups/my_setup
```

**Use Cases:**
- Compare if two setups are identical
- Track setup changes
- Verify setup integrity after loading

---

## Running System Tools

### bls - List Running Agents
**Command:** `bls`  
**Purpose:** Lists all agents currently running in an EigenD instance (requires eigend running).

**Usage:**
```bash
bls <name>
```

**Arguments:**
- `<name>`: Index name to query (typically '<main>')

**Example:**
```bash
# List all running agents
bls '<main>'

# Output:
eigend 1
interpreter 1
midi output 1
audio unit rig 1
...
```

**For Our Investigation:**
```bash
# Check what agents are actually loaded after failed load
bls '<main>'

# Count loaded agents
bls '<main>' | wc -l

# Compare with expected count (should be 60)
```

---

### brpc - Execute RPC on Running Agent
**Command:** `brpc`  
**Purpose:** Send RPC command to a running agent.

**Usage:**
```bash
brpc [--quiet] [--timeout MS] [--verbose] ID RPC_NAME [ARGS...]
```

**Options:**
- `--quiet`: Suppress output
- `--timeout MS`: RPC timeout in milliseconds (default: 300000 = 5 min)
- `--verbose`: Show detailed output

**Arguments:**
- `ID`: Agent ID (e.g., 'eigend 1', 'audio unit rig 1.controller 1')
- `RPC_NAME`: RPC method name (e.g., 'enumerate', 'loadstate', 'postload')
- `ARGS...`: Arguments to RPC (space-separated)

**Example:**
```bash
# Enumerate agent's children
brpc 'eigend 1' enumerate ''

# Get agent property
brpc 'interpreter 1' get_property 'name'

# Call custom RPC
brpc 'audio unit rig 1' get_status ''
```

**For Our Investigation:**
```bash
# Check if agent is reachable
brpc 'audio unit rig 1 controller' enumerate ''

# Try to get connections
brpc 'audio unit rig 1 controller' get_property 'master'

# Check agent state
brpc 'eigend 1' get_all_properties ''
```

---

### bbrowse - Interactive Browser
**Command:** `bbrowse`  
**Purpose:** Interactively browse an agent's hierarchy.

**Usage:**
```bash
bbrowse
# Then enter commands interactively
```

**Commands:**
- `cd <path>`: Change directory in agent tree
- `ls`: List current directory
- `pwd`: Print current path
- `quit`: Exit

**Example:**
```bash
bbrowse
> connect eigend 1
connected to eigend 1
> ls
1: interpreter 1
2: midi output 1
...
> cd 1
> pwd
/1
> ls
```

---

### brsh - Belcanto Shell
**Command:** `brsh`  
**Purpose:** Execute Belcanto (EigenD's musical language) commands.

**Usage:**
```bash
brsh [--music] [--english]
# Then enter Belcanto commands interactively
```

**Options:**
- `--music`: Input in musical notation
- `--english`: Input in English words

**Example:**
```bash
brsh
> metronome playing start
> scale manager hey load vanilla major
```

---

### mirror - Monitor Agent Changes
**Command:** `mirror`  
**Purpose:** Monitors and displays agent additions/removals in real-time.

**Usage:**
```bash
mirror
```

**Output:**
```
added eigend 1
added interpreter 1
added midi output 1
removed midi output 1
```

**For Our Investigation:**
```bash
# Monitor setup loading in real-time
mirror &
# Then load setup in another terminal
# Watch which agents load and in what order
```

---

### capture - Capture Data from Agents
**Command:** `capture`  
**Purpose:** Captures data streams from running agents to files.

**Usage:**
```bash
capture [--name PREFIX] [--absolute] [--wav] tag=id ...
```

**Options:**
- `-n, --name PREFIX`: Output file prefix
- `-a, --absolute`: Use absolute timestamps
- `-r, --wav`: Create .wav audio file

**Arguments:**
- `tag=id`: Map agent ID to output tag

**Example:**
```bash
# Capture audio from audio agent
capture --wav --name recording audio='audio 1'

# Creates: recording-audio.wav
```

---

## Utility Tools

### annotate - Add Annotation to Setup
**Command:** `annotate`  
**Purpose:** Adds text annotation to a setup version.

**Usage:**
```bash
annotate SETUP_NAME ANNOTATION_FILE
```

**Example:**
```bash
echo "Fixed connection issue" > note.txt
annotate my_setup note.txt
```

---

### upgrade_user - Upgrade User Setups
**Command:** `upgrade_user`  
**Purpose:** Upgrades all user setups to current EigenD version.

**Usage:**
```bash
upgrade_user
```

**Note:** Automatically finds and upgrades all setups in user directory.

---

### upgrade34 - Upgrade to Python 3.4+ Format
**Command:** `upgrade34`  
**Purpose:** Upgrades setup files to Python 3.4+ compatible format.

**Usage:**
```bash
upgrade34 SETUP_FILE
```

---

## Debugging the Loading Issue

### Recommended Workflow

**1. Inspect the setup file:**
```bash
# List agents in database order
bstlist --db ~/Setups/large_setup > dev_docs/logs/agents_in_file.txt

# Dump complete state
bstdump --db ~/Setups/large_setup > dev_docs/logs/full_dump.txt

# Find all connections
grep -A5 "master" dev_docs/logs/full_dump.txt > dev_docs/logs/connections.txt
```

**2. Check actual loading order:**
```bash
# Monitor loading in real-time
mirror > dev_docs/logs/loading_order.txt &

# In another terminal, load the setup
# (through Workbench or eigend)

# Compare with file order
diff dev_docs/logs/agents_in_file.txt dev_docs/logs/loading_order.txt
```

**3. Check what actually loaded:**
```bash
# After failed load, list running agents
bls '<main>' > dev_docs/logs/actually_loaded.txt

# Compare with expected
diff dev_docs/logs/agents_in_file.txt dev_docs/logs/actually_loaded.txt
```

**4. Test RPC to agents:**
```bash
# Check if "failed" agent is actually there
brpc 'audio unit rig 1 controller' enumerate ''

# If it exists, check its connections
brpc 'audio unit rig 1 controller' get_property 'master'
```

**5. Find forward-reference connections:**
```bash
# Extract connection info from dump
grep "master" dev_docs/logs/full_dump.txt | \
  grep -oE 'conn\([^)]+\)' > dev_docs/logs/all_connections.txt

# Analyze connection patterns
# Look for agents connecting to later agents
```

**6. Check agent signatures:**
```bash
# Compare signatures before and after
signature ~/Setups/large_setup > dev_docs/logs/sig_before.txt
# Load setup
# Save it
signature ~/Setups/large_setup > dev_docs/logs/sig_after.txt
diff dev_docs/logs/sig_before.txt dev_docs/logs/sig_after.txt
```

**7. Cross-check Python 2 vs 3 decoding:**
```bash
# Dump same setup on Python 2.7
bstdump --db ~/Setups/large_setup > dev_docs/logs/py27_dump.txt

# Dump on Python 3
bstdump --db ~/Setups/large_setup > dev_docs/logs/py3_dump.txt

# Compare to find decoding differences
diff dev_docs/logs/py27_dump.txt dev_docs/logs/py3_dump.txt
```

---

## Connection Term Format

Connections are stored as Prolog terms in the 'master' property:

```
conn(index, flags, target_id, src_path, dst_path)
```

**Example:**
```
conn(0, 1, 'audio 1#1', None, None)
```

**Fields:**
- `index`: Connection index
- `flags`: Connection flags (1 = active)
- `target_id`: Target agent ID and path
- `src_path`: Source path (optional)
- `dst_path`: Destination path (optional)

**Finding in dump:**
```bash
# Find agent's connections
grep -A10 "audio unit rig 1 controller#" full_dump.txt | \
  grep "master" | \
  grep -oE 'conn\([^)]+\)'
```

---

## Python API for Custom Tools

All tools use the following pattern:

```python
from pi import state, utils
from pisession import session

@utils.nothrow
def main(manager):
    # Open database
    db = state.open_database(filename, read_only)
    snap = db.get_trunk()
    
    # Iterate agents
    for i in range(snap.agent_count()):
        agent = snap.get_agent_index(i)
        print(agent.get_address())
        
        # Get agent tree
        root = agent.get_root()
        # Navigate tree
        child = root.get_child(1)
        data = child.get_data()

def cli():
    session.run_session(main, name='mytool')
```

---

## Tool Summary Table

| Tool | Purpose | Requires eigend | Setup File | Output |
|------|---------|-----------------|------------|--------|
| `bstdump` | Dump complete state | No | Yes | Full tree |
| `bstlist` | List agents/versions | No | Yes | Agent list |
| `signature` | Setup signature | No | Yes | Hash/text |
| `bls` | List running agents | Yes | No | Agent names |
| `brpc` | Execute RPC | Yes | No | RPC result |
| `bbrowse` | Browse agent | Yes | No | Interactive |
| `brsh` | Belcanto shell | Yes | No | Interactive |
| `mirror` | Monitor changes | Yes | No | Events |
| `capture` | Capture data | Yes | No | Files |
| `annotate` | Add annotation | No | Yes | None |

---

## Next Steps for Investigation

1. **Extract connection graph:**
   ```bash
   # Get all connections with agent order
   python3 << 'EOF'
   from pi import state
   db = state.open_database('~/Setups/large_setup', False)
   snap = db.get_trunk()
   
   for i in range(snap.agent_count()):
       agent = snap.get_agent_index(i)
       addr = agent.get_address()
       print(f"{i}: {addr}")
       # Extract connections from root tree
   EOF
   ```

2. **Compare Python 2.7 vs 3 state:**
   ```bash
   # On Python 2.7
   bstdump --db setup > py27_state.txt
   
   # On Python 3
   bstdump --db setup > py3_state.txt
   
   diff py27_state.txt py3_state.txt
   ```

3. **Monitor loading with debugging:**
   ```bash
   # Add print statements to workspace.py
   # Watch which agent causes RPC exception
   mirror | tee loading_debug.txt
   ```

4. **Test connection order hypothesis:**
   - Use `bstdump` to find all connections
   - Map connections to agent load order
   - Identify forward references (agent N → agent M where M > N)
