# Copyright 2020 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    name = fields.Char(tracking=True)
    ref = fields.Char(tracking=True)
    date = fields.Date(tracking=True)
    journal_id = fields.Many2one(tracking=True)
    narration = fields.Text(tracking=True)
    reversed_entry_id = fields.Many2one(tracking=True)
