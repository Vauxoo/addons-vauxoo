#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
#
#    Coded by: Jorge Angel Naranjo Rogel (jorge_nr@vauxoo.com)
#
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
#
from openerp.osv import fields, osv
from openerp.tools.translate import _


class stock_move(osv.Model):
    _inherit = "stock.move"

    def onchange_validate_product_exist(self, cr, uid, ids, prod_id=False,
                                        product_qty=False, loc_id=False, context=None):
        """ On change validate product existe in source location
        @param prod_id: Product id to validate
        @param loc_id: Source location id
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        warning = {}
        if not prod_id:
            return warning
        product_obj = self.pool.get('product.product')
        context.update(
            {'location': loc_id, 'what': (str('in'), str('out')), 'states': (str('done'),)})
        product_available = product_obj.get_product_available(
            cr, uid, [prod_id], context=context)
        if product_qty > product_available[prod_id]:
            warning = {'title': 'Caution Products In Location!',
                       'message': "Not enough products in %s according to the quantity ordered. " %
                       (self.pool.get('stock.location').browse(
                        cr, uid, [loc_id])[0].complete_name)
                       }
            return {'warning': warning}
        return True
