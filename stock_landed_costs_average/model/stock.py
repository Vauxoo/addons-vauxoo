# -*- coding: utf-8 -*-

from openerp import fields, models


class StockDiscrete(models.Model):

    _name = 'stock.discrete'

    cost = fields.Float()
    move_id = fields.Many2one('stock.move')


class StockMove(models.Model):

    _inherit = 'stock.move'

    discrete_ids = fields.One2many('stock.discrete', 'move_id')
