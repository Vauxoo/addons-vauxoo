from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    date = fields.Date(tracking=True)
    journal_id = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)
    reversed_entry_id = fields.Many2one(tracking=True)
    fiscal_position_id = fields.Many2one(tracking=True)
    auto_post = fields.Selection(tracking=True)
    auto_post_until = fields.Date(tracking=True)
