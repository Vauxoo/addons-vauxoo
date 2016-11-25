# -*- coding: utf-8 -*-

from openerp import fields, models

SEGMENTATION_COST = [
    ('landed_cost', 'Landed Cost'),
    ('subcontracting_cost', 'Subcontracting Cost'),
    ('material_cost', 'Material Cost'),
    ('production_cost', 'Production Cost'),
]


class StockDiscrete(models.Model):

    _inherit = 'stock.discrete'

    segmentation_cost = fields.Selection(
        SEGMENTATION_COST,
        string='Segmentation',
    )
