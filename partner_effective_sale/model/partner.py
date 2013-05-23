#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>           
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
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
################################################################################

import time
from osv import fields, osv
from tools.translate import _

class Partner(osv.osv):
    _inherit = 'res.partner'
    
    def _fnct_get_date(self, cr, uid, ids, fieldname, arg, context=None):
        context = context or {}
        res = {}.fromkeys(ids,None)
        so_obj = self.pool.get('sale.order')
        
        for id in ids:
            s_id = so_obj.search(cr, uid,
                    [('partner_id','=',id)],order='date_order asc',limit=1) or []
            res[id] = s_id and \
                    so_obj.browse(cr,uid,s_id[0],context=context).date_order \
                    or None
        return res

    _columns = {
        'sale_order_date':fields.function(
            _fnct_get_date,
            method = True,
            type = 'date',
            string = 'First Sale Order',
            ),
        'sale_order_date':fields.function(
            _fnct_get_date,
            method = True,
            type = 'date',
            string = 'First Sale Order',
            ),
    }
Partner()
