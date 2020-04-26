# coding: utf-8

from odoo import models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_account_move_line(self, qty, cost,
                                   credit_account_id, debit_account_id):
        res = super(StockMove, self)._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id)
        production_id = self.production_id or self.raw_material_production_id
        if not production_id:
            return res
        for line in res:
            line[2]['production_id'] = production_id.id
        return res
