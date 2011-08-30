#!/usr/bin/env python
#Copyright (C) 2009-2010 :
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
#    Gregory Starck, g.starck@gmail.com
#    Hartmut Goebel, h.goebel@goebel-consult.de
#
#This file is part of Shinken.
#
#Shinken is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#Shinken is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.
#
#You should have received a copy of the GNU Affero General Public License
#along with Shinken.  If not, see <http://www.gnu.org/licenses/>.


class DataManager(object):
    def __init__(self):
        self.rg = None

    def load(self, rg):
        self.rg = rg

    def get_host(self, hname):
        return self.rg.hosts.find_by_name(hname)

    def get_service(self, hname, sdesc):
        return self.rg.services.find_srv_by_name_and_hostname(hname, sdesc)
    

    def get_hosts(self):
        return self.rg.hosts

    def get_services(self):
        return self.rg.services

    
    def get_important_impacts(self):
        res = []
        for s in self.rg.services:
            if s.is_impact and s.state not in ['OK', 'PENDING']:
                if s.business_impact > 2:
                    res.append(s)
        for h in self.rg.hosts:
            if h.is_impact and h.state not in ['UP', 'PENDING']:
                if h.business_impact > 2:
                    res.append(h)
        return res


    def get_important_elements(self):
        res = []
        # We want REALLY important things, so business_impact > 2, but not just IT elments that are
        # root problems, so we look only for config defined my_own_business_impact value too
        res.extend([s for s in self.rg.services if (s.business_impact > 2 and not 0 <= s.my_own_business_impact <= 2) ])
        res.extend([h for h in self.rg.hosts if (h.business_impact > 2 and not 0 <= h.my_own_business_impact <= 2)] )
        print "DUMP IMPORTANT"
        for i in res:
            print i.get_full_name(), i.business_impact, i.my_own_business_impact
        return res


    # For all business impacting elements, and give the worse state
    # if warning or critical
    def get_overall_state(self):
        h_states = [h.state_id for h in self.rg.hosts if h.business_impact > 2 and h.is_impact and h.state_id in [1, 2]]
        s_states = [s.state_id for s in self.rg.services if  s.business_impact > 2 and s.is_impact and s.state_id in [1, 2]]
        print "get_overall_state:: hosts and services business problems", h_states, s_states
        if len(h_states) == 0:
            h_state = 0
        else:
            h_state = max(h_states)
        if len(s_states) == 0:
            s_state = 0
        else:
            s_state = max(s_states)
        # Ok, now return the max of hosts and services states
        return max(h_state, s_state)

    # Return a tree of {'elt' : Host, 'fathers' : [{}, {}]}
    def get_business_parents(self, obj, levels=2):
        res = {'node' : obj, 'fathers' : []}
        if levels == 0 :
            return res

        for i in obj.parent_dependencies:
            par_elts = self.get_business_parents(i, levels=levels - 1)
            res['fathers'].append(par_elts)

        print "get_business_parents::Give elements", res
        return res


    # Ok, we do not have true root problems, but we can try to guess isn't it?
    #We can just guess for services with the same services of this host in fact
    def guess_root_problems(self, obj):
        if obj.__class__.my_type != 'service':
            return []
        r = [s for s in obj.host.services if s.state_id != 0 and s != obj]
        return r
        

datamgr = DataManager()