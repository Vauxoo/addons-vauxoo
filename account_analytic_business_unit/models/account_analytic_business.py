from odoo import models, fields, _


class AccountAnalyticDistribution(models.Model):
    _name = 'account.analytic.business.unit'
    _description = 'Analytic Account Business Unit'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner")

    _sql_constraints = [
        ('unique_code', 'UNIQUE(code, name)',
         'The combination of code and and name for a business unit must be unique.')
    ]
