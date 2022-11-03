from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    code = fields.Char(help="Internal code name of the company")

    _sql_constraints = [
        ("unique_code", "UNIQUE(code)", "Code must be unique"),
    ]
