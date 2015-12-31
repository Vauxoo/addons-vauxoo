# -*- coding: utf-8 -*-

from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    stock_landed_cost_id = fields.Many2one(
        'stock.landed.cost',
        string='Landed Costs',
        readonly=True,
        copy=False,
        )
