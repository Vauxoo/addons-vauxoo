# coding: utf-8

from openerp import models, fields


class MrpProduction(models.Model):
    """
    Production Orders / Manufacturing Orders
    """
    _inherit = 'mrp.production'
    _description = 'Manufacturing Order'
    aml_production_ids = fields.One2many(
        'account.move.line',
        'production_id',
        string='Production Journal Entries',
        readonly=True,
        )
