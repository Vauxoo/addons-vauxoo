# coding: utf-8

from openerp import api, fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    product_customer_code_ids = fields.One2many(
        'product.customer.code', 'product_id', string='Product customer codes',
        copy=False, help='Customer Codes')

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=80):
        res = super(ProductProduct, self).name_search(
            name, args=args, operator=operator, limit=limit)
        product_customer_code_obj = self.env['product.customer.code']
        if not res:
            prod_code_ids = []
            partner_id = self._context.get('partner_id')
            if partner_id:
                prod_code_ids = product_customer_code_obj.search(
                    [('product_code', '=', name),
                     ('partner_id', '=', partner_id)], limit=limit)
                # TODO: Search for product customer name
            if prod_code_ids:
                res = prod_code_ids.mapped('product_id').name_get()
        return res
