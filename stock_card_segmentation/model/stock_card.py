# coding: utf-8

from openerp import models, fields
import openerp.addons.decimal_precision as dp
SEGMENTATION = ['material', 'landed', 'production', 'subcontracting']

# TODO: multi-company awareness to be developed


class StockCardProduct(models.TransientModel):
    _inherit = ['stock.card.product']

    def _get_quant_values(self, move_id, col='', inner='', where=''):

        col = ['%s_cost' % sgmnt for sgmnt in SEGMENTATION]
        col = ['COALESCE(%s, 0.0) AS %s' % (cl, cl) for cl in col]
        col = ', ' + ', '.join(col)
        return super(StockCardProduct, self)._get_quant_values(
            move_id=move_id, col=col, inner=inner, where=where)

    def _get_stock_card_move_line_dict(self, row, vals):
        res = super(StockCardProduct, self)._get_stock_card_move_line_dict(
            row, vals)
        res = dict(
            res,
            material=vals['material'],
            landed=vals['landed'],
            production=vals['production'],
            subcontracting=vals['subcontracting'],
            )
        return res

    def _get_default_params(self):
        res = super(StockCardProduct, self)._get_default_params()
        res.update({}.fromkeys(SEGMENTATION, 0.0))
        res.update({}.fromkeys(
            ['%s_total' % sgmnt for sgmnt in SEGMENTATION], 0.0))
        return res

    def _get_price_on_consumed(self, row, vals, qntval):
        super(StockCardProduct, self)._get_price_on_consumed(
            row, vals, qntval)

        move_id = row['move_id']

        for sgmnt in SEGMENTATION:
            vals['move_dict'][move_id][sgmnt] = vals[sgmnt]
            vals['%s_valuation' % sgmnt] = sum(
                [vals['%s' % sgmnt] * qnt['qty'] for qnt in qntval
                 if qnt['qty'] > 0])
        return True

    def _get_price_on_supplier_return(self, row, vals, qntval):
        super(StockCardProduct, self)._get_price_on_supplier_return(
            row, vals, qntval)

        for sgmnt in SEGMENTATION:
            vals['%s_valuation' % sgmnt] = sum(
                [qnt['%s_cost' % sgmnt] * qnt['qty'] for qnt in qntval])

        return True

    def _get_price_on_supplied(self, row, vals, qntval):
        super(StockCardProduct, self)._get_price_on_supplied(
            row, vals, qntval)

        for sgmnt in SEGMENTATION:
            vals['%s_valuation' % sgmnt] = sum(
                [qnt['%s_cost' % sgmnt] * qnt['qty'] for qnt in qntval])

        return True

    def _get_price_on_customer_return(self, row, vals, qntval):
        super(StockCardProduct, self)._get_price_on_customer_return(
            row, vals, qntval)

        sm_obj = self.env['stock.move']
        move_id = row['move_id']
        move_brw = sm_obj.browse(move_id)
        origin_id = move_brw.origin_returned_move_id.id

        for sgmnt in SEGMENTATION:
            old_average = (
                vals['move_dict'].get(origin_id, 0.0) and
                vals['move_dict'][move_id][sgmnt] or
                vals[sgmnt])

            vals['%s_valuation' % sgmnt] = sum(
                [old_average * qnt['qty'] for qnt in qntval])

        return True

    def _get_move_average(self, row, vals):
        super(StockCardProduct, self)._get_move_average(row, vals)
        qty = row['product_qty']
        vals['cost_unit'] = vals['move_valuation'] / qty if qty else 0.0

        for sgmnt in SEGMENTATION:
            vals['%s_total' % sgmnt] += (
                vals['direction'] * vals['%s_valuation' % sgmnt])

            vals[sgmnt] = (
                vals['product_qty'] and
                vals['%s_total' % sgmnt] / vals['product_qty'] or
                vals[sgmnt])

        return True


class StockCardMove(models.TransientModel):
    _inherit = 'stock.card.move'
    material = fields.Float(
        string='Material Cost',
        digits=dp.get_precision('Account'),
        readonly=True)
    landed = fields.Float(
        string='Landed Cost',
        digits=dp.get_precision('Account'),
        readonly=True)
    production = fields.Float(
        string='Production Cost',
        digits=dp.get_precision('Account'),
        readonly=True)
    subcontracting = fields.Float(
        string='Subcontracting Cost',
        digits=dp.get_precision('Account'),
        readonly=True)
