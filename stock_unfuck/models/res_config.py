# -*- coding: utf-8 -*-

from openerp import fields, models


class StockConfiguration(models.TransientModel):

    _inherit = 'stock.config.settings'

    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)

    make_journal_entry = fields.Boolean(
        related='company_id.make_journal_entry',
        string='Make journal entry in update of cost in products like average')
