#! /usr/bin/env python
#
# SCons - a Software Constructor
#
# EigenD SCons 4.5.0 launcher
# Updated 2025-11-10 for Python 3.14 compatibility
#

import os
import os.path
import sys

# Add SCons4 package to path
here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(here, 'packages', 'SCons4'))

import SCons.Script
SCons.Script.main()
