/*
 Copyright 2012-2014 Eigenlabs Ltd.  http://www.eigenlabs.com

 This file is part of EigenD.

 EigenD is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 EigenD is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with EigenD.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef __TESTGUI__
#define __TESTGUI__

#include <set>
#include <piw/piw_data.h>
#include <string>

namespace testgui
{
    struct p2c_t
    {
        virtual ~p2c_t() { }
    };

    struct c2p0_t
    {
        c2p0_t() { }
        virtual ~c2p0_t() { }
        virtual void set_args(const char *) = 0;
        virtual std::string get_logfile() = 0;
    };

    struct c2p_t
    {
        c2p_t() { }
        virtual ~c2p_t() { }
        virtual void initialise(p2c_t *p2c, const std::string &scope) = 0;
        virtual void quit() = 0;
     };

}
#endif
