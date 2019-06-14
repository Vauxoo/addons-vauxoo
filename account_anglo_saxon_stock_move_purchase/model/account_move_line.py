# coding: utf-8

from odoo import models, fields


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    purchase_id = fields.Many2one(
        'purchase.order',
        related='sm_id.purchase_line_id.order_id',
        string='Purchase Order',
        store=True)
