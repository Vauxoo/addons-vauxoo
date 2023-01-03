from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    brand_bpp = fields.Integer(default=20, string="Number of brands")
