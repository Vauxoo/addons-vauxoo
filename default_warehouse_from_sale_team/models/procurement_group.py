from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _search_rule(self, route_ids, product_id, warehouse_id, domain):
        """Grant access to provided warehouse if it's not allowed to the current user"""
        if warehouse_id._access_unallowed_current_user_salesteams():
            warehouse_id = warehouse_id.sudo()
        return super()._search_rule(route_ids, product_id, warehouse_id, domain)
