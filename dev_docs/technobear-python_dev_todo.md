# Overview

a place to keep todo's or things to watch out for the python 3 conversion

# Disclaimer
this document is not intended to be complete, just notes...  
it also not complete, as it list whats outstanding on things Ive already 'done',
it does not included (obvious) next steps e.g. making sure EigenD app runs, or that that entails.

--------------------------
# General roadmap

- make sure things complile
- test individual units from small to large, as much as possible
- start with individual 'command line tools', to verify basic operation of python integration
- move up to more complex tools, as the simple bits work
- then  EigenD app
- start from as few modules (plg_*) as possible, simplest onces
- within this, try to do the 'important ones' first (e.g. eigenharp integration/audio), testing as we go along
- final steps are doing all plg_, again test each
- then final testing = existing setups... (this may be where users can get involved)
- once EigenD is verified, re-check command tools
- workbench - build and test
- stage - build and test
- beta release?
- decide on fate of commander/browser
----------

# For Release notes 
- python version/downloads - users will need to download from python.org
- no more bug_cli/latest version





# Dev TODO/FIX 
(some may or may not be necessary, but lets not forget)

- Windows/Linux 
will need to update tools for linux/windows and test

- python updates to current ignored plgs/apps
I can do this once Ive verified changes to the intial ones are correct.
I dont want to have to re-do the same things on many modules, so need to prove concept first.


- lock updates needed?
I changed lock_c2p for thread locking in tools/pip_cmd/template
this MAY need changing in the cpp equivilants.

pisession/src/pis_python.cpp
lib_juce/epython.cpp
app_juceworkbench/epython.cpp


- testing commandline tools ... 
http://www.eigenlabs.com/wiki/2.0/Command_line_tools_guide/



# Dev - Requires Testing/more work?


- no enumeration on types
tp_cmp is no longer used in PyTypeObject, we may need to replace with tp_as_async


- lock_c2p
changed locking behaviour needs validating


