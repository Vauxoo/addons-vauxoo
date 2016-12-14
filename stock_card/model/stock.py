# -*- coding: utf-8 -*-

from openerp import fields, models, api


class StockDiscrete(models.Model):

    _name = 'stock.discrete'

    cost = fields.Float()
    move_id = fields.Many2one('stock.move')


class StockMove(models.Model):

    _inherit = 'stock.move'

    discrete_ids = fields.One2many('stock.discrete', 'move_id')

    @api.multi
    def _check_return_move(self):
        """ Use this method to indicate when move is a
        refund customer/supplier
        """
        for move in self:
            if move.product_id.cost_method == 'average' and \
                    move.product_id.valuation == 'real_time':
                if move.location_dest_id.usage == 'internal' and \
                        move.location_id.usage in ('supplier', 'customer'):
                    return True
