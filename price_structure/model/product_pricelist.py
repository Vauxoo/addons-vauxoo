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


class inherit_price_list_item(osv.Model):

    """ """

    def default_get(self, cr, uid, fields, context=None):
        '''test context '''
        if context is None:
            context = {}

        res = super(inherit_price_list_item, self).default_get(
            cr, uid, fields, context=context)
        res.update({'product_id': context.get('create_item', False)})
        version = context.get('versions', False)
        version and res.update({'price_version_id': version and version[0]
                                and version[0][2]
                                and version[0][2][0]})

        return res

    def _get_price_list(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        res = {}
        for item in self.browse(cr, uid, ids, context=context):
            res[item.id] = item.price_version_id and \
                item.price_version_id.pricelist_id and \
                item.price_version_id.pricelist_id.id

        return res

    def _compute_price(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        res = {}
        pricelist_obj = self.pool.get('product.pricelist')
        if context.get('product', False):
            for item in self.browse(cr, uid, ids, context=context):
                price = pricelist_obj.price_get(cr, uid,
                            [item.price_list_id and item.price_list_id.id],
                    context.get('product'), 1, context=context)

                price = item.price_list_id and price.get(item.price_list_id.id)

                res[item.id] = price
        else:

            for item in self.browse(cr, uid, ids, context=context):
                if item.product_id:
                    price = pricelist_obj.price_get(cr, uid,
                                [item.price_list_id and item.price_list_id.id],
                        item.product_id.id, 1, context=context)

                    price = item.price_list_id and price.get(
                        item.price_list_id.id)

                    res[item.id] = price

                elif item.product_active_id:
                    price = pricelist_obj.price_get(cr, uid,
                                [item.price_list_id and item.price_list_id.id],
                        item.product_active_id and
                        item.product_active_id.id,
                        1, context=context)
                    price = item.price_list_id and price.get(
                        item.price_list_id.id)

                    res[item.id] = price

        return res

    _inherit = 'product.pricelist.item'

    _columns = {
        'price_list_id': fields.function(_get_price_list, method=True,
            type='many2one', relation='product.pricelist',
            string='Price LIst'),
        'compute_price': fields.function(_compute_price, method=True,
            type='float', string='Price'),
        'price_version_id': fields.many2one('product.pricelist.version',
            'Price List Version', required=True, select=True,
            ondelete='cascade'),
        'product_active_id': fields.many2one('product.product', 'product',
            help='Product active to list price'),
        'date_start': fields.related('price_version_id', 'date_start',
            type='date', string='Date Start'),
        'date_end': fields.related('price_version_id', 'date_end',
            type='date', string='Date End'),
    }

    _defaults = {
        'sequence': 1,
        'base': 2,
    }

    def delete_record(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return ids and self.unlink(cr, uid, ids, context=context)
