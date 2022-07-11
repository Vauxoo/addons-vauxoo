# Copyright 2022 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _prepare_invoice_line(self, order_line):
        '''Apply the global discount to each line.'''
        self.ensure_one()
        vals = super()._prepare_invoice_line(order_line)
        if self.session_id.config_id.module_pos_discount:
            vals = self._prepare_invoice_line_global_discount(vals)
        return vals

    def _prepare_invoice_line_global_discount(self, vals):
        '''Apply the global discount to each line. The discount is applied before taxes.
        First get the discount percentage and then apply to the unit price. After that send to the invoice creation'''
        discount_product_id = self.session_id.config_id.discount_product_id
        if discount_product_id.id == vals['product_id']:
            vals['price_unit'] = 0
            return vals
        if self.lines and discount_product_id in self.mapped('lines.product_id'):
            lines_discount = self.lines.filtered(lambda l: l.product_id == discount_product_id)
            discount_amount = sum(lines_discount.mapped('price_unit'))
            total_wo_discount_tax = self.amount_total - self.amount_tax - discount_amount
            # Keeping the 100 to minimize rounding problems
            percentage = abs(discount_amount * 100 / total_wo_discount_tax)
            vals['price_unit'] = vals['price_unit'] - (vals['price_unit'] * percentage / 100)
        return vals
