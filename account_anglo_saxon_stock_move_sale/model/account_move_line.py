# coding: utf-8

from odoo import models, fields


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    sale_id = fields.Many2one(
        'sale.order',
        related='sm_id.sale_line_id.order_id',
        string='Sale Order',
        store=True)
