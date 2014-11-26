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

from openerp.osv import osv, fields
from openerp.addons.decimal_precision import decimal_precision as dp

from datetime import datetime
from dateutil.relativedelta import relativedelta


class product_product(osv.Model):
    _inherit = "product.product"

    def _product_available_done(self, cr, uid, ids, field_names=None,
            arg=False, context=None):
        res = {}
        from_date = context.get('from_date', False)
        to_date = context.get('to_date', False)
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0.0)
        for f in field_names:
            c = context.copy()
            if f == 'incoming_done_qty':
                c.update({
                    'from_date': from_date and from_date + ' 00:00:00' or False,
                    'to_date': to_date and to_date + ' 23:59:59' or False, })
                c.update({'states': ('done',), 'what': ('in',)})
            if f == 'outgoing_done_qty':
                c.update({
                    'from_date': from_date and from_date + ' 00:00:00' or False,
                    'to_date': to_date and to_date + ' 23:59:59' or False, })
                c.update({'states': ('done',), 'what': ('out',)})
            if f == 'stock_done_start':
                if not from_date:
                    'stock_done_start' == 0.0
                else:
                    new_to_date = datetime.strptime(from_date, '%Y-%m-%d'
                                                    ) - relativedelta(days=1)
                    new_to_date = new_to_date.strftime('%Y-%m-%d') + ' 23:59:59'
                    c.update({'states': ('done',), 'what': ('in', 'out',), 'from_date': False, 'to_date': new_to_date})
            if f == 'stock_balance':
                c.update({'states': ('done',), 'what': ('in', 'out',),
                    'from_date': False, 'to_date': to_date and to_date +
                        ' 23:59:59' or False, })
            stock = self.get_product_available(cr, uid, ids, context=c)
            for id in ids:
                res[id][f] = stock.get(id, 0.0)
        return res

    _columns = {
        'incoming_done_qty': fields.function(_product_available_done,
            multi='incoming_done_qty', type='float',
            digits_compute=dp.get_precision('Product UoM'), string='Incoming'),
        'outgoing_done_qty': fields.function(_product_available_done,
            multi='incoming_done_qty', type='float',
            digits_compute=dp.get_precision('Product UoM'), string='Outgoing'),
        'stock_done_start': fields.function(_product_available_done,
            multi='incoming_done_qty', type='float',
            digits_compute=dp.get_precision('Product UoM'), string='Stock_Start'),
        'stock_balance': fields.function(_product_available_done,
            multi='incoming_done_qty', type='float',
            digits_compute=dp.get_precision('Product UoM'), string='Stock Balance'),
    }
