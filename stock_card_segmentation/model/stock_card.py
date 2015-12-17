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
                [vals['%s_cost' % sgmnt] * val['qty'] for val in values])
        return True

    def _get_price_on_supplier_return(self, row, vals, values):
        super(StockCardProduct, self)._get_price_on_supplier_return(
            row, vals, values)

        for sgmnt in SEGMENTATION:
            vals['%s_valuation' % sgmnt] = sum(
                [vals['%s_cost' % sgmnt] * val['qty'] for val in values])

        return True

    def _get_price_on_supplied(self, row, vals, values):
        super(StockCardProduct, self)._get_price_on_supplied(
            row, vals, values)

        for sgmnt in SEGMENTATION:
            vals['%s_valuation' % sgmnt] = sum(
                [vals['%s_cost' % sgmnt] * val['qty'] for val in values])

        return True

    def _get_price_on_customer_return(self, row, vals, values):
        super(StockCardProduct, self)._get_price_on_customer_return(
            row, vals, values)

        sm_obj = self.env['stock.move']
        move_id = row['move_id']
        move_brw = sm_obj.browse(move_id)
        origin_id = move_brw.origin_returned_move_id.id

        for sgmnt in SEGMENTATION:
            old_average = (
                vals['move_dict'].get(origin_id, 0.0) and
                vals['move_dict'][move_id][sgmnt] or
                vals['sgmnt'])

            vals['%s_valuation' % sgmnt] = sum(
                [old_average * val['qty'] for val in values])

        return True


class StockCardMove(models.TransientModel):
    _inherit = 'stock.card.move'
