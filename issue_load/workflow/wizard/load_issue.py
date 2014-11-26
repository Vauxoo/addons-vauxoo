# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

from openerp.osv import osv, fields

import base64
from migrate import loadProjectsTasks


class load_issue(osv.TransientModel):

    _name = 'load.issue'
    _columns = {
        'issue': fields.binary('File XLS', requered=True, help="Put a xmind file"),
        'db': fields.char('Date Base', 40, help="Name of data base"),
        'port': fields.integer('XML-RPC Port', help="XML-RPC Port of server to load data"),
        'passs': fields.char('Password', 60, help="Password of data base"),
        'user': fields.char('User', 60, help="User of data base"),
        'host': fields.char('Host', 60, help="IP adreess of server"),

    }

    _defaults = {
        'db': 'vauxoo',
        'user': 'admin',
        'host': '70.38.44.102',
    }

    def xls_file(self, cr, uid, ids, context={}):
        wz_brw = self.browse(cr, uid, ids, context=context)[0]
        archivo = open("/tmp/load_issue.xls", "w")
        archivo.write(base64.b64decode(
            wz_brw and wz_brw.issue or 'Archivo Invalido'))
        archivo.close()
        if archivo:
            if wz_brw.db and wz_brw.port and wz_brw.passs and wz_brw.user and wz_brw.host:
                loadProjectsTasks(
                    '/tmp/load_issue.xls', wz_brw.host, wz_brw.port, wz_brw.db, wz_brw.user, wz_brw.passs)
            return True
