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
from tools.translate import _
import service
import tempfile

waittime = 10
wait_count = 0
wait_limit = 12

class db_tools(osv.osv_memory):
    _name = 'db.tools'
    

    def db(self, cr, uid, context=None):
        ws_obj = service.web_services.db()
        db_list = ws_obj.exp_list()
        list = []
        list2 = []
        for db in db_list:
            list.append((db.lower(),db))
        return list
    
    def _db_default(self, cr, uid, context=None):
        res = self.db(cr, uid, context)
        list = []
        for db in res:
            if ((cr.dbname, cr.dbname) == db):
                list.append(db)
        return list
        
    def db_default(self, cr, uid, context=None):
        return self._db_default(cr, uid, context)[0][0]
        
    _columns = {
        'filter' : fields.selection([ ('backup','Backup'), ('restore','Backup-Restore')], 'Filter',),
        'server': fields.char('Server', size=128, readonly=True),
        'password': fields.char('Password', size=64, required=True),
        'list_db' : fields.selection(_db_default, 'Data Base', required = True, readonly=True),
        'name_db' : fields.char('Name DB', size=128)
    }
    
    _defaults = {
        'server' : 'http://localhost:8069',
        'filter' : 'backup',
        'list_db' : db_default,
        }
                
    def backup_db(self, cr, uid, ids, uri=False, dbname=''):
        ws_obj = service.web_services.db()
        data = self.browse(cr, uid, ids[0])
        filename = data.name_db or ('%s_%s' % (dbname, time.strftime('%Y%m%d_%H:%M'),)).replace(':','_')
        dump_db64 = ws_obj.exp_dump(dbname)
        dump = base64.decodestring(dump_db64)
        (fileno,fname)  = tempfile.mkstemp('.sql', filename)
        os.close(fileno)
        file_db = file(fname, 'wb')
        file_db.write(dump)
        file_db.close()
        return fname
    
    def backup_restore_db(self, cr, uid, ids, uri, dbname=''):
        res = self.backup_db(cr, uid, ids, uri, dbname)
        data = self.browse(cr, uid, ids[0])
        data_base = os.path.basename(res)
        name_db = data_base[:data_base.rfind(".")]
        f = file(res, 'r')
        data_b64 = base64.encodestring(f.read())
        f.close()
        password = data.password
        ws_obj = service.web_services.db()
        ws_obj.exp_restore(name_db, data_b64)
        return True
        
    def find_db(self, cr, uid, ids, context=None):
        return True
    
    def confirm_action(self, cr, uid, ids, context=None):
        uri=context.get('uri', False)
        for lin in self.browse(cr, uid, ids, context=context):
            if lin.filter=='backup':
                self.backup_db(cr, uid, ids, context.get('uri', False), lin.list_db)
            if lin.filter == 'restore':
                self.backup_restore_db(cr, uid, ids, context.get('uri', False), lin.list_db)
        return {}
        
    def cancel_action(self, cr, uid, ids, context=None):
        return {}
db_tools()
