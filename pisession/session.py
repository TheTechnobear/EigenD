
#
# Copyright 2009 Eigenlabs Ltd.  http://www.eigenlabs.com
#
# This file is part of EigenD.
#
# EigenD is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EigenD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EigenD.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import piw
import piagent
import picross
import time
import os
import gc

from pi import utils,resource
from pi import piasync

class Logger:
    def __init__(self):
        self.__buffer = []

    def write(self, msg):
        eol = (msg[-1:] == '\n')
        self.__buffer.append(str(msg).strip())

        if eol:
            piw.tsd_log(' '.join(self.__buffer))
            self.__buffer=[]

    def close(self):
        pass

    def flush(self):
        pass

def run_session(session,user=None,mt=1,name='ctx',logger=None,clock=True,rt=True):
    import threading
    
    def logfunc(msg):
        if logger:
            logger(msg)
        else:
            print

    context = None

    def ctxdun(status):
        context.release()

    scaffold = piagent.scaffold_mt(mt,utils.stringify(logfunc),utils.stringify(None),clock,rt)
    context = scaffold.context('main',utils.statusify(ctxdun),utils.stringify(logfunc),name)
    stdio = (sys.stdout,sys.stderr)
    x = None
    
    # Store the main thread that called tsd_lock for cleanup
    main_thread = threading.current_thread()
    tsd_locked = False

    try:
        if logger:
            sys.stdout = Logger()
            sys.stderr = sys.stdout

        piw.setenv(context.getenv())
        # Only lock TSD on the main thread
        if threading.current_thread() == main_thread:
            piw.tsd_lock()
            tsd_locked = True

        try:
            x = session(scaffold)
            context.trigger()
        finally:
            # Only unlock TSD on the same thread that locked it
            if tsd_locked and threading.current_thread() == main_thread:
                piw.tsd_unlock()
                tsd_locked = False

        scaffold.wait()

    finally:
        # Final cleanup - only if we haven't unlocked yet and we're on the main thread
        if tsd_locked and threading.current_thread() == main_thread:
            try:
                piw.tsd_unlock()
            except:
                pass  # Ignore errors during final cleanup
        sys.stdout,sys.stderr = stdio

    return x
