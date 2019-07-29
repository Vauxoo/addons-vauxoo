# coding: utf-8

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    warehouses_stock = fields.Text(store=False, readonly=True)
    warehouse_id = fields.Many2one(
        string="Warehouse",
        related='order_id.picking_type_id.warehouse_id', readonly=True)
    warehouses_stock_recompute = fields.Boolean(store=False, readonly=False)

    @api.multi
    def _compute_get_warehouses_stock(self):
        for line in self:
            line.warehouses_stock = line.product_id.with_context(
                warehouse_id=line.warehouse_id
            )._compute_get_quantity_warehouses_json()

    @api.onchange('warehouses_stock_recompute', 'product_id')
    def _warehouses_stock_recompute_onchange(self):
        if not self.warehouses_stock_recompute:
            self.warehouses_stock_recompute = True
            return
        self._compute_get_warehouses_stock()
        self.warehouses_stock_recompute = True
