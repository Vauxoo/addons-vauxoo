# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
###############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _


class inherited_product(osv.Model):
    """
    M321 Customizations for product.product model
    """
    _inherit = "product.product"

    def _get_even_pos(self, li):
        for index in range(len(li)):
            if (index + 1) % 2 == 0:
                yield li[index]

    def _get_odd_pos(self, li):
        for index in range(len(li)):
            if (index + 1) % 2 != 0:
                yield li[index]

    def copy(self, cr, uid, id, default=None, context=None):

        if default is None:
            default = {}

        if context is None:
            context = {}

        default = default.copy()
        default.update({'upc': False,
                        })

        return super(inherited_product, self).copy(cr, uid, id, default,
                                                                    context)

    def _stock_available(self, cr, uid, ids, field_name, arg, context):
        if context is None:
            context = {}
        if not len(ids):
            return []
        res = {}

        for id in self.browse(cr, uid, ids, context=context):
            if id.virtual_available > 0.0:
                res[id.id] = True
            else:
                res[id.id] = False
        return res

    def _get_stock(self, cr, uid, ids, context):

        if context is None:
            context = {}

        if not len(ids):
            return []
        product = []
        stock_move_obj = self.pool.get('stock.move')

        for stock in stock_move_obj.browse(cr, uid, ids, context=context):
            stock.product_id and product.append(stock.product_id.id)
        return product

    def _get_sale(self, cr, uid, ids, context):

        if context is None:
            context = {}

        if not len(ids):
            return []
        product = []

        for sale in self.pool.get('sale.order').browse(cr, uid, ids,
                                                            context=context):
            for line in sale.order_line:
                sale.product_id and product.append(sale.product_id.id)
        return product

    def _get_purchase(self, cr, uid, ids, context):

        if context is None:
            context = {}

        if not len(ids):
            return []
        product = []

        for purchase in self.pool.get('purchase.order').browse(cr, uid, ids,
                                                            context=context):
            for line in purchase.order_line:
                purchase.product_id and product.append(purchase.product_id.id)
        return product

    def _search_virtual_available(self, cr, uid, obj, name, args, context):
        product_ids = self.search(cr, uid, [], context=context)
        product_ids = product_ids and [i.id for i in self.browse(
            cr, uid, product_ids, context=context) if i .virtual_available > 0]
        if product_ids:
            return [('id', 'in', product_ids)]
        else:
            return [('id', '=', '0')]

    def _find_next_ten_multi(self, value):
        while (value % 10 != 0):
            value += 1
        return value

    # Source for the validation algorithm: http://www.ehow.com
    # /how_6810204_verify-upc-number.html
    def _check_upc(self, cr, uid, ids, context=None):
        this_record = self.browse(cr, uid, ids)

        if this_record[0].upc:
            if this_record[0].upc.isdigit():
                upc = map(int, this_record[0].upc)
                if len(upc) == 12:
                    check = upc[-1]
                    del(upc[-1])
                    result = (sum(tuple(self._get_odd_pos(
                        upc))) * 3) + sum(tuple(self._get_even_pos(upc)))
                    multi_ten = self._find_next_ten_multi(result)
                    if multi_ten - result == check:
                        return True
                return False
            else:
                raise osv.except_osv(_('Error'), _(
                    'Upc code should only be numeric'))
        else:
            return True

    def _check_upc_reference_unique(self, cr, uid, ids, context=None):

        for product in self.browse(cr, uid, ids):
            product_code_ids = product.default_code and self.search(cr, uid, [(
                'default_code', '=', product.default_code)],
                context=context) or [product.id]
            product_upc_ids = product.upc and self.search(cr, uid, [(
                'upc', '=', product.upc)], context=context) or [product.id]
            if not product.default_code and not product.upc:
                return True

            elif len(product_code_ids) > 1 or len(product_upc_ids) > 1 or\
                product.id not in product_code_ids or product.id not in\
                product_upc_ids:
                return False

        return True

    def copy(self, cr, uid, id, default=None, context=None):

        if default is None:
            default = {}

        if context is None:
            context = {}

        default = default.copy()
        default.update({'upc': False, 'ean13': False, 'default_code': False,
                        })

        return super(inherited_product, self).copy(cr, uid, id, default,
                                                                    context)

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if not len(ids):
            return []

        def _name_get(d):
            name = d.get('name', '')
            code = d.get('default_code', False)
            upc = d.get('upc', False)
            ean13 = d.get('ean13', False)
            cc = upc and '%s' % upc or ean13 and '%s' % ean13 or code
            if cc:
                name = '[%s] %s' % (cc, name)
            if d.get('variants'):
                name = name + ' - %s' % (d['variants'],)
            return (d['id'], name)

        partner_id = context.get('partner_id', False)

        result = []
        for product in self.browse(cr, user, ids, context=context):
            sellers = filter(
                lambda x: x.name.id == partner_id, product.seller_ids)
            if sellers:
                for s in sellers:
                    mydict = {
                        'id': product.id,
                        'name': s.product_name or product.name,
                        'default_code': s.product_code or product.default_code,
                        'upc': product.upc or False,
                        'ean13': product.ean13 or False,
                        'variants': product.variants,
                    }
                    result.append(_name_get(mydict))
            else:
                mydict = {
                    'id': product.id,
                    'name': product.name,
                    'default_code': product.default_code,
                    'upc': product.upc or False,
                    'ean13': product.ean13 or False,
                    'variants': product.variants,
                }
                result.append(_name_get(mydict))
        # return super(inherited_product, self).name_get(cr, user, ids,
        # context)

        return result

    _columns = {
        'upc': fields.char("UPC", size=12,
            help="Universal Product Code (12 digits)"),
        'available_boolean': fields.function(_stock_available,
            type='boolean', method=True,
            fnct_search=_search_virtual_available),
        'profit_code': fields.char("Code from profit", size=20,
            help="Code from profit database"),
    }

    _constraints = [(_check_upc, 'ERROR, Invalid UPC', ['upc']), (
        _check_upc_reference_unique,
        'ERROR, the upc or reference must by unique', ['upc', 'reference'])]
