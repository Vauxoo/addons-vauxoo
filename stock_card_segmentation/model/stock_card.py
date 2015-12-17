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

    def _get_price_on_consumed(self, row, vals, values):
        super(StockCardProduct, self)._get_price_on_consumed(
            row, vals, values)

        move_id = row['move_id']

        for sgmnt in SEGMENTATION:
            vals['move_dict'][move_id][sgmnt] = vals[sgmnt]
            vals['%s_valuation' % sgmnt] = sum(
                [vals[sgmnt] * val['qty'] for val in values])
        return True


class StockCardMove(models.TransientModel):
    _inherit = 'stock.card.move'
