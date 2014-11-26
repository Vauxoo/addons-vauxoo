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

import re


class update_price_list(osv.TransientModel):

    _name = 'update.price.list'

    _columns = {
        'those_products': fields.boolean('Products',
            help='Select if wish update price list by specific product'),
        'all': fields.boolean('All Price List',
            help="Select this options only if you wish update all price list"),
        'sure': fields.boolean('Sure?', help="Are sure this operation"),
        'price_list_id': fields.many2one('product.pricelist',
            string='Price List',
            help="Select the price list for price list Report",
            domain=[('type', '=', 'sale')]),
        'product_ids': fields.many2many('product.product', 'product_in',
            'product_out', 'Product', help='Product to update price list'),

    }

    def update_price_list(self, cr, uid, ids, context=None):
        '''
        Method that creates or updates the list price on products, performing a calculation selected
        price if the price sequence already exists this will be updated, so will not be created
        '''

        if context is None:
            context = {}
        qty = 1
        product_obj = self.pool.get('product.product')
        method_obj = self.pool.get('cost.structure')
        price_obj = self.pool.get('product.pricelist')
        wz_brw = self.browse(cr, uid, ids, context=context)[0]
        product_ids = wz_brw.those_products and\
            [i.id for i in wz_brw.product_ids] or product_obj.search(
                cr, uid, [('cost_ult', '>', 0.0), ('virtual_available', '>', 0.0)],
                context=context)
        price_brw = wz_brw and wz_brw.price_list_id and price_obj.browse(
            cr, uid, wz_brw.price_list_id.id, context=context)
        value = 'Precio|precio|price'
        if wz_brw.sure:
            if wz_brw.all:
                price_list_ids = price_obj.search(
                    cr, uid, [], context=context)
                for price in price_list_ids:
                    for product_id in product_ids:
                        dicti = {}
                        price_brw = price_obj.browse(
                            cr, uid, price, context=context)
                        if re.search(value, price_brw.name):
                            product_brw = product_obj.browse(
                                cr, uid, product_id, context=context)
                            property_id = product_brw and\
                                product_brw.property_cost_structure and\
                                product_brw.property_cost_structure.id
                            price_dict = product_brw.virtual_available and\
                                self.pool.get(
                                    'product.pricelist').price_get(cr, uid,
                                [price], product_id, qty, context=context)
                            if price_dict and\
                                    price_dict.get(price, 'False') or False:
                                [dicti.update({
                                    i.sequence: i.id})
                                 for i in product_brw.method_cost_ids]
                                number = price_brw and price_brw.name.split(
                                    ' ')
                                number and len(
                                    number) > 1 and number[1].isdigit(
                                ) and int(
                                        number[1]) in dicti.keys(
                                ) and method_obj.write(
                                            cr, uid, [
                                                property_id], {
                                                    'method_cost_ids':
                                                        [(1, dicti.get(int(number[1])),
                                                    {'reference_cost_structure_id': property_id,
                                                        'unit_price': price_dict.get(price),
                                                     })]}, context=context) or \
                                    number and len(
                                        number) > 1 and number[1].isdigit(
                                ) and product_obj.write(
                                            cr, uid, [
                                                product_id], {
                                                    'method_cost_ids': [(0, 0, {'reference_cost_structure_id': property_id,
                                                                                'unit_price': price_dict.get(price),
                                                                                'sequence': number[1]
                                                                                })]}, context=context)
                                number and len(number) > 1 and number[1].isdigit() and int(number[1]) == 1 and product_obj.write(
                                    cr, uid, [product_id], {'list_price': price_dict.get(price)}, context=context)
                        # ~ --------------------------------------------------------------------#~

            else:
                for product_id in product_ids:
                    dicti = {}
                    product_brw = product_obj.browse(
                        cr, uid, product_id, context=context)
                    property_id = product_brw and product_brw.property_cost_structure and product_brw.property_cost_structure.id
                    price_dict = product_brw.virtual_available and self.pool.get('product.pricelist').price_get(cr, uid, [
                                                                                                                wz_brw and wz_brw.price_list_id and wz_brw.price_list_id.id], product_id, qty, context=context)
                    if price_dict and price_dict.get(wz_brw.price_list_id.id, 'False') or False:
                        [dicti.update({
                                      i.sequence: i.id}) for i in product_brw.method_cost_ids]
                        number = price_brw and price_brw.name.split(' ')
                        number and len(
                            number) > 1 and number[1].isdigit(
                        ) and int(
                                number[1]) in dicti.keys(
                        ) and method_obj.write(
                                    cr, uid, [
                                        property_id], {
                                            'method_cost_ids': [(1, dicti.get(int(number[1])), {'reference_cost_structure_id': property_id,
                                                                                                'unit_price': price_dict.get(wz_brw.price_list_id.id),
                                                                                                })]}, context=context) or \
                            number and len(number) > 1 and number[1].isdigit() and product_obj.write(cr, uid, [product_id], {'method_cost_ids': [(0, 0, {'reference_cost_structure_id': product_brw and
                                                                                                                                                         product_brw.property_cost_structure and
                                                                                                                                                         product_brw.property_cost_structure.id,
                                                                                                                                                         'unit_price': price_dict.get(wz_brw.price_list_id.id),
                                                                                                                                                         'sequence': number[1]
                                                                                                                                                         })]}, context=context)

                        number and len(number) > 1 and number[1].isdigit() and int(number[1]) == 1 and product_obj.write(
                            cr, uid, [product_id], {'list_price': price_dict.get(wz_brw.price_list_id.id)}, context=context)

        return {'type': 'ir.actions.act_window_close'}
