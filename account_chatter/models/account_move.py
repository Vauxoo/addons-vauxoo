# Copyright 2020 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountMove(models.Model):

    _name = "account.move"
    _inherit = ['account.move', 'mail.thread']

    name = fields.Char(track_visibility=True)
    ref = fields.Char(track_visibility=True)
    date = fields.Date(track_visibility=True)
    journal_id = fields.Many2one(track_visibility=True)
    currency_id = fields.Many2one(track_visibility=True)
    state = fields.Selection(track_visibility=True)
    partner_id = fields.Many2one(track_visibility=True)
    amount = fields.Monetary(track_visibility=True)
    narration = fields.Text(track_visibility=True)
    auto_reverse = fields.Boolean(track_visibility=True)
    reverse_date = fields.Date(track_visibility=True)
    reverse_entry_id = fields.Many2one(track_visibility=True)
