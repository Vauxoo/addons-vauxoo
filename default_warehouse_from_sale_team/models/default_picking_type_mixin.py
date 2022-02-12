from odoo import models, api


class DefaultPickingTypeMixin(models.AbstractModel):
    _name = 'default.picking.type.mixin'
    _inherit = 'default.warehouse.mixin'
    _description = "Default Operation Type"

    @api.model
    def default_get(self, fields_list):
        """Fill a default picking type

        Get by default the picking type depending
        on the sales team warehouse in models where picking type is required,
        e.g. purchase order or purchase requisition.
        returning the first picking type that match with the warehouse
        of the sales team.
        """
        res = super().default_get(fields_list)
        default_warehouse = self.env.user._get_default_warehouse_id()
        if default_warehouse:
            pick_type = self.env['stock.picking.type'].search(
                [
                    ('code', '=', 'incoming'),
                    ('warehouse_id', '=', default_warehouse.id),
                ],
                limit=1,
            )
            res.update({'picking_type_id': pick_type.id})

        return res
