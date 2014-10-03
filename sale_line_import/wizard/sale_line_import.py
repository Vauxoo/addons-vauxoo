# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
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

import base64
import cStringIO
import openerp.netsvc as netsvc
from openerp.tools.translate import _

import openerp.tools as tools
import os
from openerp.osv import osv, fields


class wizard_import(osv.TransientModel):
    _name = 'wizard.import'
    _columns = {
        'name': fields.binary('File'),
        'msg': fields.text('Messages', readonly=True),
        'validate': fields.boolean('Validate?')
    }

    def send_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        form = self.read(cr, uid, ids, [])
        order_id = context.get('active_id', False)
        fdata = form and base64.decodestring(form[0]['name']) or False
        fvalidate = form and form[0]['validate'] or False
        msg = self.pool.get('sale.order').import_data_line(
            cr, uid, order_id, fdata, fvalidate, context=context)
        if msg:
            self.write(cr, uid, ids, {'msg': msg})
            return True
        return {}
