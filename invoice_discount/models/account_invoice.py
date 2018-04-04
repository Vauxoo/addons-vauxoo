# Copyright 2018 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountInvoiceLine(models.Model):

    """Inherit from account.invoice.line to get by line the amount without
    discount and the amount of this
    """
    _inherit = 'account.invoice.line'

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal_without_discount(self):
        """Method to get the subtotal of the amount without discount
        """
        for line in self:
            line.subtotal_wo_discount = (line.quantity * line.price_unit)

    @api.depends('subtotal_wo_discount', 'discount')
    def _compute_discount(self):
        """Method to get the amount of discount, is used subtraction by
        rounding"""
        for line in self:
            line.discount_amount = line.discount * \
                line.subtotal_wo_discount / 100

    subtotal_wo_discount = fields.Float(
        compute='_compute_subtotal_without_discount',
        string='SubTotal w/o Discount', store=True,
        help='Amount without apply the discount of the line, is calculated as '
        'Qty * Price Unit')
    discount_amount = fields.Float(
        compute='_compute_discount',
        help='Amount total of the discount, is calculated as Discount * '
        'SubTotal w/o Discount / 100.')


class AccountInvoice(models.Model):

    """Inherit from account.invoice to get the amount total without discount
    and the amount total of this, of all invoice lines.
    """
    _inherit = 'account.invoice'

    @api.depends('invoice_line_ids.subtotal_wo_discount')
    def _compute_subtotal_without_discount(self):
        """Method to get the subtotal of the amount without discount of the
        sum of invoice lines.
        """
        total = 0.0
        for inv in self:
            for line in inv.invoice_line_ids:
                total += line.subtotal_wo_discount
            inv.subtotal_wo_discount = total

    @api.depends('invoice_line_ids.discount_amount')
    def _compute_discount(self):
        """Method to get the amount total of discount in the invoice lines.
        """
        total = 0.0
        for inv in self:
            for line in inv.invoice_line_ids:
                total += line.discount_amount
            inv.discount_amount = total

    subtotal_wo_discount = fields.Float(
        compute='_compute_subtotal_without_discount',
        string='SubTotal w/o Discount', store=True,
        help='Amount without apply the discount of the lines of the invoice.')
    discount_amount = fields.Float(
        compute='_compute_discount', string='Discount',
        help='Total of discount apply in each line of the invoice.')
