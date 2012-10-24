#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
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

from osv import osv, fields, orm
import decimal_precision as dp
from tools.translate import _

class product_product(osv.osv):
    _inherit = "product.product"

    def _product_available_done(self, cr, uid, ids, field_names=None, arg=False, context=None):
        res={}
        from_date = context.get('from_date',False)
        to_date = context.get('to_date',False)
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0.0)
        for f in field_names:
            c = context.copy()
            if f == 'incoming_done_qty':
                c.update({ 'states': ('done',), 'what': ('in',) })
            if f == 'outgoing_done_qty':
                c.update({ 'states': ('done',), 'what': ('out',) })
            if f == 'stock_done_start':
                c.update({ 'states': ('done',), 'what': ('in','out',) ,'from_date': False, 'to_date': from_date })
            if f == 'qty_available2':
                c.update({ 'states': ('done',), 'what': ('in','out',) ,'from_date': False,'to_date': to_date})
            stock = self.get_product_available(cr, uid, ids, context=c)
            for id in ids:
                res[id][f] = stock.get(id, 0.0)
        return res

    _columns = {
        'incoming_done_qty': fields.function(_product_available_done, multi='incoming_done_qty',
            type='float',  digits_compute=dp.get_precision('Product UoM'),
            string='Incoming'),
        'outgoing_done_qty': fields.function(_product_available_done, multi='incoming_done_qty',
            type='float',  digits_compute=dp.get_precision('Product UoM'),
            string='Outgoing'),
        'stock_done_start': fields.function(_product_available_done, multi='incoming_done_qty',
            type='float',  digits_compute=dp.get_precision('Product UoM'),
            string='Stock_Start'),
        'qty_available2': fields.function(_product_available_done, multi='incoming_done_qty',
            type='float',  digits_compute=dp.get_precision('Product UoM'),
            string='Stock_Real2'),
}

product_product()
