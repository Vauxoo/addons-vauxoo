#!/usr/bin/python
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
##########################################################################

from openerp.osv import osv, fields
import openerp.tools as tools
from openerp.tools.translate import _

from tools import config
import openerp.netsvc as netsvc
import decimal_precision as dp
from openerp.tools.sql import drop_view_if_exists



class product_product(osv.Model):

    _inherit = 'product.product'

    def _structure_cost_status(self, cr, uid, ids, field_name, arg,
                                context=None):
        '''
        Variable indicating if the product already has a cost structure
        '''
        if context is None:
            context = {}
        res = {}
        if not ids:
            return res
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = False
            if product.property_cost_structure:
                res[product.id] = True

        return res

    def _check_default_cost(self, cr, uid, ids, context=None):
        '''
        Ochange to verified one price default by product
        '''
        if context is None:
            context = {}
        i = 0
        for product in self.browse(cr, uid, ids, context=context):
            for price in product.method_cost_ids:
                print 'pricedefault', price.default_cost
                if price.default_cost:
                    i += 1
                if i > 1:
                    return False
        return True

    _columns = {
        'property_cost_structure': fields.property(
            'cost.structure',
            type='many2one',
            relation='cost.structure',
            string="Cost and Price Structure",
            method=True,
            view_load=True,
            help="For the current product, this cost and price strucuture will\
                define how the behavior of the price and cost computation "),
        'cost_ult': fields.related('property_cost_structure', 'cost_ult',
            type='float', digits_compute=dp.get_precision('Cost Structure'),
            string='Last Cost',
            help="Last cost at which the product was obtained "),
        'qty_ult': fields.related('property_cost_structure', 'qty_ult',
            type='float', digits_compute=dp.get_precision('Cost Structure'),
            string='Last Amount',
            help='Last amount recorded at the time of calculation\
                of average cost'),
        'cost_prom': fields.related('property_cost_structure',
            'cost_prom', type='float',
            digits_compute=dp.get_precision('Cost Structure'),
            string='Average Cost',
            help='Average cost automatically calculated to validate a document\
                that alters the same'),
        'cost_suppler': fields.related('property_cost_structure',
            'cost_suppler',
            type='float', digits_compute=dp.get_precision('Cost Structure'),
            string='Supplier Cost', help='Average cost to supplier product'),
        'cost_ant': fields.related('property_cost_structure', 'cost_ant',
            type='float', digits_compute=dp.get_precision('Cost Structure'),
            string='Ant Cost',
            help='Penultimate recorded cost for this\
                product, used as history'),
        'qty_ant': fields.related('property_cost_structure', 'qty_ant',
            type='float', digits_compute=dp.get_precision('Cost Structure'),
            string='Ant Qty',
            help='Number of product when the penultimate been calculated cost\
                recorded for this product, used as history'),
        'ult_om': fields.related('property_cost_structure', 'ult_om',
            relation='product.uom', type='many2one', string='Ult UOM',
            help='Product Unit of measure when making the calculation\
                of average cost '),
        'prom_om': fields.related('property_cost_structure', 'prom_om',
            relation='product.uom', type='many2one', string='UOM Prom'),
        'ant_om': fields.related('property_cost_structure', 'ant_om',
            relation='product.uom', type='many2one', string='UOM Ant',
            help='Product unit of measure when the penultimate been\
                calculated cost recorded for this product, used as history'),
        'cost_to_price': fields.related('property_cost_structure',
            'cost_to_price', type='selection', string='Average Cost'),
        'date_cost_ult': fields.related('property_cost_structure',
            'date_cost_ult', type='datetime', string='Date',
            help='Date on which the average cost was calculated'),
        'date_ult_om': fields.related('property_cost_structure', 'date_ult_om',
            type='datetime', string='Date',
            help='Date on which the average cost was calculated'),
        'date_cost_prom': fields.related('property_cost_structure',
            'date_cost_prom', type='datetime', string='Date',
            help='Date on which the average cost was calculated'),
        'date_prom_om': fields.related('property_cost_structure',
            'date_prom_om', type='datetime', string='Date',
            help='Date on which the average cost was calculated'),
        'date_cost_suppler': fields.related('property_cost_structure',
            'date_cost_suppler', type='datetime', string='Date',
            help='Date on which the average cost was calculated'),
        'date_ant_om': fields.related('property_cost_structure',
            'date_ant_om', type='datetime', string='Date',
            help='Date on which the penultimate average cost was calculated'),
        'date_cost_ant': fields.related('property_cost_structure',
            'date_cost_ant', type='datetime', string='Date',
            help='Date on which the penultimate average cost was calculated'),
        'date_cost_to_price': fields.related('property_cost_structure',
            'date_cost_to_price', type='datetime', string='Date',
            help='Date on which the penultimate average cost was calculated'),
        'method_cost_ids': fields.related('property_cost_structure',
            'method_cost_ids', relation='method.price', type='one2many',
            string='Method Cost',),
        'status_bool': fields.function(_structure_cost_status, method=True,
            type="boolean", store=True, string='Status Price'),
    }

    _constraints = [(
        _check_default_cost, 'ERROR, The product can only a default price',
            ['default_cost'])]

    def write(self, cr, uid, ids, vals, context=None):
        '''
        Overwritten the write method to manipulate the cost structure independently and make decisions when registering or modifying a cost structure
        '''
        product_brw = self.browse(cr, uid, ids and ids[0], context=context)
        if product_brw.property_cost_structure and\
            'property_cost_structure' in vals:
            raise osv.except_osv(_('Error'), _(
                'The product already has a cost structure'))

        method_obj = self.pool.get('method.price')
        method_id = []
        if vals.get('property_cost_structure', False):
            if vals.get('method_cost_ids', False):
                for i in vals.get('method_cost_ids'):
                    if i[2] and i[2].get('cost_structure_id', False):
                        pass
                    else:
                        i[2] and i[2].update({'cost_structure_id': vals.get(
                            'property_cost_structure', False) or []})
                        print "i[2]", i[2]
                        method_id = i[2] and method_obj.create(
                            cr, uid, i[2], context=context)

                method_id and 'method_cost_ids' in vals and vals.pop(
                    'method_cost_ids')
            else:
                'method_cost_ids' in vals and not vals[
                    'method_cost_ids'] and vals.pop('method_cost_ids')

        else:
            if vals.get('method_cost_ids', False):
                for i in vals.get('method_cost_ids'):
                    if i[2] and i[2].get('cost_structure_id', False):
                        pass
                    else:
                        i[2] and i[2].update({
                                'cost_structure_id': product_brw and
                                    product_brw.property_cost_structure and
                                    product_brw.property_cost_structure.id or
                                    []})
                        method_id = i[2] and method_obj.create(
                            cr, uid, i[2], context=context)

                method_id and 'method_cost_ids' in vals and vals.pop(
                    'method_cost_ids')

            else:
                'method_cost_ids' in vals and not vals[
                    'method_cost_ids'] and vals.pop('method_cost_ids')
        return super(product_product, self).write(cr, uid, ids, vals,
                                                    context=context)

    def price_get(self, cr, uid, ids, ptype='list_price', context=None):
        '''
        Price_get overridden the method, the estimated cost to make the model for taking the money
        if the selected price list takes the cost of the product for its calculation
        '''

        if context is None:
            context = {}

        if 'currency_id' in context:
            pricetype_obj = self.pool.get('product.price.type')
            price_type_id = pricetype_obj.search(
                cr, uid, [('field', '=', ptype)])[0]
            price_type_currency_id = pricetype_obj.browse(
                cr, uid, price_type_id).currency_id.id
        res = {}
        product_uom_obj = self.pool.get('product.uom')
        for product in self.browse(cr, uid, ids, context=context):
            ptype = ptype == 'list_price' and 'list_price' or 'cost_ult'
            res[product.id] = product[ptype] or 0.0
            if ptype == 'list_price':
                res[product.id] = (res[product.id] *\
                    (product.price_margin or 1.0)) + \
                    product.price_extra
            if 'uom' in context:
                uom = product.uos_id or product.uom_id
                res[product.id] = product_uom_obj._compute_price(cr, uid,
                                    uom.id, res[product.id], context['uom'])
            # Convert from price_type currency to asked one
            if 'currency_id' in context:
                # Take the price_type currency from the product field
                # This is right cause a field cannot be in more than one
                # currency
                res[product.id] = self.pool.get(
                    'res.currency').compute(cr, uid, price_type_currency_id,
                                            context['currency_id'],
                                            res[product.id], context=context)

        return res




