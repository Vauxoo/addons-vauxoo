from odoo import models


class StockPickingType(models.Model):
    _name = "stock.picking.type"
    _inherit = ["default.warehouse.mixing", "stock.picking.type"]
