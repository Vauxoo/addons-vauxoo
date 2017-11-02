# coding: utf-8

from openerp import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _create_account_move_line(
            self, cr, uid, move, src_account_id, dest_account_id,
            reference_amount, reference_currency_id, context=None):
        """ This super will add a new key into the context sending
        `novalidate=True` in order to avoid validation at Entry Lines creation.
        after all lines are created and glued their Journal Entry if ever
        posted at `move.post()` does a validation on all the previous Journal
        Items at https://goo.gl/KHuwpR
        `valid_moves = self.validate(cr, uid, ids, context)`.
        Therefore, when creating the Journal Entry for a quant/stock_move it is
        enough to do one validate when posting the Journal Entry and skip the
        other validations at creation time
        """
        ctx = dict(context, novalidate=True)
        return super(StockQuant, self)._create_account_move_line(
            cr, uid, move, src_account_id, dest_account_id, reference_amount,
            reference_currency_id, context=ctx)
