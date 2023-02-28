# Copyright 2020 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountAccount(models.Model):

    _name = "account.account"
    _inherit = ["account.account", "mail.thread", "mail.activity.mixin"]

    tax_ids = fields.Many2many(tracking=True)
    tag_ids = fields.Many2many(tracking=True)
    group_id = fields.Many2one(tracking=True)
    allowed_journal_ids = fields.Many2many(tracking=True)
