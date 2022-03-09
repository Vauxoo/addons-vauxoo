from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """Allow to run procurement in warehouses not allowed on current user's sales teams"""
        warehouses = self.route_id.rule_ids.warehouse_id
        if warehouses._access_unallowed_current_user_salesteams():
            self = self.sudo()
        return super()._action_launch_stock_rule(previous_product_uom_qty)
