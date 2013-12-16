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

import time
import base64
import StringIO
import csv
import tempfile
import os
import sys
import ftplib
import time


class wizard_facturae_ftp(osv.TransientModel):
    _name = 'wizard.facturae.ftp'

    def invoice_ftp(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ftp_id = False
        data = self.read(cr, uid, ids)[0]
        atta_obj = self.pool.get('ir.attachment')
        atta_obj.file_ftp(cr, uid, data['files'], context=context)
        return {}

    def _get_files(self, cr, uid, context=None):
        if context is None:
            context = {}
        atta_obj = self.pool.get('ir.attachment')
        atta_ids = atta_obj.search(cr, uid, [('res_id', 'in', context[
            'active_ids']), ('res_model', '=', context['active_model'])],
            context=context)
        return atta_ids

    _columns = {
        'files': fields.many2many('ir.attachment', 'ftp_wizard_attachment_rel',
            'wizard_id', 'attachment_id', 'Attachments',
            help='Attachments to upload on FTP Server'),
    }

    _defaults = {
        'files': _get_files,
    }
