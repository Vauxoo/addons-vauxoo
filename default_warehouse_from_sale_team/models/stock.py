from openerp import fields, models


class StockPickingType(models.Model):

    _name = "stock.picking.type"
    _inherit = ['stock.picking.type', 'default.warehouse']


class StockPicking(models.Model):

    _name = "stock.picking"
    _inherit = ['stock.picking', 'default.warehouse']

    warehouse_id = fields.Many2one(related='picking_type_id.warehouse_id')


class StockMove(models.Model):

    _inherit = "stock.move"

    def _get_accounting_data_for_valuation(self):

        journal_id, acc_src, acc_dest, acc_valuation = super(
            StockMove, self)._get_accounting_data_for_valuation()

        warehouse_id = (self.picking_id.picking_type_id.warehouse_id or
                        self.warehouse_id)
        sale_team = self.env['crm.team'].search(
            [('default_warehouse', '=', warehouse_id.id)], limit=1)

        if sale_team.journal_stock_id:
            journal_id = sale_team.journal_stock_id.id

        return journal_id, acc_src, acc_dest, acc_valuation
