# coding: utf-8

from openerp import models, fields


class StockQuant(models.Model):
    _inherit = "stock.quant"

    material_cost = fields.Float(string='Material Cost')
    production_cost = fields.Float(string='Production Cost')
    subcontracting_cost = fields.Float(string='Subcontracting Cost')
    landed_cost = fields.Float(string='Landed Cost')
