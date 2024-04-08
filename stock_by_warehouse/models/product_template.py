import json

from odoo import _, api, fields, models

UNIT = "Product Unit of Measure"


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_available_not_res = fields.Float(
        string="Quantity On Hand Unreserved",
        digits=UNIT,
        compute="_compute_product_available_not_res",
    )

    warehouses_stock = fields.Json(compute="_compute_warehouse_stock")
    warehouses_stock_recompute = fields.Boolean(store=False)

    @api.depends("warehouses_stock_recompute")
    def _compute_warehouse_stock(self):
        for record in self:
            record.warehouses_stock = (
                record._compute_get_quantity_warehouses_json() if record.warehouses_stock_recompute else False
            )

    @api.depends("product_variant_ids.qty_available_not_res")
    @api.depends_context("warehouse", "company")
    def _compute_product_available_not_res(self):
        for tmpl in self:
            if isinstance(tmpl.id, models.NewId):
                continue
            tmpl.qty_available_not_res = sum(tmpl.mapped("product_variant_ids.qty_available_not_res"))

    def _compute_get_quantity_warehouses_json(self):
        # get original from onchange
        self_origin = self._origin if hasattr(self, "_origin") else self
        info = {"title": _("Stock by Warehouse"), "content": [], "warehouse": self_origin.qty_available_not_res}
        if not self_origin.exists():
            return json.dumps(info)
        self_origin.ensure_one()

        # Just in case it's asked from other place different than product
        # itself, we enable this context management
        warehouse_id = self._context.get("warehouse_id")

        for warehouse in self.env["stock.warehouse"].sudo().search([]):
            tmpl = (
                self_origin.sudo()
                .with_company(warehouse.company_id)
                .with_context(warehouse=warehouse.id, location=False)
            )
            tmpl.invalidate_recordset()
            if warehouse_id and warehouse_id.id == warehouse.id:
                info["warehouse"] = tmpl.qty_available_not_res
            info["content"].append(
                {
                    "warehouse": warehouse.name,
                    "warehouse_short": warehouse.code,
                    "product": tmpl.id,
                    "available_not_res": tmpl.qty_available_not_res,
                    "available": tmpl.qty_available,
                    "virtual": tmpl.virtual_available,
                    "incoming": tmpl.incoming_qty,
                    "outgoing": tmpl.outgoing_qty,
                    "saleable": tmpl.qty_available - tmpl.outgoing_qty,
                }
            )
        return json.dumps(info)
