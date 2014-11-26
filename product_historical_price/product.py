# -*- encoding: utf-8 -*-
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


class product_historical(osv.Model):

    """
    product_historical
    """

    def _get_historical_price(self, cr, uid, ids, field_name, field_value,
                              arg, context={}):
        res = {}
        product_hist = self.pool.get('product.historic.price')
        for id in ids:
            if self.browse(cr, uid, id).list_price != self.browse(cr, uid,
                                                                  id).\
                    list_price_historical:
                res[id] = self.browse(cr, uid, id).list_price
                product_hist.create(cr, uid, {
                    'product_id': id,
                    'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'price': self.browse(cr, uid, id).list_price,
                }, context)
        return res

    def _get_historical_cost(self, cr, uid, ids, field_name, field_value,
                             arg, context={}):
        res = {}
        product_hist = self.pool.get('product.historic.cost')
        for id in ids:
            if self.browse(cr, uid, id).standard_price != self.browse(cr,
                                                  uid, id).cost_historical:
                res[id] = self.browse(cr, uid, id).standard_price
                product_hist.create(cr, uid, {
                    'product_id': id,
                    'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'price': self.browse(cr, uid, id).standard_price,
                }, context)
        return res

    _inherit = 'product.product'
    _columns = {
        'list_price_historical':
        fields.function(_get_historical_price,
                        method=True, string='Latest Price',
                        type='float',
                        digits_compute=dp.get_precision(
                            'List_Price_Historical'),
                        store={'product.product': (lambda
                                             self, cr, uid, ids, c={}: ids, [
                                                 'list_price'], 50), },
                        help="""Latest Recorded Historical
                                             Value"""),
        'cost_historical': fields.function(_get_historical_cost, method=True,
                                           string=' Latest Cost', type='float',
                                           digits_compute=dp.get_precision(
                                               'Cost_Historical'),
                                           store={'product.product': (lambda
                                               self, cr, uid, ids, c={}: ids, [
                                                   'standard_price'], 50), },
                                           help="""Latest Recorded
                                               Historical Cost"""),
        'list_price_historical_ids': fields.one2many('product.historic.price',
                                                     'product_id',
                                                     'Historical Prices'),
        'cost_historical_ids': fields.one2many('product.historic.cost',
                                               'product_id',
                                               'Historical Prices'),

    }


class product_historic_price(osv.Model):
    _order = "name desc"
    _name = "product.historic.price"
    _description = "Historical Price List"

    _columns = {
        'product_id': fields.many2one('product.product',
                                      string='Product related to this Price',
                                      required=True),
        'name': fields.datetime(string='Date', required=True),
        'price': fields.float(string='Price',
                              digits_compute=dp.get_precision('Price')),
        'product_uom': fields.many2one('product.uom', string="Supplier UoM",
                                       help="""Choose here the Unit of Measure
                                               in which the prices and
                                               quantities are expressed
                                               below.""")

    }
    _defaults = {'name': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
                 }


class product_historic_cost(osv.Model):
    _order = "name desc"
    _name = "product.historic.cost"
    _description = "Historical Price List"

    _columns = {
        'product_id': fields.many2one('product.product',
                                      string='Product related to this Cost',
                                      required=True),
        'name': fields.datetime(string='Date', required=True),
        'price': fields.float(string='Cost',
                              digits_compute=dp.get_precision('Price2')),
        'product_uom': fields.many2one('product.uom', string="Supplier UoM",
                                       help="""Choose here the Unit of Measure
                                               in which the prices and
                                               quantities are expressed
                                               below.""")

    }
    _defaults = {'name': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
                 }
