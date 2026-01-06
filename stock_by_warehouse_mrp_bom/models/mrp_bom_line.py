from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    warehouses_stock = fields.Text(compute="_compute_get_warehouses_stock", store=False, readonly=True)
    warehouse_id = fields.Many2one(string="Warehouse", related="bom_id.picking_type_id.warehouse_id")
    warehouses_stock_recompute = fields.Boolean(store=False)
    is_storable = fields.Boolean(related="product_id.is_storable")

    @api.depends("product_id", "warehouse_id", "warehouses_stock_recompute")
    def _compute_get_warehouses_stock(self):
        for line in self:
            if line.product_id:
                line.warehouses_stock = line.product_id.with_context(
                    warehouse_id=line.warehouse_id.id
                )._compute_get_quantity_warehouses_json()
            else:
                line.warehouses_stock = ""
