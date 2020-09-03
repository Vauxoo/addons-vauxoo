from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange('product_id')
    def _onchange_product_id_stock_location(self):
        """Set the default suggestion location if the move has one."""
        if self.move_id.state not in ['done', 'cancel'] and self.move_id.suggested_location_id:
            self.location_id = self.move_id.suggested_location_id
