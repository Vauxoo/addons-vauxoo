from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _search_rule(self, route_ids, packaging_uom_id, product_id, warehouse_id, domain):
        """Grant access to provided warehouse if it's not allowed to the current user"""
        if warehouse_id and warehouse_id._access_unallowed_current_user_salesteams():
            warehouse_id = warehouse_id.sudo()
        return super()._search_rule(route_ids, packaging_uom_id, product_id, warehouse_id, domain)
