from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    code = fields.Char(help="Internal code name of the company")

    _unique_code = models.Constraint(
        "UNIQUE(code)",
        "Code must be unique",
    )
