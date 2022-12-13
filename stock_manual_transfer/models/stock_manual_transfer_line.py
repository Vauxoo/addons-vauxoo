from odoo import api, fields, models


class StockManualTransferLine(models.Model):
    _name = "stock.manual_transfer_line"
    _description = "Manual Transfer Line"
    _order = "transfer_id, sequence, id"

    transfer_id = fields.Many2one("stock.manual_transfer", "Transfer Reference", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one(
        "product.product",
        domain=[("type", "=", "product")],
        required=True,
    )
    product_uom_qty = fields.Float("Quantity", default=1.0)
    product_uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=', product_uom_category_id)]",
        required=True,
        compute="_compute_product_uom_id",
        store=True,
        readonly=False,
    )
    product_uom_category_id = fields.Many2one(
        "uom.category",
        string="Product's unit of measure category",
        related="product_id.uom_id.category_id",
    )

    @api.depends("product_id")
    def _compute_product_uom_id(self):
        for line in self:
            line.product_uom_id = line.product_id.uom_id

    def _create_procurement(self, values):
        self.ensure_one()
        transfer = self.transfer_id
        return self.env["procurement.group"].Procurement(
            product_id=self.product_id,
            product_qty=self.product_uom_qty,
            product_uom=self.product_uom_id,
            location_id=transfer.warehouse_id.lot_stock_id,
            name=transfer.name,
            origin=transfer.name,
            company_id=transfer.warehouse_id.company_id,
            values=values,
        )
