from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    margin_threshold = fields.Float(help="Margin Threshold for product in order lines")
