# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import xmlrpclib
HOST='localhost'
PORT=8069
DB='security2'
USER='admin'
PASS='admin'
url ='http://%s:%d/xmlrpc/' % (HOST,PORT)
common_proxy = xmlrpclib.ServerProxy(url+'common')
object_proxy = xmlrpclib.ServerProxy(url+'object')

#######create
#######write
#######read


###Me logueo
uid = common_proxy.login(DB,USER,PASS)
#### Creo
import csv
Partners = csv.DictReader(open('demo_use.csv'))
P={}
A={}
for Partner in Partners:
    
    P = {'name':Partner['name'],
        'is_instructor':Partner['is_instructor'],
        'country':Partner['pais']}
    p = object_proxy.execute(DB,uid,PASS,'res.partner','create',P)
    A = {'street':Partner['calle'],
        'zip':Partner['zip'],'partner_id':p}
    a = object_proxy.execute(DB,uid,PASS,'res.partner.address','create',A)
    print  "se ha creado %s " % object_proxy.execute(DB,uid,PASS,'res.partner','read',[p],['name'])












