# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################
from openerp.osv import fields, osv

from openerp.addons.decimal_precision import decimal_precision as dp
import time


class ProductHistorical(osv.Model):

    """product_historical
    """

    def _get_historical_price(self, cr, uid, ids, field_name, field_value,
                              arg, context=None):
        context = context or {}
        res = {}
        product_hist = self.pool.get('product.historic.price')
        for brw in self.browse(cr, uid, ids, context=context):
            res[brw.id] = brw.list_price_historical
            if brw.list_price != brw.list_price_historical:
                res[brw.id] = brw.list_price
                values = {
                    'product_id': brw.id,
                    'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'price': brw.list_price,
                }
                product_hist.create(cr, uid, values, context=context)
        return res

    _inherit = 'product.template'
    _columns = {
        'list_price_historical': fields.function(
            _get_historical_price,
            method=True, string='Latest Price',
            type='float',
            digits_compute=dp.get_precision('List_Price_Historical'),
            store={
                _inherit: (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['list_price'], 50),
            },
            help="Latest Recorded Historical Value"),
        'list_price_historical_ids': fields.one2many(
            'product.historic.price',
            'product_id',
            'Historical Prices',
            help='Historical changes '
            'of the sale price of '
            'this product'),
        'cost_historical_ids': fields.one2many(
            'product.price.history',
            'product_template_id',
            'Historical Cost',
            help='Historical changes '
            'in the cost of this product')
    }


class ProductHistoricPrice(osv.Model):
    _order = "name desc"
    _name = "product.historic.price"
    _description = "Historical Price List"

    _columns = {
        'product_id': fields.many2one(
            'product.template',
            string='Product related to this Price',
            required=True),
        'name': fields.datetime(string='Date', required=True),
        'price': fields.float(
            string='Price', digits_compute=dp.get_precision('Price')),
        'product_uom': fields.many2one(
            'product.uom', string="Supplier UoM",
            help="""Choose here the Unit of Measure in which the prices and
                    quantities are expressed below."""),
    }

    _defaults = {
        'name': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
