# coding: utf-8

from openerp import models, api


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.v7
    def _prepare_account_move_line(self, cr, uid, move, qty, cost,
                                   credit_account_id, debit_account_id,
                                   context=None):
        res = super(StockQuant, self)._prepare_account_move_line(
            cr, uid, move, qty, cost, credit_account_id, debit_account_id,
            context)
        for line in res:
            line[2]['production_id'] = move.production_id.id
        return res
