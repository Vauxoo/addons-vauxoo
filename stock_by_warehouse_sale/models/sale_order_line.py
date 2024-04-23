from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    warehouses_stock = fields.Json(compute="_compute_warehouse_stock")
    warehouses_stock_recompute = fields.Boolean(store=False)

    def _compute_get_warehouses_stock(self):
        for line in self:
            line.warehouses_stock = (
                line.product_id.with_context(warehouse_id=line.warehouse_id)._compute_get_quantity_warehouses_json()
                if line.warehouses_stock_recompute
                else False
            )

    @api.depends("warehouses_stock_recompute", "product_id")
    def _compute_warehouse_stock(self):
        for record in self:
            record.warehouse_id = self.order_id.warehouse_id
            record._compute_get_warehouses_stock()
