# -*- coding: utf-8 -*-
from openerp import api, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _get_avg_valuation_by_move(self, cr, uid, move, context=None):
        context = dict(context or {})
        dst = move.location_dest_id.usage
        src = move.location_id.usage
        signal = 1 if dst == 'internal' else -1
        val_amount = 0

        if dst in ('customer', 'production', 'inventory', 'transit'):
            val_amount = move.product_id.standard_price

        elif dst in ('supplier',):
            if move.product_id.qty_available > 0:
                # /!\ NOTE: We will fallback to average price if no origin is
                # found
                origin_id = move.origin_returned_move_id
                val_amount = origin_id and origin_id.price_unit or \
                        move.product_id.standard_price
            else:
                # /!\ NOTE: We will use average price if no merchandise is left
                # after Purchase Return
                val_amount = move.product_id.standard_price

        elif src in ('supplier', ):
            val_amount = move.price_unit

        elif src in ('production', 'inventory', ):
            # /!\ NOTE: Meanwhile will be taken at standard_price, i.e.,
            # current average, for Manufacturing Orders it could be the Cost of
            # Production of the product.
            val_amount = move.product_id.standard_price

        elif src in ('customer', 'transit'):
            # TODO:
            origin_id = move.origin_returned_move_id or move.move_dest_id
            val_amount = origin_id and origin_id.price_unit or \
                    move.product_id.standard_price

        return signal * val_amount

    def _prepare_account_move_line(
            self, cr, uid, move, qty, cost, credit_account_id,
            debit_account_id, context=None):
        """ Generate the account.move.line values to post to track the stock
        valuation difference due to the processing of the given quant. """
        context = dict(context or {})
        currency_obj = self.pool.get('res.currency')
        res = super(StockQuant, self)._prepare_account_move_line(
            cr, uid, move, qty, cost, credit_account_id, debit_account_id,
            context)

        # /!\ NOTE: From odoo/addons/stock_account/stock_account.py
        # _prepare_account_move_line method returns a list with the following
        # footprint: res = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        # thus debit_line_vals = res[0][2] and credit_line_vals = res[1][2]
        if not context.get('force_val_amount') and \
                move.product_id.cost_method == 'average':
            val_amount = self._get_avg_valuation_by_move(
                    cr, uid, move, context=context)
            val_amount = currency_obj.round(
                    cr, uid, move.company_id.currency_id, val_amount * qty)
            res[0][2]['debit'] = val_amount > 0 and val_amount or 0
            res[0][2]['credit'] = val_amount < 0 and -val_amount or 0
            res[1][2]['credit'] = val_amount > 0 and val_amount or 0
            res[1][2]['debit'] = val_amount < 0 and -val_amount or 0
        return res
