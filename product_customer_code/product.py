# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Rodo (rodo@vauxoo.com),Moy (moylop260@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import api, SUPERUSER_ID
from openerp.osv import osv, fields


class ProductProduct(osv.Model):
    _inherit = "product.product"

    _columns = {
        'product_customer_code_ids': fields.one2many('product.customer.code',
                                                     'product_id',
                                                     'Customer Codes'),
    }

    @api.one
    def copy(self, default=None):
        if not default:
            default = {}
        default['product_customer_code_ids'] = False
        res = super(ProductProduct, self).copy(default=default)
        return res

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []

        def _name_get(d):
            name = d.get('name', '')
            code = context.get(
                'display_default_code', True) and d.get(
                    'default_code', False) or False
            base_product = d.get('product_obj', False)
            if code:
                if context.get('type', False) == 'out_invoice' and\
                        base_product and not d.get('has_customer'):
                    name = '[%s] %s' % (base_product.default_code,
                                        base_product.name)
                else:
                    name = '[%s] %s' % (code, name)
            return (d['id'], name)
        partner_id = context.get('partner_id', False)
        if partner_id:
            partner_ids = [
                partner_id, self.pool['res.partner'].browse(
                    cr,
                    user,
                    partner_id, context=context).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights(cr, user, "read")
        self.check_access_rule(cr, user, ids, "read", context=context)

        result = []
        for product in self.browse(cr, SUPERUSER_ID, ids, context=context):
            variant = ", ".join([v.name for v in product.attribute_value_ids])
            name = variant and "%s (%s)" % (
                product.name, variant) or product.name
            sellers = []
            buyers = []
            if partner_ids:
                sellers = filter(
                    lambda x: x.name.id in partner_ids, product.seller_ids)
                buyers = filter(
                    lambda x: x.partner_id.id == partner_id,
                    product.product_customer_code_ids)
            if sellers:
                for seller in sellers:
                    seller_variant = seller.product_name and "%s (%s)" % (
                        seller.product_name, variant) or False
                    mydict = {
                        'id': product.id,
                        'name': seller_variant or name,
                        'default_code': seller.product_code or
                        product.default_code,
                        }
                    result.append(_name_get(mydict))
            elif buyers:
                for buyer in buyers:
                    mydict = {
                        'id': product.id,
                        'name': buyer.product_name or product.name,
                        'default_code': buyer.product_code or
                        product.default_code,
                        'product_obj': product,
                        'has_customer': True
                        }
                    result.append(_name_get(mydict))
            else:
                mydict = {
                    'id': product.id,
                    'name': name,
                    'default_code': product.default_code,
                    }
                result.append(_name_get(mydict))
        return result

    def name_search(self, cr, user, name='', args=None, operator='ilike',
                    context=None, limit=80):
        res = super(ProductProduct, self).name_search(
            cr, user, name, args, operator, context, limit)
        if not context:
            context = {}
        product_customer_code_obj = self.pool.get('product.customer.code')
        if not res:
            ids = []
            partner_id = context.get('partner_id', False)
            if partner_id:
                id_prod_code = \
                    product_customer_code_obj.search(cr, user,
                                                     [('product_code',
                                                       '=', name),
                                                         ('partner_id', '=',
                                                          partner_id)],
                                                     limit=limit,
                                                     context=context)
                # TODO: Search for product customer name
                id_prod = id_prod_code and product_customer_code_obj.browse(
                    cr, user, id_prod_code, context=context) or []
                for ppu in id_prod:
                    ids.append(ppu.product_id.id)
            if ids:
                res = self.name_get(cr, user, ids, context)
        return res
