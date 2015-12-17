# coding: utf-8

from openerp import models
SEGMENTATION = ['material', 'landed', 'production', 'subcontracting']

# TODO: multi-company awareness to be developed


class StockCardProduct(models.TransientModel):
    _inherit = ['stock.card.product']

    def _get_quant_values(self, move_id, col='', inner='', where=''):
        col = ', ' + ', '.join(['%s_cost' % sgmnt for sgmnt in SEGMENTATION])
        return super(StockCardProduct, self)._get_quant_values(
            move_id=move_id, col=col, inner=inner, where=where)

    def _get_default_params(self):
        res = super(StockCardProduct, self)._get_default_params()
        return res.update({}.from_keys(SEGMENTATION, 0.0))


class StockCardMove(models.TransientModel):
    _inherit = 'stock.card.move'
