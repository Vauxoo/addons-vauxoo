from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_accounting_data_for_valuation(self):
        journal_id, acc_src, acc_dest, acc_valuation = super()._get_accounting_data_for_valuation()
        warehouse_id = (
            self.picking_id.picking_type_id.warehouse_id or
            self.warehouse_id
        )
        sale_team = self.env['crm.team'].search(
            [('default_warehouse_id', '=', warehouse_id.id)], limit=1)

        if sale_team.journal_stock_id:
            journal_id = sale_team.journal_stock_id.id

        return journal_id, acc_src, acc_dest, acc_valuation
