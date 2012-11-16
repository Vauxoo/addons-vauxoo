# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import osv, fields
import xmlrpclib
import ConfigParser
import optparse
import sys
import thread
import threading
import os
import time
import pickle
import base64
import socket
uri = 'http://localhost:' + '8069'
#~ def list_db(uri):
    #~ conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
    #~ db_list = self.execute(conn,'list')
    #~ list = []
    #~ for db in db_list:
        #~ list.append((db.lower(), db))
    #~ print list,'imprimo list'
    #~ return list

class db_tools(osv.osv_memory):
    _name = 'db.tools'
    
    
    def lista_db(self, cr, uid, ids):
        uri = 'http://localhost:' + '8069'
        res = self.list_db(cr, uid, uri)
        print '7'
        return res
        
    #~ def list_db(self, cr, uid, ids, field_name, args, context=None):
    def list_db(self, cr, uid, context=None):
        res = {}
        #~ form = self.browse(cr, uid, context.get('active_ids', []))
        #~ print self.read(cr, uid, context.get('active_ids', []),['server'])
        #~ for wiz in self.browse(cr, uid, context.get('active_ids', [])):
            #~ print wiz
            #~ print wiz.server
            #~ res[wiz.id]=wiz.server
        uri = 'http://localhost:' + '8069'
        conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
        db_list = self.execute(conn,'list')
        list = []
        for db in db_list:
            list.append((db.lower(), db))
        print list,'imprimo list'
        return list
        

            
    _columns = {
        'filter' : fields.selection([ ('backup','Backup'), ('restore_backup','Restore & Backup')], 'Filter',),
        'server': fields.char('Server', size=128, readonly=True),
        'password': fields.char('Password', size=64, required=True),
        #~ 'path_db': fields.char('Path Data Base', size=256,required=True),
        'name_db': fields.char('Name Data Base', size=128,required=True),
        #~ 'list_db' : fields.function(list_db, method=True, store=False, string='Data Base', selection = [('9','9')], type='selection',),
        'list_db' : fields.selection(list_db, 'Data Base'),
    }
    
    _defaults = {
        'server' : 'socket://localhost:8070',
        'filter' : 'backup'
        }
        
    def execute(self, connector, method, *args):
        global wait_count
        res = False
        try:
            res = getattr(connector,method)(*args)
        except socket.error,e:
            if e.args[0] == 111:
                if wait_count > wait_limit:
                    print "Server is taking too long to start, it has exceeded the maximum limit of %d seconds."%(wait_limit)
                    clean()
                    sys.exit(1)
                print 'Please wait %d sec to start server....'%(waittime)
                wait_count += 1
                time.sleep(waittime)
                res = execute(connector, method, *args)
            else:
                raise e
        wait_count = 0
        return res
        
    #~ def drop_db(self, uri, dbname):
    def drop_db(self, cr, uid, ids, context=None):
        uri = 'http://localhost:' + '8069'
        dbname = 'sys_08_11_12'
        conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
        db_list = self.execute(conn,'list')
        filename=('%s_%s.sql' % (dbname, time.strftime('%Y%m%d_%H:%M'),)).replace(':','_')
        dump_db64 = self.execute(conn, 'dump', 'admin', dbname)
        dump = base64.decodestring(dump_db64)
        f = file(filename, 'wb')
        f.write(dump)
        f.close()
        f = file(filename, 'rb')
        data_b64 = base64.encodestring(f.read())
        f.close()
        self.execute(conn, 'restore', 'admin', 'admin', data_b64)
    #    if dbname in db_list:
    #        print db_list,'imprimo dbname'
        return True
        
    #~ def find_db(self, cr, uid, ids, context=None):
        #~ return True
    
    def confirm_action(self, cr, uid, ids, context=None):
        return {}
        
db_tools()

class data_server(osv.osv_memory):
    _name = 'data.server'
    
    _columns = {
        'server' : fields.char('Server', size=256, required=True),
        'port' : fields.char('Port', size=16, required=True),
        'protocol_conection': fields.selection([ ('net', 'NET-RPC (faster)(port : 8070)'), ('xml_rcp', 'XML-RCP secure'), ('xml_port', 'XML-RCP (port : 8069)')], 'Protocol Conection',),
        }
        
    _defaults = {
        'protocol_conection' : 'net'
        }
        
    def confirm_data2(self, cr, uid, ids, context=None):
        db_tools_obj = self.pool.get('db.tools')
        id_wiz_tools = context.get('active_id')
        data = self.browse(cr, uid, ids[0])
        server = data.server or ''
        port = data.port or ''
        val_prot= data.protocol_conection
        if val_prot == 'net':
            res = 'socket:'+ os.sep + os.sep + server + ':' + port
        elif val_prot == 'xml_rcp':
            res = 'https:'+ os.sep + os.sep + server + ':' + portlocalhost
        elif val_prot == 'xml_port':
            res = 'http:'+ os.sep + os.sep + server + ':' + portlocalhost
        db_tools_obj.write(cr, uid, id_wiz_tools, {'server': res})
        return res
        
    def confirm_data(self, cr, uid, ids, context=None):
        self.confirm_data2(cr, uid, ids, context=context)
        return {}
        
data_server()
