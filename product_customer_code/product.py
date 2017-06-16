# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openerp import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_customer_code_ids = fields.One2many('product.customer.code',
                                                'product_id',
                                                help='Customer Codes',
                                                string='product customer code')

    @api.one
    def copy(self, default=None):
        if not default:
            default = {}
        default['product_customer_code_ids'] = False
        res = super(ProductProduct, self).copy(default=default)
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=80):
        res = super(ProductProduct, self).name_search(name=name, args=args,
                                                      operator=operator,
                                                      limit=limit)
        product_customer_code_obj = self.env['product.customer.code']
        if not res:
            ids = []
            partner_id = self._context.get('partner_id')
            if partner_id:
                id_prod_code = product_customer_code_obj.search(
                    [('product_code', '=', name),
                     ('partner_id', '=', partner_id)], limit=limit)
                # TODO: Search for product customer name
                for ppu in id_prod_code:
                    ids.append(ppu.product_id.id)
            if ids:
                res = product_customer_code_obj.product_id.name_get()
        return res
