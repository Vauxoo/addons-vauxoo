from odoo import fields, models


class ResConfiguration(models.TransientModel):
    _inherit = "res.config.settings"

    margin_threshold = fields.Float(related="company_id.margin_threshold", readonly=False)
