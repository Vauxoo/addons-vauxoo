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

from openerp.osv import fields, osv


class virtual_items(osv.TransientModel):

    '''Create items by product'''

    _name = 'virtual.items'

    _columns = {
        'price_create_id': fields.many2one('create.price.list', 'List'),
        'items_id': fields.many2one('product.pricelist.item', 'List items',
            help='items by roduct'),

    }


class create_price_list(osv.TransientModel):

    '''Create price list to new product'''

    def default_get(self, cr, uid, fields, context=None):
        '''Add product'''
        if context is None:
            context = {}
        res = super(create_price_list, self).default_get(
            cr, uid, fields, context=context)
        res.update({'product_id': context.get('active_id', False)})

        return res

    _name = 'create.price.list'

    _columns = {
        'version_ids': fields.many2many('product.pricelist.version',
            'version_to_item_create', 'wz_id', 'version_id', 'Versions',
            help='Version from price_list'),
        'pricelist_id': fields.many2one('product.pricelist', 'Price List',
            help='Price list to create version'),

        'pricelist_ids': fields.one2many('virtual.items', 'price_create_id',
            'Items', help='Create items for this product'),

        'product_id': fields.many2one('product.product', 'Product',
            help='Product'),


    }

    def onchage_versions(self, cr, uid, ids, pricelist, context=None):
        if context is None:
            context = {}
        version_obj = self.pool.get('product.pricelist.version')

        if pricelist:
            version_ids = version_obj.search(cr, uid, [(
                'pricelist_id', '=', pricelist)], context=context)

        return {'value': {'version_ids': version_ids}}
