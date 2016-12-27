
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

class Index(piw.index):
    def __init__(self):
        piw.index.__init__(self)

    def index_opened(self):
        print 'Index: index_opened'

    @utils.nothrow
    def index_changed(self):
        print 'Index: index_changed', self.member_count()
        if self.__listener:
            self.__listener.check_progress()

    def index_closed(self):
        print 'Index: index_closed'

    def addListener(self, listener):
        self.__listener=listener


class Database(database.SimpleDatabase):

    def __init__(self):
        database.SimpleDatabase.__init__(self)
        self.__props = self.get_propcache('props')
        self.__addedList=[]
        self.__changedDict={}
        self.__agentCount=0
        self.__mainIndex=Index()
        self.__mainIndex.addListener(self)
        self.__listener=None

    def start(self,index_name):
        database.SimpleDatabase.start(self,index_name)
        self.set_monitor_listener(self.value_changed)
        piw.tsd_index(index_name,self.__mainIndex)

    def stop(self):
        self.clear_monitor_listener()
        database.SimpleDatabase.stop(self)
        self.__mainIndex.close_index()

    def value_changed(self,pid,value):
        print 'id',pid,'value changed to',value
        self.__listener.value_changed(pid)

    def object_added(self,proxy):
        database.SimpleDatabase.object_added(self,proxy)
        id=proxy.database_id()
        if 'notagent' in proxy.protocols():
            print id,'is not agent'
        #print "object_added",id,'(',proxy.id(),')'
        s=id.split('#')
        name_part=s[0]
        if not(name_part=="<workbench>" and len(s)>1):
            if not name_part in self.__addedList:
                self.__addedList.append(name_part)

        if not '#' in id:
            self.__agentCount=self.__agentCount+1
            print 'agentCount=',self.__agentCount, id, 'added'
            self.update_progress()

    def update_progress(self):
        target=self.__mainIndex.member_count()
        delta=abs(self.__agentCount-target)
        p=float(target-delta)/float(target)
        #print 'agentCount=',self.__agentCount,self.__mainIndex.member_count(),p
        if self.__listener:
            self.__listener.loaded(p)

    def stop_progress(self):
        if self.__listener:
            self.__listener.loaded(0.999)

    def check_progress(self):
        print 'check_progress', self.__agentCount, self.__mainIndex.member_count()
        if(self.__agentCount==self.__mainIndex.member_count()):
            if self.__listener:
                self.__listener.loaded(0.999)

    def object_removed(self,proxy):
        database.SimpleDatabase.object_removed(self,proxy)
        id=proxy.database_id()

        if self.__listener:
            if not '#' in id:
                print "Top level object removed", id
                self.__listener.agentRemoved(id)
                self.__agentCount=self.__agentCount-1;
                print 'agentCount=',self.__agentCount, id, 'removed'
                self.update_progress()

            else:

                 i=id.rfind('.')
                 if i>-1:
                    pid=id[:i]
                    p=self.find_item(pid)
                    if p:
                        if "create" in p.protocols():
                            self.__listener.instanceRemoved(p.database_id())
#                        else:
#                            self.__listener.portRemoved(p.database_id())
                            

    def object_changed(self,proxy,parts):
        id=proxy.database_id()
        database.SimpleDatabase.object_changed(self,proxy,parts)
        #print "object_changed",id,parts
        name_part=id.split('#')[0]

        if not name_part in self.__changedDict:
            self.__changedDict[name_part]=parts
        else:
            for p in parts:
                self.__changedDict[name_part].add(p)

        if ('name' in parts) or ('ordinal' in parts):
            if self.__listener:
                self.__listener.nameChanged(id)



    def subsys_sync(self,proxy):
        id =proxy.database_id()
        print "subsys_sync",id
        changed_parts=None
        added=False
        if id in self.__changedDict:
            changed_parts=self.__changedDict[id]
            print 'database:subsystem sync',id,'changed parts=',changed_parts

        if id in self.__addedList:
            added=True
            print 'database:subsystem sync',id,'added'

        if added:
            if self.__listener:
                if self.isTopLevel(id):
                    self.__listener.agentAdded(id)
                self.__addedList.remove(id)

        if changed_parts:
            if self.__listener:
                if ('master' in changed_parts) or ('frelation' in changed_parts) or ('relation' in changed_parts):
                    self.__listener.agentChanged(id)
                
                del self.__changedDict[id]

    def addListener(self, listener):
        self.__listener=listener

    def isTopLevel(self,id):
        return 'agent' in self.__props.get_valueset(id)




class Agent(agent.Agent):
    def __init__(self,backend):
        print 'testgui : agent create'
        self.__backend = backend
        self.__database = backend.database()
        agent.Agent.__init__(self,signature=upgrade.Signature(),names="testgui",volatile=True)
        # self.__state = WorkbenchState()
        # self.set_private(self.__state)
        # self.__current_state = ''

    def rpc_addmon(self,arg):
        print 'start monitoring',arg
        self.__database.start_monitor(arg)

    def rpc_delmon(self,arg):
        print 'stop monitoring',arg
        self.__database.stop_monitor(arg)

    def start(self):
        print 'testgui : agent start'
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
        self.__database.dump_connections()
        pass

    def rpc_dumpid(self,arg):
        self.__database.dump_connections(arg)
        pass


class Backend0(testgui_native.c2p0):
    def __init__(self):
        print 'testgui : Backend0 init'
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
        print 'testgui : Backend init'
        testgui_native.c2p.__init__(self)
        self.__database = Database()
        self.__agent = Agent(self)
        self.__help_manager=help_manager.HelpManager()

    def initialise(self,frontend,scope):
        print 'testgui : Backend initialise'
        self.__frontend = frontend
        self.__scope = piw.tsd_scope()+'.'+scope if scope else piw.tsd_scope()
        self.index_name = '<%s:main>' % self.__scope
        self.agent_name = '<%s:testgui>' % self.__scope
        print >>sys.__stdout__,'testgui scope=',self.__scope,'agent=',self.agent_name,'index=',self.index_name
        # self.__database.addListener(self.__frontend)
        self.__database.start(self.index_name)
        self.__agent.start()

    def quit(self):
        self.__agent.close_server()
        self.__database.stop()
        pass

    def mediator(self):
        return self.token()

    def database(self):
        return self.__database

    @async.coroutine('internal error')
    def get_agents(self):
        print 'Backend - get_agents'    
        names=set([])
        r=rpc.invoke_rpc(self.__database.to_usable_id('<eigend1>'),'listmodules','')
        yield r
        if not r.status():
            yield async.Coroutine.failure('get_agents failed') 
        result=r.args()[0]
        # if result!='None':

        print "get_agents: result=",result
            # terms=logic.parse_termlist(result)
            # for t in terms:
            #     r=t.args[0]
            #     r=r+","
            #     ords=t.args[2]
            #     for o in ords:
            #         r=r+str(o)
            #         r=r+','
            #     names.add(r)
            # self.__frontend.agents_updated(names)
        yield async.Coroutine.success(names) 


def main0():
    return Backend0()

def main():
    return Backend()
