from odoo import api, models


class DefaultWarehouseMixing(models.AbstractModel):
    """If you inherit from this model and add a field called warehouse_id into
    the model, then the default value for such model will be the one
    set into the sales team.
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
        if vals.get('warehouse_id') and 'name' not in vals:
            code = self._get_sequence_code()
            pick_warehouse = self.env['stock.picking.type'].browse(vals.get('picking_type_id')).warehouse_id
            warehouse_id = vals.get('warehouse_id', pick_warehouse.id)
            section = self.env['crm.team'].search([('default_warehouse_id', '=', warehouse_id)], limit=1)
            sequence = self.env['ir.sequence'].search(
                [
                    ('section_id', '=', section.id),
                    ('code', '=', code),
                ],
                limit=1,
            )
            if sequence:
                vals['name'] = sequence.next_by_id()
        return super().create(vals)

    def _get_sequence_code(self):
        return self._name
