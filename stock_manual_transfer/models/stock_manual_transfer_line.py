from odoo import api, fields, models


class StockManualTransferLine(models.Model):
    _name = "stock.manual_transfer.line"
    _description = "Manual Transfer Line"
    _order = "transfer_id, sequence, id"

    transfer_id = fields.Many2one("stock.manual_transfer", "Transfer Reference", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one(
        "product.product",
        domain=[("is_storable", "=", True)],
        required=True,
    )
    product_uom_qty = fields.Float("Quantity", default=1.0)
    product_uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        domain="[('id', 'in', allowed_uom_ids)]",
        required=True,
        compute="_compute_product_uom_id",
        store=True,
        readonly=False,
    )
    allowed_uom_ids = fields.Many2many(
        "uom.uom",
        compute="_compute_allowed_uom_ids",
        export_string_translation=False,
    )

    @api.depends("product_id.uom_id", "product_id.uom_ids")
    def _compute_allowed_uom_ids(self):
        for line in self:
            line.allowed_uom_ids = line.product_id.uom_id | line.product_id.uom_ids

    @api.depends("product_id")
    def _compute_product_uom_id(self):
        for line in self:
            line.product_uom_id = line.product_id.uom_id

    def _create_procurement(self, values):
        self.ensure_one()
        transfer = self.transfer_id
        return self.env["stock.rule"].Procurement(
            product_id=self.product_id,
            product_qty=self.product_uom_qty,
            product_uom=self.product_uom_id,
            location_id=transfer.warehouse_id.lot_stock_id,
            name=transfer.name,
            origin=transfer.name,
            company_id=transfer.warehouse_id.company_id,
            values=values,
        )
