# Quick Reference - Continue Python 3.14 Migration

## On New Computer

### 1. Clone and Setup (5 min)
```bash
git clone https://github.com/TheTechnobear/EigenD.git
cd EigenD
git checkout copilot
git pull origin copilot

# Verify latest commit
git log --oneline -1
# Should show: c9864604 Update documentation for Python 3.14 migration progress
```

### 2. Install Python 3.14 (if needed)
```bash
# macOS
brew install python@3.14

# Verify
which python3.14
# Should be: /opt/homebrew/opt/python@3.14/bin/python3.14
```

### 3. Build (10 min)
```bash
make clean
make -j8
```

### 4. Test Basic Tools (2 min)
```bash
./tmp/bin/brelease          # Should show: 2.2.1-community
./tmp/bin/bls               # Should show: can't connect (expected)
./tmp/bin/brexec --help     # Should show usage
```

## Next Tasks

### Immediate (30 min)
1. **Fix cheatsheet** - app_cmdline/cheat.py line 27
2. **Test daemon** - `./tmp/bin/eigend --cmdline`
3. **Fix any new errors** - same pattern as before

### Pattern for Fixing Errors
```python
# Import errors in pi/ modules
import const, utils  →  from pi import const, utils

# Import errors in pi/logic/ modules  
import terms  →  from pi.logic import terms

# Python 2 API removals
cmp(a,b)  →  (a > b) - (a < b)
long      →  int
xrange    →  range

# After fixing
rm -f tmp/modules/path/to/file.pyc && make -j8
```

## Documentation Files

Read these in order:
1. **copilot-session_resume.md** - Complete context (this session)
2. **copilot-python_dev_notes.md** - All changes made
3. **copilot-python_dev_todo.md** - Task tracking
4. **copilot-python_dev_howitworks.md** - Quick system reference

## Current Status

✅ **BUILD COMPLETE** - Python 3.14  
✅ **CLI TOOLS WORKING** - bcat, bls, brexec, etc.  
⚠️ **DAEMON UNTESTED** - Next step  
⚠️ **PLUGINS UNTESTED** - After daemon works  

## Commits Pushed to GitHub

- **c9864604** - Documentation updates (this commit)
- **d431988d** - pi/logic/ fixes, CLI tools working
- **98f03aa8** - Template fixes, pi/ imports
- **55a8e099** - Initial Python 3 syntax fixes
- **b5f3e975** - Base migration with syntax changes

All changes pushed to: https://github.com/TheTechnobear/EigenD/tree/copilot

---
**Ready to continue!** 🚀
