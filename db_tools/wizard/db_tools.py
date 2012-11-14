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
import os

class db_tools(osv.osv_memory):
    _name = 'db.tools'
    
    def _list_db(self):
        res=super(rpc_session, self).list_db(self.server)
        return True
    
    def confirm_data(self, cr, uid, ids, field, args, context=None):
        res = {}
        data_server_obj = self.pool.get('data.server')
        data_server = data_server_obj.confirm_data2(cr, uid, ids, context=context)
        for id in ids:
            res[id] = data_server
        return res
    
    _columns = {
        'filter' : fields.selection([ ('backup','Backup'), ('restore','Restore')], 'Filter',),
        'server': fields.function(confirm_data, method=True, store=False, string='Server', type='char'),
        'password': fields.char('Password', size=64, required=True),
        'path_db': fields.char('Path Data Base', size=256,required=True),
        'name_db': fields.char('Name Data Base', size=128,required=True),
        #~ 'list_db' : fields.function(_list_db, method=True, store=False, string='Data Base'),
    }
    
    _defaults = {
        'server' : 'socket://localhost:8070'
        }
        
    def find_db(self):
        return True
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
        data = self.read(cr, uid, ids, [], context=context)[0]
        server = data.get('server', False)
        port = data.get('port', False)
        res = 'socket:'+ os.sep + os.sep + server + ':' + port
        return res
        
    def confirm_data(self, cr, uid, ids, context=None):
        self.confirm_data2(cr, uid, ids, context=context)
        return {}
        
data_server()
