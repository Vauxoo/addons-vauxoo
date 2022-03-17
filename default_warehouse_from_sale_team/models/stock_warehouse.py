from odoo import api, models, fields


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    sale_team_ids = fields.One2many(
        "crm.team", "default_warehouse_id", string="Sales teams",
    )

    def _access_unallowed_current_user_salesteams(self):
        """Check if access will be denied because warehouse is not allowed on current user's sales teams

        In some cases, it's required to grant access to warehouses not allowed for the current user, e.g.
        when an inventory rule is triggered that involves other warehouses.
        """
        warehouses = self.exists()
        allowed_rules = self._get_salesteam_record_rules()
        failed_rules = self.env["ir.rule"]._get_failing(warehouses, mode="read")
        return (
            warehouses
            and not self.env.su
            and warehouses.check_access_rights("read", raise_exception=False)
            and failed_rules
            and not failed_rules - allowed_rules
        )

    @api.model
    def _get_salesteam_record_rules(self):
        return self.env.ref("default_warehouse_from_sale_team.rule_default_warehouse_wh")
