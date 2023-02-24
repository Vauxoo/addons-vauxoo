from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    date = fields.Date(tracking=True)
    journal_id = fields.Many2one(tracking=True)
    narration = fields.Text(tracking=True)
    reversed_entry_id = fields.Many2one(tracking=True)
