# coding: utf-8

from odoo import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    warehouses_stock = fields.Text(compute="_compute_get_warehouses_stock")
    warehouse_id = fields.Many2one(string="Warehouse",
                                   related='order_id.warehouse_id',
                                   readonly=True)

    @api.multi
    @api.depends('product_id', 'order_id.warehouse_id')
    def _compute_get_warehouses_stock(self):
        for line in self:
            line.warehouses_stock = line.product_id.with_context(
                warehouse_id=line.warehouse_id).warehouses_stock

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if res.get('warning'):
            # If there is a warning then return it to avoid double
            # control original stuff.
            return res
        if res.get('domain'):
            # When this onchange works fine, then it has a domain
            # dictionary in the core, then if a dictionary is coming
            # is when we need to set the new fields.
            self.warehouse_id = self.order_id.warehouse_id
            self._compute_get_warehouses_stock()
