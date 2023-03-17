from odoo import api, models


class DefaultWarehouseMixin(models.AbstractModel):
    """If you inherit from this model and add a field called warehouse_id into
    the model, then the default value for such model will be the one
    set into the sales team.

    Make sure to put this mixin at the top of inheritance (before the base model), e.g.

        _inherit = ["default.warehouse.mixin", "sale.order"]
    """

    _name = "default.warehouse.mixin"
    _description = "Default Warehouse"

    @api.model
    def default_get(self, fields_list):
        """Force that if model has a field called warehouse_id the default
        value is the one set in the user's sales team.
        """
        defaults = super().default_get(fields_list)
        default_warehouse = self.env.user._get_default_warehouse_id()
        if not default_warehouse:
            return defaults
        warehouse_fields = (
            self.env["ir.model.fields"]
            .sudo()
            .search(
                [
                    ("model", "=", self._name),
                    ("relation", "=", "stock.warehouse"),
                    ("ttype", "=", "many2one"),
                    ("name", "in", fields_list),
                ]
            )
        )
        defaults.update({fld.name: default_warehouse.id for fld in warehouse_fields})
        return defaults

    @api.model_create_multi
    def create(self, vals_list):
        """Pass sales team by context so it's taken into account when computing sequence name"""
        if not vals_list:
            return super().create(vals_list)
        default_obj = self
        salesteams = self._get_salesteam_from_vals_list(vals_list)
        for salesteam, salesteam_vals_list in salesteams.items():
            self = self.with_context(sequence_salesteam_id=salesteam.id)
            default_obj |= super().create(salesteam_vals_list)
        return default_obj

    def _get_salesteam_from_vals(self, vals):
        """Determine sales team from creation values"""
        if "name" in vals:
            # Already has a name, so salesteam won't be used anyway
            return self.env["crm.team"]
        warehouse = (
            self.env["stock.warehouse"].browse(vals.get("warehouse_id"))
            or self.env["stock.picking.type"].browse(vals.get("picking_type_id")).warehouse_id
        )
        salesteam = warehouse.sale_team_ids[:1]
        return salesteam

    def _get_salesteam_from_vals_list(self, vals_list):
        """Determine sales team from the list of creation values"""
        salesteams = {}
        for vals in vals_list:
            salesteam = self._get_salesteam_from_vals(vals)
            salesteams.setdefault(salesteam, []).append(vals)
        return salesteams

    def onchange(self, values, field_name, field_onchange):
        """Add an extra context to prevent current user's salesteam from being overwritten by onchanges

        This is useful in e.g. sale orders, where sales person's sales team has priority over current
        user's sales team.
        """
        self_team_ctx = self.with_context(keep_current_user_salesteam=True)
        return super(DefaultWarehouseMixin, self_team_ctx).onchange(values, field_name, field_onchange)
