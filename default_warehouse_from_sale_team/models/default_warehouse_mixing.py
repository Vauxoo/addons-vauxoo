from odoo import api, models


class DefaultWarehouseMixing(models.AbstractModel):
    """If you inherit from this model and add a field called warehouse_id into
    the model, then the default value for such model will be the one
    set into the sales team.

    Make sure to put this mixing at the top of inheritance (before the base model), e.g.

        _inherit = ["default.warehouse.mixing", "sale.order"]
    """
    _name = "default.warehouse.mixing"
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
        warehouse_fields = self.env['ir.model.fields'].search([
            ('model', '=', self._name),
            ('relation', '=', 'stock.warehouse'),
            ('ttype', '=', 'many2one'),
            ('name', 'in', list(defaults)),
        ])
        defaults.update({
            fld.name: default_warehouse.id
            for fld in warehouse_fields
        })
        return defaults

    @api.model
    def create(self, vals):
        """Pass sales team by context so it's taken into account when computing sequence name"""
        salesteam = self._get_salesteam_from_vals(vals)
        self_team = self.with_context(sequence_salesteam_id=salesteam.id)
        return super(DefaultWarehouseMixing, self_team).create(vals)

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
