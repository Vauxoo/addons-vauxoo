from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)
    type = fields.Selection(tracking=True)
    default_account_id = fields.Many2one(tracking=True)
    currency_id = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)
    active = fields.Boolean(tracking=True)
    account_control_ids = fields.Many2many(tracking=True)
    refund_sequence = fields.Boolean(tracking=True)
    restrict_mode_hash_table = fields.Boolean(tracking=True)
