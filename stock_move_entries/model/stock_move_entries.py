from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sm_id = fields.Many2one('stock.move', 'Stock move', index=True)


class StockMove(models.Model):
    _inherit = "stock.move"

    aml_ids = fields.One2many(
        'account.move.line', 'sm_id', 'Account move Lines',
        domain=[('account_id.reconcile', '=', True)])
    aml_all_ids = fields.One2many(
        'account.move.line', 'sm_id', 'All Account move Lines')

    def _prepare_account_move_line(self, qty, cost,
                                   credit_account_id, debit_account_id):
        res = super(StockMove, self)._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id)
        for line in res:
            line[2]['sm_id'] = self.id
        return res
