# -*- coding: utf-8 -*-

from __future__ import division

from openerp import api, models


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.multi
    def _recalculation_average_cost_price(self, signal=1):
        """ move is a browse record """
        for move in self:
            if move.product_qty == 0:
                return
            for quant in move.reserved_quant_ids:
                if quant.qty <= 0:
                    return
            qty_available = move.product_id.product_tmpl_id.qty_available
            if (qty_available + move.product_qty * signal) == 0:
                continue
            orig = (move.origin_returned_move_id or
                    (move.move_orig_ids and move.move_orig_ids[0]))
            amount_unit = move.product_id.standard_price
            if signal == 1:
                average_valuation_price = sum(
                    [quant.qty * (orig.price_unit if orig else amount_unit)
                     for quant in move.reserved_quant_ids])
            else:
                average_valuation_price = sum(
                    [quant.qty * (orig.price_unit if orig else quant.cost)
                     for quant in move.reserved_quant_ids])
            new_std_price = (
                (amount_unit * qty_available) +
                average_valuation_price * signal) / (
                    qty_available + move.product_qty * signal)
            move.product_id.sudo().write({'standard_price': new_std_price})

    @api.multi
    def product_price_update_before_done(self):
        res = super(StockMove, self).product_price_update_before_done()
        for move in self.filtered(
                lambda m: m.product_id.cost_method == 'average'):
            signal = 0
            if move.location_dest_id.usage == 'supplier':
                signal = -1
            elif (move.location_id.usage in ('customer', 'transit') and
                  move.location_dest_id.usage == 'internal'):
                signal = 1
            if signal:
                move._recalculation_average_cost_price(signal)
        return res
