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

import pooler
import wizard
import base64
import cStringIO
import netsvc
from tools.translate import _
import tools
import os
from osv import osv, fields


class wizard_import(osv.osv_memory):
    _name='wizard.import'
    _columns={
        'name' : fields.binary('File'),
        'msg' : fields.text('Messages',readonly=True)
    }
    
    def send_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        form = self.read(cr,uid,ids,[])
        order_id=context.get('active_id',False)
        fdata = form and base64.decodestring( form[0]['name'] ) or False
        msg = self.pool.get('sale.order').import_data_line(cr, uid, order_id, fdata, context=context) 
        if msg:
            self.write(cr,uid,ids,{'msg':msg})
            return True
        return {}

wizard_import()
