from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _create_account_move_line(
            self, credit_account_id, debit_account_id, journal_id):
        """ This super will add a new key into the context sending
        `novalidate=True` in order to avoid validation at Entry Lines creation.
        after all lines are created and glued their Journal Entry if ever
        posted at `move.post()` does a validation on all the previous Journal
        Items at https://goo.gl/KHuwpR
        `valid_moves = self.validate(cr, uid, ids, context)`.
        Therefore, when creating the Journal Entry for a stock_move it is
        enough to do one validate when posting the Journal Entry and skip the
        other validations at creation time
        """
        ctx = dict(self._context, novalidate=True)
        return \
            super(StockMove, self.with_context(ctx))._create_account_move_line(
                credit_account_id, debit_account_id, journal_id)
