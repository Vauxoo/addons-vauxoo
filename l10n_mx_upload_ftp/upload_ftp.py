# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: el_rodo_1 (rodo@vauxoo.com)
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
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools, netsvc

from openerp.tools.misc import currency
from openerp import release
from openerp.tools import config

import ftplib
import time
import os
from operator import itemgetter
import tempfile
import base64


class ir_attachment(osv.Model):
    _inherit = 'ir.attachment'

    def binary2file(self, cr, uid, ids, binary_data, file_prefix="", file_suffix=""):
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open(fname, 'wb')
        f.write(base64.decodestring(binary_data))
        f.close()
        os.close(fileno)
        return fname

    def file_ftp(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ftp_id = False
        ftp_obj = pooler.get_pool(cr.dbname).get('ftp.server')
        ftp_id = ftp_obj.search(cr, uid, [('name', '!=', False)], context=None)
        if not ftp_id:
            raise osv.except_osv(('Error Servidor ftp!'), (
                'No Existe Servidor ftp Configurado'))
        ftp = ftp_obj.browse(cr, uid, ftp_id, context)[0]
        ftp_server = ftp.name
        ftp_user = ftp.ftp_user
        ftp_pwd = ftp.ftp_pwd
        ftp_source = ftp.ftp_source
        list_files = []
        for id_file in ids:
            if id_file:
                atta_brw = self.browse(cr, uid, [id_file], context)[0]
                if release.version < '6':
                    file_binary = atta_brw.datas
                else:
                    file_binary = base64.encodestring(atta_brw.db_datas)
                file = self.binary2file(
                    cr, uid, id_file, file_binary, "ftp", "")
                file_name = atta_brw.datas_fname
                list_files.append({'source_file': file, 'name': file_name})
        for a in list_files:
            try:
                s = ftplib.FTP(ftp_server, ftp_user, ftp_pwd)
                f = open((a['source_file']), 'rb')
                s.cwd(ftp_source)
                s.storbinary('STOR ' + (a['name'].replace('/', '_')), f)
                f.close()
                s.quit()
            except:
                raise osv.except_osv(('Error ftp Configuration!'), (
                    'Check ftp Server Information'))
        return True


class ftp_server(osv.Model):
    _name = 'ftp.server'

    _columns = {
        'name': fields.char('ftp server', size=128, required=True),
        'ftp_user': fields.char('ftp user', size=128, required=True),
        'ftp_pwd': fields.char('ftp pwd', size=128, required=True),
        'ftp_source': fields.char('ftp source', size=128, required=True,
            help='Format example "/done"'),
    }
