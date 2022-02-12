from odoo import fields, models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ['default.warehouse.mixin', 'stock.picking']

    warehouse_id = fields.Many2one(related='picking_type_id.warehouse_id')
