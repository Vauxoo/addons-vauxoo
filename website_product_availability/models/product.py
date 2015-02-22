# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#    App Author: Vauxoo
#
#    Developed by Oscar Alcala
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields

SELECTION_LIST = [
    ('available', 'Available'),
    ('not_available', 'Not Available'),
    ('low_available', 'Low Availability'),
    ('on_request', 'On Request'),
]


class product_product(osv.Model):
    _inherit = 'product.product'

    def _get_availability(self, cr, uid, ids, name, args, context=None):
        res = {}
        imd = self.pool.get('ir.model.data')
        for product in self.browse(cr, uid, ids):
            xmlid = 'route_warehouse0_mto'
            route_id = imd.get_object(cr, uid, 'stock', xmlid)
            if route_id in product.route_ids:
                res[product.id] = 'on_request'
                return res
            if product.qty_available > product.low_stock:
                res[product.id] = 'available'
                return res
            elif product.qty_available <= product.low_stock:
                res[product.id] = 'low_available'
                return res
            elif product.qty_available <= 0:
                res[product.id] = 'not_available'
                return res

    _columns = {
        'low_stock': fields.integer('Low Stock', help="This field is used to show\
    on the website when a product has low availability, any number of stock\
    equals the value set or lower will show 'low avilability' on product "),
        'stock_state': fields.function(_get_availability, type='selection',
                                       method=True, selection=SELECTION_LIST,
                                       string="Website Stock State"),
    }
    _default = {
        'low_stock': 0,
    }
