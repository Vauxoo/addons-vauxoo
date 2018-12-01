from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    index_based_currency_id = fields.Many2one(
        'res.currency',
        help="Currency used por reporting purposes",
        default=lambda self: self.env.ref('base.USD'))
