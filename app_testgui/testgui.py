
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

import testgui_native
import piw
import zlib
import sys
from pi import database,agent,logic,node, async,rpc,index,plumber,resource,paths, help_manager,utils
from pisession import session
#from pibelcanto import lexicon
from app_testgui import upgrade

class EigenOpts:
    def __init__(self):
        self.stdout = False
        self.noauto = False
        self.noredirect = False




class Agent(agent.Agent):
    def __init__(self,backend):
        self.__backend = backend
        # self.__database = backend.database()
        agent.Agent.__init__(self,signature=upgrade.Signature(),names="testgui",volatile=True)
        # self.__state = WorkbenchState()
        # self.set_private(self.__state)
        # self.__current_state = ''

    def rpc_addmon(self,arg):
        print 'start monitoring',arg
        # self.__database.start_monitor(arg)

    def rpc_delmon(self,arg):
        print 'stop monitoring',arg
        # self.__database.stop_monitor(arg)

    def start(self):
        piw.tsd_server(self.__backend.agent_name,self)
        self.advertise(self.__backend.index_name)

    def set_state(self,state):
        # self.__current_state = state
        # print 'saving setup'
        # self.__state.set_state(self.__current_state)
        pass

    @async.coroutine('internal error')
    def load_state(self,state,delegate,phase):
        # yield node.server.load_state(self,state,delegate,phase)
        # self.__current_state = self.__state.get_state()
        # self.__backend.state_changed(self.__current_state)
        pass

    def rpc_dump(self,arg):
        # self.__database.dump_connections()
        pass

    def rpc_dumpid(self,arg):
        # self.__database.dump_connections(arg)
        pass


class Backend0(testgui_native.c2p0):
    def __init__(self):
        testgui_native.c2p0.__init__(self)

    def set_args(self,argv):
        args = argv.split()

        self.opts = EigenOpts()

        if '--stdout' in args:
            args.remove('--stdout')
            self.opts.stdout = True

        if '--noauto' in args:
            args.remove('--noauto')
            self.opts.noauto = True

        if '--noredirect' in args:
            args.remove('--noredirect')
            self.opts.stdout = True
            self.opts.noredirect = True

        self.args = args

        self.stdio=(sys.stdout,sys.stderr)

        if not self.opts.noredirect:
            sys.stdout=session.Logger()
            sys.stderr=sys.stdout

    def get_logfile(self):
        return resource.get_logfile('testgui') if not self.opts.stdout else ''

    def mediator(self):
        return self.token()


class Backend(testgui_native.c2p):
    def __init__(self):
        testgui_native.c2p.__init__(self)
        # self.__database = Database()
        self.__agent = Agent(self)
        self.__help_manager=help_manager.HelpManager()

    def initialise(self,frontend,scope):
        self.__frontend = frontend
        self.__scope = piw.tsd_scope()+'.'+scope if scope else piw.tsd_scope()
        self.index_name = '<%s:main>' % self.__scope
        self.agent_name = '<%s:testgui>' % self.__scope
        print >>sys.__stdout__,'testgui scope=',self.__scope,'agent=',self.agent_name,'index=',self.index_name
        # self.__database.addListener(self.__frontend)
        # self.__database.start(self.index_name)
        self.__agent.start()

    def quit(self):
        self.__agent.close_server()
        # self.__database.stop()
        pass



def main0():
    return Backend0()

def main():
    return Backend()
