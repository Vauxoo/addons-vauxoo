from odoo import models, fields


class MrpProduction(models.Model):
    """Production Orders / Manufacturing Orders
    """
    _inherit = 'mrp.production'
    _description = 'Manufacturing Order'
    aml_production_ids = fields.One2many(
        'account.move.line',
        'production_id',
        string='Production Journal Entries',
        readonly=True,
    )


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    costs_general_account_id = fields.Many2one(
        'account.account', string='General Account')
