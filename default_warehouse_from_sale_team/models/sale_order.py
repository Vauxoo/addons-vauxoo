from odoo import models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["default.warehouse.mixin", "sale.order"]

    def _prepare_invoice(self):
        """Add team by context so it's taken into account when choosing default journal"""
        return super(SaleOrder, self.with_context(salesteam=self.team_id))._prepare_invoice()
