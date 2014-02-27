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


class sale_order_line(osv.Model):

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                    uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                    lang=False, update_tax=True, date_order=False,
                    packaging=False, fiscal_position=False, flag=False,
                    context=None):
        '''
        Overridden the method of product line sales, to replace the unit price calculation and selection of the cost structure
        that handles the product, and later to filter the prices for the product selected
        '''

        if context is None:
            context = {}
        price_obj = self.pool.get('product.pricelist')
        product_obj = self.pool.get('product.product')
        product_brw = product and product_obj.browse(
            cr, uid, product, context=context)
        res = super(
            sale_order_line, self).product_id_change(cr, uid, ids, pricelist,
                        product, qty=qty,
                        uom=uom, qty_uos=qty_uos,
                        uos=uos, name=name,
                        partner_id=partner_id,
                        lang=lang, update_tax=update_tax,
                        date_order=date_order,
                        packaging=packaging, fiscal_position=fiscal_position,
                        flag=flag, context=context)
        res.get('value', False) and product_brw and\
        product_brw.uom_id and\
        res.get('value', False).update({'product_uom': product_brw.uom_id.id})
        if context.get('price_change', False):
            price = price_obj.price_get(cr, uid, [context.get(
                'price_change', False)], product, qty, context=context)
            res.get('value', {}).update({'price_unit': round(
                price.get(context.get('price_change', False)), 2)})
        res.get('value', False) and\
        product_brw and product_brw.categ_id and\
        res.get('value', False).update({'categ_id': product_brw.categ_id.id})
        res.get('value', False) and 'price_unit' in res.get(
            'value', False) and res['value'].pop('price_unit')
        return res

    def price_unit(self, cr, uid, ids, price_list, product_id, qty,
                    context=None):
        '''
        Calculating the amount of model _compute_price method product.uom
        '''
        if context is None:
            context = {}
        res = {'value': {}}
        if price_list and product_id and qty:
            price_obj = self.pool.get('product.pricelist')
            price = price_obj.price_get(cr, uid, [price_list], product_id, qty,
                                        context=context)
            res['value'].update({'price_unit': round(
                price.get(price_list), 2)})
        return res
    #
    _inherit = 'sale.order.line'
    _columns = {
        'product_id': fields.many2one('product.product', 'Product',
            domain=[('sale_ok', '=', True)], change_default=True),
        'price_list_ids': fields.many2one('product.pricelist', 'Select Price'),
        'cost_structure_id': fields.many2one('cost.structure',
            'Cost Structure'),
        'categ_id': fields.many2one('product.category', 'Category',
            help='Category by product selected'),

    }


class sale_order(osv.Model):

    _inherit = 'sale.order'

    def _price_status(self, cr, uid, ids, field_name, arg, context=None):
        '''
        Check That the products sold are not sold at a price less than or greater than the price rago allocated in the product.
        Failure to comply with this will print a message informing the product that is not complying with this requirement
        '''
        if context is None:
            context = {}
        if not ids:
            return {}
        res = {}
        product = []
        context.update({'query': False})
        pricelist_obj = self.pool.get('product.pricelist')
        for order in len(ids) == 1 and\
        self.browse(cr, uid, ids, context=context) or []:
            for line in order.order_line:
                price_compute = line.product_id and [pricelist_obj.price_get(
                    cr, uid, [i.price_list_id and i.price_list_id.id],
                    line.product_id.id, line.product_uom_qty,
                    context=context).get(i.price_list_id.id)\
                    for i in line.product_id.price_list_item_ids or\
                    line.product_id.category_item_ids]

                property_cost_structure = line and line.product_id and\
                line.product_id.property_cost_structure and\
                line.product_id.property_cost_structure.id or False
                if property_cost_structure and\
                len(price_compute) == len([i for i in price_compute\
                                        if round(line.price_unit, 2) <\
                                        round(i, 2)]):
                    product.append(
                        u'Intenta vender el producto %s a un precio menor al\
                        estimado para su venta' % line.product_id.name)
                    res[order.id] = {'status_bool': True}

                elif property_cost_structure and\
                len(price_compute) == len([i for i in price_compute\
                if round(line.price_unit, 2) > round(i, 2)]):
                    product.append(
                        u'Intenta vender el producto %s a un precio mayor al\
                        estimado para su venta' % line.product_id.name)
                    res[order.id] = {'status_bool': True}

                elif not property_cost_structure:
                    product.append(
                        u'El producto %s no tiene una estructura de costo'\
                        % line.product_id.name)
                    res[order.id] = {'status_bool': True}

            if product:
                res[order.id] = '\n'.join(product)
            else:
                res[order.id] = {'status_bool': False}
                product = []
                res[order.id] = '\n'.join(product)

        return res

    _columns = {

        'status_price': fields.function(_price_status, method=True,
            type="text", store=True, string='Status Price'),
        'status_bool': fields.function(_price_status, method=True,
            type="boolean", string='Status Price'),

    }

    _defaults = {
        'status_bool': False


    }

    def price_unit_confirm(self, cr, uid, ids, context=None):
        '''
        Workflow condition does not allow the sale process if at least one product is being sold in the price range set out in its cost structure
        '''
        if context is None:
            context = {}
        product = []
        context.update({'query': False})
        sale_brw = self.browse(cr, uid, ids and ids[0], context=context)
        pricelist_obj = self.pool.get('product.pricelist')
        for line in len(ids) == 1 and sale_brw.order_line or []:
            property_cost_structure = line and line.product_id and\
            line.product_id.property_cost_structure and\
            line.product_id.property_cost_structure.id or False
            price_compute = line.product_id and [pricelist_obj.price_get(
                cr, uid, [i.price_list_id and i.price_list_id.id],
                line.product_id.id, line.product_uom_qty,
                context=context).get(i.price_list_id.id)\
                for i in line.product_id.price_list_item_ids or\
                line.product_id.category_item_ids]

            if property_cost_structure and\
            len(price_compute) == len([i for i in price_compute\
                                if round(line.price_unit, 2) < round(i, 2)]):
                product.append(
                    u'Intenta vender el producto %s a un precio menor\
                    al estimado para su venta' % line.product_id.name)

            elif property_cost_structure and\
            len(price_compute) == len([i for i in price_compute\
            if round(line.price_unit, 2) > round(i, 2)]):
                product.append(
                    u'Intenta vender el producto %s a un precio mayor\
                    al estimado para su venta' % line.product_id.name)

            elif not property_cost_structure:
                product.append(
                    u'The product %s has not a cost structure' %\
                    line.product_id.name)

        if len(product) > 0:
            raise osv.except_osv(_('Error'), _('\n'.join(product)))

        return True
