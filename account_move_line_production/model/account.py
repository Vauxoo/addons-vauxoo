from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    production_id = fields.Many2one(
        'mrp.production',
        string='Manufacturing Order',
        readonly=True,
    )
