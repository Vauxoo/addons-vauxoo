# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
###############################################################################
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
###############################################################################

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round


class ProductTemplate(osv.osv):

    _inherit = 'product.template'

    def _product_available(self, cr, uid, ids, name, arg, context=None):
        context = context or {}
        res = super(ProductTemplate, self)._product_available(
            cr, uid, ids, name, arg, context=context)
        product_ids = self.browse(cr, uid, ids, context=context)
        var_ids = []
        for product in product_ids:
            var_ids += [p.id for p in product.product_variant_ids]
        variant_available = self.pool['product.product']._product_available(
            cr, uid, var_ids, context=context)
        for product in product_ids:
            purchase_incoming_qty = 0
            for ppp in product.product_variant_ids:
                purchase_incoming_qty += \
                    variant_available[ppp.id]["purchase_incoming_qty"]
            res.get('product.id').update({
                "purchase_incoming_qty": purchase_incoming_qty})
        return res

    def _search_product_quantity(self, cr, uid, obj, name, domain, context):
        return super(ProductTemplate, self)._search_product_quantity(
            cr, uid, obj, name, domain, context)

    _columns = {
        'purchase_incoming_qty': fields.function(
            _product_available,
            multi='qty_available',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity,
            type='float',
            string='Purchase Incoming',
            help="Quantity of products that are planned to arrive result of"
                 " purchase operations."),
    }


class ProductProduct(osv.osv):

    _inherit = 'product.product'

    def _product_available(self, cr, uid, ids, field_names=None, arg=False,
                           context=None):
        context = context or {}
        res = super(ProductProduct, self)._product_available(
            cr, uid, ids, field_names=field_names, arg=arg, context=context)
        move_obj = self.pool.get('stock.move')
        domain_move_in_pur = []
        domain_products = [('product_id', 'in', ids)]
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = \
            self._get_domain_locations(cr, uid, ids, context=context)
        domain_move_in_pur = (
            self._get_domain_dates(cr, uid, ids, context=context) +
            [('state', 'not in', ('done', 'cancel', 'draft'))] +
            domain_products)
        if (context.get('lot_id') or context.get('owner_id') or
                context.get('package_id')):
            moves_in = []
        else:
            domain_move_in_pur += domain_move_in_loc
            moves_in = move_obj.read_group(
                cr, uid, domain_move_in_pur, ['product_id', 'product_qty'],
                ['product_id'], context=context)
        moves_in = dict(map(
            lambda x: (x['product_id'][0], x['product_qty']), moves_in))
        for product in self.browse(cr, uid, ids, context=context):
            purchase_incoming_qty = float_round(
                moves_in.get(product.id, 0.0),
                precision_rounding=product.uom_id.rounding)
            res[product.id].update({
                'purchase_incoming_qty': purchase_incoming_qty,
            })
        return res

    def _search_product_quantity(self, cr, uid, obj, name, domain, context):
        res = super(ProductProduct, self)._search_product_quantity(
            cr, uid, obj, name, domain, context)
        return res

    _columns = {
        'purchase_incoming_qty': fields.function(
            _product_available,
            multi='qty_available',
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Purchase Incoming',
            fnct_search=_search_product_quantity,
            help="Quantity of products that are planned to arrive.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods arriving to this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods arriving to the Stock Location of this Warehouse, or "
                 "any of its children.\n"
                 "Otherwise, this includes goods arriving to any Stock "
                 "Location with 'internal' type."),
    }
