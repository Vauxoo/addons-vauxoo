# Copyright 2020 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    warehouse_id = fields.Many2one(related='picking_id.picking_type_id.warehouse_id')
    warehouses_stock_location = fields.Text(store=False, readonly=True)
    warehouses_stock_recompute = fields.Boolean(store=False)
    suggested_location_id = fields.Many2one('stock.location')
    stock_picking_outgoing = fields.Boolean(compute="_compute_picking_outgoing")

    @api.multi
    def _compute_picking_outgoing(self):
        """Method to know if the stock move comes from an outgoing picking.
        """
        for move in self:
            move.stock_picking_outgoing = move.picking_id.picking_type_code == 'outgoing'

    @api.multi
    def _compute_get_warehouses_stock_location(self):
        """Method to get the stock availability (per location) of the product on the wahouse of the stock move.
        Also, getting the location that has the most quantity on stock, and setting it on a field called
        `suggested_location_id` to use it as a default on the stock move lines.
        """
        for move in self:
            move.warehouses_stock_location = move.product_id.with_context(
                warehouse=move.warehouse_id
            )._compute_get_stock_location()
            info_warehouses = json.loads(move.warehouses_stock_location)['content']
            if info_warehouses and info_warehouses[0]:
                move.suggested_location_id = self.env['stock.location'].browse(
                    info_warehouses[0]['most_quantity_location_id'])

    @api.onchange('warehouses_stock_recompute', 'product_id')
    def _warehouses_stock_recompute_onchange(self):
        """Method to trigger the method '_compute_get_warehouses_stock_location' in order to get the information
        for the widget. So the information is only get when the button is being press and not all the time
        with a compute.
        """
        if not self.warehouses_stock_recompute:
            self.warehouses_stock_recompute = True
            return
        self._compute_get_warehouses_stock_location()
