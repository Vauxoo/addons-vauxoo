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


class stock_location_route(osv.Model):
    _inherit = 'stock.location.route'
    _columns = {
        'consider_on_request': fields.boolean('Route On Request',
                                              help="Checking this you will\
                                              consider this route as an \
                                              'On Request' route, this means\
                                              that every product that has this\
                                              route assigned will show on the\
                                              website the legend 'On Request'\
                                              on the availability field,\
                                              please be careful to set up this\
                                              route."),
    }


class product_product(osv.Model):
    _inherit = 'product.product'
    SELECTION_LIST = [
        ('1', 'Available'),
        ('2', 'Not Available'),
        ('3', 'Low Availability'),
        ('4', 'On Request'),
    ]

    def _get_availability(self, cr, uid, ids, name, args, context=None):
        res = {}
        for product in self.browse(cr, uid, ids):
            for route in product.route_ids:
                if route.consider_on_request:
                    res[product.id] = '4'
                    return res
            if product.qty_available > product.low_stock:
                res[product.id] = '1'
                return res
            elif 0 < product.qty_available <= product.low_stock:
                res[product.id] = '3'
                return res
            elif product.qty_available <= 0:
                res[product.id] = '2'
                return res

    _columns = {
        'low_stock': fields.integer('Low Stock', help="This field is used to show\
    on the website when a product has low availability, any number of stock\
    equals the value set or lower will show 'low avilability' on product "),
        'stock_state': fields.function(_get_availability, type='selection',
                                       method=True, selection=SELECTION_LIST,
                                       string="Website Stock State",
                                       store=True),
    }
    _default = {
        'low_stock': 0,
    }
