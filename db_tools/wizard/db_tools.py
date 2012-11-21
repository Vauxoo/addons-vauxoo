# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
#              Julio (julio@vauxoo.com)
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
import sys
import os
import time
import base64
import socket
#~ uri = 'http://localhost:' + '8070'
#~ uri = 'http://localhost:' + '8069'

waittime = 10
wait_count = 0
wait_limit = 12

class db_tools(osv.osv_memory):
    _name = 'db.tools'
    
    def list_db(self, cr, uid, context=None):
        uri=context.get('uri', False)
        conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
        db_list = self.execute(conn,'list')
        list = []
        for db in db_list:
            list.append((db, db))
        return list
             
    _columns = {
        'filter' : fields.selection([ ('backup','Backup'), ('restore','Restore')], 'Filter',),
        'server': fields.char('Server', size=128, readonly=True),
        'password': fields.char('Password', size=64, required=True),
        'list_db' : fields.selection(list_db, 'Data Base'),
    }
    
    _defaults = {
        'server' : 'http://localhost:8070',
        'filter' : 'backup'
        }
        
    def execute(self, connector, method, *args):
        global wait_count
        res = False
        try:
            res = getattr(connector,method)(*args)
        except socket.error,e:
            if e.args[0] == 111:
                if wait_count > 2:
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
        
    def backup_db(self, uri, dbname):
        conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
        filename=('%s_%s.sql' % (dbname, time.strftime('%Y%m%d_%H:%M'),)).replace(':','_')
        dump_db64=self.execute(conn, 'dump', 'admin', dbname)
        dump = base64.decodestring(dump_db64)
        file_db = file('/tmp/' + filename, 'wb')
        file_db.write(dump)
        file_db.close()
        return '/tmp/' + filename
    
    def backup_restore_db(self, cr, uid, ids, uri, dbname):
        conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
        res = self.backup_db(uri, dbname)
        name_db = res[5:-4]
        f = file(res, 'r')
        data_b64 = base64.encodestring(f.read())
        f.close()
        password = self.browse(cr, uid, ids[0]).password
        self.execute(conn, 'restore', password, name_db, data_b64)
        return True
        
    def find_db(self, cr, uid, ids, context=None):
        return True
    
    def confirm_action(self, cr, uid, ids, context=None):
        uri=context.get('uri', False)
        for lin in self.browse(cr, uid, ids, context=context):
            if lin.filter=='backup':
                self.backup_db(context.get('uri', False), lin.list_db)
            if lin.filter == 'restore':
                self.backup_restore_db(cr, uid, ids, context.get('uri', False), lin.list_db)
        return {}
        
    def cancel_action(self, cr, uid, ids, context=None):
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
            res = 'https:'+ os.sep + os.sep + server + ':' + port
        elif val_prot == 'xml_port':
            res = 'http:'+ os.sep + os.sep + server + ':' + port
        return res
        
    def confirm_data(self, cr, uid, ids, context=None):
        res = self.confirm_data2(cr, uid, ids, context=context)
        print 'res', res
        context['uri'] = res
        return {
            'name':"tool db",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'db.tools',
            'type': 'ir.actions.act_window',
            'res_id' :[],
            'nodestroy': False,
            'target': 'new',
            'domain': '[]',
            'context': context,
        }
        
data_server()
