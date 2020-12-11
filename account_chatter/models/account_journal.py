# Copyright 2020 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class AccountJournal(models.Model):

    _inherit = "account.journal"

    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)
    type = fields.Selection(tracking=True)
    default_account_id = fields.Many2one(tracking=True)
    currency_id = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)
    active = fields.Boolean(tracking=True)