class report_cost(osv.Model):
    _name = "report.cost"
    _auto = False
    _order = "date desc"
    _columns = {
        'date': fields.date('Date Invoice', readonly=True),
        'product_id': fields.many2one('product.product', 'Product',
                readonly=True, select=True),
        'quantity': fields.float('# of Products', readonly=True),
        'price_unit': fields.float('Unit Price', readonly=True),
        'last_cost': fields.float('Last Cost', readonly=True),
        'price_subtotal': fields.float('Subtotal Price', readonly=True),
        'uom_id': fields.many2one('product.uom', ' UoM', readonly=True),
        'type_inv': fields.selection([
            ('out_invoice', 'Customer Invoice'),
            ('in_invoice', 'Supplier Invoice'),
            ('out_refund', 'Customer Refund'),
            ('in_refund', 'Supplier Refund'),
        ], 'Type', readonly=True, select=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice',
                readonly=True, select=True),
        'line_id': fields.many2one('account.invoice.line', 'Linea',
                readonly=True, select=True),
    }

    _rec_name = 'date'

    def init(self, cr):
        drop_view_if_exists(cr, 'report_cost')
        cr.execute('''
            create or replace view report_cost as (
            select
                invo.date_invoice as date,
                line.id as id,
                line.product_id as product_id,
                invo.type as type_inv,
                case when invo.type='out_refund'
                    then
                        0.0
                    else
                        case when invo.type='in_invoice'
                            then
                                line.price_unit
                            else
                                case when invo.type='in_refund'
                                    then
                                        line.price_unit*(-1)
                                    else
                                        0.0
                                end
                        end
                end as last_cost,
                line.uos_id as uom_id,
                case when invo.type='out_refund'
                    then
                        line.price_unit*(-1)
                    else
                        case when invo.type='in_invoice'
                            then
                                0.0
                            else
                                line.price_unit
                        end
                end as price_unit
            from account_invoice invo
                inner join account_invoice_line line on (invo.id=line.invoice_id)
            where invo.state in ('open','paid')
        )''')

