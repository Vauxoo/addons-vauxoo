from odoo import models, fields


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    sale_team_ids = fields.One2many(
        "crm.team", "default_warehouse_id", string="Sales teams",
    )
