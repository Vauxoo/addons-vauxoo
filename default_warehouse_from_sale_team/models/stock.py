# coding: utf-8

from openerp import fields, models


class StockPickingType(models.Model):

    _name = "stock.picking.type"
    _inherit = ['stock.picking.type', 'default.warehouse']


class StockPicking(models.Model):

    _name = "stock.picking"
    _inherit = ['stock.picking', 'default.warehouse']

    warehouse_id = fields.Many2one(related='picking_type_id.warehouse_id')
