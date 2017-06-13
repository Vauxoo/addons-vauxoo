# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
#
from openerp import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('product_id')
    def _compute_product_customer_code(self):
        product_customer_code_obj = self.env['product.customer.code']
        for line in self:
            partner = line.order_id.partner_id
            product = line.product_id
            if product and partner:
                code_ids = product_customer_code_obj.search([
                    ('product_id', '=', product.id),
                    ('partner_id', '=', partner.id)], limit=1)
                self.product_customer_code = code_ids.product_code
        return self.product_customer_code

    product_customer_code = fields.Char(
        compute='_compute_product_customer_code', size=64,
        help='define customer code')
