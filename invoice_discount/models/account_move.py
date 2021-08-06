# Copyright 2018 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):

    """Inherit from account.move.line to get by line the amount without
    discount and the amount of this
    """
    _inherit = 'account.move.line'

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
            line.discount_amount = line.discount * line.subtotal_wo_discount / 100

    subtotal_wo_discount = fields.Float(
        compute='_compute_subtotal_without_discount',
        string='SubTotal w/o Discount', store=True,
        help='Amount without apply the discount of the line, is calculated as Qty * Price Unit')
    discount_amount = fields.Float(
        compute='_compute_discount',
        store=True,
        help='Amount total of the discount, is calculated as Discount * SubTotal w/o Discount / 100.')


class AccountMove(models.Model):

    """Inherit from account.move to get the amount total without discount
    and the amount total of this, of all invoice lines.
    """
    _inherit = 'account.move'

    @api.depends('invoice_line_ids.subtotal_wo_discount', 'invoice_line_ids.discount_amount')
    def _compute_discount_amounts(self):
        """Method to get the subtotal of the amount without discount of the
        sum of invoice lines.
        """
        move_lines = self.env['account.move.line'].read_group(
            [('move_id', 'in', self.ids)], ['move_id', 'discount_amount', 'subtotal_wo_discount'], ['move_id'])
        amounts = dict((lines['move_id'][0], {
            'subtotal_wo_discount': lines['subtotal_wo_discount'],
            'discount_amount': lines['discount_amount'],
        }) for lines in move_lines)
        for move in self:
            amount_dict = amounts.get(move.id, {})
            move.discount_amount = amount_dict.get('discount_amount', 0.0)
            move.subtotal_wo_discount = amount_dict.get('subtotal_wo_discount', 0.0)

    subtotal_wo_discount = fields.Float(
        compute='_compute_discount_amounts',
        string='SubTotal w/o Discount', store=True,
        help='Amount without apply the discount of the lines of the invoice.')
    discount_amount = fields.Float(
        compute='_compute_discount_amounts', string='Discount', store=True,
        help='Total of discount apply in each line of the invoice.')
