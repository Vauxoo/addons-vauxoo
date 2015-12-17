# coding: utf-8

from openerp import models

# TODO: multi-company awareness to be developed


class StockCardProduct(models.TransientModel):
    _inherit = ['stock.card.product']

    def _get_quant_values(self, move_id, col='', inner='', where=''):
        col = (', material_cost, landed_cost'
               ', production_cost, subcontracting_cost')
        return super(StockCardProduct, self)._get_quant_values(
            move_id=move_id, col=col, inner=inner, where=where)


class StockCardMove(models.TransientModel):
    _inherit = 'stock.card.move'
