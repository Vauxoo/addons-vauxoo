# Copyright 2020 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class AccountJournal(models.Model):

    _inherit = ["account.journal", "mail.thread"]
    _name = "account.journal"

    name = fields.Char(track_visibility=True)
    code = fields.Char(track_visibility=True)
    type = fields.Selection(track_visibility=True)
    default_credit_account_id = fields.Many2one(track_visibility=True)
    default_debit_account_id = fields.Many2one(track_visibility=True)
    currency_id = fields.Many2one(track_visibility=True)
    company_id = fields.Many2one(track_visibility=True)
    active = fields.Boolean(track_visibility=True)
