from odoo import models


class StockPickingType(models.Model):
    _name = "stock.picking.type"
    _inherit = ['stock.picking.type', 'default.warehouse.mixing']
