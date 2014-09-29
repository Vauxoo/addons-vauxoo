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



class product_product(osv.Model):

    _inherit = 'product.product'

    def _search_price_list_item_c(self, cr, uid, ids, field_name, arg,
                                    context={}):
        item_obj = self.pool.get('product.pricelist.item')
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            item_ids = item_obj.search(cr, uid, [(
                'categ_id', '=', product.categ_id.id)], context=context)
            if context.get('query', True):
                sql_str = item_ids and len(ids) == 1\
                and '''UPDATE product_pricelist_item set
                                product_active_id=%d
                                WHERE id %s %s ''' %\
                                (product.id, len(item_ids) > 1 and\
                                'in' or '=', len(item_ids) > 1 and\
                                tuple(item_ids) or item_ids[0])
                sql_str and cr.execute(sql_str)
                item_ids and len(ids) == 1 and cr.commit()
            res[product.id] = item_ids

        return res

    def _search_price_list_item_p(self, cr, uid, ids, field_name, arg,
                                    context={}):

        item_obj = self.pool.get('product.pricelist.item')
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            item_ids = item_obj.search(cr, uid, [(
                'product_id', '=', product.id)], context=context)
            if context.get('query', True):
                sql_str = item_ids and len(ids) == 1 and\
                    '''UPDATE product_pricelist_item set
                                product_active_id=%d
                                WHERE id %s %s ''' %\
                                (product.id, len(item_ids) > 1 and\
                                'in' or '=', len(item_ids) > 1 and\
                                tuple(item_ids) or item_ids[0])
                sql_str and cr.execute(sql_str)
                item_ids and len(ids) == 1 and cr.commit()
            res[product.id] = item_ids
        return res

    def _write_price_list_item_p(obj, cr, uid, id, name, value, fnct_inv_arg,
                                    context={}):
        for val in value:
            if val[0] == 1:
                sql_str = val[2].get('price_discount', False) and\
                        """UPDATE product_pricelist_item set
                            price_discount='%s'
                            WHERE id=%d """ % (val[2].get('price_discount'),
                            val[1])
                val[2].get('price_discount', False) and cr.execute(sql_str)
        return True

    _columns = {
        #'price_list_item_ids':fields.one2many('product.pricelit.item','product_id','Price List Item',help='Percent to compute cost from Price list item'),
        'price_list_item_ids': fields.function(_search_price_list_item_p,
            relation='product.pricelist.item',
            fnct_inv=_write_price_list_item_p, method=True,
            string="Price item by product", type='one2many'),
        'category_item_ids': fields.function(_search_price_list_item_c,
            relation='product.pricelist.item', method=True,
            string="Price item by category", type='one2many'),

    }


class inherit_product_category(osv.Model):
    """ """

    _inherit = 'product.category'

    def _search_price_list_item(self, cr, uid, ids, field_name, arg,
                                    context={}):

        item_obj = self.pool.get('product.pricelist.item')
        res = {}
        for category in self.browse(cr, uid, ids, context=context):
            res[category.id] = item_obj.search(cr, uid, [(
                'categ_id', '=', category.id)], context=context)
        return res

    def _write_price_list_item(obj, cr, uid, id, name, value, fnct_inv_arg,
                                context={}):
        for val in value:
            if val[0] == 1:
                sql_str = val[2].get('price_discount', False) and\
                        """UPDATE product_pricelist_item set
                            price_discount='%s'
                            WHERE id=%d """ % (val[2].get('price_discount'),
                            val[1])
                val[2].get('price_discount', False) and cr.execute(sql_str)
                cr.commit()
        return True

    _columns = {
        'price_list_item_ids': fields.function(_search_price_list_item,
            relation='product.pricelist.item', fnct_inv=_write_price_list_item,
            method=True, string="Price item by category", type='one2many'),

    }
