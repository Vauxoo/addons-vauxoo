from odoo import fields, models


class AccountAnalyticDistribution(models.Model):
    _name = "account.analytic.business.unit"
    _description = "Analytic Account Business Unit"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner")

    _sql_constraints = [
        (
            "unique_code",
            "UNIQUE(code, name)",
            "The combination of code and and name for a business unit must be unique.",
        )
    ]

    def name_get(self):
        res = []
        for business_unit in self:
            name = business_unit.name
            if business_unit.code:
                name = "[" + business_unit.code + "] " + name
            res.append((business_unit.id, name))
        return res
