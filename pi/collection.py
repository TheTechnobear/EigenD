
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

from pi import atom,logic,piasync

class Collection(atom.Atom):
    def __init__(self,protocols=None,inst_creator=None,inst_wrecker=None,*args,**kwds):
        p = protocols+' create' if protocols else 'create'
        self.__creator = inst_creator or self.instance_create
        self.__wrecker = inst_wrecker or self.instance_wreck
        atom.Atom.__init__(self,protocols=p,*args,**kwds)

    def instance_wreck(self,k,v,o):
        return piasync.success()

    def instance_create(self,o):
        return piasync.failure('not implemented')

    def listinstances(self):
        return [ self[i].get_property_long('ordinal',0) for i in self ]

    def freeinstance(self):
        current = self.listinstances()
        i = 1
        while i in current:
            i = i+1
        return i

    def rpc_listinstances(self,arg):
        i = self.listinstances()
        return logic.render_termlist(i)

    def rpc_instancename(self,arg):
        return self.get_property_string('name');

    @piasync.coroutine('internal error')
    def rpc_createinstance(self,arg):
        name = int(arg)
        outputs = self.listinstances()

        if name in outputs:
            yield piasync.Coroutine.failure('output in use')

        oresult = self.__creator(name)
        yield oresult

        if not oresult.status():
            yield piasync.Coroutine.failure(*oresult.args(),**oresult.kwds())

        output = oresult.args()[0]
        if hasattr(output,'id'):
            yield piasync.Coroutine.success(output.id())
        else:
            yield piasync.Coroutine.failure(str(output))

    @piasync.coroutine('internal error')
    def rpc_delinstance(self,arg):
        for k,v in self.items():
            if v.id() == arg:
                v.notify_destroy()
                o = v.get_property_long('ordinal',0)
                oresult = self.__wrecker(k,v,o)
                yield oresult
                if k in self: del self[k]
                yield piasync.Coroutine.success(arg)

        yield piasync.Coroutine.failure('output not in use')



